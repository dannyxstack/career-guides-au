package web

import (
	"fmt"
	"html/template"
	"io"
	"path/filepath"
	"strings"
	"time"
)

var funcMap = template.FuncMap{
	"comma":    commaAny,
	"safeHTML": func(s string) template.HTML { return template.HTML(s) },
	"safeCSS":  func(s string) template.CSS { return template.CSS(s) },
	"attr":     func(s string) template.HTMLAttr { return template.HTMLAttr(s) },
	"add":      func(a, b int) int { return a + b },
	"pct":      func(f float64) string { return fmt.Sprintf("%.1f%%", f*100) },
	"fmtdate":  fmtdate,
}

// fmtdate 把 ISO 日期 "2006-01-02" 显示为 "January 2, 2006"（解析失败原样返回）。
func fmtdate(iso string) string {
	t, err := time.Parse("2006-01-02", iso)
	if err != nil {
		return iso
	}
	return t.Format("January 2, 2006")
}

func commaAny(v any) string {
	switch n := v.(type) {
	case int:
		return comma(n)
	case float64:
		return comma(int(n + 0.5))
	}
	return fmt.Sprint(v)
}

func comma(n int) string {
	s := fmt.Sprintf("%d", n)
	neg := false
	if len(s) > 0 && s[0] == '-' {
		neg, s = true, s[1:]
	}
	out := make([]byte, 0, len(s)+len(s)/3)
	for i := 0; i < len(s); i++ {
		if i > 0 && (len(s)-i)%3 == 0 {
			out = append(out, ',')
		}
		out = append(out, s[i])
	}
	if neg {
		return "-" + string(out)
	}
	return string(out)
}

var pages = map[string]*template.Template{}

// InitTemplates 解析 templates/ 下 base.html + 各页面模板。
func InitTemplates(dir string) error {
	base := filepath.Join(dir, "base.html")
	files, err := filepath.Glob(filepath.Join(dir, "*.html"))
	if err != nil {
		return err
	}
	// 共享 partial（_*.html，如 _adoption_chart.html）注入每个页面。
	var partials []string
	for _, fpath := range files {
		if strings.HasPrefix(filepath.Base(fpath), "_") {
			partials = append(partials, fpath)
		}
	}
	for _, fpath := range files {
		name := filepath.Base(fpath)
		if name == "base.html" || strings.HasPrefix(name, "_") {
			continue
		}
		t := template.New("").Funcs(funcMap)
		parse := append([]string{base}, partials...)
		parse = append(parse, fpath)
		if _, err := t.ParseFiles(parse...); err != nil {
			return fmt.Errorf("parse %s: %w", name, err)
		}
		pages[name] = t
	}
	return nil
}

// Render 用 base 布局渲染指定页面模板。
func Render(w io.Writer, page string, vm any) error {
	t, ok := pages[page]
	if !ok {
		return fmt.Errorf("template not found: %s", page)
	}
	return t.ExecuteTemplate(w, "base.html", vm)
}
