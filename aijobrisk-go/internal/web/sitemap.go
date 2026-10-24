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

func pagePaths() []string {
	p := []string{"/", "/about", "/methodology", "/search", "/compare", "/industries", "/rankings", "/job-risk-map", "/insights", "/ai-job-loss-2030", "/career-outlook", "/data", "/contact"}
	// /ai-job-loss-2030/{cc} 与 /career-outlook/{cc} 已并入各自 hub（客户端 #CC 切换），
	// 旧 URL 301 到锚点，不再进 sitemap。
	for _, cc := range data.COUNTRIES {
		p = append(p, "/rankings/"+cc, "/job-risk-map/"+cc)
		// 无行业映射的国家渲染出来是空页，不进 sitemap（见 data.HasIndustryData）。
		if data.HasIndustryData(cc) {
			p = append(p, "/industries/"+cc)
		}
	}
	for _, s := range data.Sectors {
		p = append(p, "/industry/"+s.ID)
		for _, cc := range data.COUNTRIES {
			if !data.HasSectorData(cc, s.ID) {
				continue
			}
			p = append(p, "/industry/"+s.ID+"/"+cc)
		}
	}
	for _, b := range boardIDs {
		p = append(p, "/rankings/"+b)
		for _, cc := range data.COUNTRIES {
			p = append(p, "/rankings/"+b+"/"+cc)
		}
	}
	return p
}

func jobGlobalPaths() []string {
	out := make([]string, 0, len(data.JobSlugs))
	for _, s := range data.JobSlugs {
		if data.IsNEC(s) { // C3：n.e.c. 不入 sitemap
			continue
		}
		// 新站先提交有明确受众规模的职业页，避免一次把 4,400+ 模板页全量推给 Google。
		// 未入 sitemap 的页面仍可由站内链接访问；数据/权重成熟后可分批放开。
		if !sitemapPriorityJob(data.JobBySlug(s)) {
			continue
		}
		out = append(out, "/jobs/"+s)
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

func buildUrlset(paths []string, site string) string {
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`)
	for _, bare := range paths {
		b.WriteString("<url><loc>")
		b.WriteString(abs(site, bare))
		b.WriteString("</loc>")
		b.WriteString("<lastmod>" + DataUpdated + "</lastmod></url>")
	}
	b.WriteString("</urlset>")
	return b.String()
}

func buildIndex(children []string, site string) string {
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(`<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`)
	for _, c := range children {
		b.WriteString("<sitemap><loc>" + abs(site, c) + "</loc><lastmod>" + DataUpdated + "</lastmod></sitemap>")
	}
	b.WriteString("</sitemapindex>")
	return b.String()
}

var sitemapChildren = []string{"/sitemap-pages.xml", "/sitemap-jobs.xml", "/sitemap-blog.xml"}

// buildBlogSitemap blog 专属 sitemap：英文 only（无 hreflang），每篇用真实 updated_at 做 lastmod。
func buildBlogSitemap(site string) string {
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`)
	last := DataUpdated
	if posts := data.BlogPosts(); len(posts) > 0 {
		last = posts[0].UpdatedAt // newest-first
	}
	b.WriteString("<url><loc>" + abs(site, "/blog") + "</loc><lastmod>" + last + "</lastmod></url>")
	for _, t := range data.BlogTags() {
		b.WriteString("<url><loc>" + abs(site, "/blog/tag/"+t) + "</loc><lastmod>" + last + "</lastmod></url>")
	}
	for _, p := range data.BlogPosts() {
		b.WriteString("<url><loc>" + abs(site, "/blog/"+p.Slug) + "</loc><lastmod>" + p.UpdatedAt + "</lastmod></url>")
	}
	b.WriteString("</urlset>")
	return b.String()
}

func writeXML(w http.ResponseWriter, s string) {
	w.Header().Set("Content-Type", "application/xml; charset=utf-8")
	w.Write([]byte(s))
}

// RegisterSitemap 注册 sitemap / robots 端点。
func RegisterSitemap(mux *http.ServeMux, site string) {
	mux.HandleFunc("/sitemap.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildIndex(sitemapChildren, site)) })
	mux.HandleFunc("/sitemap-pages.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildUrlset(pagePaths(), site)) })
	mux.HandleFunc("/sitemap-jobs.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildUrlset(jobGlobalPaths(), site)) })
	mux.HandleFunc("/sitemap-blog.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildBlogSitemap(site)) })
	mux.HandleFunc("/robots.txt", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		w.Write([]byte("User-agent: *\nAllow: /\n\nSitemap: " + strings.TrimRight(site, "/") + "/sitemap.xml\n"))
	})
}
