# 会话交接 · 2026-07-13（英文母本质检 + 全量 zh→en 补齐/修复）

> 接续 `docs/session-handoff-2026-07-12c.md`。主题：为"以英文为翻译锚点/母本"做准备——把英文源串补全并质检修复。
> DB = 远程 MySQL（`.env`：MYSQL_*；TM 表 `translation_src` + `translations`）。
> LLM：翻译/质检用 **DeepSeek**（`.env` DEEPSEEK_API_KEY，OpenAI 兼容）；本地 **Ollama gemma3:12b**（`localhost:11434/v1`）做过基准与探路。

---

## 背景与思路演进
- 现状：TM 以**简体中文为母本**，`src_hash=sha1(中文)`，英文只是众多译文之一（`translate_strings.py` 各语种从中文直译）。
- 用户担忧：中文母本→远距离语种有**语义损失**（领域术语英文原生 + zh→欧洲语是远语对）。
- 定调路线：**先把英文补全+质检修好，作为将来其余 11 语种的锚点**；en→其他语言（145.8 万条）**降优先级推迟**。

## 本会话完成（全部已落库到远程 TM）

### 1. 英文质量抽样质检 ✅ → 规则表
- `scripts/audit_en_quality.py`：分层抽 1 万（A 数值层含「万」/区间 + B 通用层）→ DeepSeek judge，类别枚举映射"系统性 vs 语义"。
- 结论（剔除 judge_error）：A 层 OK 87.5%/系统性 7.2%/语义 3.2%；B 层 OK 91.7%/系统性 2.8%/**语义 2.1%**。
- `scripts/en_rule_probe.py`：候选检测器跑**全量 202,834** 英文实测命中；**修复规则表** → `docs/en-fix-rules-draft.md`。
  - 关键规则：R1 cjk 残留(157)/R2c 万→thousand(20)/R2b 万因子丢(180)/R2a 万筛查(3,103)/R5 senior models(26)/R6 学费 pay(280)；**R3 货币缺失撤销**（补拼写币种后仅 4，非真问题）。

### 2. 高价值字段全量 judge ✅
- `scripts/judge_highvalue_fields.py`：DeepSeek 全判 faq_a/visa_desc/suitability 既有英文 **44,713 条**（拆单条重试，judge_error 仅 68）。
- 结果：faq_a OK 85.5%、visa_desc 86.7%、suitability 94.6%；捞出 **3,156 条**待重译（含 1,288 纯语义错，集中在移民术语：人才护照/劳工证/排期 等）→ `.codex_tmp/judge_highvalue_flagged.json`。

### 3. DeepSeek zh→en 合并 pass ✅（写库）
- `scripts/run_en_pass.py`：补缺 **58,449** + 修规则错 ∪ 重译判分命中（去重 6,003）= **64,452 条**，写 `translations(locale='en')` `ON DUPLICATE KEY UPDATE`，`gen_model=deepseek-chat`。
- 跑完 64,429 条 / ~30min / ~36 串/秒。**英文源现已 0 缺口**。
- 幂等断点：`.codex_tmp/en_pass_done.txt`；20% 里程碑打日志。

### 4. 残留定向修复 ✅
- `scripts/fix_en_residual.py`：本地简查新英文残留 363（cjk131/wan_drop200/wan_thousand16/pay16）→ 加固 prompt 重译 → cjk 归零（4 条顽固签证句用术语表单条精修）。
- **真缺陷已归零**；剩 ~58 为检测器假阳（wan_drop/pay，译文正确）。

### 5. 本地 gemma 基准（探路，非主线）
- `scripts/bench_gemma_retrans.py`：gemma3:12b zh→en 重译 300 条，DeepSeek 判 **OK 95.7%**（多条被判错实为 DeepSeek 假阳）；系统性错误 R5/R6 100% 修净，「万」处理良好。
- **gemma 吞吐实测 ~0.25 串/秒**（单卡瓶颈，大 batch 会崩），AI-block 27,473 条若用 gemma 约 30h → 本会话最终**全走 DeepSeek**。

## 待办 / 下一步
1. **母本翻转决策（用户未定）**：
   - 含义①：只要其他语种质量 → 翻译时用**英文桥**（双语 prompt 参考英文），**不动架构**，零工程。已验证能修「万」。
   - 含义②：**英文优先架构/SEO** → 运行时 pivot 翻转（TM 主键/occupations.json 基文/data.ts `tr()` 改英文；**DB 不重写、seed 不动**）。评估 **~4–5 天工程、API≈0**；坑：training 英文派生 + 英文串碰撞 + data.ts 238 处。
   - 含义③（重写 228 seed + `*_zh` 列）不推荐。
   - **关键**：翻转 ≠ 质量提升；其他语种质量收益仍需从干净英文**重译**（推迟的 145.8 万条大活）。
2. **en→其他 11 语种翻译**（145.8 万条，推迟）：引擎待定（本地 gemma 免费但慢 ~周级 / DeepSeek 小钱快）。
3. 上上会话遗留：nginx 301 部署、百度充值（可改 DeepSeek）。

## 关键坑（本会话）
1. pymysql 的 `%` 需转义 `%%`（LIKE '%万%'）；`long` 是保留字做别名会报错。
2. DeepSeek/gemma 批判易 len-mismatch（丢/并条）→ 必须**拆单条重试**兜底，否则整批丢。
3. gemma 单卡吞吐 ~0.25 串/秒且**大 batch(≥12)会丢条**，可靠 batch 6–8。
4. 检测器假阳：wan_drop（裸数字匹配）、pay（发薪 vs 学费）、cjk 对 CSOL 签证句顽固——需语义/术语表辅助。
5. 长任务用 PowerShell `Start-Process` 独立进程；Bash 后台会被 harness 回收（见 [[i18n-translation-pipeline]] 运维坑）。

## 本会话新增脚本
`scripts/{audit_en_quality,en_rule_probe,judge_highvalue_fields,run_en_pass,fix_en_residual,bench_gemma_retrans}.py` + `docs/en-fix-rules-draft.md`。

> 恢复：读本文件 + memory [[i18n-translation-pipeline]]。英文源已定稿，下一步多为母本翻转（等用户定①/②）或启动 en→X 翻译。
