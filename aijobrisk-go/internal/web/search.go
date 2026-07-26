package web

import (
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

// SearchVM 搜索页。
type SearchVM struct {
	*Ctx
	Q         string
	Count     int
	CountPlus bool
	Results   []resCard
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

	vm := &SearchVM{Ctx: ctx, Q: q, Count: len(gs), CountPlus: len(gs) == 60}
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
