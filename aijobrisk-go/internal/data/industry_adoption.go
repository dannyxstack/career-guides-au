package data

// —— 行业 AI 采纳率（渗透率）时间序列 ——
// 指标 = 使用 AI 于任何业务环节的企业占比（美国普查局 BTOS 定义）。
// 数据由 scripts/build_industry_ai_adoption.py 生成 industry_ai_adoption.json：
// BTOS 真实行业锚点 + logistic 扩散曲线拟合，2021–2031（>2026 为预测=虚线）。
// 非美国国家按 country_mult 缩放（默认 1.0 = 以美国为基准，待补各国数据）。

type adoptionDoc struct {
	Source      string                  `json:"source"`
	SourceURL   string                  `json:"source_url"`
	Definition  string                  `json:"definition"`
	MeasuredTo  float64                 `json:"measured_to"`
	Note        string                  `json:"note"`
	Years       []int                   `json:"years"`
	All         [][3]float64            `json:"all"`
	Sectors     map[string][][3]float64 `json:"sectors"`
	CountryMult map[string]float64      `json:"country_mult"`
	Proxy       []string                `json:"proxy_sectors"`
}

var adoption adoptionDoc

// loadAdoption 载入行业采纳率序列（best-effort：缺文件则该图不显示）。
func loadAdoption() {
	_ = readJSON("industry_ai_adoption.json", &adoption)
}

func adoptionMult(cc string) float64 {
	if m, ok := adoption.CountryMult[cc]; ok {
		return m
	}
	if m, ok := adoption.CountryMult["_default"]; ok {
		return m
	}
	return 1
}

func scaleSeries(s [][3]float64, mult float64) [][3]float64 {
	if s == nil || mult == 1 {
		return s
	}
	out := make([][3]float64, len(s))
	for i, p := range s {
		v := p[1] * mult
		if v > 100 {
			v = 100
		}
		out[i] = [3]float64{p[0], v, p[2]}
	}
	return out
}

// AdoptionHas 是否有可用的采纳率数据。
func AdoptionHas() bool { return len(adoption.All) > 1 }

// AdoptionAll 全行业采纳率序列（按国缩放）。
func AdoptionAll(cc string) [][3]float64 { return scaleSeries(adoption.All, adoptionMult(cc)) }

// AdoptionSector 某行业采纳率序列（按国缩放）。
func AdoptionSector(cc, id string) ([][3]float64, bool) {
	s, ok := adoption.Sectors[id]
	if !ok {
		return nil, false
	}
	return scaleSeries(s, adoptionMult(cc)), true
}

// AdoptionIsProxy 该行业是否为代理值（BTOS 未覆盖，如政府/管理）。
func AdoptionIsProxy(id string) bool {
	for _, p := range adoption.Proxy {
		if p == id {
			return true
		}
	}
	return false
}

// AdoptionSource / AdoptionDefinition 供图注与方法论。
func AdoptionSource() string     { return adoption.Source }
func AdoptionDefinition() string { return adoption.Definition }
func AdoptionUSOnly(cc string) bool { return cc != "US" && adoptionMult(cc) == adoptionMult("US") }
