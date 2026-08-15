package web

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sort"
	"sync"

	"aijobrisk/internal/data"
)

// dataRow 公开数据集一行（精简、稳定，供 AI/记者直接引用）。
type dataRow struct {
	Slug string `json:"slug"`
	Name string `json:"name"`
	Cat  string `json:"category"`
	Pct  int    `json:"ai_exposure_pct"`
	Band string `json:"band"`
}

var (
	dataOnce sync.Once
	dataAll  []dataRow // 按 AI 暴露分降序（全球去重职业）
)

// buildDataRows 遍历全球去重职业，取 AIOE 暴露分，构建一次并缓存。
func buildDataRows() {
	for _, s := range data.JobSlugs {
		if data.IsNEC(s) { // n.e.c. 兜底桶不入公开榜
			continue
		}
		g := data.JobBySlug(s)
		if g == nil {
			continue
		}
		rep := data.OccFull(g.Rep)
		if rep.AI == nil {
			continue
		}
		p := rep.AI.AioePct.Ptr()
		if p == nil {
			continue
		}
		dataAll = append(dataAll, dataRow{
			Slug: s, Name: rep.NameEn, Cat: rep.Category,
			Pct: int(*p + 0.5), Band: data.ExpBand(p).Cls,
		})
	}
	sort.SliceStable(dataAll, func(i, j int) bool { return dataAll[i].Pct > dataAll[j].Pct })
}

// DataVM /data 视图模型。
type DataVM struct {
	*Ctx
	Risky, Safe []dataRow
	Updated     string
	Total       int
	// 可引用统计（喂 GEO / 命中 “ai replacing jobs statistics”）。
	HighPct, MidPct, LowPct int
	HighN, LowN             int
	Countries               int
}

// DataPage /data：Top 100 高危 / Top 100 安全职业（机器可爬 HTML 表 + JSON 链接）。
func DataPage(w http.ResponseWriter, ctx *Ctx) {
	dataOnce.Do(buildDataRows)
	n := 100
	risky := dataAll
	if len(risky) > n {
		risky = risky[:n]
	}
	safe := make([]dataRow, len(dataAll))
	copy(safe, dataAll)
	sort.SliceStable(safe, func(i, j int) bool { return safe[i].Pct < safe[j].Pct })
	if len(safe) > n {
		safe = safe[:n]
	}
	// 全局暴露分布（可引用统计）。
	high, mid, low := 0, 0, 0
	for _, r := range dataAll {
		switch {
		case r.Pct >= 70:
			high++
		case r.Pct >= 40:
			mid++
		default:
			low++
		}
	}
	pct := func(n int) int {
		if len(dataAll) == 0 {
			return 0
		}
		return int(float64(n)/float64(len(dataAll))*100 + 0.5)
	}
	vm := &DataVM{Ctx: ctx, Risky: risky, Safe: safe, Updated: DataUpdated, Total: len(dataAll),
		HighPct: pct(high), MidPct: pct(mid), LowPct: pct(low), HighN: high, LowN: low,
		Countries: len(data.COUNTRIES)}
	ctx.Active = ""
	// 统计枢纽措辞：命中 “ai replacing jobs statistics / ai job replacement statistics”。
	ctx.Title = "AI Job Replacement Statistics 2026 — exposure data for " + data.Comma(len(dataAll)) + " occupations | AI Job Risk"
	ctx.Description = fmt.Sprintf("AI job statistics: %d%% of the %s occupations we track are highly exposed to generative AI, %d%% moderately, %d%% low. Machine-readable ranking of the most-exposed and safest jobs, plus an open JSON dataset.",
		vm.HighPct, data.Comma(len(dataAll)), vm.MidPct, vm.LowPct)
	ctx.JSONLD = datasetLD(ctx.Site, ctx.CanonicalURL(), "AI Job Risk — occupation exposure dataset", ctx.Description)
	renderPage(w, "data.html", vm)
}

// DataJSON /data/occupations.json：全量公开数据集（供 Perplexity 等直接爬取）。
func DataJSON(w http.ResponseWriter, ctx *Ctx) {
	dataOnce.Do(buildDataRows)
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	b, _ := json.Marshal(map[string]any{
		"updated":     DataUpdated,
		"count":       len(dataAll),
		"source":      "https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure",
		"license":     "https://creativecommons.org/licenses/by/4.0/",
		"occupations": dataAll,
	})
	w.Write(b)
}
