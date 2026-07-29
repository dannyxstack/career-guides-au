# 会话交接 2026-07-28b（aijobriskmap：CZ/HU/SG 完整管线 + 数据来源权威性 + 首页长文修正）

本会话聚焦 **aijobriskmap（job-treemap）** 两块工作，全部完成并已 commit（分支 `feat/aijobriskmap-czhusg-sources`，两 commit `74f2ba4f`+`f2464494`，**未 push**）。

---

## 一、CZ/HU/SG 升级到完整管线（官方薪资 + DeepSeek 文案）✅ commit `74f2ba4f`

此前三国只走 `seed_treemap_country`（仅 workforce + ISCO 英文名，薪资空）。本会话补齐官方四位薪资并跑完整管线（同北欧）。

### 官方薪资解析（零 LLM，零编造）——新脚本
- `scripts/build_cz_salary.py`：ČSÚ/ISPV 2025 私营(MZS-M8r)+公共(PLS-M8r) xlsx。col0=四/五位 CZ-ISCO，col1=人数(千)，col2=medián，col7=průměr。仅取四位、两部门按人数加权、×12 年化。**348/436**。
- `scripts/build_hu_salary.py`：KSH `20.8.1.10.` xlsx，col0=HSCO'08 四位，col26="2023 Total"（最新年、全年龄），`…`=保密跳过，×12。**185/436**（HSCO 四位与 ISCO 不全对齐属正常）。
- `scripts/build_sg_salary.py`：MOM OWS 2025 Table 4(All Industries)，col1=SSOC-2024 五位、col4=Median($) 月度 basic wage。**SSOC 前四位=ISCO 四位组**（用户定：截前四位聚合），同 ISCO 下多 SSOC 取中位数、×12。**194/436**。
- 三脚本都是 load 现有 `downloads/{cc}/{cc}_by_isco.json` → 补 `avg_salary/salary_mean/salary_note` → 写回（保留 workforce/name_local）。数值量级已核对合理（CZ 中位 ~56 万 CZK/年、HU ~660 万 HUF、SG ~5.1 万 SGD）。

### 配置与管线
- `scripts/gen_intl_v2.py`：`COUNTRY` 加 CZ/HU/SG（name/currency/native_locale/native_lang/official/visa）。**SG native_locale=None**（英文工作语言，不灌本地名）。
- `scripts/gen_nordic_official.py`：`NORDIC` 集合扩为北欧5国 + CZ/HU/SG；注入本地名时**优先取官方 by_isco 的 name_local**（保留 CZ 官方捷克名，不被 LLM 覆盖）。

### DeepSeek 文案跑批（关键坑：速度）
- v4-flash 是**推理模型，21 秒/次**；1308 次串行 = **7.6 小时**，不可接受。
- 解决：把 436 码切 4 片，三国共 **12 路并发后台进程**（I/O 密集、等 API），实际 **~40 分钟**跑完。6 条偶发失败（缺字段）已补跑归零。
- **AI 暴露块（aioe_pct，决定 treemap 颜色）跨重 seed 保留**：`seed_occupation_en` 的 occ_id 稳定(upsert)，且**没有** `DELETE occupation_ai_v2` → 无需重跑 copy_ai_blocks。
- DB 结果：CZ/HU/SG 各 436 职业、summary 436/436、salary 按覆盖、aioe 427/436（9 缺为军职等全局正常）。

---

## 二、各国数据来源与权威性描述 ✅ commit `f2464494`（`job-treemap/build.py`）

用户要求：说明已收集多少国、各国数据来源与权威性，且**各国描述不同**（此前 Eurostat/ILOSTAT 国的 source 行千篇一律）。

- 新建**单一来源** `SOURCE_INFO`（42 国 tuple：`(权威机构HTML, 分类, 层级A/B/C, 是否官方薪资)`）。**批次国也点名各自本国统计局**（BE=Statbel、PL=GUS、AR=INDEC…），使描述真正各异。
- 三层权威度：**A** 国家统计局官方（自采/登记/普查，含官方薪资）；**B** 经 Eurostat EU-LFS（就业官方、四位由大类份额建模、无四位薪资）；**C** 经 ILOSTAT(UN ILO)。当前 **25 A / 11 B / 6 C**。
- 三处渲染（helper：`sidebar_source_html` / `source_paragraph` / `methodology_sources_section`）：
  1. 国家页**侧栏**来源行（由 SOURCE_INFO 生成，替代旧 `COUNTRY_META[cc][3]`）。
  2. 国家页**正文**新增 "Data sources & authority for {国}" 段（含 FR/JP/KR 的 LLM 映射诚实说明）。
  3. **methodology 页**：替换过时 3 行覆盖表 → **全 42 国来源权威总表**（Country/Authority/Classification/Employment basis/Occupation pay）。
- 修正残留 `17 countries` → 42（About 页 desc + Dataset JSON-LD）。
- **命名坑**：新注册表最初叫 `SRC`，与 build.py 顶部已有 `SRC=occupations_v2.json 路径`冲突 → 改名 `SOURCE_INFO`。

---

## 三、首页长文：行业问题 + 42 国数字修正 ✅ commit `f2464494`

- `scripts/build_treemap_longform.py` 的 compare 段：标题 `Which countries and industries are most exposed` → **`Which industries are most exposed`**，指令改为**聚焦行业**（不排名国家）。
- 旧 `longform.json` 通篇 13 国旧数（6,675 职业、Germany 5.8 最高、half a billion workers…），42 国下**全是错的**。用户定：**三段全重生**。
- 用 `build_treemap_longform --force` 基于真实 42 国数据重生（`build_facts()` 喂真数、禁编造）。新数：42 国、19,000+ 职业、全球均值 4.8、行业 8.1(Business/Finance/Legal)→1.9(Trades)、国家 Iceland 6.1→India 3.9。
- 全仓扫描：**"13 countries" 类描述 0 处残留**。

---

## 导出 / 重建 / 验证
- `export_site_data_v2`（19308 职业·43 国）→ `job-treemap/build.py` 重建 42 国。
- CZ/HU/SG 现显示薪资（如 `Kč486,492`）；BE/TH 等 B/C 层仍正确无薪资。
- 浏览器验证：CZ 页来源段+薪资列、methodology 42 国表、首页新行业问题段均渲染正确。
- **静态 PNG 地图未重截**：几何(就业)与颜色(暴露)未变，薪资不上地图。

## 文件清单
- **新增**：`scripts/build_{cz,hu,sg}_salary.py`
- **修改**：`scripts/gen_intl_v2.py`、`scripts/gen_nordic_official.py`、`scripts/build_treemap_longform.py`、`job-treemap/build.py`、`job-treemap/longform.json`
- **gitignore 产物（未提交）**：`downloads/{cz,hu,sg}/*_by_isco.json`（已含薪资）、`job-treemap/dist/*`（已重建）
- **重导出（未提交，因 `site/` 整目录未跟踪）**：`site/src/data/*`

## commit / 部署状态
- 分支 `feat/aijobriskmap-czhusg-sources`：`74f2ba4f`（数据管线）+ `f2464494`（站点文案）。**未 push**。
- DB：CZ/HU/SG 全量已落库。
- `site/src/data/*`、`downloads/*`、`dist/*` 均已是最新但**未纳入本次提交**（site/ 整目录未跟踪、其余 gitignore）。

## 待办（下次）
1. **部署**：aijobriskmap dist 上线（用户操作）；push 本分支或并入 main。
2. **仍未提交的旧工作**（见 `docs/session-handoff-2026-07-28.md`）：批次20/北欧的 `build_{eurostat,ilostat,no,se,fi,dk,is}_official.py`、`seed_treemap_country.py`、`gen_cn_official.py` 等 aijobriskmap 管线脚本；aijobrisk-go 全套；均仍 `??`/`M` 未提交。
3. **可选**：MY 2012 / TH 2013 workforce 年份较旧，可补更近数据。
4. **翻译**：CZ/HU/SG 新增英文文案（~5语言）未翻，走现有 DeepSeek/Azure 管线。
5. 相关记忆见 `[[eu-asia-batch-collection]]`、`[[nordic-collection]]`。
