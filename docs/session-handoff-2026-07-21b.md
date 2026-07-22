# 会话交接 · 2026-07-21b（aijobrisk.com 全新 SSR 站落地 + 设计稿实现）

> 接续 `docs/session-handoff-2026-07-21.md`（industries 数据固化 + theme.css + 设计探索稿，待落地）。
> 本会话按 `aijobrisk-design/deepseek/` 设计稿，**新建独立目录 `aijobrisk/`** 把 aijobrisk.com 全站页面用 **Astro SSR** 实现，并逐页对齐指定 mockup 的视觉风格。
> **全部未 commit**（用户手动提交）。恢复请读本文件 + memory [[aijobrisk-ssr-site]]。

---

## 用户 5 条要求（贯穿全程）
1. 统一用 `aijobrisk-design/deepseek/index.html` + `job-detail.html` 的**蓝系配色**（= `aijobrisk-design/theme.css` token），其它 mockup（rankings.html 暖灰、bookkeeper-vs-accountant.html 深色）只借布局、**一律改蓝**。
2. **SSR**。
3. **复用** site 的 `job-risk-map`。
4. **不多做翻译，英文兜底**。
5. 职业详情页：**职业为主 + 国家放 tab**，薪资/教育/资质/签证等在国家 tab 下。

后续追加：职业详情第一屏用 `job-detail.html` 风格；排行榜详情用 `ranking-item.html`；对比结果页用 `bookkeeper-vs-accountant.html`（配色仍蓝）；FAQ 加通用「2030」问句并 Azure 译 7 语言。

---

## 一、新建 `aijobrisk/` 独立 SSR 项目（完全独立 = 全部复制）

- **技术栈**：Astro `^4.16` + `@astrojs/node` standalone，`output:'server'`。`astro.config.mjs` / `package.json` / `tsconfig.json` 已建。dev 端口 **4331**（根 `.claude/launch.json` 配置名 `aijobrisk-dev`，用 `npm --prefix ./aijobrisk run dev`）。`preview` 脚本 = `node ./dist/server/entry.mjs`。
- **数据层复制**（与 `site/` 解耦）：`aijobrisk/src/data/` 复制了 `occupations_v2.json`(23MB)、`occ-detail-v2/`、`categories_v2/industries_v2/occ_industries_v2/outline-paths/ui_i18n/polls/hot_occupations`；**未**复制 `translations-v2/` → `tr(..,'en')` 回退英文母本（`i18n['zh-CN']` 装的就是英文母本，见 data.ts 顶注）。
- **lib 复制**：`data.ts`(原样)、`riskmap.ts`(原样)、`site-config.ts`、`polls.ts`；**新增** `ui.ts`(expBand 百分位分档 / riskBand10 十分制 / fmtSalary / fmtNum)、`rankings.ts`(6 榜)、`industries.ts`(行业轴)、`riskmap-meta.ts`(由 layout 生成 RiskMap tooltip meta)。
- **组件复制**：`RiskMap.astro` / `RatingRadar.astro` / `PollBlock.astro`。
- **配色桥接**（关键）：新建 `Base.astro`（顶部固定白导航 + logo.svg + 页脚 + Font Awesome CDN），全局 CSS 定义 theme.css token，**并给复用组件加别名**：`--card→--surface`、`--white→--text`、`--muted→--text-muted`、`--green→--brand`、`--hero→--surface-tint-2`、`--amber→--risk-mid`、`--border→--line`。故 RiskMap/RatingRadar/PollBlock **零改样式**即变蓝系。

### RiskMap 改造（SSR 适配）
`RiskMap.astro` 原来 tooltip meta 走 `fetch(metaUrl)` 外置 JSON、nav 链接指向旧站 URL。改为：**SSR 内联** `<script define:vars={{M: meta}}>`（无需端点），nav 链接改新路由 `/job-risk-map` 与 `/job-risk-map/{cc}`。已验证 tooltip 正常（hover 出「职业/分类/人数/AI风险/薪资」）。

### 页面清单（全站，SSR 无 getStaticPaths）
| 路由 | 说明 | mockup |
|---|---|---|
| `/` | 首页(hero+搜索+榜单预览+explore+热门+FAQ+来源) | index.html |
| `/[category]/[slug]` | **职业详情**(职业为主 + 国家 tab `?country=CC` 服务端切换) | index.html + job-detail.html(第一屏) |
| `/industries` `/industry/[sector]` | 行业总览 + 可排序职业表 | industries.html / industry-detail.html |
| `/rankings` `/rankings/[board]` | 6 榜 hub + 榜单详情 | rankings.html / **ranking-item.html** |
| `/compare` `/compare/[pair]` | 对比 hub + **对比结果页** | **bookkeeper-vs-accountant.html** |
| `/job-risk-map` `/job-risk-map/[country]` | 全球/各国风险图(复用 RiskMap) | — |
| `/search?q=` `/about` `/methodology` `/404` | 搜索/关于/方法论/404 | — |
`[category]` 段仅装饰，按 `slug` 查找。榜单/行业默认国 **US**（mockup 口径，真实官方薪资），`?country=` 切换。

---

## 二、职业详情第一屏 → `job-detail.html` 风格
`[category]/[slug].astro` 第一屏重构成白色圆角 `.detail-section` 卡：`.detail-header`(H1 + `Occupation baseline · updated {date}` pill + 分类/代码/N国 meta-pills) + 右侧大号 `.risk-badge-lg`(暴露百分位 + 档位色) + `.risk-meter`(标签+渐变条+数值 + **三连概要 pill**：🔴Replaces/🟢Augments/🔵Moat 各取该职业真实首项) + 一句 verdict + 4 项评分条 + 行动按钮。下方全球 AI 区 / 国家 tab / 国家面板不变。

## 三、排行榜详情 → `ranking-item.html`（改蓝）
`rankings/[board].astro` 重构：渐变 `.page-header`(图标+H1+国家+副标 + `.stats-row` 高/中/低风险占比 + 更新日期，占比按该国全部职业暴露实时算) + `.filter-bar`(档位 All/High/Mid/Low **客户端过滤** + 国家 select + mini 搜索) + `.rank-table`(前 3 名金/银/铜、职业+分类+暴露 tag、暴露渐变条、护城河徽章 Strong/Moderate/Weak、**主指标列随榜单变**、View→) + 窄屏 `data-label` 卡片降级 + `.rank-footer` + FAQ + FAQPage schema。**主指标列自适应**：workforce→Workforce、demand→Demand、其余→Avg salary（已验证）。**未做**：mockup 的「趋势 +12%」列（无趋势数据，用主指标列替代，不编造）、真实分页。

## 四、对比结果页 → `bookkeeper-vs-accountant.html`（结构照搬，配色改蓝）
`compare/[pair].astro` 重构（丢弃原雷达版）：H1 + 2×`.score-card`(职业名+大号 X/10 任务暴露+High/Mid/Low 徽章+副行「暴露百分位·护城河·国家」) + `.verdict`(**数据派生**一句话) + Tasks most exposed(两栏红标真实 replaced 列表) + Where AI augments(两栏绿标 augmented) + Human moat(要点 + Shallow/Moderate/Deep 进度条=真实 human_moat/10) + Other dimensions(薪资/学历路径/考证门槛/前景/需求/综合) + FAQ`<details>`。
- **诚实性**：mockup 的逐任务百分比标注 illustrative（编造），改用**真实任务列表**，只有真实数字才画条。
- **修一个真 bug**：`avg_salary` 在数据里是**字符串**(`"106600.00"`)，`>=` 做了**字典序**比较导致「谁薪资高」判反（`'7'>'1'` 使 7 万 > 10 万）。改 `Number()` 数值比较修复。排行榜/行业排序用减法算术，不受影响。

## 五、职业详情 FAQ 增通用「2030」问句 + Azure 7 语言
- **语法纠正**：采用 `Will AI replace {occupation} by 2030?`（最自然）。其余：`be taken`→应 `be taken over by AI`；`be replaced in 2030`→建议补 `by AI`；`take over … in 2030`→`by 2030` 更贴切。
- **Azure 翻译**（`scripts/translate_faq_2030.py`）：从英文母本译 **es/fr/de/pt/ja/zh-Hans/ko** 7 种主流语言。**跨职业通用**关键：用 HTML `notranslate` span 包 `{name}` 占位符，Azure 保留占位并放到各语言正确语法位；渲染时替换英文职业名 → 一次翻译全职业复用。产物 `aijobrisk/src/data/faq_2030.json`。
- **落地**：每职业详情 FAQ **第一条**(默认展开)：英文问句 + **数据驱动答案**(暴露档/百分位/护城河 + 该职业 AI 结论，不编造) + 「ALSO ASKED AS:」7 语言列表(带 `lang` 属性)。FAQPage JSON-LD 把这条排首位。Azure 凭据在根 `.env`（`AZURE_TRANSLATOR_KEY/REGION/ENDPOINT`），封装参考 `video_pipeline/azure_translate.py`。

---

## 六、⚠ 待办 / 待决
1. **全部未 commit**（连同上游 07-21/07-17/16d）。数据 JSON(23MB)因「完全独立」随 `aijobrisk/` 提交；`.gitignore` 已忽略 node_modules/dist/.astro。
2. **深浅主题**：mockup 是浅色，现站以浅色为主（theme.css 有深色变量但未接切换按钮）。
3. **2030 FAQ**：答案(A)仍英文（用户只要求译问句）。若要答案也多语言 / 改折叠 / 只留结构化数据不显示，再说。
4. **排行榜**：真实分页、趋势列（需趋势数据源）未做。
5. **主站迁移**（07-17b 待办仍在）：aicareergraph→aijobrisk 品牌/域名/301；logo.svg 接进 site 主站 `Base.astro` 未做。
6. 生产部署：`npm run build` 后 `node ./dist/server/entry.mjs`，可套现有 Docker/nginx（`site/` 有样板）。

> 关键文件：`aijobrisk/`（整个新项目）、`aijobrisk/src/lib/{ui,rankings,industries,riskmap-meta}.ts`、`aijobrisk/src/pages/**`、`aijobrisk/src/layouts/Base.astro`、`aijobrisk/src/data/faq_2030.json`、`scripts/translate_faq_2030.py`、根 `.claude/launch.json`（加了 aijobrisk-dev）。
> 见 memory [[aijobrisk-ssr-site]] [[multi-domain-architecture]] [[design-exploration-decoupled]] [[occupation-industry-relation]] [[azure-translator-backend]] [[flag-rendering-rule]]。
