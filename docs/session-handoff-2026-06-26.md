# 会话交接 · 2026-06-26（全量 AIOE、UK/DE 接入、AU 520/CA 540/NZ 519 扩充、404 页、已合并 main；翻译因 DeepSeek 余额中断待续）

> 接续 `docs/session-handoff-2026-06-25.md`。
> DB = 远程 MySQL `192.168.194.135:13306`，配置读 `.env`（键名 **MYSQL_HOST/PORT/USER/PASSWORD/DATABASE**；表名是 `occupations` 非 `occupation`，国家列是 `country_code`）。
> **AI 生成（insights/disruptors/翻译）必须 `LLM_PROVIDER=deepseek`**——默认 claude 会因 Anthropic 余额不足全失败（本会话踩过）。gen_au/nz/ca 核心数据直连 DEEPSEEK_API_KEY 不受影响。
> 长 Python 任务前加 `PYTHONIOENCODING=utf-8`。站点品牌 **AI Career Graph**。Python：`e:/run/conda_envs/career-video/python.exe`。

---

## ⚠️ 立即可续做（RESUME / 待办）

### 1.【唯一大待办】完成 9 语言翻译 — **因 DeepSeek 余额耗尽中断**
- `translation_src` 现 156,038 源串（含 CA 540）。**已译完：en / es / pt（各 156,038，在 DB）**；vi 部分；**th/ms/id/zh-Hant/ja 未译**。
- 中断原因：DeepSeek **402 Insufficient Balance**（充值后即可续）。**用并行器**，不要用单线程 translate_strings（会因无超时挂死）：
  `$env:LLM_PROVIDER="deepseek"; python -m scripts.translate_parallel --workers 20 --batch 20`（幂等，自动只补未译对；线程池 20 并发；失败批二分重试）。
- 跑完 `python scripts/export_site_data.py` + `npm --prefix site run build`。
- **注意：en/es/pt 译文还在 DB，尚未 export 进 translations.json**，所以当前线上构建这 3 语言还未变化；充值跑完后统一 export 即生效。

### 2. 生产部署机制（重要）
- 生产环境**每 5 分钟 `git pull`(main) + `npm run build`**。`site/dist/` 是 gitignore 的（仓库不收构建产物），生产从源码构建。
- 本会话全部改动**已合并并推送到 `main`（HEAD `90828e44`）**，下个构建周期自动生效。

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

### 4. CA 二次扩充（NOC 清单驱动）— 完成
- 原 gen_ca 镜像 AU、由 LLM 反推 NOC 受碰撞限制只到 262。新建 **`scripts/gen_ca2_occupations.py`**（克隆 gen_au，CA/NOC/CAD/Express Entry·PNP·LMIA），用官方 NOC 2021 五位清单（516 个，`.codex_tmp/noc_target.json`，源自 `noc2016_2021.csv`）直接驱动。CA 262→**540**（仅中英）。AIOE 540/540。

### 5. 导出 + 构建 — 完成
- `export_site_data` → 3381 职业入 occupations.json。`npm run build` → **33,953 页 0 错误**（含 UK/DE + 404 页）。

### 6. 自定义 404 页 — 完成
- `site/src/pages/404.astro`（Astro 构建为 `dist/404.html`，主机未命中路径时返回）。用 Base 的 `global` 模式保留顶部菜单+底部说明，中英双语，按钮回首页/图谱/榜单。
- 注：线上旧 404（如 US `medical-and-health-services-managers`）本质是**旧构建**，该职业(11-9111)当前数据存在，重新构建即恢复。

### 7. 并行翻译器 + DeepSeek 超时 — 完成（基础设施）
- `scripts/translate_parallel.py`：线程池并发翻译（替代会挂死的单线程 translate_strings）。`video_pipeline/llm._deepseek` 加 120s 超时+重试（原无超时，一个挂起连接阻塞全部）。

## 当前规模（DB & 站点）
AU **520** + CA **540** + NZ **519** + UK **368** + DE **642** + US **792** = **3381**（构建 33,953 页 0 错误，含 404 页）。

## Git 状态（已全部合并推送）
- 分支 `feat/aioe-ukde-breadth` 4 个 commit 已 **fast-forward 合并进 `main`，HEAD `90828e44`，已 push origin/main**。
- commit：`70658d4` AIOE/UK·DE/AU·CA gen 脚本 → `e49de7e` 3381 职业数据+career-contents → `3bc2db9` 并行翻译器+deepseek超时 → `90828e4` 404 页。
- `.codex_tmp/`(gitignore) 留有 crosswalk json（compute_aioe 依赖）；`site/dist/`(gitignore) 生产自行构建。

## 关键运维 / 坑（持续有效）
1. AI 生成全部走 **LLM_PROVIDER=deepseek**（claude 无余额）。gen_ai_disruptors 必须 `--rest 0`（默认 1800）。各脚本幂等。
2. compute_aioe 对**无 occupation_ai 行**的职业 UPDATE 是空操作——必须先 insights 建行再 compute_aioe。
3. BLS 全站屏蔽下载；ISCO 桥走 O*NET ESCO。.xls 读取需 xlrd。
4. 评分 10 分制存储展示÷2；is_migration 0/1/2；国旗内联 SVG 禁 emoji；URL 国家码大写（/UK/zh-CN/...）。
5. 翻译链：`collect_strings`（采集源串）→ **`translate_parallel`（并发，推荐）** → `export_site_data` → build。单线程 `translate_strings` 无超时易挂死，勿用于全量。
6. 生产：每 5 分钟 `git pull`(main)+`npm run build`；`dist/` 不入库。改动须合并到 **main** 才会上线。
7. 余额坑：DeepSeek 与 Anthropic 都可能余额耗尽（402/credit）——大批量任务前先确认余额；翻译已踩 DeepSeek 402。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-26.md 继续」。
