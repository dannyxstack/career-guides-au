# 会话交接 · 2026-07-16d（job-treemap：诚实性修复 + SEO 大改 + /country 路由 + 静态图/embed/记者页 + 折叠表）

> 接续 `docs/session-handoff-2026-07-16c.md`（每国独立 URL + 静态第二屏 + 国旗 + hover 修复）。
> 前置：16c 的改动用户已手动 commit。**本会话全部改动用户将手动 commit**（`job-treemap/{build.py,template.html}`、
> `scripts/shoot_maps.mjs`、`docs/nginx-301-treemap-country.conf`、`package.json`/`package-lock.json`/`node_modules`、
> `dist/` 靠部署流程推）。
> 本会话把 job-treemap 从「每国 SEO 页」进一步升级成 **多页 SEO 站 + 静态图资产 + 记者/嵌入生态**，并修多处诚实性/布局问题。

---

## 一、按时间顺序的改动（每条=用户一次需求）

### 1. 诚实性修复（延续"事实语义错误"清理）
- **薪资标注**：`avg_salary` 实为**均值**（`occupations_v2.json` 无中位数字段），页面却写 "Median pay" → 双重错误。
  改为 **"Average annual pay"**（tooltip/详情面板/第二屏表头 3 处）。想要真中位数需改导出管线 `occupation_salaries band=median`，超范围未做。
- **方法论过度绝对**：`build.py` 里 4 处改保守——lead "is not our opinion" → "derived from published exposure research,
  occupational crosswalks and… clearly identified model-assisted mappings"；"two peer-reviewed / institutional studies" →
  "two published research datasets"；"(the same approach the ILO study used)" → "(a clearly identified model-assisted mapping)"；
  第二屏 "two open, peer-reviewed datasets" → "published research datasets"。

### 2. llms.txt
- `build_llms()` 生成 `dist/llms.txt`（Markdown 给 AI 爬虫）：站点简介 + 13 国页链接(职业数/人数/加权暴露) + methodology + dataset。

### 3. SSR = 方案 C（不真 SSR，补足首屏可爬性）
- 现状本就是 SSG（`build.py` 写静态 HTML），第二屏已静态可爬；唯一客户端渲染是 canvas。故只补**首屏**：
  - `__H1__`（国别化，与 JS 运行时 `AI Exposure of the {country} Job Market` 同款）、`__SUBTITLE__`（职业数等，替换 "Loading..."）、
    `__STAT_TOTALJOBS__`/`__STAT_AVGEXP__`（预填真值替换 "—"）。
  - `__NOSCRIPT__`：canvas 无 JS 时的兜底块（提示需 JS + 锚点跳 `#industries`）。
  - JS 加载时会重设这些值（一致，无冲突）。

### 4. URL 重构 → `/country/{slug}/`（**两周内第二次迁移**）
- 目录 `dist/{slug}/` → `dist/country/{slug}/`；canonical/og:url/sitemap/落地卡片/国家下拉框/第二屏跨国链接/llms.txt 全同步。
- 常量：`country_path()/country_url()`；`ORDER/SLUG` 不变。清理旧 `dist/{slug}`、`dist/country`、`dist/embed`（保留 `static/`）。
- **修 URL 迁移遗漏 bug**：第二屏 "Other countries" 链接曾漏改仍是 `/{slug}/`，已修为 `/country/{slug}/`。
- 301：`docs/nginx-301-treemap-country.conf`（旧 `/{slug}/`→`/country/{slug}/`；**不再** 301 about→methodology，因 about 现独立）。

### 5. /methodology 页（原 about → methodology）
- `ABOUT_HTML`→`METHODOLOGY_HTML`，title/canonical/og 改 `/methodology.html`；加 "Download the data"（链 dataset.csv）+ "Read the source papers"（ILO 140 / OpenAI 论文链接）。

### 6. dataset.csv
- `write_dataset_csv()` → `dist/dataset.csv`（一行一职业×13 国：country/code/occupation/occ_code/category/exposure_0_10/percentile/avg_annual_pay/workforce）。methodology/llms/Dataset schema/footer 均引用。

### 7. JSON-LD（注入 `<head>` 的 `__JSONLD__`）
- **Dataset**：首页 `dataset_ld_global`（全球 13 国）+ 每国 `dataset_ld_country`（PNG 存在时自动加 image/png distribution）。
- **BreadcrumbList**：每国页（仅 schema 不显示面包屑，position 1/2；用户示例 1/3 是笔误）。
- FAQPage **未做**（依赖 LLM 文案，见待办）。

### 8. Playwright 静态图（真机已跑）
- `scripts/shoot_maps.mjs`：起内置静态服务 → 加载 `/embed/{slug}` 裸图页 → 截 `#canvas` → `dist/static/maps/ai-job-risk-map-{slug}-{YEAR}.png`。
  viewport 1600×1200 ×2.5 DPR。可选 WebP（需 `sharp`，未装故跳过）。**依赖**：`npm i -D playwright && npx playwright install chromium chromium-headless-shell`（已装）。
- **已生成 13 张 PNG（3400×3000，各 ~0.8MB）**，质量优（满屏彩色 treemap 带标签）。设计为你的**每晚 cron**：`build.py`→`shoot_maps.mjs`→再 `build.py`（让新图进 og/gallery/schema）。
- build.py 接图：`map_filename()`；PNG 存在则该国 **og:image/twitter:image** 换成该 PNG + Dataset PNG distribution。

### 9. /embed 记者页 + /embed/{slug} 裸图页
- **`/embed`**（`build_embed_hub`，index,follow）：① 国家下拉 → JS 生成 iframe 代码 + Copy；② 13 图下载网格(Download PNG，CC BY 4.0)；③ 引用话术 Plain/HTML 两版随国联动真实数据 + Copy；④ 数据源链 methodology/dataset；⑤ Custom Map 表单 → **mailto:hello@aijobriskmap.com**（静态站无后端，待接端点）。title/H1 定位为 "Embed & Download AI Job Risk Maps"。
- **`/embed/{slug}`**：复用模板 **embed-mode**（`<body class="embed">` 隐藏侧栏/第二屏/footer，canvas 满宽），`noindex,follow`，`dataUrl` 复用 `/country/{slug}/data.json`，`__STATIC_CONTENT__/__FOOTER__` 置空。**不入 sitemap**（避免重复内容）。

### 10. about 页（独立重建，与 methodology 并存）
- `build_about()`：这是什么/给谁用/有何不同/独立性与许可/延伸阅读。与 methodology（"怎么算"）区分。sitemap 含 about+methodology+embed。

### 11. 全站底部 footer（单一来源）
- `build_footer()`（自带作用域 `<style>`）注入所有页：链接组 **Home · Download & embed · Methodology · About · Dataset (CSV)** + 版权行(© YEAR + CC BY/MIT + 独立声明)。
- 首页原突兀的 Download `.cta` 独立行删除，改由 footer 链接承载（删死 CSS `.cta/.foot/.txt`）。embed 裸页**不含 footer**。

### 12. 国家页 "Embed this map" → 弹层
- 第二屏下载卡的按钮从 `<a href="/embed">` 改 `<button id="embedBtn">` → 触发模态框(`#embedModal`)显示该国 iframe 代码 + **Copy code** + 关闭(× / 点遮罩 / Esc)。代码经 `CONFIG.embedSnippet` 注入。

### 13. 首屏交互图 vs 第二屏静态图"重复"优化（2A）
- 国家页静态图从第二屏**顶部**移到**最底部**（Methodology 之后），从满宽大图改 **400px "下载卡"**（缩略图+图注+Download PNG/Embed 按钮），标题 "Download / share this map"。保留可爬 `<img>`+alt+caption（图片 SEO 不损）。

### 14. 首页 download 突兀 → 收敛到 /embed（3A）
- 首页**删 13 图 gallery**（去重复，回归导航主题），只留 footer 里一个 "Download & embed" 链接。下载体验只在 `/embed`。

### 15. 排名表横向溢出修复（折叠表）
- 根因：`.two-col` 用 `1fr 1fr`，`1fr`=`minmax(auto,1fr)` 最小=nowrap 内容 min-content → 撑宽整页。
- 方案：**去掉并排**，两表各占一行全宽；默认 **5 行**，第 6 行起 CSS `nth-child(n+6){display:none}` 折叠（**20 行全留 DOM，可爬**）；标题行尾 `.tbl-toggle` 按钮 "Show all 20"⟷"Show less"。`collapsible_table()`。
- 实测 France：`pageHorizScroll:false`(scrollW==clientW)、rowsInDOM 20、折叠 5/展开 20。

### 16. WebP 去链接
- `map_card` 及 embed 文案的 WebP 链接/字样移除（暂不实现 WebP）。脚本可选 WebP 能力保留（sharp 未装不产出）。

---

## 二、关键文件 / 新增函数（build.py）
- 常量：`DOMAIN/SITE_NAME/YEAR/DATASET_URL/SLUG`；`country_path/country_url/map_filename`。
- 页面：`build_landing`(首页 hub+全局 Dataset schema)、`METHODOLOGY_HTML`、`build_about`、`build_embed_hub`、`DOC_CSS`/`doc_head`(about/embed 共享外壳)、`build_footer`。
- 数据/资产：`build_record`(pay 读 avg_salary)、`country_stats`、`occ_table`、`collapsible_table`、`static_content`(下载卡在底部)、`fallback_summary`、`write_dataset_csv`、`build_sitemap`(含 about/methodology/embed，排除 embed/{slug})、`build_llms`、`build_og_image`。
- JSON-LD：`ld_script/dataset_ld_country/dataset_ld_global/breadcrumb_ld`。
- 模板占位符（template.html）：`__TITLE__ __META_DESC__ __CANONICAL__ __ROBOTS__ __SITE_NAME__ __OG_IMAGE__ __JSONLD__ __ABOUT_URL__ __H1__ __SUBTITLE__ __STAT_TOTALJOBS__ __STAT_AVGEXP__ __NOSCRIPT__ __STATIC_CONTENT__ __FOOTER__ __CONFIG__ __BODYCLASS__`。
- CONFIG 新增键：`embed`(bool)、`embedSnippet`、`dataUrl`(embed 用绝对 `/country/{slug}/data.json`)。

## 三、dist 产物
```
dist/
  index.html            (国家索引 landing + footer；无 gallery)
  about.html methodology.html   (独立两页)
  embed/index.html      (记者/下载 hub)
  embed/{slug}/index.html (13 裸图 iframe 页, noindex)
  country/{slug}/index.html + data.json + favicon.svg (13 国交互页)
  static/maps/ai-job-risk-map-{slug}-2026.png (13 张真图)
  dataset.csv robots.txt sitemap.xml llms.txt og-image.png favicon.svg
```

## 四、⚠ 待办 / 待决
1. **未 commit**：本会话全部改动用户手动提交（含新增 `package.json`/`package-lock.json`/`node_modules`——考虑是否 gitignore node_modules）。
2. **部署顺序**：先上 `docs/nginx-301-treemap-country.conf`（含旧 URL 301 + `/embed/*` 的 **CSP `frame-ancestors *`**，注意 `X-Frame-Options` 无 `ALLOWALL` 值，用 CSP）再切新 `dist/`。
3. **每晚 cron**：`python job-treemap/build.py` → `node scripts/shoot_maps.mjs` → 再 `build.py`（让新图进 og/gallery/schema）。
4. **Custom Map 表单**：现 `mailto:hello@aijobriskmap.com`，待决定接 Formspree 或 `api/polls_api.py`（`build_embed_hub` JS 里有 TODO）。
5. **WebP**：脚本支持，装 `sharp` 后重跑即产出（当前无 WebP 链接）。
6. **仍未做（16c/本会话讨论过但用户未拍板/未执行）**：
   - **Risk vs Exposure 术语统一 + 百分制显示**（品牌 Risk vs 指标 Exposure 混用；建议 A1 统一 Risk + `57/100` 而非 `57% Risk` 以免概率误读；aioe_pct 覆盖 99%）——**未实现**。
   - **首页 3×1000 字 SEO 文案 + 每国 FAQPage schema**（LLM 生成+缓存，像 summaries.json；严禁编造 "40%任务/human moat" 类无数据支撑的数字）——**未实现**。
   - `/job/{occ}-{country}` 空内链：已决定**暂不链**（软 404 不传权重）。
7. **H1 措辞**：`AI Exposure of the {country} Job Market`（"the Australia" 略生硬，且仍用 "Exposure"）——留待术语统一时与 JS 一起改。

## 五、关键坑
1. **网格 `1fr` 撑宽**：nowrap 表格在 `1fr` 轨道里不收缩→整页横向溢出；需 `minmax(0,1fr)` 或本会话的"去并排+折叠"。
2. **CSS 折叠不伤 SEO**：折叠行必须留 DOM（服务端渲染），只 `display:none`，爬虫可读；`nth-child(n+6)` 对 `display:block` 的滚动表格仍有效。
3. **embed-mode 复用模板**：`body.embed` 隐藏侧栏/第二屏/footer；`__FOOTER__`/`__STATIC_CONTENT__` 置空；`noindex`。
4. **static/ 保留**：`build.py` 清理旧目录时**不删 `dist/static/`**（PNG 在此），否则每次 build 都得重截。
5. **后台 Bash cwd 残留**（memory 老坑复现）：跑 `build.py` 用**绝对路径**，别依赖 cwd。
6. **Playwright headless**：`chromium.launch()` 要 `chromium-headless-shell` 变体，`npx playwright install chromium` 之外还需 `... chromium-headless-shell`。
7. **截图工具本会话持续卡死**：改用 `javascript_tool` 断言验证（scrollWidth/naturalWidth/display 等），可靠。
8. **Windows GBK**：跑 build/脚本设 `PYTHONIOENCODING=utf-8`。

> 恢复：读本文件 + memory [[job-treemap-clone]] [[genai-exposure-pipeline]] [[flag-rendering-rule]]。
> 关键产物：`job-treemap/{build.py,template.html,summaries.json}`、`scripts/shoot_maps.mjs`、`docs/nginx-301-treemap-country.conf`、`dist/`（landing+about+methodology+embed hub+13 embed 裸页+13 国+static/maps 13 PNG+dataset.csv+sitemap/robots/llms）。
