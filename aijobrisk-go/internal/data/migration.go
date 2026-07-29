package data

import "html/template"

// 移民板块分档（对应产品决策，见 docs/session-handoff）：
//
//	full = 经典移民国：保留逐职业移民板块（签证表/职业相关）。
//	info = 有主流工作签→永居通道：退化为一段静态说明 + 官方链接（不随职业变）。
//	none = 非移民国：不显示移民板块。
var migrationTier = map[string]string{
	// ① 经典移民国
	"AU": "full", "NZ": "full", "CA": "full", "US": "full", "UK": "full", "DE": "full", "IE": "full",
	// ② EU Blue Card / EEA / 工作签转永居
	"FR": "info", "ES": "info", "IT": "info", "NL": "info", "BE": "info", "AT": "info",
	"PL": "info", "PT": "info", "GR": "info", "HU": "info", "CZ": "info", "RO": "info",
	"LU": "info", "SK": "info", "SI": "info", "HR": "info", "DK": "info", "FI": "info",
	"SE": "info", "NO": "info", "IS": "info", "CH": "info", "SG": "info", "JP": "info", "KR": "info",
	"EE": "info", "LV": "info", "LT": "info",
	// ③ 其余国家默认 none（CN BR MX AR CL ID MY TH VN TR IN…）
}

// MigrationTier 返回该国移民板块档位（默认 none）。
func MigrationTier(cc string) string {
	if t, ok := migrationTier[cc]; ok {
		return t
	}
	return "none"
}

// MigInfo ②档国家的静态移民说明：一段话 + 官方门户链接。
type MigInfo struct {
	Body     string // 英文母本（经 Tr 本地化，缺译回退英文）
	URL      string // 官方移民机构/门户
	LinkText string
}

// EU Blue Card 成员国共享文案（{C} 替换国名）。
const euBlueCardBody = "As an EU member state, {C} admits skilled foreign professionals mainly through the EU Blue Card and national work-permit routes. Eligibility depends on your qualifications, a qualifying job offer and salary threshold — not on any single occupation. Rules and salary thresholds change yearly, so always check the official source before making plans."

var euBlueCard = map[string]bool{
	"FR": true, "ES": true, "IT": true, "NL": true, "BE": true, "AT": true, "PL": true,
	"PT": true, "GR": true, "HU": true, "CZ": true, "RO": true, "LU": true, "SK": true,
	"SI": true, "HR": true, "FI": true, "SE": true, "EE": true, "LV": true, "LT": true,
}

// 非 Blue Card 的 ②档国家（EEA / 双边 / 亚洲工作签），各自文案。
var migInfoSpecial = map[string]MigInfo{
	"DK": {"Denmark does not take part in the EU Blue Card but runs its own skilled-migration schemes, such as the Pay Limit Scheme and the Positive List for occupations facing shortages. Eligibility depends on your job offer and salary, not on any single occupation.",
		"https://www.nyidanmark.dk/en-GB", "Danish Immigration Service (nyidanmark.dk)"},
	"NO": {"As an EEA country, Norway grants skilled-worker residence permits to qualified professionals who hold a concrete job offer meeting local pay and qualification rules; long-term residence can follow. Requirements are set nationally and change over time.",
		"https://www.udi.no/en/", "Norwegian Directorate of Immigration (UDI)"},
	"IS": {"As an EEA country, Iceland issues residence and work permits to qualified professionals with a job offer, subject to labour-market and qualification checks; permanent residence can follow after several years.",
		"https://utl.is/index.php/en/", "Directorate of Immigration Iceland (utl.is)"},
	"CH": {"Switzerland admits non-EU/EFTA professionals under an annually capped quota system for qualified specialists with a Swiss job offer, via bilateral agreements; settlement permits can follow after several years of residence.",
		"https://www.sem.admin.ch/sem/en/home.html", "State Secretariat for Migration (SEM)"},
	"SG": {"Singapore's main professional work pass is the Employment Pass, granted to qualifying professionals with a job offer above a salary threshold; long-term holders may apply for Permanent Residence. Criteria are set by the Ministry of Manpower and updated regularly.",
		"https://www.mom.gov.sg/passes-and-permits/employment-pass", "Ministry of Manpower (MOM)"},
	"JP": {"Japan issues status-of-residence work visas by field, and high-scoring professionals can use the Highly Skilled Professional route, which offers a faster path to permanent residence. Eligibility depends on your qualifications and employer, not on any single occupation.",
		"https://www.isa.go.jp/en/", "Immigration Services Agency of Japan"},
	"KR": {"Korea's E-7 skilled-worker visa is granted to qualifying professionals with a local job offer, and long-term holders may move to F-2/F-5 residence. Requirements are set by the Korea Immigration Service and change over time.",
		"https://www.immigration.go.kr/immigration_eng/index.do", "Korea Immigration Service"},
}

// EU 各国官方移民门户（Blue Card 走 EU Immigration Portal 权威源）。
const euImmigrationPortal = "https://immigration-portal.ec.europa.eu/index_en"

// MigrationInfoOf 返回 ②档国家的本地化说明；非 ②档返回 (MigInfo{}, false)。
func MigrationInfoOf(cc, locale string) (MigInfo, bool) {
	if MigrationTier(cc) != "info" {
		return MigInfo{}, false
	}
	if euBlueCard[cc] {
		body := replaceCountry(euBlueCardBody, CountryName(cc, locale))
		return MigInfo{Body: Tr(body, locale), URL: euImmigrationPortal, LinkText: Tr("EU Immigration Portal", locale)}, true
	}
	if mi, ok := migInfoSpecial[cc]; ok {
		return MigInfo{Body: Tr(mi.Body, locale), URL: mi.URL, LinkText: Tr(mi.LinkText, locale)}, true
	}
	return MigInfo{}, false
}

func replaceCountry(tmpl, name string) string {
	out := make([]byte, 0, len(tmpl)+len(name))
	for i := 0; i < len(tmpl); i++ {
		if i+2 < len(tmpl) && tmpl[i] == '{' && tmpl[i+1] == 'C' && tmpl[i+2] == '}' {
			out = append(out, name...)
			i += 2
			continue
		}
		out = append(out, tmpl[i])
	}
	return string(out)
}

// SafeURL 把官方链接标为安全（仅用于本文件内置的固定官方域名）。
func SafeURL(u string) template.URL { return template.URL(u) }
