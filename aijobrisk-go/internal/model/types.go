// Package model 定义 aijobrisk 数据层结构，字段对齐 aijobrisk/src/lib/data.ts 的 Occ 等。
package model

import (
	"encoding/json"
	"strconv"
)

// Num 兼容 JSON 中「数字 / 字符串 / null」三种数值写法：
// avg_salary、salaries.min/max 在导出里是字符串（"91364.00"），aioe_pct/workforce_size 是数字。
type Num struct {
	V   float64
	Set bool
}

func (n *Num) UnmarshalJSON(b []byte) error {
	s := string(b)
	if s == "null" || s == `""` || s == "" {
		return nil
	}
	if s[0] == '"' {
		var str string
		if err := json.Unmarshal(b, &str); err != nil {
			return err
		}
		if str == "" {
			return nil
		}
		f, err := strconv.ParseFloat(str, 64)
		if err != nil {
			return nil // 非数值字符串按缺失处理
		}
		n.V, n.Set = f, true
		return nil
	}
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return err
	}
	n.V, n.Set = f, true
	return nil
}

// Ptr 返回可空浮点（缺失=nil），便于模板判空。
func (n Num) Ptr() *float64 {
	if !n.Set {
		return nil
	}
	v := n.V
	return &v
}

// Int 返回四舍五入整数；缺失返回 0（配合 Set 判空使用）。
func (n Num) Int() int { return int(n.V + 0.5) }

type I18nEntry struct {
	Name         string `json:"name"`
	Summary      string `json:"summary"`
	ForecastNote string `json:"forecast_note"`
	TrendSummary string `json:"trend_summary"`
}

type Salary struct {
	Label string `json:"label"`
	Min   Num    `json:"min"`
	Max   Num    `json:"max"`
	Note  string `json:"note"`
}

type Rating struct {
	Dimension string `json:"dimension"`
	Stars     Num    `json:"stars"`
}

type Disruptor struct {
	Name    string `json:"name"`
	URL     string `json:"url"`
	Type    string `json:"type"`
	Level   string `json:"level"`
	Year    any    `json:"year"`
	ScopeZh string `json:"scope_zh"`
}

type Adjacent struct {
	Slug   string `json:"slug"`
	NameEn string `json:"name_en"`
}

// AI 为 occupation 的 AI 暴露块（country-neutral，跨国复制一致）。含详情懒加载字段。
type AI struct {
	VerdictType        string `json:"verdict_type"`
	Cluster            string `json:"cluster"`
	AutomationExposure Num    `json:"automation_exposure"`
	HumanMoat          Num    `json:"human_moat"`
	EntryRisk          Num    `json:"entry_risk"`
	AIUpside           Num    `json:"ai_upside"`
	AioeScore          Num    `json:"aioe_score"`
	AioePct            Num    `json:"aioe_pct"`
	AioeMethod         string `json:"aioe_method"`
	VerdictZh          string `json:"verdict_zh"`
	// —— 详情（occ-detail-v2）——
	EntryNarrowingZh string      `json:"entry_narrowing_zh"`
	UpgradePathZh    string      `json:"upgrade_path_zh"`
	ReplacedZh       []string    `json:"replaced_zh"`
	AugmentedZh      []string    `json:"augmented_zh"`
	MoatZh           []string    `json:"moat_zh"`
	SkillsZh         []string    `json:"skills_zh"`
	Adjacent         []Adjacent  `json:"adjacent"`
	Disruptors       []Disruptor `json:"disruptors"`
}

type Education struct {
	Stage    string `json:"stage"`
	Duration string `json:"duration"`
	CostMin  Num    `json:"cost_min"`
	CostMax  Num    `json:"cost_max"`
	CostNote string `json:"cost_note"`
}

type Visa struct {
	Subclass string `json:"subclass"`
	Name     string `json:"name"`
	Desc     string `json:"desc"`
	MinScore Num    `json:"min_score"`
	ScoreAsof string `json:"score_asof"`
}

type Qualification struct {
	Name      string `json:"name"`
	Issuer    string `json:"issuer"`
	Note      string `json:"note"`
	Mandatory bool   `json:"mandatory"`
}

type Suitability struct {
	Fit   []string `json:"fit"`
	Unfit []string `json:"unfit"`
}

type FAQItem struct {
	Type     string `json:"type"`
	Question string `json:"question"`
	Answer   string `json:"answer"`
}

// BakedPoll 构建期烘焙的投票聚合（occupations_v2.json 的 o.polls，可能缺省）。
type BakedPoll struct {
	Total  int            `json:"total"`
	Counts map[string]int `json:"counts"`
}

type Occ struct {
	ID             int                  `json:"id"`
	Country        string               `json:"country"`
	OccCode        string               `json:"occ_code"`
	OccCodeType    string               `json:"occ_code_type"`
	AnzscoCode     string               `json:"anzsco_code"`
	Category       string               `json:"category"`
	Currency       string               `json:"currency"`
	IsMigration    int                  `json:"is_migration"`
	ShortageListed bool                 `json:"shortage_listed"`
	WorkforceSize  Num                  `json:"workforce_size"`
	Slug           string               `json:"slug"`
	NameEn         string               `json:"name_en"`
	I18n           map[string]I18nEntry `json:"i18n"`
	Salaries       []Salary             `json:"salaries"`
	Ratings        []Rating             `json:"ratings"`
	OverallScore   Num                  `json:"overall_score"`
	AvgSalary      Num                  `json:"avg_salary"`
	AI             *AI                  `json:"ai"`
	Education      []Education          `json:"education"`
	// —— 详情懒加载（occ-detail-v2；lean 对象为空）——
	Visa           []Visa               `json:"visa"`
	Qualifications []Qualification      `json:"qualifications"`
	Suitability    *Suitability         `json:"suitability"`
	Faqs           []FAQItem            `json:"faqs"`
	GrowthAreas    []string             `json:"growth_areas"`
	Polls          map[string]BakedPoll `json:"polls"`
}

// Zh 取 zh-CN 槽的内容（v2 里该槽实为英文母本源串，供 tr() 翻译）。
func (o *Occ) Zh() I18nEntry { return o.I18n["zh-CN"] }

// Rating 取某维度星级（缺失 nil）。
func (o *Occ) Rating(dim string) *float64 {
	for _, r := range o.Ratings {
		if r.Dimension == dim {
			return r.Stars.Ptr()
		}
	}
	return nil
}
