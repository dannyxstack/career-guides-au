import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const sourcePath = resolve(root, '../site/src/data/occupations_v2.json');
const outputPath = resolve(root, './data/occupations.json');
const source = JSON.parse(await readFile(sourcePath, 'utf8'));

const categorySlugs = {
  'Agriculture & Environment': 'agriculture-environment',
  'Business, Finance & Legal': 'business-finance-legal',
  'Creative, Media & Personal Services': 'creative-media-personal-services',
  'Education & Community': 'education-community',
  'Engineering & Infrastructure': 'engineering-infrastructure',
  'Government & Public Sector': 'government-public-sector',
  'Healthcare & Care': 'healthcare-care',
  'Hospitality, Retail & Tourism': 'hospitality-retail-tourism',
  'IT & Digital': 'it-digital',
  'Trades & Construction': 'trades-construction',
  'Transport, Logistics & Mining': 'transport-logistics-mining'
};

const aliases = {
  'accountant': ['accounting'],
  'software-engineer': ['developer', 'programmer', 'software developer'],
  'registered-nurse': ['nurse', 'rn'],
  'secondary-school-teacher': ['teacher', 'high school teacher'],
  'primary-school-teacher': ['teacher', 'elementary teacher'],
  'lawyer': ['attorney', 'solicitor'],
  'general-practitioner': ['doctor', 'physician', 'gp'],
  'data-analyst': ['analytics'],
  'graphic-designer': ['designer'],
  'electrician': ['electrical worker']
};

const groups = new Map();
for (const occupation of source.occupations) {
  const group = groups.get(occupation.slug) || [];
  group.push(occupation);
  groups.set(occupation.slug, group);
}

const average = (values, fallback) => {
  const valid = values.map(Number).filter(Number.isFinite);
  return valid.length ? Math.round(valid.reduce((sum, value) => sum + value, 0) / valid.length * 10) / 10 : fallback;
};

const rating = (occupation, dimension) => occupation.ratings?.find((item) => item.dimension === dimension)?.stars;
const occupations = [...groups.entries()].map(([slug, group]) => {
  const representative = group.find((item) => item.country === 'US') || group.find((item) => item.country === 'AU') || group[0];
  return {
    slug,
    name: representative.name_en,
    category: representative.category,
    categorySlug: categorySlugs[representative.category] || '',
    countries: [...new Set(group.map((item) => item.country))].sort(),
    exposure: average(group.map((item) => item.ai?.automation_exposure ?? rating(item, 'ai_risk')), 5),
    moat: average(group.map((item) => item.ai?.human_moat), 5),
    upside: average(group.map((item) => item.ai?.ai_upside), 6),
    ...(aliases[slug] ? { aliases: aliases[slug] } : {})
  };
}).sort((a, b) => a.name.localeCompare(b.name));

const output = {
  generatedAt: new Date().toISOString(),
  sourceGeneratedAt: source.generated_at,
  count: occupations.length,
  fields: 'Search and scoring fields only. Full occupation records remain on the related data sites.',
  occupations
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(output)}\n`, 'utf8');
console.log(`Wrote ${occupations.length} roles to ${outputPath}`);
