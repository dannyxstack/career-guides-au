package data

import (
	"sort"

	"aijobrisk/internal/model"
)

// RankItem 榜单条目。
type RankItem struct {
	Name      string
	Slug      string
	Cat       string
	CatSlug   string
	Aioe      *float64
	Salary    *float64
	Workforce *float64
	Demand    *float64
	Moat      *float64
}

// Board 榜单。
type Board struct {
	ID     string
	Title  string
	Desc   string
	Metric string
	Items  []RankItem
}

func toItem(o *model.Occ, loc string) RankItem {
	var aioe, moat *float64
	if o.AI != nil {
		aioe = o.AI.AioePct.Ptr()
		moat = o.AI.HumanMoat.Ptr()
	}
	return RankItem{
		Name: Name(o, loc), Slug: o.Slug, Cat: o.Category, CatSlug: CatSlug(o.Category),
		Aioe: aioe, Salary: o.AvgSalary.Ptr(), Workforce: o.WorkforceSize.Ptr(),
		Demand: o.Rating("job_demand"), Moat: moat,
	}
}

func filter(items []RankItem, keep func(RankItem) bool) []RankItem {
	var out []RankItem
	for _, it := range items {
		if keep(it) {
			out = append(out, it)
		}
	}
	return out
}

func topN(items []RankItem, val func(RankItem) *float64, desc bool, n int) []RankItem {
	cp := make([]RankItem, len(items))
	copy(cp, items)
	sort.SliceStable(cp, func(i, j int) bool {
		a, b := val(cp[i]), val(cp[j])
		if desc {
			return f(a) > f(b)
		}
		return f(a) < f(b)
	})
	if len(cp) > n {
		cp = cp[:n]
	}
	return cp
}

// BuildBoards 6 个榜单（对齐 rankings.ts）。
func BuildBoards(country string, top int, loc string) []Board {
	var all []RankItem
	for _, o := range OccByCountry(country) {
		all = append(all, toItem(o, loc))
	}
	withExp := filter(all, func(i RankItem) bool { return i.Aioe != nil })
	withPay := filter(all, func(i RankItem) bool { return i.Salary != nil })
	// AI-proof 高薪：有薪资且 AI 暴露分低（< 40，即“低”暴露带），按薪资降序。
	aiProof := filter(withPay, func(i RankItem) bool { return i.Aioe != nil && *i.Aioe < 40 })
	withWork := filter(all, func(i RankItem) bool { return i.Workforce != nil && *i.Workforce > 0 })
	withDemand := filter(all, func(i RankItem) bool { return i.Demand != nil })
	withMoat := filter(all, func(i RankItem) bool { return i.Moat != nil })

	aioe := func(i RankItem) *float64 { return i.Aioe }
	return []Board{
		{ID: "most-exposed", Title: Tr("Most exposed to AI", loc), Desc: Tr("Highest generative-AI exposure percentile", loc), Metric: "aioe",
			Items: topN(withExp, aioe, true, top)},
		{ID: "least-exposed", Title: Tr("Least exposed to AI", loc), Desc: Tr("Most resilient to automation", loc), Metric: "aioe",
			Items: topN(withExp, aioe, false, top)},
		{ID: "highest-paying", Title: Tr("Highest paying", loc), Desc: Tr("Average annual salary", loc), Metric: "salary",
			Items: topN(withPay, func(i RankItem) *float64 { return i.Salary }, true, top)},
		{ID: "largest-workforce", Title: Tr("Largest workforce", loc), Desc: Tr("Total employed", loc), Metric: "workforce",
			Items: topN(withWork, func(i RankItem) *float64 { return i.Workforce }, true, top)},
		{ID: "strongest-demand", Title: Tr("Strongest job demand", loc), Desc: Tr("Projected demand (1–10 scale)", loc), Metric: "demand",
			Items: topN(withDemand, func(i RankItem) *float64 { return i.Demand }, true, top)},
		{ID: "deepest-moat", Title: Tr("Deepest human moat", loc), Desc: Tr("Hardest for AI to replace (1–10 scale)", loc), Metric: "moat",
			Items: topN(withMoat, func(i RankItem) *float64 { return i.Moat }, true, top)},
		{ID: "ai-proof-high-paying", Title: Tr("High-paying AI-proof jobs", loc), Desc: Tr("Best-paid occupations with low AI exposure", loc), Metric: "salary",
			Items: topN(aiProof, func(i RankItem) *float64 { return i.Salary }, true, top)},
	}
}

// BoardByID 单个榜单（top 默认更大）。
func BoardByID(country, id string, top int, loc string) *Board {
	for _, b := range BuildBoards(country, top, loc) {
		if b.ID == id {
			bb := b
			return &bb
		}
	}
	return nil
}
