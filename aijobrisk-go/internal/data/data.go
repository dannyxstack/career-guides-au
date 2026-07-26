// Package data 加载 aijobrisk 数据（进程内常驻，架构对齐 aijobrisk/src/lib/data.ts）。
package data

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sort"

	"aijobrisk/internal/model"
)

// COUNTRIES 路由支持的国家（对齐 data.ts）。
var COUNTRIES = []string{"AU", "NZ", "CA", "US", "UK", "DE", "FR", "ES", "IT", "NL", "IE", "JP", "KR"}

// CURRENCY 国家 -> 本币代码。
var CURRENCY = map[string]string{
	"AU": "AUD", "NZ": "NZD", "CA": "CAD", "US": "USD", "UK": "GBP", "DE": "EUR",
	"FR": "EUR", "ES": "EUR", "IT": "EUR", "NL": "EUR", "IE": "EUR", "JP": "JPY", "KR": "KRW",
}

var (
	dataDir     string
	Occupations []*model.Occ                 // 去重后（slug|country 唯一）
	jobGroups   map[string][]*model.Occ      // slug -> 各国
	JobSlugs    []string                     // jobGroups 键（保序）
	bySlugCC    map[string]*model.Occ        // "slug|cc" -> occ
	Categories  []string                     // 职业族
	CategorySlug map[string]string           // 类名 -> slug
)

// DataDir 返回数据根目录。
func DataDir() string { return dataDir }

func readJSON(name string, v any) error {
	b, err := os.ReadFile(filepath.Join(dataDir, name))
	if err != nil {
		return err
	}
	return json.Unmarshal(b, v)
}

// Load 从 dir 载入全部数据；应在服务启动时调用一次。
func Load(dir string) error {
	dataDir = dir

	var occDoc struct {
		Occupations []*model.Occ `json:"occupations"`
	}
	if err := readJSON("occupations_v2.json", &occDoc); err != nil {
		return err
	}

	// 去重：同一 slug|country 保留「字段更完整」者（对齐 data.ts occupationQuality）。
	best := map[string]*model.Occ{}
	order := []string{}
	for _, o := range occDoc.Occupations {
		key := o.Slug + "|" + o.Country
		cur, ok := best[key]
		if !ok {
			best[key] = o
			order = append(order, key)
		} else if quality(o) > quality(cur) {
			best[key] = o
		}
	}
	Occupations = make([]*model.Occ, 0, len(order))
	for _, k := range order {
		Occupations = append(Occupations, best[k])
	}

	// jobGroups + JOB_SLUGS（按 COUNTRIES 顺序排组）。
	jobGroups = map[string][]*model.Occ{}
	bySlugCC = map[string]*model.Occ{}
	for _, o := range Occupations {
		jobGroups[o.Slug] = append(jobGroups[o.Slug], o)
		bySlugCC[o.Slug+"|"+o.Country] = o
	}
	ord := map[string]int{}
	for i, c := range COUNTRIES {
		ord[c] = i
	}
	rank := func(cc string) int {
		if v, ok := ord[cc]; ok {
			return v
		}
		return 99
	}
	// JOB_SLUGS：按首次出现顺序取键。
	JobSlugs = JobSlugs[:0]
	seenSlug := map[string]bool{}
	for _, o := range Occupations {
		if !seenSlug[o.Slug] {
			seenSlug[o.Slug] = true
			JobSlugs = append(JobSlugs, o.Slug)
		}
	}
	for _, g := range jobGroups {
		sort.SliceStable(g, func(i, j int) bool { return rank(g[i].Country) < rank(g[j].Country) })
	}

	// categories
	var catDoc struct {
		Categories   []string          `json:"categories"`
		CategorySlug map[string]string `json:"category_slug"`
	}
	if err := readJSON("categories_v2.json", &catDoc); err != nil {
		return err
	}
	Categories = catDoc.Categories
	CategorySlug = catDoc.CategorySlug

	initComparePairs()

	if err := loadTranslations(); err != nil {
		return err
	}
	if err := loadIndustries(); err != nil {
		return err
	}
	if err := loadDicts(); err != nil {
		return err
	}
	if err := loadFAQ2030(); err != nil {
		return err
	}
	return nil
}

func quality(o *model.Occ) int {
	q := 0
	if o.AI != nil {
		q += 20
	}
	if o.WorkforceSize.Set {
		q += 8
	}
	if o.OverallScore.Set {
		q += 4
	}
	q += len(o.Salaries) + len(o.Ratings)
	return q
}

// OccByCountry 返回某国职业（cc 空返回全部）。
func OccByCountry(cc string) []*model.Occ {
	if cc == "" {
		return Occupations
	}
	out := make([]*model.Occ, 0, 600)
	for _, o := range Occupations {
		if o.Country == cc {
			out = append(out, o)
		}
	}
	return out
}

// JobGroup 全球聚合。
type JobGroup struct {
	Slug      string
	Rep       *model.Occ
	Countries []*model.Occ
}

// JobBySlug 取某 slug 的全球聚合。
func JobBySlug(slug string) *JobGroup {
	a := jobGroups[slug]
	if len(a) == 0 {
		return nil
	}
	return &JobGroup{Slug: slug, Rep: a[0], Countries: a}
}

// GetBySlug 取某国某 slug 的职业。
func GetBySlug(slug, cc string) *model.Occ { return bySlugCC[slug+"|"+cc] }

// CatSlug 类名 -> slug。
func CatSlug(c string) string { return CategorySlug[c] }

// Name 取职业名（tr 母本源串在 zh-CN 槽，按 locale 翻译）。
func Name(o *model.Occ, locale string) string {
	zh := o.Zh().Name
	if zh != "" {
		if t := Tr(zh, locale); t != "" {
			return t
		}
	}
	if zh != "" {
		return zh
	}
	return o.NameEn
}

// Summary 取职业摘要。
func Summary(o *model.Occ, locale string) string {
	return Tr(o.Zh().Summary, locale)
}

// CurrencyOf 国家本币。
func CurrencyOf(cc string) string {
	if c, ok := CURRENCY[cc]; ok {
		return c
	}
	return "AUD"
}
