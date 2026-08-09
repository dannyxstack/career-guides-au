package web

import (
	"encoding/json"
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
	vm := &DataVM{Ctx: ctx, Risky: risky, Safe: safe, Updated: DataUpdated, Total: len(dataAll)}
	ctx.Active = ""
	ctx.Title = "AI Job Risk Data — Top 100 most exposed & safest occupations | AI Job Risk"
	ctx.Description = "Machine-readable ranking of occupations by generative-AI exposure: the 100 most-exposed and 100 safest jobs, plus a full open JSON dataset."
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
