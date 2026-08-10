package web

import (
	"net/http"
	"sort"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

func riskColor(aioe *float64) string {
	b := data.ExpBand(aioe)
	switch b.Cls {
	case "critical", "high":
		return "var(--risk-high)"
	case "moderate":
		return "var(--risk-mid-fg)"
	default:
		return "var(--risk-low)"
	}
}

type indExtreme struct {
	Name, Color string
	Has         bool
}
type indCard struct {
	ID, Name, Icon string
	Count          string
	Workforce      string // 该行业从业人口合计
	HasWorkforce   bool
	Riskiest       indExtreme
	Safest         indExtreme
	HasExtremes    bool
	Href           string
}
type cOpt struct {
	Code, Name, Href string
	On               bool
}

// IndustriesVM 行业总览。
type IndustriesVM struct {
	*Ctx
	CC          string
	CountryName string
	Cards       []indCard
	CountryOpts []cOpt
	Adoption    *adoptionChartVM
}

func resolveCC(country string) string {
	for _, c := range data.COUNTRIES {
		if c == country {
			return country
		}
	}
	return "US"
}

// Industries /industries[/{cc}]。
func Industries(w http.ResponseWriter, ctx *Ctx, country string) {
	CL := ctx.CL
	cc := resolveCC(country)

	type sc struct {
		s     *data.Sector
		count int
	}
	var scs []sc
	for _, s := range data.Sectors {
		scs = append(scs, sc{s, s.ByCountry[cc]})
	}
	sort.SliceStable(scs, func(i, j int) bool { return scs[i].count > scs[j].count })

	used := map[string]bool{}
	var cards []indCard
	for _, x := range scs {
		occs := data.OccupationsInSector(cc, x.s.ID, CL)
		var withExp []data.SectorOcc
		for _, o := range occs {
			if o.Aioe != nil {
				withExp = append(withExp, o)
			}
		}
		wfTotal := 0.0
		wfHas := false
		for _, o := range occs {
			if o.Workforce != nil {
				wfTotal += *o.Workforce
				wfHas = true
			}
		}
		byRisk := make([]data.SectorOcc, len(withExp))
		copy(byRisk, withExp)
		sort.SliceStable(byRisk, func(i, j int) bool { return *byRisk[i].Aioe > *byRisk[j].Aioe })
		bySafe := make([]data.SectorOcc, len(withExp))
		copy(bySafe, withExp)
		sort.SliceStable(bySafe, func(i, j int) bool { return *bySafe[i].Aioe < *bySafe[j].Aioe })

		var riskiest, safest indExtreme
		var riskiestSlug string
		for _, o := range byRisk {
			if !used[o.Slug] {
				riskiest = indExtreme{Name: o.Name, Color: riskColor(o.Aioe), Has: true}
				riskiestSlug = o.Slug
				used[o.Slug] = true
				break
			}
		}
		if !riskiest.Has && len(byRisk) > 0 {
			o := byRisk[0]
			riskiest = indExtreme{Name: o.Name, Color: riskColor(o.Aioe), Has: true}
			riskiestSlug = o.Slug
		}
		for _, o := range bySafe {
			if !used[o.Slug] {
				safest = indExtreme{Name: o.Name, Color: riskColor(o.Aioe), Has: true}
				used[o.Slug] = true
				break
			}
		}
		if !safest.Has {
			for _, o := range bySafe {
				if o.Slug != riskiestSlug {
					safest = indExtreme{Name: o.Name, Color: riskColor(o.Aioe), Has: true}
					break
				}
			}
		}

		wfStr := ""
		if wfHas {
			wfStr = data.Comma(int(wfTotal + 0.5))
		}
		cards = append(cards, indCard{
			ID: x.s.ID, Name: data.Tr(x.s.Name, CL), Icon: data.SectorIcon(x.s.ID),
			Count: data.Comma(x.count), Workforce: wfStr, HasWorkforce: wfHas,
			Riskiest: riskiest, Safest: safest,
			HasExtremes: riskiest.Has || safest.Has, Href: i18n.HrefIndustry(ctx.Loc, x.s.ID, cc),
		})
	}

	vm := &IndustriesVM{Ctx: ctx, CC: cc, CountryName: data.CountryName(cc, CL), Cards: cards}
	if data.AdoptionHas() {
		vm.Adoption = buildAdoptionChart(ctx, data.AdoptionAll(cc),
			data.Tr("AI adoption across all industries", CL), data.AdoptionUSOnly(cc), false)
	}
	for _, c := range data.COUNTRIES {
		vm.CountryOpts = append(vm.CountryOpts, cOpt{Code: c, Name: data.CountryName(c, CL), Href: i18n.HrefIndustries(ctx.Loc, c), On: c == cc})
	}

	ctx.Active = "industries"
	ctx.Title = data.Tr("Industries — AI exposure across 20 sectors", CL) + " | AI Job Risk"
	ctx.Description = data.Tr("Explore AI exposure across 20 industry sectors. An occupation can belong to several industries (many-to-many).", CL)
	renderPage(w, "industries.html", vm)
}
