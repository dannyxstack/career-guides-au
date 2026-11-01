package web

import (
	"net/http"
	"strings"

	"aijobrisk/internal/data"
)

// DataUpdated sitemap lastmod 与页面「最后更新」展示用。
// 启动时由 main 从 data.Updated（data/ 关键数据源的最新 mtime）覆盖；
// 这里的字面量只是取不到 mtime 时的兜底，不要再手工维护它。
var DataUpdated = "2026-07-16"

var boardIDs = []string{"most-exposed", "least-exposed", "highest-paying", "largest-workforce", "strongest-demand", "deepest-moat", "ai-proof-high-paying"}

const sitemapMinGlobalWorkforce = 10_000

// countrySEOUpdated 仅在国家维度页面的可见正文或 SEO 元数据实质更新时修改。
// 它与 DataUpdated（底层数据包日期）分开，避免模板更新仍谎报旧数据日期。
const countrySEOUpdated = "2026-11-01"

type sitemapURL struct {
	Path    string
	LastMod string
}

func pageURLs() []sitemapURL {
	// 只有页面主体会随数据包变化时才发 lastmod。联系页、Insights 导航页没有
	// 可验证的修改日期，宁可省略，也不拿数据日期冒充页面更新时间。
	p := []sitemapURL{
		{"/", DataUpdated}, {"/about", DataUpdated}, {"/methodology", DataUpdated},
		{"/search", DataUpdated}, {"/compare", DataUpdated}, {"/industries", countrySEOUpdated},
		{"/rankings", countrySEOUpdated}, {"/job-risk-map", DataUpdated},
		{"/insights", ""}, {"/ai-job-loss-2030", DataUpdated},
		{"/career-outlook", DataUpdated}, {"/data", DataUpdated}, {"/contact", ""},
	}
	// /ai-job-loss-2030/{cc} 与 /career-outlook/{cc} 已并入各自 hub（客户端 #CC 切换），
	// 旧 URL 301 到锚点，不再进 sitemap。
	for _, cc := range data.COUNTRIES {
		// /rankings 与 /industries 的无后缀路由就是 US；显式 /US 会 301，不进 sitemap。
		if cc != "US" {
			p = append(p, sitemapURL{"/rankings/" + cc, countrySEOUpdated})
		}
		p = append(p, sitemapURL{"/job-risk-map/" + cc, DataUpdated})
		// 无行业映射的国家渲染出来是空页，不进 sitemap（见 data.HasIndustryData）。
		if cc != "US" && data.HasIndustryData(cc) {
			p = append(p, sitemapURL{"/industries/" + cc, countrySEOUpdated})
		}
	}
	for _, s := range data.Sectors {
		p = append(p, sitemapURL{"/industry/" + s.ID, countrySEOUpdated})
		for _, cc := range data.COUNTRIES {
			if cc == "US" || !data.HasSectorData(cc, s.ID) {
				continue
			}
			p = append(p, sitemapURL{"/industry/" + s.ID + "/" + cc, countrySEOUpdated})
		}
	}
	for _, b := range boardIDs {
		p = append(p, sitemapURL{"/rankings/" + b, countrySEOUpdated})
		for _, cc := range data.COUNTRIES {
			if cc != "US" {
				p = append(p, sitemapURL{"/rankings/" + b + "/" + cc, countrySEOUpdated})
			}
		}
	}
	return p
}

func jobGlobalURLs() []sitemapURL {
	out := make([]sitemapURL, 0, len(data.JobSlugs))
	for _, s := range data.JobSlugs {
		if data.IsNEC(s) { // C3：n.e.c. 不入 sitemap
			continue
		}
		// 新站先提交有明确受众规模的职业页，避免一次把 4,400+ 模板页全量推给 Google。
		// 未入 sitemap 的页面仍可由站内链接访问；数据/权重成熟后可分批放开。
		if !sitemapPriorityJob(data.JobBySlug(s)) {
			continue
		}
		out = append(out, sitemapURL{"/jobs/" + s, DataUpdated})
	}
	return out
}

func sitemapPriorityJob(g *data.JobGroup) bool {
	if g == nil {
		return false
	}
	workforce := 0.0
	for _, o := range g.Countries {
		if o.WorkforceSize.Set {
			workforce += o.WorkforceSize.V
		}
	}
	return workforce >= sitemapMinGlobalWorkforce
}

var xmlEsc = strings.NewReplacer("&", "&amp;", "<", "&lt;", ">", "&gt;", `"`, "&quot;")

func abs(site, p string) string { return xmlEsc.Replace(site + p) }

func buildURLSet(urls []sitemapURL, site string) string {
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`)
	for _, u := range urls {
		b.WriteString("<url><loc>")
		b.WriteString(abs(site, u.Path))
		b.WriteString("</loc>")
		if u.LastMod != "" {
			b.WriteString("<lastmod>" + u.LastMod + "</lastmod>")
		}
		b.WriteString("</url>")
	}
	b.WriteString("</urlset>")
	return b.String()
}

func buildIndex(children []sitemapURL, site string) string {
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(`<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`)
	for _, c := range children {
		b.WriteString("<sitemap><loc>" + abs(site, c.Path) + "</loc>")
		if c.LastMod != "" {
			b.WriteString("<lastmod>" + c.LastMod + "</lastmod>")
		}
		b.WriteString("</sitemap>")
	}
	b.WriteString("</sitemapindex>")
	return b.String()
}

func latestBlogUpdate(posts []*data.BlogPost) string {
	latest := ""
	for _, p := range posts {
		if p.UpdatedAt > latest {
			latest = p.UpdatedAt
		}
	}
	return latest
}

func latestURLUpdate(urls []sitemapURL) string {
	latest := ""
	for _, u := range urls {
		if u.LastMod > latest {
			latest = u.LastMod
		}
	}
	return latest
}

func sitemapChildren() []sitemapURL {
	return []sitemapURL{
		{"/sitemap-pages.xml", latestURLUpdate(pageURLs())},
		{"/sitemap-jobs.xml", DataUpdated},
		{"/sitemap-blog.xml", latestBlogUpdate(data.BlogPosts())},
	}
}

// buildBlogSitemap blog 专属 sitemap：英文 only（无 hreflang），每篇用真实 updated_at 做 lastmod。
func buildBlogSitemap(site string) string {
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`)
	last := latestBlogUpdate(data.BlogPosts())
	if last == "" {
		last = DataUpdated
	}
	b.WriteString("<url><loc>" + abs(site, "/blog") + "</loc><lastmod>" + last + "</lastmod></url>")
	for _, t := range data.BlogTags() {
		tagLast := latestBlogUpdate(data.BlogByTag(t))
		b.WriteString("<url><loc>" + abs(site, "/blog/tag/"+t) + "</loc><lastmod>" + tagLast + "</lastmod></url>")
	}
	for _, p := range data.BlogPosts() {
		b.WriteString("<url><loc>" + abs(site, "/blog/"+p.Slug) + "</loc><lastmod>" + p.UpdatedAt + "</lastmod></url>")
	}
	b.WriteString("</urlset>")
	return b.String()
}

func writeXML(w http.ResponseWriter, s string) {
	w.Header().Set("Content-Type", "application/xml; charset=utf-8")
	w.Header().Set("Cache-Control", DiscoveryCacheControl)
	w.Write([]byte(s))
}

// RegisterSitemap 注册 sitemap / robots 端点。
func RegisterSitemap(mux *http.ServeMux, site string) {
	mux.HandleFunc("/sitemap.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildIndex(sitemapChildren(), site)) })
	mux.HandleFunc("/sitemap-pages.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildURLSet(pageURLs(), site)) })
	mux.HandleFunc("/sitemap-jobs.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildURLSet(jobGlobalURLs(), site)) })
	mux.HandleFunc("/sitemap-blog.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildBlogSitemap(site)) })
	mux.HandleFunc("/robots.txt", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		w.Header().Set("Cache-Control", DiscoveryCacheControl)
		w.Write([]byte("User-agent: *\nAllow: /\n\nSitemap: " + strings.TrimRight(site, "/") + "/sitemap.xml\n"))
	})
}
