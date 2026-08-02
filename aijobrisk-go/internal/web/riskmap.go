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

// RiskMeta 供客户端 tooltip（SSR 内联，短键对齐 RiskMap.astro）。
type RiskMeta struct {
	N   string   `json:"n"`   // 职业名（已本地化）
	C   string   `json:"c"`   // 分类名（已本地化）
	W   float64  `json:"w"`   // 从业人数
	R   float64  `json:"r"`   // AI 风险 1..10（一位小数）
	A   *float64 `json:"a"`   // 平均薪资（可空）
	Cur string   `json:"cur"` // 货币
	U   string   `json:"u"`   // 职业链接
	Col string   `json:"col"` // 方块颜色
}

// riskMeta 由缓存几何 + 当前语言生成 tooltip meta（方案 B：每请求只本地化这一层）。
func riskMeta(layout *data.RiskLayout, cl, loc string) []RiskMeta {
	out := make([]RiskMeta, len(layout.Occs))
	for i, o := range layout.Occs {
		out[i] = RiskMeta{
			N: data.Tr(o.Name, cl), C: data.Tr(o.Cat, cl), W: o.Workforce,
			R: float64(int(o.Risk*10+0.5)) / 10, A: o.AvgSalary, Cur: o.Currency,
			U: i18n.HrefJob(loc, o.Slug, ""), Col: data.RiskColor(o.Risk),
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
	FootText     string
	HeadingSub   string
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
		"clickOpen": data.Tr("Click to open", cl),
	})

	var cflag template.HTML
	if !global {
		cflag = data.CountryFlag(country)
	}
	vm := &RiskMapVM{
		Ctx: ctx, Global: global, CountryName: cn, CountryFlag: cflag, SVG: svg,
		MetaJSON: template.JS(metaJSON), TJSON: template.JS(tJSON),
		Total: layout.Total, TotalWorkers: data.Comma(int(totalWorkers + 0.5)),
		HasData: layout.HasData,
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
