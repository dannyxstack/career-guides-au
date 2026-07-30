# 会话交接 2026-07-30b（C2 单数归一去重 + 应用层 301 + hot-tags 风险配色）

承接 `docs/session-handoff-2026-07-30.md`（C1 ISCO canonical + C3 n.e.c. 降权）。
本会话 5 件事：①补跑评分成本评估（仅分析）；②C2 全类型单数归一去重；
③去重 301 改为 Go 应用层处理（nginx 与业务数据解耦）；④首页 hot-tags 风险分级边框+暴露值；
⑤`data.zip` 加入 gitignore。

---

## 1. 补跑职业评分的翻译量/API 量评估（仅分析，无改动）

DB 实测：**13,066 条**记录缺完整 11 维评分（不是旧估 11,322，数据涨了），分两组：

- **G1 只缺数值评分**（已有全套英文文案+FAQ+官方薪资）：**3,910 条** / 9 国
  （CN, CZ, DK, FI, HU, IS, NO, SE, SG）。→ 基本免费：评分标签 19 字符/职业且高度重复，
  过 TM 后净翻译≈0；评分大概率是当年 LLM 已返回未入库，优先回读缓存 JSON 或按 ISCO 码复制内在维度。
- **G2 空壳需整体补全**（只有官方薪资/就业+ai_risk，零文案零 FAQ）：**9,156 条** / 21 国
  （AR AT BE CH CL EE GR HR ID LT LU LV MY PL PT RO SI SK TH TR VN）。→ 真正成本：
  - LLM 生成：~9,156 次 DeepSeek（1/职业），~15M tokens，**十几美元量级**，12 路并发 ~6–7h。
  - 每职业可翻译英文实测（取 CZ 标定）：summary+forecast+trend **1,461** + FAQ **852** + edu/qual/visa/fit ~600 ≈ **2,900 字符**。
  - 翻译（5 展示语 es/pt/ja/fr/zh-CN）：毛量 26.6M×5=133M，TM 去重后**净 ~100–115M 字符**；
    Azure（$10/M）≈ **$1,000–1,150**，是主要预算项（远超生成费）。改 DeepSeek 翻译可降。
- **一句话**：G1 先做（近零成本）；G2 才是投入，钱在翻译不在生成；可用"按 ISCO 码复制内在文案/评分、只本地化薪资签证段"压成本。

## 2. C2 全类型单数归一去重 ✅（提交 `b50fb25b`）

C1 只归一了 ISCO08，非 ISCO 10 国（SOC/NOC/ANZSCO/NCO2015/CNO/KECO/KldB/ROME/JSCO）仍单复数并存
（`photographer`(ISCO,40国) ‖ `photographers`(SOC/NOC…)）。

- `scripts/dedup_slug.py` 新增 **`build_singular_map(records)`**：按 `singular_slug(slug)` 分组，
  **仅对含 2+ 变体的重复组**归一到单数 canonical（`k`），返回 old→canonical。幂等（二次归一残留 0）。
  不误改孤立复数 URL。
- `scripts/export_site_data_v2.py`：C1 之后接 C2（`smap=build_singular_map(out)` 逐条改 slug），
  redirects 合并进同一 dict。
- **结果**：distinct slug **4,866 → 4,491**（−375）；490 条记录改 slug；**785 条 301**（C1 406 + C2 379）。
  非 ISCO 国自动并入 ISCO 的 by-country tab（`photographer` 40→44 国、`pharmacist` 46 国全合并）。
- 产物 `docs/dedup-c2-preview.csv`（379 条 old→canonical，供审阅）。

## 3. 去重 301 改 Go 应用层（nginx 解耦）✅（提交 `a6af4aee`）

用户要求：nginx 尽量不耦合业务数据，301 在 Go 层做。

- `export_site_data_v2._write_dedup_redirects`：额外输出 **`site/src/data/slug_redirects.json`**（old→canonical，785 条）。
- `aijobrisk-go/internal/data/data.go`：`Load` 读 `slug_redirects.json`（**可选**，缺文件静默跳过），
  新增 **`data.RedirectSlug(old) (canon, ok)`**。
- `internal/web/job.go`：`JobBySlug==nil` 时先查 redirect，命中即 **301**（手写 Location+WriteHeader，
  不需 *http.Request），**保留语言前缀、国家段、query**；否则 404。
- `docs/nginx-301-dedup-c1.conf` 降级为备份（注释注明 301 已在 Go 层处理，nginx 不必挂）。
- curl 实测：`/jobs/photographers`→301`/jobs/photographer`；`/jobs/photographers/US?x=1`→保留国家+query；
  `/es/jobs/photographers`→保留前缀；canonical 200；不存在 slug 404。

## 4. 首页 hot-tags 风险分级边框 + 暴露值 ✅（提交 `a9894f01`）

- `internal/web/home.go`：`tagVM` 加 `HasPct/Pct/BorderColor`；构建 hotTags 时从 `Rep.AI.AioePct`
  取暴露分，复用现有 `pctColor()` 三级分色（绿 `#059669`<40 / 琥珀 `#f59e0b` 40–69 / 红 `#dc2626`≥70）。
- `templates/index.html`：tag 内联 `border-color`，名称后加 `<span class="tag-pct">83%</span>`（同色）；
  移除 `:hover` 的 border-color 覆盖（内联 style 本就高于 :hover 类规则，风险边框始终可见）。
- 浏览器验证通过（General Office Clerk 83% 红 / Shop Sales Assistant 60% 琥珀 / Building Construction Labourer 13% 绿）。

## 5. `data.zip` gitignore ✅（提交 `be156416`）

`aijobrisk-go/.gitignore` 加 `/data.zip`（部署打包产物，随 `upload-data.sh` rsync，非源码）。

---

## 提交（全部 `--ff-only` 合并 main，**未 push**，origin/main 仍 f2464494）
- `6b52434f` C1+C3（上会话）
- `b50fb25b` C2 单数归一
- `a6af4aee` 应用层 301
- `a9894f01` hot-tags 风险配色
- `be156416` gitignore data.zip

## 数据流（本会话已跑）
`export_site_data_v2`（C1+C2+slug_redirects.json）→ cp occupations_v2.json / categories_v2 /
occ-detail-v2 / translations-v2 / **slug_redirects.json** 到 `aijobrisk-go/data` →
**重跑 `translate_go_new_strings.py`**（export 覆盖 UI 译文，每语 51 条 Blue Card）。
`go build` / `go vet` 通过。

## 部署待办
1. 重新 `go build` aijobrisk-go 并重启（加载 `slug_redirects.json` + 新 slug + 新模板）。
2. rsync `aijobrisk-go/data`（含新增 `slug_redirects.json`）+ job-treemap dist。
3. **nginx 无需再挂** `nginx-301-dedup-c1.conf`（应用层已接管；文件保留作备份）。
4. 未 push——需要时再 `git push`。
5. 遗留：G1 评分回补（近零成本，建议先做）；G2 整体补全（评估见 §1）；C2 之外的词序/近义碎片（方案 B）后置。

相关记忆 `[[aijobrisk-go-port]]`。
