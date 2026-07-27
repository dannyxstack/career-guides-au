// Nightly static-map shooter for job-treemap.
//
// Loads each bare /embed/{slug}/ page (full-bleed treemap, no sidebar/second
// screen) from the built dist/, screenshots the canvas at high resolution and
// writes dist/static/maps/ai-job-risk-map-{slug}-{YEAR}.png (+ .webp if sharp
// is available). build.py picks these up automatically on the next build:
// they become each country's og:image, the Dataset PNG distribution and the
// homepage / embed / country-page gallery thumbnails.
//
// Usage:
//   node scripts/shoot_maps.mjs                 # all countries
//   node scripts/shoot_maps.mjs australia japan # subset (by slug)
//
// Requires: npm i -D playwright && npx playwright install chromium
// Optional (for .webp): npm i -D sharp
//
// Meant to run on a schedule (cron/Task Scheduler) after `python job-treemap/build.py`.

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.resolve(HERE, "..", "job-treemap", "dist");
const OUT = path.join(DIST, "static", "maps");
const YEAR = new Date().getFullYear();
const PORT = 8977;

// slug list — mirrors build.py SLUG (order not important).
const SLUGS = [
  "australia", "united-states", "united-kingdom", "canada", "new-zealand",
  "japan", "south-korea", "germany", "france", "spain", "italy",
  "netherlands", "ireland", "brazil", "mexico", "india", "china",
];

const MIME = {
  ".html": "text/html", ".json": "application/json", ".svg": "image/svg+xml",
  ".png": "image/png", ".csv": "text/csv", ".xml": "application/xml",
  ".txt": "text/plain", ".webp": "image/webp",
};

function serveDist() {
  return http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split("?")[0]);
    if (p.endsWith("/")) p += "index.html";
    const file = path.join(DIST, p);
    if (!file.startsWith(DIST) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404); res.end("not found"); return;
    }
    res.writeHead(200, { "Content-Type": MIME[path.extname(file)] || "application/octet-stream" });
    fs.createReadStream(file).pipe(res);
  });
}

async function main() {
  const want = process.argv.slice(2);
  const slugs = want.length ? SLUGS.filter((s) => want.includes(s)) : SLUGS;
  if (!fs.existsSync(DIST)) {
    console.error("dist/ not found — run `python job-treemap/build.py` first.");
    process.exit(1);
  }
  fs.mkdirSync(OUT, { recursive: true });

  let sharp = null;
  try { sharp = (await import("sharp")).default; }
  catch { console.warn("[maps] sharp not installed — skipping .webp variants"); }

  const server = serveDist();
  await new Promise((r) => server.listen(PORT, r));

  const browser = await chromium.launch();
  // 4:3, ~4K after deviceScaleFactor.
  const ctx = await browser.newContext({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: 2.5 });
  const page = await ctx.newPage();

  for (const slug of slugs) {
    const url = `http://localhost:${PORT}/embed/${slug}/`;
    await page.goto(url, { waitUntil: "networkidle" });
    // Let the canvas finish its treemap paint (data fetch + squarify + draw).
    await page.waitForTimeout(1800);
    const canvas = page.locator("#canvas");
    const png = path.join(OUT, `ai-job-risk-map-${slug}-${YEAR}.png`);
    await canvas.screenshot({ path: png });
    if (sharp) {
      const webp = png.replace(/\.png$/, ".webp");
      await sharp(png).webp({ quality: 82 }).toFile(webp);
    }
    console.log(`  shot ${slug} -> ${path.relative(DIST, png)}`);
  }

  await browser.close();
  server.close();
  console.log(`\nDone: ${slugs.length} maps -> ${path.relative(process.cwd(), OUT)}`);
}

main().catch((e) => { console.error(e); process.exit(1); });
