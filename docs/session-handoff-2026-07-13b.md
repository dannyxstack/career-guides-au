# 会话交接 · 2026-07-13b（英文母本翻转 v2：新管线 + 全量迁移 + 前端硬切 + dist 瘦身）

> 接续 `docs/session-handoff-2026-07-13.md`（英文源已 0 缺口、质检定稿）。
> 本会话把「母本从简体中文翻转为英文」真正落地：建并行 v2 管线、迁移全部数据、前端切到 v2、并把 dist 从 8GB 压到 3.5GB。
> 分支 **`feat/english-master-v2`**，3 个提交**未 push、未合 main**：`a36826d8` / `a3df96b3` / `e2e774c9`。
> DB = 远程 MySQL（`.env` MYSQL_*）。LLM 走 **DeepSeek**（v2 用 `scripts/_deepseek_rest.py` 经 requests 直连，避开未安装的 openai）。

---

## 决策（用户已定）
1. **方案**：新建 v2 并行管线（strangler），旧中文母本管线不动、逐步废弃；旧数据一次性全量迁入。
2. **复用**：沿用 `occupations` 主表 + 跨切面数值卫星表（invitation_scores/occ_search_hits/poll_agg）；文本类各建 `*_v2` 镜像表。
3. **新 TM 主键**：`sha1(英文)+locale`（接受碰撞）。
4. **采集脚本**：即刻改英文优先（`gen_intl_v2.py`，已接瑞士 CH）。
5. **前端硬切**：本会话完成到「读 v2 JSON」；默认无前缀页=英文。
6. **dist 瘦身 task1**：非优先语种走 **noindex 静态桩页**（本站纯静态无 SSR adapter，未上 SSR）。

## 背景排查结论（翻转前）
- 旧管线：所有展示文案=中文母本，运行时 `tr(中文源串)→译文`；英文只是 TM 里的一种译文。两种母本存储：locale 表（occupations_i18n/faqs_i18n）+ `*_zh` 硬列（ratings.label_zh、ai.*_zh、disruptor scope_zh、ai_disruptors.summary_zh）+ 无后缀中文列（education/salaries/quals/visa/suitability）。
- 旧英文覆盖：`translations` en gap=**0**（261,283 条），故迁移=**数据搬运，非重翻**。
- 「英文页夹中文」根因：**不是 TM 不全**（各国 en 覆盖~100%），而是 `growth_areas` 等**按设计不翻译**的字段存了中文，且 `JobDetail.astro:195` 直接渲染 growth_areas（不走 tr）。

## 本会话完成

### 1. v2 schema + 管线（commit a36826d8）
- `scripts/migrate_v2_schema.py`：11 张英文母本文本表（`occupations_text_v2` + education/qualifications/salaries/visa/suitability/ratings/faqs/ai_v2 + ai_disruptors_v2/occupation_ai_disruptor_v2）+ `translation_src_v2`/`translations_v2`。**英文比中文长**→多列用 TEXT/加宽（ai verdict/entry/upgrade、visa desc、suitability item、salary/edu/qual、rating label VARCHAR(120)、faq question(600)、visa_subclass(120)）。
- 脚本：`_seed_helper_v2.py`(seed_occupation_en)、`_i18n_fields_v2.py`(fetch/collect，母本=英文，含 growth)、`collect_strings_v2.py`、`translate_v2.py`(DeepSeek from-English)、`export_site_data_v2.py`、`gen_intl_v2.py`(英文优先采集器→CH)、`_deepseek_rest.py`、`migrate_to_v2.py`。

### 2. 全量迁移（commit a36826d8）
- `migrate_to_v2.py --country XX`：逐职业读旧 bundle，文本用旧 TM 英文替换写 v2；**单职业独立事务 try/except**（否则一条列溢出拖垮整国——首轮踩过只迁 485）。
- 结果：**11 国 5813 职业全迁，0 失败**，英文缺失仅 3（旧 TM 自身空洞，已补）。
- `--port-tm`：把旧 translations 非英文译文按 sha1(英文)**复用 1,256,306 行**（免重翻）；另回填 **zh-CN 25.1 万**（旧 TM 中文只当源，用英文串反查原中文写入）。
- 残留中文清零：`fix_growth_en.py`（133 条中文 growth_areas 就地翻英，改共享 occupations 列→旧站+v2 同修，备份 `.codex_tmp/growth_zh_backup.json`）；另清 visa_subclass(588)、disruptor name/vendor(~90)、faq_type 等「按设计不翻译却夹中文」字段。**v2 DB + 导出 JSON 中文残留 0**。

### 3. 前端硬切（commit a3df96b3）
- `data.ts`：改读 `occupations_v2.json`/`categories_v2.json`/`translations-v2`/`occ-detail-v2`；`tr()`/`hasTr` 母本 zh-CN→**en**（源即英文，含 zh-CN 的目标语走 v2 TM，缺译回退英文）。
- **零改组件技巧**：`export_site_data_v2` 输出**沿用旧键名**（英文装进 `i18n['zh-CN']`/`training_zh`/`ai.*_zh`）。
- heap：v2 TM 更满 eager-glob 撑爆 8GB → `site/package.json` dev/build 调 **16384**（机器 63GB）。更优解=按 locale 懒加载 TM（未做）。
- dev 实测：默认无前缀页=英文、`/zh-CN/`=中文、`/de/`=德文。

### 4. dist 瘦身 8GB→3.5GB（-56%）（commit e2e774c9）
- **task1** 职业详情页仅 6 优先语种（`en/zh-CN/zh-Hant/ja/es/pt`，`data.ts` 的 `FULL_JOB_LOCALES`）出完整页；其余 7 语种出 `layouts/Stub.astro` 极简 noindex 桩页（canonical→英文，~977B）。
- **task2** `JobDetail` 只渲染 active 国面板（原所有国 SSR 后 hidden），tab 变纯链接、删客户端切换脚本；聚合页=tabs+默认国单面板。
- **task3** 风险地图 meta 外置 `src/pages/risk-map/[scope].json.ts`→`/risk-map/{WORLD,cc}.json`，`RiskMap.astro` 客户端 fetch（删内联 `window.__RM`），meta 仍作 prop 供 SSR 上色/合计。
- **关键杠杆**：`astro.config` 加 `build.inlineStylesheets:'never'`——页面 import JobDetail 会把其作用域 CSS 内联进桩页（即使不渲染），外置共享后桩页 7KB→977B、全站每页省~4KB。
- build **129,949 页 / 327s / exit0**；验证：全页 3 外链 CSS/0 内联/1 面板，桩页 noindex 无 hreflang，world 图无 __RM 引用 WORLD.json。

## 待办 / 下一步
1. **合并+push**：分支 `feat/english-master-v2` 3 提交未 push（main 直推历史上被拦）。
2. **en→X 补齐**：`translation_src_v2` 270,643 源串中约 7.5 万缺部分语言译文（port-tm 已复用 125.6 万；缺的是旧 TM 本就没翻的部分）。引擎待定（DeepSeek 小钱快 / 本地 gemma 慢）。
3. **删旧件**（达标 M1 全量迁移✅ + M2 前端切✅ 后可动）：旧 `translations/`、`occ-detail/`、`occupations.json`、`gen_*`/旧 `collect_strings`/`translate_strings`/`export_site_data`/`_i18n_fields`/`_seed_helper`；上会话英文质检脚本（audit_en_quality 等）；3 张空死表 `occupation_{education,salaries,suitability}_i18n`。见弃用分组 0/A/B/C/D（前次会话）。
4. `inlineStylesheets:'never'` 是**站点级**改动（CSS 外链，多一个可缓存请求）；若更看重首屏内联可单独回退。
5. **可选**：把 `rankings`/`compare`/国家页也纳入优先语种策略可再省（超「职业详情页」范围，需用户确认）。
6. `/jobs/{slug}` 全局路由本会话未动，探测时 404，建议合并前抽验。

## 关键坑（本会话）
1. `openai` 未装在 `E:\run\Python3.13`（现有 gen_*/llm.py 依赖）→ v2 改 requests 直连 DeepSeek（`_deepseek_rest.py`）。
2. DeepSeek `json_object` 模式 prompt **必须含字面 "json"** 否则 400。
3. `video_pipeline/azure_translate.py` 源固定 `zh-Hans`、目标映射缺 fr/it/nl/zh-CN → 不适配英文母本，v2 弃用之走 DeepSeek。
4. 迁移：英文更长导致列溢出；`migrate_country` 必须单职业独立事务，否则整国被一条拖垮。
5. dist：页面 import 组件即内联其作用域 CSS 到产物（即使不渲染），靠 `inlineStylesheets:'never'` 根治。
6. dev/build 需 **16GB heap**（v2 TM eager-glob）。长任务用 PowerShell 独立进程或后台 Bash（见 [[i18n-translation-pipeline]]）。

## 本会话新增/改动文件
- 新脚本：`scripts/{migrate_v2_schema,_seed_helper_v2,_i18n_fields_v2,collect_strings_v2,translate_v2,export_site_data_v2,gen_intl_v2,_deepseek_rest,migrate_to_v2,fix_growth_en}.py`
- 新前端：`site/src/layouts/Stub.astro`、`site/src/pages/risk-map/[scope].json.ts`
- 改前端：`site/src/lib/data.ts`、`layouts/Base.astro`、`components/{JobDetail,RiskMap}.astro`、`site/astro.config.mjs`、`site/package.json`、`site/src/pages/[locale]/[category]/[slug].astro` + `.../[country].astro`、`job-risk-map` 两页

> 恢复：读本文件 + memory [[english-master-v2-pipeline]] [[i18n-translation-pipeline]]。英文母本 v2 已全量上线到「数据+前端」两层，下一步多为收尾（合并/en→X 补齐/删旧件）。
