# 会话交接 · 2026-07-15（JP 上主站 + 各国就业前景 outlook 采集入库 + job-treemap 部署文档）

> 接续 `docs/session-handoff-2026-07-14.md`（JP 328 职业已入库、job-treemap 12 国就绪，全部待 commit）。
> 本会话完成 4 件事并**已 commit 到 main（本地，未 push）**：① JP 上主站（nav + risk map）；② 分析 5yr outlook 数据源 + 全量采集各国 outlook 到 `downloads/outlook/`；③ 把 AU/US/CA/UK 的 outlook **解析入库**（新建 2 表）；④ 给 `job-treemap/` 写单独域名部署 README。
> 环境：DB = 远程 MySQL（本会话新装 `cryptography` + `openpyxl` 到 `E:\run\Python3.13`）；长任务前设 `PYTHONIOENCODING=utf-8`。

---

## 一、JP 上主站（nav + job-risk-map）

- 承 07-14 待办①⑤：JP 数据已在库/JSON，本会话只做**前端接线**。
- 单点改动：`site/src/lib/data.ts` 的 `COUNTRIES` 数组**末尾加 `JP`**（保持既有 tab 顺序不变），并补齐 `CURRENCY(JPY)`、`COUNTRY_NAME`、`COUNTRY_FLAG`（日之丸内联 SVG，遵守禁 emoji 规则 [[flag-rendering-rule]]）、`COUNTRY_TITLE_ZH`。
- 该数组同时驱动 3 处：**头部国家切换 nav**（Base.astro）、**risk-map 地域切换 + 国别 risk-map 页 getStaticPaths**（RiskMap.astro / `[country]/[locale]/job-risk-map`）、首页国家列表 → 一改全通。
- 浏览器验证：`/JP/en/job-risk-map/` 正常渲染 **328 职业 / 99,222,400 workers**，标题「AI Job Risk Map · Japan」，无 console 错误。
- **已知小限**：`outline-paths.json` **无 JP 键**（用户选择本次跳过），故 JP risk-map 背景无日本列岛水印，但页脚文案仍写「outline of Japan」（全国共用模板，未特判）。后续若要补：`scripts/gen_country_outline.py` 的 `A3` 加 `"JPN":"JP"` + 下 NE 50m GeoJSON 重生成 → 再跑 `gen_outline_paths.py`（两个输入 geojson 不在仓库，需重新下载）。

## 二、5yr outlook 数据源分析 + 全量采集（`downloads/outlook/`，已 gitignore）

**两参考站结论**（都**不是逐年序列**，只是「基准年+预测年」少数锚点 + 一个区间增长率%）：
- `karpathy/jobs`：源 **BLS OOH/Employment Projections**；字段 `num_jobs_2024 / projected_employment_2034 / outlook_pct / outlook_desc`（2 锚点，SOC）。
- `0xtreme/aus-jobs`：源 **JSA**；字段 `outlook`(%) + `outlook_desc`（1 个区间增长率，ANZSCO4）。

**采集战果**（`downloads/outlook/{国}/` + 每国 README + 顶层 README；`downloads/` 整个已被 .gitignore，**原始数据不入库**）：

| 国 | 源 | 分类 | 时间形态 | 采集方式/坑 |
|---|---|---|---|---|
| AU | JSA Employment Projections xlsx | ANZSCO4 | **3锚点** 2024/29/34 + 5/10yr 变化率 | curl 直下；职业级在 `Table_6`(358 个4位组) |
| US | BLS `occupation.xlsx`(Table 1.2) | SOC | **2锚点** 2024/34 | **Akamai 反爬 curl/WebFetch 全 403** → 用**真实浏览器**页内 `fetch()`+base64 落盘 |
| CA | ESDC COPS csv×2 | NOC2021 5位 | **逐年 2023–2033** | open.canada.ca WAF → curl **必带 Referer 头**；文件是 **latin-1** 编码 |
| UK | Skills Imperative 2035 csv(+官方 zip 含 data-guidance) | SOC2020 4位 | **逐年 2021–2035** | EES 开放数据 CSV 直链可 curl |
| NZ | MBIE PDF | 宽职业组~97 | 到2028 | 2019发布**已过时**、仅 PDF；浏览器 fetch 落盘 |
| DE/FR/ES/IT/NL/IE | **CEDEFOP Skills Forecast 2025** | ISCO2（粗） | 到2035 | **需填表注册才给下载链**，无直链/无公开 API → 未下载，README 记录步骤 + 各国更细本国源(FR《Métiers en 2030》/IT Excelsior/NL ROA/DE QuBe) |
| JP | 无职业级预测 | — | — | JILPT 仅产业级到2040 → README 记录，建议不渲染 |

## 三、outlook 解析入库（`scripts/load_outlook.py`，已 commit）

- 新建 2 表（结构统一、各国差异由**数据内容**体现，不改表结构）：
  - `occupation_outlook`（逐年序列，画图用）：`country, occ_code, occ_code_type, year, employment(人), is_projected, source, source_code`
  - `occupation_outlook_meta`（头条+出处）：`... base_year, end_year, growth_pct, growth_desc, note`
- 单位统一归一到**人**（AU/US 源千人 ×1000；CA/UK 已是人）；`occ_code` 对齐本地 `occupations_v2.json`。
- **对齐规则**：AU 本地 ANZSCO6 位 → 取前 4 位映射 JSA 4 位 Unit Group（多个本地职业共享一条曲线，`source_code` 记4位组）；US=SOC 精确；CA=NOC5 精确；UK=职业名前4位 SOC 精确。
- `is_projected`：AU 2024 / US 2024 / CA 2023 / UK ≤2023 = 实测(0)，其余预测(1)（UK 分界为近似，note 已标）。
- **入库结果**：series **13,825** 行 + meta **2,104** 行。覆盖 AU 504/531(95%)、US 751/803(94%)、CA 481/551(87%)、UK 368/379(97%)；未匹配多为**合成岗位码**(能源/半导体11岗) + CA NOC 粒度差异。
- 抽验正确：US 首席执行官 309,400→322,700(+4.3%)、CA 软件工程师逐年 113,100→140,600(+24.3%)、UK 程序员 2021–2035(+12.4%)，与官方吻合。
- 坑：pymysql 连库 caching_sha2_password 需 `cryptography` 包（已装）；`openpyxl` 也已装。

## 四、job-treemap 单独域名部署文档

- 写 `job-treemap/README.md`：目录作用 / 数据来源(读主站 occupations_v2.json + 字段映射表) / 构建(`build.py` 无三方依赖) / 部署(纯静态、相对路径可任意域名、Nginx+rsync 示例、整站 vs 单国两形态)。
- 用户对 README 顶部手工补了第三个复刻来源链接 `madeye.github.io/jobs`。
- **本会话把 `job-treemap/dist/` 与 `dist.zip` 加进 .gitignore**（build.py 可重建的 9MB 产物，不入库），只提交源码。注意：`dist.zip`(06:40) 比 `dist/`(11:47) 旧，如需分发请先 `python job-treemap/build.py` 重建再打包。

## 五、本会话 commit（main 本地，未 push）

```
2ab85caf docs(rules): add project execution rules (conda env, deprecated_ tables, lang)
04c09881 chore(docs): add dist deploy scripts and prior session handoffs
056728f5 feat(outlook): parse & load AU/US/CA/UK employment outlook into DB
1da21b59 feat(job-treemap): standalone multi-country AI-exposure treemap site
9c74ceb4 feat(jp): add Japan (JSCO) occupations and enable JP in nav & risk map
```
（本交接文档另起一 commit。`downloads/` 与 `job-treemap/dist*` 均 gitignore 未入库。）

## 待办 / 下一步

1. **outlook 上前端（未做）**：① 把 `occupation_outlook*` 随 `export_site_data_v2` 导出成前端 JSON（或按国懒加载）；② 职业详情页**按国渲染**：CA/UK 逐年折线（实测段+预测段分色）、AU 3点、US 2点(可 CAGR 插值补逐年、`is_projected` 区分)、NZ/JP/EU6 无库内数据 → 不渲染或仅定性文案。
2. **EU6 outlook 补采（可选）**：CEDEFOP 填表下载（ISCO2/到2035）或接各国更细本国源；补采后 `load_outlook.py` 加对应 parser（注意 ISCO2→本地 ISCO4 的组级共享）。
3. **JP risk-map 轮廓（可选）**：补 `outline-paths.json` 的 JP（见一节末），否则页脚「outline of Japan」文案与实渲不符。
4. **主站上线 JP（承 07-14 待办⑤，仍未做）**：主站 Astro 未 build/部署；JP 上线需 `npm --prefix site run build` + 部署（线上 dist 仍未重建）。
5. **push**：本会话 6 个 commit 仍在本地 main（auto 模式历来拦 push 主分支）。
6. **job-treemap dist.zip 对齐**：如要用 zip 分发，先重建再打包。

## 关键坑（本会话）

1. **US BLS(Akamai)/CA(WAF)/NZ(MBIE) 直连受阻**：BLS/NZ 用真实浏览器页内 `fetch()`+base64（>token 限时结果落到 tool-results 文件，再 Python 解码；须剔除末尾「(captured at origin…)」再 base64 解）；CA 加 `Referer` 头即过。
2. **CEDEFOP 无直链**（必须填表），且粒度仅 ISCO2 → 对本地 ISCO4 偏粗，只能组级共享曲线。
3. **多数国 outlook 只有 2–3 锚点**，逐年折线要么用 CA/UK 的真逐年、要么对 AU/US 做 CAGR 插值并标注「推算」。
4. `downloads/` 早已在 .gitignore（07-12 为薪资原始数据设），故 outlook 原始数据天然不入库；本会话又加 `job-treemap/dist*`。
5. CA COPS csv 是 **latin-1**（法语重音），非 utf-8。

---

## 补记（同日续作：outlook 上 job-treemap + exposure 直方图修复）

> 本段两件事，**均未 commit**（`job-treemap/build.py`、`job-treemap/template.html` 改动；`dist/**` 已重建但 gitignore）。

### A. 把 outlook 数据接到 job-treemap
- `build.py` 新增 `load_outlook_map()`：从 DB 读 `occupation_outlook_meta` + `occupation_outlook`，按 `(country, occ_code)` 建 `{g:增减率, b/e:基准/终止年, desc, src, s:[[年,人数,预测标记]]}`；merge 进每条 record 的 `outlook` 字段。DB 不可用时告警并跳过（不阻断构建）。
  - 坑：build.py 作为脚本运行时 sys.path 不含仓库根 → `from db.connection import` 报 `No module named 'db'`；已在顶部 `sys.path.insert(0, REPO)` 修复。
- `template.html`：tooltip(`.tt-outlook`) 与 detail panel(`.dp-outlook`) 新增 outlook 块 = 「Employment outlook +X% (基准→终止)」标题 + **内联 SVG 迷你折线**（`outlookHTML()`；实测=实线、预测=虚线、首尾圆点；按增减染绿/红/灰）。
- 覆盖率（重建后 data.json）：**AU 504 / US 751 / CA 481 / UK 368**；系列点数 AU=3、US=2、CA=11、UK=15；JP 等无 outlook 正确不渲染。浏览器 JS 验证 CA「Landscaping…」= +18.8%(2023→2033)+11点折线；**canvas 常驻重绘导致 screenshot 超时**，改用 `javascript_tool` 读 DOM 验证。

### B. "Jobs by exposure" 4/6/8 三根假山 → 诊断 + 修复
- **根因（两层）**：① 生 `automation_exposure` 多为 **.5 刻度且挤在 3.5–8.5**（低 1–3、高 9–10 几乎为空，平均回归）；② `build.py` 原 `int(round())` 是 **Python 银行家舍入(偶数)**，把 {3.5,4.5}→4、{5.5,6.5}→6、{7.5,8.5}→8 折叠 → 只在 4/6/8 起山、奇数(5,7)近空。参照站(aus-jobs/karpathy) exposure 在 1–10 平滑分散（甚至低端更重）。
- **修复（用户选「即效1行」）**：`build.py` 改 **round-half-up** `int(math.floor(x+0.5))`。
  - AU 分布：修前 `{4:165,5:16,6:257,7:5,8:82,9:1}` → 修后 `{3:4,4:50,5:131,6:140,7:122,8:49,9:34,10:1}`；US 同样是正。三根假山消除、3–10 单峰分散。加权(按 jobs)版同理受益。
- **仍存**：中央寄（峰在 5–7、1–3 薄）是**数据本身粗糙**所致，非 bug。要达到参照站的分散度需**再评分/用 `aioe_pct` 较正**（选项3，本次保留）。

### 补充待办
7. **job-treemap 未 commit**：`build.py`(outlook+舍入) + `template.html`(outlook 折线)；如需分发先 `python job-treemap/build.py` 重建 dist 再打包。
8. **exposure 数据较正（选项3，可选）**：`automation_exposure` 粗糙(.5刻度/中央寄)，若要分布贴近参照站需整数0–10两极锚点重评分或按 aioe_pct 较正；影响 treemap 颜色 + 直方图 + 加权均值。

> 恢复：读本文件 + memory [[japan-collection]] [[job-treemap-clone]] [[salary-median-mean]]。outlook 采集在 `downloads/outlook/`(gitignore)，入库脚本 `scripts/load_outlook.py`，DB 新表 `occupation_outlook` / `occupation_outlook_meta`（AU/US/CA/UK 已载）；job-treemap 已接 outlook 折线 + 修 exposure 舍入（build.py/template.html 未 commit，dist 已重建）。
