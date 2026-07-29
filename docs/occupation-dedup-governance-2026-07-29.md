# 职业重复治理报告（aijobrisk-go / 全站数据）

生成日期：2026-07-29 · 数据源：`aijobrisk-go/data/occupations_v2.json`

## 1. 现状量化

| 指标 | 数值 |
|---|---|
| 职业记录总数（含跨国重复） | **19,308** |
| distinct slug（全局职业主键） | **5,192** |
| 覆盖国家 | 43 |

跨国同 slug 是**设计使然**（by-country tab 靠同 slug 合并同一职业的各国页面），不算"重复"。真正的重复来自：**不同国家用各自分类体系（ANZSCO / SOC / ISCO-08 / NCO / KECO / CBO…）slug 化，语义相同的职业产生了多个 slug**，无法被 tab 合并。

## 2. 重复的三种形态（可量化）

### ① 单复数成对（最纯粹的重复）——**435 对**
同一职业的单数与复数 slug 同时存在，各自独立成页：
- `accountant` ↔ `accountants`
- `actor` ↔ `actors`
- `aerospace-engineer` ↔ `aerospace-engineers`
- `air-traffic-controller` ↔ `air-traffic-controllers`
- …（共 435 对）

### ② n.e.c. catch-all 桶——**97 个 slug**
`...-not-elsewhere-classified` / `...-nec` 这类兜底桶，语义空泛、彼此高度相似，且常与具体职业重叠。

### ③ 近义碎片（同一显著词集，不同措辞）——**613 个聚类 / 683 个可折叠冗余 slug**
把 slug 归一化（去停用词/n.e.c./单复数）后按"显著词集"聚类，613 个聚类各含 2+ 个 slug。典型：
- `human-resource-manager` / `human-resource-managers` / `human-resources-manager` / `human-resources-managers`（4 个 → 1）
- `interpreter-and-translator` / `interpreters-and-translators` / `translator-and-interpreter` / `translator-interpreter`（4 个 → 1）
- `dancer-and-choreographer` / `choreographer-and-dancer` / `dancer-choreographer` / `dancers-and-choreographers`（4 个 → 1）
- `software-developer` / `software-developers` / `application-software-developer` / `software-and-applications-developer-and-analyst` …（含 software 的 slug 共 16 个）
- 美国 SOC 把 teacher 炸成 **119** 个 slug（`*-teachers-postsecondary` 系列）

**保守估计**：仅靠机械规则（单复数 + 词序 + n.e.c. 归并），全局 5,192 slug 可收敛约 **680–900 个（约 13–17%）**，语义近义合并空间更大。

## 3. 根因

1. **无全局 canonical 职业主键**：slug 直接由各国本地职业名生成，未映射到统一概念层。
2. **slug 化不归一**：未做单复数归一、词序归一、停用词剔除。
3. **n.e.c. 兜底桶**当作独立职业建页。
4. **分类粒度不齐**：SOC（美）细到 postsecondary 学科级，ISCO 只到四位组，ANZSCO 又是另一套。

## 4. 解决方案（按投入从小到大）

### 方案 A — 轻量规则去重（低风险，1 天内）
- slug 归一：单复数归一 + 词序排序 + 去 `and/of/the`。
- 把 435 单复数对、683 近义冗余合并到"代表 slug"，其余做 301 重定向（`docs/nginx-301-*.conf` 既有先例）。
- **收益**：全局职业数掉约 13–17%，搜索/列表立刻干净。
- **代价**：合并是启发式的，需人工抽查代表名；跨国 tab 仍受限于合并质量。

### 方案 B — canonical 概念层 + 跨国映射（中等，3–5 天）
- 以 **ISCO-08 四位码**（所有国已对齐，见 `SOURCE_INFO`）为 canonical 主键，各国 slug 映射到同一 ISCO 概念。
- 职业页主键从"本地 slug"改为"ISCO 概念"，各国自动成为该概念下的 tab（跨国合并从"字符串相等"升级为"概念相等"）。
- **收益**：从根上消除跨分类碎片，by-country 覆盖大幅提升。
- **代价**：改数据管线（`export_site_data_v2.py`）与 Go 路由/主键；美国 SOC 细粒度需向上归并到 ISCO 四位。

### 方案 C — 混合（推荐路线）
1. 先上**方案 A** 清掉机械重复（快速见效、可回滚）。
2. 再逐步引入**方案 B** 的 ISCO canonical 层做跨国合并。
- n.e.c. 桶单独策略：保留但降权（不进搜索首屏 / noindex），或并入父类。

## 5. 建议下一步
先按方案 A 产出**具体合并清单**（每个聚类的代表 slug + 待重定向 slug + 涉及国家/记录数），人工过一遍再执行。本报告已定位全部 435 对 + 613 聚类，可直接导出为 CSV 供审阅。
