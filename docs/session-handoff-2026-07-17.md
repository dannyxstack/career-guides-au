# 会话交接 · 2026-07-17（job-treemap：FAQ + 首页长文 + Risk/Exposure 术语统一 + 一键构建脚本）

> 接续 `docs/session-handoff-2026-07-16d.md`（诚实性修复 + SEO 大改 + /country 路由 + 静态图/embed/记者页 + 折叠表）。
> 本会话推进 16d 待办中的 **#6 首页 SEO 长文 + 每国 FAQPage** 和 **术语统一（Risk vs Exposure）**，并把整条构建流水线整合成**一个脚本**。
> **本会话全部改动用户将手动 commit**（沿用惯例）。

---

## 一、按需求顺序的改动

### 1. 每国 FAQPage + 首页 3×1000 字长文（16d 待办 #6，选定**方案 C**）
决策：**首页长文走 LLM（表达力），每国 FAQ 走确定性模板（数字保证正确、零编造）**。诚实性红线（严禁编造无数据支撑数字）压在带数字的 FAQ 上，全部取自 `country_stats`。

**每国 FAQ（`build.py`，全确定性）**
- `country_faqs(name, st)`：6 条固定问答，数字全来自 `st`（加权均值 + band + top/bottom/industries）。答案纯文本，**可见 HTML 与 FAQPage schema 逐字一致**（Google 硬要求）。
- `faq_accordion(faqs)`：原生 `<details>/<summary>` 手风琴，**默认折叠**、内容留 DOM 可爬。插在第二屏「Methodology & sources」前，`<h2 id="faq">`。
- `faq_ld(faqs)`：`FAQPage` JSON-LD。主循环 `faqs = country_faqs(...)` 算一次，同时喂 `static_content`（显示）和 `faq_ld`（schema）保证一致；接进国家页 `__JSONLD__`（Dataset + Breadcrumb + **FAQPage**）。
- CSS：`template.html` `.faq-item`（`+`/`−` 标记、折叠样式）。

**首页长文（`build.py` + 新脚本）**
- `load_longform()` 读 `job-treemap/longform.json` → `{"sections":[{"h2","html"}×3]}`；缺失则首页不渲染该段（回退安全）。
- `build_landing` 在国家网格后渲染 `<div class="longform">` 3 段。
- 新脚本 **`scripts/build_treemap_longform.py`**（照 `build_treemap_summaries.py` 骨架）：DeepSeek `complete_json`、增量缓存、可续跑、**分 3 段各一次调用**（一次 3000 字会缩水）。`build_facts()` 聚合真实数字（13 国加权均值/总职业/总人数/行业排名去重）喂模型，prompt 硬约束「只用 FACTS 里的数字，禁编造 '40% of tasks / human moat'」。3 段主题：①暴露度是什么/怎么读图/暴露≠失业 ②哪些国家和行业最暴露 ③高暴露怎么办 + 数据局限。
- **`longform.json` 已生成**（用户本会话跑过 `python -m scripts.build_treemap_longform`，17KB）。

### 2. Risk vs Exposure 术语统一（16d 待办 #6，选定**方案 C 双层 + 桥接句**）
原状：品牌/域名/SEO 押 **risk**（aijobriskmap.com、AI Job Risk Map），指标却叫 **exposure**（0–10）→ 混用、SEO 分散。
方案 C：**门面/叙事层用 risk 抓流量，数据/指标标签层保留 exposure 保准确，加一句桥接把两者显式绑定**。
- 评估过 H1 两候选（按搜索量/SEO/GEO），用户最终选 **A：`AI Job Risk in {country}`**（非加强版 `Jobs Most at Risk from AI in {country}`）。加强版的长尾/CTR 由 FAQ/首页 H1 承担。

**门面层改动（build.py + template.html）**
- 国家页 H1（构建期 `__H1__` + `template.html` JS 运行时 `pageTitle`，两处同步）→ **`AI Job Risk in {name}`**（原 `AI Exposure of the {name} Job Market`，顺带解决 "the Australia" 生硬）。
- **桥接句**：`template.html` 侧栏副标题下新增静态 `<p class="bridge">`（无国名 → 免 JS/免 build.py）：*"We score each job's **AI risk** by its **exposure** to generative AI — how much of its day-to-day tasks AI can already do, from 0 to 10."* + CSS。
- 第二屏 H2：`AI job automation risk in {name}` → **`AI job risk in {name}`**（去 "automation" 过度断言）。
- 首页 landing：H1 `Which jobs are most exposed to AI?` → **`Which jobs are most at risk from AI?`**；lead 段改成 risk↔exposure 桥接叙事。
- FAQ 问题：Q1 `How exposed is…?`→`How much AI risk do jobs in {name} face?`、Q2 `…most exposed…`→`…most at risk from AI?`（答案保留 exposure 措辞 = 内建桥接）。**Q5 industries 故意保留 "most exposed"**（分仓对冲长尾）。

**数据层保留 exposure（一个没动）**：sidebar「Weighted avg. exposure」「Jobs by exposure」、表头 `Exposure`、tooltip `AI Exposure: X/10`、详情面板 `AI exposure`、`AI exposure pct.`、方法论。

**关键词分仓对冲**（H1 选错代价≈0）：H1/FAQ/第二屏 H2 走 risk 词；title、Q5、meta desc、schema keywords、img alt/文件名（`ai-job-risk-map-{cc}`）仍带 exposed/exposure —— 两套词同时布，任一路失手另一路仍收量。GEO 补偿靠桥接句（可引用的定义+数字）+ FAQ 直答 + `llms.txt` + FAQPage/Dataset schema，与 H1 措辞解耦。事后看 Search Console，H1 是构建期字符串改一行重跑即可，无需回退。

- **注意**：`data.json` 里仍有 `automation risk` —— 那是数据库单职业 `exposure_rationale` 文案（职业内容层），非术语层，读来自然，未动。

### 3. 首页长文改折叠（默认 2 行 + 渐隐 + 点击展开）
- 用户反馈首页 3 段长文太长。`build_landing`：每段 body 包进 `.lf-body` + `Read more` 按钮。
- CSS：`.lf-body{max-height:3.2em;overflow:hidden}` clamp ~2 行 + `::after` 底部渐隐（`linear-gradient(rgba(10,10,15,0),#0a0a0f)`）；`.lf.open .lf-body{max-height:none}`。**完整内容留 DOM 可爬**（只 CSS clip，不损 SEO）。
- 一小段 toggle JS（加在 landing `</body>` 前）：点击切 `.open`，按钮 `Read more`⟷`Show less`。
- 实测：折叠 51px（≈2 行）↔ 展开 2737px 全文，渐隐/切换正常。

### 4. 一键构建脚本 `job-treemap/build_all.py`（16d 待办 #3 落地）
把 `summaries` + `longform` + `build.py`×2 + `shoot_maps.mjs` 整合成**一个命令**。
- 顺序：summaries(缓存)→longform(缓存)→**build 第1遍**(产出 shooter 需要的 /embed 页)→shoot_maps(13 截图)→**build 第2遍**(新 PNG 进 og/schema)。
- **best-effort**：步骤 1/2/4 失败（无 DeepSeek key/无 Playwright/断网）只告警不中断，build.py 有确定性回退；只有 build.py 本身 fatal。
- **缓存跳过**：LLM 两步已生成即 `cached, skip`，不打 API；加新国家自动只补新的。实测完整跑 **~37s**（含 13 张截图）。
- 子进程强制 `PYTHONIOENCODING=utf-8`（GBK 坑）；编排层 print 全 ASCII。用 `sys.executable`，子步骤同一解释器。
- 用法：
  ```
  python job-treemap/build_all.py                 # 完整流水线
  python job-treemap/build_all.py --no-maps       # 跳过截图+第2遍build
  python job-treemap/build_all.py --fast          # 只 build.py
  python job-treemap/build_all.py --force-content # 强制重生成 LLM 文案
  ```
- 每晚 cron 直接挂 `python job-treemap/build_all.py`。原 `build.py`/`shoot_maps.mjs`/两个 LLM 脚本均保留，可单独调用。

---

## 二、新增 / 改动文件
- `job-treemap/build.py`：+`country_faqs`/`faq_accordion`/`faq_ld`/`load_longform`；改 `static_content`(新增 `faqs` 形参 + 插 FAQ)、`build_landing`(长文渲染+折叠+CSS+toggle JS)、主循环(算 faqs + 拼 FAQPage schema)、H1/H2/landing/FAQ 术语。
- `job-treemap/template.html`：FAQ `.faq-item` CSS、桥接句 `.bridge` + CSS、JS 运行时 H1 改 risk。
- `scripts/build_treemap_longform.py`：**新增**，产 `longform.json`。
- `job-treemap/build_all.py`：**新增**，一键编排。
- `job-treemap/longform.json`：**新增产物**（已生成）。

## 三、⚠ 待办 / 待决
1. **全部未 commit**（本会话改动 + 上轮 16d 全部；`node_modules` 是否 gitignore 仍待决——见 16d #1）。
2. **部署顺序不变**（见 16d #2）：先上 `docs/nginx-301-treemap-country.conf`（旧 URL 301 + `/embed/*` CSP `frame-ancestors *`）再切 `dist/`。
3. **longform.json 需人工审一遍**（尤其有没有编数字），满意后锁定。数据大改后可 `--force-content` 重生成。
4. **仍未做**（16d 遗留）：`/job/{occ}-{country}` 空内链**暂不链**（软 404）；Custom Map 表单现 `mailto:`（待接 Formspree/端点）；WebP（装 sharp 后重跑即产出）。
5. **术语事后测量**：部署后看 Search Console，若 H1(risk) 在 "exposed" 类 query 吃亏（理论上有分仓不会），补某个次要槽位即可，不必回退 H1。

## 四、关键坑
1. **FAQ schema 与可见文本必须一致**：`country_faqs` 只算一次，可见 accordion 和 `faq_ld` 都从它渲染。
2. **CSS 折叠不伤 SEO**：FAQ `<details>` / 首页 `.lf-body` clip 的内容都留 DOM，爬虫可读。
3. **longform 分段调用**：一次要 3000 字模型缩水，必须 3 段各一次。
4. **build_all best-effort**：LLM/Playwright 非 fatal，否则没网/没 key 就无法构建。
5. **GBK**：子进程 + 编排层都要防（env UTF-8 + print ASCII）。
6. **桥接句做成无国名静态行** → 不进 JS/不进 build.py 主循环，13 国零 churn。

> 恢复：读本文件 + `docs/session-handoff-2026-07-16d.md` + memory [[job-treemap-clone]] [[genai-exposure-pipeline]] [[flag-rendering-rule]]。
> 关键产物：`job-treemap/{build.py,template.html,build_all.py,summaries.json,longform.json}`、`scripts/{build_treemap_longform.py,build_treemap_summaries.py,shoot_maps.mjs}`、`docs/nginx-301-treemap-country.conf`、`dist/`。
> 一键构建：`python job-treemap/build_all.py`。
