# 会话交接 · 2026-07-21（职业 md 双语重生成 + 职业↔行业多对多关系 + 设计探索稿）

> 接续 `docs/session-handoff-2026-07-17b.md`（多域名架构规则 + aijobrisk 主站迁移方案，待动手）。
> 本会话做了 5 件事：①职业介绍 md 双语全量重生成；②job-treemap 外部评测 audit.md；③DeepSeek 设计探索稿（配色解耦）；④**职业↔行业多对多关系验证 + 固化导出**；⑤主题配色固化 + logo + industries 设计稿。
> **全部未 commit**（用户手动提交）。

---

## 一、职业介绍 md 双语全量重生成（career-contents）

- **背景**：旧 `generate_md.py` + `pipeline/generators/md_generator.py` 读的是已废弃旧 DB 表（`occupations_i18n` 等，现 `deprecated_*`），**对 v2 库已跑不通**且中文写死。原 `career-contents/` 5715 个中文文件是过时产物。
- **新管线**：`scripts/gen_career_md.py`（不依赖 DB，直接读 `site/src/data/`）
  - 数据源：`occupations_v2.json`（英文母本 + education/salaries/ratings/ai）+ `occ-detail-v2/{cc}.json`（visa/qualifications/suitability/faqs/growth_areas/ai明细）+ `translations-v2/zh-CN.*.json`（英→中 TM，key=英文源串）。
  - 双语 `T(s,lang)`：en 返回原文；zh 查 TM 命中取中文、**未命中回退英文**（用户拍板）。章节标题/评级档位词/移民说明等骨架在脚本里写死中英两套，不走机翻。
  - 输出：`career-contents/{cc}/{slug}.md`（EN）+ `career-contents-zh/{cc}/{slug}.md`（ZH），各 **6678**；每树 1 根 README + 14 国 README（数据来源署名 + 按分类的职业索引链接）。slug 用 v2 的 `occ['slug']`；同国 slug 撞车（100 例）追加 `-{occ_code}` 消歧，两语言共用同一 slug。
- **翻译工作量**（用户已决策 = **英文兜底先出版**，平台留 **Azure** 以后补）：英文版 0 翻译；中文版各国覆盖 80–100%，**JP 仅 4%、KR 仅 5%**（几乎全英文兜底）。以后定向补翻只需把缺串补进 `translations_v2` 后重跑脚本。
- 见 memory [[career-md-bilingual]]。**旧 `generate_md.py` 建议弃用**（对 v2 失效）。

---

## 二、job-treemap 外部评测 audit.md

- 第三方对 **aijobriskmap.com** 落地页的评测，整理成 `job-treemap/audit.md`（可勾选 todolist，按严重度）：
  1. **CTA 缺失（High）**：只有 "Read more" → 换动作导向 CTA（下载报告 / 订阅周报）。
  2. **受众不明确（Medium）**：太学术 → 副标注明"为 HR/求职者/政策规划者而建"。
  3. **H1 只提问不给答案（Medium）**：加澄清从句（"探索 13 国数据集 / 6600+ 职业交互式暴露分数"）。
- 每条带评测方给的现成 Instant Fix 文案。**尚未落到实际页面**。

---

## 三、DeepSeek 设计探索稿（配色**解耦**，供横向对比决策）

- 脚本 `scripts/gen_design_deepseek.py`（DeepSeek REST，非 JSON 模式；封装 `scripts/_deepseek_rest.py` 锁死 JSON 不能用于 HTML）。
- **关键约定**（见 memory [[design-exploration-decoupled]]）：探索稿**不喂现站配色**，让模型从零自主提配色 + 页面底部输出色板 swatch，否则无法横向对比。放 `aijobrisk-design/deepseek/`。
- 已出 3 版（各自风格迥异）：
  - `compare.html`（职业对比页）— 暖色米白编辑风（赤陶红 #cc4b3c + 墨绿 + 芥末黄）
  - `bookkeeper-vs-accountant.html`（对比结果页）— 深色数据仪表盘（#0f1117 + 亮蓝 #4f8cff + 青）
  - `rankings.html`（排行榜，6 榜×Top5，每榜 `ranking-item.html` 入口）— 机构权威风（暖灰 + 深蓝 #1f4b8a）
- 数据都用真实 v2 数字（FACTS 块喂入，禁编造）。三版 + 现站冷调蓝 = 四种路线。**用户后来定了用现站蓝系**（见第五节）。

---

## 四、职业↔行业 多对多关系：验证 + 固化导出（本会话重头）

用户方向：做**多对多 occupation↔industry 关系**（**不做平均 risk**），职业可从全球行业进、也可从国家进。

### 数据源（都在 `downloads/onet-industry/`，有 README）
- **O*NET Resource Center 本身没有 occ→NAICS 下载文件**（crosswalks 只有 CIP/DOT/RAPIDS/ESCO/OOH）。
- **BLS 全国就业矩阵**：`data.bls.gov/projections/nationalMatrix?queryParams={SOC}&ioType=o`（`www.bls.gov` 被 Akamai 403，但 `data.bls.gov` 可达 200）。给 SOC×NAICS 成员关系（含就业量、占比）。
- **O*NET `ESCO_to_ONET-SOC.xlsx`**（`/crosswalks/esco/`，CC BY）：列 `ESCO/ISCO Code`（点前 4 位=ISCO 单位组）→ `O*NET-SOC`，即 **ISCO→SOC 桥**，覆盖 428/436 ISCO 组。

### 链路
```
美国职业   occ_code(SOC) ───────────────► BLS 矩阵 ──► NAICS 大类   （直连）
非美国职业 aioe_soc(ISCO) ─► ESCO桥(ISCO→SOC) ─► BLS 矩阵 ──► NAICS 大类   （桥接）
```
行业粒度 = NAICS 2 位大类（规范 20 个）；成员阈值 = 占该职业就业 ≥1%。

### 四个坑（都已修，脚本必看）
1. `aioe_soc` 字段**美国存 SOC、其余国家存 ISCO**，不能统一按 `\d{4}` 当 ISCO（否则把 SOC 后 4 位误当 ISCO，覆盖假低到 9%）。
2. BLS 表 **col4=占该职业比重**（成员关系用它），col5=占该行业比重，别混。
3. 就业量带**千位逗号**（`2,850.7`），`float()` 前必须去逗号，否则大行业行被整行丢弃（护士的 Health care 84% 曾消失）。
4. 制造(31-33)/零售(44-45)/运输(48-49)三合并大类 **BLS 无 2 位汇总行**，须由 **3 位子类(xxx000)求和**（抓取改留 `code.endswith("000")`）。

### 结果
- **覆盖度**：全局 **98.5%**（6580/6678），非美国 97–100%，美国 93.5%（直连），CH 3 职业无 ISCO=0%。
- **真·多对多**：美国平均 4.8 个行业/职业，分布 1–16。抽查正确（护士→health 84%、机加工→manufacturing 83%、零售员→retail 69%、卡车司机跨批发/运输/建筑）。

### 脚本 & 产物
- `scripts/fetch_onet_industry.py`（抓 803 US SOC，0 失败）→ `downloads/onet-industry/us_soc_industry.json`
- `scripts/analyze_industry_coverage.py`（覆盖度）→ `coverage_summary.json`
- **`scripts/build_occ_industry.py`（固化导出）**→ `site/src/data/`：
  - **`occ_industries_v2.json`**：`{occ_id: [{s:行业id, n:名, p:占该职业%}]}`，6580 职业
  - **`industries_v2.json`**：20 个规范 NAICS 大类（含各国 occ 数）
- 见 memory [[occupation-industry-relation]]。行业轴与现有 11 个"职业族 category"是**并行两根轴**，不冲突。

---

## 五、主题配色固化 + logo + industries 设计稿（用户定用现站蓝系）

- **配色固化**：`aijobrisk-design/deepseek/{job-detail,index}.html`（用户早前建，用的是现站冷调蓝系）提取 → **`aijobrisk-design/theme.css`**（CSS 变量 token，含明暗双主题）：主蓝 `#2563eb` + 藏青文字 `#0b1a2e/#1e3a5f/#2c3e5a` + 弱化 `#4b5e7a` + 蓝白面 `#f6f9fc/#eaf0f6/#f0f5fe` + 风险语义 绿`#059669`/琥珀`#f59e0b`/红`#dc2626`。**后续页面统一用它**。
- **logo**：从 `bookkeeper-vs-accountant.html` 提取（圆角方框 + "A"峰 + 圆点），改配主题蓝 `#2563eb` + 琥珀点 → **`site/public/logo.svg`**（静态资源已就位，**未接进 Base.astro 站头**）。
- **industries 设计稿**（用主题 + 真实数据，**不解耦**）：
  - `aijobrisk-design/deepseek/industries.html`：/industries 总览，20 张行业卡 + 20 个 `industry.html` 详情链接，不显示平均 risk。
  - `aijobrisk-design/deepseek/industry-detail.html`：/industry/health，职业表 + 4 个可排序列头（▲▼：职业/AI风险/薪资/从业人数），风险徽章配文字标签。
  - DeepSeek 8192 token 上限会截断复杂页 → 提示词加"CSS 紧凑/去掉色板条"后 `finish=stop` 正常。

---

## 六、⚠ 待办 / 待决

1. **industries 落地**：把 `industries.html`/`industry-detail.html` 设计稿落成真实 Astro 页面 `/industries` + `/industry/[sector]`，接 `occ_industries_v2.json` + `industries_v2.json`。非美国行业名可另做本地化；CH 3 职业与无 ISCO 职业留空。
2. **logo 接线**：`site/public/logo.svg` 已就位，未接进 `Base.astro` 站头——属品牌迁移（aijobrisk）的一部分，待做。
3. **中文 md 补翻**：JP/KR 覆盖仅 4–5%，以后用 Azure 定向补进 `translations_v2` 后重跑 `gen_career_md.py`。
4. **job-treemap audit.md** 三条改进未落到实际页面。
5. **主站迁移**（上一份交接 07-17b 的待办仍在）：aicareergraph→aijobrisk 品牌/域名机械层 + 差异化 + 301。
6. **全部未 commit**，加上游 07-17/16d 一并待用户手动提交。旧 `generate_md.py` 建议弃用。

> 恢复：读本文件 + memory [[career-md-bilingual]] [[occupation-industry-relation]] [[design-exploration-decoupled]] [[multi-domain-architecture]]。
> 关键文件：`scripts/{gen_career_md,fetch_onet_industry,analyze_industry_coverage,build_occ_industry,gen_design_deepseek}.py`、`site/src/data/{occ_industries_v2,industries_v2}.json`、`aijobrisk-design/{theme.css,deepseek/*.html}`、`site/public/logo.svg`、`downloads/onet-industry/`（含 README）。
