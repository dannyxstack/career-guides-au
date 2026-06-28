# 会话交接 · 2026-06-29（Azure 翻译后端、9 语言译完、translations 按语言拆分、货币符号+跨国移民链接、德语全量、法国 ROME 532 职业接入并上线）

> 接续 `docs/session-handoff-2026-06-26.md`。
> DB = 远程 MySQL `192.168.194.135:13306`，配置读 `.env`（键名 MYSQL_HOST/PORT/USER/PASSWORD/DATABASE；表 `occupations`，国家列 `country_code`）。
> **AI 生成/翻译回退必须 `LLM_PROVIDER=deepseek`**。长 Python 任务前加 `PYTHONIOENCODING=utf-8`。Python：`e:/run/conda_envs/career-video/python.exe`。
> 生产：每 5 分钟 `git pull`(main) + `npm run build`；`site/dist/` 不入库；改动须合并 main 才上线。

---

## ⚠️ 立即可续做（待办 / RESUME）

### 1. 德语已全量翻译但**未接入站点**（follow-up）
- `translations.de.json` 已导出入库（commit `7b7a6c8e`），但 `data.ts` **没 import**，`Locale` 类型/`LOCALES` 也没加 `'de'`。
- 接线：`data.ts` 加 `import trDe from '../data/translations.de.json'`、`Locale` 加 `'de'`、`LOCALES` 加 `'de'`、`TM_BY_LOCALE` 加 `de`。然后 export→build→push。UI 文案会回退英文（同其它非 en/zh locale）。

### 2. 法国仅 **EN + ZH**，其余 8 语言未翻
- 按用户要求只生成中英。若要多语言：FR 源串已在 `translation_src`（collect_strings 已采，总 180,637），跑 `translate_parallel --workers 20 --batch 40`（Azure 优先）补其余 locale → export → build。

### 3. 法国 3 个职业无 disruptor（真实"无有效 AI 工具"，正常，无需处理）

---

## 本会话完成（2026-06-29）

### 1. Azure Translator 翻译后端（Azure 优先 + DeepSeek 回退）
- 新 `video_pipeline/azure_translate.py`：批量 MT，源固定 `zh-Hans`；**401(凭据无效)/403(配额)都抛 `AzureQuotaExhausted` → 禁用 Azure + 回退 DeepSeek**；429 退避重试；`LOCALE_TO_AZURE` 含 de。
- 入口 `scripts/translate_strings.py::translate_batch`：Azure 优先，失败落 `llm.complete_json`（须 deepseek）。`.env` 有 `AZURE_TRANSLATOR_KEY/REGION(australiaeast)/ENDPOINT`。
- **坑**：Azure key 曾被禁用返 401（资源停用，非换 key 能解；后恢复）；config 读 .env，全 region 401 = 资源/订阅级问题。

### 2. 9 语言翻译全部译完
- en/es/pt/vi/th/ms/id/zh-Hant/ja 各 156,038（100%）。zh-CN 是源（不翻）。

### 3. translations.json 按语言拆分（GitHub 100MB 限）
- 单文件 9 语言达 195MB 超限。`export_site_data.py` 改为按 locale 写 `translations.<locale>.json`（各 24-51MB）。`data.ts` 改为 import 各分文件 + `TM_BY_LOCALE` + `hasTr()`。

### 4. 货币符号 + 跨国移民链接
- `CURRENCY_SYMBOL`：UK=£、DE/FR=€、其余=$；`money(v, country)` 各调用点传国家。
- 职业页 Migration 板块标题加目标国家（"Migration (to United States)"）、`id="migration"` 锚点、末尾"移民到其它国家"链接（`sameOccAbroad` 按规范化英文名跨国匹配，带 `#migration`）。

### 5. 德语全量翻译（Azure）
- 156,038 全部 Azure 译完（零 401/回退）。导出 `translations.de.json`。

### 6. 法国 ROME 532 职业采集 + 接入 + 上线
- 清单 `.codex_tmp/soc_fr.json`：ROME 532 fiches métiers（源 labonneboite rome_labels.csv，`rome_id|rome_label`，14 领域）。
- 新 `scripts/gen_fr_occupations.py`（克隆 gen_de）：FR/ROME/EUR/法国签证（Carte bleue UE/Passeport Talent/Salarié/reconnaissance），DeepSeek 产 zh-CN+en 母本。幂等 `fr_done.json`，AI 母体匹配 `fr_ai_match.json`。
- **532/532** 入库；AI insights 532/532；ai-block 复用 217（copy_ai_blocks）+ 生成；disruptors 529/532。
- FR 源串经 collect_strings 入 TM，`translate --locales en`（Azure）补英文 → 站点英文页正常（name/summary 走 TM，非 i18n.en）。
- `data.ts` 接线 FR：COUNTRIES/COUNTRY_NAME/COUNTRY_TITLE_ZH/COUNTRY_FLAG(三色旗 SVG)/CURRENCY(EUR)/CURRENCY_SYMBOL(€)/SOURCES_BODY/MIG_TEXT；about 页加 ROME。

### 7. 构建内存修复（**生产关键**）
- 页面增至 **39,283**，Node 默认 ~4GB 堆 OOM。`site/package.json` 的 build 改为 `node --max-old-space-size=8192 ./node_modules/astro/astro.js build`（shell 无关，Win/Linux 通用）。

## 当前规模
AU 520 + CA 540 + NZ 519 + UK 368 + DE 642 + US 792 + **FR 532** = **3913 职业**（构建 39,283 页 0 错误）。

## Git（已 push main）
- HEAD `7b7a6c8e`。关键 commit：`6568f14c` 法国接入+构建堆修复 → `7b7a6c8e` 德语 locale 映射+translations.de.json。
- 更早本会话：Azure 后端 `57d6cc64`、translations.en split `1487b7cb`/`aab16058`、货币+移民链接 `00e63843`、401 回退 `9956a0b3`。

## 关键运维 / 坑（持续有效）
1. 翻译 Azure 优先、配额/401 自动回退 DeepSeek；回退须 `LLM_PROVIDER=deepseek`。
2. 站点英文/各语言**走 TM**（`tr(zh,locale)`），不读 `i18n.en`——新国家必须 collect_strings + translate 才有非中文显示。
3. `npm run build` 已内置 8GB 堆；页面再增长可调高。
4. translations 单文件超 100MB 会被 GitHub 拒——已按 locale 拆分。
5. 评分 10 分制÷2 展示；is_migration 0/1/2；国旗内联 SVG 禁 emoji；URL 国家码大写。
6. gen_ai_disruptors 必须 `--rest 0`；compute_aioe 对无 occupation_ai 行是空操作（先 insights）。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-29.md 继续」。
