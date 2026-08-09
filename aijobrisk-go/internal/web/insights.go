package web

import (
	"net/http"

	"aijobrisk/internal/data"
)

// Insights 板块落地页：收纳专题（AI job loss 2030、Career outlook）。

type insightCard struct {
	Title, Desc, Href, Icon, Accent string
}

// InsightsVM /insights。
type InsightsVM struct {
	*Ctx
	Cards []insightCard
}

// Insights /insights：专题总览。
func Insights(w http.ResponseWriter, ctx *Ctx) {
	ctx.Active = "insights"
	ctx.Title = data.Tr("Insights", ctx.CL) + " — " + data.Tr("AI job loss & career outlook", ctx.CL) + " | " + SiteName
	ctx.Description = data.Tr("Data-driven views on the future of work: our AI-driven job-loss scenarios to 2030, and official employment projections for where jobs are growing or shrinking.", ctx.CL)
	renderPage(w, "insights.html", &InsightsVM{
		Ctx: ctx,
		Cards: []insightCard{
			{
				Title:  data.Tr("AI job loss by 2030", ctx.CL),
				Desc:   data.Tr("How many jobs AI could displace by 2030 — a transparent low/mid/high scenario across countries and occupations.", ctx.CL),
				Href:   ctx.WithL("/ai-job-loss-2030"),
				Icon:   "fa-robot",
				Accent: "high",
			},
			{
				Title:  data.Tr("Career outlook", ctx.CL),
				Desc:   data.Tr("Official employment projections — which occupations are growing or shrinking over the next decade, and which survive AI exposure.", ctx.CL),
				Href:   ctx.WithL("/career-outlook"),
				Icon:   "fa-arrow-trend-up",
				Accent: "low",
			},
		},
	})
}
