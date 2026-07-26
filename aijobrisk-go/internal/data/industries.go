package data

import "sort"

// —— 行业轴（occupation↔industry 多对多，读 occ_industries_v2 + industries_v2）——

type occIndEntry struct {
	S string `json:"s"`
	N string `json:"n"`
	P float64 `json:"p"`
}

var occInd map[string][]occIndEntry

// Sector 行业。
type Sector struct {
	ID       string         `json:"id"`
	Name     string         `json:"name"`
	OccTotal int            `json:"occ_total"`
	ByCountry map[string]int `json:"by_country"`
}

var Sectors []*Sector

func loadIndustries() error {
	var oi struct {
		Occ map[string][]occIndEntry `json:"occ"`
	}
	if err := readJSON("occ_industries_v2.json", &oi); err != nil {
		return err
	}
	occInd = oi.Occ
	var ind struct {
		Sectors []*Sector `json:"sectors"`
	}
	if err := readJSON("industries_v2.json", &ind); err != nil {
		return err
	}
	Sectors = ind.Sectors
	return nil
}

// SectorByID 取行业。
func SectorByID(id string) *Sector {
	for _, s := range Sectors {
		if s.ID == id {
			return s
		}
	}
	return nil
}

var sectorIconMap = map[string]string{
	"admin-support": "fa-clipboard-list", "government": "fa-landmark", "education": "fa-graduation-cap",
	"other-services": "fa-screwdriver-wrench", "professional": "fa-briefcase", "manufacturing": "fa-industry",
	"wholesale": "fa-boxes-stacked", "retail": "fa-cart-shopping", "health": "fa-heart-pulse",
	"construction": "fa-helmet-safety", "management": "fa-sitemap", "arts": "fa-masks-theater",
	"real-estate": "fa-building", "information": "fa-tower-broadcast", "transport": "fa-truck-fast",
	"hospitality": "fa-utensils", "finance": "fa-coins", "utilities": "fa-plug", "mining": "fa-mountain",
	"agriculture": "fa-tractor",
}

// SectorIcon 行业图标。
func SectorIcon(id string) string {
	if v, ok := sectorIconMap[id]; ok {
		return v
	}
	return "fa-layer-group"
}

var categoryIconMap = map[string]string{
	"Trades & Construction":               "fa-helmet-safety",
	"Business, Finance & Legal":           "fa-briefcase",
	"Healthcare & Care":                   "fa-heart-pulse",
	"Engineering & Infrastructure":        "fa-gears",
	"Creative, Media & Personal Services": "fa-palette",
	"Hospitality, Retail & Tourism":       "fa-utensils",
	"Transport, Logistics & Mining":       "fa-truck-fast",
	"Education & Community":               "fa-graduation-cap",
	"Agriculture & Environment":           "fa-leaf",
	"Government & Public Sector":          "fa-landmark",
	"IT & Digital":                        "fa-code",
}

// CategoryIcon 职业族图标。
func CategoryIcon(name string) string {
	if v, ok := categoryIconMap[name]; ok {
		return v
	}
	return "fa-briefcase"
}

// SectorOcc 行业下职业行。
type SectorOcc struct {
	Name      string
	Slug      string
	CatSlug   string
	Pct       float64
	Aioe      *float64
	Salary    *float64
	Workforce *float64
}

// OccupationsInSector 某国某行业下职业（按人数降序）。
func OccupationsInSector(country, sectorID, loc string) []SectorOcc {
	var out []SectorOcc
	for _, o := range OccByCountry(country) {
		rels := occInd[itoa(o.ID)]
		if rels == nil {
			continue
		}
		var hit *occIndEntry
		for i := range rels {
			if rels[i].S == sectorID {
				hit = &rels[i]
				break
			}
		}
		if hit == nil {
			continue
		}
		var aioe, sal, wf *float64
		if o.AI != nil {
			aioe = o.AI.AioePct.Ptr()
		}
		sal = o.AvgSalary.Ptr()
		wf = o.WorkforceSize.Ptr()
		out = append(out, SectorOcc{
			Name: Name(o, loc), Slug: o.Slug, CatSlug: CatSlug(o.Category), Pct: hit.P,
			Aioe: aioe, Salary: sal, Workforce: wf,
		})
	}
	sort.SliceStable(out, func(i, j int) bool { return f(out[i].Workforce) > f(out[j].Workforce) })
	return out
}

func f(p *float64) float64 {
	if p == nil {
		return 0
	}
	return *p
}
