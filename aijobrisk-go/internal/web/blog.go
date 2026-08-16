package web

import (
	"html/template"
	"net/http"
	"strings"
	"time"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

// Blog 板块：AI 资讯/分析（英文 only）。由 scripts/build_blog.py 烘焙的 data/blog 驱动。

// linkVM 相关数据/资讯卡的一个链接。
type linkVM struct{ Name, Href string }

// blogCardVM 列表卡（复用 data.BlogPost，附本地化日期由模板 fmtdate 处理）。

// BlogIndexVM /blog。
type BlogIndexVM struct {
	*Ctx
	Featured []*data.BlogPost
	Posts    []*data.BlogPost // 非置顶
	Tags     []string
}

// BlogIndex /blog：最新列表 + 置顶精选 + 标签筛选。
func BlogIndex(w http.ResponseWriter, ctx *Ctx) {
	ctx.Active = "blog"
	ctx.EnglishOnly = true
	ctx.Title = "AI & Jobs Blog — layoffs, automation & the future of work | " + SiteName
	ctx.Description = "Original analysis and news on AI-driven job loss, layoffs and automation — cross-checked against our generative-AI exposure data."
	ctx.JSONLD = jsonLD(
		map[string]any{"@context": "https://schema.org", "@type": "Blog",
			"name": "AI & Jobs Blog", "url": ctx.CanonicalURL(), "inLanguage": "en"},
		map[string]any{"@context": "https://schema.org", "@type": "BreadcrumbList",
			"itemListElement": []map[string]any{
				{"@type": "ListItem", "position": 1, "name": "Home", "item": ctx.Site + ctx.HrefHome()},
				{"@type": "ListItem", "position": 2, "name": "Blog", "item": ctx.CanonicalURL()},
			}},
	)

	var featured, rest []*data.BlogPost
	for _, p := range data.BlogPosts() {
		if p.Featured {
			featured = append(featured, p)
		} else {
			rest = append(rest, p)
		}
	}
	renderPage(w, "blog_index.html", &BlogIndexVM{Ctx: ctx, Featured: featured, Posts: rest, Tags: data.BlogTags()})
}

// BlogPostVM /blog/{slug}。
type BlogPostVM struct {
	*Ctx
	Post        *data.BlogPost
	Body        template.HTML
	TOC         template.HTML
	Author      data.BlogAuthor
	HasAuthor   bool
	RelJobs     []linkVM
	RelSectors  []linkVM
	RelCountries []linkVM
	Newer       *data.BlogPost
	Older       *data.BlogPost
}

// BlogPost /blog/{slug}：文章详情 + 相关数据卡 + 上下篇。
func BlogPost(w http.ResponseWriter, ctx *Ctx, slug string) {
	p := data.BlogBySlug(slug)
	if p == nil {
		notFound(w, ctx)
		return
	}
	ctx.Active = "blog"
	ctx.EnglishOnly = true
	ctx.OGType = "article"
	ctx.Title = p.Title + " | " + SiteName
	ctx.Description = p.Dek
	if p.HeroImage != "" {
		ctx.OGImage = absURL(ctx.Site, p.HeroImage)
	}
	ctx.JSONLD = jsonLD(blogArticleLD(ctx, p), blogBreadcrumbLD(ctx, p.Title))

	vm := &BlogPostVM{
		Ctx:  ctx,
		Post: p,
		Body: template.HTML(p.Body),
		TOC:  template.HTML(p.TOC),
	}
	if a, ok := data.BlogAuthorByID(p.Author); ok {
		vm.Author, vm.HasAuthor = a, true
	}

	// 相关数据卡（P1 正向内链）。
	for _, s := range p.RelatedSlugs {
		if g := data.JobBySlug(s); g != nil {
			vm.RelJobs = append(vm.RelJobs, linkVM{Name: data.Name(g.Rep, "en"), Href: ctx.HrefJob(s)})
		}
	}
	for _, id := range p.RelatedSectors {
		if sec := data.SectorByID(id); sec != nil {
			vm.RelSectors = append(vm.RelSectors, linkVM{Name: sec.Name, Href: i18n.HrefIndustry(ctx.Loc, id, "")})
		}
	}
	for _, cc := range p.RelatedCountries {
		vm.RelCountries = append(vm.RelCountries, linkVM{Name: data.CountryName(cc, "en"), Href: i18n.HrefMap(ctx.Loc, cc)})
	}

	// 上一篇（更新）/下一篇（更旧）：blogPosts newest-first。
	posts := data.BlogPosts()
	for i, q := range posts {
		if q.Slug == slug {
			if i > 0 {
				vm.Newer = posts[i-1]
			}
			if i < len(posts)-1 {
				vm.Older = posts[i+1]
			}
			break
		}
	}
	renderPage(w, "blog_post.html", vm)
}

// BlogTagVM /blog/tag/{tag}。
type BlogTagVM struct {
	*Ctx
	Tag   string
	Posts []*data.BlogPost
}

// BlogTag /blog/tag/{tag}：标签归档。
func BlogTag(w http.ResponseWriter, ctx *Ctx, tag string) {
	posts := data.BlogByTag(tag)
	if len(posts) == 0 {
		notFound(w, ctx)
		return
	}
	ctx.Active = "blog"
	ctx.EnglishOnly = true
	ctx.Title = "#" + tag + " — AI & Jobs Blog | " + SiteName
	ctx.Description = "Articles tagged " + tag + " on AI-driven job loss, layoffs and automation."
	renderPage(w, "blog_tag.html", &BlogTagVM{Ctx: ctx, Tag: tag, Posts: posts})
}

// topNews 取前 n 篇（posts 已 newest-first）。
func topNews(posts []*data.BlogPost, n int) []*data.BlogPost {
	if len(posts) > n {
		return posts[:n]
	}
	return posts
}

// absURL 把站内路径转绝对 URL（已是 http(s) 则原样）。
func absURL(site, p string) string {
	if strings.HasPrefix(p, "http://") || strings.HasPrefix(p, "https://") {
		return p
	}
	return strings.TrimRight(site, "/") + p
}

// blogArticleLD schema.org BlogPosting / NewsArticle。
func blogArticleLD(ctx *Ctx, p *data.BlogPost) map[string]any {
	typ := "BlogPosting"
	if p.Type == "news" {
		typ = "NewsArticle"
	}
	authorName := "aijobrisk Editorial"
	authorURL := ctx.Site + ctx.HrefAbout()
	if a, ok := data.BlogAuthorByID(p.Author); ok {
		authorName = a.Name
		if a.URL != "" {
			authorURL = absURL(ctx.Site, a.URL)
		}
	}
	ld := map[string]any{
		"@context":         "https://schema.org",
		"@type":            typ,
		"headline":         p.Title,
		"description":      p.Dek,
		"datePublished":    p.PublishedAt,
		"dateModified":     p.UpdatedAt,
		"url":              ctx.CanonicalURL(),
		"mainEntityOfPage": ctx.CanonicalURL(),
		"inLanguage":       "en",
		"author":           map[string]any{"@type": "Person", "name": authorName, "url": authorURL},
		"publisher": map[string]any{
			"@type": "Organization", "name": SiteName, "url": ctx.Site,
			"logo": map[string]any{"@type": "ImageObject", "url": ctx.Site + "/logo.svg"},
		},
	}
	if len(p.Tags) > 0 {
		ld["keywords"] = strings.Join(p.Tags, ", ")
	}
	if p.HeroImage != "" {
		ld["image"] = absURL(ctx.Site, p.HeroImage)
	}
	if p.Type == "news" && p.SourceURL != "" {
		ld["citation"] = p.SourceURL
	}
	return ld
}

// blogBreadcrumbLD Home › Blog › Title。
func blogBreadcrumbLD(ctx *Ctx, title string) map[string]any {
	return map[string]any{
		"@context": "https://schema.org", "@type": "BreadcrumbList",
		"itemListElement": []map[string]any{
			{"@type": "ListItem", "position": 1, "name": "Home", "item": ctx.Site + ctx.HrefHome()},
			{"@type": "ListItem", "position": 2, "name": "Blog", "item": ctx.Site + ctx.HrefBlog()},
			{"@type": "ListItem", "position": 3, "name": title, "item": ctx.CanonicalURL()},
		},
	}
}

// BlogRSS /blog/rss.xml：RSS 2.0 订阅（英文）。
func BlogRSS(w http.ResponseWriter, ctx *Ctx) {
	site := strings.TrimRight(ctx.Site, "/")
	esc := func(s string) string {
		return strings.NewReplacer("&", "&amp;", "<", "&lt;", ">", "&gt;").Replace(s)
	}
	pub := func(iso string) string {
		if t, err := time.Parse("2006-01-02", iso); err == nil {
			return t.Format(time.RFC1123Z)
		}
		return iso
	}
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(`<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>`)
	b.WriteString("<title>AI &amp; Jobs Blog — " + esc(SiteName) + "</title>")
	b.WriteString("<link>" + site + "/blog</link>")
	b.WriteString(`<atom:link href="` + site + `/blog/rss.xml" rel="self" type="application/rss+xml"/>`)
	b.WriteString("<description>Analysis and news on AI-driven job loss, layoffs and automation.</description>")
	b.WriteString("<language>en</language>")
	if posts := data.BlogPosts(); len(posts) > 0 {
		b.WriteString("<lastBuildDate>" + pub(posts[0].UpdatedAt) + "</lastBuildDate>")
		for _, p := range posts {
			link := site + "/blog/" + p.Slug
			b.WriteString("<item>")
			b.WriteString("<title>" + esc(p.Title) + "</title>")
			b.WriteString("<link>" + link + "</link>")
			b.WriteString(`<guid isPermaLink="true">` + link + "</guid>")
			b.WriteString("<pubDate>" + pub(p.PublishedAt) + "</pubDate>")
			b.WriteString("<description>" + esc(p.Dek) + "</description>")
			for _, t := range p.Tags {
				b.WriteString("<category>" + esc(t) + "</category>")
			}
			b.WriteString("</item>")
		}
	}
	b.WriteString("</channel></rss>")
	w.Header().Set("Content-Type", "application/rss+xml; charset=utf-8")
	w.Write([]byte(b.String()))
}
