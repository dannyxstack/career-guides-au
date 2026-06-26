# 会话交接 · 2026-06-25（UK+DE 全量采集完成、AI Exposure(AIOE)学术指数试点、待全量铺开）

> 接续 `docs/session-handoff-2026-06-23.md`。
> DB = 远程 MySQL `192.168.194.135:13306`，配置读 `.env`（键名 **MYSQL_HOST/PORT/USER/PASSWORD/DATABASE**）；翻译/AI 生成 `$env:LLM_PROVIDER="deepseek"`。长任务命令前加 `PYTHONIOENCODING=utf-8`（GBK 崩进程，见记忆）。
> 站点品牌 **AI Career Graph**。Python：`e:/run/conda_envs/career-video/python.exe`。

---

## ⚠️ 立即可续做（RESUME / 待办，按优先级）

### 1. 【新增 · 重点】全量 AI Exposure 指数（AIOE）计算与铺开
试点已完成（6 个职业：3 US + 3 AU，见下「本会话完成 4」）。**全量铺开的核心工作 = 4 套分类→ISCO→美国 SOC 的批量 crosswalk**：
- 数据源：`AIOE-Data/AIOE`（GitHub）`AIOE_DataAppendix.xlsx` 的 **Appendix A**（774 个美国 SOC，AIOE z-score）。已下载 `.codex_tmp/aioe.xlsx`，解析成 `.codex_tmp/aioe_soc.json`（{SOC: {title, aioe, pct}}，pct=百分位 0-100）。
- **US**：occ_code 即 SOC，直接 join。**坑**：US 用 SOC **2018**，AIOE 用 SOC **2010**，部分码不同（如 Software Developers 15-1252 在 2010 是 15-1132/1133）→ 需 SOC2018↔2010 对照（BLS 有 crosswalk）补未命中。试点中直接命中率：US 792 里约命中大多数（具体数未全量统计）。
- **UK(SOC2020) / DE(KldB) / AU·NZ(ANZSCO) / CA(NOC)**：各国官方都有到 **ISCO-08** 的对照表（ONS/BA/ABS/StatCan），BLS 有 SOC↔ISCO → 链路：本国码→ISCO→US SOC→AIOE。多对多，组内对 AIOE 取平均。试点的 3 个 AU 是**手工**映射（254422→29-1141、331212→47-2031、221111→13-2011），全量需写 crosswalk 管线。
- 落地：写 `scripts/compute_aioe.py`（读各 crosswalk + aioe_soc.json，UPDATE occupation_ai 的 aioe_* 列），再 `export_site_data`。前端展示块已就绪（见下），全量后自动生效。
- 记录 aioe_method='direct'(US) / 'crosswalk'(其余)；展示已标注"经 ISCO 跨分类对应，仅供参考"。

### 2. UK + DE 接入站点（Phase 3 + 4，目前数据在 DB 但前端未配）
- UK 368、DE 642 已全量采集 + ai-block 齐全，但**前端 COUNTRIES 仍是 ['AU','NZ','CA','US']**，未加 UK/DE；且新增中文母本未翻译。
- 需：data.ts COUNTRIES 加 'UK'/'DE' + 国旗 SVG(带 xmlns，禁 emoji)/COUNTRY_NAME/currency(GBP/EUR)；`SOURCES_BODY` 补 UK(ONS/HMRC/UKVI)、DE(BA/destatis/Make it in Germany)；`MIG_TEXT` 补 UK(Skilled Worker/Global Talent/Shortage list)、DE(EU Blue Card/技术移民法/Chancenkarte/Anerkennung)；about 页 SOC 提及 UK、KldB 提及 DE。
- **建议与 AIOE 全量、AU/CA/NZ 补全一起，最后统一做一次 Phase 3 翻译/导出/构建**（翻译最耗时，只翻一次增量）。用户已认可"等数据齐了统一翻一次"。

### 3. AU/CA/NZ 补全广度（已评估，待用户定目标）
AU 是手工 seed 的 257（202 个 seed_*.py），CA/NZ 镜像 AU。要补到 US/DE 广度(~640)：建 ANZSCO-list 驱动的 `gen_au_occupations.py`（克隆 gen_uk/gen_de，取 ABS ANZSCO 清单）→ AU 采集 → 重跑 gen_ca/gen_nz 镜像。目标 B(~640) 新增约 1250；A(全量 ANZSCO 998) 新增约 2200。前端无需 Phase 4（AU/CA/NZ 已配）。

### 4. 大量未提交改动（见下「未提交清单」）

---

## 本会话完成（2026-06-25）

### 1. US/NZ + 全球化 已提交并推送
`ccd8a40b feat(site): add US & NZ occupations and globalize country-specific UI` 已 **push 到 origin/main**。含：US 792/NZ 全量数据、AU 硬编码全面 country-aware（sourcesBody/migration 文案/visaCode/JSON-LD 按国家）、US 国旗/首页卡。线上 occupations.json 仅 AU/CA/NZ/US（**不含 UK/DE**，符合用户"英国先不进站点"）。

### 2. 英国(UK · SOC 2020) 全量采集完成
- 清单：ONS SOC 2020 Volume 1 Excel → 412 unit groups，剔 44 个 n.e.c. → **368**，存 `.codex_tmp/soc_2020.json`。
- `scripts/gen_uk_occupations.py`（克隆美国版 + 英国特化：SOC 码/GBP/Skilled Worker·Global Talent·Health&Care·Scale-up 签证）。**UK 368/368 入库 0 失败**。
- ai-block：`copy_ai_blocks --country UK` 复制 116（母体池 AU+CA+US）+ insights **368/368** + disruptor 364/368。

### 3. 德国(DE · KldB 2010) 全量采集完成
- 清单：BA Systematisches Verzeichnis Excel → 702 个 4 位 Berufsuntergruppen，剔 60 个 "sonstige" → **642**（保留 "ohne Spezialisierung"），存 `.codex_tmp/soc_de.json`。
- `scripts/gen_de_occupations.py`：KldB 码/EUR/occ_code_type='KldB'/EU Blue Card·技术移民法·Chancenkarte·Job Seeker。**关键差异：德文标题→LLM 产出英文名(name_en)**。**DE 642/642 入库 0 失败**，母体匹配率 37%（池 AU+CA+US+UK）。
- ai-block：复制 241 + insights **642/642** + disruptor 639/642。

### 4. AI Exposure(AIOE) 学术指数 — 试点完成
- 选 Felten-Raj-Seamans **AIOE**（10 AI 能力×O*NET 52 能力，按 level×importance 加权），数据 GitHub `AIOE-Data/AIOE`。
- DB：`occupation_ai` 新增 4 列 `aioe_score`(z 分)/`aioe_pct`(百分位 0-100)/`aioe_soc`(映射 SOC)/`aioe_method`(direct/crosswalk)。**原 LLM 列(automation_exposure 等)原样保留**。
- 导出：`scripts/_i18n_fields.py` ai 块加上 aioe_*。
- 前端：`[slug].astro` 结论卡下新增「AI Exposure Index (AIOE)」展示块（百分位大号数字 + 渐变条 + 方法/SOC 来源行），**只 zh/en，其余语言走英文**（locale==='zh-CN' ? 中 : 英）。data.ts Occ.ai 类型加 aioe_*。
- **6 个试点**（已灌库、本地预览验证、未提交）：
  - US direct：Chief Executives 11-1011→**91**、Registered Nurses 29-1141→**57**、Carpenters 47-2031→**9**。
  - AU crosswalk(手工)：Accountant 221111→13-2011→**99**、Reg Nurse 254422→29-1141→**57**、Formwork Carpenter 331212→47-2031→**9**。
  - 重要发现：AIOE 与 LLM 分数显著分歧（木工 LLM 7.5"高"但 AIOE 9"低"；会计/高管 AIOE 99/91 高）——印证学术指数价值。

## 当前规模（DB）
职业：AU **257** + CA **168** + NZ **258** + UK **368** + DE **642** + US **792** = **2485**。
（注：UK/DE 全量但前端未接；US/UK/DE 中文母本未翻译；AIOE 仅 6 个试点。）

## 未提交清单（git status，HEAD=ccd8a40b）
- 改：`scripts/_i18n_fields.py`(aioe 导出)、`site/src/data/occupations.json`(含 UK/DE/aioe，本地导出)、`site/src/lib/data.ts`(Occ.ai aioe 类型)、`site/src/pages/[country]/[locale]/[category]/[slug].astro`(AIOE 展示块 + 之前 migration country-aware)。
- 改名：`scripts/copy_us_ai_blocks.py` → `scripts/copy_ai_blocks.py`（已泛化 `--country`）。
- 新：`scripts/gen_uk_occupations.py`、`scripts/gen_de_occupations.py`、`career-contents/uk/`、`career-contents/de/`。
- **未提交、未推送**。occupations.json 现含 UK/DE（仅本地预览，COUNTRIES 未含故不渲染）；正式提交前需决定是否带 UK/DE 数据。

## 关键运维 / 坑（持续有效）
1. `.env` 键名 MYSQL_*；签证表是 `occupation_visa_pathways`。先 `show columns` 别猜列名。
2. 长 Python 任务命令前加 `PYTHONIOENCODING=utf-8`（GBK 会让含 ö/� 的 print 崩进程，已发生在 disruptors）。后台用 run_in_background。
3. 各 gen 脚本幂等（done.json）；失败分类：`数据不完整`/JSON 格式错=瞬时可重跑；`1406 Data too long`=列长需改。
4. 回退脚本 `gen_ai_disruptors` 默认 `--rest 1800`，**必须显式 `--rest 0`**。insights/disruptors 自动跳过已有的。
5. `copy_ai_blocks --country XX` 读 `.codex_tmp/{xx}_ai_match.json`，幂等。
6. AIOE：US SOC 2018 vs AIOE SOC 2010 有码差；非 US 国家经 ISCO 桥接、多对多取平均。
7. dev server preview MCP 起在 4399。评分 10 分制存储展示÷2；is_migration 0/1/2；国旗内联 SVG 禁 emoji。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-25.md 继续」。
