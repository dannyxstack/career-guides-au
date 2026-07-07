# 会话交接 · 2026-07-08（"AI时代"文案、热门职业板块、滚动播报、百度大模型翻译接入+跑批、job-risk-map 宽屏/全轮廓/深填充）

> 接续 `docs/session-handoff-2026-07-07.md`。
> DB = 远程 MySQL（`.env`：MYSQL_*；表 `occupations`，国家列 `country_code`）。
> Python：`e:/run/conda_envs/career-video/python.exe`；长任务前 `PYTHONIOENCODING=utf-8`。
> 生产：每 5 分钟 `git pull`(main) + `npm run build`（8GB 堆）；导出前须停 astro dev 预览（否则 Errno22）。

---

## 本会话完成

### 1. 首页 Q3 文案「AI 时代」（10 语言）
- `hQ3T`「我接下来该学什么？」→「AI 时代我该学什么？」。中英母本在 `data.ts`（zh `AI 时代我该学什么？` / en `What should I learn in the AI era?`），其余 8 语言在 `ui_i18n.json` 手改。

### 2. 首页「热门职业搜索」板块（16 标签，DB 表驱动）
- 新表 **`occ_search_hits(country_code, slug, hits, seed_score, updated_at)`**（`scripts/seed_hot_occupations_schema.py`）。热度 = `hits + seed_score`；`hits` 留给未来真实搜索量，`seed_score` 为启发式预填充。
- `scripts/seed_hot_occupations.py`：按 workforce 0.5 / AI自动化暴露 0.3 / shortage 0.2 打分，写 4503 行 `seed_score`（幂等，不碰 hits）。
- `export_site_data.py`：查 `occ_search_hits` → 分散选 top-16（每国≤2、每类≤2，逐步放宽）→ 写 **`site/src/data/hot_occupations.json`**（`{country,slug,cat,name_en}`）。`HOT_N=16`。
- `Home.astro`：methodology 之后渲染板块，标签**带国旗**、链 `/{cc}/{locale}/{catSlug}/{slug}/`、职业名走 `name()` 本地化。UI 键 `hHotH`/`hHotB`。
- **未来接线**：搜索/点击结果发 beacon `UPDATE occ_search_hits SET hits=hits+1`，前端与导出零改动。

### 3. 首页滚动播报（搜索框下方，构建期预生成，前端轮播）
- 新文件 **`site/src/lib/ticker.ts`**：`buildTicker(locale)` 从 `occupations` 生成结构化洞察句（30–100 条，实测 en 69 条）。
  - #1 每分类 AI 暴露 top-3；#2 未来5年替代概率（`automation_exposure×9`，措辞"预计~"）；#6 AIOE 曝光度(0–100)。
  - #4/#5 **投票类**仅当 `polls` 有真实票数才入池（现为空自动跳过，投票上线后自动出现）。#3 工具替代类**已去掉**（无结构化工具名数据）。
- `Home.astro`：hero 内 hint 下方 `#tk`，JS `setInterval` 淡入淡出轮播；UI 模板键 `hTk1/hTk2/hTk4/hTk5/hTk6`（占位符 `{name}/{cat}/{pct}/{n}/{a}{b}{c}`）。
- 语言：中英母本在 `data.ts`；其余 9 语言经百度补译（见 §4）。

### 4. 百度大模型文本翻译接入（**关键：接口与之前设想不同**）
- **正确端点/鉴权**（踩坑后确认）：`POST https://fanyi-api.baidu.com/ait/api/aiTextTranslate`，**Header `Authorization: Bearer <API_KEY>` + JSON body `{appid,from,to,q}`**，响应 `{"trans_result":[{"src","dst"}]}`。**不是** MD5 签名的通用翻译接口（`/api/trans/vip/translate`）——一开始接错了那个，报 54001 Invalid Sign。
- `.env`：`BAIDU_TRANSLATE_APPID` + **`BAIDU_TRANSLATE_API_KEY`**(Bearer token) 是有效凭证；`BAIDU_TRANSLATE_SECRET`(通用翻译密钥) 大模型用不到，保留备用。
- 新模块 **`video_pipeline/baidu_translate.py`**：`enabled()/translate(texts,loc,src_lang)`；逐条翻译保证等长对齐，源串含换行时 `\n` 重组多行 dst；**全局限速**（多线程共享 `1/QPS`，默认 QPS=10）；错误码分级（`_FATAL_CODES`→`BaiduAuthError`禁用回退；`_RETRY_CODES`退避）。语言码百度私有：`es→spa, vi→vie, ms→may, zh-Hant→cht, ja→jp`。
- 调度链（`translate_strings.py`/`translate_parallel.py`）：**百度 → Azure → DeepSeek**，非破坏；`config.py` 加 `BAIDU_TRANSLATE_*`。

### 5. 翻译跑批（精简范围：6 国新岗 + UI 新键，**不含 FR/ES 全量**）
- **正文·6 国新增能源/半导体岗**：`scripts/translate_scope.py --countries AU,CA,UK,DE,US,NZ`——从 `occupations.json` 重建 6 国源串集合，只翻 `translation_src` ∩ 该集合、且各语言尚缺的（每语言 1,284 条 × 9 = 11,556，en 已翻完）。走百度。**（会话结束时后台仍在跑，见待办 #1）**
- **UI 新键**：`scripts/translate_ui_baidu.py`——8 键(`hHeadline/hHotH/hHotB/hTk1/2/4/5/6`) × 9 语言，en 母本经百度译，**占位符完整性校验**（丢失则回退英文）。**坑**：百度繁体把半角 `{}` 转全角 `｛｝`→归一化修复；`es hTk5` 真丢了 `{n}`→回退英文；`zh-Hant hHeadline` 百度漏 `{n}`→手动用中文母本繁体版补 `AI 正在重塑全球 {n} 職業：你的工作還在安全區嗎？`。

### 6. job-risk-map 三项改动（本次用户要求）
- **宽屏**：`riskmap.ts` 画布 `1000×640 → 1600×720`；页面 `.rm` 突破 Base 的 980px 窄栏 → `width:min(94vw,1680px); margin-left:50%; transform:translateX(-50%)` 视口居中。
- **全部轮廓（含岛屿）**：重生成 **`country-outline.json`** 为**多环** `{cc:[[ [lon,lat]... ], ...]}`。脚本 **`scripts/gen_country_outline.py`**（源 Natural Earth 50m admin_0，按 ADM0_A3；每国取全部多边形外环，**剔除距主陆块中心 >30° 的远洋领地**避免水印横跨大洋——法属圭亚那/留尼汪/夏威夷/阿拉斯加被剔，塔斯马尼亚/NZ南北岛/英国各岛/西班牙加那利保留；DP 简化 tol=0.05）。环数：AU 38 / NZ 9 / CA 93 / US 20 / UK 22 / DE 5 / FR 3 / ES 12，文件 101KB。`riskmap.ts` 的 `outlineToPath` 改为**多环共享 bbox 投影**、拼多子路径。
- **深色填充**：`.rm-outline-fill` 由 `fill:var(--muted);opacity:.07` → `fill:#000;opacity:.38`（描边 opacity .14→.2）。脚注文案改「including its surrounding islands」。
- **验证**（curl，preview 截图本会话仍卡）：rm-svg viewBox=1600×720；轮廓子路径数=环数；坐标在画布内居中；无编译错误。

## 当前规模 / 状态
- 8 国 4503 职业不变。`origin/main` = `6ed7cfd7`（**本会话所有改动均未 commit 未 push**）。
- 百度翻译已入库 ~7,500+ 行（`gen_model='baidu-llm-mt'`）。

## 待办 / RESUME
1. **正文 6 国翻译收尾 + 导出**：`translate_scope.py` 后台跑到 11,556/11,556 后，跑 `export_site_data.py` 把新译文烘焙进 `occupations.json`/`translations.*.json`（导出前停预览）。若中途中断，重跑 `translate_scope.py`（幂等）补齐。
2. **FR/ES 全量翻译**（缺口大头，约 45,494 串/语言）：`translate_scope.py --countries FR,ES` 或直接 `translate_parallel`（走百度）。费用见 07-07 会话统计（含标点约 11.7M 字符×口径）。
3. **提交/推送**：本会话大量改动待 commit（建议按功能拆几个 commit）+ push main（auto 模式拦 push，需授权直推）。
4. 投票功能上线（`docs/polls-deploy.md`，agent 无法代执行）。
5. 可选：job-risk-map 微调（远洋领地阈值/深浅/CA 93 环体积）。

## 关键坑（本会话新增）
1. **百度大模型翻译 ≠ 通用翻译**：大模型走 `/ait/api/aiTextTranslate` + Bearer；通用走 `/api/trans/vip/translate` + MD5 签名。用错端点报 54001。
2. **百度繁体输出全角花括号 `｛｝`**：含占位符的模板译后须归一化回半角并校验，否则占位符失效。
3. **DP 简化闭合环会坍缩**：首尾同点导致基线退化→全点距离算 0→坍成 2 点。须在"距起点最远点"拆两段弧分别 DP（`simplify_ring`）。
4. **Natural Earth admin_0 含远洋领地**：France 含法属圭亚那、USA 含夏威夷/阿拉斯加，直接全取会撑爆 bbox；用 30° 距离过滤。
5. preview 截图工具本会话持续卡死；用 curl + python 解析核对。导出前停预览（Errno22）。auto 模式拦 push main。

> 恢复任务直接说「读取 docs/session-handoff-2026-07-08.md 继续」。
