package web

import (
	"fmt"
	"net/http"
	"sort"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

// Career outlook 页面（英文版；文案后续接 Tr 翻译）。
// 官方就业预测，与 AI job loss（自建情景模型）互补 —— 见 internal/data/outlook_agg.go。

func growthStr(g float64) string {
	if g >= 0 {
		return fmt.Sprintf("+%.1f%%", g)
	}
	return fmt.Sprintf("%.1f%%", g)
}

// olAggRow hub 全局聚合行（跨国均值）。
type olAggRow struct {
	Title, Href, GrowthStr string
	Growth                 float64
	NCountries             int
}

// olOccRow 国家页单职业行。
type olOccRow struct {
	Title, Href, GrowthStr, Granularity string
	Growth                              float64
}

type olCountryLink struct {
	CC, Name, Href string
}

// OutlookHubVM /career-outlook。
type OutlookHubVM struct {
	*Ctx
	NCountries    int
	Sources       []string
	TopGrow       []olAggRow
	TopDecline    []olAggRow
	HighExpGrow   []olAggRow
	LowExpDecline []olAggRow
	Countries     []olCountryLink
}

// OutlookCountryVM /career-outlook/{cc}。
type OutlookCountryVM struct {
	*Ctx
	CC, Name, Source string
	GroupNote        bool // 该国存在群组级预测 → 提示
	TopGrow          []olOccRow
	TopDecline       []olOccRow
	HubHref          string
}

func aggRow(ctx *Ctx, a data.OutlookAgg) olAggRow {
	return olAggRow{
		Title: a.NameEn, Href: i18n.HrefJob(ctx.Loc, a.Slug, ""),
		GrowthStr: growthStr(a.AvgGrowth), Growth: a.AvgGrowth, NCountries: a.NCountries,
	}
}

// OutlookHub /career-outlook：全球增长/萎缩榜 + 增速×AI暴露交叉双榜 + 国家入口。
func OutlookHub(w http.ResponseWriter, ctx *Ctx) {
	agg := data.OutlookGlobal(3, 80) // hub 榜单用更严的 80% 上限，滤除群组级小基数假象

	var grow, decline, highGrow, lowDecline []data.OutlookAgg
	for _, a := range agg {
		if a.AvgGrowth > 0 {
			grow = append(grow, a)
			if a.AvgExposure >= 6.5 {
				highGrow = append(highGrow, a)
			}
		} else if a.AvgGrowth < 0 {
			decline = append(decline, a)
			if a.AvgExposure <= 4 {
				lowDecline = append(lowDecline, a)
			}
		}
	}
	sort.SliceStable(grow, func(i, j int) bool { return grow[i].AvgGrowth > grow[j].AvgGrowth })
	sort.SliceStable(decline, func(i, j int) bool { return decline[i].AvgGrowth < decline[j].AvgGrowth })
	sort.SliceStable(highGrow, func(i, j int) bool { return highGrow[i].AvgGrowth > highGrow[j].AvgGrowth })
	sort.SliceStable(lowDecline, func(i, j int) bool { return lowDecline[i].AvgGrowth < lowDecline[j].AvgGrowth })

	toRows := func(xs []data.OutlookAgg, n int) []olAggRow {
		if len(xs) > n {
			xs = xs[:n]
		}
		out := make([]olAggRow, len(xs))
		for i, a := range xs {
			out[i] = aggRow(ctx, a)
		}
		return out
	}

	ccs := data.OutlookCountries()
	links := make([]olCountryLink, 0, len(ccs))
	srcSet := map[string]bool{}
	for _, cc := range ccs {
		links = append(links, olCountryLink{CC: cc, Name: data.CountryName(cc, ctx.CL),
			Href: ctx.WithL("/career-outlook/" + cc)})
		for _, r := range data.OutlookByCountry(cc) {
			if r.Source != "" {
				srcSet[r.Source] = true
			}
		}
	}
	sort.SliceStable(links, func(i, j int) bool { return links[i].Name < links[j].Name })
	var sources []string
	for s := range srcSet {
		sources = append(sources, s)
	}
	sort.Strings(sources)

	ctx.Active = "insights"
	ctx.Title = data.Tr("Career outlook", ctx.CL) + " — " + data.Tr("which jobs are growing or shrinking", ctx.CL) + " | " + SiteName
	ctx.Description = data.Tr("Official employment projections across", ctx.CL) + " " + data.Comma(len(ccs)) + " " +
		data.Tr("countries: the fastest-growing and fastest-declining occupations, and which high-AI-exposure jobs are still projected to grow.", ctx.CL)
	ctx.JSONLD = datasetLD(ctx.Site, ctx.CanonicalURL(),
		"Career outlook — official employment projections", ctx.Description)

	renderPage(w, "outlook_hub.html", &OutlookHubVM{
		Ctx: ctx, NCountries: len(ccs), Sources: sources, Countries: links,
		TopGrow: toRows(grow, 15), TopDecline: toRows(decline, 15),
		HighExpGrow: toRows(highGrow, 12), LowExpDecline: toRows(lowDecline, 12),
	})
}

// OutlookCountry /career-outlook/{cc}。
func OutlookCountry(w http.ResponseWriter, ctx *Ctx, cc string) {
	if !inCountries(cc) || !data.HasOutlook(cc) {
		notFound(w, ctx)
		return
	}
	rows := data.OutlookByCountry(cc)
	name := data.CountryName(cc, ctx.CL)

	src, group := "", false
	seen := map[string]bool{}
	var srcs []string
	for _, r := range rows {
		if r.Source != "" && !seen[r.Source] {
			seen[r.Source] = true
			srcs = append(srcs, r.Source)
		}
		if r.Granularity == "group" {
			group = true
		}
	}
	sort.Strings(srcs)
	for i, s := range srcs {
		if i > 0 {
			src += " · "
		}
		src += s
	}

	sorted := append([]data.OutlookRow{}, rows...)
	// 榜单剔除离群值。
	clean := sorted[:0]
	for _, r := range sorted {
		if r.Growth <= data.OutlookMax && r.Growth >= -data.OutlookMax {
			clean = append(clean, r)
		}
	}
	sort.SliceStable(clean, func(i, j int) bool { return clean[i].Growth > clean[j].Growth })

	mk := func(r data.OutlookRow) olOccRow {
		return olOccRow{Title: r.NameEn, Href: i18n.HrefJob(ctx.Loc, r.Slug, cc),
			GrowthStr: growthStr(r.Growth), Growth: r.Growth, Granularity: r.Granularity}
	}
	top := func(asc bool, n int) []olOccRow {
		var out []olOccRow
		if asc {
			for i := len(clean) - 1; i >= 0 && len(out) < n; i-- {
				if clean[i].Growth < 0 {
					out = append(out, mk(clean[i]))
				}
			}
		} else {
			for i := 0; i < len(clean) && len(out) < n; i++ {
				if clean[i].Growth > 0 {
					out = append(out, mk(clean[i]))
				}
			}
		}
		return out
	}

	ctx.Active = "insights"
	ctx.Title = data.Tr("Career outlook", ctx.CL) + " — " + name + " | " + SiteName
	ctx.Description = data.Tr("Official employment projections for", ctx.CL) + " " + name + ": " +
		data.Tr("the fastest-growing and fastest-declining occupations over the next decade.", ctx.CL)
	ctx.JSONLD = datasetLD(ctx.Site, ctx.CanonicalURL(), "Career outlook — "+name, ctx.Description)

	renderPage(w, "outlook_country.html", &OutlookCountryVM{
		Ctx: ctx, CC: cc, Name: name, Source: src, GroupNote: group,
		TopGrow: top(false, 20), TopDecline: top(true, 20),
		HubHref: ctx.WithL("/career-outlook"),
	})
}
