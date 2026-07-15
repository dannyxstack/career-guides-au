# 会话交接 · 2026-07-13c（v1 旧管线全退役 + 英文页中文残留修复 + 前端「非AU」逻辑审计）

> 接续 `docs/session-handoff-2026-07-13b.md`（英文母本 v2 已落地到「数据+前端」两层，剩收尾）。
> 本会话完成 v2 收尾的删旧件（#3/#6）、把整套 v1 zh 母本管线全退役、修复英文页 Migration/Data Source 夹中文的逻辑 bug、审计全前端同类「非AU」问题、并清理 404 与死代码。
> **分支 `main`**，本会话 5 个提交**均已 push**：`05fb1965` / `06fdb839` / `fde5a931` / `2b86f388` / `9d4ca1ec`。
> DB = 远程 MySQL（`.env` MYSQL_*）；Python = `E:\run\Python3.13\python.exe`（长任务前设 `PYTHONIOENCODING=utf-8`）。

---

## 本会话完成（按提交顺序）

### 1. 删旧件 #3 + /jobs 路由 #6（commit 05fb1965）
- **背景**：交接 b 的待办 #3「删旧件」与 #6「/jobs 路由抽验」。
- **/jobs 路由其实上一会话（2026-07-12 URL 迁移）已删**，`site/src/pages` 下无 `jobs` 目录/`[slug]` 全局路由；`jobHref()` 现返回 `/{cat}/{slug}[/{cc}]`，History API 切换脚本也在 b 的 task2 删了。故「探测 404」是预期。本次仅清 4 处陈旧注释（JobDetail.astro、riskmap.ts、ticker.ts、data.ts）。
- **删旧数据**（前端只读 *_v2，无 live import，已验证）：`site/src/data/{occupations.json,categories.json,translations/,occ-detail/}`。
- **删旧脚本**（有 v2 替代）：`collect_strings`/`translate_strings`/`export_site_data`/`_i18n_fields`/`_seed_helper`；en 质检脚本 `audit_en_quality`/`en_rule_probe`/`judge_highvalue_fields`/`run_en_pass`/`fix_en_residual`/`bench_gemma_retrans`；10 个旧分国生成器 `gen_{au,ca,ca2,de,es,fr,isco,nz,uk,us}_occupations`（保留 gen_intl_v2、gen_country_outline/gen_outline_paths）。合计删 115 文件。
- **3 张空死表改名**（用户选：改名不 DROP，可逆）：`occupation_{education,salaries,suitability}_i18n` → `deprecated_*`（均为空表）。

### 2. v1 zh 母本管线全退役（commit 06fdb839）
- **决策**：用户选「全退役（脚本删 + 表改名）」。确认 go-forward v2 管线（`gen_intl_v2`/`_seed_helper_v2` → *_v2 表 + 共享 `occupations`；`export_site_data_v2` 只读 *_v2 + 复用 `occupation_invitation_scores`）**不读任何 v1 文本表**，故整套 v1 apparatus 是自循环死件（v1 表只被 v1 脚本引用）。
- **删 224 个脚本**：203 个旧 per-occupation/batch zh `seed_*.py` + 21 个 v1 helper（`fix_desinify/sinicized/untranslated/visa_terminology`、`translate_parallel/scope/salary_labels/fr_baidu`、`add_sources_strings`、`backfill_fields`、`migrate_queryability/score_scale_10/ai_graph/ai_insights`、`copy_ai_blocks`、`gen_ai_insights/disruptors`、`load_salary_median`、`fetch_official_nl`、`fill_isco_salary_bands`、`verify_electrician`）。`scripts/` 从 250+ → **30**。
- **保留**（go-forward/共享）：全部 v2 脚本、`compute_aioe`、`translate_ui`/`translate_ui_baidu`、`gen_*outline*`、复用表 schema/seeder（`seed_hot_occupations_schema`/`seed_polls_schema`/`seed_invitation_scores`）、`migrate_{currency,public_servant,invitation_scores}`、`seed_hot_occupations`（**已重指向 occupations_v2.json**，因其产物 hot_occupations.json 仍被 Home.astro 用）。
- **14 张 v1 表改名 `deprecated_`**（不 DROP，可逆）：其中 12 张成功（occupations_i18n / occupation_{ai,education,qualifications,salaries,suitability,ratings,faqs} / ai_disruptors / occupation_ai_disruptor / translation_src / translations，保留 220 万+ 行），`faqs_i18n`、`occupation_visa` 裸名不存在跳过。
- **决策反转（已按全退役执行）**：`gen_ai_insights`/`gen_ai_disruptors` 首轮曾选保留，但它们只写已弃用的 v1 `occupation_ai`/`ai_disruptors`，本轮纳入删除（v2 的 AI 块由 gen_intl_v2 生成）。若日后要向 v2 灌 AI 数据需改写成写 *_v2 表（git 可恢复）。

### 3. occupation_visa_pathways 退役（commit fde5a931）
- **用户提问引出的遗漏**：v1 签证表真名是 `occupation_visa_pathways`（非首轮搜的裸名 `occupation_visa`），与 `occupation_visa_v2` 同构（id/occupation_id/visa_subclass/visa_name/description/sort_order），已迁移 16213→16223 行，首轮改名漏掉。
- 它唯一区别于其它 v1 表：仍被保留的 `seed_invitation_scores.py:42` 读取（`SELECT DISTINCT visa_subclass`，去填**复用活表** occupation_invitation_scores）。
- **处理（用户选：重指向后改名退役）**：把 seed_invitation_scores 改读 `occupation_visa_v2`（安全性核对：脚本只用真实子类码 190/491，两表完全一致；438 处差异全是被误当 subclass 存的描述性标签如「公民要求」→「Citizen requirement」，此处不用），更新 migrate_invitation_scores 注释，再改名 `deprecated_occupation_visa_pathways`（16213 行保留）。至此 v1 表实退 **13 张**。

### 4. 修复英文页 Migration/Data Source 夹中文（commit 2b86f388）
- **现象**：部分职业英文页的 Migration 提示与 Data Source 段落显示中文。
- **根因**（非数据层——导出 JSON 零 CJK）：`data.ts` 两个硬编码文案函数用了 `hasTr(v['zh-CN'],locale) ? tr(v['zh-CN'],locale) : v.en` 的 v1 写法：
  - `hasTr(s,'en')` 第 90 行**无条件返回 true**；
  - `tr(s,'en')` 第 4 行**原样返回入参**（「英文为母本」）；
  - → 英文 locale 命中 `tr(中文,'en')`，把 zh-CN 母本直接吐到英文页。
  - 命中函数：`sourcesBody`（801，非 AU 全部国家的 Data Source）+ `migText`（809，US/NZ/CA 的 migRestrictedNote/nonMigVisa/restrictedOcc）。
- **修复**：英文 locale 直返 `v.en`；其余语言改用英文母本 `v.en` 作 v2 TM 键（这些硬编码串本不在 TM，回退英文，与现状一致）。**英文文案本就存在且正确，无需 DeepSeek 翻译**。
- **验证**：dev 实测 `/agriculture-environment/farm-labor-contractors/US`（英文）Migration 提示与 Data sources 段均为英文。

### 5. 前端「非AU」逻辑审计 + 404/死代码修复（commit 9d4ca1ec）
- **审计结论**：`hasTr()/tr()` 坏模式全前端仅 2 处（即上条已修的 sourcesBody/migText），**无第三处**。其余本地化取值（`countryName`/`countryTitleName`/`disType`/`disLevel`/`dimLabel`/PollBlock UI/`locText`）都是 `[locale] || ['en']` 直选，对 en 必得英文，安全；`tr(o.*_zh)`/`tr(i18n['zh-CN'])` 操作的是 v2 里装英文的旧键（JSON 扫描 0 CJK），安全；`[country]/[locale]/index.astro:39` 的中文 meta 标题已被 `locale==='zh-CN' ?` 正确门控。
- **发现两处独立问题并修复**：
  - **404.astro**：原 `Base locale="zh-CN"` + 中英双语，任何未命中 URL（含英文默认站）都渲染中文。改 `locale="en"` + 纯英文文案。dev 实测 `fetch('/不存在')` 返回 status 404、`<html lang="en">`、H1「Page not found」、CTA 全英文（页面残留中文仅来自导航栏语言切换下拉的各语言本族名，属设计）。
  - **AU_SOURCE_LINKS**（data.ts:54）：导出但全仓无消费的死代码（带 zh-CN 母本映射），已删。

---

## 待办 / 下一步
1. **重新 build + 部署**：本会话第 4、5 项是源码修复，已 push main，但**线上 dist 未重建**，需 build（约 5 分钟 / 16GB heap）+ 部署后才生效。build 命令 `npm --prefix site run build`（已含 `--max-old-space-size=16384`）；部署见 `docs/deploy-dist-over-ssh.md` + `scripts/deploy_dist.{ps1,sh}`（这 4 个未跟踪文件仍未提交）。
2. **en→X 补齐**（交接 b 遗留）：`translation_src_v2` ~7.5 万源串缺部分语言译文；引擎待定（DeepSeek / 本地 gemma）。
3. **可选增强**：`migText`/`sourcesBody` 对 ja/de/es 等非中英语言现回退英文（这些硬编码串不在 v2 TM）。若要本地化需纳入 v2 翻译管线 + DeepSeek 补译。
4. **遗留孤儿/失效脚本**（git 可恢复，不影响 live）：
   - `migrate_to_v2.py` 现已失效（import 已删的 `_i18n_fields` + 引用已改名表），是已跑完的一次性迁移，不再运行。
   - 4 个未跟踪文件未提交：`docs/deploy-dist-over-ssh.md`、`docs/session-handoff-2026-07-13b.md`、`scripts/deploy_dist.{ps1,sh}`（外加本文件）。
5. **可选**：`inlineStylesheets:'never'` 站点级决定**保持不动**（大型多页站 CSS 共享缓存更优；回退到 'auto' 会重引入桩页 CSS 内联 + 逐页重复）。

## 关键坑（本会话）
1. 删除大批脚本前用**保守规则 + 显式 KEEP 白名单**程序化生成清单，并检查「保留脚本是否 import 待删脚本」，避免误删 go-forward。
2. `[一-鿿]` 在 Windows Git Bash 里按**字节**匹配，会把 `→ · 🌙 ✓` 等所有非 ASCII 误报为 CJK；真 CJK 扫描须用 **Python（真 Unicode 正则）**。
3. Astro dev 对未命中路由返回 HTTP 404，浏览器工具判为「导航失败」不渲染 `404.astro`；验证自定义 404 用 `javascript_tool` 的 `fetch()` 抓 HTML 绕开。
4. `git push origin main` 曾撞 2 分钟超时但 ref 实际已更新（`git ls-remote` 核实）；后续用 `timeout 300` 均正常。
5. 远程表改名前必须确认 live 重建路径（`export_site_data_v2`）不读该表；改名脚本先查存在性/目标不存在/行数再 RENAME，幂等。

## 本会话改动文件（除删除外）
- 改：`site/src/lib/data.ts`（sourcesBody/migText 逻辑修复 + 删 AU_SOURCE_LINKS + 注释）、`site/src/pages/404.astro`（英文单语）、`site/src/components/{JobDetail,riskmap→lib/riskmap}.astro/ts`、`site/src/lib/ticker.ts`、`scripts/seed_hot_occupations.py`（重指向 v2）、`scripts/seed_invitation_scores.py`（读 occupation_visa_v2）、`scripts/migrate_invitation_scores.py`（注释）
- 删：见上（115 + 224 文件）；DB 改名 13 张 v1 表 + 3 张空死表 → `deprecated_*`

> 恢复：读本文件 + memory [[english-master-v2-pipeline]] [[i18n-translation-pipeline]]。v1 已全退役、英文页中文残留已修（待 build 上线）。
