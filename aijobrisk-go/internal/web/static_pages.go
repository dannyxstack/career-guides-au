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

// AboutVM / MethodologyVM 走 UI 字典（strings）。
type AboutVM struct {
	*Ctx
	Title    string
	Lead     string
	Sections []proseSection
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
