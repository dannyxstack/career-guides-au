package web

import (
	"net/http"
	"regexp"
	"strings"

	"aijobrisk/internal/data"
)

type tagVM struct {
	Icon, Name, Href   string
	HasPct             bool
	Pct                int
	BorderColor        string
}
type rankVM struct{ Icon, Name, Href string; Pct int }
type hotVM struct {
	Name, CatIcon, CatName, Href string
	Pct                          int
	BarColor, PctColor           string
}
type qaVM struct{ Q, A string }

// HomeVM 首页视图模型。
type HomeVM struct {
	*Ctx
	HeroL1, HeroL2 string
	PctHigh        int
	GlobalJobs     int
	CountryCount   int
	HotTags        []tagVM
	MostExposed    []rankVM
	LeastExposed   []rankVM
	HotJobs        []hotVM
	FAQ            []qaVM
}

func barColor(pct int) string {
	if pct >= 70 {
		return "linear-gradient(90deg,#f59e0b,#dc2626)"
	}
	if pct >= 40 {
		return "#f59e0b"
	}
	return "#059669"
}
func pctColor(pct int) string {
	if pct >= 70 {
		return "#dc2626"
	}
	if pct >= 40 {
		return "#f59e0b"
	}
	return "#059669"
}

var heroSplitters = []*regexp.Regexp{
	regexp.MustCompile(`\s+—\s+`),
	regexp.MustCompile(`——`),
	regexp.MustCompile(`:\s+`),
}

// heroLines 在主句/反问句边界断两行（对齐 index.astro heroLines）。
func heroLines(s string) (string, string) {
	for _, re := range heroSplitters {
		if m := re.FindStringIndex(s); m != nil {
			sep := s[m[0]:m[1]]
			first, rest := s[:m[0]], s[m[1]:]
			if strings.Contains(sep, "—") {
				return first, strings.TrimLeft(sep, " \t") + rest
			}
			return first + strings.TrimRight(sep, " \t"), rest
		}
	}
	return s, ""
}

// Home 首页处理器。
func Home(w http.ResponseWriter, ctx *Ctx) {
	CL := ctx.CL
	ctx.Active = "occupations"
	ctx.Title = data.Tr("AI Job Risk — is your job still here in 5 years?", CL)
	ctx.Description = data.Tr("Check AI replacement risk, task exposure and the human moat across occupations and countries, with local salary, licensing and outlook.", CL)

	globalJobs := len(data.JobSlugs)
	countryCount := len(data.COUNTRIES)

	// 全球聚合
	type gjob struct {
		slug, cat, name string
		exp             *float64
		work            float64
	}
	var globals []gjob
	withExp, highExp := 0, 0
	for _, slug := range data.JobSlugs {
		g := data.JobBySlug(slug)
		if g == nil {
			continue
		}
		var exp *float64
		if g.Rep.AI != nil {
			exp = g.Rep.AI.AioePct.Ptr()
		}
		if exp != nil {
			withExp++
			if *exp >= 70 {
				highExp++
			}
		}
		work := 0.0
		for _, o := range g.Countries {
			work += o.WorkforceSize.V
		}
		globals = append(globals, gjob{slug: slug, cat: g.Rep.Category, name: data.Name(g.Rep, CL), exp: exp, work: work})
	}
	pctHigh := 0
	if withExp > 0 {
		pctHigh = int(float64(highExp)/float64(withExp)*100 + 0.5)
	}

	// 热门职业：有暴露分 + 有人数，按人数降序
	var hotRanked []gjob
	for _, g := range globals {
		if g.exp != nil && g.work > 0 {
			hotRanked = append(hotRanked, g)
		}
	}
	sortStable(hotRanked, func(a, b gjob) bool { return a.work > b.work })

	// hero 标签：每个 category 取人数最高一个，凑 6 个
	var hotTags []tagVM
	seenCat := map[string]bool{}
	for _, g := range hotRanked {
		if seenCat[g.cat] {
			continue
		}
		seenCat[g.cat] = true
		t := tagVM{Icon: data.CategoryIcon(g.cat), Name: g.name, Href: ctx.HrefJob(g.slug), BorderColor: "var(--line)"}
		if g.exp != nil { // 按 AI 暴露分给边框上色 + 显示风险值（同热门卡分级）
			t.HasPct, t.Pct = true, int(*g.exp+0.5)
			t.BorderColor = pctColor(t.Pct)
		}
		hotTags = append(hotTags, t)
		if len(hotTags) >= 6 {
			break
		}
	}

	// 热门职业卡（12）
	var hotJobs []hotVM
	for i, g := range hotRanked {
		if i >= 12 {
			break
		}
		pct := int(*g.exp + 0.5)
		hotJobs = append(hotJobs, hotVM{
			Name: g.name, CatIcon: data.CategoryIcon(g.cat), CatName: data.Tr(g.cat, CL),
			Href: ctx.HrefJob(g.slug), Pct: pct, BarColor: barColor(pct), PctColor: pctColor(pct),
		})
	}

	// 榜单预览（US）
	boards := data.BuildBoards("US", 5, CL)
	toRank := func(b *data.Board) []rankVM {
		var out []rankVM
		for _, it := range b.Items {
			p := 0
			if it.Aioe != nil {
				p = int(*it.Aioe + 0.5)
			}
			out = append(out, rankVM{Icon: data.CategoryIcon(it.Cat), Name: it.Name, Href: ctx.HrefJob(it.Slug), Pct: p})
		}
		return out
	}
	var mostExposed, leastExposed []rankVM
	for i := range boards {
		if boards[i].ID == "most-exposed" {
			mostExposed = toRank(&boards[i])
		}
		if boards[i].ID == "least-exposed" {
			leastExposed = toRank(&boards[i])
		}
	}

	// hero 大标题
	heroRaw := strings.Replace(
		data.Tr("AI is reshaping {n}+ jobs worldwide — is yours still in the safe zone?", CL),
		"{n}", data.Comma((globalJobs/100)*100), 1)
	l1, l2 := heroLines(heroRaw)

	faq := []qaVM{
		{data.Tr("Which jobs will AI most likely replace?", CL), data.Tr("The highest-exposure roles are repetitive and rule-based — clerks, data entry, standard writing and lookup tasks. Their work is highly structured and easy to model. Even so, full replacement is rare; more often the task mix is reshaped.", CL)},
		{data.Tr(`What exactly is the "human moat"?`, CL), data.Tr("The human moat is the set of capabilities AI struggles to replace: complex judgement, empathy and care relationships, creativity, cross-domain integration, and face-to-face trust. These rely on human experience, intuition and accountability.", CL)},
		{data.Tr("My job scores high risk — should I switch careers now?", CL), data.Tr("Not blindly. High risk does not mean unemployment; it means your task mix is being reshaped. Learn to use AI tools, move toward AI-augmented work, and strengthen moat skills like client communication and strategic judgement. Assess before you act.", CL)},
		{data.Tr("How is the AI exposure score calculated?", CL), data.Tr(`The exposure percentile comes from two open, authoritative studies — the ILO Working Paper 140 and Eloundou et al. "GPTs are GPTs" (OpenAI) — mapped onto official occupation classifications, not our own opinion.`, CL)},
		{data.Tr("Is the ranking data reliable?", CL), data.Tr("We integrate public labour statistics (BLS, ONS, ABS, etc.), official occupation classifications, and published AI-capability research. All figures are estimates, sourced and updated periodically, and indicative only.", CL)},
	}

	vm := &HomeVM{
		Ctx: ctx, HeroL1: l1, HeroL2: l2, PctHigh: pctHigh, GlobalJobs: globalJobs, CountryCount: countryCount,
		HotTags: hotTags, MostExposed: mostExposed, LeastExposed: leastExposed, HotJobs: hotJobs, FAQ: faq,
	}
	renderPage(w, "index.html", vm)
}
