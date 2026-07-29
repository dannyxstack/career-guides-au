# 会话交接 2026-07-28

本会话完成：①aijobriskmap 国家字母序+SVG 旗帜下拉（commit `d42eb30`）；②**北欧 5 国全入库**并加入 aijobriskmap + aijobrisk-go；③**新 20 国全入库**并加入 aijobriskmap + aijobrisk-go；④**aijobrisk-go 5 语言翻译字符量评估**。相关记忆见 `[[nordic-collection]]`、`[[eu-asia-batch-collection]]`。

**当前站点国家数：aijobriskmap（job-treemap）= 42 国；aijobrisk-go = 43 国（含旧 CH 数据）。全部改动未 commit。**

---

## 一、aijobriskmap：字母序 + SVG 国旗下拉（✅ commit `d42eb30`，未 push）

- 所有国家列表来自 `job-treemap/build.py` 的 `present`，改 `sorted(key=COUNTRY_META[c][0])` → 首页/下拉/footer/embed/sitemap/CSV 全字母序。
- 原生 `<select>` 改自定义下拉（`template.html` 的 `.cty-dd`）以渲染 SVG 国旗（规则禁 emoji）。

---

## 二、北欧 5 国（NO/SE/FI/DK/IS）✅ 全入库 + 两站

- **官方数据层**（零 LLM）：`build_{no,fi,dk,se,is}_official.py` → `downloads/{cc}/{cc}_by_isco.json`。
- **生成**：通用 `gen_nordic_official.py --country XX`（官方薪资/就业直取 + 规则评分 + DeepSeek 英文文案 + name_local 灌 native_locale TM）。DeepSeek 后台已跑完：**NO 434 / SE 433 / FI 435 / DK 434 / IS 430** 入库。
- copy_ai_blocks_by_code --from IT（5 国）已补。
- native_locale：NO=nb / SE=sv / FI=fi / DK=da / IS=is。

---

## 三、新 20 国（欧 12+TR+南美 2+亚 6）✅ 全入库 + 两站

国家：BE/AT/PL/PT/GR/HU/CZ/RO/LU/SK/SI/HR/TR + AR/CL/MY/ID/TH/VN/SG，各 436 入库。

**数字全部官方、零 LLM**（薪资留空——Eurostat/ILOSTAT 均无四位职业薪资，不编造）：
- **13 EU/TR**：`build_eurostat_official.py`（LFS 大类就业按跨国份额拆四位）→ workforce。
- **7 非 EU**（AR/CL/MY/ID/TH/VN/SG）：新 **`build_ilostat_official.py`** 读 `downloads/{cc}/ilostat_annual_all_labour.rds`。
  - **坑**：pyreadr 对这些 .rds **segfault** → 改用 `rdata` 包 + 自定义 factor 构造器绕过 "Categorical categories cannot be null"（低层 R 属性 tag=SYM→CHAR→bytes）。
  - ILOSTAT 只到 ISCO 1 位大类 → 拆四位（同 Eurostat）。选源：max-TOTAL×1.5 上限剔膨胀源 → 单年大类和峰值最大 source → 剔残缺年取最新。得 AR2025/CL2024/ID2023/VN2024/SG2025（MY2012/TH2013 较旧但官方）。
- **入库**：通用 `seed_treemap_country.py`（workforce + ISCO 英文名 + category 借 IT + ai_risk=aioe_pct/10；薪资/文案空）。copy_ai_blocks_by_code --from IT 补 AI 暴露块。

**本地名**（规则：文档有目标国语言才录、无则跳过，不用 LLM）：
- **CZ**：434 条捷克语职业名（czso xlsx kód/název）→ TM locale `cs`。
- **SI**：用 SURS 官方四位就业（414 条）覆盖 workforce（英文名，无 sl 名）。
- 其余 EU + 全部非 EU 文档职业名均为英文 → 跳过本地名，前端回退英文。

---

## 四、前端两站接入

### job-treemap（aijobriskmap）✅
- `build.py` 加 25 国（北欧 5 + 批次 20）COUNTRY_META/SLUG/FLAG（25 国旗 SVG，scratchpad/gen_flags.py 构造 + XML 自检，patch_build.py 程序化插入）+ ORDER + 计数 17→**42**（含此前北欧 22）。
- 全 42 国重建 + `shoot_maps.mjs`（SLUGS 加 25）补 25 张静态图 + 接 og:image。
- 浏览器验证：首页 42 国字母序、全 SVG 国旗、下拉 42 项、捷克页 treemap 无报错。

### aijobrisk-go ✅
- **关键**：`data/derived/*.json` 比 `aijobrisk/src/lib/data.ts` **更新**（BR/CN/IN/MX 直接写进 derived，data.ts 只到 KR）→ **直接改 derived JSON**（走 extract_dicts.mjs 会回退丢 4 国）。`scratchpad/patch_go_derived.py` 灌 25 国（中文名 + flagsvg 国旗 + 双语 SOURCES_BODY）。
- `internal/data/data.go`（COUNTRIES/CURRENCY）、`dicts.go`（currencySym）各 +25。
- 复制 `site/src/data` 的 occupations_v2 / occ-detail-v2 / translations-v2 / categories → `aijobrisk-go/data`（43 国、19308 职业）。
- **坑**：`go build ./...` 不产 exe，必须 `go build -o aijobrisk.exe .`；rankings/job-risk-map 按 `data.COUNTRIES` 校验（旧 exe 仍 17 国→新国 404），jobs/industries 按数据存在。
- **URL**：en 无前缀；国家页 `/rankings/{CC大写}`、`/job-risk-map/{CC}`、`/jobs/{slug}/{CC}`；中文前缀 **zh-Hans**（内容 locale 才是 zh-CN）。
- 验证：25 国 × 6 页型 × 5 语言（en/es/fr/pt/ja/zh-Hans）**全 200**；国名本地化、地图 38 国旗、捷克数据源正常、无回归。

---

## 五、aijobrisk-go 5 语言翻译字符量评估（`count_go_translation.py`，NEW25 子集）

| 范围 | 源串 | 字符 |
|---|---|---|
| 新增 25 国 | 57,913 条 | 8.02M |
| 每语言待翻（es/pt/fr/ja/zh-hans 各） | ~47,000 条 | ~7.0M |
| **5 语言合计待翻** | | **≈35M 字符** |

- 全站 43 国：源串 333,575 条 / 36.3M 字符；5 语言各完成度 74–77%。
- **关键**：8M 字符几乎全来自**北欧 5 国**（有完整 DeepSeek 英文文案）；批次 20 是 treemap 层、无 DeepSeek 文案、英文串多与 IT 共享 → 已译，增量极小（新国子集"已译 18.6%"即职业名 + 共享 AI 块）。

---

## 文件清单（本会话）

**新增 scripts**：`build_{no,fi,dk,se,is}_official.py`、`gen_nordic_official.py`、`build_eurostat_official.py`、`build_ilostat_official.py`、`seed_treemap_country.py`
**修改 scripts**：`gen_intl_v2.py`（北欧 5 国配置）、`export_site_data_v2.py`（avg_salary 加 median 回退 `pick_avg_salary`）、`shoot_maps.mjs`（SLUGS +25）、`count_go_translation.py`（NEW25 + 43 国文案）
**修改 job-treemap**：`build.py`（+25 国 META/SLUG/FLAG/ORDER，计数 42）
**修改 aijobrisk-go**：`internal/data/data.go`、`internal/data/dicts.go`、`data/derived/{COUNTRY_NAME,COUNTRY_FLAG,SOURCES_BODY}.json`、`data/{occupations_v2,categories_v2}.json`、`data/occ-detail-v2/*`、`data/translations-v2/*`、重编 `aijobrisk.exe`
**下载产物**（gitignore）：25 国 `{cc}_by_isco.json`、`is/isco88_to_isco08.xlsx`、各国 ilostat/eurostat 源
**新增依赖**：`pyreadr`（未用成）、`rdata`（读 .rds）

## DB / commit 状态
- **DB**：43 国全部入库（22 原 + 北欧 5 + 批次 20，另旧 CH 3 条）。
- **未 commit**：除 `d42eb30`（已提交未 push）外，本会话全部改动均未 commit。

## 待办（下次）
1. **commit**：本会话所有脚本 + 两站改动。
2. **可选升级**：CZ/HU/SG 有官方四位薪资 → 走完整管线（DeepSeek 文案 + 薪资）替换其 treemap 层。
3. MY 2012 / TH 2013 workforce 年份较旧（其余 2023–2025），可日后补更近数据。
4. 若要真翻 5 语言 35M 字符 → 走现有 DeepSeek/Azure 管线（批次 20 因共享省了绝大部分，主要翻北欧）。
5. 部署：aijobriskmap dist 与 aijobrisk-go 二进制/数据的上线（用户操作）。
