# 会话交接 · 2026-06-26（全量 AIOE 铺开完成、UK/DE 接入站点、AU/CA/NZ 补全广度、翻译待跑）

> 接续 `docs/session-handoff-2026-06-25.md`。
> DB = 远程 MySQL `192.168.194.135:13306`，配置读 `.env`（键名 **MYSQL_HOST/PORT/USER/PASSWORD/DATABASE**；表名是 `occupations` 非 `occupation`，国家列是 `country_code`）。
> **AI 生成（insights/disruptors/翻译）必须 `LLM_PROVIDER=deepseek`**——默认 claude 会因 Anthropic 余额不足全失败（本会话踩过）。gen_au/nz/ca 核心数据直连 DEEPSEEK_API_KEY 不受影响。
> 长 Python 任务前加 `PYTHONIOENCODING=utf-8`。站点品牌 **AI Career Graph**。Python：`e:/run/conda_envs/career-video/python.exe`。

---

## ⚠️ 立即可续做（RESUME / 待办）

### 1.【唯一大待办】统一 9 语言翻译（~110 万对，付费数十小时）
- collect 后 `translation_src` 145,124 源串；未翻译 (src_hash×locale) 对 **≈1,105,719**（9 语言，含全部 3103 职业）。
- 跑：`$env:LLM_PROVIDER="deepseek"; python -m scripts.translate_strings`（默认 batch 50 → ~2.2 万次调用）。幂等，只翻缺失对。
- 完成后 `python scripts/export_site_data.py` + `npm --prefix site run build`。
- 可先翻 en/zh-Hant/ja（~36 万对）让三大核心语言齐全，其余 6 语言后补。
- **用户已明确：先导出构建上线（已完成），翻译以后再统一跑。**

### 2. 大量未提交改动（见下）；线上 occupations.json 现含全部 6 国 3103 职业。

---

## 本会话完成（2026-06-26）

### 1. 全量 AI Exposure 指数（AIOE）铺开 — 完成
- **BLS 屏蔽程序化下载**（curl 得 1323B "Access Denied"）。改用 **O*NET center（onetcenter.org，可下载）的 `ESCO_to_ONET-SOC.xlsx`**：ESCO 码前 4 位即 ISCO-08 → 映射 O*NET-SOC≈SOC6 → AIOE。建 `.codex_tmp/isco4_aioe.json`（436 个 ISCO unit group 100% 覆盖）。
- 各国→ISCO crosswalk（均落 `.codex_tmp/`）：AU/NZ=ABS ANZSCO2022 corr Table4(`anzsco_isco.json`)；DE=BA KldB5→ISCO 聚合4位(`xwalk_de.json`)；UK=ONS SOC2020→2010→SOC2010-ISCO(.xls 需 `pip install xlrd`)(`xwalk_uk.json`)；CA=StatCan NOC2016→2021 csv + NOC2011→ISCO HTML 表(`xwalk_ca.json`+`xwalk_ca_noc4.json`)。
- 新脚本 **`scripts/compute_aioe.py`**（`--country` / `--dry`）：US 直配 SOC（未命中按 SOC 组均值回退，method='direct'）；其余国本国码→ISCO 均值（method='crosswalk'，aioe_soc 存 "ISCO:xxxx"，前缀回退兜底）。
- 覆盖 **AU 519/520·NZ 518/519·CA 262/262·UK 368·DE 642·US 775/792**（17 个 US 军职 major 55 AIOE 本身不含，留空正确；AU/NZ 各 1 个 ANZSCO 未映射）。
- 前端 `[slug].astro` AIOE 块按 method 区分文案（crosswalk 显示 "经 ISCO-08 xxxx 跨分类对应，仅供参考"）。

### 2. UK + DE 接入站点 — 完成（已构建，翻译待跑）
- `site/src/lib/data.ts`：COUNTRIES 加 'UK'/'DE'；CURRENCY(GBP/EUR)；COUNTRY_NAME/COUNTRY_TITLE_ZH；**国旗 SVG**（UK Union Jack、DE 三色，带 xmlns，禁 emoji）；SOURCES_BODY(ONS/HMRC/UKVI、BA/destatis/技术移民法)；MIG_TEXT(Skilled Worker/Global Talent/Health&Care、EU Blue Card/Chancenkarte/Anerkennung)。
- `pages/en/about` 分类说明补 UK(SOC)/DE(KldB)。
- 预览验证 UK/DE 页面 200、代码标签(SOC/KldB)、AIOE、国旗均正常。

### 3. AU/CA/NZ 补全广度 — 完成
- 新脚本 **`scripts/gen_au_occupations.py`**（克隆 gen_uk，ANZSCO/AUD/482·186·189·190·491 签证）。清单 `.codex_tmp/anzsco_target.json`（ABS ANZSCO 1076 个中跨 8 大类均衡抽样 ~290 新 + 现有以便跳过）。
- AU 257→**520**；gen_nz 镜像→NZ 258→**519**；gen_ca（LLM 分配 NOC 码）→CA 168→**262**。
- ai-block：copy_ai_blocks 复制母体匹配；未匹配的用 `gen_ai_insights`/`gen_ai_disruptors`（**LLM_PROVIDER=deepseek**）补；现 AU/NZ/CA `no_ai=0`，仅极少数无 disruptor（真实"无有效工具"）。

### 4. 导出 + 构建 — 完成
- `export_site_data` → 3103 职业入 occupations.json。`npm run build` → **31,172 页 0 错误**（含 UK/DE）。

## 当前规模（DB & 站点）
AU **520** + CA **540** + NZ **519** + UK **368** + DE **642** + US **792** = **3381**（构建 33,952 页 0 错误）。
（CA 后续又用官方 NOC 2021 清单驱动 `scripts/gen_ca2_occupations.py` 从 262→**540**，仅中英；NOC 清单 `.codex_tmp/noc_target.json`/`noc2016_2021.csv`。AIOE 540/540。）

## 未提交清单（git status，HEAD=ccd8a40b，全部未提交未推送）
- 新脚本：`scripts/compute_aioe.py`、`scripts/gen_au_occupations.py`、`scripts/gen_uk_occupations.py`、`scripts/gen_de_occupations.py`。
- 改：`scripts/_i18n_fields.py`(aioe 导出)、`site/src/lib/data.ts`(UK/DE 全套+Occ.ai aioe 类型)、`site/src/pages/.../[slug].astro`(AIOE 块+migration country-aware)、`site/src/pages/en/about`、`site/src/data/*.json`(导出产物)。
- 改名：`scripts/copy_us_ai_blocks.py`→`scripts/copy_ai_blocks.py`。
- 新数据目录：`career-contents/{uk,de,au,ca,nz}/` 增量 md。
- `.codex_tmp/` 多个 crosswalk json（compute_aioe 依赖，建议保留/纳入）。

## 关键运维 / 坑（持续有效）
1. AI 生成全部走 **LLM_PROVIDER=deepseek**（claude 无余额）。gen_ai_disruptors 必须 `--rest 0`（默认 1800）。各脚本幂等。
2. compute_aioe 对**无 occupation_ai 行**的职业 UPDATE 是空操作——必须先 insights 建行再 compute_aioe。
3. BLS 全站屏蔽下载；ISCO 桥走 O*NET ESCO。.xls 读取需 xlrd。
4. 评分 10 分制存储展示÷2；is_migration 0/1/2；国旗内联 SVG 禁 emoji；URL 国家码大写（/UK/zh-CN/...）。
5. 翻译链：`collect_strings`（采集源串）→ `translate_strings`（翻缺失）→ `export_site_data` → build。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-26.md 继续」。
