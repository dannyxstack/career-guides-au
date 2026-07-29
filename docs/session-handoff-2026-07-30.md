# 会话交接 2026-07-30（职业 slug 去重 方案 C：C1 ISCO canonical + C3 n.e.c. 降权）

承接 `docs/occupation-dedup-governance-2026-07-29.md`（去重治理报告，含方案 A/B/C）。
用户选**方案 C**，本次决策：slug/URL 用**单数**（`name_en`/标题/AI 文案/FAQ 保持自然语言复数）、
dedup **落地 export 管线**、本次做 **C1+C3**（C2 非 ISCO 国启发式后置）。

---

## 关键发现（让 C 比报告更省事）

- **36/46 国已对齐同一套 ISCO-08 四位码** → ISCO 码本身就是 canonical 概念主键，跨国合并**无损**。
- 问题只是同一码在不同国被存成单/复数等变体：**436 码 → 1084 slug**。
- 真正需要启发式的是 10 个非 ISCO 国（AU/NZ=ANZSCO、UK/US=SOC、CA=NOC、DE=KldB、
  ES=CNO、FR=ROME、IN=NCO2015、JP=JSCO、KR=KECO）= **C2，后置**。

---

## C1 — ISCO 跨国 canonical slug ✅

- 新增共享模块 `scripts/dedup_slug.py`（export 与将来的诊断共用，单一来源）：
  - `build_canonical_map(records)`：每个 ISCO 码取**出现最多的英文名** → `slugify` → **确定性单数化** = canonical。
  - 单数化 `singular_slug`/`singularize_token`：逐词剥复数（-ies→y、-sses/-shes/…→ 去 es、-s 去尾），
    但含 **KEEP 白名单**保留领域/集合名词复数：`forces/electronics/communications/sports/athletics/
    economics/…/goods/sales/news/series/species`（**刻意不含 mechanics**，机械师应 →mechanic）。
- `scripts/export_site_data_v2.py`：**按 occ_code 归一**（不是按 slug！），每条 ISCO 记录
  `slug := code_canon[occ_code]`。为何按码：少数记录借用了**邻近码的 nec-slug**
  （如 14 条 `2512 软件开发` 记录被存成 `2519 …nec` slug），按 slug 归一会与 2519 的
  canonical 撞车；按码归一彻底消除。在建 adjacent/also 引用**前**做，使跨引用自动用 canonical。
  - `name_en` / i18n / 标题 / AI 文案 / FAQ **一律不动**（保持自然语言）。
  - 新增 `_write_dedup_redirects()`：写 `docs/dedup-c1-redirects.csv`（406 条 old→canonical）
    + `docs/nginx-301-dedup-c1.conf`（`rewrite ^/jobs/{old}(/.*)?$ /jobs/{canon}$1 permanent;`）。
    **仅对归一后不再存活的旧 slug 发 301**（撞车的 nec-slug 仍作其本码 canonical 存活，不 301）。
- **结果**：ISCO distinct slug **1084→436**（0 码残留多 slug）；全局 slug **5213→4866**。
  副产品：270 个 canonical 恰好命中非 ISCO 国现有 slug（`actor`/`air-traffic-controller` 等
  良性跨分类合并，顺带把 AU/NZ/DE/… 并进同一 by-country tab）。
- **IN 灰色地带**（用户决定保持现状）：印度用 ISCO 436 码但 `occ_code_type=NCO2015`，
  未纳入 C1 → `software-developers` 复数页仍来自 IN + US。可低成本并入（改判据含 IN），后续再说。

## C3 — n.e.c. 兜底桶降权（92 个 slug）✅（aijobrisk-go）

- `internal/data/data.go`：新增 `IsNEC(slug)`（后缀 `-not-elsewhere-classified` 或 `-nec`）。
- `internal/web/ctx.go`：Ctx 加 `Noindex bool`；`templates/base.html` 输出
  `{{ if .Noindex }}<meta name="robots" content="noindex,follow" />{{ end }}`。
- `internal/web/job.go`：`ctx.Noindex = data.IsNEC(slug)`。
- `internal/web/search.go`：无查询的默认榜单剔除 n.e.c.（**仍可被检索命中**）。
- `internal/web/sitemap.go`：两个 job sitemap（global + country）排除 n.e.c.。

---

## 验证 ✅

- `go build ./...` + `go vet ./...` 通过。
- 数据流：`export_site_data_v2`（C1 应用）→ `cp` occupations_v2.json / occ-detail-v2 /
  categories_v2 / translations-v2 到 `aijobrisk-go/data` → **重跑 `translate_go_new_strings.py`**
  （export 覆盖了 UI 译文，51/52 重灌，幂等）。
- 浏览器 + curl：canonical 页 `/jobs/software-developer` = **36 countries** 合并；
  n.e.c. 页有 `noindex,follow`、普通页无；sitemap/搜索默认 0 个 nec、搜 "elsewhere" 仍出 60 个；
  首页 `/` 200、404 正常（**注：改 Ctx 后必须重新 `go build`，旧二进制会报
  `can't evaluate field Noindex`——是陈旧二进制非代码 bug**）。
- job-treemap 重建成功（46 国，新 slug 流入 `/jobs/` 链接）。

---

## 提交

- 分支提交本次 C1+C3 代码 + 两份 docs 产物 + 交接文档，快进合并 main。
- **仅代码**；衍生数据（`site/`、`aijobrisk-go/data`）已 gitignore 不进 git，
  经 `data.zip` / `upload-data.sh` rsync 部署。`aijobrisk-go/data.zip` 排除。

## 待办
1. **部署**：重新 `go build` aijobrisk-go 并重启；rsync `aijobrisk-go/data`（新 slug）+
   job-treemap dist；nginx 挂 `docs/nginx-301-dedup-c1.conf`（406 条 301）。
2. **export 后必重跑** `translate_go_new_strings.py`（UI 译文会被覆盖）。
3. **C2**（非 ISCO 国启发式 slug 去重）+ IN 并入 C1，仍后置。
4. 前会话遗留：info 档官方移民链接复核；~11,322 条评分补跑。
5. 相关记忆 `[[aijobrisk-go-port]]`。
