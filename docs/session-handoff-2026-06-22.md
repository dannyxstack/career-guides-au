# 会话交接 · 2026-06-22（美国 SOC 职业全量采集 + 新西兰待跑 + 站点三大板块全球化收敛）

> 接续 `docs/session-handoff-2026-06-21.md`。
> DB = 远程 MySQL `192.168.194.135:13306`，配置读 `.env`；翻译/AI 生成 `$env:LLM_PROVIDER="deepseek"`。
> 站点品牌 **AI Career Graph**，域名 `https://aicareergraph.com`。Python：`e:/run/conda_envs/career-video/python.exe`。

---

## ⚠️ 立即可续做（RESUME / 待办）

1. **续跑美国全量生成（最优先）**。进程此前已自行退出（停在本次 107，`us_done.json` 共 **155** 个完成；目标 742，剩 ~587）。幂等续跑：
   ```powershell
   Set-Location E:\work\career-guides-au; $env:LLM_PROVIDER="deepseek"
   e:/run/conda_envs/career-video/python.exe -m scripts.gen_us_occupations --batch-size 50 --rest 0
   ```
   后台跑（run_in_background）。完成后 DB US 应接近 ~790（867 detailed − 75 "All Other" − 失败若干）。

2. **启动新西兰全量生成**（用户要求与美国并行）。脚本 `scripts/gen_nz_occupations.py` **已就绪**：镜像每个 AU 职业生成 NZ 版（沿用 AU 的 ANZSCO 码，country='NZ'），**ai-block 直接按相同 ANZSCO 码从 AU 复制**（无需 LLM 匹配）。当前只有 2 个，待全量 ~257。幂等状态 `.codex_tmp/nz_done.json`：
   ```powershell
   Set-Location E:\work\career-guides-au; $env:LLM_PROVIDER="deepseek"
   e:/run/conda_envs/career-video/python.exe -m scripts.gen_nz_occupations --batch-size 50 --rest 0
   ```
   ⚠️ 美国 + 新西兰并行会同时打 DeepSeek + DB 连接池，注意限速/连接坏（坏了杀掉重启即可，幂等）。

3. **美国 Phase 2 — ai-block 复用（US 全量跑完后做）**：
   - 读 `.codex_tmp/us_ai_match.json`（{us_occ_id: {country, occ_code, src_occ_id}}，~67% 命中母体），把母体的 `occupation_ai` 行 + `occupation_ai_disruptor` 链接**复制**到 US occupation_id（`adjacent` 置空；`ai_disruptors` 目录天然共享）。**复制脚本尚未写**，需新建（参考 `gen_nz_occupations.py` 里的 ai-block 复制函数，约 136 行起）。
   - 无母体的 US 职业回退：`gen_ai_insights --country US` + `gen_ai_disruptors --country US`。
   - 决策已定：方案 **B + 匹配方式 a**（采集时让 LLM 输出最接近的现有 AU/CA 职业名，Python 归一化解析；country-aware）。

4. **Phase 3 — 翻译/导出/构建**（US+NZ 数据齐后统一做一次）：
   `collect_strings → translate_strings --locales en →`（只生成 zh-CN+en，US/NZ 新增大量中文母本需翻 en）`export_site_data → cd site; npm run build`。

5. **Phase 4 — 前端接入 US**：`COUNTRIES`（data.ts 第 8 行）目前 `['AU','NZ','CA']`，**需加 'US'**；并补 `COUNTRY_FLAG` 美国 SVG 国旗（带 xmlns，禁 emoji，见记忆 flag-rendering-rule）、`COUNTRY_NAME`、currency=USD、首页国家卡。NZ 已在 COUNTRIES 内但数据原仅 2 个，全量后需确认前端正常。

6. **大量未提交改动**（建议 US/NZ 全流程完成后统一提交，避免提交半成品 md）：
   - 前端：站点三大板块全球化收敛（见下「本会话完成 1」），**已 dev 实测、未 commit**。
   - 新脚本：`scripts/gen_us_occupations.py`、`scripts/gen_nz_occupations.py`。
   - 数据：`.codex_tmp/soc_2018.json`（已 gitignore，可不提交）；`career-contents/us/`、`career-contents/nz/` 的 md。
   - 注意 `.env`、`__pycache__`、`.codex_tmp`、`.claude` 已被 `.gitignore` 排除。

7. **未决/含糊**：用户最后有一句「选A」但当时无待答问题，含义不明，需向用户澄清（可能指某个被打断的选择）。

---

## 本会话完成

### 1. 站点三大板块全球化收敛（前端，已 dev 实测，未 commit）
**目标**：AI Career Map / Rankings / About 不再每国一套，改为**全球唯一一套**（`/en/...`）。
- **删除** 4 个国家级页面：`site/src/pages/[country]/[locale]/{about,ai-graph,rankings/index,rankings/[rank]}/`。旧路由 `/AU/en/{about,ai-graph,rankings}/` 现 **404**（已验证）。
- **nav/入口重定向到全球版**：`Base.astro` 国家页导航 AI图谱/榜单/关于 → `/en/...`（Home 仍指本国）；详情页 `[slug].astro` 的「查看图谱」、国家首页两张促卡（ai-graph-promo / rankings-promo）→ `/en/...`；全球 about 的「各国清单」改指各国首页 `/{cc}/en/`（原指已删的各国 about）。
- **地域榜（高增长 / 移民友好）改成全球跨国榜保留**（用户决策「改成全球榜保留」）：`data.ts` 的 `GLOBAL_RANKING_ORDER` 扩为全部 8 个键（原排除 high_growth/migration_friendly）。于是 `/en/rankings/` hub 自动多出 `rank-high-growth`、`rank-migration-friendly` 跨国卡片榜，且各有 `/en/rankings/{key}/` 全量页（实测 200）。
- 清理：hub 移除 geo 国家选择器 section、"{cc} rankings →" 提示及 `.geo-*` 样式与无用 import；全球 `[rank]` 的国家列由「链接到各国榜」改为**纯标签** `<span class="tag gov">`，删除无用 `slug2`、`.cty-link` 样式。
- 验证（dev 4399）：hub 200 且含两新榜、无 geo section；`/en/rankings/migration-friendly/` 200；`/AU/en/{rankings,about,ai-graph}/` 全 404；`/AU/zh-CN/` 导航与促卡 href 全部 `/en/...`。

### 2. 全球榜单页交互（上一指令）
- 全球榜单 `[rank]` 表头滚动**保持吸顶**（原已实现，确认 `thead th{position:sticky;top:0}` 生效）。
- 全球榜单页 `data-section="filter"` 筛选条**取消吸顶**（全球页 `.controls` 漏设 position，补 `position:static`；实测滚动后 top=-351，表头仍 top=0）。
- 文件：`site/src/pages/en/rankings/[rank]/index.astro`。**此两项 + CA 英文翻译导出已被外部提交进 `415c868 "update site"`**（非本 agent 提交，疑用户/钩子顺手提交；该提交不含 US，干净）。

### 3. 美国 SOC 职业采集（Phase 0–1，进行中）
- **Phase 0**：SOC 2018 清单。BLS 官网反爬（Akamai 403），改从 GitHub `rageycomma/soc-json` 下载 `soc.json`，解析出 **867 个 Detailed 职业**（23 major 组），存 `.codex_tmp/soc_2018.json`（含 soc/title/major/definition）。生成时**排除 75 个 "…All Other" 兜底类** → 目标 ~792。
- **Phase 1**：`scripts/gen_us_occupations.py`（照搬 CA 生成器 + 美国特化）：
  - 遍历 SOC 清单，DeepSeek 生成：中文名、中英简介、教育、资质、薪资(USD)、**签证(H-1B/EB-2/EB-3/O-1/TN/L-1/Green Card)**、11 维 10 分制评分、适合人群、中英 FAQ、增长词；**分类由 LLM 从站点现有 11 类择一**；`is_migration` 新语义（0=难担保/几乎无技术移民；1=常见 H-1B/EB 绿卡；2=受限/配额紧张）。
  - **方式 a 匹配**：system prompt 内置 AU+CA 职业英文名候选池（DeepSeek 缓存便宜），LLM 返回 `match_name`/`match_country`，Python 归一化解析（优先 (country,name) 再回退 name），写 `.codex_tmp/us_ai_match.json`。
  - `seed_occupation_v2` 入库（country='US', occ_code=SOC, occ_code_type='SOC', anzsco_code=SOC, currency='USD'）+ 英文 FAQ + `generate_md(soc,'US')` 出中英 md（career-contents/us/）。
  - 幂等 `.codex_tmp/us_done.json`；批次 `--batch-size/--rest`。
  - **试水 50 个验收**：成功 48、有母体 32（复用率 ~67%）、失败 2（瞬时超时 + 数据不完整，幂等可补）；抽查 Advertising and Promotions Managers：USD 三档薪资、H-1B/EB-2/EB-3/L-1A、母体 CA/10022 有效，全部正确。
  - **全量进度**：`us_done.json` **155** 完成（DB US **157**，含早期 2 个测试），进程已退出，**待续跑**（见 RESUME 1）。

## 当前规模（DB）
- 职业：AU **257** + CA **168** + NZ **2** + US **157** = **584**（US/NZ 全量后预计 ~257+790 再增）。
- 注意：US 的 ai-block 多数尚未复用/生成（待 Phase 2）；US/NZ 新增中文母本尚未 collect/translate（待 Phase 3）。

## 关键运维 / 坑（持续有效）
1. DB 远程 `192.168.194.135:13306`，读 `.env`；连不上让用户启那台机。
2. 翻译/AI 生成需 `$env:LLM_PROVIDER="deepseek"`。长进程连接池会坏（大量 Connection error 空转）→ 杀掉重启（幂等，新连接正常）。后台用 run_in_background。
3. 跑 `-m scripts.X` 前先 `Set-Location` 回项目根（PowerShell 工作目录可能漂到 site\，相对路径 Tee/Out-File 会失败）。
4. **后台任务输出文件是 GBK 编码**，Read/Grep 看会乱码；用 python `open(path,encoding='gbk',errors='replace')` 读，或直接看终行汇总。
5. `export_site_data`：is_migration 用 `int()`；评分/AI 分 float。slug 在导出时按 name_en 生成（seed 不写 slug）。
6. PowerShell 5.1 无 `&&`；`@'...'@` 是 PowerShell here-string，**勿在 Bash 工具里用**（会把 `@` 当内容）。
7. 评分 10 分制存储、展示 ÷2；is_migration 0/1/2（见记忆）。国旗用 data.ts 的 COUNTRY_FLAG 内联 SVG，禁 emoji。
8. 本会话期间 Bash/PowerShell 安全分类器一度「temporarily unavailable」→ 只读工具（Read/Grep/Glob）不受影响，命令类需稍后重试。
9. dev server 由 preview MCP 起在 4399（astro，端口 4321 常被本地另一实例占用）。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-22.md 继续」。
