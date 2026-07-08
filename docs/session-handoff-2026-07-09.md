# 会话交接 · 2026-07-09（FR 百度翻译跑到额度用尽、ticker 高度修复、job-risk-map 静态轮廓图、/jobs 1+N 职业体系 + 多语言矩阵 + hreflang + sitemap + 旧页入口）

> 接续 `docs/session-handoff-2026-07-08.md`。
> DB = 远程 MySQL（`.env`：MYSQL_*；表 `occupations`，国家列 `country_code`）。
> Python：`e:/run/conda_envs/career-video/python.exe`；长任务前 `PYTHONIOENCODING=utf-8`。
> 生产：每 5 分钟 `git pull`(main) + `npm run build`（8GB 堆）；导出前须停 astro dev 预览（否则 Errno22）。
> **本会话所有改动已 commit 且已 push main**（`6ed7cfd7..d40bf319`）。

---

## 本会话完成

### 1. FR 法国职业·百度翻译跑到额度用尽（纯百度、耗尽即停）
- 需求：只用百度翻 FR，跑到额度用尽为止。现成 `translate_scope.py` 走 `translate_batch`（百度→Azure→DeepSeek 回退），**不符合「只用百度」**——故新写 **`scripts/translate_fr_baidu.py`**：直接调 `baidu_translate.translate`，遇 `BaiduAuthError`（额度用尽 54004）**立即停全部、不回退**；单条内容错误（敏感词 20003 等）跳过；每 50 条增量写库（幂等）；按 locale 分组顺序（es→…→de）。
- 结果：**es 翻了 22,378 条后百度返回 `54004 用户余额不足`**（额度/余额耗尽）自动停。跳过 0。FR 各语言剩余：**es 2,309**、pt/vi/th/ms/id/zh-Hant/ja/de **各 24,692**（合计约 199,845，需百度充值后重跑续翻，幂等）。
- 已跑 `export_site_data.py` 把 es 译文烘焙进 `translations.es.json`（提交在 `006e8adc`）。
- 会话开头顺带补齐上批 6 国残留 7 条（1 th + 6 ja）：其中 **6 条 ja 被百度误判敏感词(20003)**（"故障/死锁/替代" 等正常技术词），改手动 `baidu_translate.disable()` 走 Azure/DeepSeek 回退补齐。

### 2. 首页 hero ticker 高度跳动修复
- 病因：`.ticker` 只有 `min-height:22px`（单行），长播报句换行成 2 行 → 容器高度 22→~42px → hero 整体跳。
- 修法（`Home.astro`）：`.ticker` 固定 `height:44px` + flex 垂直居中 + `.ticker-line` `-webkit-line-clamp:2` 截断。实测塞 296 字符仍恒 44px。

### 3. job-risk-map 背景改为静态 SVG 轮廓图（不再运行期算 geo）
- 新 **`scripts/gen_outline_svg.py`**：从 `country-outline.json` 按**与 riskmap.ts 完全相同的投影**（1600×720, margin=30）预生成每国轮廓到 **`site/public/outlines/{cc}.svg`**（深填充 #000/.38 + 白描边 /.2 两条 path）。
- `riskmap.ts`：删除 `country-outline.json` import、`outlineToPath` 函数、`outlinePath` 字段——运行期不再算轮廓。
- `job-risk-map/index.astro`：两条内联 `<path>` 换成单个 `<image href="/outlines/{country}.svg">` 背景层（`pointer-events:none` 不挡 tile）。`country-outline.json` 现只作构建期源数据（gen_country_outline.py 产 → gen_outline_svg.py 消费）。

### 4. /jobs 1+N 职业 URL 体系（核心大功能，纯新增、不动旧页）
- **URL 矩阵**：一级 `/jobs/{slug}`（全球通用 AI 区）+ 二级 `/jobs/{slug}/{country}`（继承 AI + 注入该国硬核数据：薪资/教育/资质/移民/从业人口/评分）。
- **主键**：按 **slug 跨国聚合**（已验证 slug 是安全全球主键——3650 唯一 slug，仅 3 个因标点差异对应 2 个 name_en，都是同一职业）。`data.ts` 新增 `JOB_SLUGS`(3650)/`jobBySlug()`。
- **共用组件 `components/JobDetail.astro`**：上半层全球 AI 区（结论/AIOE/disruptors/替代·增强/护城河·技能/入门变窄/升级路线，取任一国副本，AI 跨国一致）+ 国家 Tab 栏（真实 `<a>`）+ 逐国服务端渲染的数据面板（仅激活国可见）。**客户端 Tab 切换 + `history.pushState` 改地址栏 + `popstate` 同步 + `<title>` 更新**；无 JS 时静态页仍完整（SEO）。**每个国家面板底部有小入口指向旧详情页** `/{cc}/{locale}/{catSlug}/{slug}/`（键 `jClassic`）。
- **路由**：`pages/jobs/[slug].astro`、`pages/jobs/[slug]/[country].astro`（en 裸）；`pages/[locale]/jobs/[slug].astro`、`pages/[locale]/jobs/[slug]/[country].astro`（非英文核心语言）。
- **首页搜索去重**（`Home.astro`）：按 slug 归一「一职一条」，链向 `/jobs/{slug}`，带 Available Countries **SVG 国旗**（注入 `COUNTRY_FLAG` 到客户端，遵守禁 emoji 国旗规则）。localized 首页链 `/{locale}/jobs/`，非核心语言回退英文裸。

### 5. /jobs 多语言矩阵 + hreflang（SEO 防惩罚）
- 决策（用户定）：**沿用全站 locale 完整码**（`/jobs/`=en 裸、`/zh-CN/jobs/`、`/zh-Hant/`、`/es/`、`/ja/`、`/de/`），**不用 /zh/ 短码**；**先做核心 6 语言** `JOBS_LOCALES=['en','zh-CN','zh-Hant','es','ja','de']`（一行可扩）；`/jobs` **self-canonical**、旧页不动。
- `data.ts`：`JOBS_LOCALES`/`jobHref(locale,slug,country?)`/`jobAlternates()`。
- `Base.astro`：新增 `xDefault` prop（向后兼容），渲染 `<link rel="alternate" hreflang="x-default">`；既有 alternates 映射 zh-CN→zh-Hans。
- `JobDetail.astro` 改 locale 感知（`name(o,locale)`/`tr()`/`strings(locale)`）。新增 UI 键 `jLead/jByCountry/jWork/jAvail/jAioeT/jAioeD/jTitleG/jTitleC/jClassic`（en/zh-CN 母本在 data.ts，zh-Hant/es/ja/de 写入 ui_i18n.json）。
- hreflang 实测：en/zh-Hans/zh-Hant/es/ja/de + x-default→英文裸，canonical 自指，内容按语言本地化（zh-CN 页全中文、es 页西语 UI）。

### 6. sitemap 收录 /jobs + 旧页入口
- `astro.config.mjs` 已用 `@astrojs/sitemap()`，**默认自动收录全部构建页**，无需改配置。实测 build 后 `dist/` 生成 `sitemap-index.xml` + `sitemap-0/1/2.xml`；**/jobs URL 共 48,348 条全部进 sitemap**（每语言 8,058：en 裸/zh-CN/es/ja/de/zh-Hant 各 8,058）。
- 旧页入口见 §4。

### 7. RULES.md 新增「多语言 URL 与 hreflang 规则（SEO 防惩罚）」
- 三点：干净前缀模式（语言最前置、沿用完整 locale 码）、head 埋 hreflang + x-default、canonical 自指。位于「站点前端规则(site/ Astro)」小节内。

### 8. 全量 build 验证 + commit + push
- **实测生产 build：98,758 页 / 264s（~4.4 分钟），exit 0，无 OOM**——6 核心语言翻倍规模 8GB 堆扛得住，**不需收窄 JOBS_LOCALES**。生产 5 分钟窗口仍够（略紧）。
- 本会话 9 个 commit 已 push main：`9cb7f1b3`(百度后端)`c0a84f8e`(首页热门/播报)`2dc34ccf`(risk-map 宽屏)`11e27879`(6国重导出)`63f85b41`(交接doc) + `08e702f3`(risk-map 静态轮廓)`006e8adc`(FR 翻译脚本+es)`18b52b45`(/jobs 全体系+多语言+搜索去重+ticker修复+旧页入口)`d40bf319`(RULES.md)。

## 当前规模 / 状态
- 8 国 4503 职业 / 3650 唯一 slug 不变。`origin/main` = `d40bf319`（已同步）。
- 站点页数 build 后约 **98,758**（原 ~48,864 + /jobs 6 语言 ~48,348 + 少量）。

## 待办 / RESUME
1. **FR 翻译续跑**：百度充值后重跑 `python -m scripts.translate_fr_baidu`（幂等续翻剩余 ~199,845），完再 `export_site_data.py`（停预览）。es 只剩 2,309；pt/vi/th/ms/id/zh-Hant/ja/de 各 24,692 未动。
2. **ES 全量翻译**（未开始，缺口大头）。
3. 可选：扩 `JOBS_LOCALES` 至更多语言（build 扛得住；每加 1 语言 ≈ +16k 页）。
4. **`translations.th.json` 已 50.49MB**，逼近 GitHub 100MB 硬限（本次 push 仅软警告未拒）。FR/ES 继续增长前，考虑超大语言文件再拆分或迁 Git LFS。
5. 投票功能上线（`docs/polls-deploy.md`，agent 无法代执行）。
6. 可选：导航/首页加显式 /jobs 入口（现仅搜索导流）；sitemap i18n hreflang（因旧 URL 结构复杂 /[country]/[locale]/ 未启用，避免误分组）。

## 关键坑（本会话新增）
1. **百度大模型 20003 敏感词误判**：正常技术词（故障/死锁/替代）被拦；`translate_fr_baidu` 的 quota-stop 只认 `BaiduAuthError`，单条内容错误仅跳过不回退（设计如此，跑完少量残留可换后端手补）。
2. **百度额度已尽（54004 用户余额不足）**：充值前无法再用百度翻译。
3. **translate_batch 对 zh-Hant 后端偶发返回英文源串**：本会话译 /jobs UI 新键时 zh-Hant 整批未翻→手工繁体补；机器翻译丢 `{pct}`/`{c}` 占位符→手工补 + 校验。
4. **slug 是安全全球主键**（3650 唯一，3 处标点差异同职业）——/jobs 按 slug 聚合。
5. **多语言 /jobs 用完整 locale 码**（/zh-CN/ 非 /zh/），与全站 /[locale]/ 一致；hreflang 值用规范 zh-Hans/zh-Hant。
6. **Home.astro/data.ts 单文件跨多功能**（ticker/搜索、数据层/UI键），Bash 不支持 `git add -p`，故按文件边界拆 4 commit（非按功能 7 个）。
7. preview_screenshot 本会话仍偶发卡死/超时；改用 curl + preview_eval 验证。导出前停预览（Errno22）。
8. build 已达 **98,758 页/264s**，仍在 5 分钟窗口内但更紧。

> 恢复任务直接说「读取 docs/session-handoff-2026-07-09.md 继续」。
