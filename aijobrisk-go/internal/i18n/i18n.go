// Package i18n 对齐 aijobrisk/src/lib/i18n.ts：显示语言在 URL 第一级，国家在末级，英文裸路径无前缀。
package i18n

import "strings"

// DisplayInfo 显示语言。Content = 供 tr()/name() 用的数据层 locale。
type DisplayInfo struct {
	Code     string
	Label    string
	Content  string
	Hreflang string
}

// DisplayLocales nav 语言下拉顺序（fr 已映射到 fr）。
var DisplayLocales = []DisplayInfo{
	{"en", "English", "en", "en"},
	{"es", "Español", "es", "es"},
	{"fr", "Français", "fr", "fr"},
	{"ja", "日本語", "ja", "ja"},
	{"zh-Hans", "简体中文", "zh-CN", "zh-Hans"},
}

var codeSet = func() map[string]DisplayInfo {
	m := map[string]DisplayInfo{}
	for _, d := range DisplayLocales {
		m[d.Code] = d
	}
	return m
}()

// IsDisplay 是否合法显示语言码。
func IsDisplay(x string) bool { _, ok := codeSet[x]; return ok }

// indexableDisplay 翻译已完整、允许被搜索引擎索引的显示语言；
// 其余语言页整体 noindex（半英文兜底≈重复英文页），补齐后把该码加入即放开。
// zh-Hans 覆盖 94.4% 于 2026-09-09 放开；ja 仍缺四成，见 hiddenDisplay。
var indexableDisplay = map[string]bool{"en": true, "es": true, "fr": true, "zh-Hans": true}

// hiddenDisplay 暂时不对外暴露入口的显示语言：URL 仍可访问、译文照常渲染，
// 但不进 nav 下拉、不发 hreflang、不进 sitemap alternate——避免把半英文页面
// 推给用户和搜索引擎。翻译补齐后从这里移除即可，无需改动其它地方。
// ja 覆盖仅 59.6%（缺 168,201 条 / 28.3M 字符）。
var hiddenDisplay = map[string]bool{"ja": true}

// IsHidden 该显示语言是否暂时隐藏入口。
func IsHidden(code string) bool { return hiddenDisplay[code] }

// IsIndexable 该显示语言的页面是否允许索引（翻译已完整且入口未隐藏）。
func IsIndexable(code string) bool { return indexableDisplay[code] && !hiddenDisplay[code] }

// PublicDisplayLocales 对外暴露的显示语言：nav 下拉 / hreflang / sitemap alternate 用。
// 与 DisplayLocales 的区别仅在于剔除 hiddenDisplay——载入译文、路由仍以后者为准。
func PublicDisplayLocales() []DisplayInfo {
	out := make([]DisplayInfo, 0, len(DisplayLocales))
	for _, d := range DisplayLocales {
		if hiddenDisplay[d.Code] {
			continue
		}
		out = append(out, d)
	}
	return out
}

// RetiredLocales 已下线的旧显示语言：其 URL 前缀 301 回英文对应页。
var RetiredLocales = map[string]bool{"de": true, "pt": true, "ko": true}

// ContentLocale 显示语言 -> 数据层 locale（未知回退 en）。
func ContentLocale(d string) string {
	if info, ok := codeSet[d]; ok {
		return info.Content
	}
	return "en"
}

// WithL 给英文裸路径加语言前缀（en 不加）。
func WithL(d, path string) string {
	if d == "en" {
		return path
	}
	if path == "/" {
		return "/" + d
	}
	return "/" + d + path
}

// StripLocale 去掉 pathname 的语言前缀 -> 英文裸路径。
func StripLocale(pathname string) string {
	parts := strings.Split(pathname, "/")
	if len(parts) > 1 && parts[1] != "" && parts[1] != "en" && IsDisplay(parts[1]) {
		rest := "/" + strings.Join(parts[2:], "/")
		if rest == "/" {
			return "/"
		}
		return strings.TrimSuffix(rest, "/")
	}
	return pathname
}

// SplitLocale 从 pathname 剥出（显示语言, 英文裸路径）。无前缀返回 ("en", pathname)。
func SplitLocale(pathname string) (loc, bare string) {
	parts := strings.Split(pathname, "/")
	if len(parts) > 1 && IsDisplay(parts[1]) && parts[1] != "en" {
		rest := "/" + strings.Join(parts[2:], "/")
		if rest != "/" {
			rest = strings.TrimSuffix(rest, "/")
		}
		return parts[1], rest
	}
	return "en", pathname
}

// —— 链接构造（语言前缀 + 国家末级）——

func HrefJob(d, slug, country string) string {
	if country != "" {
		return WithL(d, "/jobs/"+slug+"/"+country)
	}
	return WithL(d, "/jobs/"+slug)
}
func HrefIndustries(d, country string) string {
	if country != "" {
		return WithL(d, "/industries/"+country)
	}
	return WithL(d, "/industries")
}
func HrefIndustry(d, sector, country string) string {
	if country != "" {
		return WithL(d, "/industry/"+sector+"/"+country)
	}
	return WithL(d, "/industry/"+sector)
}
func HrefRankings(d, country string) string {
	if country != "" {
		return WithL(d, "/rankings/"+country)
	}
	return WithL(d, "/rankings")
}
func HrefBoard(d, board, country string) string {
	if country != "" {
		return WithL(d, "/rankings/"+board+"/"+country)
	}
	return WithL(d, "/rankings/"+board)
}
func HrefCompare(d, pair string) string {
	if pair != "" {
		return WithL(d, "/compare/"+pair)
	}
	return WithL(d, "/compare")
}
func HrefMap(d, country string) string {
	if country != "" {
		return WithL(d, "/job-risk-map/"+country)
	}
	return WithL(d, "/job-risk-map")
}
func HrefBlog(d string) string           { return WithL(d, "/blog") }
func HrefBlogPost(d, slug string) string { return WithL(d, "/blog/"+slug) }
func HrefBlogTag(d, tag string) string   { return WithL(d, "/blog/tag/"+tag) }
func HrefSearch(d string) string         { return WithL(d, "/search") }
func HrefAbout(d string) string          { return WithL(d, "/about") }
func HrefMethodology(d string) string    { return WithL(d, "/methodology") }
func HrefHome(d string) string           { return WithL(d, "/") }
