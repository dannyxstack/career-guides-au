# 会话交接 · 2026-07-14（多国 AI 暴露 treemap 复刻站 + 日本 JSCO 全量采集）

> 接续 `docs/session-handoff-2026-07-13c.md`（v1 全退役 + 英文页中文残留修复）。
> 本会话两件事：① 复刻外部项目 [0xtreme/aus-jobs](https://github.com/0xtreme/aus-jobs) 做**多国 treemap 站**（新目录 `job-treemap/`）；② **采集日本(JP)全量 328 职业**（方案 A：日文撰写→英文规范存储，走现有 v2 管线）。
> **分支 `main`**，本会话改动**全部未 commit**（工作区）。DB = 远程 MySQL；Python = `E:\run\Python3.13\python.exe`（长任务前设 `PYTHONIOENCODING=utf-8`）。

---

## 一、多国 AI 暴露 treemap 复刻站（`job-treemap/`）

**来源**：外部项目是**自包含 `site/index.html`（内联 CSS/JS 的 canvas squarified treemap）+ `data.json`（职业数组）**，面积=就业人数、颜色=AI 暴露 0–10。用官方 JSA/ABS 数据给 358 个 ANZSCO 4 位职业打分。

**结论**：我方 `occupations_v2.json` 字段完全够喂这套模板，关键 AI 暴露分 = `ai.automation_exposure`。

**产物**（用户选「两者都要 + 全部国家」）：
- `job-treemap/template.html` — 唯一共享模板（改编自原仓库；参数化标题/货币符号/数据源；`__CONFIG__` 占位符构建期注入 JSON）。相比原版：删「按学历分布」侧栏图（各国 education 是自由文本无法套 AU 固定分桶）、货币符号按国切、加 AIOE 百分位行、outlook 无数值留空。
- `job-treemap/build.py` — 读 `site/src/data/occupations_v2.json` + `categories_v2.json`，输出到 `dist/`。字段映射：name_en→title、workforce_size→jobs、avg_salary→pay、**ai.automation_exposure 四舍五入取整→exposure**（直方图需整数桶）、ai.verdict_zh→rationale、ai.aioe_pct→百分位、occ_code→code、category→11 统一大类 slug。
- `dist/{cc}/index.html + data.json` — 每国一个可独立部署的单国站；`dist/data/{cc}.json` + `dist/index.html` — 带国家下拉切换器的总览页。
- 覆盖 **12 国**：AU/US/UK/CA/NZ/**JP**/DE/FR/ES/IT/NL/IE（CH 仅 3 条占位跳过）。浏览器验证：DE 切换（EUR/653 条/€854B/Destatis）、US 独立站（803/USD）、JP（328/¥）均正常。
- 重建：`python job-treemap/build.py`；本地预览：`cd job-treemap/dist && python -m http.server`（fetch 需 http 非 file://）。

**已知小限**：各国薪资分档沿用原版 AUD 阈值只换符号（EUR/GBP/JPY 名义值不同，偏保守但不影响主体）；JP 无「average」薪资档→avg_salary=None→JP pay 档空（面积靠 workforce、色靠 exposure 不受影响）。

---

## 二、日本(JP)JSCO 全量采集（方案 A：日撰英存）

**用户三条要求**：① 全量跑；② 不新增大分类，日本自有分类(JSCO)本地留一份并在数据上标记，但数据仍走我们现有 11 大类；③ 只保留英文和日文。

**架构决策（方案 A）**：v2 全站是**英文母本硬绑定**（TM 键=sha1(英文)、slug 由英文名生成、导出 master="en"），真·日文母本需重构且倒退回刚退役的混合母本复杂度。故用户拍板走**日撰英存**：DeepSeek 以日本労働市場・在留資格専門家视角、JSCO、日元生成**全日文** → DeepSeek **日译英**作规范母本入库 → **原生日文按叶子对齐**直接挂 `translations_v2` 的 ja（避免英→日二次机翻，保最高保真）。

**新脚本 `scripts/gen_jp_v2.py`（go-forward）**，每职业：
1. 生成全日文 JSON（category 从 11 英文大类枚举选、数值/代码语言中性、内含 AI 暴露块）。
2. `collect_leaves`/`apply_leaves` 定长叶子按序对齐；`translate_ja_to_en` 分块 25 + 逐条回退防长度漂移 → 英文经 `seed_occupation_en` 写 `occupations` + `*_v2`（`occ_code_type=JSCO`, `currency=JPY`）。
3. `inject_ja` 把原生日文挂 ja（含派生 training 摘要）。
- CLI：`--codes/--offset/--limit/--no-resume`，**默认 resume**（跳过已入库 occ_code），中断可无缝续。

**JSCO 全量码表**：`.codex_tmp/jsco_universe.json` = 总务省「日本標準職業分類(平成21)」页 `kou_h21.htm`（shift_jis，curl 原始 HTML → Python 真 Unicode 正则解析 `大分類X−` / `NNN　名`）解析出 **328 小分類**（排除大分類 L「分類不能」；官方 329 含 L）。字段 `{jsco,title_ja,major,major_name}`。

**结果**：
- **JP 328 条 = JSCO 小分類全集入库，0 失败**。（试跑用的 10 条假码已删净；两轮跑：首轮成 125，DeepSeek 中途 API 中断 503/DNS 致 202 失败，修 bug 后续跑补齐 202/0 失败。）
- **category 全部落我们 11 类，0 越界**（严格遵守「不新增分类」）；AI 暴露 **328/328 覆盖**（1.5–8.5）。
- **只有英日**（JP 仅注入 ja，从未跑 translate_v2 其它语言）。
- `export_site_data_v2` 出 **6141 职业**（detail×13，仍 11 类）；treemap 重建 JP=328（总就业 99.2M、加权暴露 5.3，浏览器验证 328 方块渲染正常）。

**采集途中修的 3 个真 bug（gen_jp_v2）**：
1. `salary_max`/`cost_*` 列 `decimal(10,2)` 上限≈1 亿日元，日元高薪岗（会社役員/职业运动员）溢出 → `to_seed` 加 `_clamp` 到 99999999。
2. 模型偶把 education/qualifications/salaries/visa/faqs 元素返成字符串、或 ratings[dim] 非 [label,score] 二元 → 崩在 apply_leaves；validate 增结构校验（列表元素须 dict、ratings 须二元）。
3. 每条加**一次重试**（sleep 2）吸收瞬时 503/JSON 控制字符抖动。

---

## 待办 / 下一步
1. **commit**：本会话全部未提交（`job-treemap/` 新目录、`scripts/gen_jp_v2.py` 新脚本、`site/src/data/*` 重新导出、job-treemap build.py 加 JP、`.codex_tmp/jsco_universe.json`）。另仍有上会话遗留 4 个未跟踪文件（`docs/deploy-dist-over-ssh.md`、`scripts/deploy_dist.{ps1,sh}`、前一份 handoff）。
2. **JP workforce 精度（可选）**：`workforce_size` 是 LLM 逐职业估算，求和 99.2M > 日本实际劳动力 ~69M（各国同此局限，相对 treemap 不影响）。若要精确可接 e-Stat 労働力調査官方就业数。
3. **JP 官方薪资层（可选）**：现薪资是 LLM 估算档，无「average」档故 avg_salary 空。若要 treemap 显示 pay 档 + 精确薪资，可接厚労省 賃金センサス。
4. **category 校正（可选）**：个别 JP 职业归类可商榷（试跑期见保育士曾被归 Healthcare 而非 Education），可后校正。
5. **主站上线 JP（未做）**：本会话只重建了 `job-treemap/`，主站（Astro）未 build/部署；JP 若要上主站需 `npm --prefix site run build` + 部署（承 07-13c 待办①线上 dist 仍未重建）。
6. **treemap 货币分档（可选）**：按币种调整薪资分档阈值（现沿用 AUD 阈值换符号）。

## 关键坑（本会话）
1. 外网可 curl（`gh` 不存在但 curl 通）；日本 gov 站是 **shift_jis**，解析须指定编码 + Python 真 Unicode 正则（`[一-鿿]` 在 Git Bash 按字节误报）。
2. WebFetch 会摘要/截断，**329 行码表不可靠**→ 改 curl 原始 HTML 本地解析。
3. DeepSeek 大批调用会中途 API 中断（503/DNS），**断点续跑（resume by occ_code）是刚需**；每条重试 + 分块翻译逐条回退防长度漂移。
4. `occupation_ai_v2.verdict_type` 是 `enum('compressed','amplified','mixed')`（非 mixed/augment/replace/safe），to_seed 里 VT 映射兜底。
5. JSCO 无 AIOE 交叉映射 → automation_exposure 由日文生成直接给（`aioe_method='llm_jp'`，aioe_* 留空），treemap 上色够用。
6. 试跑用的临时 JSCO 码是我编的（看護師 159≠真实 133），全量前必须删净假码行再按真实码跑。

## 本会话改动/新增文件
- 新增：`job-treemap/{template.html,build.py,dist/**}`、`scripts/gen_jp_v2.py`、`.codex_tmp/jsco_universe.json`、本文件。
- 改：`site/src/data/**`（export 重新生成，+328 JP）、`job-treemap/build.py`（加 JP 到 COUNTRY_META/ORDER）。
- DB：`occupations` + 各 `*_v2` 表新增 328 JP 行；`translations_v2` 新增 JP 的 ja 串 + `translation_src_v2` 对应英文源串。

> 恢复：读本文件 + memory [[japan-collection]] [[job-treemap-clone]] [[english-master-v2-pipeline]]。日本 328 职业已入库（英日双语、11 大类、0 越界），treemap 12 国就绪，全部待 commit。
