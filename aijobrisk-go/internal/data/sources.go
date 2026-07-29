package data

import "html/template"

// SourceRow 单国数据来源与权威性（移植自 job-treemap SOURCE_INFO）。
// 字段：Authority=机构(含 &amp; 实体的 HTML)、Class=分类体系、
// Tier=权威层级 A/B/C、OfficialPay=是否有官方职业薪资。
type SourceRow struct {
	Authority   string
	Class       string
	Tier        string
	OfficialPay bool
}

// tierLabel 三层权威度标签。
var tierLabel = map[string]string{
	"A": "National statistics office (self-collected / register / census)",
	"B": "Eurostat EU-LFS (employment official; 4-digit modelled)",
	"C": "ILOSTAT (UN ILO)",
}

// TierLabel 返回权威层级说明（可本地化）。
func TierLabel(tier, locale string) string {
	s, ok := tierLabel[tier]
	if !ok {
		return tier
	}
	if locale == "en" {
		return s
	}
	return Tr(s, locale)
}

// SourceOf 取某国来源行（缺失返回 false）。
func SourceOf(cc string) (SourceRow, bool) { r, ok := sourceInfo[cc]; return r, ok }

// SourceAuthorityHTML 机构名（保留 &amp; 等实体，安全 HTML）。
func SourceAuthorityHTML(cc string) template.HTML {
	if r, ok := sourceInfo[cc]; ok {
		return template.HTML(r.Authority)
	}
	return ""
}

// SourceOrder 返回按权威层级(A→B→C)、层内字母序排列的国家码。
func SourceOrder() []string { return sourceInfoOrder }

var sourceInfoOrder = []string{
	"AU", "BR", "CA", "CN", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "HU", "IE", "IN", "IS", "IT", "JP", "KR", "MX", "NL", "NO", "NZ", "SE", "SG", "UK", "US", "AT", "BE", "CH", "GR", "HR", "LT", "LU", "LV", "PL", "PT", "RO", "SI", "SK", "TR", "AR", "CL", "ID", "MY", "TH", "VN",
}

var sourceInfo = map[string]SourceRow{
	"AU": {"Jobs and Skills Australia &amp; the Australian Bureau of Statistics (ABS)", "ANZSCO", "A", true},
	"BR": {"the Brazilian Institute of Geography and Statistics (IBGE), PNAD Contínua microdata", "CBO → ISCO-08", "A", true},
	"CA": {"Statistics Canada &amp; Job Bank (Employment and Social Development Canada)", "NOC", "A", true},
	"CN": {"the National Bureau of Statistics of China, 2020 Population Census", "CSCO → ISCO-08", "A", true},
	"CZ": {"the Czech Statistical Office (ČSÚ) &amp; the ISPV Regional Wage Survey", "CZ-ISCO (ISCO-08)", "A", true},
	"DE": {"the Federal Statistical Office (Destatis) &amp; the Federal Employment Agency (Bundesagentur für Arbeit)", "KldB / ISCO-08", "A", true},
	"DK": {"Statistics Denmark", "DISCO-08 (ISCO-08)", "A", true},
	"EE": {"Statistics Estonia (Statistikaamet), PA633 occupational earnings", "ISCO-08", "A", true},
	"ES": {"the National Statistics Institute (INE) &amp; the Public Employment Service (SEPE)", "CNO / ISCO-08", "A", true},
	"FI": {"Statistics Finland", "Classification of Occupations 2010 (ISCO-08)", "A", true},
	"FR": {"the National Institute of Statistics and Economic Studies (INSEE) &amp; France Travail", "ROME / PCS → ISCO-08", "A", true},
	"HU": {"the Hungarian Central Statistical Office (KSH)", "HSCO'08 (ISCO-08 aligned)", "A", true},
	"IE": {"the Central Statistics Office (CSO Ireland)", "ISCO-08", "A", true},
	"IN": {"the Ministry of Statistics (MoSPI) Periodic Labour Force Survey 2023-24 unit-level microdata", "NCO-2015 (ISCO-08 aligned)", "A", true},
	"IS": {"Statistics Iceland", "ÍSTARF95 (ISCO-88) → ISCO-08", "A", true},
	"IT": {"the National Institute of Statistics (ISTAT)", "ISCO-08 (CP)", "A", true},
	"JP": {"the Statistics Bureau of Japan &amp; the Ministry of Health, Labour and Welfare (Basic Survey on Wage Structure)", "JSCO → ISCO-08", "A", true},
	"KR": {"the Korea Employment Information Service (KEIS) WorkNet/KNOW &amp; Statistics Korea", "KECO → ISCO-08", "A", true},
	"MX": {"the National Institute of Statistics and Geography (INEGI), ENOE microdata", "SINCO → ISCO-08", "A", true},
	"NL": {"Statistics Netherlands (CBS)", "ISCO-08 (BRC)", "A", true},
	"NO": {"Statistics Norway (SSB)", "STYRK-08 (ISCO-08)", "A", true},
	"NZ": {"Stats NZ &amp; the Ministry of Business, Innovation and Employment (MBIE)", "ANZSCO", "A", true},
	"SE": {"Statistics Sweden (SCB)", "SSYK 2012 → ISCO-08", "A", true},
	"SG": {"the Ministry of Manpower (MOM) Occupational Wage Survey &amp; the Department of Statistics", "SSOC 2024 (ISCO-08 based)", "A", true},
	"UK": {"the UK Office for National Statistics (ONS)", "SOC", "A", true},
	"US": {"the U.S. Bureau of Labor Statistics (BLS) Occupational Employment &amp; Wage Statistics and O*NET", "SOC", "A", true},
	"AT": {"Statistics Austria (Statistik Austria)", "ISCO-08", "B", false},
	"BE": {"Statistics Belgium (Statbel)", "ISCO-08", "B", false},
	"CH": {"the Swiss Federal Statistical Office (FSO)", "ISCO-08", "B", false},
	"GR": {"the Hellenic Statistical Authority (ELSTAT)", "ISCO-08", "B", false},
	"HR": {"the Croatian Bureau of Statistics (DZS)", "ISCO-08", "B", false},
	"LT": {"Statistics Lithuania (State Data Agency) &amp; Eurostat SES", "LPK 2023 (ISCO-08)", "B", false},
	"LV": {"the Central Statistical Bureau of Latvia (CSB) &amp; Eurostat SES", "ISCO-08", "B", false},
	"LU": {"the National Institute of Statistics and Economic Studies (STATEC)", "ISCO-08", "B", false},
	"PL": {"Statistics Poland (GUS)", "ISCO-08", "B", false},
	"PT": {"Statistics Portugal (INE)", "ISCO-08", "B", false},
	"RO": {"the National Institute of Statistics (INS)", "ISCO-08", "B", false},
	"SI": {"the Statistical Office of the Republic of Slovenia (SURS)", "ISCO-08 (SKP-08)", "B", false},
	"SK": {"the Statistical Office of the Slovak Republic (ŠÚSR)", "ISCO-08 (SK ISCO-08)", "B", false},
	"TR": {"the Turkish Statistical Institute (TÜİK)", "ISCO-08", "B", false},
	"AR": {"Argentina's INDEC (Permanent Household Survey, EPH)", "ISCO-08", "C", false},
	"CL": {"Chile's National Statistics Institute (INE), National Employment Survey (ENE)", "ISCO-08", "C", false},
	"ID": {"BPS-Statistics Indonesia (Sakernas)", "ISCO-08", "C", false},
	"MY": {"Malaysia's Department of Statistics (DOSM) Labour Force Survey", "ISCO-08", "C", false},
	"TH": {"Thailand's National Statistical Office (NSO) Labour Force Survey", "ISCO-08", "C", false},
	"VN": {"Vietnam's General Statistics Office (GSO) Labour Force Survey", "ISCO-08", "C", false},
}
