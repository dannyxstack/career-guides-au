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
	{"pt", "Português", "pt", "pt"},
	{"ja", "日本語", "ja", "ja"},
	{"zh-Hans", "简体中文", "zh-CN", "zh-Hans"},
	{"ko", "한국어", "en", "ko"},
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
var indexableDisplay = map[string]bool{"en": true, "es": true, "fr": true}

// IsIndexable 该显示语言的页面是否允许索引（翻译已完整）。
func IsIndexable(code string) bool { return indexableDisplay[code] }

// RetiredLocales 已下线的旧显示语言：其 URL 前缀 301 回英文对应页。
var RetiredLocales = map[string]bool{"de": true}

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
func HrefSearch(d string) string      { return WithL(d, "/search") }
func HrefAbout(d string) string       { return WithL(d, "/about") }
func HrefMethodology(d string) string { return WithL(d, "/methodology") }
func HrefHome(d string) string        { return WithL(d, "/") }
