package web

import (
	"encoding/json"
	"html/template"
	"net/http"
	"sort"
	"strings"

	"aijobrisk/internal/data"
)

type resFlag = template.HTML
type resCard struct {
	Name, CatIcon, CatName, Href string
	HasAioe                      bool
	Aioe                         int
	BandCls, BandLabel           string
	Flags                        []template.HTML
}

// suggestItem 自动补全条目（短键，减小体积）。
type suggestItem struct {
	N string `json:"n"` // 职业名（本地化）
	C string `json:"c"` // 分类名
	H string `json:"h"` // 职业链接
	R *int   `json:"r"` // AI 暴露分（0-100，可空）
}

// Suggest /suggest?q= 返回 JSON 自动补全（前缀/包含匹配，最多 8 条）。
func Suggest(w http.ResponseWriter, ctx *Ctx, q string) {
	CL := ctx.CL
	ql := strings.ToLower(strings.TrimSpace(q))
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	out := []suggestItem{}
	if len([]rune(ql)) < 2 {
		_ = json.NewEncoder(w).Encode(out)
		return
	}
	type hit struct {
		item    suggestItem
		name    string
		starts  bool
		work    float64
	}
	var hits []hit
	for _, slug := range data.JobSlugs {
		grp := data.JobBySlug(slug)
		if grp == nil {
			continue
		}
		name := data.Name(grp.Rep, CL)
		nl := strings.ToLower(name)
		if !strings.Contains(nl, ql) {
			continue
		}
		var r *int
		if grp.Rep.AI != nil && grp.Rep.AI.AioePct.Set {
			v := int(grp.Rep.AI.AioePct.V + 0.5)
			r = &v
		}
		work := 0.0
		for _, o := range grp.Countries {
			work += o.WorkforceSize.V
		}
		hits = append(hits, hit{
			item: suggestItem{N: name, C: data.Tr(grp.Rep.Category, CL), H: ctx.HrefJob(slug), R: r},
			name: name, starts: strings.HasPrefix(nl, ql), work: work,
		})
	}
	// 前缀命中优先，其次按全球人数降序，再按名称短优先
	sort.SliceStable(hits, func(i, j int) bool {
		if hits[i].starts != hits[j].starts {
			return hits[i].starts
		}
		if hits[i].work != hits[j].work {
			return hits[i].work > hits[j].work
		}
		return len(hits[i].name) < len(hits[j].name)
	})
	for i, h := range hits {
		if i >= 8 {
			break
		}
		out = append(out, h.item)
	}
	_ = json.NewEncoder(w).Encode(out)
}

// blogHit 搜索结果中的一篇文章。
type blogHit struct{ Title, Href, Dek, Type, Date string }

// SearchVM 搜索页。
type SearchVM struct {
	*Ctx
	Q         string
	Count     int
	CountPlus bool
	Results   []resCard
	BlogHits  []blogHit
}

// searchBlog 在标题/导语/标签里匹配文章（仅有查询时）。
func searchBlog(ql string) []blogHit {
	if ql == "" {
		return nil
	}
	var out []blogHit
	for _, p := range data.BlogPosts() {
		hay := strings.ToLower(p.Title + " " + p.Dek + " " + strings.Join(p.Tags, " "))
		if !strings.Contains(hay, ql) {
			continue
		}
		out = append(out, blogHit{Title: p.Title, Href: "/blog/" + p.Slug, Dek: p.Dek, Type: p.Type, Date: p.PublishedAt})
		if len(out) >= 6 {
			break
		}
	}
	return out
}

// Search /search?q=。
func Search(w http.ResponseWriter, ctx *Ctx, q string) {
	CL := ctx.CL
	q = strings.TrimSpace(q)
	ql := strings.ToLower(q)

	type g struct {
		slug, name, cat string
		aioe            *float64
		countries       []string
		work            float64
	}
	var gs []g
	for _, slug := range data.JobSlugs {
		grp := data.JobBySlug(slug)
		if grp == nil {
			continue
		}
		name := data.Name(grp.Rep, CL)
		if ql != "" && !strings.Contains(strings.ToLower(name), ql) {
			continue
		}
		// C3：无查询的默认榜单剔除 n.e.c. 兜底桶（仍可被检索命中）。
		if ql == "" && data.IsNEC(slug) {
			continue
		}
		var aioe *float64
		if grp.Rep.AI != nil {
			aioe = grp.Rep.AI.AioePct.Ptr()
		}
		work := 0.0
		ccs := make([]string, 0, len(grp.Countries))
		for _, o := range grp.Countries {
			work += o.WorkforceSize.V
			ccs = append(ccs, o.Country)
		}
		gs = append(gs, g{slug, name, grp.Rep.Category, aioe, ccs, work})
	}
	if ql != "" {
		sort.SliceStable(gs, func(i, j int) bool { return len(gs[i].name) < len(gs[j].name) })
	} else {
		sort.SliceStable(gs, func(i, j int) bool { return gs[i].work > gs[j].work })
	}
	if len(gs) > 60 {
		gs = gs[:60]
	}

	vm := &SearchVM{Ctx: ctx, Q: q, Count: len(gs), CountPlus: len(gs) == 60, BlogHits: searchBlog(ql)}
	for _, x := range gs {
		rc := resCard{Name: x.name, CatIcon: data.CategoryIcon(x.cat), CatName: data.Tr(x.cat, CL), Href: ctx.HrefJob(x.slug)}
		if x.aioe != nil {
			b := data.ExpBand(x.aioe)
			rc.HasAioe = true
			rc.Aioe = int(*x.aioe + 0.5)
			rc.BandCls = b.Cls
			rc.BandLabel = data.Tr(b.Label, CL)
		}
		limit := x.countries
		if len(limit) > 6 {
			limit = limit[:6]
		}
		for _, cc := range limit {
			rc.Flags = append(rc.Flags, data.CountryFlag(cc))
		}
		vm.Results = append(vm.Results, rc)
	}

	ctx.Active = "occupations"
	if q != "" {
		ctx.Title = data.Tr("Search", CL) + ": " + q + " | AI Job Risk"
	} else {
		ctx.Title = data.Tr("Browse occupations", CL) + " | AI Job Risk"
	}
	ctx.Description = data.Tr("Search occupations and check AI replacement risk.", CL)
	renderPage(w, "search.html", vm)
}
