package web

import (
	"log"
	"net/http"
	"sort"
	"strings"

	"aijobrisk/internal/i18n"
)

// sortStable 稳定排序泛型助手。
func sortStable[T any](s []T, less func(a, b T) bool) {
	sort.SliceStable(s, func(i, j int) bool { return less(s[i], s[j]) })
}

// renderPage 渲染并处理错误。
func renderPage(w http.ResponseWriter, page string, vm any) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	if err := Render(w, page, vm); err != nil {
		log.Printf("render %s: %v", page, err)
		http.Error(w, "internal error", http.StatusInternalServerError)
	}
}

// NewCtx 从请求构造渲染上下文（剥语言前缀）。
func NewCtx(r *http.Request, site string) *Ctx {
	loc, bare := i18n.SplitLocale(r.URL.Path)
	q := ""
	if r.URL.RawQuery != "" {
		q = "?" + r.URL.RawQuery
	}
	return &Ctx{Loc: loc, CL: i18n.ContentLocale(loc), Site: site, Bare: bare, Query: q}
}

// Router 页面路由：剥语言前缀后按裸路径分发（对齐 Astro middleware + 文件路由）。
func Router(site string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ctx := NewCtx(r, site)
		if ctx.Bare == "/" {
			Home(w, ctx)
			return
		}
		seg := strings.Split(strings.Trim(ctx.Bare, "/"), "/")
		switch seg[0] {
		case "jobs":
			switch len(seg) {
			case 2:
				Job(w, ctx, seg[1], "")
				return
			case 3:
				Job(w, ctx, seg[1], seg[2])
				return
			}
		case "industries":
			if len(seg) == 1 {
				Industries(w, ctx, "")
				return
			}
			if len(seg) == 2 {
				Industries(w, ctx, seg[1])
				return
			}
		case "industry":
			if len(seg) == 2 {
				Industry(w, ctx, seg[1], "")
				return
			}
			if len(seg) == 3 {
				Industry(w, ctx, seg[1], seg[2])
				return
			}
		case "rankings":
			Rankings(w, ctx, seg[1:])
			return
		case "search":
			if len(seg) == 1 {
				Search(w, ctx, r.URL.Query().Get("q"))
				return
			}
		case "suggest":
			if len(seg) == 1 {
				Suggest(w, ctx, r.URL.Query().Get("q"))
				return
			}
		case "about":
			if len(seg) == 1 {
				About(w, ctx)
				return
			}
		case "methodology":
			if len(seg) == 1 {
				Methodology(w, ctx)
				return
			}
		case "compare":
			if len(seg) == 1 {
				CompareIndex(w, ctx)
				return
			}
			if len(seg) == 2 {
				ComparePair(w, ctx, seg[1])
				return
			}
		case "job-risk-map":
			if len(seg) == 1 {
				RiskMap(w, ctx, "")
				return
			}
			if len(seg) == 2 {
				RiskMap(w, ctx, seg[1])
				return
			}
		case "ai-job-loss-2030":
			if len(seg) == 1 {
				JobLossHub(w, ctx)
				return
			}
			if len(seg) == 2 {
				JobLossCountry(w, ctx, seg[1])
				return
			}
		}
		notFound(w, ctx)
	})
}

func notFound(w http.ResponseWriter, ctx *Ctx) {
	w.WriteHeader(http.StatusNotFound)
	ctx.Active = ""
	ctx.Title = ctx.Tr("Page not found") + " | AI Job Risk"
	renderPage(w, "404.html", &struct{ *Ctx }{ctx})
}
