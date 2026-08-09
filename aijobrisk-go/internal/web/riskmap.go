package web

import (
	"encoding/json"
	"fmt"
	"html"
	"html/template"
	"net/http"
	"sort"
	"strings"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

// RiskMeta 供客户端 tooltip + 按指标切换着色（SSR 内联，短键对齐 RiskMap.astro）。
type RiskMeta struct {
	N    string   `json:"n"`    // 职业名（已本地化）
	C    string   `json:"c"`    // 分类名（已本地化）
	W    float64  `json:"w"`    // 从业人数
	R    float64  `json:"r"`    // AI 风险 1..10（一位小数）
	A    *float64 `json:"a"`    // 平均薪资（可空）
	Med  *float64 `json:"med"`  // 薪资中位数（可空）
	Out  *float64 `json:"out"`  // outlook growth_pct（可空）
	Cur  string   `json:"cur"`  // 货币
	U    string   `json:"u"`    // 职业链接
	Col  string   `json:"col"`  // 风险色（默认）
	ColS string   `json:"colS"` // 平均薪资色（"" = 无数据）
	ColM string   `json:"colM"` // 中位数色（"" = 无数据）
	ColO string   `json:"colO"` // outlook 色（"" = 无数据）
}

// favColor 高值=绿、低值=红（薪资/前景，正向指标）；复用 RiskColor 的绿→红渐变。
func favColor(pct float64) string { return data.RiskColor(1 + (1-pct)*9) }

// pctColors 按当前地图内分位数为正向指标着色（无值返回 ""）。
func pctColors(vals []*float64) []string {
	type iv struct {
		i int
		v float64
	}
	var xs []iv
	for i, p := range vals {
		if p != nil {
			xs = append(xs, iv{i, *p})
		}
	}
	out := make([]string, len(vals))
	if len(xs) == 0 {
		return out
	}
	sort.SliceStable(xs, func(a, b int) bool { return xs[a].v < xs[b].v })
	n := len(xs)
	for rank, x := range xs {
		pct := 0.5
		if n > 1 {
			pct = float64(rank) / float64(n-1)
		}
		out[x.i] = favColor(pct)
	}
	return out
}

// riskMeta 由缓存几何 + 当前语言生成 tooltip meta（方案 B：每请求只本地化这一层）。
func riskMeta(layout *data.RiskLayout, cl, loc string) []RiskMeta {
	avg := make([]*float64, len(layout.Occs))
	med := make([]*float64, len(layout.Occs))
	grw := make([]*float64, len(layout.Occs))
	for i, o := range layout.Occs {
		avg[i], med[i], grw[i] = o.AvgSalary, o.MedSalary, o.Growth
	}
	colS, colM, colO := pctColors(avg), pctColors(med), pctColors(grw)
	out := make([]RiskMeta, len(layout.Occs))
	for i, o := range layout.Occs {
		out[i] = RiskMeta{
			N: data.Tr(o.Name, cl), C: data.Tr(o.Cat, cl), W: o.Workforce,
			R: float64(int(o.Risk*10+0.5)) / 10, A: o.AvgSalary, Med: o.MedSalary, Out: o.Growth,
			Cur: o.Currency, U: i18n.HrefJob(loc, o.Slug, ""), Col: data.RiskColor(o.Risk),
			ColS: colS[i], ColM: colM[i], ColO: colO[i],
		}
	}
	return out
}

// catLabel 分类标题是否放得下 + 截断（对齐 RiskMap.astro，rune 安全）。
func catLabel(text string, bw float64) string {
	if bw < 66 {
		return ""
	}
	max := int(bw/6.2) - 1
	r := []rune(text)
	if len(r) > max {
		cut := max - 1
		if cut < 1 {
			cut = 1
		}
		return string(r[:cut]) + "…"
	}
	return text
}

// riskMapSVG 由缓存几何 + 本地化分类标题构建整块 <svg>（tiles 用缓存 rects，颜色取 meta）。
func riskMapSVG(layout *data.RiskLayout, meta []RiskMeta, outlineKey, cl string) template.HTML {
	var b strings.Builder
	fmt.Fprintf(&b, `<svg viewBox="0 0 %.0f %.0f" class="rm-svg" preserveAspectRatio="xMidYMid meet" role="img" aria-label="%s">`,
		layout.W, layout.H, html.EscapeString(data.Tr("AI job risk treemap", cl)))
	if land := data.OutlinePath(outlineKey); land != "" {
		b.WriteString(`<g class="rm-outline" aria-hidden="true"><path class="rm-land" d="` + land + `" /><path class="rm-coast" d="` + land + `" /></g>`)
	}
	b.WriteString(`<g class="rm-tiles">`)
	for _, r := range layout.Rects {
		col := ""
		if r.I >= 0 && r.I < len(meta) {
			col = meta[r.I].Col
		}
		fmt.Fprintf(&b, `<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" data-i="%d" />`,
			r.X, r.Y, r.W, r.H, col, r.I)
	}
	b.WriteString(`</g><g class="rm-cats" aria-hidden="true">`)
	for _, bl := range layout.CatBlocks {
		lbl := catLabel(data.Tr(bl.Text, cl), bl.W)
		if lbl != "" {
			fmt.Fprintf(&b, `<text x="%.2f" y="%.2f">%s</text>`, bl.X+4, bl.Y+15, html.EscapeString(lbl))
		}
	}
	b.WriteString(`</g></svg>`)
	return template.HTML(b.String())
}

// RiskChip 区域切换 chip。
type RiskChip struct {
	Label string
	Name  string // 国家全名（hover title）
	Href  string
	Flag  template.HTML
	On    bool
	IsCC  bool
}

// RiskMapVM 风险地图页。
type RiskMapVM struct {
	*Ctx
	Global       bool
	CountryName  string
	CountryFlag  template.HTML
	SVG          template.HTML
	MetaJSON     template.JS
	TJSON        template.JS
	Chips        []RiskChip
	Total        int
	TotalWorkers string
	HasData      bool
	HasAvg       bool // 有平均薪资 → 显示切换
	HasMed       bool // 有薪资中位数 → 显示切换
	HasOut       bool // 有 outlook → 显示切换
	FootText     string
	HeadingSub   string
	FAQ          []faqEntry
}

// faqEntry 地图页 FAQ 条目。
type faqEntry struct{ Q, A string }

// mapFAQ 地图页 FAQ（英文母本，逐条 tr；本地化视图 + FAQPage 结构化数据共用）。
func mapFAQ(cl string) []faqEntry {
	src := [][2]string{
		{"What does this AI job risk map show?",
			"Each tile is an occupation. Its area is the number of people employed in it, and its colour shows the selected metric — by default AI automation exposure (green = lower, red = higher). Use the buttons above the map to recolour tiles by average pay, median pay or career outlook where that data is available."},
		{"How is the AI risk score calculated?",
			"The AI risk colour is each occupation's generative-AI task exposure, based on ILO Working Paper 140 and Eloundou et al., rescaled to a 1–10 automation-exposure score. It measures how much of the job's tasks AI can perform, not a prediction that the job will disappear. Full detail is on the methodology page."},
		{"Does a high AI risk mean the job will be replaced?",
			"No. A high score means many of the job's tasks are exposed to AI, but exposure often means AI augments the work rather than eliminating it. Read the score alongside the human moat and career outlook — a high-exposure job can still grow."},
		{"Where do the salary and workforce numbers come from?",
			"Workforce, salary and outlook figures come from each country's official statistics (e.g. ABS, BLS, Eurostat). Salaries are shown in the local currency, so pay colours are only comparable within a single country's map. See the About page for the full source list."},
		{"Why do some countries show fewer occupations, or no salary colours?",
			"Coverage depends on each country's official data. Occupations without a workforce figure are not drawn, and the pay or outlook buttons only appear when that data exists for the country you are viewing."},
		{"How often is the data updated?",
			"The dataset is versioned and refreshed as new official releases are published. The current data version is shown in the site footer and on the methodology page."},
	}
	out := make([]faqEntry, len(src))
	for i, qa := range src {
		out[i] = faqEntry{Q: data.Tr(qa[0], cl), A: data.Tr(qa[1], cl)}
	}
	return out
}

// faqLD 由 FAQ 条目构建 FAQPage JSON-LD。
func faqLD(items []faqEntry) template.JS {
	type ans struct {
		Type string `json:"@type"`
		Text string `json:"text"`
	}
	type q struct {
		Type   string `json:"@type"`
		Name   string `json:"name"`
		Answer ans    `json:"acceptedAnswer"`
	}
	doc := struct {
		Ctx    string `json:"@context"`
		Type   string `json:"@type"`
		Entity []q    `json:"mainEntity"`
	}{Ctx: "https://schema.org", Type: "FAQPage"}
	for _, it := range items {
		doc.Entity = append(doc.Entity, q{Type: "Question", Name: it.Q, Answer: ans{Type: "Answer", Text: it.A}})
	}
	b, _ := json.Marshal(doc)
	return template.JS(b)
}

// RiskMap /job-risk-map[/{cc}]（country=="" 为全球）。
func RiskMap(w http.ResponseWriter, ctx *Ctx, country string) {
	cl := ctx.CL
	global := country == ""
	key := "WORLD"
	cn := ""
	if !global {
		if !inCountries(country) {
			notFound(w, ctx)
			return
		}
		key = country
		cn = data.CountryName(country, cl)
	}

	layout := data.RiskLayoutFor(key)
	meta := riskMeta(layout, cl, ctx.Loc)
	svg := riskMapSVG(layout, meta, key, cl)

	totalWorkers := 0.0
	for _, m := range meta {
		totalWorkers += m.W
	}
	metaJSON, _ := json.Marshal(meta)
	tJSON, _ := json.Marshal(map[string]string{
		"category": data.Tr("Category", cl), "workforce": data.Tr("Workforce", cl),
		"aiRisk": data.Tr("AI risk", cl), "avgSalary": data.Tr("Avg salary", cl),
		"medSalary": data.Tr("Median salary", cl), "outlook": data.Tr("Career outlook", cl),
		"clickOpen": data.Tr("Click to open", cl), "noData": data.Tr("No data", cl),
		"lgRiskLo": data.Tr("Lower AI risk", cl), "lgRiskHi": data.Tr("Higher AI risk", cl),
		"lgHi": data.Tr("Higher", cl), "lgLo": data.Tr("Lower", cl),
	})

	// 指标可用性（决定是否显示切换按钮）。
	var hasAvg, hasMed, hasOut bool
	for _, m := range meta {
		if m.A != nil {
			hasAvg = true
		}
		if m.Med != nil {
			hasMed = true
		}
		if m.Out != nil {
			hasOut = true
		}
	}

	var cflag template.HTML
	if !global {
		cflag = data.CountryFlag(country)
	}
	vm := &RiskMapVM{
		Ctx: ctx, Global: global, CountryName: cn, CountryFlag: cflag, SVG: svg,
		MetaJSON: template.JS(metaJSON), TJSON: template.JS(tJSON),
		Total: layout.Total, TotalWorkers: data.Comma(int(totalWorkers + 0.5)),
		HasData: layout.HasData,
		HasAvg:  hasAvg && !global, HasMed: hasMed && !global, HasOut: hasOut && !global,
		FAQ: mapFAQ(cl),
	}
	// chips：World + 各国
	vm.Chips = append(vm.Chips, RiskChip{Label: data.Tr("World", cl), Href: i18n.HrefMap(ctx.Loc, ""), On: global})
	sortedCC := append([]string{}, data.COUNTRIES...)
	sort.Strings(sortedCC)
	for _, cc := range sortedCC {
		vm.Chips = append(vm.Chips, RiskChip{Label: cc, Name: data.CountryName(cc, cl), Href: i18n.HrefMap(ctx.Loc, cc),
			Flag: data.CountryFlag(cc), On: !global && cc == country, IsCC: true})
	}

	ctx.Active = "map"
	if global {
		vm.HeadingSub = data.Tr("Each tile is an occupation; area is its global workforce and colour is AI automation exposure (green = lower, red = higher). Hover for details, click to open the occupation.", cl)
		vm.FootText = data.Tr("Area ∝ workforce (sum across countries). Colour ∝ AI automation exposure (1–10). Estimates only.", cl)
		ctx.Title = data.Tr("Global AI Job Risk Map", cl) + " | AI Job Risk"
		ctx.Description = data.Tr("A treemap of the global workforce coloured by AI automation exposure — area is workforce, colour is AI risk.", cl)
	} else {
		vm.HeadingSub = data.Tr("Each tile is an occupation; area is its workforce and colour is AI automation exposure (green = lower, red = higher). Hover for details, click to open the occupation.", cl)
		vm.FootText = data.Tr("Area ∝ workforce. Colour ∝ AI automation exposure (1–10). Estimates only.", cl)
		ctx.Title = data.Tr("AI Job Risk Map", cl) + " — " + cn + " | AI Job Risk"
		ctx.Description = data.Tr("A treemap of the workforce coloured by AI automation exposure — area is workforce, colour is AI risk.", cl) + " · " + cn
	}
	ctx.JSONLD = faqLD(vm.FAQ)
	renderPage(w, "job_risk_map.html", vm)
}

func inCountries(cc string) bool {
	for _, c := range data.COUNTRIES {
		if c == cc {
			return true
		}
	}
	return false
}
