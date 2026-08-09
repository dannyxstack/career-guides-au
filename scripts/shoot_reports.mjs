// Country-report PDF printer for aijobriskmap (job-treemap).
//
// Renders each dist/reports/{slug}/report.html to a real-text, selectable PDF
// at dist/reports/{slug}/{slug}-ai-job-risk-{YEAR}.pdf via headless Chromium.
// The HTML is fully self-contained (inline CSS + base64 map image), so it loads
// straight from file:// — no dev server needed.
//
// Usage:
//   node scripts/shoot_reports.mjs                 # every built report
//   node scripts/shoot_reports.mjs australia poland # subset (by slug)
//
// Requires: playwright (already used by shoot_maps.mjs).

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";
import { chromium } from "playwright";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPORTS = path.resolve(HERE, "..", "job-treemap", "dist", "reports");
const YEAR = new Date().getFullYear();

async function main() {
  if (!fs.existsSync(REPORTS)) {
    console.error("dist/reports not found — run `python job-treemap/build_reports.py` first.");
    process.exit(1);
  }
  const want = process.argv.slice(2);
  let slugs = fs.readdirSync(REPORTS).filter((d) =>
    fs.existsSync(path.join(REPORTS, d, "report.html")));
  if (want.length) slugs = slugs.filter((s) => want.includes(s));
  if (!slugs.length) { console.error("no reports to print."); process.exit(1); }

  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const slug of slugs) {
    const src = path.join(REPORTS, slug, "report.html");
    const out = path.join(REPORTS, slug, `${slug}-ai-job-risk-${YEAR}.pdf`);
    await page.goto(pathToFileURL(src).href, { waitUntil: "networkidle" });
    await page.pdf({
      path: out,
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: true,
      headerTemplate: "<span></span>",
      footerTemplate:
        '<div style="width:100%;font-size:8px;color:#8a8d93;padding:0 14mm;display:flex;justify-content:space-between">' +
        '<span>AI Job Risk Map</span><span class="pageNumber"></span>/<span class="totalPages"></span></div>',
      margin: { top: "14mm", bottom: "16mm" },
    });
    const kb = Math.round(fs.statSync(out).size / 1024);
    console.log(`[${slug}] -> ${path.basename(out)} (${kb} KB)`);
  }
  await browser.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
