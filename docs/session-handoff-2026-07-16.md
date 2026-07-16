# 会话交接 · 2026-07-16（韩国 KECO 537 职业上主站 + JP/KR risk-map 轮廓 + export 抗文件锁）

> 接续 `docs/session-handoff-2026-07-15.md`（JP 上主站、outlook 采集入库、job-treemap outlook+exposure）。
> 本会话把**韩国从零采集到上站**（方案 A，同日本），并补了 JP/KR 地图轮廓、修了 export 的 Windows 文件锁坑。
> **3 个 commit 已 push 到 main**（`4c046feb` / `2e670cbc` / `9e8ecbbb`，HEAD=`9e8ecbbb`）。
> 环境：DB=远程 MySQL；DeepSeek 直连（key 在 env）；长任务前 `set PYTHONIOENCODING=utf-8`。

---

## 一、韩国数据源检索 + 下载（`downloads/kr/`，已 gitignore）

主线分类走 **KECO（한국고용직업분류，就业职业分类）**——WorkNet/KNOW/한국직업전망 共用的 **537 세세분류职业**，是本站对齐锚点（非 KSCO 统计标准 1231）。

**已下载**（data.go.kr / 한국고용정보원 KEIS，全 **CP949** 编码，见 `downloads/kr/README.md`）：
| 文件 | 数据集 | 内容 |
|---|---|---|
| `keco_occupation_detailed_classification.csv` | 15119096 | KECO 537 职业（5 级码 + 名）→ **universe 来源** |
| `keco_occupation_mid_classification.csv` | 15119096 | 35 中类名 |
| `worknet_jobcode_20230825.csv` | 15120487 | WorkNet 직종코드 |
| `worknet_outlook_edu/worknet_job_outlook_text.csv` | 15119098 | 职业展望**叙述文本**（定性） |
| `worknet_outlook_edu/worknet_education_major_distribution.csv` | 15119098 | 教育/学历/专业分布 |
| `worknet_outlook_edu/know_similar_job_names.csv` | 15119098 | 相似/别名 |
| `know_2019/*` | 15114089 | KNOW 2019 재직자조사微数据（性格/知识，⚠仅学术用途） |

**未取（门户限制，README 记步骤）**：① `한국직업전망 일자리전망 통합本`(15140284，537 职业×10 年**定量**展望+5 档) 需**登录+신청审批**；② `KSCO` 标准分类(통계청门户 JS+证书 SAN 不匹配)需浏览器手动下。→ 用户选**先用现有数据（KECO 清单）**推进。

## 二、韩国职业入库（方案 A，同日本 `gen_jp_v2`）

用户在岔口选 **B·日本同款完整生成**（LLM 造富字段，页面同档完整；非只落原始清单）。

- **universe**：`.codex_tmp/keco_universe.json`（537 条 = keco 5位码 + title_ko + major/mid_name；10 大분류名用 KECO 2018 官方名，已对照 mid 文件校验）。由 `keco_occupation_detailed_classification.csv` 生成（gitignore，脚本可重建）。
- **生成器 `scripts/gen_kr_v2.py`**（复制 gen_jp_v2 改韩国）：DeepSeek 以韩国劳动/签证专家视角**韩文撰写**全字段（summary/11 维评分/薪资 KRW/签证 E-7·E-9·F-2·F-5/AI 暴露块，category 用 11 英文枚举）→ **韩译英**存英文母本 → 原生韩文按叶子对齐挂 `translations_v2` 的 `ko`（键=sha1(英文)）。`occ_code_type=KECO`, `country_code=KR`, `currency=KRW`, `aioe_method=llm_kr`。DEC_MAX clamp 99999999。
- **跑批**：试跑 2 条验证全链路（Stenographer→속기사，薪资/评分/AI/ko 全齐）→ 后台 resume 循环 wrapper 跑全量。**坑：`api.deepseek.com` DNS 间歇解析失败**，首轮 58 条失败 48（瞬时），靠 resume（按 `occupations.country_code='KR'` 跳已完成）多轮 mop-up。**最终 537/537 全入库，零失败**。
- **接站**（`site/src/lib/data.ts`）：COUNTRIES 末加 `'KR'`；CURRENCY `KR:'KRW'`；COUNTRY_NAME/TITLE_ZH `韩国/South Korea`；CURRENCY_SYMBOL 补 `KR:'₩'` + **顺带补原缺的 `JP:'¥'`**；COUNTRY_FLAG 加**太极旗内联 SVG**（红蓝阴阳+四卦角，sharp 渲染验证正确，遵 [[flag-rendering-rule]]）。
- export 不按国过滤，DB 有 KR 即自动出：`export_site_data_v2` → `occupations_v2.json` 含 537 KR + 新 `occ-detail-v2/KR.json`。dev 4321 验证：`/KR/en/` **555 卡**、详情页 ₩ 富字段、`/KR/en/job-risk-map/` 537。

## 三、修 export 的 Windows 文件锁坑（重要）

**现象**：重导出时 `PermissionError: [WinError 5] 拒绝访问` 反复命中 `translations-v2/*.json` 大分片，且 export 的「先全删再重写」逻辑中途崩溃 → **渐进删空 en/de/es/fr/id 等 locale 分片**（影响这些语言全站，不止 KR）。
**根因**：Windows Defender 实时扫描锁住**刚写出的大 JSON**（如 es.7 5.8MB）数秒，紧接的 remove/open 撞锁。（初判是 dev server，kill 后仍复现，实为 AV。）
**修复**：`scripts/export_site_data_v2.py` 给分片删/写加 `_retry_io`（退避重试 6×0.5~3s + 容忍删不掉的，文件名 `{loc}.{i}.json` 确定，写阶段覆盖）。重导出 **13 locale×8 分片全恢复**（`en`/`nl` 本就无分片=英文母本直读）。
**运维**：导出前最好停 dev(port 4321) 或靠重试兜。

## 四、₩0 薪资补正 + 教育费说明

- 扫 KR：**实际薪资 ₩0 仅 1 条**（Singer 入门 min=0）→ 补为 **₩12,000,000**（<该档 max 3000万）。清零。
- 页面常见 `₩0` 实为**教育费**（285 条），但绝大多是**合法免费**（note 证实：国家全额资助/义务教育/边培训边领薪/无学历要求，229 条 `0~0`；56 条 `0~X`）。属费用非薪资，伪造会与 note 冲突，**未动**。若要页面显示「Free」需模板层改（影响所有国家，待定）。

## 五、JP/KR risk-map 地图轮廓

交接 07-15 遗留：JP risk-map 无轮廓、页脚文案「outline of Japan」不符。本会话补 JP+KR：
- `scripts/gen_country_outline.py` 的 A3 加 `"JPN":"JP","KOR":"KR"`。
- 下 Natural Earth 50m/110m admin_0 GeoJSON（`.codex_tmp`，gitignore），写脚本**只提取 JP/KR 的环**（复用 gco 的 polygons_of/simplify_ring/MAX_DEG 剔远洋领地）并用 `gop.country_path` 投影，**外科式并进** `country-outline.json` + `outline-paths.json`（**不动既有 11 国与 WORLD**，避免 NE 版本差异改动他国）。
- sharp 渲染验证：日本（本州/北海道/九州四国）、韩国（半岛+南部离岛+济州）形状正确。页面验证：JP path 4841 字符、KR 1370，`rm-land` 层就位。

## 六、本会话 commit（已 push main，HEAD=9e8ecbbb）

```
9e8ecbbb feat(risk-map): add JP & KR country outlines to job-risk-map background
2e670cbc fix(export): retry-tolerant translation-shard IO for Windows AV file locks
4c046feb feat(kr): collect South Korea (KECO) occupations and enable KR in site
```
（`downloads/kr`、`.codex_tmp/*`、`scripts/_*.log` 均 gitignore；临时 wrapper `_run_kr_until_done.sh` 已删。）

## 待办 / 下一步

1. **韩国其余 9 语言翻译（未做）**：现只有英文母本 + 原生韩文(ko)。跑 `translate_v2 --locales zh-CN,zh-Hant,es,pt,vi,th,ms,id,ja,de,it,nl`（去华人化按 [[i18n-translation-pipeline]]）→ 再 export。KR UI 层（locale 下拉）若需韩语界面另配。
2. **韩国 outlook 上前端（可选）**：现库内无 KR outlook 定量数据。可① 浏览器登录 data.go.kr 申请 15140284（537×10 年+5 档）→ `load_outlook.py` 加 KECO parser；或② 先用已下载的 `worknet_job_outlook_text.csv` 叙述文本做定性展示。
3. **KSCO（可选）**：如需与国际 ISCO 对齐再浏览器手动下（1231 职业）。
4. **主站上线（未做）**：本会话只在 dev(4321) 验证；上线需 `npm --prefix site run build` + 部署（线上 dist 未重建）。
5. **教育费 ₩0 显示（可选）**：模板把 0 费用渲染成「Free/免费」（影响所有国家）。
6. **job-treemap 遗留改动（承 07-15 待办 7，仍未 commit）**：`job-treemap/build.py`(outlook 折线+舍入) + `job-treemap/template.html` + `docs/session-handoff-2026-07-15.md`——**与韩国无关，本会话有意未扫入 KR 的 push**，待单独处理。

## 关键坑（本会话）

1. **DeepSeek DNS 间歇失败**：`api.deepseek.com` getaddrinfo 失败成批出现；gen_kr_v2 内建 resume（跳 DB 已有 KR），多轮重跑即补齐。
2. **Windows Defender 锁大 JSON**：export 分片删/写撞 WinError 5，已加重试；导出前最好停 dev。
3. **CP949 编码**：韩国政府 CSV 全 EUC-KR/CP949，读取须 `encoding='cp949'`。
4. **Windows Python 看不到 MSYS `/tmp`**：curl 写 `/tmp/x` 后 Python 读不到；跨 bash/python 传文件用 scratchpad 或 grep(MSYS 工具)验证。
5. **NE 版本差异**：outline 用外科式只加 JP/KR、不重生成他国，避免下载的 NE 版本与原始不一致改动既有轮廓。

> 恢复：读本文件 + memory [[korea-collection]] [[japan-collection]] [[flag-rendering-rule]] [[i18n-translation-pipeline]]。韩国数据在 `downloads/kr`(gitignore)，生成器 `scripts/gen_kr_v2.py`（universe `.codex_tmp/keco_universe.json` 可由 CSV 重建），537 职业已入库上站(KR tab)；risk-map JP/KR 轮廓已补；export 已抗文件锁。3 commit 已 push main。
