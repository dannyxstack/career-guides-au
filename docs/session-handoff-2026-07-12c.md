# 会话交接 · 2026-07-12（c）（IT/NL/IE 采集收尾上线 + occupations.json 方案B瘦身）

> 接续 `docs/session-handoff-2026-07-12b.md`（同日）。任务：完成 IT/NL/IE 职业采集收尾并上线。
> DB = 远程 MySQL（`.env`：MYSQL_*；表 `occupations`，国家列 `country_code`）。
> Python：`e:/run/conda_envs/career-video/python.exe`；长任务前 `PYTHONIOENCODING=utf-8`；LLM 用 `LLM_PROVIDER=deepseek`（百度/Anthropic 欠费）。
> 生产：每 5 分钟 `git pull`(main) + `npm run build`（8GB 堆）；导出前须停 astro dev（Errno22，本会话遇到 pid 需 taskkill）。
> **本会话有一次 commit `8ad11f17`（已 push? 否，仅本地）；其后又有一批改动未 commit（见末尾）。**

---

## 一、AI 块补齐（阶段2）✅
- **copy_ai_blocks**：复用 346 条母体 AI 块（IT 118/NL 103/IE 125）。`copy_ai_blocks.py` 加回退识别 `isco_{CC}_ai_match.json` 命名。
- **gen_ai_insights + gen_ai_disruptors**（deepseek，后台）：补齐剩余 ~961 条 + redo 扫残缺。最终 occupation_ai：IT 436/NL 436/IE 435 全齐；disruptor 少量职业无适用工具（正常）。

## 二、locale it/nl（阶段6，UI 层）✅
- data.ts：Locale 类型 + LOCALES + JOBS_LOCALES 加 `it`/`nl`。
- Base.astro / Home.astro：LANG_ATTR/LABEL/NAME 加 it/nl 原生名（Italiano/Nederlands）。
- `translate_ui.py` 加 it/nl → 各 221 键 UI 文案入 `ui_i18n.json`。
- **正文 it/nl 翻译（阶段3）用户决定暂缓**（见四）。

## 三、国家接线 + 风险地图（阶段7）✅
- data.ts：COUNTRIES 加 IT/NL/IE，配齐 CURRENCY/COUNTRY_NAME/COUNTRY_FLAG(SVG)/CURRENCY_SYMBOL/COUNTRY_TITLE_ZH/MIG_TEXT/SOURCES_BODY。
- outline：`gen_country_outline.py` 的 A3 加 ITA/NLD/IRL；下载 NE 50m/110m，用增量 runner 只给 IT/NL/IE 追加 `country-outline.json`+`outline-paths.json`（**保留原 8 国+WORLD 不动**），坐标校验在框内。
- 风险地图 getStaticPaths 走 COUNTRIES+locale=en → **三国图 build 后自动生成，已浏览器验证**（IT 527 方块 + 靴形轮廓 + 436职业/2847万从业者 + Avg salary 弹层）。

## 四、翻译（阶段3）⏸️ 用户决定暂缓
- 实测待翻译共 **145.8 万** (src,locale) 对：it/nl 各 26.1 万（全站新增）+ 其余 10 语言历史积压 5.8–10.4 万各。DeepSeek 全量约 13h+ 付费。
- 缺译文时页面**回退 en 不阻塞上线** → 用户选「暂不翻译，先 export/build 上线」。
- 启动方式（后续）：`collect_strings`（已跑，261k 源串）→ `translate_parallel --workers N`（`translate_strings.LOCALES` 已含 it/nl）。

## 五、官方薪资层（阶段4）🔶 NL 完成，IT/IE 数据源不可达
用户选「全量三国4位都做」。实测：
- **Eurostat**（lfsa_egais 就业 / earn_ses_monthly 薪资）**仅 ISCO 1 位**（OC1-9），太粗，不该 override 逐职业 LLM。
- **NL=CBS 表 `85517NED`**（时薪 P25/P50/P75 + 员工数×1000，BRC2014 约 114 组，OData 干净）✅ →
  `scripts/fetch_official_nl.py`：DeepSeek 建 BRC→ISCO crosswalk（386/436 映射，`.codex_tmp/official_NL_xwalk.json` 缓存）→ 时薪×1976(38h×52)折年薪 → 覆盖 **252 个职业**的 median 档（`official_NL.json`）。抽查语义准（软件开发→软件开发组€68.8k、医生→Artsen€79.2k）。
- **IT=ISTAT SDMX 500 / IE=CSO 无4位职业薪资**（CSO 职业薪资仅 SOC 大类≈1位，ISTAT SDMX 服务端错误）→ **IT/IE 保留逐职业 LLM 估算基线**（见六），页面 SOURCES_BODY 已注明估算。

## 六、🐛 两个数据 bug（本会话发现并修复）
1. **薪资货币错存 AUD**：三国 `occupation_salaries` 全部 AUD（应 EUR）。根因 `_seed_helper.py` 两处 INSERT **没写 currency 列**用了默认 AUD。已 UPDATE 三国 3916 行→EUR，并修 helper 两处 INSERT 加 `currency=OCC.get("currency","AUD")`（向后兼容 AU）。
2. **IT/NL/IE 缺 median/mean 汇总薪资档**（salary_band 全 NULL 只有经验档），而风险地图 avg_salary 用 mean 档 → 三国弹层薪资会空。新脚本 `fill_isco_salary_bands.py` 用各职业经验档区间中值填 median+mean 估算档（三国 436/436/435 全覆盖，currency=EUR）。作为**基线桩**，NL 官方层再 override median。

## 七、export + build（阶段5）✅ 已上线
- `export_site_data`：5810 职业（IT/NL/IE 各 436/436/435 纳入）。build exit 0，三国职业页 + 风险地图页全生成，浏览器验证通过。

## 八、occupations.json 方案B 瘦身 ✅（用户从 A/B/C/D 选 B）
文件曾达 68MB（`ai` 字段占 60%）。见 memory [[occupations-json-lean-detail]]。
- **LEAN**（occupations.json，**17.3MB**，↓75%）：身份 + i18n + salaries + education + ratings(**瘦身:只留{dimension,stars}**,删无人读的label_zh/name_zh) + overall_score/avg_salary/training_zh + aiMeta(verdict+cluster+4分数+aioe)。
- **DETAIL**（`occ-detail/{cc}.json` × 11,各2.8-6.9MB,懒加载）：visa/qualifications/suitability/faqs/growth_areas + ai重文案(entry_narrowing/replaced/augmented/moat/skills/upgrade_path/adjacent/disruptors)。
- **合并**：data.ts 加 `import.meta.glob` 惰性加载 + `loadDetail(cc)` + `occFull(o)`。**仅 JobDetail.astro 调 occFull**（富化 rep+各国 countries）；compare 只用 is_migration、旧详情页渲染 `<JobDetail>` 自富化 → 无需改。
- **关键约束**：salaries/education 必须留 lean（OccCard 全局列表+rankings hub 经 seniorSalary/trainingMonths 读它们）。
- 验证：build exit 0；NL 软件开发详情页 occFull 合并全生效（AI文案/disruptors/FAQ/NL专属签证/13国Tab，无控制台报错）；列表卡片薪资/培训派生正常；风险地图 527 方块无回归。

## 待办 / 卡点
1. **未 commit 改动**（`8ad11f17` 之后）：`scripts/{export_site_data,translate_strings,fetch_official_nl}.py`、`site/src/components/JobDetail.astro`、`site/src/lib/data.ts`、`site/src/data/{occupations.json(17.3MB),occ-detail/*.json}`。DB 侧改动（NL官方/median-mean档/货币）在远程库。
2. **阶段3 翻译**（暂缓）：145.8万条，上线后独立跑。
3. **IT/IE 官方薪资**：无4位可达源，如需可退而用 Eurostat 1位做「大组参考」或找二手源（本会话判定不值当，保留 LLM 估算）。
4. 上上会话遗留：nginx 301 部署、百度充值（可改 DeepSeek）。

## 关键坑（本会话新增）
1. `_seed_helper.py` INSERT 漏 currency 列 → 非 AU 国家薪资默认 AUD（FR/DE/ES 可能同病，未查）。
2. 风险地图 avg_salary 严格取 band='mean' 行（experience='平均薪资'），无则弹层空。
3. Eurostat 职业维度全线只到 ISCO 1 位；各国 4 位职业薪资多为本国分类需 crosswalk，且 IT/IE 无干净 API 源。
4. occupations.json 拆 lean/detail 时 **salaries/education 不能移走**（全局卡片依赖派生值），移走需移植中文时长正则（风险大）。
5. astro dev 占用文件致导出 Errno22：`wmic process where "name='node.exe'" get ProcessId,CommandLine` 找 `astro.js dev` 的 pid → taskkill。

> 恢复：读本文件 + memory [[it-nl-ie-collection]] [[occupations-json-lean-detail]]。下一步多为 commit + （按需）翻译/官方层。
