package web

import (
	"html/template"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

// SiteName 站名。
const SiteName = "AI Job Risk"

// LocaleURL 语言下拉 / hreflang 用。
type LocaleURL struct {
	Code, Label, Hreflang, Href string
}

// NavItem 顶部导航项。
type NavItem struct {
	Key, Label, Href string
	On               bool
}

// Ctx 每个页面共享的渲染上下文（页面 VM 内嵌 *Ctx）。
type Ctx struct {
	Loc         string // 显示语言
	CL          string // 内容层 locale
	Site        string // 站点绝对根，如 https://aijobrisk.com
	Active      string // 当前导航高亮 key
	Title       string
	Description string
	Bare        string // 去语言前缀的英文裸路径
	Query       string // 原始 query（含 ? 或空）
	JSONLD      template.JS
	Noindex     bool // 方案 C3：n.e.c. 兜底桶页面 noindex,follow
}

func (c *Ctx) Tr(s string) string  { return data.Tr(s, c.CL) }
func (c *Ctx) WithL(p string) string { return i18n.WithL(c.Loc, p) }

func (c *Ctx) HrefHome() string                 { return i18n.HrefHome(c.Loc) }
func (c *Ctx) HrefJob(slug string) string        { return i18n.HrefJob(c.Loc, slug, "") }
func (c *Ctx) HrefJobC(slug, cc string) string    { return i18n.HrefJob(c.Loc, slug, cc) }
func (c *Ctx) HrefIndustries() string             { return i18n.HrefIndustries(c.Loc, "") }
func (c *Ctx) HrefRankings() string               { return i18n.HrefRankings(c.Loc, "") }
func (c *Ctx) HrefCompare() string                { return i18n.HrefCompare(c.Loc, "") }
func (c *Ctx) HrefSearch() string                 { return i18n.HrefSearch(c.Loc) }
func (c *Ctx) HrefMethodology() string            { return i18n.HrefMethodology(c.Loc) }
func (c *Ctx) HrefAbout() string                  { return i18n.HrefAbout(c.Loc) }

// SiteName 供模板使用。
func (c *Ctx) SiteName() string { return SiteName }

// CanonicalURL 当前页 canonical（语言前缀 + 裸路径）。
func (c *Ctx) CanonicalURL() string {
	return c.Site + i18n.WithL(c.Loc, c.Bare)
}

// Nav 顶部导航项（已本地化 + 高亮）。
func (c *Ctx) Nav() []NavItem {
	defs := []struct{ key, label, href string }{
		{"occupations", "Occupations", "/"},
		{"rankings", "Rankings", "/rankings"},
		{"industries", "Industries", "/industries"},
		{"map", "Risk map", "/job-risk-map"},
		{"compare", "Compare", "/compare"},
		{"about", "About", "/about"},
	}
	out := make([]NavItem, len(defs))
	for i, d := range defs {
		out[i] = NavItem{Key: d.key, Label: c.Tr(d.label), Href: i18n.WithL(c.Loc, d.href), On: c.Active == d.key}
	}
	return out
}

// LangOptions 语言下拉（对齐 Base.astro：隐藏 de/ko）。
func (c *Ctx) LangOptions() []LocaleURL {
	var out []LocaleURL
	for _, d := range i18n.DisplayLocales {
		if d.Code == "de" || d.Code == "ko" {
			continue
		}
		out = append(out, LocaleURL{Code: d.Code, Label: d.Label, Hreflang: d.Hreflang,
			Href: i18n.WithL(d.Code, c.Bare) + c.Query})
	}
	return out
}

// Alternates hreflang 备用链接（全部 8 语言 + x-default）。
func (c *Ctx) Alternates() []LocaleURL {
	var out []LocaleURL
	for _, d := range i18n.DisplayLocales {
		out = append(out, LocaleURL{Code: d.Code, Hreflang: d.Hreflang,
			Href: c.Site + i18n.WithL(d.Code, c.Bare)})
	}
	return out
}

// XDefault hreflang x-default（英文裸 URL）。
func (c *Ctx) XDefault() string { return c.Site + c.Bare }

// CurLoc 当前显示语言码（下拉 selected 判断用）。
func (c *Ctx) CurLoc() string { return c.Loc }
