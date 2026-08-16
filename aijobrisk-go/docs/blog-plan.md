# aijobrisk-go Blog/News 功能规划

> 目标:在 aijobrisk-go 增加 blog/articles 功能,定时分享 AI 相关资讯/新闻,尤其是「AI 取代工作 / 裁员」主题。
> 本文档给出定位、内容模型、页面设计、URL/路由、系统架构、i18n、SEO/分发、内链策略、风险与坑、分期路线图,以及待决策项。
> 约束基线:纯 Go 标准库 SSR、启动时把 `data/` 的 JSON 载入内存、`Router()` 按 `seg[0]` 分发、i18n 语言前缀、sitemap 分片、JSON-LD 助手齐备、运行时无 DB。

---

## 0. 战略定位:blog 的角色
不是「再开个博客」,而是给现有程序化 SEO 数据站补两块短板:

- **时效性(Freshness)**:现有页面都是常青数据,缺「新鲜度信号」;新闻流持续喂新。
- **内链枢纽 + E-E-A-T**:每篇文章反向链到 `/jobs/*`、`/industry/*`、`/job-risk-map/{country}`,把新闻热度导流到变现页,同时用「持续分析」建立专业度/权威度。

**结论**:blog 价值约 80% 在「内链与时效」、20% 在文章本身。因此架构上要把「文章 ↔ 职业/行业/国家页的双向关联」作为一等公民设计,而非事后补。

---

## 1. 内容模型:两种文体,分开对待
| 类型 | 说明 | 频率 | SEO 风险 |
|---|---|---|---|
| **A. 原创分析(BlogPosting)** | 自有解读长文(如「2026 上半年科技裁员与 AI 的关系」) | 低频、重质 | 低,主力 |
| **B. 新闻速递/摘要(NewsArticle)** | 摘编外部新闻 + 一句点评 + 链到我们的相关数据页 | 高频、轻量 | ⚠️ 高(见 §8 版权 & 薄内容) |

建议 **以 A 为主、B 为辅**。B 必须「摘要 + 点评 + 我们独有的数据角度」,不能变成纯转载聚合(既侵权又被判薄内容)。

**统一数据结构(每篇一条)**:
```
id / slug / title / dek(导语) / body_html(预渲染) /
type(post|news) / published_at / updated_at /
author_id / hero_image / tags[] /
related_slugs[](职业) / related_sectors[] / related_countries[] /
source_name / source_url(仅 B 类) / lang / status(draft|scheduled|published)
```

---

## 2. URL 与路由设计(贴合现有 `Router()`)
```
/blog                      列表(最新,分页)
/blog/{slug}               文章详情
/blog/tag/{tag}            标签归档(layoffs / ai-tools / policy / research …)
/{lang}/blog/…             语言前缀走现有 i18n(如 /es/blog/… /zh-Hans/blog/…)
/blog/rss.xml              RSS/Atom 订阅
```
在 `server.go` 的 `switch seg[0]` 增加 `case "blog"`,与现有 `insights`/`data` 完全同构。
命名建议用 `/blog`(通用)优于 `/news`(会被 Google News 政策更严格审视)。

---

## 3. 页面设计(三个模板,复用 base.html)

**a) 列表页 `/blog`**
- 顶部:板块标题 + 一句定位 + RSS 按钮 + 标签筛选条(layoffs / ai-tools / policy / research …)
- 卡片流:hero 图 + 类型徽章(分析/速递)+ 标题 + 导语 + 日期 + 阅读时长 + 标签
- 置顶「专题精选」区(手动 pin 1–2 篇重头)
- 分页(每页约 12)

**b) 详情页 `/blog/{slug}`**
- 面包屑 Home › Blog › 标题
- 标题 / 导语 / **作者署名 + 日期 + “更新于” + 阅读时长**(E-E-A-T 必备)
- hero 图(带 alt、来源署名)
- 正文(H2/H3、可选 TOC)
- **文末/右栏「相关数据」卡片**:自动列出本文 `related_*` 指向的职业/行业/国家页(核心内链)
- 文末:来源出处(B 类)、作者简介小卡、上一篇/下一篇、订阅 CTA
- 社交分享(OG / Twitter card)

**c) 标签归档 `/blog/tag/{tag}`**:同列表页,过滤 + 该标签说明。

**风格**:复用现有 `--brand` / `--risk-high` 等 CSS 变量与卡片样式;裁员/风险类标签沿用首页 hot-tags 的三级风险配色(绿 <40 / 琥珀 40–69 / 红 ≥70),视觉与全站一致。

---

## 4. 系统架构:延续「Python 烘焙 + Go 服务」范式
现有 Go 为纯 stdlib、启动读 JSON 进内存。**Markdown 渲染会破坏 stdlib 纯度**,因此最省事、最一致的做法:

```
作者写 Markdown(含 front-matter)
        │  build_blog.py(新脚本,类比 build_industry_ai_adoption.py)
        ▼
  预渲染 HTML + 抽 front-matter → data/blog/index.json + data/blog/{slug}.html
        │  (进 git 或随 data/ 部署——见 §9)
        ▼
  Go: data.LoadBlog() 启动载入 index.json(元数据) + 一次性/惰性读 body html
        ▼
  web/blog.go: BlogIndex / BlogPost / BlogTag / BlogRSS 处理器
```
优点:运行时零新依赖、与现有数据流一致、可版本化。Markdown→HTML、代码高亮、TOC、阅读时长全在 Python 侧算好。

**Go 侧新增(对齐现有文件组织)**:
- `internal/data/blog.go`:`LoadBlog(dir)` + `BlogPosts()` / `BlogBySlug()` / `BlogByTag()`;在 `data.go` 的 `Load()` 内加一行 `loadBlog()`(best-effort,缺文件不影响主站)。
- `internal/web/blog.go`:四个处理器 + VM(对齐 `insights.go` 的写法)。
- `internal/i18n/i18n.go`:加 `HrefBlog()` / `HrefBlogPost()` / `HrefBlogTag()`。
- 模板 3 个(`blog_index.html` / `blog_post.html` / `blog_tag.html`)+ base.html nav/footer 加入口。
- `sitemap.go`:新增 `/sitemap-blog.xml`,且**必须用每篇真实 `updated_at` 做 lastmod**(现全站用常量 `DataUpdated`,新闻不能沿用)。

---

## 5. i18n 策略(易被低估的成本)
全站 8 种显示语言,**逐篇翻 8 语 = 持续重资产**。建议分层:
- **默认英文优先**:新闻速递(B 类)只出英文,过期快,不值得翻。
- **常青分析(A 类)选择性翻译**:重头文章走现成 DeepSeek 翻译管线,翻 es / zh 等高价值语言。
- 未翻语言:显示英文原文 + `hreflang` 指回英文(避免薄译/机翻惩罚)。
- front-matter 里用 `translate: true/false` 控制。

---

## 6. SEO / 分发(新闻特有,勿照搬常青页)
- **结构化数据**:A 类 `BlogPosting`、B 类 `NewsArticle` + `Person`(作者)+ `BreadcrumbList`(复用现有 `jsonLD()` 助手)。
- **新闻专用 sitemap**:`<news:news>` 标签、**仅含 48 小时内**文章(Google News 规则),与常规 blog sitemap 分开。
- **RSS/Atom** `/blog/rss.xml`:订阅、聚合器、可选 WebSub 实时推送。
- **OG / Twitter Card**:每篇 hero 图 + 标题 + 导语,决定社交转发效果。
- **作者实体**:作者页 + `sameAs` 到社交账号,喂 Google 知识图谱。
- **Google Discover**:高质量原创 + 大图最有机会,是新闻类流量大头。

---

## 7. 内链枢纽(最该重视、最易被忽略)
- **正向**:文章 front-matter 声明 `related_slugs / sectors / countries` → 详情页自动渲染「相关数据」卡。
- **反向**:在职业/行业/国家页加「**相关资讯**」小模块,列出 tag 命中的最新文章(如 `/job-risk-map/US` 显示 US 裁员相关文章)。把新闻时效性回灌到变现页,双赢。
- 用 tag × country × sector 自动匹配,零人工维护。

---

## 8. ⚠️ 容易被忽略的坑(重点)
1. **版权/转载合法性(最关键)**:绝不整篇复制新闻。只做「短摘要 + 归属署名 + 链接 + 我们独有的数据点评」。图片同理——新闻配图有版权,用自有图/授权图/CC 图并署名。
2. **薄内容 & 重复内容惩罚**:纯聚合链接会被判 low-value。每篇 B 类至少要有原创点评 + 指向我们数据的独有角度。
3. **停更比不做更糟**:荒废的 blog 拉低全站信任。先定一个能长期扛住的低频节奏(如每周 1 篇),配「编辑日历」,避免开局猛更后烂尾。
4. **事实性与更正政策**:新闻涉具体公司裁员数字,错了有声誉/法律风险。需要 correction 说明 + `dateModified`。
5. **每篇独立日期**:sitemap / 结构化数据 / 展示都要真实 `published/updated`,不能沿用全站常量。
6. **草稿与定时发布**:`status` + `published_at`,渲染时过滤未来时间;别把草稿 build 进去。
7. **评论区**:建议**不做**(垃圾评论 + 审核成本);用**邮件订阅(newsletter)**替代,建立自有受众(不受算法波动)。
8. **AI 生成内容合规**:若用 DeepSeek 起草,需人工审校署名,避免「无差别 AI 内容」打击 + 保持 E-E-A-T。
9. **图片体量/性能**:hero 图压缩 + 尺寸规范 + lazyload + alt,否则拖慢 LCP。
10. **站内搜索**:把文章纳入现有 `/search`,别让 blog 成信息孤岛。
11. **部署一致性**:决定 blog 内容是**进 git**(有版本、无需额外 sync,推荐)还是像 `data/` 那样 rsync(gitignored)。新闻建议进 git。

---

## 9. 分期路线图
- **P0 骨架**:路由 + 列表/详情模板 + `build_blog.py`(Markdown→HTML)+ 2 篇种子文 + BlogPosting/Breadcrumb JSON-LD + sitemap + RSS。英文 only。
- **P1 内链枢纽**:related 卡 + 职业/行业/国家页「相关资讯」模块 + 标签归档 + 站内搜索纳入。
- **P2 新闻化**:NewsArticle + news sitemap(48h)+ 作者实体页 + OG 卡 + newsletter 订阅。
- **P3 规模化**:DeepSeek 辅助起草工作流 + 选择性 i18n 翻译 + 编辑日历/定时发布。

---

## 10. 待决策项(需拍板后才进 P0 详细执行计划)
1. **内容来源与工作流**:纯手写 Markdown 提交?还是搭「DeepSeek 起草 + 人工审校」半自动管线?
2. **i18n 范围**:英文 only 起步?还是重头文也翻译(用现有管线)?
3. **内容存放**:进 git(推荐)还是走 gitignored `data/` rsync?
4. **更新节奏**:能承诺的更新频率(决定 P2 是否值得上 Google News)?

---

## 附:落地时的具体挂载点(现有代码参照)
- 路由:`internal/web/server.go` `Router()` 的 `switch seg[0]` → 加 `case "blog"`(参照 `case "insights"` / `case "data"`)。
- 数据装载:`internal/data/data.go` `Load()` 末尾加 `loadBlog()`(参照 `loadAdoption()` 的 best-effort 模式)。
- 处理器/VM:`internal/web/blog.go`(参照 `insights.go` 的 VM + `renderPage`)。
- i18n 链接:`internal/i18n/i18n.go`(参照 `HrefMethodology` 等)。
- sitemap:`internal/web/sitemap.go`(新增 child `/sitemap-blog.xml`;lastmod 用每篇 `updated_at`)。
- JSON-LD:复用 `job.go` 里的 `jsonLD()` / `breadcrumbLD()` 助手。
- 模板注册:`InitTemplates` 已自动收集 `_*.html` partials,可复用。
