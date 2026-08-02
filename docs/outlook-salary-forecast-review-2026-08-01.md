# 职业「未来就业预估 + 薪资预期」数据核查与落地方案（2026-08-01）

## 结论速览

需求区分为**两类**数据，现状差异很大：

| 类别 | 数据库表 | 现有覆盖 | 缺口 |
|---|---|---|---|
| **A. 未来从业人数预估**（employment projection） | `occupation_outlook` + `occupation_outlook_meta` | **AU / US / CA / UK** | 其余 40+ 国 |
| **B. 未来薪资预期**（salary forecast，数字预测） | 无结构化表；仅 `occupations_text_v2.forecast_note`/`trend_summary`（LLM 文字） | **无任何国家**（含加拿大） | 全部 |

> 注：用户所说"加拿大已有的数据"实为 **A 类就业预估**（COPS 2023–2033 逐年）。加拿大并无 B 类结构化薪资数字预测。

## A. 就业人数预估

### 已入库（`scripts/load_outlook.py`）
| 国 | 源 | 覆盖率 | 时间形态 |
|---|---|---|---|
| CA | ESDC COPS | 481/551 (87%) | 逐年 2023–2033 |
| UK | Skills Imperative 2035 (NFER/IER) | 368/379 (97%) | 逐年 2021–2035 |
| AU | JSA Employment Projections | 504/531 (95%) | 3 锚点 2024/29/34 |
| US | BLS Employment Projections | 751/803 (94%) | 2 锚点 2024/34 |

### EU 一揽子：CEDEFOP Skills Forecast 2025
- **覆盖**：EU-27 + 挪威、冰岛、北马其顿、瑞士、土耳其（约 32 国），就业量预测**到 2035**。
- **粒度**：仅 ISCO **1 位 / 2 位**（职业大组）。本地为 ISCO 4 位（436 码）→ 需按 2 位父组映射（多职业共用一条曲线，类比现 AU 4 位 Unit Group）。
- **⚠️ 获取障碍（2026-08-01 实测）**：
  1. 全量数据集**注册下载表单已关闭**（"This form is closed to new submissions"）。
  2. 在线 STAS 交互工具（`?t=employment`）现被**反爬人机验证**拦截（算术验证）。自动化抓取不可行（不绕过 bot-detection）。
- **可行获取路径（需人工）**：
  - a) 真人在浏览器通过验证后，用在线工具导出 employment 视图表格；或
  - b) 邮件联系 CEDEFOP 索取全量 spreadsheet（Thessaloniki，见官网 contact；CC BY 4.0）。
  - 拿到文件放 `downloads/outlook/EU/`，写解析器（仿 `load_outlook.py` 增加 `parse_EU`，ISCO 2位→本地 4 位父组）一次性入库约 30 国。

### EU 一揽子入库结果（2026-08-01 已完成）
- 脚本 `scripts/load_outlook_eu.py`，源 `downloads/outlook/EU/skills2026-country-occupations.json`。
- **入库 25 国**（纯 ISCO08、覆盖率均 99%）：AT BE CH CZ DK EE FI GR HR HU IE IS IT LT LU LV NL NO PL PT RO SE SI SK TR。
  逐年 2015–2035；ISCO 2位组曲线（同组4位职业共用）；`is_projected`：≥2025=1。
- **排除 3 国**（本地编码非 ISCO，需 crosswalk 才能用 CEDEFOP）：**FR=ROME、DE=KldB、ES=CNO**。
- 全库 outlook 覆盖：**4 → 29 国**（含既有 AU/US/CA/UK）。

### 其他大国逐国检索结果（2026-08-01）
| 国 | 官方职业级就业预测 | 说明 |
|---|---|---|
| **TR** | ✅ 已入库 | 由 CEDEFOP 覆盖（见上）|
| **KR** | ✅ **已入库** | `scripts/load_outlook_kr.py`：KEIS 전망DB III-4(KSCO-7 세분류 2018/23/28/33) 经 KECO2018↔KSCO7 官方连接表 → 本地 KECO，**532/537 (99%)** 入库（358 세분류 + 174 중분류兜底）。见 `downloads/outlook/KR/README.md` |
| **JP** | ❌ 下载文件不可用 | JILPT sansyoku Excel 年份仅到 **2010**(2000年旧vintage)；到2040的「労働力需給の推計」仅产业+职业**大分类**、无小分类。见 `downloads/outlook/JP/README.md` |
| **NZ** | ⚠️ 仅过时 | MBIE 仅 2019 版(到2028)、宽职业组+技能级、已归档停更；无4位细分 |
| **SG** | ❌ 无 | SkillsFuture SDFE 仅定性技能需求，无职业就业数字序列 |
| **MX/BR/AR/CL** | ❌ 无 | 仅总量/短期宏观预测(OECD/央行)，CAGED/ENOE 为登记非预测 |
| **CN** | ❌ 无 | 仅劳动力总量趋势/五年规划叙述 |
| **IN** | ❌ 无 | 无官方职业级预测 |

**建议**：
- **KR / JP**：值得做，但需人工取文件(韩/日文报告或 Excel) + KSCO/JSCO→ISCO crosswalk，逐国工作量中等。
- **FR / DE / ES**：CEDEFOP 已有其数据，缺的是 ROME/KldB/CNO→ISCO08 的编码 crosswalk；建好 crosswalk 即可复用已下载的 CEDEFOP 文件入库。
- **NZ / SG / 拉美 / CN / IN**：无结构化源 → 只能走**薪资推算同款的就业量推算**（用 ILOSTAT/OECD 国家级或行业级增长回推），或不做就业预测、仅保留 LLM 文字趋势。

## B. 薪资预期（推算方案）

### 检索结论
1. **官方结构化分职业薪资预测**：确认**不存在**。BLS/OEWS 等仅发"现价薪资 + 就业量预测"。
2. **官方分职业薪资预测方法论**：不存在。官方方法论只覆盖就业量预测（[BLS EP methods](https://www.bls.gov/emp/documentation/projections-methods.htm)）。
3. **权威宏观工资增长预测（可作驱动）**：**OECD Economic Outlook / Employment Outlook** 按国家发布**实际工资增长**（compensation per employee，CPI 平减）；通胀取 IMF WEO / OECD CPI。

### 采用的推算方法（已与用户确认）
名义薪资（n 年后）：

```
salary_forecast(n) = salary_now × (1 + g)^n
g（名义工资年增速）= OECD 国家级实际工资增速 + 该国 CPI 通胀（IMF WEO）
职业微调：再按该职业 outlook 就业增长率对 g 做小幅上浮/下调（高增长上浮、萎缩下调）
```
- 全部标注 **estimate / 推算**，与实测薪资区分。
- 在 methodology 页新增该推算方法说明（引用 OECD Economic Outlook + IMF WEO 为权威输入；说明官方无分职业薪资预测，故采用宏观工资增速 + 职业需求微调的复合推算）。

## 下一步（待用户/数据到位后执行）
1. **[阻塞]** 取得 CEDEFOP 全量表 → 写 `parse_EU` → 入库约 30 国就业预估。
2. 实现薪资推算脚本（OECD 工资增速表 + IMF CPI + outlook 微调 → 写入结构化 forecast），methodology 增说明。
3. 渲染层：CA/UK 逐年折线、AU/US 锚点、EU 2 位粗线；薪资推算曲线单独标注"推算"。

## 源链接
- CEDEFOP Skills Forecast：https://www.cedefop.europa.eu/en/tools/skills-forecast
- CEDEFOP 全量数据集（表单已关）：https://www.cedefop.europa.eu/en/content/access-cedefop-skills-forecast-full-dataset
- OECD Employment Outlook 2026：https://www.oecd.org/en/publications/oecd-employment-outlook-2026_7e710f54-en.html
- OECD Average annual wages：https://www.oecd.org/en/data/indicators/average-annual-wages.html
- BLS EP methodology：https://www.bls.gov/emp/documentation/projections-methods.htm
