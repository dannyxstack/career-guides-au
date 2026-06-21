# 会话交接 · 2026-06-21（AI 工具栈 disruptors 全量 + 加拿大 CA 全量 + 全球英文站 + 榜单全球化 + 国旗/板块标识规则）

> 接续 `docs/session-handoff-2026-06-20.md`。
> DB = 远程 MySQL `192.168.194.135:13306`，配置读 `.env`；翻译/AI 生成 `$env:LLM_PROVIDER="deepseek"`。
> 站点品牌 **AI Career Graph**，域名 `https://aicareergraph.com`。Python：`e:/run/conda_envs/career-video/python.exe`。

---

## ⚠️ 立即可续做（RESUME / 待办）

1. **`occupation_visa_pathways` 加技术移民分数字段**（用户提问，方向未定，**待决策**）：
   - 现状：分数（如「邀请制，EOI 约 65~75 分（竞争激烈）」）写在 `occupation_visa_pathways.description` 文本里。
   - **已存在专表** `occupation_invitation_scores`（`min_score`/`asof`/`note`/`source_url`，已 join 进 export、前端已显示「竞争性获邀约 X 分」）。
   - 方向 A（推荐）：复用该专表补录；方向 B：按字面在 `occupation_visa_pathways` 新增列（与专表重叠）。**等用户选 A/B 再做。**

2. **CA 英文页存在中文回退**：CA 职业只生成了 zh-CN + en 母本，但 `education/qualifications/salaries/visa.desc/ratings.label/suitability` 仅 zh 母本（只有 `summary` 和 FAQ 做了中英）。CA 的 en 页这些字段会**显示中文**。
   - 解决：跑 `collect_strings → translate_strings`（会把 CA 新增中文串翻到 9 语言，en 页即正常），或单独为 CA 这些字段生成英文。用户当时要求「先不批量翻译」，故未跑。

3. **CA 数据为 LLM 估计**：NOC 码 / 薪资(CAD) / 移民资格(EE/PNP) 上线前需二次核对。

4. **少量生成失败可补跑**（幂等）：CA disruptors 失败约 15、AI 洞察约 2；AU「起重机操作员」无 disruptor。需要时重跑对应脚本即可。

5. **本次大量改动尚未 git commit**（站点前端 + 多个新脚本 + rules.md + 记忆）。

6. （可选）全球榜单 hub 的 AI 榜**卡片预览**仍可能显示同名职业的 AU/CA 两张卡（合并只做在 `[rank]` 全量表格）。

7. （搁置）`ai-entry`/`ai-upgrade` 文案开头加职业名（SEO）——用户暂缓；方案是渲染层拼接职业名（零重译），见 06-21 对话。

---

## 本会话完成

### 1. AI 工具栈 disruptors（已替代该职业的 AI 工具/产品/研究/新闻）
- 表：`migrate_ai_disruptors.py` → `ai_disruptors`(工具目录,name 唯一,品牌名不翻译) + `occupation_ai_disruptor`(职业↔工具多对多,`replacement_level` partial/major/full,`scope_zh`)。
- 生成：`gen_ai_disruptors.py`（DeepSeek，禁编造，容错解析数组/对象，`--batch-size/--rest`，`--country`，幂等跳过已有）。
- 管线：`_i18n_fields.py` fetch 时挂 `ai.disruptors` 并采集 `summary_zh/scope_zh`；`export_site_data.py` 后处理算「也影响」跨职业 `also`。
- 前端：`data.ts` 加 `disType/disLevel`；详情页 `[category]/[slug].astro` AI 区块新增 `data-section="ai-disruptors"` 卡片列表（名称+类型+程度 chip+年份+scope+来源）。
- **「也影响」展示已移除**（数据保留在 `d.also` / DB，留给后续「AI 工具栈」功能）。
- 规模：AU 260/261、CA 153/168 有 disruptors；`ai_disruptors` ~900+ 工具去重。

### 2. 评分维度说明上关于页
- about（各国 + 全球）新增 11 维度释义区（复用 `dimLabel/dimDesc`）。

### 3. 详情页 `ai-position` 隐藏
- `[slug].astro` 的 AI 图谱位置卡 `style="display:none;..."`（DOM 保留）。

### 4. 加拿大 CA 全量（NOC）
- `gen_ca_occupations.py`：按每个 AU 职业用 DeepSeek 生成加拿大对应职业（NOC 码/中英简介/教育/资质 ECA-省牌照/CAD 薪资/EE-PNP-AIP 移民/11 维 10 分制评分/中英 FAQ/增长词），`seed_occupation_v2` 入库 + 英文 FAQ + `generate_md(code,'CA')` 出中英 md。批次 50/休 20min（阶段1），幂等状态文件 `.codex_tmp/ca_done.json`，NOC 撞码跳过。
- AI 板块：`gen_ai_insights.py --country CA` + `gen_ai_disruptors.py --country CA`。
- **规模：CA 168 职业**（含原 2）；md 在 `career-contents/ca/`。export 后 427 职业、build 4710 页。

### 5. 全球英文站
- 根 `/`：从跳转页改为**全球英文品牌入口**（`site/src/pages/index.astro`，自带 global 头/脚，不依赖 Base 国家绑定）。Hero+迷你图谱、全局搜索(427 职业，带国家标签)、国家卡片、四能力、方法论、Who、Questions、底部 CTA。
- `Base.astro` 加 `global` 模式（无国家导航，链接 `/en/...` 与 `/{cc}/en/`）；左上角 Logo 全站统一指向 `/`。
- 全球页：`/en/about/`、`/en/ai-graph/`（跨国合并矩阵，点/项带国家标签）、`/en/rankings/`（hub）、`/en/rankings/[rank]/`（全量）。
- data 助手：`graphOccsGlobal/occByClusterGlobal`、`GLOBAL_RANKING_ORDER`；`rankingList(key, undefined)` = 跨国。

### 6. 榜单全球化与交互
- 全球榜 hub：6 个 AI 榜（跨国，OccCard 带 `showCountry`）+ **Highest growth / Migration-friendly 作为同级 section，用带国旗的国家选择器**进各国榜。
- 全球 `[rank]` 全量页：**同名职业跨国合并为一行**（按 `name_en`，指标取排名最高者），Country 列多国标签**且链接到该国对应榜** `/{cc}/en/rankings/{rank}/`；**国家复选框筛选**（默认全选，实时过滤+重排名次）；「About this ranking」段并入标题区、原卡片删除。

### 7. 国旗规则（已写入 rule + 记忆）
- 全站国旗收敛为唯一来源 `data.ts` 的 `COUNTRY_FLAG`（内联 SVG，**带 `xmlns`** + `class="flagsvg"`），Base/首页/榜单页全部 import 复用。**禁用 emoji 国旗**。
- 规则写入 `rules.md`「站点前端规则 / 国旗渲染规则」+ 记忆 `flag-rendering-rule.md`。

### 8. 板块标识 data-section（已写入 rule）
- **全站所有页面**的 `<section>` 与 card 级板块都加了 `data-section="<kebab名>"`，便于按名定位修改。
- 规则写入 `rules.md`「站点前端规则 / 板块标识规则」。
- 命名参考：首页 `hero/search/countries/capabilities/methodology/who-its-for/questions/bottom-cta`；ai-graph `matrix/cluster-{key}/{key}-why...`；rankings `rank-{key}/geo-{key}/ranking-table/filter`；详情页 `ai-*/salary/education/visa/suitability-*/faq` 等。

---

## 关键运维 / 坑（持续有效）
1. DB 远程 `192.168.194.135:13306`，读 `.env`；连不上让用户启那台机。
2. 翻译/AI 生成需 `$env:LLM_PROVIDER="deepseek"`。长翻译进程**连接池会坏**（大量 "Connection error" 空转）——杀掉重启即可（新连接正常）。后台用 run_in_background。
3. 跑 `-m scripts.X` 前先 `Set-Location` 回项目根。
4. 标准重建链：（改 DB 文案后）`collect_strings → translate_strings →` `export_site_data → cd site; npm run build`。仅改前端则只 `npm run build`。
5. `export_site_data`：is_migration 用 `int()`；评分/AI 分 float。
6. PowerShell 5.1 无 `&&`；给 native exe 传多行用单引号 here-string；复杂 SQL 转义麻烦时改用 Bash 跑 Python。
7. 评分 10 分制存储、展示 ÷2（见记忆 scoring-10-point-scale）；is_migration 0/1/2（见 is-migration-enum）。

## 当前规模
- 职业 **427**（AU 257 + CA 168 + NZ 2）；AU/CA 多数有 AI 洞察 + disruptors。
- 源串 16357/语言（AU 9 语言已齐；**CA 新增中文串未 collect/translate**）。build **4710 页**。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-21.md 继续」。
