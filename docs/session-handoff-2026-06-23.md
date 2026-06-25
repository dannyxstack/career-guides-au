# 会话交接 · 2026-06-23（美国 + 新西兰职业全量采集完成，待 Phase 2-4）

> 接续 `docs/session-handoff-2026-06-22.md`。
> DB = 远程 MySQL `192.168.194.135:13306`，配置读 `.env`（键名 **MYSQL_HOST/PORT/USER/PASSWORD/DATABASE**，非 DB_*）；翻译/AI 生成 `$env:LLM_PROVIDER="deepseek"`。
> 站点品牌 **AI Career Graph**，域名 `https://aicareergraph.com`。Python：`e:/run/conda_envs/career-video/python.exe`。

---

## ⚠️ 立即可续做（RESUME / 待办）

1. **US Phase 2 — ai-block 复用脚本（最优先，尚未编写）**：
   - 读 `.codex_tmp/us_ai_match.json`（{us_occ_id: {country, occ_code, src_occ_id}}，~67% 命中母体），把母体的 `occupation_ai` 行 + `occupation_ai_disruptor` 链接**复制**到 US occupation_id（`adjacent` 置空；`ai_disruptors` 目录天然共享）。
   - 参考 `scripts/gen_nz_occupations.py` 里的 ai-block 复制函数（约 136 行起，NZ 是按相同 ANZSCO 从 AU 复制，US 是按 us_ai_match 映射复制）。
   - 无母体的 US 职业回退：`gen_ai_insights --country US` + `gen_ai_disruptors --country US`。
   - 决策已定：方案 **B + 匹配方式 a**（采集时 LLM 已输出最接近的现有 AU/CA 职业名，已归一化写入 us_ai_match.json）。

2. **Phase 3 — 翻译/导出/构建**（US Phase 2 完成后统一做一次）：
   `collect_strings → translate_strings --locales en →`（US/NZ 新增大量中文母本需翻 en）`export_site_data → cd site; npm run build`。
   - 导出注意：`is_migration` 用 `int()`（0/1/2 枚举）；评分/AI 分 float；slug 按 name_en 生成。

3. **Phase 4 — 前端接入 US**：`COUNTRIES`（`site/src/lib/data.ts` 第 8 行）目前 `['AU','NZ','CA']`，**需加 'US'**；并补 `COUNTRY_FLAG` 美国 SVG 国旗（带 xmlns，禁 emoji）、`COUNTRY_NAME`、currency=USD、首页国家卡。NZ 已在 COUNTRIES 内，全量后需确认前端正常。

4. **大量未提交改动**（建议 Phase 2-4 全部完成后统一提交）：
   - 本会话脚本改动：`scripts/gen_us_occupations.py`、`scripts/gen_nz_occupations.py`（visa_subclass 截断到 20）、`db/schema.sql`（两列放宽到 150）。
   - 上一会话未提交的前端三大板块全球化收敛（见 `session-handoff-2026-06-22.md`「本会话完成 1」，已 dev 实测）。
   - 数据 md：`career-contents/us/`、`career-contents/nz/`。
   - `.env`、`__pycache__`、`.codex_tmp`、`.claude` 已被 `.gitignore` 排除。

---

## 本会话完成（2026-06-23）

### 1. 美国 SOC 职业全量采集完成
- `us_done.json` **792**，DB US **792**，**0 失败**。幂等续跑（`gen_us_occupations --batch-size 50 --rest 0`，后台）多轮补齐。

### 2. 新西兰职业全量采集完成
- `nz_done.json` **256**（目标 257），**0 失败**。镜像 AU 职业、沿用 ANZSCO 码、ai-block 按相同码从 AU 复制。

### 3. 修复 3 个列长 bug（确定性，已根治）
采集时 LLM 偶发超长值 / SOC 标题天生长，触发 MySQL 1406 Data too long：
- `occupation_visa_pathways.visa_subclass` VARCHAR(20)：**脚本侧截断** `(v.get("visa_subclass") or "")[:20]`（US+NZ 两脚本，保持短码约定，完整描述在 visa_name/description）。
- `occupations.anzsco_title` VARCHAR(100)→**150**（ALTER + schema.sql 同步）。真实官方英文名，最长 SOC 标题 102 字符。
- `occupations_i18n.name` VARCHAR(100)→**150**（ALTER + schema.sql 同步）。英文 locale 存的就是 SOC 全名。

## 当前规模（DB）
- 职业：AU **257** + CA **168** + NZ **256** + US **792** = **~1473**。
- 注意：US 的 ai-block **尚未复用/生成**（待 Phase 2）；US/NZ 新增中文母本**尚未 collect/translate**（待 Phase 3）。

## 关键运维 / 坑（持续有效）
1. `.env` 键名是 **MYSQL_HOST/PORT/USER/PASSWORD/DATABASE**。表无 `country` 列？——别瞎猜列名，先 `show columns`。签证表名是 `occupation_visa_pathways`（非 occupation_visa）。
2. 翻译/AI 生成需 `$env:LLM_PROVIDER="deepseek"`。长进程连接池会坏 → 杀掉重启（幂等）。后台用 run_in_background。
3. 跑 `-m scripts.X` 前先 `Set-Location` 回项目根。
4. **后台任务输出文件是 GBK 编码**，Read/Grep 看会乱码；用 `open(path,encoding='gbk',errors='replace')` 读。
5. 失败分类：`数据不完整` / `Expecting ',' delimiter`(JSON 格式错) = 瞬时，幂等重跑可补；`1406 Data too long` = 确定性列长，须改库/脚本。
6. PowerShell 5.1 无 `&&`；Bash 工具里勿用 `@'...'@` here-string。
7. 评分 10 分制存储、展示 ÷2；is_migration 0/1/2。国旗用 data.ts 的 COUNTRY_FLAG 内联 SVG，禁 emoji。
8. dev server 由 preview MCP 起在 4399（4321 常被占用）。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-23.md 继续」。
