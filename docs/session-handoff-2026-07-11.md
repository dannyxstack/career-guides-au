# 会话交接 · 2026-07-11（risk-map hero/tooltip 修复、投票+适合/前景/FAQ 迁到职业页、【进行中】职业页 URL 全量迁移 /jobs→/{cat}/{slug} + 11 语言）

> 接续 `docs/session-handoff-2026-07-10.md`。
> DB = 远程 MySQL（`.env`：MYSQL_*；表 `occupations`，国家列 `country_code`）。
> Python：`e:/run/conda_envs/career-video/python.exe`；长任务前 `PYTHONIOENCODING=utf-8`。
> 生产：每 5 分钟 `git pull`(main) + `npm run build`（8GB 堆）；导出前须停 astro dev 预览（Errno22）。
> **前半已 push main（`dbdf5cf1..def99aa7`）；后半「职业页 URL 全量迁移 #5」全部未提交（见 §待办）。**

---

## 一、本会话已完成并已 push（`59b8a309` + `def99aa7`，接在 dbdf5cf1 后）

### 1. risk-map hero 不再限宽断行（commit `59b8a309`）
- 去掉两个 risk-map 页 `.rm-hero p` 的 `max-width`，宽屏一行不断行（窄屏仍自然换行）。

### 2. risk-map tooltip 修复（`59b8a309`，根因很关键）
- 病因：tooltip 内容由 JS `innerHTML` 注入，**不带 Astro scoped 属性** → `.rt-name`(加粗)/`.rt-row`(flex 分列) 的 scoped CSS 全部不生效 → 标题没加粗、`Category`/`Workforce` label 与值粘连。
- 修法（`RiskMap.astro`）：内部选择器改 `:global()`（父 `.rm-tip` 在模板中有 scope，后代全局匹配注入内容）；另加 `.rt-row span{margin-right:12px}` 明确间距。computed 验证 fontWeight=700 / display=flex。

### 3. 投票 + 适合不适合 + 职业前景 + FAQ 迁到新职业页（`def99aa7`，`JobDetail.astro`）
- **评估国家绑定性**：适合/不适合、职业前景(trend_summary/forecast_note/growth_areas)、FAQ **都因国而异**（各国执照/英语/需求/移民问题不同）→ **放国家 panel 内**（用 `o.`，逐国渲染，随 Tab 切换）。
- **投票**：`occ_key=slug` 跨国共享（全球一份）→ 放**国家区之后**（`<PollBlock slug baked={rep.polls}>`，单实例；若放 panel 内会有 3 实例、client 只绑第一个）。

## 二、【进行中·未提交】待办 #5：删旧职业页、全量切到新职业页（用户已定方案）

### 用户拍板的方案（AskUserQuestion 自定义答复）
1. 新页补 **adjacent 相邻职业**（从旧页复制）。
2. 新页 URL 从 `/jobs/{slug}[/{cc}]` **改成 `/{cat}/{slug}[/{cc}]`**（去掉 /jobs 前缀，用分类段）。
3. 旧页所有引用链接（OccCard/Home/rankings/ai-graph/JobDetail 经典页入口/abroad）**全部指向新页**。
4. 语言：**扩到 11 语言全覆盖**（JOBS_LOCALES 6→11）。

### 已改动的文件（全部未提交，git status 见文末）
- **`data.ts`**：`JOBS_LOCALES` 扩到全 11 语言；`jobHref(locale,slug,country?)` 改为 `/{cat}/{slug}[/{cc}]`（分类段取 `catSlug(_jobGroups.get(slug)[0].category)`=rep 分类，en 裸/其余 `/{locale}` 前缀）。
- **新增 4 个路由文件**（克隆自旧 jobs 路由 + 加 `category` 段 + import catSlug）：
  - `pages/[category]/[slug].astro`（en 全局）、`pages/[category]/[slug]/[country].astro`（en 国家）
  - `pages/[locale]/[category]/[slug].astro`（语言全局）、`pages/[locale]/[category]/[slug]/[country].astro`（语言国家）
  - getStaticPaths 里 `category: catSlug(jobBySlug(slug)!.rep.category)`。
- **删除 4 个旧 jobs 路由**：`pages/jobs/[slug].astro`、`pages/jobs/[slug]/[country].astro`、`pages/[locale]/jobs/[slug].astro`、`pages/[locale]/jobs/[slug]/[country].astro`（git 记为 D）。
- **`JobDetail.astro`**：全球 AI 区末尾补 **adjacent**（`(ai as any).adjacent`，链 `jobHref(locale,j.slug)`，名 `name(jobBySlug(j.slug)?.rep,...)`）；**删除底部「经典页」入口**块 + 其 CSS；移除已不用的 `catSlug` import。
- **内链重指新页**：
  - `OccCard.astro`：`href={jobHref(locale,o.slug,country)}`（import catSlug→jobHref）。
  - `Home.astro`：搜索 SEARCH 的 `cs` 改成 rep 分类 slug（`catSlug(jobBySlug(o.slug)!.rep.category)`，原 cs 是死字段）；client 结果链接 `'/jobs/'+o.s` → `'/'+o.cs+'/'+o.s`；热门职业 `url` → `jobHref`；import 加 jobBySlug/jobHref。
  - `rankings/[rank]/index.astro`、`ai-graph/index.astro`：old 详情链接 → `jobHref(locale,o.slug,o.country)`（import catSlug→jobHref）。

### 已验证（dev + build 期）
- **路由歧义实测通过**：`/{cat}/{slug}/{cc}`(3段全动态) 与 `/{locale}/{cat}/{slug}`(3段全动态) 同构，但各 getStaticPaths 生成的具体路径集**互不相交**（分类/语言/国家值域不重叠），dev 下 `/AU/en/`(国家首页)、`/zh-CN/healthcare-care/registered-nurse`(语言全局页)、`/healthcare-care/registered-nurse/NZ`(en 国家页) 全部正确解析；**build 清单阶段无冲突报错**，正常生成 11 语言 `/{loc}/{cat}/{slug}` 页。
- dev：新 URL(含 /th/ /pt/.../CA) 全 200；OccCard 链 `/healthcare-care/aged-care-worker/AU`；adjacent 链 `/healthcare-care/enrolled-nurse` 等。

### ⚠ 未决策 / 卡点（RESUME 从这里继续）
1. **旧页处置 + build 规模**：现状=旧页(约 4.9 万) + 新页 11 语言(约 8.9 万) ≈ **14 万页**。
   - 已实测：最重配置 build **139,524 页 / 427.74s(~7分8秒) / exit 0 / 无 OOM**（8GB 堆扛得住）。但 **427s 超生产 5 分钟窗口**。
   - **意图终态 = 删旧页**（新 11 语言已全覆盖）→ 约 9 万页、build 回落到窗口内。删旧页(`pages/[country]/[locale]/[category]/[slug].astro`)为必需。
   - **但删旧页的 SEO**：旧 URL `/{cc}/{locale}/{cat}/{slug}` 已被收录，直接删=大面积 404。需 301 重定向到新 `jobHref`。Astro 静态重定向对「en 裸 vs 语言前缀」条件 + 参数重排不好表达；**host 级(nginx)重定向零 build 成本**但需用户那边配置。**这一步(删旧页 + 重定向策略)需用户最终确认后再执行**（涉及 SEO、难回滚）。
2. jClassic UI 键已成死键（ui_i18n.json/data.ts 里仍在，无害，未清理）。
3. abroad 交叉链只存在于旧页；旧页删除后自然消失，新页用国家 Tab 替代，无需单独重指。
4. 提交计划：#5 建议拆 2 commit（①URL 迁移+路由+11语言+jobHref ②内链重指+adjacent），或按用户偏好按文件边界拆。

## 当前规模 / 状态
- 8 国 4503 职业 / 3650 唯一 slug 不变。`origin/main` = `def99aa7`（#1-4 已同步；#5 未提交）。

## 关键坑（本会话新增）
1. **Astro scoped 样式不作用于 `innerHTML` 注入的内容**（无 data-astro-cid）→ 动态注入的 DOM 用 `:global()` 或内联 style。
2. **同构动态路由在 SSG 可共存**：只要各 getStaticPaths 生成的具体路径互不相交（此处分类 slug 恒非 locale/国家码），Astro build 不报冲突、dev 也正确消歧。是 `/jobs` 前缀改 `/{cat}` 可行的关键。
3. **11 语言职业页 build 约 14 万页（含旧页），超 5 分钟窗口**；删旧页降到约 9 万页是回到窗口内的前提。
4. 前台 `sleep` 被 harness 拦截；等后台任务用完成通知，别 sleep 轮询。

> 恢复任务：读取本文件继续。**首要动作**：确认上一次 build（task `bhzqewlem`/`build4.log`）结果；然后就「删旧页 + 301 重定向策略」与用户确认后执行，再提交 push。
