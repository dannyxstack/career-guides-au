package web

import (
	"fmt"
	"html/template"
	"io"
	"path/filepath"
)

var funcMap = template.FuncMap{
	"comma":    commaAny,
	"safeHTML": func(s string) template.HTML { return template.HTML(s) },
	"safeCSS":  func(s string) template.CSS { return template.CSS(s) },
	"attr":     func(s string) template.HTMLAttr { return template.HTMLAttr(s) },
	"add":      func(a, b int) int { return a + b },
	"pct":      func(f float64) string { return fmt.Sprintf("%.1f%%", f*100) },
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
	for _, fpath := range files {
		name := filepath.Base(fpath)
		if name == "base.html" {
			continue
		}
		t := template.New("").Funcs(funcMap)
		if _, err := t.ParseFiles(base, fpath); err != nil {
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
