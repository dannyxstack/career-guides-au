# 会话交接 · 2026-06-15（PPT 决策视频化 + 雷达评分 + 30 新职业 + 10 大类重构）

> 接续 `session-handoff-2026-06-14.md`。本会话重点：把 PPT/视频升级为"决策视频"风格、评分改雷达图+综合分、
> 修签证术语、新增 30 个职业（含非移民标识）、职业分类重构为 10 个英文大类、markdown 生成器通用化重写。

---

## 一、本会话完成（按时间顺序）

1. **幻灯片英文断词修复** `slides.py:_wrap`：含空格英文按单词换行（textwrap），中文仍按字符切。修了 "Science" 被切成 "Scie/nce"。
2. **Web 列表页加「生成 PPT」按钮**：`web/app.py` 新增 `GET /ppt/{occupation_id}` → 调 `ppt_builder.build_ppt` 直接下载 pptx；`templates/index.html` 在"生成大纲"旁加链接。
3. **大纲导出文件**：`scriptwriter.generate_outline` 成功后调 `_export_outline`，把大纲写成可读 Markdown 文案稿到 `out/outlines/{content_id}_{slug}_{platform}.md`。
4. **PPT 决策视频化改造（7 点建议）**，仅以 BI Analyst(occ 149) 为样板：
   - 签证数据修正：occ 149 visa 改 `482 Skills in Demand`（去旧 TSS），desc 说明按职责匹配 Data Analyst 224114；visa 页加通用 ANZSCO 风险声明。
   - 首屏强钩子：`_slide_title` 用 LLM 生成的 hook_title + 3 个关键数字 + 右侧实拍图。
   - 图表标题不绝对化：需求页改"岗位需求估算：2025 后仍偏强，但初级竞争加剧" + 估算逻辑说明。
   - 页序重排为决策视频流：钩子→每天做什么→收入/需求/薪资→评分→适合谁→技能路线(教育/资质)→增长热词→移民+ANZSCO→30天清单→CTA。
   - 新增页：`_slide_daily`(每天做什么)、`_slide_suitability`(适合谁/不适合谁)、`_slide_action`(30天行动清单)。
   - 增长页用 LLM 的 search 热词，回退 DB growth_areas。
   - **LLM 文案 brief**：`prompts.PPT_BRIEF_SCHEMA` + `scriptwriter.generate_ppt_brief()`，产出 hook_title/key_stats/daily_tasks/action_plan_30d/growth_keywords/anzsco_note，**存 `platform_contents`（platform='ppt'，为此 enum 加了 'ppt'）**；`build_ppt` 自动读取，缺失则即时生成，失败降级。
5. **评分页改雷达图 + 综合分**（覆盖上面的"5维"方案，改回全维度）：
   - `charts.draw_radar(ax,occ,labels)` + `charts.rating_radar_png` + `charts.overall_score(occ)`（按 `charts.RATING_POLARITY` 反转负向维度再平均，0~10）。
   - PPT `_slide_ratings` 用雷达图，标题"职业评分 · 综合 X.X/10"。
   - 视频 `slides.py:_s_ratings` 复用 `charts.draw_radar`，**PPT 与视频评分页一致**。
6. **大纲签证术语规则**：`prompts.build_outline_prompt` 加规则——482 用 Skills in Demand（去 TSS）、移民路径不说绝对、点明"需看 ANZSCO 匹配/雇主/州政策"。⚠ 仅改 prompt，**库里已生成的旧大纲(9 条含旧术语)未重生成**。
7. **新增 30 个职业 + 分类重构 + md 生成器重写**（见下）。

---

## 二、数据库结构变更（重要）

`occupations` 表：
- 新增 `is_migration TINYINT(1) NOT NULL DEFAULT 1`（1=技术移民职业 0=非移民）。
- 唯一键 `uq_country_occ_code` → 普通索引 `idx_country_occ_code`（允许多个空 occ_code）。
- 新增 `idx_anzsco_code`。
- `platform_contents.platform` enum 增加 `'ppt'`（存 PPT 文案 brief）。

> 因唯一键放开，新职业入库改用 `scripts/_seed_helper.seed_occupation_v2`（按 occ_code 或 anzsco_title 幂等 upsert，支持 is_migration）。旧 191 仍可用各自 seed。

---

## 三、新增 30 个职业（2026-06）

- 样板：`scripts/seed_sales_assistant.py`(621111,非移民)、`scripts/seed_web_developer.py`(261212,移民)。
- 批量：`scripts/seed_batch_2026_06.py`（28 个，数据驱动列表）。
- 数据来源：联网检索（Seek/JSA/Glassdoor 2025-2026）薪资区间估算 + 判断式评分。
- 现状：DB 共 **221 职业**；`is_migration` = **205 移民 / 16 非移民**。
- 非移民职业（文员/前台/医疗前台/办公室经理/诊所经理/牙助/医技/巴士司机/零售主管/记账/薪资文员/银行职员/信贷专员/商业清洁/厨房帮工）：照填真实 ANZSCO 分类码，但无签证路径、shortage=0、markdown 标注"非技术移民职业"。

---

## 四、职业分类重构为 10 个英文大类

`scripts/remap_categories.py`（幂等，整类映射 + 混合桶按 anzsco_title 逐职业覆盖）。已对 191+30 全部生效。

10 类：Healthcare & Care / Education & Community / Trades & Construction / IT & Digital /
Engineering & Infrastructure / Business, Finance & Legal / Hospitality, Retail & Tourism /
Transport, Logistics & Mining / Agriculture & Environment / Creative, Media & Personal Services。

当前分布：Business 41 / Trades 37 / Healthcare 32 / Engineering 25 / IT 19 / Education 16 /
Hospitality 14 / Transport 14 / Creative 13 / Agriculture 10。

---

## 五、Markdown 生成器通用化重写

`pipeline/generators/md_generator.py`：
- 去掉全部电工硬编码文本（旧版把电工专属句子套到所有职业）。
- `is_migration` 感知：非移民职业第6段写"非技术移民职业"说明、无签证表、结论尾句调整、顶部加注。
- 输出改到 `career-contents/au/{en名slug}.md`（旧版误写 `output/{code}.md`）。
- 已 `python generate_md.py` 全量重生成 **221 个 md，0 失败**；删除孤儿 `carpenter.md`（无对应职业，已有 formwork-carpenter.md）。
- 残留"电工/TRA"字样均为合法数据（plumber/hvac summary、solar/wind 确需电工资质、技工 FAQ 提 TRA 评估），非污染。

---

## 六、文档同步

- `rules.md`：新增"PPT / 决策视频内容规则"（签证/ANZSCO 写法、估算图声明、强钩子、评分雷达+综合分极性、增长热词、决策视频页序、LLM brief）。
- `.claude/skills/occupation-ppt/SKILL.md`：结构更新为 13 页决策视频版 + LLM brief 说明 + 雷达评分。

---

## 七、⚠️ 待办 / 提醒

1. **改任何代码/数据后必须重启 Web 服务**（config 启动读、uvicorn 不热重载）。界面看新职业/新分类需重启。
2. **旧大纲术语**：库里 9 条含 "482/TSS" 旧术语的视频大纲(occ 118/145/146/147/148/149/150/151)未重生成；prompt 已修，重生成即更新。
3. **PPT/视频改造仅落在 BI Analyst(149) 样板**；其余职业批量化未做。新职业首次出 PPT 会各触发一次 LLM brief。
4. 新增 30 职业数据为联网估算，非逐年官方统计；如需更精可二次核对。
5. （沿用）批量渲染 Remotion bundle 复用、发布自动化等更早待办仍在。

---

## 八、自检命令

```powershell
# 职业总数 / 移民分布
"e:/run/conda_envs/career-video/python.exe" -c "from db.connection import get_cursor;\
c=get_cursor().__enter__();c.execute('SELECT is_migration,COUNT(*) n FROM occupations GROUP BY is_migration');print(c.fetchall())"
# 全量重生成 markdown
python generate_md.py
# 生成某职业 PPT（自动取/生成 brief）
"e:/run/conda_envs/career-video/python.exe" -c "from video_pipeline import ppt_builder; print(ppt_builder.build_ppt(149))"
# 起界面
.\start_python_web.bat
```

---

## 九、续会话（同日下午）：TSS 术语全库修复 + Astro 站点搭建

### 9.1 签证术语全库规范化（修复所有职业介绍 markdown）
- 根因：DB `occupation_visa_pathways` 等字段里大量职业 482 仍写旧 "TSS"（上次仅改 149）。
- `scripts/fix_visa_terminology.py`：全库 **TSS → Skills in Demand**，覆盖 visa_name/description、i18n.summary、faqs.answer；保留"旧称 TSS"历史说明；`normalize()` **保护 MLTSSL/STSOL**（含子串 TSS）。
- 同时文本替换修复了 7 条视频大纲 body 的 TSS。
- ⚠ 过程中一度把 `MLTSSL` 误伤成 `MLSkills in DemandL`（179 处），已 SQL 精确回滚修复，并给脚本加保护；重生成后 MLTSSL 在 99 个文件完好。
- DB 482 visa_name 现全为 `Skills in Demand`（+1"工业消防"变体）；**全量重生成 221 个 md，0 失败**。
- 已验证非 149 职业（通信工程师 231）PPT/视频生成正确、术语正确。

### 9.2 Astro SSG 多语言职业站（新目录 `site/`）
- 方案：**DB → `scripts/export_site_data.py` 导出 `site/src/data/occupations.json` → Astro 构建期消费**（DB 不参与构建，可复现）。
- 技术栈：Astro 4（静态 SSG），Node v20.10。已 `npm install` + `npm run build` 通过，**生成 459 页**。
- 结构：
  - `site/src/lib/data.ts` 数据层 + 多语言 UI/维度标签 + `RAW_PAIRS` 精选对比配对 + `DIM_ORDER`。
  - `site/src/components/RatingRadar.astro` 多序列雷达（详情1序列/对比2序列叠加）。
  - `site/src/layouts/Base.astro` 深色主题 + hreflang。
  - 页面：`/`→`/AU/zh-CN/`；列表 `/AU/{zh-CN,en}/`（按10大类）；详情 `/AU/{locale}/{category}/{slug}/`（442页）；对比 `/AU/{locale}/compare/{a}-vs-{b}/`（7对×2，叠加雷达+并排薪资+逐维度"更优"按极性判定）。
- 设计决策：URL 用英文 slug 不随语言变；前端只依赖导出 JSON 不依赖 md；对比只做**精选静态可索引页**，长尾留交互工具（避免 4 万薄页）。
- 运行：`cd site && npm run dev`(4321) / `npm run build`(dist/)；数据更新后重跑 `export_site_data.py` 再 build；部署改 `astro.config.mjs` 的 `site` URL。

### 9.3 续会话待办
- 站点：加 `@astrojs/sitemap` + schema.org 结构化数据；长尾交互式对比工具(noindex)；更多语言(LLM 翻译入 `occupations_i18n`)/国家。
- 新增 `scripts/`：`fix_visa_terminology.py`、`export_site_data.py`（均幂等可重跑）。

---

> 恢复任务直接说「读取 docs/session-handoff-2026-06-15.md 继续」。
