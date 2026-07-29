# 会话交接 · 2026-07-25（aijobrisk：fr 上线 + 动态 sitemap + 部署文档 + **Go 全量重写**）

> 接续 `docs/session-handoff-2026-07-24.md`。本会话主线：①让法语 fr 在 aijobrisk 页面真正生效并提交；
> ②给 aijobrisk 新建动态 sitemap + robots；③写 `aijobrisk/deployment.md`；④**用 Go 全量 1:1 重写 aijobrisk**
> （新目录 `aijobrisk-go/`，架构不动、省内存），含投票功能，并把投票 API 合并进主站单端口。
> 恢复请读本文件 + memory [[aijobrisk-go-port]] [[aijobrisk-ssr-site]] [[i18n-translation-pipeline]]。

---

## 1. 法语 fr 在 aijobrisk 页面生效（已提交）

之前 fr 是显示语言但内容层回退英文。本会话让其真正显示法语（fr 引用集译文早已 100%）：
- `aijobrisk/src/lib/data.ts`：`Locale` 类型与 `LOCALES` 数组加 `'fr'`。
- `aijobrisk/src/lib/i18n.ts`：fr 的 `content:'en'` → `'fr'`（+更新注释）。
- `scripts/gen_aijobrisk_tm.py`：`LOCALES` 加 `'fr'`，重生成 `translations-v2/fr.*`（248,659 全覆盖）。
- 顺手补翻 fr 仅缺的 2 条 hero 串（`translate_v2 --locales fr`）。
- **已知小缺口（方案 A 保留）**：`about`/`methodology` + AU sourcesBody 走旧 `ui_i18n.json`（无 fr）→ fr 英文兜底。

**已提交 `dd0cf799`**（feat(aijobrisk): enable French display locale…）：含 fr 三处改动 + 上会话遗留全部代码改动
（IN 采集脚本、hero、industries/jobs/Base.astro、翻译标记工具链、4 份交接文档）。**排除**了 dist.zip/deprecated_*/PNG。**未 push**。

## 2. aijobrisk 动态 sitemap + robots（未提交）

原本**没有** sitemap/robots。新建 SSR 端点（每页级 hreflang 早已在 Base.astro）：
- `aijobrisk/src/lib/sitemap.ts`：URL 枚举 + XML 生成（每 `<url>` 含 8 语言 hreflang + x-default，canonical=英文裸 URL）。
- `aijobrisk/src/pages/sitemap.xml.ts`（index）+ `sitemap-pages.xml.ts`(411) + `sitemap-jobs.xml.ts`(4861) + `sitemap-jobs-country.xml.ts`(6575) + `robots.txt.ts`。
- 排除 CH（非路由国家，`occupations` 已按 slug|country 去重）与 compare 组合页。合计 **11,847** canonical URL。

## 3. `aijobrisk/deployment.md`（未提交）

SSR（@astrojs/node standalone）部署文档：本地构建（build 需 16GB，数据打进 bundle）→ rsync dist → systemd（读 HOST/PORT）→ nginx 反代 + TLS。**未含新的 Go 版**（Go 版部署方式见下）。

## 4. 后端语言省内存讨论（结论 Go）

主站运行时内存大头 = 约 300MB 数据常驻。排序：**Go 最省**（原生 struct/单进程共享）> Node（V8 对象膨胀）> Python > PHP（fpm 多 worker 复制）。用户据此决定用 Go 重写。

## 5. **Go 全量重写 aijobrisk（新目录 `aijobrisk-go/`，未提交）**——本会话主体

见 memory [[aijobrisk-go-port]]。用户三选：**全量 1:1 移植 / 复用现有 CSS + html.template 重写结构 / 数据复制到新目录**。
**纯 Go 标准库 + 唯一 1 个第三方依赖（mysql 驱动，仅投票 API 用）；无 web 框架、无 ORM。**

### 结构（30 个 .go、12 个模板）
```
aijobrisk-go/
  main.go                 HTTP 服务 + 路由 + 静态 + sitemap + 投票 API(同端口)
  cmd/pollsapi/main.go    可选：独立投票 API 二进制(复用 internal/pollsapi)
  data/                   复制的全部 JSON(358MB) + derived/(从 data.ts 提取的字典)
  static/app.css, logo.svg
  templates/*.html        base + 各页面(结构重写，CSS 复用)
  tools/extract_dicts.mjs 从 aijobrisk/src/lib/data.ts 提取双语字典→data/derived/*.json
  internal/
    model/    Occ 等结构(Num 兼容 字符串/数字)
    data/     加载/去重/tr()/rankings/industries/compare/dicts/detail(occFull)/faq2030/helpers
    i18n/     显示语言/contentLocale/withL/href(对齐 i18n.ts)
    polls/    投票定义+helper(polls.go) + DB 存储层(store.go, database/sql)
    pollsapi/ 投票 API 处理器(可挂主站 mux，DB 懒连接)
    web/      Ctx+渲染+路由+各页 handler+sitemap+radar SVG+PollBlock
```

### 已完成并验证（EN+FR 逐字对齐 Astro 版）
首页 · 职业详情(/jobs/{slug}[/{cc}]) · industries[/{cc}] · industry/{sector}[/{cc}](可排序表) ·
rankings/{...seg}(hub+board 双模式+筛选/搜索 JS) · compare(index 可搜索 combobox+实时预览；{a}-vs-{b} 动态任意组合) ·
search · about · methodology · sitemap(index+3分片) · robots · 404 · 语言切换 · hreflang · **投票**。

### 关键手法
- **双语字典从 data.ts 提取成 JSON**：`node tools/extract_dicts.mjs`（字符串感知花括号切片+eval）→
  `data/derived/{DIM_LABEL,DIM_DESC,DIS_TYPE,DIS_LEVEL,UI,SOURCES_BODY,RANKINGS,MIG_TEXT,COUNTRY_FLAG,COUNTRY_NAME}.json`。
  **改了 data.ts 这些常量后需重跑该脚本。**
- `model.Num` 兼容 JSON 数字/字符串/null（avg_salary、salaries.min 是字符串）。
- `data.OccFull` 懒加载 `occ-detail-v2/{cc}.json` 合并（含 AI 块合并）。
- 雷达图 `web.RadarSVG` Go 端算几何输出 SVG；i18n 语言前缀在 `web.Router` 里剥（对齐 Astro middleware）。
- about/methodology 走 `Strings()`→ui_i18n.json 无 fr 故 fr 英文兜底（与 Node 版一致，非缺陷）。

### 性能/内存（架构不动前提）
构建：**无需 16GB**（运行时读数据，不打进 bundle）；启动 **1.9s**；RSS **~694MB**（6 语言翻译英文键重复占主，可后续 intern）。

## 6. 投票功能（Go，已合并进主站单端口）

- **组件**：`web/pollblock.go` 构建 SSR 数据 + `job.html` 末尾 markup/JS/CSS。题目走 polls.json 的 zh-CN/en 母本（非 tr，fr→en，与 Node 一致）；`{name}` 服务端填。
- **API**：`internal/pollsapi`（`ConfigureFromEnv()`+`Register(mux)`）——`GET /api/polls`、`POST /api/polls/vote`、`/api/health`；
  一人一票 client_token upsert、IP 哈希软去重、内存滑窗限流、CORS、可选 Turnstile；`database/sql`+`go-sql-driver/mysql` 复用 `poll_*` 三表。
- **用户拍板合并成单端口**：投票 API 挂到主站同一 mux（`pollsapi.Register(mux)`），组件默认 `data-api="/api"`（同源、**免 CORS**）。
  **DB 懒连接**：`sql.Open` 不拨号，首个投票请求才连；连不上则投票降级（GET 返空票、POST 503），**页面照常**——保留"MySQL 挂了站不挂"。
- 端到端验证：health/GET/vote/改票 upsert(avg 折算)/校验 400·429·403/CORS 204 全通过；启动**不碰 DB**。
- 独立 `cmd/pollsapi` 二进制保留（想职责分离时用；同一包）。

### 运行方式
```bash
cd aijobrisk-go
go run .                                  # 单端口(默认 4332)：站点 + /api 投票，读 ../.env 的 MYSQL_*
# 或独立投票 API：go run ./cmd/pollsapi   # POLLS_PORT=8790
```
环境变量：`HOST`/`PORT`/`AIJOBRISK_SITE`/`AIJOBRISK_DATA`；投票：`MYSQL_*`（.env 自动加载）、`POLLS_IP_SALT`/`POLLS_TURNSTILE_SECRET`/`POLLS_CORS_ORIGINS`(同源可空)/`POLLS_RATE_MAX`/`POLLS_RATE_WINDOW`；`PUBLIC_POLLS_API`(仅跨域独立子域时设)。

### 环境坑
本机 **Windows Defender 把新构建的 Go `.exe` 当误报隔离**（构建成功但文件随即消失/Permission denied）。改用 `go run` 验证；真机在服务器构建或给二进制加 AV 排除。

## 待办 / 待决

1. **Go 版唯一未移植页面：job-risk-map**（`/job-risk-map[/{cc}]`，含 `riskmap.ts` 的 squarified treemap 布局算法 +
   世界地图 outline SVG（读 `outline-paths.json`）+ `RiskMap.astro` 交互脚本，最复杂）。
2. **全部未 commit**：`aijobrisk-go/` 整个目录、`aijobrisk/deployment.md`、aijobrisk 的 sitemap/robots 端点（§2）。
   `dd0cf799`（fr 批）已提交未 push。
3. **投票表**：`poll_votes/poll_agg/poll_agg_num` 已存在于 MySQL（本会话验证过）；生产用最小权限 DB 账号（只 DML poll_*）。
4. Go 版部署文档待写（单端口 + 懒连接 DB + seed_polls_schema + systemd/nginx）；用户问过是否补进 deployment.md。
5. 上一交接 `session-handoff-2026-07-24.md` 待办仍在。

> 见 memory [[aijobrisk-go-port]] [[aijobrisk-ssr-site]] [[multi-domain-architecture]] [[i18n-translation-pipeline]]。
