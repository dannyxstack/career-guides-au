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
- 仅 **30 个职业有 ai_graph 数据**（cluster+4 分），仅 **2 个有完整 AI 文案**（532111/254422）→ 图谱/榜单/AI 板块目前只覆盖这些。

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
2. **189 获邀分采集**（按职业公布，技工 65 等）→ `occupation_invitation_scores`(visa_subclass='189')；190/491 待定时任务接入各州精确数据。
3. 定时任务：更新获邀分（占位参考值 → 真实）。
4. 可选：cluster editorial / rkMethod / About / AI 板块标题 等 UI 文案补全 10 语言（走 translate_ui 或 TM）。
5. 部署前改真实域名再 build。
6. 25 新职业 + 4 国际样本薪资为联网估算，上线前二次核对（todo#5 历史项）。
7. 矩阵可选增强：hover 卡片、按类别筛选高亮（之前定先不做复杂交互）。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-19.md 继续」。
