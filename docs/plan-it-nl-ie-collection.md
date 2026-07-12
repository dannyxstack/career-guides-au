# 计划 · 意大利(IT)/荷兰(NL)/爱尔兰(IE) 职业数据采集

> 本会话（2026-07-12 续）确认的架构与骨架；全量生成前对照本文件。

## 已确认决策
1. **分类**：统一 **ISCO-08 4 位**（436 码）。清单 `.codex_tmp/isco08_universe.json`
   = `{isco,label_en,major,aioe_z,aioe_pct}`；标签源自 [ISCO-08 gist](https://gist.github.com/iamarsenibragimov/39b5186a782ee66cca9fb72bf535c655)，
   AIOE 来自现成 `.codex_tmp/isco4_aioe.json`（428/436 直挂，其余走前缀回退）。三国共用同一 universe。
2. **数据 = 官方优先 + 叙述兜底（分层）**：
   - 官方层：workforce_size、salaries(median/mean)、shortage、visa 框架 → Eurostat / 各国官方。
   - 叙述层：summary/education/ratings/fit/FAQ + name → DeepSeek 生成；官方缺薪资时 LLM 保守估算兜底。
   - 理由：官方统计没有 summary/教育/评分/FAQ 这类字段，纯官方无法填满职业页 schema。
3. **母本 = 中文仅内部**（复用现有管线，不改采集门控）：出 zh-CN + en 母本，中文永不对外展示；
   目标语（IT→it / NL→nl；IE 只英文）由后续翻译步骤按母本串产出。
4. **本步不接站点 locale**：it/nl 暂不进 `LOCALES/JOBS_LOCALES`/语言下拉/hreflang/UI；仅把 en + 目标语数据入库。
5. **AI 块复用**：① AIOE 由 ISCO 4 位直挂（compute_aioe 链路）；② 叙述性 ai-block 按 match_name 从 AU/CA/US/UK 池匹配复用（同 gen_fr）。
6. 三国 currency=**EUR**，occ_code_type=**ISCO08**，occ_code=ISCO 4 位。

## 官方数据源映射（待逐一验证可达性/粒度）
| 字段 | 通用(EU) | IT | NL | IE |
|---|---|---|---|---|
| 就业人数 | Eurostat `lfsa_egais`(ISCO 1位) | ISTAT | CBS StatLine | CSO PxStat |
| 薪资 median/mean | Eurostat SES `earn_ses`(按 ISCO) | ISTAT | CBS | CSO |
| 紧缺 shortage | — | Decreto Flussi 配额 | IND kennismigrant 门槛 | Critical Skills Occupations List |
| 签证/居留 | EU Blue Card | Decreto Flussi/Nulla Osta | Highly Skilled Migrant/Orientation Year | Critical Skills/General Employment Permit |

- 官方层落地格式：`.codex_tmp/official_{cc}.json` = `{isco4: {workforce_size, shortage, salaries:[{band,experience,salary_min,salary_max,salary_note}]}}`，
  薪资 median/mean 口径复用 `load_salary_median.py`。gen 脚本 `fetch_official()` 读取，官方值覆盖 LLM 值。

## 骨架现状（本会话产出）
- `.codex_tmp/isco08_universe.json` —— 436 码清单（已带标签+AIOE）。✅
- `scripts/gen_isco_occupations.py` —— 骨架，`--country IT|NL|IE`，读 universe / 连库 / 算待生成 / 国家配置已通；
  `validate/gen/save` 待从 `gen_fr_occupations` 复用接线，`fetch_official` 待接官方源。✅ 冒烟通过。

## 下一步（确认后）
1. 复用 gen_fr 的 `gen/validate/save` 接进骨架，母本 zh-CN+en，occ 字段改 ISCO08/EUR/cc。
2. 先跑 **样例**（如每国 3-5 个 ISCO）验证入库 + generate_md(en) + ai_match，人工核对。
3. 接官方层：先做一国一字段打样（如 IE 就业人数 via CSO），验证 `official_{cc}.json` 流程。
4. 全量生成 → copy_ai_blocks 补未匹配 → 翻译目标语(it/nl) → export。
5. （后续单独阶段）接 it/nl 站点 locale：LOCALES/JOBS_LOCALES/语言下拉/hreflang/UI 串翻译。

## 未决/待验证
- Eurostat SES/LFS 到 ISCO 4 位的粒度与可达性（1 位可直取，4 位多需各国源）。
- 三国 ISCO→本地紧缺清单/签证清单的对应。
- IE 是否需要爱尔兰语(ga)（默认否，只英文）。
