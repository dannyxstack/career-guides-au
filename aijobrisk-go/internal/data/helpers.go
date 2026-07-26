package data

import (
	"strconv"
	"strings"
)

func itoa(n int) string { return strconv.Itoa(n) }

// Band AI 暴露 / 风险语义档。
type Band struct {
	Label string
	Cls   string
}

// ExpBand 生成式 AI 暴露百分位（0-100）-> 语义档（对齐 ui.ts expBand）。
func ExpBand(pct *float64) Band {
	if pct == nil {
		return Band{"n/a", "verylow"}
	}
	v := *pct
	switch {
	case v >= 90:
		return Band{"critical", "critical"}
	case v >= 70:
		return Band{"high", "high"}
	case v >= 40:
		return Band{"moderate", "moderate"}
	case v >= 20:
		return Band{"low", "low"}
	default:
		return Band{"very low", "verylow"}
	}
}

// RiskBand10 10 分制自动化暴露 -> 简档。
func RiskBand10(v *float64) Band {
	if v == nil {
		return Band{"Unknown", "verylow"}
	}
	switch {
	case *v >= 7:
		return Band{"High", "high"}
	case *v >= 4.5:
		return Band{"Moderate", "moderate"}
	default:
		return Band{"Lower", "low"}
	}
}

// Comma 千分位整数格式（en-US 风格）。
func Comma(n int) string {
	s := strconv.Itoa(n)
	neg := strings.HasPrefix(s, "-")
	if neg {
		s = s[1:]
	}
	var b strings.Builder
	for i, c := range s {
		if i > 0 && (len(s)-i)%3 == 0 {
			b.WriteByte(',')
		}
		b.WriteRune(c)
	}
	if neg {
		return "-" + b.String()
	}
	return b.String()
}

// FmtNum 四舍五入 + 千分位；nil -> "—"。
func FmtNum(n *float64) string {
	if n == nil {
		return "—"
	}
	return Comma(int(*n + 0.5))
}

var currencySymbol = map[string]string{
	"AUD": "A$", "NZD": "NZ$", "CAD": "C$", "USD": "$", "GBP": "£",
	"EUR": "€", "JPY": "¥", "KRW": "₩", "INR": "₹",
}

// FmtSalary 货币格式（符号 + 千分位）；nil -> "—"。
func FmtSalary(v *float64, country string) string {
	if v == nil {
		return "—"
	}
	cur := "USD"
	if country != "" {
		if c, ok := CURRENCY[country]; ok {
			cur = c
		}
	}
	sym := currencySymbol[cur]
	if sym == "" {
		return Comma(int(*v+0.5)) + " " + cur
	}
	return sym + Comma(int(*v+0.5))
}
