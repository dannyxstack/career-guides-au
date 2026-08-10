package web

import (
	"encoding/json"
	"html/template"

	"aijobrisk/internal/data"
)

// adoptionChartVM 行业 AI 采纳率折线图（实线过去 / 虚线未来，"现在"=2026）。
// 内嵌 *Ctx 以在 partial 中使用 .Tr（自有 Title 字段覆盖 Ctx.Title）。
type adoptionChartVM struct {
	*Ctx
	Title    string
	DataJSON template.JS // {"pts":[[year,pct,isProjected],...],"base":2026}
	Source   string
	Note     string
	USOnly   bool // 非美国国家：以美国轨迹为基准（暂无该国实测数据）
	IsProxy  bool // 该行业为代理值（BTOS 未覆盖，如政府/管理）
}

// buildAdoptionChart 由采纳率序列构建图表 VM（序列不足则返回 nil）。
func buildAdoptionChart(ctx *Ctx, series [][3]float64, title string, usOnly, isProxy bool) *adoptionChartVM {
	if len(series) < 2 {
		return nil
	}
	b, _ := json.Marshal(map[string]any{"pts": series, "base": 2026})
	return &adoptionChartVM{
		Ctx:      ctx,
		Title:    title,
		DataJSON: template.JS(b),
		Source:   data.AdoptionSource(),
		USOnly:   usOnly,
		IsProxy:  isProxy,
	}
}
