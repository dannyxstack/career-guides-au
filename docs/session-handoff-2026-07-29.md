# 会话交接 2026-07-29（aijobrisk-go：移民三档改造 + 国旗修复 + 锚点 + About 来源表 + 评分核查 + 去重报告）

本会话 7 项任务。任务 1 已 commit+push；任务 2–5 的 aijobrisk-go 代码改动**全部完成并浏览器验证，但未 commit**；任务 6/7 产出报告文档。

---

## 任务 1 — aijobriskmap 合并 main 并 push ✅（已 push）
- 分支 `feat/aijobriskmap-czhusg-sources`（`74f2ba4f`+`f2464494`）**快进合并**进 `main` 并 push：`10d9492d..f2464494`。
- 与 main 无重叠（分支只改 `job-treemap/` 与 `scripts/`，工作区未提交的 `aijobrisk-go/*.go`、`scripts/export_*` 等原样保留）。

---

## 任务 3 — 印度国旗渲染修复 ✅（`internal/data/dicts.go`）
- **根因**：derived `COUNTRY_FLAG.json` 里 **IN、CN、BR、MX** 四个后加国的国旗 SVG **缺 `class="flagsvg"`**；CSS `.tab .flagsvg{width:20px;height:13px}` 靠该类设尺寸，缺失→SVG 无宽高属性→计算宽度塌成 **0px**（不止印度，CN/BR/MX 同病）。
- **修法**（aijobrisk-go 范围内、最稳）：`loadDicts()` 加载 `COUNTRY_FLAG.json` 后**归一化**——凡 `<svg` 开头且不含 `flagsvg` 的，插入 `class="flagsvg"`。一次修好 4 国，且将来重导出也不怕。
- 验证：印度 tab 国旗现 `svgW=20px`、`class=flagsvg`；浏览器 CN/BR/MX 旗均正常。

## 任务 4 — by-country 链接加锚点 ✅（`templates/job.html` + `internal/web/job.go`）
- `<h2 class="by-country">` → 加 `id="region-data"`。
- 国家 tab 的 `Href` = `i18n.HrefJob(...) + "#region-data"`。切换国家后新页面直接定位到"Local data by country"板块，不再停在顶部。
- 验证：href 现为 `/jobs/{slug}/{CC}#region-data`。

---

## 任务 2 — 移民板块三档改造 ✅（核心）
用户定的**三档**（`internal/data/migration.go` 的 `migrationTier` map）：

| 档 | 行为 | 国家（共 43） |
|---|---|---|
| **full** 经典移民国 | 保留**逐职业**签证表 + PR 雷达维度 + 移民徽章 + 移民FAQ | AU NZ CA US UK **DE IE**（7） |
| **info** 工作签→永居 | 退化为**一段静态话 + 官方链接**（不随职业变）；雷达去 PR 维度；无徽章；移民FAQ过滤 | EU Blue Card 19 国(FR ES IT NL BE AT PL PT GR HU CZ RO LU SK SI HR **DK** FI SE) + EEA(NO IS CH) + 亚洲(SG JP KR)（25） |
| **none** 非移民国 | **整块移除**；雷达去 PR；无徽章；移民FAQ过滤 | CN BR MX AR CL ID MY TH VN TR **IN**（11） |

**边界决策**（用户拍板）：DE/IE 归 full（有真实逐职业数据）；NO/IS/CH 归 info；DK 单列（退出 Blue Card，用 Pay Limit/Positive List 文案）。**India 归 none**（非技术移民目的地）——待用户复核。

三处实现：
1. **移民板块**（`job.html` 按 `.MigMode` 三分支 + `job.go` switch 构建）：full=原签证表；info=`MigrationInfoOf(cc,locale)` 返回 `{Body,URL,LinkText}`（EU Blue Card 共享文案 `{C}` 插国名→EU Immigration Portal；DK/NO/IS/CH/SG/JP/KR 各自文案+官方门户）；none=不渲染。
2. **FAQ 过滤**（`job.go` 的 `isMigrationFAQ`）：非 full 档，按英文母本关键词(`migrat/immigra/visa/work permit/permanent resid/green card/...`)剔除签证移民诱导问答（原始数据里 FR 510/CN 412/JP 271 条这类 FAQ）。
3. **雷达 PR 维度**（`dicts.go` 的 `dimOrderFor/RadarLabelsFor/RadarValuesFor`）：非 full 档从 11 维去掉 `pr_friendliness`+`pr_difficulty` → 9 维。徽章由 `ShowMigBadge`(=full)门控。

**验证**（`photographer` 三国真实 slug）：AU=Migration(to Australia)+签证表+PR维度+徽章+移民FAQ；FR=Immigration pathways(to France)+EU Immigration Portal 链接+9维雷达+无徽章+无移民FAQ；CN=整块无+9维+无徽章。浏览器确认 FR 段落国名插值正确、雷达 9 辐条。

**官方链接**（我起草，上线前请复核）：EU=`immigration-portal.ec.europa.eu`；DK=nyidanmark.dk；NO=udi.no；IS=utl.is；CH=sem.admin.ch；SG=mom.gov.sg；JP=isa.go.jp；KR=immigration.go.kr。

---

## 任务 5 — About 页各国数据来源与权威性 ✅（`internal/data/sources.go` + `static_pages.go` + `templates/about.html`）
- 从 `job-treemap/build.py` 的 `SOURCE_INFO`（42 国）**移植为 Go map**（补 CH 一条），字段 `(Authority HTML, Class, Tier A/B/C, OfficialPay)`。
- About 页新增 `#data-sources` 段：A/B/C 图例 + **全 43 国来源表**（Country/Data source/Classification/Authority/Occupation pay），按层级 A→B→C 排序。层级：**25 A（国家统计局）/ 12 B（Eurostat EU-LFS，含 CH）/ 6 C（ILOSTAT）**。
- Authority 含 `&amp;` 实体，用 `template.HTML` 保留避免双转义。
- 验证：43 行渲染正确，AU=A/Official，VN=C/—。

---

## 任务 6 — 未完成评分国家核查 ✅（报告）
- 雷达 11 维里，**26 国基本只有 `ai_risk` 一维**（少数含 `income_level`），其余 9 维全缺。
- **约 11,322 条职业待补评分**（9,026 条仅 ai_risk；2,091 条 ai_risk+income）。
- 完整 17 国：AU BR CA CH DE ES FR IE IN IT JP KR MX NL NZ UK US。
- 未完整 26 国：AR AT BE CL CN CZ DK FI GR HR HU ID IS LU MY NO PL PT RO SE SG SI SK TH TR VN。
- 注：CN 虽在补录名单，其 436 条也只有 ai_risk。

## 任务 7 — 职业重复解决方案 ✅（报告 `docs/occupation-dedup-governance-2026-07-29.md`）
- 现状：19,308 记录 / 5,192 distinct slug。根因=各国用本地分类体系(ANZSCO/SOC/ISCO/NCO/KECO…)独立 slug 化，语义相同职业产生多 slug，by-country tab 只合并**完全同 slug**。
- 量化：单复数成对 **435 对**；n.e.c. catch-all **97 个**；近义聚类 **613 组 / 683 个可折叠冗余 slug**（保守收敛 13–17%）。
- 三方案：**A** 轻量规则去重(单复数/词序/n.e.c.，配 301 重定向)；**B** ISCO-08 四位 canonical 层+跨国映射(改管线)；**C** 混合(先 A 后 B，推荐)。等用户选方向再动代码。

---

## 改动文件（aijobrisk-go，**全部未 commit**）
- **新增**：`internal/data/migration.go`、`internal/data/sources.go`、`.claude/launch.json`（dev 用，PORT 需另设 4339）
- **改**：`internal/data/dicts.go`、`internal/web/job.go`、`internal/web/static_pages.go`、`templates/job.html`、`templates/about.html`
- **文档**：`docs/occupation-dedup-governance-2026-07-29.md`、本交接
- `go build ./...` + `go vet ./...` 均通过；dev server（`go run .` PORT=4339）本会话在跑。

## 待办（下次）
1. **India 归档复核**（none 是否正确）。
2. **新增英文文案翻译**：任务 2 的 25 国移民段落 + 任务 5 表头/A·B·C 分层标签 + "Immigration pathways"/"EU Immigration Portal" 等；走 DeepSeek/Azure 补 5 语言（未翻回退英文）。
3. **②档官方移民链接**上线前人工复核域名/路径。
4. **任务 6 的 11,322 条评分补跑**（数据生成，本会话未做）。
5. **任务 7 去重**：等用户选 A/B/C 方向。
6. **commit**：aijobrisk-go 本批改动 + 更早各会话未提交的 aijobrisk-go/scripts 大批工作（见 `docs/session-handoff-2026-07-28*.md`）。
7. 相关记忆 `[[aijobrisk-go-port]]`。
