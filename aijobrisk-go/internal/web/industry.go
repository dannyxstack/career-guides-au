package web

import (
	"fmt"
	"net/http"

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

	ctx.Active = "industries"
	ctx.Title = secName + " — " + data.Tr("AI exposure by occupation", CL) + " | AI Job Risk"
	ctx.Description = data.Tr("AI exposure, salary and workforce for occupations in this industry.", CL) + " " + secName + " · " + data.CountryName(cc, CL)
	renderPage(w, "industry.html", vm)
}
