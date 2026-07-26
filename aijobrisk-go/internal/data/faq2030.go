package data

import (
	"fmt"
	"strings"
)

type faq2030T struct {
	Q     map[string]string            `json:"q"`
	Label map[string]map[string]string `json:"label"`
	A1    map[string]string            `json:"a1"`
	AMoat map[string]string            `json:"aMoat"`
	A2    map[string]string            `json:"a2"`
}

var faq2030 faq2030T

func loadFAQ2030() error { return readJSON("faq_2030.json", &faq2030) }

func pickLoc(m map[string]string, loc string) string {
	if v, ok := m[loc]; ok {
		return v
	}
	return m["en"]
}

// Build2030 生成职业详情页的「2030 年」通用 FAQ 问答（按显示语言 loc）。
// 对齐 [...country].astro：问答本地化、注入 {name}/{level}/{moat}，不泄漏英文 verdict。
func Build2030(loc, dispName, bandCls, bandLabel string, aioe, exposure, moat *float64) (q, a string) {
	fill := func(s string) string { return strings.ReplaceAll(s, "{name}", dispName) }
	q = fill(pickLoc(faq2030.Q, loc))

	lvlLabel := bandLabel
	if lm, ok := faq2030.Label[loc]; ok {
		if v, ok := lm[bandCls]; ok {
			lvlLabel = v
		}
	}
	var level string
	switch {
	case aioe != nil:
		level = fmt.Sprintf("%s (%d/100)", lvlLabel, int(*aioe+0.5))
	case exposure != nil:
		level = fmt.Sprintf("%s (%.1f/10)", lvlLabel, *exposure)
	default:
		level = lvlLabel
	}
	a = strings.ReplaceAll(fill(pickLoc(faq2030.A1, loc)), "{level}", level)
	if moat != nil {
		a += strings.ReplaceAll(pickLoc(faq2030.AMoat, loc), "{moat}", fmt.Sprintf("%.1f", *moat))
	}
	a += pickLoc(faq2030.A2, loc)
	return q, a
}
