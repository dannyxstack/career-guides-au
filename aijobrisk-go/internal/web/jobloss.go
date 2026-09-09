package web

import (
	"encoding/json"
	"fmt"
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
// 各国明细内嵌为 JSON、客户端切换（#CC 深链），不再拆成 46 个 URL——
// 那些页面每国仅约 250 词且跨国结构逐字相同，Google 判为薄内容拒绝索引。
type JobLossHubVM struct {
	*Ctx
	Agg           data.LossAgg
	MidTargetPct  int
	NCountries    int
	Countries     []jlCountryRow
	TopOccs       []jlOccRow
	DetailJSON    template.JS
	DefaultCC     string
	DefaultCCName string
}

// jlDetail 单国明细，供客户端切换渲染。字段名压到 1-2 字符控制内嵌体积。
type jlDetail struct {
	N string   `json:"n"` // 国家名
	J int      `json:"j"` // workforce
	L int      `json:"l"` // 低
	M int      `json:"m"` // 中
	H int      `json:"h"` // 高
	R float64  `json:"r"` // 中位损失率 %
	O [][2]any `json:"o"` // [职业名, 中位损失数]
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
		CountryHref: ctx.WithL("/ai-job-loss-2030") + "#" + o.Country,
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
	b, _ := json.Marshal(datasetLDObj(site, url, name, desc))
	return template.JS(b)
}

// datasetLDObj 返回 Dataset schema.org 对象（供 jsonLD 与其它类型合并成数组）。
func datasetLDObj(site, url, name, desc string) map[string]any {
	ld := map[string]any{
		"@context":    "https://schema.org",
		"@type":       "Dataset",
		"name":        name,
		"description": desc,
		"url":         url,
		"creator":     map[string]any{"@type": "Organization", "name": SiteName, "url": site},
		"license":     "https://creativecommons.org/licenses/by/4.0/",
		"isBasedOn":   "https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure",
		"citation": []any{
			map[string]any{"@type": "CreativeWork",
				"name": "Generative AI and Jobs: A Refined Global Index of Occupational Exposure (ILO Working Paper 140)",
				"url":  "https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure"},
			map[string]any{"@type": "CreativeWork",
				"name": "GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models (Eloundou et al., 2023)",
				"url":  "https://arxiv.org/abs/2303.10130"},
		},
	}
	return ld
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
	midTarget := data.LossMidTarget * 100
	// FAQPage：问句直接命中 “how many jobs will AI replace by 2030 / 2050” 等关键词簇。
	hubFAQ := []faqRow{
		{Q: "How many jobs will AI replace by 2030?",
			A: fmt.Sprintf("On our mid scenario, generative AI could displace roughly %d%% of tasks across the occupations we track by 2030 — a reshaping of work rather than one-for-one job loss. We publish low/mid/high ranges for %s countries and the most-exposed occupations.", int(g.RateMid*100+0.5), data.Comma(len(rows)))},
		{Q: "How many jobs will AI replace by 2050?",
			A: "2050 is beyond the horizon of the underlying ILO exposure research, so we do not publish a 2050 figure. Our estimates run to 2030, where the task-exposure evidence is strongest; treat anything further out as speculative."},
		{Q: "Which jobs will AI replace first?",
			A: "The occupations with the highest generative-AI task exposure — clerical, routine writing and data roles top the list. See the most-exposed ranking and each country page for the specific occupations."},
	}
	ctx.JSONLD = jsonLD(
		datasetLDObj(ctx.Site, ctx.CanonicalURL(), "AI job loss by 2030 by country", ctx.Description),
		faqPageLD(hubFAQ),
	)
	// 各国明细内嵌：原 /ai-job-loss-2030/{cc} 的独有内容就是该国 top-20 职业表，
	// 搬到这里由客户端按 #CC 切换，URL 面从 47 收敛到 1。
	detail := map[string]jlDetail{}
	for _, r := range rows {
		occs := byCC[r.CC]
		if len(occs) == 0 {
			continue
		}
		d := jlDetail{N: r.Name, J: r.Jobs, L: r.CountLow, M: r.CountMid, H: r.CountHigh, R: r.RatePct}
		for _, o := range topOccRows(occs, 20) {
			d.O = append(d.O, [2]any{o.Title, o.CountMid})
		}
		detail[r.CC] = d
	}
	defCC := ""
	if len(rows) > 0 {
		defCC = rows[0].CC
	}
	renderPage(w, "job_loss_hub.html", &JobLossHubVM{
		Ctx: ctx, Agg: g, MidTargetPct: int(midTarget + 0.5),
		NCountries: len(rows), Countries: rows, TopOccs: top,
		DetailJSON: jsonJS(detail), DefaultCC: defCC, DefaultCCName: data.CountryName(defCC, ctx.CL),
	})
}

// JobLossCountry 旧的 /ai-job-loss-2030/{cc}：内容已并入 hub，301 到锚点。
// 保留 301 而非 404，是为了不丢已被抓取/外链的国家 URL 的权重。
func JobLossCountry(w http.ResponseWriter, ctx *Ctx, cc string) {
	if len(occsByCountry()[cc]) == 0 {
		notFound(w, ctx)
		return
	}
	w.Header().Set("Location", ctx.WithL("/ai-job-loss-2030")+"#"+cc)
	w.WriteHeader(http.StatusMovedPermanently)
}
