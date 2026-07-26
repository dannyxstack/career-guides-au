package web

import (
	"encoding/json"
	"fmt"
	"html/template"
	"net/http"
	"sort"
	"strings"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
	"aijobrisk/internal/model"
)

// ---------- /compare 索引 ----------

type occJSON struct {
	S   string         `json:"s"`
	N   string         `json:"n"`
	E   *int           `json:"e"`
	C   string         `json:"c"`
	Sal map[string]int `json:"sal"`
}
type ctryMeta struct {
	Cur  string `json:"cur"`
	Name string `json:"name"`
}
type popPair struct {
	Key, A, B          string
	Ea, Eb             string
	EaCls, EbCls       string
	HasEa, HasEb       bool
}

// CompareIndexVM 对比索引页。
type CompareIndexVM struct {
	*Ctx
	OccsJSON      template.JS
	CtryJSON      template.JS
	TJSON         template.JS
	DefA, DefB    string
	ComparePrefix string
	Pairs         []popPair
	FAQ           []qaVM
}

func ptrInt(p *float64) *int {
	if p == nil {
		return nil
	}
	v := int(*p + 0.5)
	return &v
}

// CompareIndex /compare。
func CompareIndex(w http.ResponseWriter, ctx *Ctx) {
	CL := ctx.CL

	var occs []occJSON
	for _, slug := range data.JobSlugs {
		g := data.JobBySlug(slug)
		if g == nil {
			continue
		}
		name := data.Name(g.Rep, CL)
		if name == "" {
			continue
		}
		sal := map[string]int{}
		for _, o := range g.Countries {
			if o.AvgSalary.Set {
				sal[o.Country] = int(o.AvgSalary.V + 0.5)
			}
		}
		var e *int
		if g.Rep.AI != nil {
			e = ptrInt(g.Rep.AI.AioePct.Ptr())
		}
		occs = append(occs, occJSON{S: slug, N: name, E: e, C: data.Tr(g.Rep.Category, CL), Sal: sal})
	}
	sort.SliceStable(occs, func(i, j int) bool { return occs[i].N < occs[j].N })

	ctry := map[string]ctryMeta{}
	for _, c := range data.COUNTRIES {
		ctry[c] = ctryMeta{Cur: data.CurrencyOf(c), Name: data.CountryName(c, CL)}
	}

	defA, defB := "", ""
	if len(data.ComparePairs) > 0 {
		defA, defB = data.ComparePairs[0][0], data.ComparePairs[0][1]
	} else if len(occs) >= 2 {
		defA, defB = occs[0].S, occs[1].S
	}

	tstr := map[string]string{
		"na": data.Tr("n/a", CL), "veryHigh": data.Tr("very high", CL), "high": data.Tr("high", CL),
		"moderate": data.Tr("moderate", CL), "low": data.Tr("low", CL), "veryLow": data.Tr("very low", CL),
		"equal": data.Tr("Equal exposure", CL), "higherFor": data.Tr("Higher for", CL),
		"pays": data.Tr("pays", CL), "paysPlus": data.Tr("pays", CL), "paysMore": data.Tr("pays more", CL),
	}

	vm := &CompareIndexVM{
		Ctx: ctx, OccsJSON: jsonJS(occs), CtryJSON: jsonJS(ctry), TJSON: jsonJS(tstr),
		DefA: defA, DefB: defB, ComparePrefix: i18n.HrefCompare(ctx.Loc, "") + "/",
	}
	for _, p := range data.ComparePairs {
		ga, gb := data.JobBySlug(p[0]), data.JobBySlug(p[1])
		pp := popPair{Key: data.PairKey(p[0], p[1]), A: data.Name(ga.Rep, CL), B: data.Name(gb.Rep, CL)}
		if ga.Rep.AI != nil && ga.Rep.AI.AioePct.Set {
			pp.HasEa = true
			pp.Ea = fmt.Sprintf("%d", int(ga.Rep.AI.AioePct.V+0.5))
			pp.EaCls = data.ExpBand(ga.Rep.AI.AioePct.Ptr()).Cls
		}
		if gb.Rep.AI != nil && gb.Rep.AI.AioePct.Set {
			pp.HasEb = true
			pp.Eb = fmt.Sprintf("%d", int(gb.Rep.AI.AioePct.V+0.5))
			pp.EbCls = data.ExpBand(gb.Rep.AI.AioePct.Ptr()).Cls
		}
		vm.Pairs = append(vm.Pairs, pp)
	}
	vm.FAQ = []qaVM{
		{data.Tr("How does the comparison work?", CL), data.Tr("We combine occupation-level data from national labour statistics with generative-AI exposure scores from ILO Working Paper 140 and Eloundou et al. (OpenAI). Each occupation is scored on a 0–100 exposure percentile based on task overlap with large language models.", CL)},
		{data.Tr("What does the AI exposure score mean?", CL), data.Tr("A low percentile means minimal exposure (tasks unlikely to be automated or augmented by AI); a high percentile means near-full exposure. Scores reflect the share of tasks that could be affected by current generative AI, not job elimination.", CL)},
		{data.Tr("Where does the data come from?", CL), data.Tr("Official sources include the U.S. Bureau of Labor Statistics, UK ONS, Australia Jobs and Skills, Germany BA and others. AI-exposure research is drawn from the ILO working paper and Eloundou et al. Figures are estimates and indicative only.", CL)},
		{data.Tr("Can I trust the risk labels?", CL), data.Tr("Risk labels (low/moderate/high) always appear alongside the numeric score and a text description — colour is never the sole indicator. The full methodology is documented on the Methodology page.", CL)},
	}

	ctx.Active = "compare"
	ctx.Title = data.Tr("Compare occupations side by side", CL) + " — " + data.Tr("AI risk, salary & outlook", CL) + " | AI Job Risk"
	ctx.Description = data.Tr("Compare two occupations: AI exposure, salary and the human moat, built on official labour statistics and AI-exposure research.", CL)
	renderPage(w, "compare_index.html", vm)
}

func jsonJS(v any) template.JS {
	b, _ := json.Marshal(v)
	return template.JS(b)
}

// ---------- /compare/{a}-vs-{b} ----------

type cmpSide struct {
	Name, Slug, Href, CatIcon      string
	Exp                            string
	SevCls, BandLabel              string
	HasAioe                        bool
	Aioe                           int
	HasMoat                        bool
	Moat                           string
	Country                        string
	Replaced, Aug, Moatl           []string
	MoatVal                        string
	MoatLbl                        string
	MoatDeep, MoatShallow          bool
	MoatWidth                      int
	HasMoatBar                     bool
	Salary, Edu, Cert, Prospect, Demand, Overall string
}

// ComparePairVM 对比详情。
type ComparePairVM struct {
	*Ctx
	Na, Nb          string
	HrefCompareHub  string
	Sides           []cmpSide
	Verdict         string
	FAQ             []qaVM
	NoTaskData      string
}

func sevClsOf(cls string) string {
	if cls == "high" || cls == "critical" {
		return "high"
	}
	if cls == "moderate" {
		return "mid"
	}
	return "low"
}

// ComparePair /compare/{a}-vs-{b}。
func ComparePair(w http.ResponseWriter, ctx *Ctx, pair string) {
	CL := ctx.CL
	parts := strings.Split(pair, "-vs-")
	if len(parts) != 2 {
		notFound(w, ctx)
		return
	}
	ga, gb := data.JobBySlug(parts[0]), data.JobBySlug(parts[1])
	if ga == nil || gb == nil {
		notFound(w, ctx)
		return
	}
	a := data.OccFull(ga.Rep)
	b := data.OccFull(gb.Rep)
	na := data.Name(a, CL)
	nb := data.Name(b, CL)

	trList := func(arr []string) []string {
		out := make([]string, 0, len(arr))
		for _, x := range arr {
			out = append(out, data.Tr(x, CL))
		}
		return out
	}
	dimVal := func(o *model.Occ, dim string) *float64 { return o.Rating(dim) }
	scale := func(v *float64) string {
		if v == nil {
			return "—"
		}
		return fmt.Sprintf("%g/10", *v)
	}
	certLabel := func(o *model.Occ) string {
		v := dimVal(o, "certification_difficulty")
		if v == nil {
			return "—"
		}
		lbl := data.Tr("Low", CL)
		if *v >= 7 {
			lbl = data.Tr("High", CL)
		} else if *v >= 4 {
			lbl = data.Tr("Moderate", CL)
		}
		return fmt.Sprintf("%g/10 (%s)", *v, lbl)
	}
	eduSummary := func(o *model.Occ) string {
		if len(o.Education) == 0 {
			return "—"
		}
		f := o.Education[0]
		stage := data.Tr(f.Stage, CL)
		dur := data.Tr(f.Duration, CL)
		more := ""
		if len(o.Education) > 1 {
			more = fmt.Sprintf(" (+%d %s)", len(o.Education)-1, data.Tr("more", CL))
		}
		if dur != "" {
			return stage + " · " + dur + more
		}
		return stage + more
	}

	build := func(o *model.Occ, n string) cmpSide {
		var exp, aioe, moat *float64
		if o.AI != nil {
			exp = o.AI.AutomationExposure.Ptr()
			aioe = o.AI.AioePct.Ptr()
			moat = o.AI.HumanMoat.Ptr()
		}
		band := data.RiskBand10(exp)
		s := cmpSide{
			Name: n, Slug: o.Slug, Href: i18n.HrefJob(ctx.Loc, o.Slug, ""), CatIcon: data.CategoryIcon(o.Category),
			SevCls: sevClsOf(band.Cls), BandLabel: data.Tr(band.Label, CL), Country: data.CountryName(o.Country, CL),
			Salary: data.FmtSalary(o.AvgSalary.Ptr(), o.Country), Edu: eduSummary(o), Cert: certLabel(o),
			Prospect: scale(dimVal(o, "future_prospect")), Demand: scale(dimVal(o, "job_demand")),
		}
		if exp != nil {
			s.Exp = fmt.Sprintf("%.1f", *exp)
		} else {
			s.Exp = "—"
		}
		if aioe != nil {
			s.HasAioe = true
			s.Aioe = int(*aioe + 0.5)
		}
		if moat != nil {
			s.HasMoat = true
			s.Moat = fmt.Sprintf("%g", *moat)
			s.HasMoatBar = true
			s.MoatVal = fmt.Sprintf("%.1f", *moat)
			s.MoatWidth = int(*moat * 10)
			s.MoatDeep = *moat >= 6
			s.MoatShallow = *moat < 4
			if *moat >= 6 {
				s.MoatLbl = data.Tr("Deep", CL)
			} else if *moat >= 4 {
				s.MoatLbl = data.Tr("Moderate", CL)
			} else {
				s.MoatLbl = data.Tr("Shallow", CL)
			}
		}
		if o.OverallScore.Set {
			s.Overall = fmt.Sprintf("%g/10", o.OverallScore.V)
		} else {
			s.Overall = "—"
		}
		if o.AI != nil {
			s.Replaced = trList(o.AI.ReplacedZh)
			s.Aug = trList(o.AI.AugmentedZh)
			s.Moatl = trList(o.AI.MoatZh)
		}
		return s
	}

	sa := build(a, na)
	sb := build(b, nb)

	vm := &ComparePairVM{
		Ctx: ctx, Na: na, Nb: nb, HrefCompareHub: i18n.HrefCompare(ctx.Loc, ""),
		Sides: []cmpSide{sa, sb}, NoTaskData: data.Tr("No task data.", CL),
		Verdict: cmpVerdict(a, b, na, nb, CL),
	}
	vm.FAQ = []qaVM{
		{data.Tr("Should a", CL) + " " + lower(na) + " " + data.Tr("retrain toward", CL) + " " + lower(nb) + "?", data.Tr("It depends on the human moat and pay gap. A deeper moat and higher salary can justify retraining, but weigh the education path and certification barrier shown above. Focus on analytical, advisory and AI-tooling skills either way.", CL)},
		{data.Tr("Will AI eliminate these jobs entirely?", CL), data.Tr("Not entirely. High exposure means routine tasks (data entry, standard drafting, reconciliation) are highly automatable, while judgement, advisory and accountability remain human. Workers who move up into those areas stay valuable.", CL)},
		{data.Tr("What does the AI task-exposure score mean?", CL), data.Tr("The 0–10 score reflects how much of an occupation's core tasks could be performed or substantially augmented by generative AI, based on task-exposure research. Higher means greater potential disruption — not a guarantee of job loss.", CL)},
		{data.Tr("Where does the data come from?", CL), data.Tr(`Official national labour statistics (e.g. BLS OEWS, O*NET) combined with generative-AI exposure research — ILO Working Paper 140 and Eloundou et al. "GPTs are GPTs" (OpenAI). The ILO paper is a working paper, not peer-reviewed. Figures are estimates and indicative only.`, CL)},
	}

	ctx.Active = "compare"
	ctx.Title = na + " " + data.Tr("vs", CL) + " " + nb + ": " + data.Tr("AI risk comparison", CL) + " | AI Job Risk"
	ctx.Description = data.Tr("Compare", CL) + " " + na + " " + data.Tr("and", CL) + " " + nb + ": " + data.Tr("AI task exposure, the tasks AI takes over and augments, the human moat, salary, education and demand.", CL)
	renderPage(w, "compare_pair.html", vm)
}

func cmpVerdict(a, b *model.Occ, na, nb, CL string) string {
	if a.AI == nil || b.AI == nil {
		return na + " " + data.Tr("and", CL) + " " + nb + " " + data.Tr("differ in how AI reshapes their tasks — compare the exposure, human moat and dimensions below.", CL)
	}
	sExp := func(o *model.Occ) *float64 { return o.AI.AutomationExposure.Ptr() }
	scale := func(v *float64) string {
		if v == nil {
			return "—"
		}
		return fmt.Sprintf("%g/10", *v)
	}
	ma, mb := a.AI.HumanMoat.Ptr(), b.AI.HumanMoat.Ptr()
	hiN, hiM, loM := na, ma, mb
	if valOr(mb, 0) > valOr(ma, 0) {
		hiN, hiM, loM = nb, mb, ma
	}
	loN := nb
	if hiN == nb {
		loN = na
	}
	_ = loN
	s := data.Tr("Both roles face notable AI task exposure", CL) + " (" + scale(sExp(a)) + " " + data.Tr("vs", CL) + " " + scale(sExp(b)) + ")."
	if hiM != nil && loM != nil && *hiM != *loM {
		s += " " + hiN + " — " + data.Tr("deeper human moat", CL) + " (" + fmt.Sprintf("%g", *hiM) + "/10 " + data.Tr("vs", CL) + " " + fmt.Sprintf("%g", *loM) + "/10) " + data.Tr("makes it more resilient to AI displacement.", CL)
	}
	// 薪资更高者
	pn, ps, pc := na, a.AvgSalary.Ptr(), a.Country
	if valOr(b.AvgSalary.Ptr(), 0) >= valOr(a.AvgSalary.Ptr(), 0) {
		pn, ps, pc = nb, b.AvgSalary.Ptr(), b.Country
	}
	if ps != nil {
		s += " " + pn + " " + data.Tr("pays more on average", CL) + " (" + data.FmtSalary(ps, pc) + ")."
	}
	return s
}

func valOr(p *float64, d float64) float64 {
	if p == nil {
		return d
	}
	return *p
}
