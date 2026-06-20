# 会话交接 · 2026-06-19（Docker 部署 + 25 新职业/公职字段 + 多国(NZ/CA) + AI 时代职业图谱/榜单 + About）

> 接续 `session-handoff-2026-06-16.md`。本会话把站点从「澳洲多语言职业站」升级为 **「AI 时代职业图谱 / 职业规划」** 产品方向，并扩展多国与公职类职业。
> DB = 远程 MySQL `192.168.194.135`，**端口 13306（非 3306）**，全部配置从 `.env` 读（MYSQL_HOST/PORT/USER/PASSWORD/DATABASE）。翻译用 DeepSeek（`LLM_PROVIDER=deepseek`）。

---

## 一、本会话完成（按主题）

### 1. Docker 部署（site/）
- 纯静态 SSG，数据 JSON 已落盘 `site/src/data/`，构建期不连 DB。
- 文件：`site/Dockerfile`（多阶段 node:20→nginx:1.27，`ARG SITE_URL` 注入域名）、`nginx.conf`（监听 8080、目录式 try_files、gzip、缓存、安全头）、`docker-compose.yml`（仅绑 127.0.0.1:8080，交前置反代）、`.dockerignore`、`DEPLOY.md`。
- 线上已有 nginx 时**更推荐直接 host nginx 托管 dist**（见 DEPLOY.md），不必套 Docker。**绝不要后台跑 `npm run dev`**。

### 2. PR 标签改文案（方案 A）
- `cardBadges`（`data.ts`）：在移民清单上 → 绿色「可技术移民 / PR pathway」+ hover 释义；**不在清单上不再显示标签**；子标签 `Easier PR`。筛选器 `fPR` 同步改「可技术移民」。

### 3. 新增 25 个职业（福利/澳洲特有 10 + 公职 15）+ 公职字段
- 新列 `occupations.is_public_servant`（`migrate_public_servant.py`）；前端卡片蓝色「公职 / Public sector」标签（`.tag.gov`）+ hover 释义。
- 新分类 **Government & Public Sector**（共 11 类）。
- 入库脚本 `seed_batch_public_au.py`（NDIS 支持协调员/行为支持师/计划管理/LAC/居家照护协调/理财顾问/Strata/买方代理/原住民健康/石棉清除 + 政府行政/客服/议会/项目/儿童保护/惩教/住房/高校行政/拨款/选举/法院书记/健康信息/医院行政/环境健康/交通车站）。`flag_public_servants_existing.py` 给已存在的 Procurement Officer 补标记。全部 `is_migration=0`。
- 占位 occ_code 已逐个核验不与现有冲突（唯一键 = country_code+occ_code）。

### 4. 教育路径表头修正
- 那列是费用不是薪资：新增 UI 键 `cost`，表头 `年薪(AUD)`→`费用 (AUD)`（后改为动态货币）；薪资表仍用 `annual`。两者已分离。

### 5. 190/491 最低获邀分
- 独立表 `occupation_invitation_scores`（occupation_id×visa_subclass→min_score/asof/note/source_url，`migrate_invitation_scores.py`）——与 seed 解耦（seed 清 visa 行不影响），**供后续定时任务 upsert**。
- `seed_invitation_scores.py` 按大类填 190/491 的 2025–26 竞争性参考分（技工 75/70 等，标「参考」）。详情页 190/491 说明后追加「· 2025–26 竞争性获邀约 X 分（参考）」。
- **190/491 无全国统一每职业分（各州自定）；189 全国按职业公布（2025-11 技工 65）——189 采集待办未做。**

### 6. 多国支持（NZ / CA）
- 每国独立行（country_code），**无需"是否存在某国"标记**；occ_code_type 区分 ANZSCO(AU/NZ)/NOC(CA)。
- 新列 `occupations.currency`（`migrate_currency.py`，AUD/NZD/CAD）。`_i18n_fields.fetch_bundles(cur, country=None)` 默认导出**全部国家**。
- `data.ts`：COUNTRIES=['AU','NZ','CA']、CURRENCY、countryName、occByCountry、categoriesFor；首页所有 section/详情/列表按 country 过滤；薪资/费用表头货币动态（`{t.annual} ({cur})`，UI 标签去掉写死 AUD）。`Base.astro` 顶部**国家切换器**（与语言分离）。compare 仅 AU。md_generator 加 `country` 参数（国名/货币/输出 `career-contents/{cc}/`）。
- 样本：CA RN(31301)/SWE(21231)、NZ RN(254418)/电工(341111)，`seed_intl_sample.py`，含各国签证（Express Entry/PNP、Green List/SMC/AEWV）。
- CA/NZ 详情页底部「数据来源」按国家区分：`sourcesBody(country, locale)`（AU/CA/NZ 各自来源，已纳入 TM 全 10 语言，见 `add_sources_strings.py`）。

### 7. AI 时代板块（每职业详情页，雷达图下方）
- 新表 `occupation_ai`（`migrate_ai_insights.py` + `migrate_ai_graph.py`）：
  - 文案：verdict_type(compressed/amplified/mixed)、verdict_zh、entry_narrowing_zh、replaced_zh/augmented_zh/moat_zh/skills_zh(JSON)、upgrade_path_zh、adjacent(同国 occ_code 数组)。
  - 图谱：cluster + automation_exposure/human_moat/entry_risk/ai_upside（1-5）。
- 展示顺序：①结论(彩色徽章) ②[AI 会接管/替代/消除的任务 | AI 会增强的任务] ③[人类护城河 | 未来5年技能(并排)] ④入门是否变窄 ⑤AI 时代升级路线 ⑥相邻职业(可跳转) ⑦你在 AI 图谱中的位置(cluster 徽章+4 项 1-10 分条+链接)。
- 标题动态「{职业名}会怎样 / {职业名}在 AI 图谱中的位置」；分数展示 ×2 为 /10。
- 样本：`seed_ai_sample.py`（General Clerk 532111=compressed、RN Medical Practice 254422=amplified，含精修的护理语境文案 + 升级路线）。中文列表/句子经 TM 翻全 10 语言。

### 8. AI 职业图谱页 `/[country]/[locale]/ai-graph/`
- hero + 6 类卡片 + 二维矩阵(SVG，x=automation_exposure y=human_moat，同分加确定性 jitter 散开，圆点点击进职业页) + 分类详情(why/replaced/moat/fit/unfit/actionIn/actionOut/pivot/代表职业)。
- 类别 editorial = 常量 `AI_CLUSTERS`（data.ts，zh/en，其余语言回退 en）。`seed_ai_graph.py` 给 30 个代表职业按大类分配 cluster+原型分（只更新这几列不动文案）。

### 9. AI 时代职业榜单 `/[country]/[locale]/rankings/`（hub）+ `/rankings/[rank]/`（完整页）
- 8 榜单（low_ai_replacement/ai_augmented_rank/licensed_moat/physical_site/human_trust/high_growth/migration_friendly/cautious_newbie），**全部由排序公式实时生成**（`RANK_SCORE`/`rankingList`），不入库、无 ai_rank_tags。
- hub：每榜 Top6（OccCard）+ 一句话解释 + 查看完整。完整页：筛选 chips(技术移民/高薪/短培训) + 榜单解释 + 表格(排名/职业/AI风险★/护城河/未来增长★/薪资/PR★/推荐理由) + 相关榜单 + **数据来源与方法**(h2 标题，复用 sourcesBody)。
- 完整页表头 `position:sticky` 吸顶（本页 .controls 改 static、wrap 桌面 overflow:visible 才能吸顶）。

### 10. 导航 + About
- nav：首页 / AI 图谱 / 职业榜单 / 关于（`navHome/navGraph/navRank/navAbout`）。
- About 页 `/[country]/[locale]/about/`（基于项目历程，zh/en 自包含）+ 按国家数据来源。
- 修了首页两个入口卡错位：`a.card{display:block}`（行内 a 包块级子元素导致）。

---

## 一·补（2026-06-20 续）：品牌升级 + 评分 10 分制 + AI 字段铺全量

### A. 品牌升级为 AI Career Graph（域名 aicareergraph.com）
- `siteTitle` 全 10 语言统一 `AI Career Graph`（data.ts zh/en + 脚本批量改 ui_i18n.json 8 语言）；`tagline` 改新定位。
- SEO 标题：根页/各国首页/职业页/AI图谱页按 locale 分支（zh / 其余→en）；新增 `countryTitleName`（zh 简称 澳洲/新西兰/加拿大）、`homeMetaDesc`/`agMetaDesc`。
- `astro.config.mjs` site→`https://aicareergraph.com`；`Base.astro` 加 OG/Twitter。
- 关于页重构 6 板块（我们是谁/解决什么/如何分析/数据与方法/不做什么/未来计划）。
- nav：国家切换加内联 SVG 国旗（Windows 无 emoji 字形，故不用 🇦🇺）+ nav-sep；首页 AI 图谱板块补 `homeAgTitle`。

### B. 评分全面改 10 分制（小数，≥1 位；仅展示星星时 ÷2 取半星）
- 迁移 `scripts/migrate_score_scale_10.py`（**幂等**：max>5 视为已迁移跳过）：
  - `occupation_ratings.stars/score` ×2；`occupation_ai` 4 列 TINYINT→**DECIMAL(3,1)** 且 ×2。
  - `occupation_invitation_scores.min_score`(65-90) 非五分制，**不动**。
- 计算同步：`export.overall_score`（`6-s`→`12-s`、去 `/5*10`）；`data.ts` RANK_SCORE 常数（`6-`→`12-`、`+3`→`+6`、`+2`→`+4`，`*2` 权重不变=2×等比排序不变）；`cardBadges` 阈值 ×2；ai-graph 矩阵 `(v-1)/4`→`(v-1)/9`、分隔线 `px(3)`→`px(5.5)`。
- 展示：新增 `data.ts:renderStars(n10)`（÷2 半星 ½）；slug/compare/rankings 三页改用它；slug AI 分条 `/5`→`/10`、去 `×2`；RatingRadar 调用传 `max={10}`；`md_generator._stars` 同步半星。
- `_i18n_fields` 把 AI 4 分转 float（避免 DECIMAL→字符串）。`seed_ai_graph` 原型分 ×2。
- **新增/改评分数据务必产出 10 分制**（含未来新职业的 ratings seed——目前历史 seed 仍是 1-5，再用时需 ×2 或走迁移）。

### C. AI 字段铺全量（todo#1 执行中）
- `scripts/gen_ai_insights.py`：缺数据(verdict_zh|cluster 为空)的职业逐个调 `llm.complete_json`（DeepSeek，需 `$env:LLM_PROVIDER="deepseek"`），生成 cluster+4 分(10 分制)+全套文案；adjacent 由 LLM 从「同国职业清单」挑 occ_code 再校验存在才写。逐行 REPLACE，`--limit/--country/--redo`。
- 跑完后链路：`collect_strings` → `translate_strings`（9 语言）→ `export_site_data` → `npm run build`。

### D. is_migration 升级为 0/1/2 枚举（2026-06-20）
- 列注释更新：**0=非技术移民；1=可直接技术移民(189/190/491，也可雇主担保)；2=受限(仅雇主担保482/494或DAMA/劳务协议)**。
- AU 分类核对：抓取官方 **CSOL PDF**(`immi.homeaffairs.gov.au/Documents/core-sol.pdf`，456 职业)实证核对；22 个 1→2、10 个 1→0、快递司机(732111)→0。AU 现 0=52 / 1=172 / 2=22。
- **导出坑**：`export_site_data.py` 原把 is_migration `bool()` → 必须 `int()` 输出 0/1/2，否则前端 `===1/===2` 全失效。
- 前端：`data.ts` Occ.is_migration 改 `number`；cardBadges 1=绿「可技术移民」/2=橙「雇主担保移民」(+hover)；`bestMigration`/`migration_friendly`/OccCard&rankings 的 `data-pr` 全改 `===1`；slug 顶部标签三态 + value2 移民板块加 `migRestrictedNote`；新增 UI 串 `migRestrictedOcc/migRestrictedNote/overallTip/visaCode`(zh/en)。
- markdown：`md_generator` `_sec_visa(mig)` 三态 + head/tail 三态；受影响 33 个已 `generate_md.py` 重生成。
- 关于页：新增 `AU_SOURCE_LINKS`（CSOL/Home Affairs 技术清单/DAMA/JSA/ABS ANZSCO），仅 AU 关于页渲染。
- 评分标题加即时 CSS 信息提示 `.info`（Base.astro 全局）；移民板块顶部显示「提名职业代码」。

## 二、关键运维 / 坑

1. DB 远程 MySQL `192.168.194.135` **端口 13306**；连不上让用户启动那台机。配置全读 `.env`。
2. 翻译 DeepSeek 后台用 **PowerShell `Start-Process`**（`-WindowStyle Hidden`，先在当前会话 `$env:LLM_PROVIDER="deepseek"` 让子进程继承——**5.1 不支持 `-Environment` 参数**）；输出重定向 log/err。Bash `&` 子进程会被回收。
3. **PowerShell 工具工作目录跨调用持续**：`cd site` 后再 `-m scripts.X` 会 ModuleNotFound，先 `Set-Location` 回项目根。
4. **Astro `getStaticPaths` 被提升**，不能引用其后定义的 const（如 slugRank），需 inline 或在其前定义。
5. 行内 `<a class="card">` 包块级子元素会错位 → 已加 `a.card{display:block}`。
6. UI 级新文案（cluster editorial、rkMethod、About、AI 板块标题等）多为 **zh/en，其余 8 语言回退 en**；**职业正文/列表/来源**走 TM 全 10 语言。
7. 部署前 `site/astro.config.mjs` 的 `site` 仍是占位 `https://example.com`，需改真实域名（或 Docker `--build-arg SITE_URL=`）。

---

## 三、当前规模 / 自检

- 职业 **250**（AU 246 + CA 2 + NZ 2）；公职 16；源串 **7801**，9 语言均 7801；构建 **2931 页**；11 分类。
- ~~仅 30 个职业有 ai_graph 数据~~ → **2026-06-20：全部 250 职业均有 cluster+4 分(10 分制)+完整 AI 文案**，已翻 10 语言。AI 图谱矩阵(AU 246 点)、8 个榜单(每榜 ~247 行)、各职业 AI 板块均自动填满（页面数据驱动，重新 export+build 即更新，无需改代码）。源串 7801→**13482**，10 语言均齐（es 曾差 389 已补）。

```powershell
# 标准重建链（DB→JSON→build）
Set-Location E:\work\career-guides-au; $env:PYTHONUTF8="1"; $py="e:/run/conda_envs/career-video/python.exe"
& $py -m scripts.export_site_data
Set-Location E:\work\career-guides-au\site; npm run build   # dev: npm run dev -- --host （手机预览需 --host）
# 各语言译文计数
& $py -c "import sys;sys.path.insert(0,'.');from db.connection import get_cursor`nwith get_cursor() as c:`n c.execute('SELECT locale,COUNT(*) n FROM translations GROUP BY locale');[print(r) for r in c.fetchall()]"
```

---

## 四、待办 / 下一步（重点）

1. **【重点】把 AI 字段铺到全部 250 职业**：用 LLM 按模板批量生成每职业的 `ai_graph`(cluster+4 分) + AI 文案(verdict/replaced/augmented/moat/entry/skills/upgrade/adjacent)，人工抽检；之后图谱/榜单自动填满。
   - 实现方式（2026-06-19 已定）：新脚本 `scripts/gen_ai_insights.py`，查 `verdict_zh IS NULL OR cluster IS NULL` 的职业，逐个调 `video_pipeline/llm.py:complete_json`（DeepSeek，json_object）按 schema 生成全部字段，校验(cluster∈6类/分数1-5/verdict_type∈3类/列表非空) 后 upsert `occupation_ai`；再 export→translate(走 TM 全 10 语言，中文母本经 `collect_from_bundle` 自动产出 ai_verdict/ai_entry/ai_upgrade/ai_list)→build。
   - **adjacent 生成（已定）：让 LLM 推荐职业名 → 反查同国 `occ_code` 校验，查不到的丢弃**（不走纯 DB 同分类）。
   - 建议先试跑 5 个抽检文案语气后再跑全量 ~248（当前仅 30 有 cluster、2 有完整文案）。
2. **189 获邀分采集**（按职业公布，技工 65 等）→ `occupation_invitation_scores`(visa_subclass='189')；190/491 待定时任务接入各州精确数据。
3. 定时任务：更新获邀分（占位参考值 → 真实）。
4. 可选：cluster editorial / rkMethod / About / AI 板块标题 等 UI 文案补全 10 语言（走 translate_ui 或 TM）。
5. 部署前改真实域名再 build。
6. 25 新职业 + 4 国际样本薪资为联网估算，上线前二次核对（todo#5 历史项）。
7. 矩阵可选增强：hover 卡片、按类别筛选高亮（之前定先不做复杂交互）。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-19.md 继续」。
