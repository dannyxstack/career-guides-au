import { readFile, readdir, stat } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), 'dist');
const errors = [];
const read = (path) => readFile(resolve(root, path), 'utf8');

for (const path of [
  'index.html', 'methodology/index.html', 'about/index.html', 'editorial-policy/index.html',
  'privacy/index.html', 'sitemap.xml', 'robots.txt', 'llms.txt', 'brand-logo.png', 'favicon.ico',
  'favicon-16x16.png', 'favicon-32x32.png', 'apple-touch-icon.png', 'site.webmanifest'
]) {
  try { await stat(resolve(root, path)); } catch { errors.push(`Missing ${path}`); }
}

const home = await read('index.html');
for (const expected of [
  '<h1 id="assessment-title">Is my job AI-proof?</h1>',
  'href="/methodology/"',
  'id="share-button"',
  'href="/job/accountant/"',
  'href="/favicon.ico?v=4"',
  'href="/favicon-32x32.png?v=4"',
  'class="brand-mark" src="/brand-logo.png?v=4"'
]) if (!home.includes(expected)) errors.push(`Homepage missing ${expected}`);

const jobDirectories = await readdir(resolve(root, 'job'));
if (jobDirectories.length !== 550) errors.push(`Expected 550 occupation pages, found ${jobDirectories.length}`);
for (const slug of jobDirectories) {
  const html = await read(`job/${slug}/index.html`);
  for (const expected of ['<link rel="canonical"', 'application/ld+json', 'Exposure is not replacement probability', '/methodology/', 'href="/favicon.ico?v=4"', 'class="brand-mark" src="/brand-logo.png?v=4"']) {
    if (!html.includes(expected)) errors.push(`${slug} missing ${expected}`);
  }
}

const sitemap = await read('sitemap.xml');
const sitemapUrls = (sitemap.match(/<url>/g) || []).length;
if (sitemapUrls !== 556) errors.push(`Expected 556 sitemap URLs, found ${sitemapUrls}`);
if ((await read('robots.txt')).includes('Disallow: /data/')) errors.push('Occupation data remains blocked in robots.txt');

const rankings = await read('rankings/index.html');
const rankingRows = (rankings.match(/class="ranking-row"/g) || []).length;
const rankingLinks = new Set([...rankings.matchAll(/href="\/job\/([^/]+)\/"/g)].map((match) => match[1]));
if (rankingRows !== 550) errors.push(`Expected 550 ranking rows, found ${rankingRows}`);
if (rankingLinks.size !== 550) errors.push(`Expected 550 unique ranking links, found ${rankingLinks.size}`);
for (const expected of ['id="ranking-search"', 'id="ranking-category"', 'id="ranking-band"', 'id="ranking-sort"', '"@type":"ItemList"']) {
  if (!rankings.includes(expected)) errors.push(`Ranking page missing ${expected}`);
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else {
  console.log(`Static checks passed: ${jobDirectories.length} occupation pages and ${sitemapUrls} sitemap URLs.`);
}
