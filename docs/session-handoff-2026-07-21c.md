# 会话交接 · 2026-07-21c（aijobrisk SSR 站：路由重构 + 语言下拉 + 深浅主题 + compare 重做 + 行业 icon + 页脚）

> 接续 `docs/session-handoff-2026-07-21b.md`（aijobrisk.com SSR 站落地 + 设计稿实现）。
> 本会话按用户 6 项要求，对 `aijobrisk/` 做以**路由重构为骨架**的一批改造。**全部未 commit**（用户手动提交）。
> 恢复请读本文件 + memory [[aijobrisk-ssr-site]]。

---

## 用户 6 项要求（针对 aijobrisk.com / 目录 `aijobrisk/`）

1. 增加深浅主题切换。
2. nav 增加语言选择下拉框。
3. 职业详情 FAQ 中关于 AI 的问题下去掉多国语言并列，只保留当前所选语言；翻译改由 **nav 切换语言**时变换，而非页面内展示多语言。
4. 按 `aijobrisk-design/deepseek/compare.html` 重做职业比较页面（下拉可**搜索职业**），替代当前 `/compare`。
5. 排行榜/首页/行业/职业比较页，所有 `{industry}` 前带一个小 icon（同 index.html 热门卡 `.job-industry i` 的样式）。
6. 所有页面底部加带 copyright 的页脚（可与 `site/` 一致）。

**开工前询问 + 用户定的 3 个决策**：
- 翻译范围 = **仅可译内容**（FAQ 2030 问句 / 国家名 / 走 `strings()`·`tr()` 的内容按语言切换；页面硬编码英文 UI 与职业正文英文兜底，因 `translations-v2/` 未复制）。
- 语言保持 = **路径路由规则**（用户明确指定）：英文全站无前缀；其余 `/{lang}/` 开头（**语言第一级**）；国家放**最后一级**。职业 `/{lang}/jobs/{occupation}/[{country}]`；行业 `/{lang}/industries/[{country}]` 与 `/{lang}/industry/{industry}/[{country}]`。**并要求写入 RULES.md**（已写，见 `RULES.md` 新增「aijobrisk.com（aijobrisk/ SSR 站）路由规约」小节）。
- 行业 icon = **按行业映射**（复用/新增图标表，非统一一个）。

---

## 一、路由重构（骨架，影响全站内部链接）

**目标结构**：语言第一级（en 裸、其余 `/{lang}/`）、国家最后一级（取代旧 `?country=`）。

- **踩坑 1**：Astro 4.16 内置 i18n(`prefixDefaultLocale:false`) 在 **SSR 下不自动双发** `/{lang}/*`（实测 `/es/*` 全 404）。→ 弃用 i18n 配置，改用**自写中间件** `src/middleware.ts`：识别首段是否 8 语言之一 → 写 `context.locals.locale` → `context.rewrite()` 到**去前缀**的裸路径，复用同一套页面文件（无需复制）。`astro.config.mjs` 的 `i18n` 块已删除。
- **踩坑 2**：Astro **不支持 `[[param]]`**（单段可选），报 `parameter name must match`。→ 可选「国家末级」用 **rest 参数** `[...country].astro`；页面 `Astro.params.country` 拿到 `US`（无则 `undefined`），对 `COUNTRIES` 校验，非法回退默认国。
- **中间件 rewrite 后 `Astro.url.pathname` 已是裸路径**（前缀被剥），故 `Base.astro` 里 `bare` 直接用它；`pageLocale(Astro)` 改为**优先读 `Astro.locals.locale`**，再 `currentLocale`，再 URL 首段兜底。canonical 改 `withL(loc, bare)` 自指。

**文件移动**（旧→新）：
- `pages/[category]/[slug].astro` → `pages/jobs/[occupation]/[...country].astro`（分类段废弃，URL 用 `/jobs/`）。
- `pages/industries/index.astro` → `pages/industries/[...country].astro`。
- `pages/industry/[sector].astro` → `pages/industry/[sector]/[...country].astro`。
- 职业详情国家切换：从 `?country=` 服务端读 query → 改读 `Astro.params.country`；国家 tab 链接 `hrefJob(loc, slug, cc)`。

**新增 `src/lib/i18n.ts`**（路由/语言单一来源）：
- `DISPLAY_LOCALES` = 8 种 `en/es/fr/de/pt/ja/zh-Hans/ko`（= `faq_2030.json` 覆盖集），带 `label`（下拉展示名）+ `content`（映射到 data.ts 的 `Locale`：fr/ko→`en`、zh-Hans→`zh-CN`，其余同名）+ `hreflang`。
- `pageLocale(Astro)` / `contentLocale(display)` / `withL(display, path)`（加前缀）/ `stripLocale(pathname)`。
- 链接构造：`hrefJob(d,slug,cc?)`=`/jobs/{slug}[/{cc}]`、`hrefIndustries`、`hrefIndustry`、`hrefRankings`、`hrefBoard`、`hrefCompare`、`hrefMap`、`hrefSearch`、`hrefAbout`、`hrefMethodology`、`hrefHome`——一律语言前缀+国家末级。

**data.ts**：旧 `jobHref(locale,slug,cc?)`（分类前缀）瘦成 `jobHref(slug,cc?)` 返回裸 `/jobs/{slug}[/{cc}]`，仅供 `riskmap-meta` 等内部默认；页面链接全走 `i18n.hrefJob`。`riskmap-meta.ts` 的 `riskMeta(layout, locale?)` 增 locale 参数用 `hrefJob`。`RiskMap.astro` 增 `locale` prop，区域 chip 用 `hrefMap(loc, cc)`。

**各页改造**（`'en'`→`CL=contentLocale(loc)`；链接→`hrefXxx(loc,..)`）：index / rankings/index / rankings/[board] / industries / industry / compare/index(重写) / compare/[pair] / job-risk-map(index+[country]) / search / about / methodology / 404。

---

## 二、req #1 深浅主题切换
- `Base.astro` nav 右侧加 `🌙/☀️` 按钮；`is:inline` 脚本切 `documentElement[data-theme]` + `localStorage.theme`，另有 head 内早执行脚本防闪烁。
- 全局 CSS 加 `:root[data-theme="dark"]{…}` 深色 token（源 `theme.css` 深色值：bg/surface/line/text/brand/risk*，并补 `--risk-*-bg` 深色与深色 `--shadow`）+ `@media(prefers-color-scheme:dark) :root:not([data-theme="light"])` 系统偏好回退。组件别名走 `var()` 自动跟随。
- 页面级硬编码 `#fff`/`#ffffff`/灰阶（`#f0f5fa`/`#e2e8f0`/`#ecf3fa`/`#dce7f5`/`#e2edff`）已在 index/rankings[board]/search 用 perl 扫成 token（背景→`--surface`、边框/轨道→`--line`/`--surface-tint`）；**文字白**（如渐变上的 `color:#fff`）保留。装饰性徽章的固定暖色少量保留（可接受）。

## 三、req #2 nav 语言下拉
- `Base.astro` 加 `.lang-select`（native `<select>`，`onchange` 跳 `this.value`）。选项 = `DISPLAY_LOCALES` 各语言对**当前裸路径**的 URL（`withL(code, bare) + qs`，保留 query）。同时按 8 语言 + `x-default` 输出 `hreflang`。

## 四、req #3 FAQ 只留当前语言
- 职业详情去掉 `.faq-langs`「ALSO ASKED AS」7 语言并列块；首条问句改 `faq2030[loc] || faq2030.en`（`loc` = nav 当前显示语言，faq_2030 键正好含 8 种）。切 `/es/jobs/...` 即显示西语问句。答案(A)仍英文（用户只要求译问句）。

## 五、req #4 compare 重做（`compare.html` 蓝系）
- 重写 `pages/compare/index.astro`：hero + 两张 `.selector-card`，每张一个**可搜索 combobox**（`<input>` 过滤 + 自绘 `.cb-list`，`mousedown` 选中）+ 分类 tag + 预览行（暴露徽章 + 薪资）；中间 VS 交换按钮；CTA「Compare these jobs」实时指向 `/compare/{a}-vs-{b}`；`.metric-tiles` 实时对比（暴露/薪资，诚实只显有数据项）；热门对 grid；FAQ。
- 全量职业 `{s,n,e,p,cur,c}` 由 SSR 以 `<script type="application/json">` 内嵌，client 端搜索（截前 30）。默认预选 `COMPARE_PAIRS[0]`。
- `compare/[pair].astro`（结果页，沿用上会话 bookkeeper-vs-accountant 风格）仅做 locale/链接更新。

## 六、req #5 行业 icon
- `industries.ts` 新增 `CATEGORY_ICON`（11 类职业族 category 显示名 → FA 图标）+ `categoryIcon(name)`（回退 `fa-briefcase`）。加到：首页热门卡 `.job-industry`（替原硬编码 `fa-briefcase`）、`rankings/[board]` 的 `.job-cat`、`search` 的 `.rc-cat`。行业 hub 卡片本就有 `sectorIcon` 大图标，不重复。

## 七、req #6 页脚
- `Base.astro` 本就含 `© 2026 …` 页脚；确认所有页面（含重写的 compare）统一走 Base，均带页脚。页脚链接加 `withL(loc,..)` 前缀。

---

## 八、验证
dev（端口 4331，`aijobrisk-dev`）浏览器 + curl 全验证：
- 路由：`/`、`/es/`、`/es/about`、`/es/rankings`、`/es/jobs/...`、`/zh-Hans/industry/finance/US`、`/fr/compare`、`/ko/rankings`、`/de/industry/health/DE`、industries/industry/rankings/compare/map/search/about/methodology **全 200**；`/nonexistent` 404；**服务端零错误**。
- `/es/jobs/correspondence-clerks`：FAQ 问句西语「¿Sustituirá la IA a … para 2030?」、nav/tab/map 链接带 `/es`、`html lang=es`、canonical 自指。
- compare combobox 搜索「nurse」正常过滤、CTA 实时更新、热门对链接正确。
- 深色：toggle 切 `data-theme=dark` + localStorage，首页/榜单卡片暗色正常。
- 榜单行：`.job-cat` 带 `categoryIcon`、链接 `/jobs/{slug}`。

**未跑** `npm run build`（SSR 构建慢）；验证靠 dev 全路由请求 + 渲染 + 日志零错误。

---

## 九、待办 / 待决
1. **全部未 commit**（连同上游 07-21b 等）。
2. **国家路径化范围**：仅按用户点名做了 jobs/industries/industry；**rankings/compare 的国家维度仍用 `?country=`**（同样带 `/{lang}` 前缀、功能正常）。如需统一改成路径末级可再做。
3. **深色打磨**：token 级已覆盖；页面内少量装饰性固定暖色（徽章等）与文字白未动；如需彻底暗色可再扫。
4. **翻译深度**：仅「可译内容」切换；页面硬编码英文 UI 文案与职业正文仍英文兜底（无 `translations-v2/`）。如要全站 UI 文案随语言变，需把各页硬编码串改走 `strings()`/`ui_i18n`（工作量大且 ui_i18n 未必覆盖新页 key）。
5. `industries.ts` 的 `occupationsInSector`/`sectorExamples` 内部 `occName(..,'en')` 仍英文（行业表职业名不随语言切），低优先。
6. 2030 FAQ 答案仍英文；生产部署（`npm run build` → `node ./dist/server/entry.mjs`）沿用上会话方案。

> 关键文件：`aijobrisk/src/middleware.ts`（新）、`aijobrisk/src/lib/i18n.ts`（新）、`aijobrisk/src/layouts/Base.astro`、`aijobrisk/src/pages/jobs/[occupation]/[...country].astro`、`industries/[...country].astro`、`industry/[sector]/[...country].astro`、`compare/index.astro`（重写）、`aijobrisk/src/lib/industries.ts`（+categoryIcon）、`aijobrisk/astro.config.mjs`（删 i18n）、根 `RULES.md`（+路由规约）。
> 见 memory [[aijobrisk-ssr-site]] [[multi-domain-architecture]] [[design-exploration-decoupled]] [[azure-translator-backend]]。
