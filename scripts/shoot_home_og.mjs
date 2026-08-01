// 首页 OG 截图：加载已构建的 dist 首页，1200x630 视口截图，写 dist/og-home.png。
// build.py 的 landing og:image / twitter:image 指向 /og-home.png。
// 内容/气泡变动后，在 `python job-treemap/build.py` 之后重跑本脚本刷新首页大图。
//
// 依赖：npm i -D playwright && npx playwright install chromium
// 用法：node scripts/shoot_home_og.mjs

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.resolve(HERE, "..", "job-treemap", "dist");
const PORT = 8978;
const W = 1200, H = 630;

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
  if (!fs.existsSync(path.join(DIST, "index.html"))) {
    console.error("dist/index.html not found — run `python job-treemap/build.py` first.");
    process.exit(1);
  }
  const server = serveDist();
  await new Promise((r) => server.listen(PORT, r));

  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.goto(`http://localhost:${PORT}/`, { waitUntil: "networkidle" });
  // 等气泡渲染完成（JS 打包 + 布局）
  await page.waitForFunction(() => {
    const el = document.getElementById("bubbleChart");
    return el && el.querySelectorAll(".bubble").length > 30;
  }, { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(600);

  const out = path.join(DIST, "og-home.png");
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: W, height: H } });
  console.log(`  home OG -> ${path.relative(process.cwd(), out)} (${W}x${H} @2x)`);

  await browser.close();
  server.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
