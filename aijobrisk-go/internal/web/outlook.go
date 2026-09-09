package web

import (
	"fmt"
	"html/template"
	"net/http"
	"sort"
	"strings"

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
// 各国明细内嵌为 JSON、客户端切换（#CC 深链），不再拆成 34 个 URL——
// 那些页面每国仅约 270 词且跨国结构逐字相同，Google 判为薄内容拒绝索引。
type OutlookHubVM struct {
	*Ctx
	NCountries    int
	Sources       []string
	TopGrow       []olAggRow
	TopDecline    []olAggRow
	HighExpGrow   []olAggRow
	LowExpDecline []olAggRow
	Countries     []olCountryLink
	DetailJSON    template.JS
	DefaultCC     string
}

// olDetail 单国明细，供客户端切换渲染。字段名压到 1-2 字符控制内嵌体积。
type olDetail struct {
	N string   `json:"n"` // 国家名
	S string   `json:"s"` // 数据来源
	G bool     `json:"g"` // 是否含群组级预测
	U [][3]any `json:"u"` // 增长 [职业名, 增幅字符串, 链接]
	D [][3]any `json:"d"` // 下滑
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

	// 各国明细内嵌，客户端按 #CC 切换；URL 面从 35 收敛到 1。
	detail := map[string]olDetail{}
	for _, l := range links {
		detail[l.CC] = buildOutlookDetail(ctx, l.CC)
	}
	defCC := ""
	if len(links) > 0 {
		defCC = links[0].CC
	}
	renderPage(w, "outlook_hub.html", &OutlookHubVM{
		Ctx: ctx, NCountries: len(ccs), Sources: sources, Countries: links,
		TopGrow: toRows(grow, 15), TopDecline: toRows(decline, 15),
		HighExpGrow: toRows(highGrow, 12), LowExpDecline: toRows(lowDecline, 12),
		DetailJSON: jsonJS(detail), DefaultCC: defCC,
	})
}

// buildOutlookDetail 单国明细（原 /career-outlook/{cc} 的独有内容），供 hub 内嵌。
func buildOutlookDetail(ctx *Ctx, cc string) olDetail {
	rows := data.OutlookByCountry(cc)
	d := olDetail{N: data.CountryName(cc, ctx.CL)}

	seen := map[string]bool{}
	var srcs []string
	for _, r := range rows {
		if r.Source != "" && !seen[r.Source] {
			seen[r.Source] = true
			srcs = append(srcs, r.Source)
		}
		if r.Granularity == "group" {
			d.G = true
		}
	}
	sort.Strings(srcs)
	d.S = strings.Join(srcs, " · ")

	// 榜单剔除离群值。
	clean := make([]data.OutlookRow, 0, len(rows))
	for _, r := range rows {
		if r.Growth <= data.OutlookMax && r.Growth >= -data.OutlookMax {
			clean = append(clean, r)
		}
	}
	sort.SliceStable(clean, func(i, j int) bool { return clean[i].Growth > clean[j].Growth })

	mk := func(r data.OutlookRow) [3]any {
		return [3]any{r.NameEn, growthStr(r.Growth), i18n.HrefJob(ctx.Loc, r.Slug, cc)}
	}
	for i := 0; i < len(clean) && len(d.U) < 20; i++ {
		if clean[i].Growth > 0 {
			d.U = append(d.U, mk(clean[i]))
		}
	}
	for i := len(clean) - 1; i >= 0 && len(d.D) < 20; i-- {
		if clean[i].Growth < 0 {
			d.D = append(d.D, mk(clean[i]))
		}
	}
	return d
}

// OutlookCountry 旧的 /career-outlook/{cc}：内容已并入 hub，301 到锚点。
// 保留 301 而非 404，是为了不丢已被抓取/外链的国家 URL 的权重。
func OutlookCountry(w http.ResponseWriter, ctx *Ctx, cc string) {
	if !inCountries(cc) || !data.HasOutlook(cc) {
		notFound(w, ctx)
		return
	}
	w.Header().Set("Location", ctx.WithL("/career-outlook")+"#"+cc)
	w.WriteHeader(http.StatusMovedPermanently)
}
