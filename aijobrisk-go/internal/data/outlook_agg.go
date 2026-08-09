package data

import (
	"sort"
	"sync"
)

// Career outlook —— 官方就业预测（occupation_outlook；growth_pct 为预测期名义增速 %）。
// 数据源各国官方：BLS(US)/CEDEFOP(EU)/JSA(AU)/COPS(CA)/KEIS(KR)/Skills Imperative(UK) 等，
// 懒加载于 occ-detail-v2；33/46 国有数据，缺者页面优雅隐藏。绝非我们自建模型（与 AI job loss 区分）。

// OutlookRow 单职业（含国家 detail）的官方就业预测行。
type OutlookRow struct {
	Slug, NameEn, Country string
	Growth                float64 // growth_pct（%）
	Source                string
	Granularity           string  // occupation / group（群组级为 ISCO 两位共享）
	Exposure              float64 // automation_exposure 1..10（供增速×AI暴露交叉分析）
}

// OutlookMax 排行榜离群值上限：|growth| 超过此值视为小基数假象，剔除出榜（仍见于职业详情页）。
const OutlookMax = 150.0

var (
	outlookOnce      sync.Once
	outlookByCC      map[string][]OutlookRow
	outlookCountries []string
)

func buildOutlook() {
	outlookByCC = map[string][]OutlookRow{}
	for _, o := range Occupations {
		full := OccFull(o)
		if full.Outlook == nil || full.Outlook.GrowthPct == nil {
			continue
		}
		exp := 0.0
		if o.AI != nil {
			exp = o.AI.AutomationExposure.V
		}
		outlookByCC[o.Country] = append(outlookByCC[o.Country], OutlookRow{
			Slug: o.Slug, NameEn: o.NameEn, Country: o.Country,
			Growth: *full.Outlook.GrowthPct, Source: full.Outlook.Source,
			Granularity: full.Outlook.Granularity, Exposure: exp,
		})
	}
	for cc := range outlookByCC {
		outlookCountries = append(outlookCountries, cc)
	}
	sort.Strings(outlookCountries)
}

// OutlookByCountry 返回某国的官方预测行（缺失返回 nil）。
func OutlookByCountry(cc string) []OutlookRow {
	outlookOnce.Do(buildOutlook)
	return outlookByCC[cc]
}

// OutlookCountries 有 outlook 数据的国家码（字母序）。
func OutlookCountries() []string {
	outlookOnce.Do(buildOutlook)
	return outlookCountries
}

// HasOutlook 该国是否有官方就业预测数据。
func HasOutlook(cc string) bool {
	outlookOnce.Do(buildOutlook)
	return len(outlookByCC[cc]) > 0
}

// OutlookAgg 按职业名跨国聚合的全局视图（用于 hub 榜单，稳健于单国离群）。
type OutlookAgg struct {
	NameEn      string
	Slug        string
	AvgGrowth   float64
	AvgExposure float64
	NCountries  int
}

// OutlookGlobal 按职业名聚合全部国家的平均增速/暴露；minCountries 过滤弱信号，
// 且剔除 |AvgGrowth| > maxAbs 的离群项（hub 榜单用比国家页更严的阈值，滤除群组级小基数假象）。
// 返回未排序切片。
func OutlookGlobal(minCountries int, maxAbs float64) []OutlookAgg {
	outlookOnce.Do(buildOutlook)
	type acc struct {
		slug             string
		sumG, sumE       float64
		n                int
	}
	m := map[string]*acc{}
	for _, rows := range outlookByCC {
		for _, r := range rows {
			a := m[r.NameEn]
			if a == nil {
				a = &acc{slug: r.Slug}
				m[r.NameEn] = a
			}
			a.sumG += r.Growth
			a.sumE += r.Exposure
			a.n++
		}
	}
	var out []OutlookAgg
	for name, a := range m {
		if a.n < minCountries {
			continue
		}
		avgG := a.sumG / float64(a.n)
		if avgG > maxAbs || avgG < -maxAbs {
			continue
		}
		out = append(out, OutlookAgg{
			NameEn: name, Slug: a.slug, AvgGrowth: avgG,
			AvgExposure: a.sumE / float64(a.n), NCountries: a.n,
		})
	}
	return out
}
