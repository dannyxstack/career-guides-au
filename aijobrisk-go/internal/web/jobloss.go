package web

import (
	"encoding/json"
	"html/template"
	"net/http"
	"sort"

	"aijobrisk/internal/data"
	"aijobrisk/internal/model"
)

// AI job loss by 2030 页面（英文版；文案后续接 Tr 翻译）。
// 模型见 internal/data/jobloss.go（A1 情景带，与 job-treemap 同口径）。

type jlCountryRow struct {
	CC, Name, Href                string
	Jobs                          int
	CountLow, CountMid, CountHigh int
	RatePct                       float64
}

type jlOccRow struct {
	Title                         string
	Jobs                          int
	CountLow, CountMid, CountHigh int
	RatePct                       float64
}

// JobLossHubVM /ai-job-loss-2030。
type JobLossHubVM struct {
	*Ctx
	Agg          data.LossAgg
	MidTargetPct int
	NCountries   int
	Countries    []jlCountryRow
	TopOccs      []jlOccRow
}

// JobLossCountryVM /ai-job-loss-2030/{cc}。
type JobLossCountryVM struct {
	*Ctx
	CC      string
	Name    string
	Agg     data.LossAgg
	TopOccs []jlOccRow
	HubHref string
}

// jobLossOccVM 职业详情页内嵌的「到 2030 的 AI 岗位影响」小块。
type jobLossOccVM struct {
	CountLow, CountMid, CountHigh int
	RatePct                       float64
	Jobs                          int
	HubHref, CountryHref          string
	CountryName                   string
}

func buildJobLossOcc(o *model.Occ, ctx *Ctx) *jobLossOccVM {
	l := data.OccLoss(o)
	if l == nil || l.CountMid <= 0 {
		return nil
	}
	return &jobLossOccVM{
		CountLow: l.CountLow, CountMid: l.CountMid, CountHigh: l.CountHigh,
		RatePct: l.RateMid * 100, Jobs: l.Jobs,
		HubHref:     ctx.WithL("/ai-job-loss-2030"),
		CountryHref: ctx.WithL("/ai-job-loss-2030/" + o.Country),
		CountryName: data.CountryName(o.Country, ctx.CL),
	}
}

func occsByCountry() map[string][]*model.Occ {
	m := map[string][]*model.Occ{}
	for _, o := range data.Occupations {
		m[o.Country] = append(m[o.Country], o)
	}
	return m
}

// topOccRows 取一组职业里中档流失最多的 n 个。
func topOccRows(occs []*model.Occ, n int) []jlOccRow {
	var rows []jlOccRow
	for _, o := range occs {
		if l := data.OccLoss(o); l != nil && l.CountMid > 0 {
			rows = append(rows, jlOccRow{
				Title: o.NameEn, Jobs: l.Jobs,
				CountLow: l.CountLow, CountMid: l.CountMid, CountHigh: l.CountHigh,
				RatePct: l.RateMid * 100,
			})
		}
	}
	sort.SliceStable(rows, func(i, j int) bool { return rows[i].CountMid > rows[j].CountMid })
	if len(rows) > n {
		rows = rows[:n]
	}
	return rows
}

func datasetLD(site, url, name, desc string) template.JS {
	ld := map[string]any{
		"@context":    "https://schema.org",
		"@type":       "Dataset",
		"name":        name,
		"description": desc,
		"url":         url,
		"creator":     map[string]any{"@type": "Organization", "name": SiteName, "url": site},
		"license":     "https://creativecommons.org/licenses/by/4.0/",
		"isBasedOn":   "https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure",
	}
	b, _ := json.Marshal(ld)
	return template.JS(b)
}

// JobLossHub /ai-job-loss-2030：全球总量 + 国家排行 + 全球 Top 职业。
func JobLossHub(w http.ResponseWriter, ctx *Ctx) {
	byCC := occsByCountry()
	var rows []jlCountryRow
	var g data.LossAgg
	occAgg := map[string]int{}
	occJobs := map[string]int{}
	for cc, occs := range byCC {
		a := data.AggregateLoss(occs)
		if a.Jobs == 0 {
			continue
		}
		g.Jobs += a.Jobs
		g.CountLow += a.CountLow
		g.CountMid += a.CountMid
		g.CountHigh += a.CountHigh
		rows = append(rows, jlCountryRow{
			CC: cc, Name: data.CountryName(cc, ctx.CL),
			Href:     ctx.WithL("/ai-job-loss-2030/" + cc),
			Jobs:     a.Jobs,
			CountLow: a.CountLow, CountMid: a.CountMid, CountHigh: a.CountHigh,
			RatePct: a.RateMid * 100,
		})
		for _, o := range occs {
			if l := data.OccLoss(o); l != nil {
				occAgg[o.NameEn] += l.CountMid
				occJobs[o.NameEn] += l.Jobs
			}
		}
	}
	if g.Jobs > 0 {
		g.RateLow = float64(g.CountLow) / float64(g.Jobs)
		g.RateMid = float64(g.CountMid) / float64(g.Jobs)
		g.RateHigh = float64(g.CountHigh) / float64(g.Jobs)
	}
	sort.SliceStable(rows, func(i, j int) bool { return rows[i].CountMid > rows[j].CountMid })

	var top []jlOccRow
	for name, mid := range occAgg {
		top = append(top, jlOccRow{Title: name, CountMid: mid, Jobs: occJobs[name]})
	}
	sort.SliceStable(top, func(i, j int) bool { return top[i].CountMid > top[j].CountMid })
	if len(top) > 20 {
		top = top[:20]
	}

	ctx.Active = "jobloss"
	ctx.Title = "How many jobs will AI replace by 2030? — country estimates | " + SiteName
	ctx.Description = "A transparent scenario estimate of AI-driven job loss by 2030 across " +
		data.Comma(len(rows)) + " countries: low/mid/high ranges by country and occupation, built on ILO GenAI exposure research."
	ctx.JSONLD = datasetLD(ctx.Site, ctx.CanonicalURL(),
		"AI job loss by 2030 by country", ctx.Description)
	midTarget := data.LossMidTarget * 100
	renderPage(w, "job_loss_hub.html", &JobLossHubVM{
		Ctx: ctx, Agg: g, MidTargetPct: int(midTarget + 0.5),
		NCountries: len(rows), Countries: rows, TopOccs: top,
	})
}

// JobLossCountry /ai-job-loss-2030/{cc}。
func JobLossCountry(w http.ResponseWriter, ctx *Ctx, cc string) {
	occs := occsByCountry()[cc]
	if len(occs) == 0 {
		notFound(w, ctx)
		return
	}
	a := data.AggregateLoss(occs)
	name := data.CountryName(cc, ctx.CL)
	ctx.Active = "jobloss"
	ctx.Title = "AI job loss in " + name + " by 2030 — scenario estimate | " + SiteName
	ctx.Description = "How many jobs could AI cost " + name + " by 2030: low/mid/high estimates and the most exposed occupations, from ILO GenAI exposure research."
	ctx.JSONLD = datasetLD(ctx.Site, ctx.CanonicalURL(),
		"AI job loss in "+name+" by 2030", ctx.Description)
	renderPage(w, "job_loss_country.html", &JobLossCountryVM{
		Ctx: ctx, CC: cc, Name: name, Agg: a,
		TopOccs: topOccRows(occs, 20),
		HubHref: ctx.WithL("/ai-job-loss-2030"),
	})
}
