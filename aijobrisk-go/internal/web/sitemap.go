package web

import (
	"net/http"
	"strings"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

// DataUpdated sitemap lastmod（对齐 site-config DATA_UPDATED）。
const DataUpdated = "2026-07-16"

var boardIDs = []string{"most-exposed", "least-exposed", "highest-paying", "largest-workforce", "strongest-demand", "deepest-moat", "ai-proof-high-paying"}

func pagePaths() []string {
	p := []string{"/", "/about", "/methodology", "/search", "/compare", "/industries", "/rankings", "/job-risk-map", "/insights", "/ai-job-loss-2030", "/career-outlook", "/data"}
	for _, cc := range data.COUNTRIES {
		p = append(p, "/industries/"+cc, "/rankings/"+cc, "/job-risk-map/"+cc, "/ai-job-loss-2030/"+cc)
		if data.HasOutlook(cc) {
			p = append(p, "/career-outlook/"+cc)
		}
	}
	for _, s := range data.Sectors {
		p = append(p, "/industry/"+s.ID)
		for _, cc := range data.COUNTRIES {
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
		out = append(out, "/jobs/"+s)
	}
	return out
}

func jobCountryPaths() []string {
	set := map[string]bool{}
	for _, cc := range data.COUNTRIES {
		set[cc] = true
	}
	var out []string
	for _, o := range data.Occupations {
		if set[o.Country] && !data.IsNEC(o.Slug) { // C3：n.e.c. 不入 sitemap
			out = append(out, "/jobs/"+o.Slug+"/"+o.Country)
		}
	}
	return out
}

var xmlEsc = strings.NewReplacer("&", "&amp;", "<", "&lt;", ">", "&gt;", `"`, "&quot;")

func abs(site, p string) string { return xmlEsc.Replace(site + p) }

func buildUrlset(paths []string, site string) string {
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">`)
	for _, bare := range paths {
		b.WriteString("<url><loc>")
		b.WriteString(abs(site, bare))
		b.WriteString("</loc>")
		for _, d := range i18n.DisplayLocales {
			b.WriteString(`<xhtml:link rel="alternate" hreflang="` + d.Hreflang + `" href="` + abs(site, i18n.WithL(d.Code, bare)) + `"/>`)
		}
		b.WriteString(`<xhtml:link rel="alternate" hreflang="x-default" href="` + abs(site, bare) + `"/>`)
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

var sitemapChildren = []string{"/sitemap-pages.xml", "/sitemap-jobs.xml", "/sitemap-jobs-country.xml"}

func writeXML(w http.ResponseWriter, s string) {
	w.Header().Set("Content-Type", "application/xml; charset=utf-8")
	w.Write([]byte(s))
}

// RegisterSitemap 注册 sitemap / robots 端点。
func RegisterSitemap(mux *http.ServeMux, site string) {
	mux.HandleFunc("/sitemap.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildIndex(sitemapChildren, site)) })
	mux.HandleFunc("/sitemap-pages.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildUrlset(pagePaths(), site)) })
	mux.HandleFunc("/sitemap-jobs.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildUrlset(jobGlobalPaths(), site)) })
	mux.HandleFunc("/sitemap-jobs-country.xml", func(w http.ResponseWriter, r *http.Request) { writeXML(w, buildUrlset(jobCountryPaths(), site)) })
	mux.HandleFunc("/robots.txt", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		w.Write([]byte("User-agent: *\nAllow: /\n\nSitemap: " + strings.TrimRight(site, "/") + "/sitemap.xml\n"))
	})
}
