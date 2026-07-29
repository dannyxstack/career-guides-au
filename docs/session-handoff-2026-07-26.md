# 会话交接 · 2026-07-26（BR/MX 官方职业采集 + aijobrisk-go job-risk-map + 部署文档）

> 接续 `docs/session-handoff-2026-07-25.md`。本会话三条主线：
> ① **巴西/墨西哥职业采集**——先估算、后**推翻改为官方微数据检索(不估算)+ LLM 仅补文案**，两国 436×2 全入库；
> ② **aijobrisk-go 的 job-risk-map** 用「方案 B」实现（最后一个未移植页面，全站现已齐）；
> ③ 写 `aijobrisk-go/deployment.md`。
> 恢复请读本文件 + memory [[brazil-mexico-collection]] [[aijobrisk-go-port]]。

---

## 1. 巴西(BR)/墨西哥(MX)职业采集 —— 本会话主体

见 memory [[brazil-mexico-collection]]。骨架统一 **ISCO-08 436**。

### 1.1 方向大转弯（关键）
- 起初复用 [[india-collection]] 的 `gen_intl_v2.py`（ISCO-08 英文母本 + LLM 估算薪资/人数）。用户小样验证后追问数据来源，得知**薪资/人数/评分全是 DeepSeek 估算、非检索**。
- 用户拍板：**「不用 deepseek 估算，要先检索」**。范围选定 = **官方硬数据(薪资/人数/本地语言名)走官方检索、不估算；LLM 仅补无官方源字段**（评分/文案/FAQ/签证/教育/category/英文名）。
- 已入库的 24 条估算数据（BR/MX 各 12）+ TM 注入 **已清库重来**。

### 1.2 环境坑（重要）
- **DeepSeek 停用 `deepseek-chat`**，改 `deepseek-v4-pro` / `deepseek-v4-flash`——**v4 系列都是推理模型**。pro 单条 89s/reasoning 5881；flash 单条 26s/reasoning 1399。**用户选 flash 跑全量**。
- `.env` 用户手设为 pro；采集命令行用 `DEEPSEEK_MODEL=deepseek-v4-flash` 覆盖（`load_dotenv(override=False)` → shell env 优先，不动 .env）。
- `scripts/_deepseek_rest.py` 的 `max_tokens` **4000→8000**（推理模型必需，否则 `finish_reason=length` 被思考吃光只吐几十字符）。

### 1.3 官方数据链（两国对称：官方微数据本地聚合）
**BR — PNAD-C 微数据（IBGE）**
- 下载 `ftp.ibge.gov.br/.../Trimestral/Microdados/{年}/PNADC_{季}{年}.zip`（本次 `PNADC_042025.zip`，定宽 ~212MB，txt 解压 ~1.7GB）。
- **关键突破：`V4010`(职业码 COD) = ISCO-08 4位码直连**（COD 由 IBGE 照 ISCO-08 建，覆盖 428/436，**零交叉表**）。葡语名从 `Estrutura_Ocupacao_COD.xls`。
- 定宽位（1-based，`dict_pnadc/input_PNADC_trimestral.txt`）：`V1028@50`(权重，**字符串自带小数点→float**)、`V4010@152`、`VD4002@410`(=1 在业)、`VD4016@427`(月收入)。
- 脚本 `scripts/build_br_salary.py` → `downloads/br/br_by_isco.json`（429 职业，mean/median 年薪×12 + 加权中位数 + workforce + 葡语名）。

**MX — ENOE 微数据（INEGI）**
- 下载 `inegi.org.mx/.../datosabiertos/{年}/conjunto_de_datos_enoe_{年}_{季}t_csv.zip`（本次 `enoe_2025_3t_csv.zip`，~46MB）。⚠️ INEGI 对错误 URL 返回 **200+HTML 软404**，需精确命名。
- **SINCO→ISCO-08**：官方 `sinco_tablas_comparativas.xlsx`（'SINCO-CIUO' 表 4位级）→ `scripts/parse_mx_crosswalk.py` → `sinco_to_isco.json`（含西语名，覆盖 315/436）。
- **需合并两表**（主键 `cd_a+cve_ent+con+v_sel+n_hog+h_mud+n_ren`）：COE1 的 `p3`(SINCO 4位) + SDEM 的 `clase2`(=1在业)/`ingocup`(月收入)/`fac_tri`(季度权重)。
- 脚本 `scripts/build_mx_salary.py` → `downloads/mx/mx_by_isco.json`（311 ISCO，mean/median + workforce + 西语名）。

**BR 死路（勿再试）**：salario.com.br 依赖 CBO-2002→ISCO；官方 mtecbo 交叉表下载被 **Google reCAPTCHA 挡死**（不可绕，安全红线）；UCSD 版本(CBO-94)不符；ILOSTAT 太粗(1位大类)。故改 PNAD-C 微数据（V4010 直连 ISCO）。

### 1.4 入库（官方硬数据 + LLM 补文案的合并）
脚本 **`scripts/gen_br_mx_official.py`**（独立脚本，不动 CH/IN 的 gen_intl_v2）：
- **官方覆盖**：薪资 mean/median → `occupation_salaries_v2` 两行 `experience="Average salary"`(喂 export 的 avg_salary) + `"Median salary"`；人数 → `occupations.workforce_size`；本地名(pt/es) → 直灌 `translations_v2`(gen_model=`collected:BR/MX`，translate_v2 自动跳过)。
  - ⚠️ 旧的 `occupation_salaries`(median/mean band 表) 在 v2 库已是 `deprecated_` 前缀；故适配到 v2 原生的 `occupation_salaries_v2` 标签法（`avg_salary` 由 `export_site_data_v2.py` 取 label∈{average salary,average,mean,avg salary} 那行的 min）。
- **LLM 仅补**（`build_prompt_official` 去掉 salary/workforce/name_local）：英文名/category/summary/forecast/trend/11维评分/签证/教育/资历/FAQ/fit/unfit/growth/is_migration/shortage。
- 无官方薪资的 ISCO(BR 14/MX 126)：仍生 LLM 文案，薪资/人数**留空不估算**。
- `--codes` 支持定向重试；`--archive` 累积 `downloads/{br,mx}/collected.json`（含 `official` 块，可不调 LLM 重灌）。

**跑批命令**：`DEEPSEEK_MODEL=deepseek-v4-flash LLM_PROVIDER=deepseek python -m scripts.gen_br_mx_official --country BR --archive`（MX 同）。

### 1.5 最终结果（全部完成）
| 国 | 职业 | AI块(拷自IT) | 官方avg薪资 | 本地名注入 | 有人数 | 归档 |
|---|---|---|---|---|---|---|
| BR | 436 | 436 | 422 | 421(pt) | 422 | 436 |
| MX | 436 | 436 | 310 | 311(es) | 311 | 436 |
- 全量并行跑（各 6+7 个 LLM 偶发 JSON 失败已 `--codes` 定向重试补齐）。
- AI 块：`python -m scripts.copy_ai_blocks_by_code --to BR/MX --from IT`（436/436，0 缺码）。
- `downloads/{br,mx}/README.md` 已改写为官方检索版。

**按约定未做（仅录库）**：未翻译其余语种、未接 locale、未 export/build、**全未 commit**。

---

## 2. aijobrisk-go 的 job-risk-map（方案 B，已完成）

见 memory [[aijobrisk-go-port]]。这是 aijobrisk-go 最后一个未移植页面，**全站页面现已齐**。
用户选 **方案 B：几何启动/首访算一次并缓存，每请求只本地化 meta**。

- **`internal/data/riskmap.go`**：移植 `riskmap.ts` 全部算法（`RiskColor`/`worstRatio`/`squarify`/`splitAspect`/`layoutFromOccs`/`BuildRiskMap`/`BuildGlobalRiskMap`）+ **几何缓存 `RiskLayoutFor(key)`**（key=`WORLD` 或国码，语言无关，`sync.Mutex` 首访计算）+ `OutlinePath`（读 `data/outline-paths.json`）。
- **`internal/web/riskmap.go`**：`riskMeta`（每请求 tr 名称/分类——方案 B 的「只本地化 meta」）+ `riskMapSVG`（`strings.Builder` 拼整块 SVG，与 `RadarSVG` 同风格=方式①）+ handler（全球 `country==""`/国家/无效国 404）。
- **`templates/job_risk_map.html`**：移植 RiskMap.astro 的 markup + tooltip JS(读内联 M/T) + CSS（app.css 里 `--muted/--green/--white/--card/--line` 都在，逐字照搬）。
- **`internal/web/server.go`**：路由接 `case "job-risk-map"`（删 TODO）。

**验证**（`go vet` 干净 + 浏览器 :4399）：全球图 4932 tiles/11 分类块/图例 503,475,343 workers/世界轮廓；AU 国家图 586 tiles+澳洲轮廓；FR 本地化(h1+职业名法语)；无效国 404；**缓存：全球图 4932 tiles 仍 2~16ms（几何未重算）**；控制台无报错。

---

## 3. `aijobrisk-go/deployment.md`（已写）

Go SSR 部署文档：架构（单二进制单端口/运行时读数据免16GB构建/投票DB懒连接）、构建（Linux `CGO_ENABLED=0 go build -ldflags="-s -w" -trimpath`；**Windows Defender/火绒把新Go .exe当误报隔离**→本机用 `go run`、正式在Linux构建）、部署文件、环境变量表、投票DB最小权限账号、systemd unit、nginx反代+TLS、更新回滚、资源小结（启动~1.9s/RSS~694MB/Go 1.24+go-sql-driver v1.8.1）。

---

## 待办 / 待决

1. **BR/MX 仅录库**：未翻译其余语种（pt/es 本地名已灌，其余 10 语种未跑 translate_v2）、未接 locale/前端、未 export_site_data_v2、未 build。**全未 commit**。
2. **aijobrisk-go**：job-risk-map 等全部页面已移植；deployment.md 已写；**整个 `aijobrisk-go/` 仍未 commit**（含本会话的 riskmap 三文件 + deployment.md）。
3. 上一交接 `session-handoff-2026-07-25.md` 待办仍在（aijobrisk 的 sitemap/robots 端点、`aijobrisk/deployment.md`、`dd0cf799` 已提交未 push、投票表最小权限账号）。
4. 本会话新建脚本：`scripts/{parse_mx_crosswalk,build_br_salary,build_mx_salary,gen_br_mx_official}.py`；改动 `scripts/{gen_intl_v2,_deepseek_rest}.py`。

> 见 memory [[brazil-mexico-collection]] [[aijobrisk-go-port]] [[aijobrisk-ssr-site]] [[india-collection]] [[salary-median-mean]] [[i18n-translation-pipeline]]。
