# 会话交接 · 2026-07-17b（多域名架构规则落定 + aijobrisk.com 主站迁移方案）

> 接续 `docs/session-handoff-2026-07-17.md`（job-treemap FAQ/首页长文/术语统一/一键构建）。
> 本会话不写业务代码，只做两件事：①把**四域名多站架构**写进规则 + memory；②盘点 `site/` 现状并**给出迁移到 aijobrisk.com 的方案**（已收集用户 4 项决策，待动手实现）。

---

## 一、多域名架构规则（已落库）

四域名拆多站，各承接不同定位、对应不同源码目录。规则已写入仓库 **`RULES.md`** 顶部新增的「多域名与目录映射规则」一节（表格 + 3 条约定），并存入 memory **`multi-domain-architecture.md`**（project 类型，MEMORY.md 已加索引行）。

| 域名 | 目录 | 定位 | 状态 |
|---|---|---|---|
| **aijobrisk.com** | `site/`（Astro 主站） | 主站，职业分析全量内容 | 在用（**本会话决定迁移到此**）|
| **aijobriskmap.com** | `job-treemap/` | 数据可视化（AI 风险 treemap/地图）| 在用 |
| **ismyjobaiproof.com** | `ismyjobaiproof/` | 评测工具，精简只放工具，其余导流主站 | 在用 |
| **aicareergraph.com** | （待定）| 职业转移/迁移内容 | 暂不做，留作占位 |

约定：单一职责防站间重复被判重罚；ismyjobaiproof 非工具内容一律链接导流 aijobrisk；aicareergraph 当前不搭建。

---

## 二、site/ 现状盘点（迁移前基线）

- **形态**：Astro 纯静态（SSG），8–13 国 × 11 语言。
- **URL**：职业页 `/{country}/{locale}/{category}/{slug}/`；全局页 `/{locale}/`（首页/rankings/about/ai-graph）；**主站自带三套地图** `/job-risk-map/`、`/risk-map/`、`/{country}/{locale}/job-risk-map/`（与 aijobriskmap.com 功能重叠）。
- **域名/品牌硬编码点（迁移必改，散落 6 处）**：
  | 位置 | 当前值 |
  |---|---|
  | `astro.config.mjs` `site:` | `https://aicareergraph.com` |
  | `Base.astro` `og:site_name` | `AI Career Graph` |
  | `data.ts`（zh+en 两套 strings）| `siteTitle`/`tagline`/`homeMetaDesc`/`hFoot`/`abTitle`/`abLead` 全含 "AI Career Graph" |
  | `public/robots.txt` | `aicareergraph.com` sitemap |
  | `public/llms.txt` | 全篇 `aicareergraph.com` + "AI Career Graph" |
  | 首页 H1（data.ts `hHeadline`）| "AI is reshaping {n} jobs worldwide — is yours still in the safe zone?" |

### 两个核心矛盾
1. **品牌 ≠ 域名**：现品牌 "AI Career Graph" 对应 aicareergraph.com，却要上 aijobrisk.com → 需改品牌。
2. **主站与 map 站强重叠**：两域名都押 "AI job risk" 且都有风险地图 → 有重复内容/互相稀释风险（差异化的要害）。

---

## 三、用户已拍板的 4 项决策

1. **主站品牌名 = `AI Job Risk`**（与域名一致；靠副标题/定位与 aijobriskmap 区分）。
2. **主站三套地图页 = 全部保留不动**（不下线、不 noindex）。
3. **aicareergraph.com = 留作职业转移站占位**（旧内容迁走，域名另用）。
4. （待确认，见第五节）主站地图页标题是否"避让"裸词 `AI Job Risk Map`。

---

## 四、迁移方案（待实现，用户全程手动 commit）

### A. 域名/品牌机械层（不涉取舍，可直接做）
- **新增 `src/lib/site.ts`**：导出 `SITE_URL='https://aijobrisk.com'`、`SITE_NAME='AI Job Risk'`，全站引用（单一配置源，杜绝再散 6 处）。
- `astro.config.mjs` `site:` → `https://aijobrisk.com`（canonical/hreflang/sitemap 自动跟随）。
- `Base.astro`：`og:site_name` → `AI Job Risk`；顺带补 `WebSite`+`Organization` JSON-LD（新品牌）。
- `data.ts`（zh+en）：strings 里 "AI Career Graph" → "AI Job Risk"。
- `public/robots.txt` + `public/llms.txt`：域名+品牌全量替换。

### B. 差异化（地图两站都留 → 靠定位分层+标题错位+交叉链，不删页）
- **品牌副标错位**：主站 `AI Job Risk` +副标 "salary, migration & skills guide"（内容库）；map 站 `AI Job Risk Map`（可视化）。
- **主站地图页标题避让**（待用户确认 A/B）：主站 `/{country}/.../job-risk-map/` 标题收敛为偏"该国职业概览"（如 `AI Job Risk in {country} — browse every occupation`），把裸词 `AI Job Risk Map` 让给 map 站。⚠ 撞车点：map 站国家页 H1 已是 `AI Job Risk in {country}`（见 07-17 交接），主站须错开。
- **双向交叉链**：主站职业/国家页 → "看交互式风险地图" 指向 aijobriskmap.com；map 站 → "看完整职业详情" 回指主站。**不用跨域 canonical**（Google 忽略且有险）。

### C. 主站自身 SEO/布局
- 首页 H1 泛词 → 押主词（如 `AI Job Risk: check if your job is safe`）。
- 首页强化职业搜索（长尾入口）+ 热门职业；地图降为次级 CTA。
- 职业页顶部加桥接"本职业在风险地图中的位置 →"。

### D. 部署/301（保权重）
- 新增 nginx：aicareergraph 已收录职业页**路径级 301** → aijobrisk（参照现成 `docs/nginx-301-*.conf`）；aicareergraph 根/其余返回"职业转移站 coming soon"占位。
- ⚠ 不做路径级 301 则 aicareergraph 旧权重丢失。

---

## 五、⚠ 待办 / 待决
1. **待用户确认**：主站地图页标题避让 **A（推荐，改成 browse every occupation 款）** vs **B（维持原标题、接受同词竞争）**。
2. **待用户确认**：是否要一并生成 aicareergraph→aijobrisk 的路径级 301 nginx 配置。
3. 确认后动手顺序：先做 **A. 机械层**（无取舍）→ 再做 B/C 差异化 → 最后 D 部署配置。**改代码前先给 diff 思路再写**（用户偏好）。
4. 本会话仅改了 `RULES.md`（+新章节）+ memory 两文件；**site/ 代码一行未动**。这两处改动 + 上游 07-17/16d 全部仍**未 commit**。

---

## 六、关键坑 / 注意
1. **主站 vs map 站撞车**：`AI Job Risk in {country}` 是 map 站国家页 H1，主站地图页必须错开标题，否则同词自我竞争。
2. **域名散 6 处**：迁移务必走 `site.ts` 单一源，否则漏改。
3. **aicareergraph 权重**：不 301 会丢；但域名要留作职业转移站，故用"路径级 301 旧职业页 + 根占位"折中。
4. data.ts strings 是 **zh + en 两套**，品牌名要两处都改。

> 恢复：读本文件 + memory [[multi-domain-architecture]] [[job-treemap-clone]]。关键文件：`RULES.md`（多域名节）、`site/{astro.config.mjs,src/layouts/Base.astro,src/lib/data.ts,public/robots.txt,public/llms.txt}`、待建 `site/src/lib/site.ts`。
