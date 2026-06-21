# 会话交接 · 2026-06-20（品牌升级 AI Career Graph + 评分10分制 + AI字段铺全量 + 移民枚举0/1/2 + 新增11职业）

> 接续 `session-handoff-2026-06-19.md`（其末尾「一·补」已记录品牌/评分/AI/移民枚举的实现细节，务必一并读）。
> DB = 远程 MySQL `192.168.194.135:**13306**`，配置读 `.env`；翻译 DeepSeek（`$env:LLM_PROVIDER="deepseek"`）。
> 站点品牌 = **AI Career Graph**，域名 `https://aicareergraph.com`。

---

## ⚠️ 立即续做（RESUME HERE）

**新增的 11 个职业，翻译未跑完、尚未 export+build。** 重置前后台翻译任务(btutxuv2n)会中断，但 `translate_strings` 幂等，重跑补齐即可：

```powershell
Set-Location E:\work\career-guides-au; $env:PYTHONUTF8="1"; $env:LLM_PROVIDER="deepseek"; $py="e:/run/conda_envs/career-video/python.exe"
& $py -m scripts.translate_strings              # 补齐 9 语言（源串总数应到 14087/语言）
& $py -m scripts.export_site_data               # 导出 JSON
Set-Location E:\work\career-guides-au\site; npm run build   # 构建（约 2942 页）
```
翻译进度查询：`SELECT locale,COUNT(*) FROM translations GROUP BY locale`（截至保存时 en=14087 已完成、es=13989 进行中、其余 8 语言仍 13489 待译）。

---

## 本会话完成（2026-06-20）

### 1. 品牌升级 AI Career Graph + SEO（见 06-19 handoff「一·补 A」）
域名 aicareergraph.com、siteTitle 全语言统一、各页 SEO 标题(locale 分支)、OG/Twitter、关于页重构 6 板块、nav 内联 SVG 国旗。

### 2. 评分全面改 10 分制（见 06-19 handoff「一·补 B」+ 记忆 scoring-10-point-scale）
`occupation_ratings.stars/score` 与 `occupation_ai` 4 分均 10 分制；展示星星 `renderStars()` ÷2 半星；`migrate_score_scale_10.py` 幂等。**新增评分数据必须 10 分制**。

### 3. AI 字段铺全量（250→现 261 职业）
`scripts/gen_ai_insights.py`（DeepSeek，缺 verdict_zh|cluster 即生成；adjacent 从同国清单挑 occ_code 校验）。AI 图谱矩阵/榜单/AI 板块数据驱动，重新 export+build 自动填满。

### 4. AI 图谱页交互修复（site）
- 圆点自定义即时悬浮提示（`.matrix-tip`，对应 cluster 颜色，非浏览器 title）；
- `clampX/clampY` 把圆点夹在边框内（PAD=8），不再跑出；分隔线 `px(5.5)`。

### 5. is_migration 升级 0/1/2 枚举（见 06-19 handoff「一·补 D」）
0=非移民 / 1=可直接技术移民(189/190/491) / 2=受限(仅雇主担保/DAMA)。抓官方 **CSOL PDF**(`immi.homeaffairs.gov.au/Documents/core-sol.pdf`，456 职业，已存 `.codex_tmp/core-sol.pdf`)实证核对。前端三态标签+受限说明；`migration_friendly`/`bestMigration`/`data-pr` 全用 `===1`；md_generator 三态；关于页 AU 加 `AU_SOURCE_LINKS`(CSOL/DAMA/JSA/ABS 等)。**导出坑：`export_site_data` is_migration 必须 `int()` 不能 `bool()`**。

### 6. 评分标题信息提示 + 移民板块职业代码（site）
评分 h2 加即时 CSS `.info` 提示(Base.astro 全局，`overallTip`)；移民职业的移民板块顶部显示「提名职业代码」(`visaCode`)。

### 7. 快递司机教育路径改驾照（DB id 180）+ is_migration=0（之前会话）

### 8. 【本次重点】新增 11 个艺术/教练/营养职业
- 脚本 `scripts/seed_batch_arts_coaches.py`（`seed_occupation_v2`，**10 分制评分**，英文分类名，中性文案）。id 261-271。
- 清单与分类（CSOL 实证）：
  | occ_code | 职业 | is_migration | 分类 |
  |---|---|---|---|
  | 211411 | Painter (Visual Arts) | 0 | Creative, Media & Personal Services |
  | 211213 | Musician (Instrumental) | 0 | 同上 |
  | 211214 | Singer | 0 | 同上 |
  | 249212 | Dance Teacher (Private Tuition) 舞蹈教练 | 0 | 同上 |
  | 452111 | Fitness Instructor | 0 | 同上 |
  | **452111Y**(占位) | Yoga Instructor（anzsco 452111） | 0 | 同上 |
  | 452316 | Swimming Coach or Instructor | 0 | 同上 |
  | 452317 | Sports Coach or Instructor | **2** (在 CSOL) | 同上 |
  | 451511 | Driving Instructor 含卡车驾照教练 | 0 | 同上 |
  | 452413 | Outdoor Adventure Instructor 含滑翔伞等 | 0 | 同上 |
  | 251112 | Nutritionist | **1** (GSM/MLTSSL，非 482 CSOL) | Healthcare & Care |
- AI 字段已生成（gen_ai_insights，0 失败）。markdown 已生成（career-contents/au/ 共 257）。
- **Yoga/Fitness 同 anzsco_code 坑**：给 `md_generator.generate_md(..., occ_code=)` 与 `_fetch_occupation(..., occ_code=)` 加消歧参数；Yoga 用 `generate_md('452111', occ_code='452111Y')` 生成。
- **待办**：翻译 + export + build（见顶部 RESUME）。上线前二次核对薪资（联网估算）。

---

## 关键运维 / 坑（持续有效）
1. DB 远程 `192.168.194.135:13306`，配置读 `.env`；连不上让用户启那台机。
2. 翻译/AI 生成需 `$env:LLM_PROVIDER="deepseek"`（PowerShell 当前会话设，子进程继承；5.1 无 `-Environment`）。后台用 run_in_background 或 `Start-Process -WindowStyle Hidden`；Bash `&` 子进程会被回收。
3. PowerShell 工作目录跨调用持续：跑 `-m scripts.X` 前先 `Set-Location` 回项目根。
4. 标准重建链：`export_site_data` → `cd site; npm run build`。改 DB 文案后需 `collect_strings`→`translate_strings`→export→build 才进多语言。
5. `export_site_data`：is_migration 用 `int()`；AI 4 分与 ratings stars 在 `_i18n_fields` 已转 float。
6. 部署前把真实域名确认（astro.config 已是 aicareergraph.com），上线前核对新职业薪资。

## 当前规模
- 职业 **261**（AU 257 + CA 2 + NZ 2）；全部有 AI 数据；评分 10 分制；is_migration 0/1/2 枚举。
- 源串 14087/语言（en 已齐，其余翻译待补）。构建上次 2931 页（新增 11 职业后约 2942）。

> 恢复任务直接说「读取 docs/session-handoff-2026-06-20.md 继续」。
