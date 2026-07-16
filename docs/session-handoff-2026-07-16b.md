# 会话交接 · 2026-07-16b（AI 暴露度指数重算：ILO WP140 + OpenAI Eloundou 替代 Felten；treemap 铺满 1–9；全 13 国接桥）

> 接续 `docs/session-handoff-2026-07-16.md`（韩国 KECO 537 上主站）。
> 本会话把 job-treemap / 主站的 **AI 暴露度**从压缩的 4–9（LLM 主观分）**重算**为自然的 1–9，
> 改用生成式 AI 时代的两个权威源；全 13 国接上 →ISCO 桥；补文档 / 关于页 / downloads 归档 / 缓存修复。
> **全部改动未 commit**；末尾一步「treemap 重建带缓存版本号」因命令分类器临时不可用**待执行**。

---

## 一、动机

参照站 0xtreme/aus-jobs、karpathy/jobs 的 AI 暴露直方图铺满 **1–9**（用连续的 AIOE 百分位），
而本站 treemap 挤在 **4–9**——因为显示的是 **LLM 主观分 `automation_exposure`**（中心趋同偏差，几乎不低于 2.5）。
旧的 `scripts/compute_aioe.py`（Felten AIOE，2021，**前生成式 AI 时代**）也被淘汰。

## 二、新方法学（核心）

**两个源（均可自由复用，已下载归档 `downloads/ai-exposure/`）**
| 源 | 键 | 覆盖 | 分值 | 许可 |
|---|---|---|---|---|
| **ILO 工作论文 140**《Generative AI and Jobs: A Refined Global Index》(2025) | ISCO-08 四位 | 附录 Table A1 = 112 个有实质暴露的职业 | GenAI 暴露 mean 0–1 | CC BY 4.0 |
| **Eloundou《GPTs are GPTs》**(OpenAI, 2023) `data/occ_level.csv` | O*NET-SOC 六位 | ~800（连续） | 任务型 LLM 暴露 beta 0–1 | MIT |

> 两套 0–1 分实测**同尺度且高度吻合**（Data Entry 0.70/0.696；Accountants 0.51/0.54）→ 直接拼接、无需重缩放。

**算法**（每职业 → 0–100 百分位）
1. 取 0–1 原始分（ILO 优先锚高档、Eloundou 连续填充）：
   - US → Eloundou beta by SOC-6（缺失按 SOC 组均值）。
   - 其余国 → 本国码 → **ISCO-08 四位**，命中 ILO 112 用 **ILO mean**，否则经 **ESCO/O*NET 桥**（`isco4→SOC→beta`）取 **Eloundou**。
2. 原始分在**同一套全局参考分布**（Eloundou ~800 beta 经验分布）里取百分位 → `aioe_pct` 0–100（全球绝对锚定、跨国可比）。
3. treemap 颜色 `exposure = round(aioe_pct/10)`（0–10）。

**决策记录**：归一化=①**全球绝对锚定**（非各国百分位）；范围=②**全站一起切**（treemap + 主站职业页）。

## 三、新增 / 改动脚本

- `scripts/build_genai_refs.py`（新）：下载 ILO PDF（pdfplumber 提 Table A1，112 行）+ Eloundou CSV → `.codex_tmp/genai_ref.json`（ilo / soc_beta / isco_beta(434) / ref_dist）。
- `scripts/compute_ai_exposure.py`（新，取代 compute_aioe.py）：算 aioe 写回 `occupation_ai_v2`（aioe_score/aioe_pct/aioe_soc/aioe_method）。`--country` / `--dry`。含 `LLM_XWALK={FR,JP,KR}`（打 `_llmmap` 后缀）。
- `scripts/build_llm_isco_xwalk.py`（新）：LLM 把职业英文名映射到官方 ISCO-08 436 码（候选表放 system prompt 强约束 + 校验）→ `.codex_tmp/xwalk_{cc}.json`。ILO WP140 本身的做法。
- 旧 `scripts/compute_aioe.py` **保留未删**（被取代）。

## 四、各国 → ISCO/SOC 覆盖（全 13 国已接，仅 ~57 pending=US 军职 SOC55 + 边缘码）

| 方式 | 国家 | 说明 |
|---|---|---|
| 直连 | US(SOC) · IE/IT/NL(occ_code 即 ISCO) | — |
| 官方桥 | AU/NZ(ANZSCO) · DE(KldB) · UK(SOC) · CA(NOC) · **ES(INE 官方 CNO-11↔ISCO)** | ES 513 码 100% 命中，511 scored |
| **AI 映射**`_llmmap` | **FR / JP / KR** | 官方码表本环境拿不到→LLM 映射到官方 ISCO-08；JP 325/328 · KR 536/537 · FR 531/532 |

**官方桥可得性核实**：ES=INE 官方表（已用，`downloads/es/corr_cno11_ciuo08_en.xls`）；
**JP 无代码级官方 JSCO↔ISCO 表**（総務省只发原则比较 PDF，`downloads/jp/`）；
**KR KOSTAT 门户本环境不可达**（kostat.go.kr 证书=`*.narastat.kr`、narastat.kr DNS 不解析）；
**FR 无 ROME↔ISCO 直表**（官方须 ROME→ESCO→ISCO 多跳；`downloads/fr/` 有历史 ROME-V3→FAP→PCS 表可作升级路径）。
→ FR/JP/KR 走 LLM，各 downloads README 记官方源 + 阻塞 + 升级步骤。**升级**：官方表存 `.codex_tmp/xwalk_{cc}.json` 并从 `LLM_XWALK` 移除该国，重跑 compute 即自动去 `_llmmap`、前端零改动。

**分布效果**（旧→新，AU 例）：`{4:50,5:131,6:140,7:122,8:49,9:34}`（挤 4–9）→ `{1:34,2:52,…7:83,…10:4}`（铺满 0–10）。JP/KR/FR/ES 同样从压缩恢复到 0–10（浏览器已验证）。

## 五、treemap 改动（`job-treemap/`）

- `build.py`：`exposure` 优先 `aioe_pct/10`，缺失回退 LLM 分；**加 KR**（COUNTRY_META + ORDER，₩/KECO 署名）→ 13 站；生成 **`dist/about.html`**（方法学关于页，ILO/OpenAI 引文 + 许可 + 覆盖表 tag）；**缓存修复**：加 `VER=时间戳` 注入 `CONFIG.ver`。
- `template.html`：侧栏加「About & methodology →」链接（href 经 `CONFIG.aboutUrl` 按页层级注入）；**数据 fetch 加 `?v=${CONFIG.ver}`** 防浏览器缓存陈旧 JSON。
- `README.md`：加「AI 暴露度指数计算方式」章节 + 覆盖表（官方桥/AI 映射）。

## 六、主站改动（`site/`，全站切换）

- `src/lib/data.ts`：`jAioeT` 标签 `AIOE(学术)` → `GenAI · ILO/OpenAI`；注释更新（Felten→新源）；新增关于页键 **abAiExpH/abAiExpA/abAiExpB**（en + zh-CN 母本；其余 locale 回退 en，**UI 翻译 translate_ui 待补**）。
- `src/pages/[locale]/about/index.astro`：新增「How the AI Exposure Index is computed」段落。
- `src/data/occupations_v2.json`：**外科补丁**回填 aioe 四字段（避开 `export_site_data_v2` 重写 145 万翻译分片的慢 + AV 锁；aioe 在 lean 文件、不在 AI_DETAIL）。职业页浏览器验证：显示「AI Exposure Index (GenAI · ILO/OpenAI) — 86/100」。

## 七、downloads 归档（均 gitignore，见各 README）

- `downloads/ai-exposure/`：ILO WP140 PDF、Eloundou occ_level.csv、ESCO→SOC 桥 xlsx + README。
- `downloads/es/`：INE 官方 CNO-11↔ISCO 两版 .xls + README。
- `downloads/jp/`：総務省 JSCO↔ISCO 原则比较 PDF（参考，非码表）+ README。
- `downloads/fr/`：README（标注已有历史 ROME→FAP→PCS 表为升级路径 + LLM 方法）。
- `downloads/kr/README.md`：追加 crosswalk 章节（KOSTAT 阻塞 + LLM + 升级步骤）。

## 八、⚠ 未完成 / 待办

1. **treemap 重建带缓存版本号（本会话最后一步，待执行）**：缓存修复已写入 `build.py`+`template.html`（只读核对到位），但重建 `dist/` 时**命令安全分类器临时不可用**跑不了。恢复后跑：`E:\run\Python3.13\python.exe job-treemap\build.py`，验证 `dist/*/index.html` 含 `?v=` 与 `"ver":"<14位>"`。
2. **主站正式导出**：本会话用补丁改 occupations_v2.json；上线前跑一次完整 `python -m scripts.export_site_data_v2`（DB aioe 已是最新，全量导出结果一致）。
3. **UI 新键多语言翻译**：abAiExpH/A/B 及 jAioeT 现仅 en/zh-CN；跑 `translate_ui` 补其余 9 语言。
4. **FR/JP/KR 升级为官方桥**（可选）：ES 已官方；KR=KOSTAT KECO↔KSCO + KSCO↔ISCO 两跳（需浏览器人工下）；JP 无官方码表；FR=ROME→ESCO/PCS。
5. **主站 build + 部署**：本会话仅 dev(4399)/静态验证；线上 dist 未重建。
6. **部署侧缓存**：`?v=` 只解数据 JSON；`index.html` 本身若被 CDN 长缓存仍可能陈旧 → 给 `*.json`/`index.html` 设短缓存或 `no-cache`（README Nginx 示例里 `.json` 已 max-age=3600，可再调短）。
7. **全部改动未 commit**（含 07-16 待办 6 的 job-treemap 遗留改动，现已叠加）。

## 九、关键坑

1. **命令分类器临时不可用**：会话末 Bash/PowerShell 均报 `claude-opus-4-8 temporarily unavailable`，只读工具正常；写文件（Write）不受影响。
2. **ILO 只有 112 条**：WP140 只逐条公布有实质暴露的 112 个 ISCO；其余靠 Eloundou 连续填充才铺得开（纯 ILO 会底部一根大尖峰）。
3. **浏览器缓存陈旧 JSON**：treemap 刷新前直方图显旧值（1–3 空）；根因是 data JSON 被缓存，已加 `?v=构建号` 修复。
4. **KOSTAT 不可达 / JP 无官方表**：见第四节。
5. **screenshot 卡死**：本项目 preview screenshot 一贯 30s 超时 → 全程用 `javascript_tool`/`get_page_text` 验证（[[job-treemap-clone]] 已记）。
6. **静态验证服务器**：`python -m http.server` 用工具级 `run_in_background` 起（shell `&` 会随调用结束被回收）；kill 后 exit 1 属预期。

> 恢复：读本文件 + memory [[genai-exposure-pipeline]]（含全链路与升级步骤）；旧 [[aioe-crosswalk]] 为被取代的 Felten 链路。
> 关键产物：`scripts/{build_genai_refs,compute_ai_exposure,build_llm_isco_xwalk}.py`；`.codex_tmp/{genai_ref,xwalk_es,xwalk_fr,xwalk_jp,xwalk_kr}.json`（gitignore，可重建）；`downloads/{ai-exposure,es,jp,fr,kr}/`。
