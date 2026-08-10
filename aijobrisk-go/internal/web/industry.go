package web

import (
	"fmt"
	"net/http"
	"sort"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

type indRow struct {
	Name, Slug, Href     string
	Aioe                 string
	AioeVal              float64
	HasAioe              bool
	BandCls, BandLabel   string
	Share                string
	ShareVal             float64
	Salary               string
	SalaryVal            float64
	Workforce            string
	WorkforceVal         float64
}

// IndustryVM 行业详情。
type IndustryVM struct {
	*Ctx
	SecName          string
	SecIcon          string
	CC               string
	CountryName      string
	RowsLen          string
	Rows             []indRow
	CountryOpts      []cOpt
	HrefIndustriesCC string
	Adoption         *adoptionChartVM
	FAQ              []faqRow
}

// Industry /industry/{sector}[/{cc}]。
func Industry(w http.ResponseWriter, ctx *Ctx, sector, country string) {
	CL := ctx.CL
	sec := data.SectorByID(sector)
	if sec == nil {
		notFound(w, ctx)
		return
	}
	cc := resolveCC(country)
	occs := data.OccupationsInSector(cc, sec.ID, CL)
	secName := data.Tr(sec.Name, CL)

	vm := &IndustryVM{
		Ctx: ctx, SecName: secName, SecIcon: data.SectorIcon(sec.ID), CC: cc,
		CountryName: data.CountryName(cc, CL), RowsLen: data.Comma(len(occs)),
		HrefIndustriesCC: i18n.HrefIndustries(ctx.Loc, cc),
	}
	if s, ok := data.AdoptionSector(cc, sec.ID); ok {
		vm.Adoption = buildAdoptionChart(ctx, s,
			data.Tr("AI adoption in", CL)+" "+secName, data.AdoptionUSOnly(cc), data.AdoptionIsProxy(sec.ID))
	}
	for _, o := range occs {
		r := indRow{
			Name: o.Name, Slug: o.Slug, Href: i18n.HrefJob(ctx.Loc, o.Slug, cc),
			Share: fmt.Sprintf("%.1f%%", o.Pct), ShareVal: o.Pct,
			Salary: data.FmtSalary(o.Salary, cc), Workforce: data.FmtNum(o.Workforce),
			AioeVal: -1, SalaryVal: -1, WorkforceVal: -1,
		}
		if o.Aioe != nil {
			b := data.ExpBand(o.Aioe)
			r.HasAioe = true
			r.Aioe = fmt.Sprintf("%d", int(*o.Aioe+0.5))
			r.AioeVal = *o.Aioe
			r.BandCls = b.Cls
			r.BandLabel = data.Tr(b.Label, CL)
		} else {
			r.Aioe = "—"
		}
		if o.Salary != nil {
			r.SalaryVal = *o.Salary
		}
		if o.Workforce != nil {
			r.WorkforceVal = *o.Workforce
		}
		vm.Rows = append(vm.Rows, r)
	}
	for _, c := range data.COUNTRIES {
		vm.CountryOpts = append(vm.CountryOpts, cOpt{Code: c, Name: data.CountryName(c, CL), Href: i18n.HrefIndustry(ctx.Loc, sec.ID, c), On: c == cc})
	}

	// 数据驱动的模板 FAQ + FAQPage/BreadcrumbList 结构化数据（答案优先，GEO）。
	vm.FAQ = buildIndustryFAQ(ctx, secName, cc, sec.ID, occs)
	ctx.JSONLD = jsonLD(faqPageLD(vm.FAQ), industryBreadcrumbLD(ctx, cc, secName))

	ctx.Active = "industries"
	ctx.Title = secName + " — " + data.Tr("AI exposure by occupation", CL) + " | AI Job Risk"
	ctx.Description = data.Tr("AI exposure, salary and workforce for occupations in this industry.", CL) + " " + secName + " · " + data.CountryName(cc, CL)
	renderPage(w, "industry.html", vm)
}

// industryValAt 取采纳率序列中某年的值。
func industryValAt(series [][3]float64, year float64) (int, bool) {
	for _, p := range series {
		if p[0] == year {
			return int(p[1] + 0.5), true
		}
	}
	return 0, false
}

// buildIndustryFAQ 由该行业的真实数据生成答案优先的模板 FAQ（缺数据的条目自动跳过）。
func buildIndustryFAQ(ctx *Ctx, secName, cc, sectorID string, occs []data.SectorOcc) []faqRow {
	CL := ctx.CL
	country := data.CountryName(cc, CL)
	var faqs []faqRow

	// 按暴露分排序（仅有分值的）
	var withA []data.SectorOcc
	for _, o := range occs {
		if o.Aioe != nil {
			withA = append(withA, o)
		}
	}
	join3 := func(list []data.SectorOcc) string {
		s := ""
		for i, o := range list {
			if i > 0 {
				s += ", "
			}
			s += fmt.Sprintf("%s (%d%%)", o.Name, int(*o.Aioe+0.5))
		}
		return s
	}

	if len(withA) >= 3 {
		sort.SliceStable(withA, func(i, j int) bool { return *withA[i].Aioe > *withA[j].Aioe })
		top := withA[:3]
		faqs = append(faqs, faqRow{
			Q:    secName + " — " + data.Tr("which occupations are most exposed to AI?", CL),
			A:    data.Tr("The most AI-exposed occupations in this industry are", CL) + " " + join3(top) + ".",
			Open: true,
		})
		bot := make([]data.SectorOcc, len(withA))
		copy(bot, withA)
		sort.SliceStable(bot, func(i, j int) bool { return *bot[i].Aioe < *bot[j].Aioe })
		faqs = append(faqs, faqRow{
			Q: secName + " — " + data.Tr("which occupations are most resilient to AI?", CL),
			A: data.Tr("The most AI-resilient occupations in this industry are", CL) + " " + join3(bot[:3]) + ".",
		})
	}

	// 采纳率
	if s, ok := data.AdoptionSector(cc, sectorID); ok {
		cur, ok1 := industryValAt(s, 2026)
		fut, ok2 := industryValAt(s, 2031)
		if ok1 && ok2 {
			a := fmt.Sprintf("%s %d%% %s %d%% %s", data.Tr("Around", CL), cur,
				data.Tr("of firms in this sector currently use AI in a business function, projected to reach about", CL),
				fut, data.Tr("by 2031.", CL))
			if data.AdoptionUSOnly(cc) {
				a += " " + data.Tr("(US benchmark; national data pending.)", CL)
			}
			faqs = append(faqs, faqRow{
				Q: secName + " — " + data.Tr("what is the AI adoption rate?", CL),
				A: a,
			})
		}
	}

	// 中位暴露 → 高/中/低
	if len(withA) > 0 {
		vals := make([]float64, len(withA))
		for i, o := range withA {
			vals[i] = *o.Aioe
		}
		sort.Float64s(vals)
		med := int(vals[len(vals)/2] + 0.5)
		band := data.Tr("low", CL)
		if med >= 70 {
			band = data.Tr("high", CL)
		} else if med >= 40 {
			band = data.Tr("moderate", CL)
		}
		faqs = append(faqs, faqRow{
			Q: secName + " — " + data.Tr("is it a high-risk industry for AI?", CL),
			A: fmt.Sprintf("%s %d/100 (%s). ", data.Tr("The median AI exposure across these occupations is", CL), med, band) +
				data.Tr("A higher score means more day-to-day tasks are exposed to AI — it does not mean the jobs disappear.", CL),
		})
	}

	// 就业规模（有数据才出）
	var total float64
	for _, o := range occs {
		if o.Workforce != nil {
			total += *o.Workforce
		}
	}
	if total > 0 {
		faqs = append(faqs, faqRow{
			Q: secName + " — " + data.Tr("how many people work in these occupations?", CL),
			A: fmt.Sprintf("%s %s %s %s. %s", data.Tr("About", CL), data.Comma(int(total)),
				data.Tr("people are employed across the tracked occupations in", CL), country,
				data.Tr("Occupations can belong to several industries, so this sums occupation employment rather than industry totals.", CL)),
		})
	}
	return faqs
}

// industryBreadcrumbLD Home › Industries › Sector 的 BreadcrumbList JSON-LD。
func industryBreadcrumbLD(ctx *Ctx, cc, secName string) map[string]any {
	items := []map[string]any{
		{"@type": "ListItem", "position": 1, "name": ctx.Tr("Home"), "item": ctx.Site + ctx.HrefHome()},
		{"@type": "ListItem", "position": 2, "name": ctx.Tr("Industries"),
			"item": ctx.Site + i18n.HrefIndustries(ctx.Loc, cc)},
		{"@type": "ListItem", "position": 3, "name": secName, "item": ctx.CanonicalURL()},
	}
	return map[string]any{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}
}
