package data

import (
	"html/template"
	"path/filepath"
	"strings"

	"aijobrisk/internal/model"
)

// Bi 双语文案（英文母本 + 中文）。
type Bi struct {
	ZhCN string `json:"zh-CN"`
	En   string `json:"en"`
}

type rankingDef struct {
	Name Bi `json:"name"`
	Sub  Bi `json:"sub"`
	Why  Bi `json:"why"`
}

type uiI18nEntry struct {
	UI      map[string]string `json:"ui"`
	Dim     map[string]string `json:"dim"`
	Dimdesc map[string]string `json:"dimdesc"`
}

var (
	dimLabelD    map[string]map[string]string
	dimDescD     map[string]map[string]string
	disTypeD     map[string]map[string]string
	disLevelD    map[string]map[string]string
	uiBase       map[string]map[string]string // en / zh-CN 母本
	uiI18n       map[string]uiI18nEntry       // 其余语言
	sourcesD     map[string]Bi
	rankingsD    map[string]rankingDef
	migTextD     map[string]map[string]Bi
	countryFlag  map[string]string
	countryNameD map[string]Bi
)

// DimOrder 雷达维度固定顺序（对齐 data.ts DIM_ORDER）。
var DimOrder = []string{
	"income_level", "job_demand", "future_prospect", "pr_friendliness", "ai_risk", "competition",
	"work_intensity", "learning_difficulty", "learning_duration", "certification_difficulty",
}

var currencySym = map[string]string{
	"AU": "$", "NZ": "$", "CA": "$", "US": "$", "UK": "£", "DE": "€", "FR": "€",
	"ES": "€", "IT": "€", "NL": "€", "IE": "€", "JP": "¥", "KR": "₩",
	"BR": "R$", "MX": "$", "IN": "₹", "CN": "¥",
	"NO": "kr", "SE": "kr", "FI": "€", "DK": "kr", "IS": "kr",
	"BE": "€", "AT": "€", "PL": "zł", "PT": "€", "GR": "€", "HU": "Ft", "CZ": "Kč",
	"RO": "lei", "LU": "€", "SK": "€", "SI": "€", "HR": "€", "TR": "₺",
	"AR": "$", "CL": "$", "MY": "RM", "ID": "Rp", "TH": "฿", "VN": "₫", "SG": "$",
}

func loadDicts() error {
	d := func(name string, v any) error { return readJSON(filepath.Join("derived", name), v) }
	if err := d("DIM_LABEL.json", &dimLabelD); err != nil {
		return err
	}
	if err := d("DIM_DESC.json", &dimDescD); err != nil {
		return err
	}
	if err := d("DIS_TYPE.json", &disTypeD); err != nil {
		return err
	}
	if err := d("DIS_LEVEL.json", &disLevelD); err != nil {
		return err
	}
	if err := d("UI.json", &uiBase); err != nil {
		return err
	}
	if err := d("SOURCES_BODY.json", &sourcesD); err != nil {
		return err
	}
	if err := d("RANKINGS.json", &rankingsD); err != nil {
		return err
	}
	if err := d("MIG_TEXT.json", &migTextD); err != nil {
		return err
	}
	if err := d("COUNTRY_FLAG.json", &countryFlag); err != nil {
		return err
	}
	// 归一化：部分后加国（BR/MX/IN/CN）的国旗 SVG 缺 class="flagsvg"，
	// 导致 CSS 尺寸规则不生效、渲染为 0 宽。补齐后所有国旗一致。
	for cc, svg := range countryFlag {
		if strings.HasPrefix(svg, "<svg") && !strings.Contains(svg, "flagsvg") {
			countryFlag[cc] = strings.Replace(svg, "<svg", `<svg class="flagsvg"`, 1)
		}
	}
	if err := d("COUNTRY_NAME.json", &countryNameD); err != nil {
		return err
	}
	if err := readJSON("ui_i18n.json", &uiI18n); err != nil {
		return err
	}
	return nil
}

// CountryName 国家名（对齐 data.ts countryName）。
func CountryName(cc, locale string) string {
	v, ok := countryNameD[cc]
	if !ok || v.En == "" {
		return cc
	}
	if locale == "zh-CN" {
		return v.ZhCN
	}
	if locale == "en" {
		return v.En
	}
	return Tr(v.En, locale)
}

// DimLabel 维度标签（对齐 data.ts dimLabel）。
func DimLabel(dim, locale string) string {
	if m := dimLabelD[dim]; m != nil {
		if v, ok := m[locale]; ok {
			return v
		}
	}
	if e, ok := uiI18n[locale]; ok {
		if v, ok := e.Dim[dim]; ok {
			return v
		}
	}
	if m := dimLabelD[dim]; m != nil {
		if v, ok := m["en"]; ok {
			return v
		}
	}
	return dim
}

// DimDesc 维度说明。
func DimDesc(dim, locale string) string {
	if m := dimDescD[dim]; m != nil {
		if v, ok := m[locale]; ok {
			return v
		}
	}
	if e, ok := uiI18n[locale]; ok {
		if v, ok := e.Dimdesc[dim]; ok {
			return v
		}
	}
	if m := dimDescD[dim]; m != nil {
		if v, ok := m["en"]; ok {
			return v
		}
	}
	return ""
}

// DisType / DisLevel 干扰源类型/程度标签。
func DisType(k, locale string) string  { return disMap(disTypeD, k, locale) }
func DisLevel(k, locale string) string { return disMap(disLevelD, k, locale) }
func disMap(d map[string]map[string]string, k, locale string) string {
	if m := d[k]; m != nil {
		if v, ok := m[locale]; ok {
			return v
		}
		if v, ok := m["en"]; ok {
			return v
		}
	}
	return k
}

// Strings 取某语言 UI 文案（对齐 data.ts strings()：UI.en 打底 + ui_i18n.ui + UI[locale]）。
func Strings(locale string) map[string]string {
	out := map[string]string{}
	for k, v := range uiBase["en"] {
		out[k] = v
	}
	if e, ok := uiI18n[locale]; ok {
		for k, v := range e.UI {
			out[k] = v
		}
	}
	if m, ok := uiBase[locale]; ok {
		for k, v := range m {
			out[k] = v
		}
	}
	return out
}

func biPick(v Bi, locale string) string {
	switch locale {
	case "zh-CN":
		return v.ZhCN
	case "en":
		return v.En
	default:
		if HasTr(v.En, locale) {
			return Tr(v.En, locale)
		}
		return v.En
	}
}

// SourcesBody 数据来源文案（对齐 data.ts sourcesBody）。
func SourcesBody(country, locale string) string {
	if v, ok := sourcesD[country]; ok {
		return biPick(v, locale)
	}
	return Strings(locale)["sourcesBody"] // AU：走 UI 字典
}

var migFallbackKey = map[string]string{
	"restrictedOcc": "migRestrictedOcc", "restrictedNote": "migRestrictedNote", "nonMigVisa": "nonMigVisa",
}

func migText(country, key, locale string) string {
	if m, ok := migTextD[country]; ok {
		if v, ok := m[key]; ok {
			return biPick(v, locale)
		}
	}
	if fk, ok := migFallbackKey[key]; ok {
		return Strings(locale)[fk]
	}
	return ""
}

func MigRestrictedOccOf(country, locale string) string {
	return migText(country, "restrictedOcc", locale)
}
func MigRestrictedNoteOf(country, locale string) string {
	return migText(country, "restrictedNote", locale)
}
func NonMigVisaOf(country, locale string) string { return migText(country, "nonMigVisa", locale) }

// RankName / RankSub / RankWhy 榜单文案。
func RankName(key, locale string) string { return biPick(rankingsD[key].Name, locale) }
func RankSub(key, locale string) string  { return biPick(rankingsD[key].Sub, locale) }
func RankWhy(key, locale string) string  { return biPick(rankingsD[key].Why, locale) }

// Money 货币格式（符号 + 千分位）；对齐 data.ts money()。
func Money(v *float64, country string) string {
	if v == nil || *v == 0 {
		return "—"
	}
	sym := "$"
	if s, ok := currencySym[country]; ok {
		sym = s
	}
	return sym + Comma(int(*v+0.5))
}

// RadarLabels / RadarValues 雷达图。
func RadarLabels(locale string) []string {
	out := make([]string, len(DimOrder))
	for i, d := range DimOrder {
		out[i] = DimLabel(d, locale)
	}
	return out
}
func RadarValues(o *model.Occ) []float64 {
	m := map[string]float64{}
	for _, r := range o.Ratings {
		m[r.Dimension] = r.Stars.V
	}
	out := make([]float64, len(DimOrder))
	for i, d := range DimOrder {
		out[i] = m[d]
	}
	return out
}

// dimOrderFor 按国家移民档位返回维度顺序：非"经典移民国"去掉
// pr_friendliness / pr_difficulty 两个永居相关维度。
func dimOrderFor(cc string) []string {
	if MigrationTier(cc) == "full" {
		return DimOrder
	}
	out := make([]string, 0, len(DimOrder))
	for _, d := range DimOrder {
		if d == "pr_friendliness" || d == "pr_difficulty" {
			continue
		}
		out = append(out, d)
	}
	return out
}

// RadarLabelsFor / RadarValuesFor 国家感知版（对齐 dimOrderFor）。
func RadarLabelsFor(cc, locale string) []string {
	order := dimOrderFor(cc)
	out := make([]string, len(order))
	for i, d := range order {
		out[i] = DimLabel(d, locale)
	}
	return out
}
func RadarValuesFor(cc string, o *model.Occ) []float64 {
	m := map[string]float64{}
	for _, r := range o.Ratings {
		m[r.Dimension] = r.Stars.V
	}
	order := dimOrderFor(cc)
	out := make([]float64, len(order))
	for i, d := range order {
		out[i] = m[d]
	}
	return out
}

// CountryFlag 国旗 SVG（HTML 安全）。
func CountryFlag(cc string) template.HTML { return template.HTML(countryFlag[cc]) }

// FlagRaw 国旗 SVG 原文。
func FlagRaw(cc string) string { return countryFlag[cc] }
