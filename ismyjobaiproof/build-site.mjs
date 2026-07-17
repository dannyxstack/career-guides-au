import { copyFile, cp, mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  SITE_URL, MODEL_VERSION, DATA_SNAPSHOT, featuredSlugs,
  jobOverrides, categoryTasks
} from './site-content.mjs';

const root = dirname(fileURLToPath(import.meta.url));
const dist = resolve(root, 'dist');
const files = [
  'index.html', 'styles.css', 'app.js', 'brand-logo.png', 'favicon.ico',
  'favicon-16x16.png', 'favicon-32x32.png', 'apple-touch-icon.png',
  'site.webmanifest', 'og-image.png', 'robots.txt'
];
const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
}[char]));
const round = (value) => Math.round(Number(value));
const riskBand = (score) => score >= 75 ? 'High' : score >= 60 ? 'Elevated' : score >= 40 ? 'Moderate' : 'Lower';
const resilienceBand = (score) => score >= 76 ? 'Strong' : score >= 61 ? 'Resilient with change' : score >= 46 ? 'Mixed' : 'Exposed';

function shell({ title, description, canonical, body, schema = [], pageClass = 'content-page' }) {
  const schemas = Array.isArray(schema) ? schema : [schema];
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(description)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="theme-color" content="#f4f6f2">
  <link rel="icon" href="/favicon.ico?v=4" sizes="any">
  <link rel="icon" href="/favicon-32x32.png?v=4" type="image/png" sizes="32x32">
  <link rel="icon" href="/favicon-16x16.png?v=4" type="image/png" sizes="16x16">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png?v=4" sizes="180x180">
  <link rel="manifest" href="/site.webmanifest?v=4">
  <link rel="canonical" href="${canonical}">
  <link rel="stylesheet" href="/styles.css">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Is My Job AI-Proof?">
  <meta property="og:title" content="${escapeHtml(title)}">
  <meta property="og:description" content="${escapeHtml(description)}">
  <meta property="og:url" content="${canonical}">
  <meta property="og:image" content="${SITE_URL}/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  ${schemas.map((item) => `<script type="application/ld+json">${JSON.stringify(item)}</script>`).join('\n  ')}
</head>
<body class="${pageClass}">
  <header class="site-header">
    <a class="brand" href="/"><img class="brand-mark" src="/brand-logo.png?v=4" alt="" width="38" height="38" aria-hidden="true"><span>Is My Job AI-Proof?</span></a>
    <nav class="page-nav" aria-label="Site navigation"><a href="/rankings/">Rankings</a><a href="/methodology/">Methodology</a><a href="/about/">About</a></nav>
  </header>
  ${body}
  <footer>
    <span>&copy; ${new Date().getUTCFullYear()} Is My Job AI-Proof?</span>
    <nav aria-label="Site information"><a href="/methodology/">Methodology</a><a href="/editorial-policy/">Editorial policy</a><a href="/privacy/">Privacy</a></nav>
  </footer>
</body>
</html>`;
}

const breadcrumb = (name, url, parent) => ({
  '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Assessment', item: `${SITE_URL}/` },
    ...(parent ? [{ '@type': 'ListItem', position: 2, name: parent.name, item: parent.url }] : []),
    { '@type': 'ListItem', position: parent ? 3 : 2, name, item: url }
  ]
});

function jobPage(job) {
  const exposure = round(job.exposure * 10);
  const moat = round(job.moat * 10);
  const upside = round(job.upside * 10);
  const resilience = round((100 - exposure) * .45 + moat * .35 + upside * .2);
  const tasks = jobOverrides[job.slug] || categoryTasks[job.category] || categoryTasks.default;
  const risk = riskBand(exposure);
  const resilienceLabel = resilienceBand(resilience);
  const url = `${SITE_URL}/job/${job.slug}/`;
  const title = `Is ${job.name} AI-Proof? AI Job Risk Baseline (2026)`;
  const description = `${job.name} has a ${exposure}/100 baseline AI exposure score. See exposed tasks, human advantages and where AI can augment the role, then take the personal assessment.`;
  const direct = exposure >= 70
    ? `The ${job.name} role is not fully AI-proof. Its baseline suggests that a substantial share of the work is reachable by current AI, while human accountability, context and relationships can still protect important tasks.`
    : exposure >= 50
      ? `The ${job.name} role is partly exposed to AI, but it is more likely to be reshaped than removed as a whole. Outcomes depend heavily on the person's task mix, seniority and work setting.`
      : `The ${job.name} role has a comparatively lower AI-exposure baseline. AI may still change routine and digital tasks, but human presence, judgment or accountability remain meaningful defenses.`;
  const list = (items) => items.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  const schema = [
    {
      '@context': 'https://schema.org', '@type': 'Article', headline: title,
      description, dateModified: DATA_SNAPSHOT, mainEntityOfPage: url,
      author: { '@type': 'Organization', name: 'Is My Job AI-Proof?' },
      publisher: { '@type': 'Organization', name: 'Is My Job AI-Proof?', url: SITE_URL },
      about: { '@type': 'Occupation', name: job.name }
    },
    breadcrumb(job.name, url, { name: 'AI Job Exposure Rankings', url: `${SITE_URL}/rankings/` })
  ];
  const body = `<main class="article-shell">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Assessment</a><span aria-hidden="true">/</span><a href="/rankings/">Rankings</a><span aria-hidden="true">/</span><span>${escapeHtml(job.name)}</span></nav>
    <header class="article-hero">
      <p class="eyebrow">Occupation baseline · Model ${MODEL_VERSION}</p>
      <h1>Is the ${escapeHtml(job.name)} role AI-proof?</h1>
      <p class="article-lede">${escapeHtml(direct)}</p>
      <div class="baseline-strip" aria-label="Baseline scores">
        <div><strong>${exposure}</strong><span>AI exposure</span></div>
        <div><strong>${risk}</strong><span>Exposure band</span></div>
        <div><strong>${resilience}</strong><span>Baseline resilience</span></div>
        <div><strong>${resilienceLabel}</strong><span>Resilience band</span></div>
      </div>
      <a class="button button-primary article-cta" href="/?job=${encodeURIComponent(job.slug)}#assessment-tool">Assess my actual ${escapeHtml(job.name)} work</a>
    </header>
    <section class="article-section direct-answer">
      <p class="eyebrow">Direct answer</p>
      <h2>Exposure is not replacement probability</h2>
      <p>${escapeHtml(direct)} The ${exposure}/100 figure is an occupation-level starting point. It does not mean that ${exposure}% of workers will lose their jobs or that ${exposure}% of the role will certainly disappear.</p>
    </section>
    ${job.roleSummary ? `<section class="article-section role-context"><p class="eyebrow">Role context</p><h2>What ${escapeHtml(job.name)} work involves</h2><p>${escapeHtml(job.roleSummary)}</p></section>` : ''}
    <div class="task-columns">
      <section><p class="task-kicker automate">More exposed</p><h2>Tasks AI can reach</h2><ul>${list(tasks.automate)}</ul></section>
      <section><p class="task-kicker human">Human advantage</p><h2>Tasks that resist removal</h2><ul>${list(tasks.human)}</ul></section>
      <section><p class="task-kicker augment">Augmentation</p><h2>Where AI may help</h2><ul>${list(tasks.augment)}</ul></section>
    </div>
    <section class="article-section">
      <p class="eyebrow">Why your result may differ</p>
      <h2>A title cannot describe the whole job</h2>
      <p>Two people called ${escapeHtml(job.name)} may have different exposure. Routine digital inputs and repeatable rules raise automation pressure. Accountability, trust, unusual cases, physical presence and senior decision-making generally raise resilience. The personal assessment adjusts this baseline around those factors.</p>
    </section>
    <section class="evidence-note">
      <div><strong>Data snapshot</strong><span>${DATA_SNAPSHOT}</span></div>
      <div><strong>Coverage</strong><span>${job.countries.length} ${job.countries.length === 1 ? 'market' : 'markets'} in the compiled dataset</span></div>
      <div><strong>Model</strong><span>Job Resilience Model ${MODEL_VERSION}</span></div>
      <p>Baseline inputs come from the site's compiled occupation dataset. Scores are editorial planning indicators, not official labour-market forecasts. See the <a href="/methodology/">methodology, formulas and limitations</a>.</p>
    </section>
    <section class="article-final-cta"><h2>Measure the work you actually do</h2><p>Adjust this baseline using your task mix, career level and workplace context. No account is required and answers remain in your browser.</p><a class="button button-primary" href="/?job=${encodeURIComponent(job.slug)}#assessment-tool">Start the ${escapeHtml(job.name)} assessment</a></section>
  </main>`;
  return shell({ title, description, canonical: url, body, schema, pageClass: 'content-page job-page' });
}

function rankingPage(jobs) {
  const ranked = [...jobs].sort((a, b) => (b.exposure - a.exposure) || a.name.localeCompare(b.name));
  const categories = [...new Set(ranked.map((job) => job.category))].sort();
  const rows = ranked.map((job, index) => {
    const exposure = round(job.exposure * 10);
    const resilience = round((100 - exposure) * .45 + (job.moat * 10) * .35 + (job.upside * 10) * .2);
    const risk = riskBand(exposure);
    return `<li class="ranking-row" data-name="${escapeHtml(job.name.toLowerCase())}" data-category="${escapeHtml(job.category)}" data-band="${risk.toLowerCase()}" data-exposure="${exposure}" data-resilience="${resilience}">
      <span class="ranking-position">${index + 1}</span>
      <span class="ranking-role"><a href="/job/${job.slug}/">${escapeHtml(job.name)}</a><small>${escapeHtml(job.category)}</small></span>
      <span class="ranking-band band-${risk.toLowerCase()}">${risk}</span>
      <strong class="ranking-score">${exposure}</strong>
      <strong class="ranking-resilience">${resilience}</strong>
    </li>`;
  }).join('\n');
  const url = `${SITE_URL}/rankings/`;
  const schema = [
    {
      '@context': 'https://schema.org', '@type': 'ItemList', name: 'AI Job Exposure Rankings',
      numberOfItems: ranked.length,
      itemListElement: ranked.map((job, index) => ({
        '@type': 'ListItem', position: index + 1, name: job.name,
        url: `${SITE_URL}/job/${job.slug}/`
      }))
    },
    breadcrumb('AI Job Exposure Rankings', url)
  ];
  const body = `<main class="ranking-shell">
    <header class="ranking-hero"><p class="eyebrow">${ranked.length} distinct occupations · Model ${MODEL_VERSION}</p><h1>AI job exposure rankings</h1><p class="article-lede">Compare occupation-level AI exposure baselines, then open any role to see exposed tasks, human advantages and augmentation opportunities. These scores measure exposure, not the probability of job loss.</p></header>
    <section class="ranking-controls" aria-label="Ranking filters">
      <label><span>Search occupations</span><input id="ranking-search" type="search" placeholder="e.g. nurse, engineer, designer"></label>
      <label><span>Category</span><select id="ranking-category"><option value="">All categories</option>${categories.map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`).join('')}</select></label>
      <label><span>Exposure band</span><select id="ranking-band"><option value="">All bands</option><option value="high">High</option><option value="elevated">Elevated</option><option value="moderate">Moderate</option><option value="lower">Lower</option></select></label>
      <label><span>Sort by</span><select id="ranking-sort"><option value="exposure-desc">AI exposure: high to low</option><option value="exposure-asc">AI exposure: low to high</option><option value="resilience-desc">Resilience: high to low</option><option value="name">Occupation name</option></select></label>
    </section>
    <div class="ranking-summary"><strong id="ranking-count">${ranked.length}</strong><span>occupations shown</span><a href="/methodology/">How scores are calculated</a></div>
    <div class="ranking-list-head" aria-hidden="true"><span>Rank</span><span>Occupation</span><span>Band</span><span>Exposure</span><span>Resilience</span></div>
    <ol class="ranking-list" id="ranking-list">${rows}</ol>
    <p class="ranking-empty" id="ranking-empty" hidden>No occupations match these filters.</p>
  </main>
  <script>
    (() => {
      const list = document.querySelector('#ranking-list');
      const rows = [...list.querySelectorAll('.ranking-row')];
      const search = document.querySelector('#ranking-search');
      const category = document.querySelector('#ranking-category');
      const band = document.querySelector('#ranking-band');
      const sort = document.querySelector('#ranking-sort');
      const count = document.querySelector('#ranking-count');
      const empty = document.querySelector('#ranking-empty');
      const compare = {
        'exposure-desc': (a, b) => Number(b.dataset.exposure) - Number(a.dataset.exposure) || a.dataset.name.localeCompare(b.dataset.name),
        'exposure-asc': (a, b) => Number(a.dataset.exposure) - Number(b.dataset.exposure) || a.dataset.name.localeCompare(b.dataset.name),
        'resilience-desc': (a, b) => Number(b.dataset.resilience) - Number(a.dataset.resilience) || a.dataset.name.localeCompare(b.dataset.name),
        name: (a, b) => a.dataset.name.localeCompare(b.dataset.name)
      };
      function update() {
        const query = search.value.trim().toLowerCase();
        const visible = rows.filter((row) => (!query || row.dataset.name.includes(query)) && (!category.value || row.dataset.category === category.value) && (!band.value || row.dataset.band === band.value));
        const visibleSet = new Set(visible);
        rows.forEach((row) => { row.hidden = !visibleSet.has(row); });
        visible.sort(compare[sort.value]).forEach((row, index) => { row.querySelector('.ranking-position').textContent = index + 1; list.appendChild(row); });
        count.textContent = visible.length.toLocaleString();
        empty.hidden = visible.length !== 0;
      }
      [search, category, band, sort].forEach((control) => control.addEventListener(control === search ? 'input' : 'change', update));
    })();
  </script>`;
  return shell({
    title: 'AI Job Exposure Rankings: 550 Occupations Compared',
    description: `Compare AI exposure and baseline job resilience across ${ranked.length} distinct occupations, with links to task-level AI-proof assessments.`,
    canonical: url, body, schema, pageClass: 'content-page ranking-page'
  });
}

const methodologyBody = `<main class="article-shell prose-page">
  <header class="article-hero"><p class="eyebrow">Model transparency</p><h1>How the Job Resilience Score works</h1><p class="article-lede">The assessment estimates task-level exposure and resilience. It is a transparent planning model, not a prediction of unemployment or a claim that any job is permanently AI-proof.</p><div class="version-row"><span>Model ${MODEL_VERSION}</span><span>Data snapshot ${DATA_SNAPSHOT}</span><span>Updated July 2026</span></div></header>
  <section class="article-section"><h2>What the model measures</h2><p>The model starts with three occupation baselines: AI exposure, human moat and augmentation upside. It then adjusts them using the respondent's task mix, career level, digital workflow, repeatability, formal accountability, relationships, unusual situations and workplace AI adoption.</p><p><strong>AI exposure</strong> measures how much work current generative AI can reach. <strong>Automation pressure</strong> adds workflow and organisational incentives. <strong>Human advantage</strong> measures protection from trust, accountability, physical context and judgment. <strong>Augmentation upside</strong> estimates how much AI may improve the work while a person remains responsible.</p></section>
  <section class="article-section"><h2>Calculation sequence</h2><div class="formula-list">
    <div><strong>1. Task scores</strong><code>weighted average(task amount × task coefficient)</code><p>Six task families are rated from none to core work: routine information, analysis, content creation, communication and care, judgment and accountability, and physical or on-site work.</p></div>
    <div><strong>2. Context risk</strong><code>mean(digital, repeatable, adoption, inverse accountability, inverse relationships, inverse uncertainty)</code><p>Each context answer is represented as 0, 0.5 or 1.</p></div>
    <div><strong>3. AI exposure</strong><code>baseline exposure × 0.58 + task automation × 0.28 + context risk × 0.14 + level adjustment</code></div>
    <div><strong>4. Automation pressure</strong><code>AI exposure × 0.57 + task automation × 0.20 + context risk × 0.23 + level adjustment</code></div>
    <div><strong>5. Human advantage</strong><code>baseline moat × 0.43 + task human score × 0.34 + context protection × 0.23 + level adjustment</code></div>
    <div><strong>6. Augmentation upside</strong><code>baseline upside × 0.54 + task augmentation × 0.32 + workplace adoption × 0.14</code></div>
    <div><strong>7. Job Resilience Score</strong><code>(100 − automation pressure) × 0.45 + human advantage × 0.35 + augmentation upside × 0.20</code></div>
  </div><p>All displayed scores are rounded and clamped to 0–100. Career-level adjustments recognise that junior work is often more routine while senior and management work usually carries more accountability. These are model assumptions, not universal facts.</p></section>
  <section class="article-section"><h2>Occupation data</h2><p>The lightweight tool uses a compiled index of 4,861 occupation titles across 13 countries. For each normalised occupation it stores only the fields needed for search and scoring: title, category, represented markets, exposure baseline, human-moat baseline and augmentation baseline. Full salary, migration and career records are deliberately kept outside this tool.</p><p>Where multiple country records share a normalised occupation slug, the tool averages valid baseline values. A US record is preferred as the display label when available, followed by Australia and then the first available market record. The current client dataset was generated from the project's occupation snapshot dated ${DATA_SNAPSHOT}.</p></section>
  <section class="article-section"><h2>Baseline provenance and fallbacks</h2><p>The compiled source records carry an exposure-method label. Depending on the source occupation and available crosswalk, that label identifies either an Eloundou-style occupational AI exposure mapping or an ILO generative-AI occupational exposure mapping. Crosswalks may be direct through SOC or ISCO codes, grouped at a broader code level, or produced through a documented title-to-occupation mapping step.</p><p>The compact tool does not claim that these research measures directly predict layoffs. They are used only to establish a relative starting point. During index generation, an explicit <code>automation_exposure</code> value is preferred; the occupation's AI-risk rating is the fallback. Valid values are averaged across records that share a normalised slug. Human-moat values fall back to 5/10 and augmentation-upside values to 6/10 when those fields are absent. These fallbacks prevent a missing field from becoming a false zero.</p><p>A method label describes lineage, not certainty. Country records may use different occupational classifications, granularity and publication dates. The normalised slug improves search coverage but can merge specialties whose real task profiles differ. That is one reason the personal task questions carry substantial weight.</p></section>
  <section class="article-section"><h2>How to read the score bands</h2><p>Exposure-oriented scores use four descriptive bands: 75–100 High, 50–74 Moderate, 30–49 Limited and 0–29 Low. The occupation landing pages use a slightly more detailed presentation for baseline exposure: 75–100 High, 60–74 Elevated, 40–59 Moderate and 0–39 Lower. These labels organise the interface; they are not statistical confidence intervals.</p><p>The Job Resilience Score is interpreted as 76–100 strong human defenses, 61–75 likely to change more than disappear, 46–60 meaningful exposure and 0–45 substantial automation pressure. A higher resilience score does not mean no change. It can also reflect high augmentation potential, where the person remains responsible but the tools and workflow change quickly.</p><p>Small differences should not drive major decisions. A score of 62 is not meaningfully safer than 60 without additional evidence. Look first at which component moved, then at the tasks and context that produced it.</p></section>
  <section class="article-section"><h2>Worked interpretation example</h2><p>Consider an occupation with a relatively high digital-work baseline. If a respondent reports that routine information work is central, inputs are mostly digital, rules repeat often and AI is already widely adopted, both task automation and context risk rise. Automation pressure can therefore exceed the occupation baseline.</p><p>The same title can produce a different result when the respondent owns regulated outcomes, handles unusual cases, maintains long-term relationships or performs on-site work. Human advantage rises and automation pressure falls even though the occupation baseline has not changed. Seniority adjustments also move the scores because junior task mixes are often more execution-heavy while senior roles more often carry judgment and accountability.</p><p>This example demonstrates what the tool is designed to do: reveal which assumptions drive the output. It does not prove that either worker will keep or lose a job.</p></section>
  <section class="article-section"><h2>Calibration and interpretation</h2><p>The weights are editorial model parameters designed to keep the result interpretable and sensitive to actual work. They have not been validated as a causal forecast of layoffs. A 70 exposure score does not mean a 70% probability of replacement, and differences of a few points should not be treated as statistically significant.</p><p>Use the scores to compare task patterns, identify where human review matters and plan experiments. Do not use them as the sole basis for employment, education, financial or legal decisions.</p></section>
  <section class="article-section"><h2>Known limitations</h2><ul><li>Occupation averages hide differences between employers, countries and specialties.</li><li>AI capability and adoption can change faster than the data snapshot.</li><li>The model does not estimate labour demand, wages, regulation or employer strategy.</li><li>Self-reported task estimates may be incomplete or biased.</li><li>Physical robotics exposure is not modelled in the same depth as generative AI exposure.</li></ul></section>
  <section class="article-section"><h2>Privacy and reproducibility</h2><p>The calculation runs in the browser. Answers are not submitted to the site. A shared result URL contains only the selected occupation slug, the five displayed scores and the model version; it excludes task answers, country, career level and goal. See the <a href="/privacy/">privacy notice</a> for details.</p><p>The formulas above correspond to Model ${MODEL_VERSION}. Material scoring changes will increment the model version and be recorded here.</p></section>
  <section class="article-section"><h2>Update policy and model history</h2><p>Occupation-data refreshes update the snapshot date. Changes to coefficients, task families, context questions, fallback values or score interpretation require a model-version change. Copy edits, accessibility improvements and corrections that do not change a result may be released without incrementing the model.</p><p><strong>Model ${MODEL_VERSION}, July 2026:</strong> initial public scoring model with six task families, six context factors, career-level adjustments, four component scores and a weighted Job Resilience Score. The public occupation index contains 4,861 normalised titles from 13 represented countries.</p><p>When results from different model versions are compared, the version should be reported with the score. Shared-result links reject unknown model versions instead of silently interpreting them with newer logic.</p></section>
  <section class="article-final-cta"><h2>Test the model against your work</h2><p>The occupation baseline is only the first input. The assessment becomes more useful when you describe what fills your week.</p><a class="button button-primary" href="/#assessment-tool">Start the assessment</a></section>
</main>`;

const infoPages = [
  {
    slug: 'methodology', title: 'AI Job Resilience Methodology and Scoring Model',
    description: 'See the data inputs, formulas, weights, limitations and privacy design behind the Job Resilience Score.',
    body: methodologyBody
  },
  {
    slug: 'about', title: 'About Is My Job AI-Proof?',
    description: 'Why this independent AI job resilience assessment exists, what it covers and how it approaches uncertainty.',
    body: `<main class="article-shell prose-page"><header class="article-hero"><p class="eyebrow">About the project</p><h1>A practical tool for a question with no certain answer</h1><p class="article-lede">Is My Job AI-Proof? is an independent, free self-assessment built to help people separate task exposure from job replacement claims.</p></header><section class="article-section"><h2>What we are trying to do</h2><p>AI discussions often collapse several different ideas into one frightening number. This tool separates exposure, automation pressure, augmentation upside and human advantage so a person can see where change may occur and what they can do next.</p><p>The site is intentionally lightweight. It does not require an account, does not ask for a name and calculates personal results in the browser.</p></section><section class="article-section"><h2>How the work is maintained</h2><p>The project team maintains the occupation index, scoring code and explanatory content. Model assumptions and formulas are published on the <a href="/methodology/">methodology page</a>. Corrections should be evaluated against the dataset and model version rather than silently changing historical interpretations.</p><p>No claim on this site should be understood as individual career advice or a guaranteed forecast.</p></section><section class="article-section"><h2>Our standards</h2><p>We distinguish AI exposure from replacement probability, label baseline estimates, date material updates and avoid presenting model outputs as official statistics. The <a href="/editorial-policy/">editorial policy</a> explains these standards in more detail.</p></section><section class="article-final-cta"><h2>Start with your actual tasks</h2><p>A job title is a useful baseline, not a verdict.</p><a class="button button-primary" href="/#assessment-tool">Take the assessment</a></section></main>`
  },
  {
    slug: 'editorial-policy', title: 'Editorial and Data Policy',
    description: 'The standards used to write, review, update and label AI job-risk content on Is My Job AI-Proof?.',
    body: `<main class="article-shell prose-page"><header class="article-hero"><p class="eyebrow">Editorial policy</p><h1>Clear labels, visible assumptions, no false certainty</h1><p class="article-lede">Our editorial standard is to make every score interpretable, dated and proportionate to the evidence behind it.</p></header><section class="article-section"><h2>Core rules</h2><ul><li>We call model outputs estimates, baselines or planning indicators.</li><li>We do not describe an exposure score as a probability of job loss.</li><li>We identify the model and data snapshot used for generated occupation pages.</li><li>We publish scoring formulas and material limitations.</li><li>We do not fabricate expert review, popularity data or source attribution.</li></ul></section><section class="article-section"><h2>Generated occupation pages</h2><p>Occupation pages are generated from a curated list and the same compact dataset used by the assessment. Their task examples combine occupation-specific editorial entries with category-level patterns. They are reviewed as product guidance, not presented as official occupational standards.</p></section><section class="article-section"><h2>Updates and corrections</h2><p>Material scoring changes require a model-version update. Data refreshes carry a new snapshot date. Typographical and accessibility corrections may be released without changing the model version. Pages should be removed or consolidated when their occupation match is ambiguous or their content cannot add useful context.</p></section><section class="article-section"><h2>Commercial independence</h2><p>Assessment scores are not raised or lowered in exchange for payment. Any future sponsorship, affiliate relationship or paid placement must be visibly labelled and kept separate from scoring logic.</p></section></main>`
  },
  {
    slug: 'privacy', title: 'Privacy Notice',
    description: 'Learn what the AI job resilience assessment processes, what stays in your browser and what a shared result URL contains.',
    body: `<main class="article-shell prose-page"><header class="article-hero"><p class="eyebrow">Privacy</p><h1>Your assessment answers stay in your browser</h1><p class="article-lede">The tool is designed to provide a useful result without an account and without submitting your questionnaire answers to the site.</p></header><section class="article-section"><h2>Assessment data</h2><p>Your occupation selection, task sliders, career level, work context, optional country and goal are processed by JavaScript in your browser. The assessment does not send those answers to an application database.</p></section><section class="article-section"><h2>Shared results</h2><p>When you choose Share result, the generated URL includes only the occupation slug, the five displayed scores and Model ${MODEL_VERSION}. It does not include task answers, country, career level or goal. Anyone with the URL can see those summary scores. Web servers and analytics services may record requested URLs, so do not add personal information to a shared link.</p></section><section class="article-section"><h2>Result cards</h2><p>Result-card images are generated locally with the browser Canvas API. The site does not upload the image. Your browser or operating system handles the share or save action you choose.</p></section><section class="article-section"><h2>Operational logs and measurement</h2><p>The hosting provider may retain standard security and access logs. The site exposes privacy-minimised product events such as assessment start, result view and share action; these events contain no questionnaire answers. If analytics is enabled by the operator, its own retention and consent configuration also applies.</p></section><section class="article-section"><h2>Your choices</h2><p>You can use the assessment without specifying a country, avoid creating a shared URL, or close the page to clear the in-memory assessment state. No email address is required.</p></section></main>`
  }
];

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });
for (const file of files) await copyFile(resolve(root, file), resolve(dist, file));
await cp(resolve(root, 'data'), resolve(dist, 'data'), { recursive: true });

const occupationPayload = JSON.parse(await readFile(resolve(root, 'data/occupations.json'), 'utf8'));
const bySlug = new Map(occupationPayload.occupations.map((job) => [job.slug, job]));
const featuredJobs = featuredSlugs.map((slug) => bySlug.get(slug));
const missing = featuredSlugs.filter((slug, index) => !featuredJobs[index]);
if (missing.length) throw new Error(`Featured occupation slugs not found: ${missing.join(', ')}`);

const fullPayload = JSON.parse(await readFile(resolve(root, '../site/src/data/occupations_v2.json'), 'utf8'));
const sourceGroups = new Map();
for (const occupation of fullPayload.occupations) {
  const group = sourceGroups.get(occupation.slug) || [];
  group.push(occupation);
  sourceGroups.set(occupation.slug, group);
}
for (const job of occupationPayload.occupations) {
  const countryRank = (code) => code === 'US' ? 0 : code === 'AU' ? 1 : 2;
  const candidates = (sourceGroups.get(job.slug) || []).sort((a, b) => countryRank(a.country) - countryRank(b.country));
  const source = candidates.find((item) => {
    const summary = item.i18n?.['zh-CN']?.summary;
    return typeof summary === 'string' && summary.length > 50 && /^[\x00-\x7F\s]+$/.test(summary);
  });
  if (source) job.roleSummary = source.i18n['zh-CN'].summary.split(/(?<=[.!?])\s+/)[0];
}

const similarityStopWords = new Set(['and', 'or', 'the', 'of', 'in', 'for', 'to', 'with', 'other', 'general', 'related', 'not', 'elsewhere', 'classified']);
const normaliseToken = (token) => token === 'engineering' ? 'engineer'
  : token.endsWith('ies') && token.length > 4 ? `${token.slice(0, -3)}y`
    : token.endsWith('s') && !token.endsWith('ss') && token.length > 4 ? token.slice(0, -1)
      : token;
const titleTokens = (name) => new Set((name.toLowerCase().match(/[a-z0-9]+/g) || [])
  .map(normaliseToken).filter((token) => !similarityStopWords.has(token)));
const jaccard = (left, right) => {
  let intersection = 0;
  for (const token of left) if (right.has(token)) intersection += 1;
  return intersection / (left.size + right.size - intersection || 1);
};
const pageCandidate = (job) => /^[\x20-\x7E]+$/.test(job.name)
  && /^[a-z0-9]/i.test(job.name)
  && job.name.length >= 3
  && job.name.length <= 72
  && !/not elsewhere classified|undefined|unknown|miscellaneous/i.test(job.name)
  && job.slug !== 'occ'
  && job.roleSummary
  && titleTokens(job.name).size > 0;
const qualityScore = (job) => (job.countries.length * 5)
  + (job.roleSummary.length >= 80 ? 4 : 0)
  + (job.name.split(/\s+/).length <= 5 ? 3 : 0)
  - (job.name.length / 100);

const selectedJobs = [...featuredJobs];
const selectedSlugs = new Set(featuredSlugs);
const selectedTokenSets = selectedJobs.map((job) => titleTokens(job.name));
const selectedSignatures = new Set(selectedTokenSets.map((tokens) => [...tokens].sort().join('|')));
const pools = new Map();
for (const job of occupationPayload.occupations.filter(pageCandidate)) {
  if (selectedSlugs.has(job.slug)) continue;
  const pool = pools.get(job.category) || [];
  pool.push(job);
  pools.set(job.category, pool);
}
for (const pool of pools.values()) pool.sort((a, b) => qualityScore(b) - qualityScore(a) || a.name.localeCompare(b.name));

const categories = [...pools.keys()].sort();
const additionalTarget = 500;
for (const threshold of [.58, .68, .78, .9]) {
  let addedThisPass = true;
  while (selectedJobs.length < featuredJobs.length + additionalTarget && addedThisPass) {
    addedThisPass = false;
    for (const category of categories) {
      const candidate = pools.get(category).find((job) => {
        if (selectedSlugs.has(job.slug)) return false;
        const tokens = titleTokens(job.name);
        const signature = [...tokens].sort().join('|');
        if (selectedSignatures.has(signature)) return false;
        return selectedTokenSets.every((chosen) => jaccard(tokens, chosen) < threshold);
      });
      if (!candidate) continue;
      const tokens = titleTokens(candidate.name);
      selectedJobs.push(candidate);
      selectedSlugs.add(candidate.slug);
      selectedTokenSets.push(tokens);
      selectedSignatures.add([...tokens].sort().join('|'));
      addedThisPass = true;
      if (selectedJobs.length === featuredJobs.length + additionalTarget) break;
    }
  }
}
if (selectedJobs.length !== featuredJobs.length + additionalTarget) {
  throw new Error(`Could only select ${selectedJobs.length - featuredJobs.length} distinct additional occupations; expected ${additionalTarget}.`);
}

let maximumTitleSimilarity = 0;
let nearDuplicatePairs = 0;
for (let left = 0; left < selectedTokenSets.length; left += 1) {
  for (let right = left + 1; right < selectedTokenSets.length; right += 1) {
    const similarity = jaccard(selectedTokenSets[left], selectedTokenSets[right]);
    maximumTitleSimilarity = Math.max(maximumTitleSimilarity, similarity);
    if (similarity >= .58) nearDuplicatePairs += 1;
  }
}

for (const job of selectedJobs) {
  const directory = resolve(dist, 'job', job.slug);
  await mkdir(directory, { recursive: true });
  await writeFile(resolve(directory, 'index.html'), jobPage(job), 'utf8');
}
for (const page of infoPages) {
  const directory = resolve(dist, page.slug);
  await mkdir(directory, { recursive: true });
  const canonical = `${SITE_URL}/${page.slug}/`;
  await writeFile(resolve(directory, 'index.html'), shell({
    title: page.title, description: page.description, canonical, body: page.body,
    schema: breadcrumb(page.title, canonical)
  }), 'utf8');
}
const rankingDirectory = resolve(dist, 'rankings');
await mkdir(rankingDirectory, { recursive: true });
await writeFile(resolve(rankingDirectory, 'index.html'), rankingPage(selectedJobs), 'utf8');

const lastmod = new Date().toISOString().slice(0, 10);
const urls = ['/', '/rankings/', ...infoPages.map((page) => `/${page.slug}/`), ...selectedJobs.map((job) => `/job/${job.slug}/`)];
const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((path) => `  <url><loc>${SITE_URL}${path}</loc><lastmod>${lastmod}</lastmod></url>`).join('\n')}\n</urlset>\n`;
await writeFile(resolve(dist, 'sitemap.xml'), sitemap, 'utf8');
await writeFile(resolve(root, 'sitemap.xml'), sitemap, 'utf8');

const llms = `# Is My Job AI-Proof?\n\n> A free, task-level AI job resilience self-assessment. Scores are planning indicators, not job-loss probabilities.\n\n- [Assessment](${SITE_URL}/)\n- [AI Job Exposure Rankings](${SITE_URL}/rankings/): Browse and compare all ${selectedJobs.length} distinct occupation baselines.\n- [Methodology](${SITE_URL}/methodology/): Inputs, formulas, weights and limitations for Model ${MODEL_VERSION}.\n- [About](${SITE_URL}/about/)\n- [Editorial policy](${SITE_URL}/editorial-policy/)\n- [Privacy](${SITE_URL}/privacy/)\n\n## Occupation Baselines\n\n${selectedJobs.map((job) => `- [Is ${job.name} AI-proof?](${SITE_URL}/job/${job.slug}/)`).join('\n')}\n\n## Interpretation\n\nAI exposure measures how much work current generative AI can reach. Automation pressure also considers workflow and adoption. Human advantage reflects trust, accountability, physical context and judgment. Augmentation upside estimates where AI can improve work while a person remains responsible.\n\nData snapshot: ${DATA_SNAPSHOT}\nModel version: ${MODEL_VERSION}\nPrivacy: Questionnaire answers remain in browser memory and are not uploaded.\n`;
await writeFile(resolve(dist, 'llms.txt'), llms, 'utf8');
await writeFile(resolve(root, 'llms.txt'), llms, 'utf8');

for (const required of ['index.html', 'robots.txt', 'sitemap.xml', 'llms.txt', 'methodology/index.html', 'rankings/index.html', 'job/accountant/index.html', 'data/occupations.json']) {
  await stat(resolve(dist, required));
}
const categoryCounts = Object.fromEntries(categories.map((category) => [category, selectedJobs.filter((job) => job.category === category).length]));
console.log(`Production site written to ${dist}: ${selectedJobs.length} occupation pages, ${infoPages.length} information pages, 1 ranking page.`);
console.log(`Occupation page distribution: ${JSON.stringify(categoryCounts)}`);
console.log(`Title diversity: maximum Jaccard similarity ${maximumTitleSimilarity.toFixed(2)}, pairs at or above 0.58: ${nearDuplicatePairs}.`);
