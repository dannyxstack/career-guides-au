package web

import (
	"fmt"
	"html"
	"html/template"
	"math"
	"strings"
)

// RadarSeries 雷达序列。
type RadarSeries struct {
	Name   string
	Color  string
	Values []float64
}

// RadarSVG 放射评分图（对齐 RatingRadar.astro，纯 SVG）。
func RadarSVG(labels []string, series []RadarSeries, max float64, ariaLabel string) template.HTML {
	const size = 360.0
	const padX = 88.0
	cx, cy := size/2, size/2
	R := size/2 - 56
	n := float64(len(labels))
	ang := func(i int) float64 { return (-90 + (float64(i)*360)/n) * math.Pi / 180 }
	pt := func(i int, r float64) (float64, float64) { return cx + r*math.Cos(ang(i)), cy + r*math.Sin(ang(i)) }
	fmtPt := func(x, y float64) string { return fmt.Sprintf("%.2f,%.2f", x, y) }

	var b strings.Builder
	b.WriteString(`<div class="radar"><svg viewBox="`)
	b.WriteString(fmt.Sprintf("%.0f 0 %.0f %.0f", -padX, size+2*padX, size))
	b.WriteString(`" width="100%" role="img" aria-label="` + html.EscapeString(ariaLabel) + `">`)

	// 环
	for _, rr := range []float64{0.25, 0.5, 0.75, 1} {
		pts := make([]string, len(labels))
		for i := range labels {
			x, y := pt(i, R*rr)
			pts[i] = fmtPt(x, y)
		}
		b.WriteString(`<polygon points="` + strings.Join(pts, " ") + `" class="ring" />`)
	}
	// 辐条
	for i := range labels {
		x, y := pt(i, R)
		b.WriteString(fmt.Sprintf(`<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" class="spoke" />`, cx, cy, x, y))
	}
	// 序列多边形
	for _, s := range series {
		pts := make([]string, len(s.Values))
		for i, v := range s.Values {
			vv := math.Max(0, math.Min(max, v))
			x, y := pt(i, (vv/max)*R)
			pts[i] = fmtPt(x, y)
		}
		b.WriteString(`<polygon points="` + strings.Join(pts, " ") + `" fill="` + html.EscapeString(s.Color) +
			`" fill-opacity="0.22" stroke="` + html.EscapeString(s.Color) + `" stroke-width="2.5" />`)
	}
	// 标签
	for i, l := range labels {
		x, y := pt(i, R+22)
		c := math.Cos(ang(i))
		anchor := "middle"
		if math.Abs(c) >= 0.3 {
			if c > 0 {
				anchor = "start"
			} else {
				anchor = "end"
			}
		}
		b.WriteString(fmt.Sprintf(`<text x="%.2f" y="%.2f" text-anchor="%s" class="rlabel">%s</text>`, x, y, anchor, html.EscapeString(l)))
	}
	b.WriteString(`</svg>`)
	if len(series) > 1 {
		b.WriteString(`<div class="legend">`)
		for _, s := range series {
			b.WriteString(`<span><i style="background:` + html.EscapeString(s.Color) + `"></i>` + html.EscapeString(s.Name) + `</span>`)
		}
		b.WriteString(`</div>`)
	}
	b.WriteString(`</div>`)
	return template.HTML(b.String())
}
