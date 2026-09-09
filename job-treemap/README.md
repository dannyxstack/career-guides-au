# job-treemap — aijobriskmap.com（多国 AI 暴露职业树图，独立站）

一套**自包含、可独立部署**的静态站点，用 squarified treemap 展示各国职业的 **AI 暴露度**：
方块面积 = 就业人数（workforce），颜色 = AI 暴露度 0–10（绿低→红高）。
暴露度基于两个公开权威、面向**生成式 AI 时代**的研究（ILO WP140 + OpenAI GPTs-are-GPTs）计算，
详见下方[「AI 暴露度指数计算方式」](#ai-暴露度指数计算方式)。

模板思路复刻自
[0xtreme/aus-jobs](https://github.com/0xtreme/aus-jobs)、
[karpathy/jobs](https://github.com/karpathy/jobs)、
[madeye.github.io/jobs](https://madeye.github.io/jobs/)，
**与主站（`site/` 的 Astro 应用）完全独立**——本目录就是为「**单独域名部署**」准备的。
按 `RULES.md` 的单一职责约定，本站只做数据可视化，不搬运主站的职业分析内容。

覆盖 **46 国**（`build.py` 的 `ORDER` / `COUNTRY_META` / `SLUG` 三者同步维护）：

```
AU US UK CA NZ JP KR DE FR ES IT NL IE BR MX IN CN NO SE FI DK IS BE AT
PL PT GR HU CZ RO LU SK SI HR TR AR CL MY ID TH VN SG CH EE LV LT
```

站点规模（随数据变化，构建时动态算出，见 `NC` / `N_OCC`）：约 **21,000 个职业**、
覆盖约 **23.9 亿劳动人口**。**文案里不要再硬编码国家数或职业数**——历史上这些数字散落十来处，
`ORDER` 一改就集体过期（about 页曾长期写着 42 国）。

---

## 目录结构

### 源码（本目录）

```
job-treemap/
├── build.py            # 主构建脚本：读主站数据 -> 生成 dist/ 全站
├── build_reports.py    # 各国 PDF 报告的 HTML + 报告落地页（依赖 build.py 已产出的 dist/country/）
├── build_all.py        # 一条命令跑完整流水线（见「构建」）
├── template.html       # 树图页唯一共享模板（内联 CSS/JS + __CONFIG__ 等占位符）
├── report_template.html# PDF 报告正文模板（Jinja2）
├── xrepo_ai.py         # 跨仓库补充：从 aijobrisk-go 数据集取「AI 会替代的任务 / 人类护城河 /
│                       #   邻近职业」，供报告第 11~13 章使用
├── summaries.json      # 各国摘要文案（LLM 生成，增量缓存，46 国齐全）
├── longform.json       # 首页长文 3 个板块（LLM 生成，增量缓存）
├── audit.md            # 第三方落地页评测转成的 todolist
└── dist/               # 构建产物（gitignore，不入库）
```

### 产物 `dist/`

```
dist/
├── index.html                     # 首页：hero + CTA + 气泡图/网格双视图 + 长文
├── country/{slug}/                # 各国树图站（46 个），slug = 小写全名如 united-states
│   ├── index.html                 #   模板 + 该国 __CONFIG__，自包含
│   ├── data.json                  #   该国职业数据（页面 fetch）
│   └── favicon.svg
├── reports/                       # PDF 报告体系
│   ├── index.html                 #   报告总览 hub（首页主 CTA 的落点，由 build.py 生成）
│   └── {slug}/
│       ├── index.html             #   该国报告落地页（build_reports.py）
│       ├── report.html            #   报告正文 HTML（供 Playwright 打印）
│       └── {slug}-ai-job-risk-{年}.pdf
├── embed/                         # 嵌入体系
│   ├── index.html                 #   embed / press-kit hub（iframe 代码 + PNG 下载 + 引用格式）
│   └── {slug}/index.html          #   裸嵌入页（iframe 目标，noindex，无侧栏/页脚）
├── static/maps/
│   └── ai-job-risk-map-{slug}-{年}.png   # 各国地图 PNG（Playwright 截图，也用作 og:image）
├── ai-job-loss-2030.html          # 「2030 年 AI 就业流失」情景估算专题页
├── about.html                     # 这个站是什么
├── methodology.html               # 方法论 + 全部国家的数据来源表
├── dataset.csv                    # 全量数据下载（一职业一行，含各国）
├── llms.txt / robots.txt / sitemap.xml
├── favicon.svg
├── og-image.png                   # 通用分享图（Pillow 画的）
├── og-home.png                    # 首页分享图（首页截图，shoot_home_og.mjs）
└── og-job-loss.png                # 2030 专题分享图（Pillow）
```

- **树图页模板只有一份**（`template.html`），所有国家页/嵌入页都是它 + 不同的 `__CONFIG__`（JSON）注入。
- 页面内资源用**相对路径**，站内链接用**绝对路径**（`/country/...`、`/reports/...`），
  故整站须部署在**域名根目录**；单国目录也可单独拿走部署（`data.json` 是相对路径）。

---

## 数据来源

`build.py` 读取主站导出的 v2 数据（**唯一数据源，本目录不自采数据**）：

- `../site/src/data/occupations_v2.json` — 职业数据（英文母本 v2 管线导出）
- `../site/src/data/categories_v2.json` — 分类 slug

字段映射（`build_record()`）：

| 树图字段 | 来自 occupations_v2.json |
|---|---|
| `title` | `name_en`（回退 `slug`） |
| `jobs`（面积） | `workforce_size` |
| `exposure`（颜色，0–10 整数） | **首选** `ai.aioe_pct/10`（权威 GenAI 指数，见下）；缺失时回退 `ai.automation_exposure`（LLM 主观分） |
| `pay` | `avg_salary` |
| `exposure_rationale` | `ai.verdict_zh` |
| `aioe_pct` | `ai.aioe_pct`（0–100 百分位；tooltip/详情/报告用） |
| `category` | `category` → `categories_v2.json` 的 slug |
| `anzsco` | `occ_code`（各国为 ANZSCO/SOC/NOC/ISCO/JSCO 等） |

**就业数据的权威分级**（`SOURCE_INFO` 的 tier，决定页面上的署名措辞）：

| Tier | 含义 | 国家数 |
|---|---|---:|
| A | 官方国家统计（JSA/ABS、BLS、ONS、StatCan…） | 26 |
| B | Eurostat 欧盟劳动力调查（职业细分由大类占比建模） | 14 |
| C | ILOSTAT（联合国 ILO 协调口径） | 6 |

各国货币符号、页脚数据源署名同样在 `COUNTRY_META` / `SOURCE_INFO` 中按国切换；
**未列入 `COUNTRY_META` 的国家会被直接跳过**。

---

## AI 暴露度指数计算方式

方块颜色（`exposure` 0–10）与详情里的 `aioe_pct`（0–100 百分位）**不是主观打分**，而是由
`scripts/compute_ai_exposure.py` 从两个公开、权威、面向**生成式 AI 时代**的研究计算得出，
再写回主站 DB（`occupation_ai_v2.aioe_pct/aioe_score/aioe_method`），随 `occupations_v2.json` 导出：

**两个数据源（均可自由复用）**

| 源 | 键 | 覆盖 | 分值 | 许可 |
|---|---|---|---|---|
| **ILO 工作论文 140**《Generative AI and Jobs: A Refined Global Index of Occupational Exposure》(2025) | ISCO-08 四位 | 112 个有实质暴露的职业（附录 Table A1） | GenAI 暴露 mean 0–1 | CC BY 4.0 |
| **Eloundou 等《GPTs are GPTs》**(OpenAI, 2023) | O\*NET-SOC 六位 | ~800 职业（连续） | 任务型 LLM 暴露 beta 0–1 | MIT |

> 两套 0–1 分实测同尺度且高度吻合（Data Entry Clerks：ILO 0.70 / Eloundou 0.696；Accountants 0.51 / 0.54），
> 故可直接拼接、无需重缩放。

**每职业 → 0–100 百分位的算法**

1. **取 0–1 原始分**（ILO 优先锚高档，Eloundou 连续填充）：
   - **美国** → 按 SOC-6 直取 Eloundou beta（缺失按 SOC 组均值回退）。
   - **其余国** → 本国码 → **ISCO-08 四位**，若命中 ILO 的 112 表用 **ILO 均值**，否则经
     **ESCO/O\*NET 桥**（`isco4→SOC→beta`）取 **Eloundou** 分。
2. **归一为全局百分位**：原始分在**同一套全局参考分布**（Eloundou ~800 职业 beta 的经验分布）里的
   百分位 → `aioe_pct` 0–100。全局绝对锚定 ⇒ **各国口径一致、可横向比较**。
3. treemap 颜色 `exposure = round(aioe_pct/10)`（0–10）。

**各国 → ISCO-08 对应**

- **ISCO 原生**（IE / IT / NL / CH 等）：`occ_code` 即 ISCO-08 四位，直接对应。
- **官方对应表**：AU/NZ（ANZSCO）、DE（KldB）、UK（SOC）、CA（NOC）、**ES（INE 官方 CNO-11↔ISCO-08，见 `downloads/es/`）** → ISCO-08。
- **AI 辅助映射**（`LLM_MAPPED` = FR / JP / KR）：本环境未能取到干净的官方 ROME/JSCO/KECO→ISCO 对应表
  （日本无代码级官方表；韩国 KOSTAT 门户证书/DNS 不可达；法国官方是 ROME→ESCO 多跳且需交互下载），
  故用 LLM 把每个职业**映射到官方 ISCO-08 的 436 个单位组**（即 ILO WP140 自己的做法，见
  `scripts/build_llm_isco_xwalk.py`），分值仍走 ILO/Eloundou，`aioe_method` 加 **`_llmmap`** 后缀以区分。
  官方表到手后放入 `.codex_tmp/xwalk_{cc}.json` 重跑即升级。

**方法标签**（`ai.aioe_method`）：`ilo_genai`（ILO 锚）/ `eloundou_soc`·`eloundou_isco`（Eloundou 填充）/
`pending_crosswalk`（暂回退 LLM）。

**复算命令**（须在 conda 环境 `career-video` 下，见 `RULES.md`）

```bash
python scripts/build_genai_refs.py       # 抓 ILO PDF + Eloundou CSV → .codex_tmp/genai_ref.json
python scripts/compute_ai_exposure.py    # 写回 occupation_ai_v2（--dry 只预览）
python -m scripts.export_site_data_v2    # 重导出 occupations_v2.json
python job-treemap/build_all.py          # 重建本站
```

> 与旧的 `scripts/compute_aioe.py`（Felten AIOE，2021，**前生成式 AI 时代**）相比，本管线换用
> 生成式 AI 时代的 ILO/OpenAI 源，数值分布从压缩的 4–9 恢复为自然的 1–9（对齐 0xtreme/karpathy 参照站）。

---

## 构建

**所有 Python 命令都必须用 conda 环境 `career-video`**（`RULES.md` 项目规则）。

```bash
python job-treemap/build_all.py                 # 全量流水线
python job-treemap/build_all.py --fast          # 只跑 build.py（跳过 LLM 与 Playwright）
python job-treemap/build_all.py --no-maps       # 跳过 Playwright 截图与二次构建
python job-treemap/build_all.py --force-content # 强制重生成 summaries + longform
```

流水线顺序（`build_all.py`）：

| 步 | 做什么 | 致命? |
|---|---|---|
| 1 | `scripts.build_treemap_summaries` → `summaries.json`（LLM，增量缓存） | 否 |
| 2 | `scripts.build_treemap_longform` → `longform.json`（LLM，增量缓存） | 否 |
| 3 | `build.py` **pass 1** → `dist/` 全站（含 `/embed/`，供截图用） | **是** |
| 4 | `scripts/shoot_maps.mjs`（Playwright）→ `dist/static/maps/*.png` | 否 |
| 5 | `build.py` **pass 2** → 新 PNG 进 og:image / Dataset schema | **是** |
| 6 | `scripts/shoot_home_og.mjs`（Playwright）→ `dist/og-home.png` | 否 |
| 7 | `build_reports.py` + `scripts/shoot_reports.mjs` → 各国报告 HTML + PDF | 否 |

- 只有 `build.py` 是致命步骤；LLM 与 Playwright 步骤失败都会走**确定性回退**（模板摘要 / 缺图时
  og 回落到 `og-image.png`），站点照样构建完成。
- LLM 步骤需要 `.env` 里的 `DEEPSEEK_API_KEY`；命中缓存时几乎零成本。
- Playwright 步骤需要 node + `npx playwright install chromium`。
- 单国预览：`python job-treemap/build.py US` 只重建 `/country/united-states/` 与 `/embed/united-states/`，
  跳过全站页与清理步骤。
- 只重建某几国的报告：`python job-treemap/build_reports.py AU US`。

**前置条件**：`../site/src/data/occupations_v2.json` 已是最新（由主站 `export_site_data_v2` 生成）。
主站数据更新了就**先重导出主站数据，再跑本流水线**。

本地预览（**必须走 HTTP**，`fetch` 不支持 `file://`）：

```bash
python -m http.server 8931 --directory job-treemap/dist
# 首页    http://localhost:8931/
# 单国站  http://localhost:8931/country/united-states/
# 报告    http://localhost:8931/reports/
```

仓库根的 `.claude/launch.json` 里已有同名配置 `treemap-dist`（端口 8931）。

---

## 部署（单独域名）

产物是**纯静态文件**，任何静态托管都可（Nginx / Apache / 对象存储+CDN / Netlify / GitHub Pages…），
只需以 **HTTP(S)** 提供（页面要 `fetch` 数据 JSON）。

站内链接是绝对路径，因此**整站必须挂在域名根目录**。
（例外：`dist/country/{slug}/` 自身是自包含的，单独拿走部署也能显示树图，只是站内链接会指向根。）

### Nginx 示例

```nginx
server {
    listen 80;
    server_name aijobriskmap.com;
    root /var/www/job-treemap;        # = dist/ 的内容
    index index.html;

    location / { try_files $uri $uri/ =404; }

    location ~* \.json$     { add_header Cache-Control "public, max-age=3600"; }
    location ~* \.(png|pdf)$ { add_header Cache-Control "public, max-age=604800"; }
    location = /favicon.svg { add_header Cache-Control "public, max-age=604800"; }
}
```

### 上传

```bash
rsync -avz --delete job-treemap/dist/ user@host:/var/www/job-treemap/
```

> 仓库里的 `scripts/deploy_dist.{sh,ps1}`、`docs/deploy-dist-over-ssh.md` 是给**主站 Astro dist** 用的，
> 默认目标路径不是本站——**用于本站前必须先确认目标路径**，不要凭默认值执行。
> 历史部署记录见 `docs/session-handoff-2026-07-30b.md`。

---

## 更新流程小结

1. 主站数据有变 → 重新导出 `occupations_v2.json`。
2. `python job-treemap/build_all.py` 重建 `dist/`（改了文案但数据没变，用 `--fast` 更快）。
3. 确认目标路径后 `rsync` 同步 `dist/` 到域名 webroot。
