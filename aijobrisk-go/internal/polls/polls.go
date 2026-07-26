// Package polls 投票定义与纯函数助手（单一真相源 = data/polls.json，前端组件与 API 共用）。
package polls

import (
	"encoding/json"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
)

type Option struct {
	Key   string            `json:"key"`
	Mid   *float64          `json:"mid"`
	Label map[string]string `json:"label"`
}
type Poll struct {
	Code       string            `json:"code"`
	Type       string            `json:"type"`
	Scope      string            `json:"scope"`
	Q          map[string]string `json:"q"`
	Conclusion map[string]string `json:"conclusion"`
	Options    []Option          `json:"options"`
}

var (
	Polls  []Poll
	ByCode = map[string]Poll{}
)

// Load 从 dir/polls.json 载入投票定义。
func Load(dir string) error {
	b, err := os.ReadFile(filepath.Join(dir, "polls.json"))
	if err != nil {
		return err
	}
	var doc struct {
		Polls []Poll `json:"polls"`
	}
	if err := json.Unmarshal(b, &doc); err != nil {
		return err
	}
	Polls = doc.Polls
	for _, p := range Polls {
		ByCode[p.Code] = p
	}
	return nil
}

// OptionKeys 某投票的合法选项键集合。
func OptionKeys(code string) map[string]bool {
	out := map[string]bool{}
	if p, ok := ByCode[code]; ok {
		for _, o := range p.Options {
			out[o.Key] = true
		}
	}
	return out
}

// LocText 取本地化文案（缺失回退 en，再回退首个）。
func LocText(m map[string]string, locale string) string {
	if v, ok := m[locale]; ok {
		return v
	}
	if v, ok := m["en"]; ok {
		return v
	}
	for _, v := range m {
		return v
	}
	return ""
}

// TotalCount 计票合计。
func TotalCount(counts map[string]int) int {
	t := 0
	for _, c := range counts {
		t += c
	}
	return t
}

// PctOf 各选项百分比（0-100 整数）。
func PctOf(counts map[string]int) map[string]int {
	total := TotalCount(counts)
	out := map[string]int{}
	for k, c := range counts {
		if total > 0 {
			out[k] = int(float64(c)*100/float64(total) + 0.5)
		} else {
			out[k] = 0
		}
	}
	return out
}

// AvgFromCounts 用 option.mid 加权折算大众平均分；任一选项无 mid 或无票返回 nil。
func AvgFromCounts(p Poll, counts map[string]int) *int {
	n, s := 0, 0.0
	for _, o := range p.Options {
		if o.Mid == nil {
			return nil
		}
		c := counts[o.Key]
		n += c
		s += float64(c) * (*o.Mid)
	}
	if n == 0 {
		return nil
	}
	v := int(s/float64(n) + 0.5)
	return &v
}

var (
	rePct  = regexp.MustCompile(`\{pct\.(\w+)\}`)
	reVar  = regexp.MustCompile(`\{(\w+)\}`)
)

// FillTpl 模板填充：{pct.<key>} 先填（若给 pct），再填 {name}/{n}/{avg}；未提供的占位符原样保留。
func FillTpl(tpl string, vars map[string]string, pct map[string]int) string {
	s := tpl
	if pct != nil {
		s = rePct.ReplaceAllStringFunc(s, func(m string) string {
			k := rePct.FindStringSubmatch(m)[1]
			if v, ok := pct[k]; ok {
				return strconv.Itoa(v)
			}
			return m
		})
	}
	s = reVar.ReplaceAllStringFunc(s, func(m string) string {
		k := reVar.FindStringSubmatch(m)[1]
		if v, ok := vars[k]; ok {
			return v
		}
		return m
	})
	return s
}
