package web

import (
	"html/template"
	"net/http"

	"aijobrisk/internal/data"
)

type proseSection struct {
	H string
	B []string
}

// sourceRowVM 各国数据来源表一行。
type sourceRowVM struct {
	Country   string
	Authority template.HTML
	Class     string
	Tier      string // A/B/C
	TierText  string
	Pay       string
}

// AboutVM / MethodologyVM 走 UI 字典（strings）。
type AboutVM struct {
	*Ctx
	Title    string
	Lead     string
	Sections []proseSection
	// 数据来源与权威性
	SourcesH    string
	SourcesLead string
	SourceRows  []sourceRowVM
	TierAText   string
	TierBText   string
	TierCText   string
}

// About /about。
func About(w http.ResponseWriter, ctx *Ctx) {
	t := data.Strings(ctx.CL)
	vm := &AboutVM{
		Ctx: ctx, Title: t["abTitle"], Lead: t["abLead"],
		Sections: []proseSection{
			{t["abS1h"], []string{t["abS1"]}},
			{t["abS2h"], []string{t["abS2a"], t["abS2b"]}},
			{t["abS3h"], []string{t["abS3a"], t["abS3b"]}},
			{t["abS4h"], []string{t["abS4a"], t["abS4b"]}},
			{t["abS5h"], []string{t["abS5"]}},
			{t["abS6h"], []string{t["abS6"]}},
		},
	}
	// 各国数据来源与权威性（全 43 国来源表 + A/B/C 权威分层）
	yes := data.Tr("Official", ctx.CL)
	no := "—"
	for _, cc := range data.SourceOrder() {
		r, ok := data.SourceOf(cc)
		if !ok {
			continue
		}
		pay := no
		if r.OfficialPay {
			pay = yes
		}
		vm.SourceRows = append(vm.SourceRows, sourceRowVM{
			Country:   data.CountryName(cc, ctx.CL),
			Authority: data.SourceAuthorityHTML(cc),
			Class:     r.Class,
			Tier:      r.Tier,
			TierText:  data.TierLabel(r.Tier, ctx.CL),
			Pay:       pay,
		})
	}
	vm.SourcesH = data.Tr("Data sources & authority by country", ctx.CL)
	vm.SourcesLead = data.Tr("We currently cover 43 countries. Occupation employment and pay come from each country's own official statistics, graded by a three-level authority scale.", ctx.CL)
	vm.TierAText = data.TierLabel("A", ctx.CL)
	vm.TierBText = data.TierLabel("B", ctx.CL)
	vm.TierCText = data.TierLabel("C", ctx.CL)
	ctx.Active = "about"
	ctx.Title = "About — AI Job Risk"
	ctx.Description = t["abLead"]
	renderPage(w, "about.html", vm)
}

// MethodologyVM 方法论页。
type MethodologyVM struct {
	*Ctx
	AbAiExpH, AbS3h, AbS7h, RkSrcTitle string
	AbAiExpA, AbAiExpB                 template.HTML
	AbS3a, AbS3b, AbS7lead, RkMethod   string
}

// Methodology /methodology。
func Methodology(w http.ResponseWriter, ctx *Ctx) {
	t := data.Strings(ctx.CL)
	vm := &MethodologyVM{
		Ctx: ctx, AbAiExpH: t["abAiExpH"], AbS3h: t["abS3h"], AbS7h: t["abS7h"], RkSrcTitle: t["rkSrcTitle"],
		AbAiExpA: template.HTML(t["abAiExpA"]), AbAiExpB: template.HTML(t["abAiExpB"]),
		AbS3a: t["abS3a"], AbS3b: t["abS3b"], AbS7lead: t["abS7lead"], RkMethod: t["rkMethod"],
	}
	ctx.Active = "about"
	ctx.Title = "Methodology — how the AI Exposure Index is computed | AI Job Risk"
	ctx.Description = t["abAiExpA"]
	renderPage(w, "methodology.html", vm)
}
