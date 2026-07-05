# 会话交接 · 2026-07-05（首页搜索本地化、11 新兴能源/半导体岗×8国、AI块+AIOE、社区投票功能）

> 接续 `docs/session-handoff-2026-06-30.md`。
> DB = 远程 MySQL（配置读 `.env`：MYSQL_HOST/PORT/USER/PASSWORD/DATABASE；表 `occupations`，国家列 `country_code`）。
> **翻译/AI 回退须 `LLM_PROVIDER=deepseek`**；长 Python 任务前 `PYTHONIOENCODING=utf-8`。Python：`e:/run/conda_envs/career-video/python.exe`。
> 生产：每 5 分钟 `git pull`(main) + `npm run build`；`site/dist/` 不入库。

---

## 本会话完成

### 1. 首页搜索结果本地化
- `data.ts` 新增 8 个 UI key（`hSrNoResults/hSrAvailIn/hSrAiAugmented/hSrAiLowRisk/hSrAiHigherExp/hSrAiMixed/hSrMigFriendly/hSrMigRestricted`，UI 现 203 key）。
- `Home.astro`：客户端搜索结果的国家名（走 `countryName`）+ AI/移民标签 + 空结果/"Available in:" 改为服务端注入 `SEARCH_I18N`（`#search-i18n` JSON），不再硬编码英文。
- 跑 `node scripts/_extract_ui.mjs` + `translate_ui.py` → 9 语言各补 8 key。
- **遗留**：搜索结果里的**职业名**走 `name_en`（英文索引）、**国家名/分类名**非 en/zh 全站显示英文（`COUNTRY_NAME` 只有 zh/en；country 页分类 chip 也直接渲染英文）——既有限制，非本次引入。

### 2. 11 个新兴能源/半导体岗 × 8 国 = 88 条（DB id 4473–4616，含回滚空洞，实 88 条）
职业：电力系统/储能BESS/EV充电/数据中心电气/保护控制/EV电池诊断/嵌入式固件/FPGA/ASIC/模拟IC/IC验证。
- `scripts/seed_energy_semiconductor_au.py`（AU 手写详数据）+ `scripts/seed_energy_semiconductor_multi.py`（NZ/CA/US/UK/DE/FR/ES 参数化：`SAL`薪资档 / `CODE`分类码 / `COUNTRY`移民签证，联网调研薪资）。详见记忆 [[energy-semiconductor-11roles]]。
- **occ_code = 「父级码-角色KEY」唯一合成**（如 `233311-PWR`/`17-2072-FPGA`），页面只展示 `anzsco_code`，避免撞既有行（id39=233311 电气工程师）。seed_v2 幂等按 `(country_code, occ_code)`。
- 评分 **10 分制直插**（DB 已统一 10 分制，seed 不再 ×2，见 [[scoring-10-point-scale]]）。
- 分类码：NZ ANZSCO / CA NOC(21310,21311,22310) / US SOC(17-2071/2072/2061/3023) / UK SOC2020(2123/2124/3113) / DE KldB(2630/2620) / FR ROME(H1202/M1805/I1305) / ES CNO(2441/2442/3132)。

### 3. AI 分析块 + AIOE
- **AI 块**：AU 跑 `gen_ai_insights --country AU` + `gen_ai_disruptors --country AU`；其余 77 用 occ_code 角色后缀匹配 AU 源、`copy_ai_blocks.copy_ai_block` 跨国复制（AI 影响与国别无关）。88/88 全覆盖 AI 块 + disruptors。
- **AIOE 学术暴露指数**（页面"AI 暴露指数"卡）：新职业初始 `aioe_pct=null`（`compute_aioe.py` 没跑过 + 读 occ_code 撞合成码）。**修 `compute_aioe.py:118` 改用 `COALESCE(NULLIF(anzsco_code,''),occ_code)`**（老数据 anzsco==occ，零回退）→ AU/CA/DE/NZ/UK/US 各 11/11 有 AIOE。**FR/ES 仍无 AIOE**（ROME/CNO 无 →ISCO crosswalk，所有 FR/ES 职业本就没有）。

### 4. 社区投票功能（通用引擎，2 个投票）
静态站外挂动态层：`GET/POST` API + MySQL。**定义配置驱动、跨国按 slug 共享、构建期烘焙**。
- `site/src/data/polls.json`（**投票定义单一真相源**，前端与 API 共用）：`ai_replace`（5 档，带 `mid` 折大众平均%）+ `career_change`（3 档）。加投票=加一项，表/API/widget 不动。
- `site/src/lib/polls.ts`（读取 + `locText/fillTpl/pctOf/avgFromCounts`）。
- `site/src/components/PollBlock.astro`（widget：SSR 题目/选项/结论 + 客户端拉实时/提交，接进 `[country]/[locale]/[category]/[slug].astro` AI 区块后）。
- `scripts/seed_polls_schema.py`：`poll_votes`（`(poll_code,occ_key,client_token)` 唯一→一人一票可改票）/ `poll_agg`（供烘焙）/ `poll_agg_num`（滑块型预留）。
- `api/polls_api.py`（FastAPI：`GET /api/polls`、`POST /api/polls/vote`、`GET /api/health`；ip_hash 限流 + Turnstile 可选 + 选项白名单校验 + 参数化 SQL）。
- `export_site_data.py` 加读 `poll_agg` 按 slug 烘进 `occupations.json`（`o.polls`）。
- 部署文档 `docs/polls-deploy.md`。
- **职业名注入（SEO/GEO）**：标题与结论句用 `{name}` 占位，服务端填职业名（爬虫可见）；结论 `{n}/{avg}/{pct.选项}` 服务端(烘焙)+客户端(实时)两处填。例：`基于 6 人投票，我们的访客认为电力系统工程师被 AI 替代的概率是 30%。`
- **坑**：`fillTpl` 第一步填 `{name}` 时 `\w+` 会误清 `{n}/{avg}/{pct.*}` → 改成**只替换传入的键、未知占位符原样保留**。

## 当前规模
AU 531 + NZ 530 + CA 551 + US 803 + UK 379 + DE 653 + FR 543 + ES 513 = **4503 职业**（较上次 +88）。

## Git
- 用户手动提交 `a8e8ac2f update site`（站点数据/前端：data.ts、occupations.json、translations、PollBlock/polls.ts/polls.json、slug.astro、export_site_data.py、compute_aioe.py 等）。
- 本 agent 补提交：`6e7af5bb`（88 岗 seed 脚本）、`c91fd65c`（投票 API+schema+deploy 文档）、本交接文档。
- **均未 push**（`git push origin main` 需你手动或授权）。origin/main 仍在 `7991a2cc`。

## 待办 / RESUME
1. **其余 8 语言未翻**（es/pt/vi/th/ms/id/zh-Hant/ja/de）：88 新岗只有 EN/ZH 母本（按用户要求暂缓）。补：`collect_strings` → `translate_parallel --locales <loc>` → export。
2. **投票功能上线**（`docs/polls-deploy.md` 详列，涉及服务器/域名，agent 无法代执行）：建最小权限 DB 账号、systemd 常驻 `uvicorn api.polls_api:app`、nginx 反代 `api.aicareergraph.com`+TLS、**build 时设 `PUBLIC_POLLS_API=https://api.aicareergraph.com/api`**、（可选）Turnstile 密钥。
3. **FR/ES AIOE**：如需补，要另建 ROME→ISCO / CNO→ISCO 对照表。
4. **push** 上述 3 个 commit。

## 关键运维 / 坑（本会话新增，持续有效）
1. **投票功能本地跑**：`python -m scripts.seed_polls_schema`（已建表）→ `POLLS_CORS_ORIGINS=http://localhost:4399 python -m uvicorn api.polls_api:app --port 8790` → `npm --prefix site run dev`（PollBlock 默认指 8790）。
2. `occupation_visa_pathways.visa_subclass` 是 **varchar(20)**；长签证名（Passeport Talent / Profesional Altamente Cualificado）会撑爆列 → **单事务整体回滚**（一度 CA/US/UK/DE 没入库）。已改短码+`[:20]`。多国批量 seed 用一个 `get_cursor`，任一国抛错会回滚全部。
3. `compute_aioe.py` 现按 `anzsco_code`（非 occ_code）查 AIOE；FR/ES 无 crosswalk。
4. 站点职业正文走 TM（`tr(zh,locale)`），**DB 的 en i18n 除 name 外基本不进正文**——en 页正文也靠 `translations.en.json`，新增职业须 `translate_parallel --locales en` 才有英文。
5. **导出前先停预览**：astro dev 占着 `occupations.json`，`export_site_data` 写入会 `OSError Errno 22`。
6. 预览标签 `location.assign` 深链常回落 `/`；验证用 `fetch()`（origin=localhost:4399 后）抓 HTML。
7. MySQL 保留字 `rows/empty` 不能直接做列别名。

> 恢复任务直接说「读取 docs/session-handoff-2026-07-05.md 继续」。
