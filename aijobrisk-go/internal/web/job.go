package web

import (
	"encoding/json"
	"fmt"
	"html/template"
	"net/http"
	"strings"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
	"aijobrisk/internal/model"
)

const networkAssessment = "https://ismyjobaiproof.com"

type scoreVM struct{ Label, Val string }
type disVM struct {
	Name, URL, Type, LevelCls, Level, Year, Scope string
	HasURL                                        bool
}
type adjVM struct{ Name, Href string }
type tabVM struct {
	Flag       template.HTML
	Name, Href string
	On         bool
}
type salRow struct{ Label, Pay, Note string }
type eduRow struct{ Stage, Duration, Cost string }
type qualRow struct {
	Name, Issuer string
	Mandatory    bool
}
type visaRow struct{ Subclass, Name, Desc string }
type faqRow struct {
	Q, A string
	Open bool
}
type badgeVM struct{ Cls, Text string }
type listCard struct {
	Title string
	Items []string
}

// JobVM 职业详情视图模型。
type JobVM struct {
	*Ctx
	DispName, Nm string
	ShowLatin    bool
	DataUpdated  string
	CatName      string
	CatURL       string
	CodeLabel    string
	OccCodeType  string
	CountriesLen int
	HasHeadline  bool
	HeadlinePct  int
	BandCls      string
	BandLabelTr  string
	// meter
	HasAioe                                  bool
	MeterUnit                                string
	FirstReplaced, FirstAugmented, FirstMoat string
	AioePct                                  int
	Verdict                                  string
	// scores
	ScoresCls          string
	Scores             []scoreVM
	Assessment, MapURL string
	// AI zone
	HasAI       bool
	AICards     []listCard // 4 tint cards（replaced/augmented/moat/skills）
	EntryNote   string
	UpgradePath string
	Disruptors  []disVM
	Adjacent    []adjVM
	// country
	Tabs []tabVM
	// active panel
	OverallScore       string
	Workforce          string
	AvgSalary          string
	MigBadge           badgeVM
	Currency           string
	RadarSVG           template.HTML
	Salaries           []salRow
	Education          []eduRow
	Qualifications     []qualRow
	MigCountryName     string
	IsMigration        int
	MigNote            string
	Visas              []visaRow
	NonMigVisa         string
	MigMode            string // full=逐职业块 / info=一段话+链接 / none=不显示
	MigInfoBody        string
	MigInfoURL         template.URL
	MigInfoLink        string
	ShowMigBadge       bool
	SuitFit, SuitUnfit []string
	Trend, Forecast    string
	GrowthAreas        []string
	Outlook            *outlookChartVM
	SalaryChart        *salaryChartVM
	Loss               *jobLossOccVM
	FAQ                []faqRow
	SourcesBody        string
	Poll               PollWidget
}

func f1(v *float64) string {
	if v == nil {
		return "—"
	}
	return fmt.Sprintf("%.1f/10", *v)
}

// Job 职业详情处理器。bare 形如 /jobs/{slug} 或 /jobs/{slug}/{cc}。
func Job(w http.ResponseWriter, ctx *Ctx, slug, country string) {
	CL := ctx.CL
	group := data.JobBySlug(slug)
	if group == nil {
		// 去重旧 slug → canonical：应用层 301（保留语言前缀、国家段与 query），nginx 不耦合业务数据。
		if canon, ok := data.RedirectSlug(slug); ok {
			w.Header().Set("Location", i18n.HrefJob(ctx.Loc, canon, country)+ctx.Query)
			w.WriteHeader(http.StatusMovedPermanently)
			return
		}
		notFound(w, ctx)
		return
	}
	ctx.Noindex = data.IsNEC(slug) // C3：n.e.c. 兜底桶降权
	rep := data.OccFull(group.Rep)
	ai := rep.AI
	nm := rep.NameEn
	dispName := data.Name(rep, CL)

	countries := make([]*model.Occ, len(group.Countries))
	for i, o := range group.Countries {
		countries[i] = data.OccFull(o)
	}
	active := countries[0]
	if country != "" {
		for _, o := range countries {
			if o.Country == country {
				active = o
				break
			}
		}
	}
	cc := active.Country
	cur := active.Currency
	if cur == "" {
		cur = data.CurrencyOf(cc)
	}

	// 风险刻度
	var exposure, moat, entry, upside, aioe *float64
	if ai != nil {
		exposure = ai.AutomationExposure.Ptr()
		moat = ai.HumanMoat.Ptr()
		entry = ai.EntryRisk.Ptr()
		upside = ai.AIUpside.Ptr()
		aioe = ai.AioePct.Ptr()
	}
	var band data.Band
	if aioe != nil {
		band = data.ExpBand(aioe)
	} else {
		band = data.RiskBand10(exposure)
	}
	hasHeadline := false
	headlinePct := 0
	if aioe != nil {
		hasHeadline, headlinePct = true, int(*aioe+0.5)
	} else if exposure != nil {
		hasHeadline, headlinePct = true, int(*exposure*10+0.5)
	}

	verdict := data.Tr("There is not enough evidence for a reliable conclusion yet.", CL)
	if ai != nil {
		verdict = data.Tr(ai.VerdictZh, CL)
	}
	first := func(arr []string) string {
		if len(arr) > 0 {
			return data.Tr(arr[0], CL)
		}
		return ""
	}

	vm := &JobVM{
		Ctx: ctx, DispName: dispName, Nm: nm, ShowLatin: dispName != nm,
		DataUpdated: DataUpdated, CatName: data.Tr(rep.Category, CL), CatURL: i18n.HrefIndustries(ctx.Loc, ""),
		OccCodeType: active.OccCodeType, CountriesLen: len(countries),
		HasHeadline: hasHeadline, HeadlinePct: headlinePct, BandCls: band.Cls, BandLabelTr: data.Tr(band.Label, CL),
		Verdict: verdict, Assessment: networkAssessment, MapURL: i18n.HrefMap(ctx.Loc, ""),
		Currency: cur, MigCountryName: data.CountryName(cc, CL), IsMigration: active.IsMigration,
		SourcesBody: data.SourcesBody(cc, CL),
	}
	if code := active.AnzscoCode; code != "" {
		vm.CodeLabel = code
	} else if active.OccCode != "" {
		vm.CodeLabel = active.OccCode
	} else {
		vm.CodeLabel = "—"
	}

	// meter
	if hasHeadline {
		vm.HasAioe = aioe != nil
		if aioe != nil {
			vm.MeterUnit = "/100"
			vm.AioePct = int(*aioe + 0.5)
		} else {
			vm.MeterUnit = "%"
		}
		if ai != nil {
			vm.FirstReplaced = first(ai.ReplacedZh)
			vm.FirstAugmented = first(ai.AugmentedZh)
			vm.FirstMoat = first(ai.MoatZh)
		}
	}

	// scores
	if hasHeadline {
		vm.ScoresCls = band.Cls
	}
	vm.Scores = []scoreVM{
		{data.Tr("Task exposure", CL), f1(exposure)},
		{data.Tr("Human moat", CL), f1(moat)},
		{data.Tr("Entry pressure", CL), f1(entry)},
		{data.Tr("AI upside", CL), f1(upside)},
	}

	// AI zone
	if ai != nil {
		vm.HasAI = true
		trList := func(arr []string) []string {
			out := make([]string, 0, len(arr))
			for _, x := range arr {
				out = append(out, data.Tr(x, CL))
			}
			return out
		}
		vm.AICards = []listCard{
			{data.Tr("Tasks AI will take over", CL), trList(ai.ReplacedZh)},
			{data.Tr("Tasks AI will augment", CL), trList(ai.AugmentedZh)},
			{data.Tr("Human moat (hard for AI)", CL), trList(ai.MoatZh)},
			{data.Tr("Skills to build (next 5 years)", CL), trList(ai.SkillsZh)},
		}
		if ai.EntryNarrowingZh != "" {
			vm.EntryNote = data.Tr(ai.EntryNarrowingZh, CL)
		}
		if ai.UpgradePathZh != "" {
			vm.UpgradePath = data.Tr(ai.UpgradePathZh, CL)
		}
		for _, d := range ai.Disruptors {
			lvlCls := "low"
			switch d.Level {
			case "full":
				lvlCls = "high"
			case "major":
				lvlCls = "moderate"
			}
			year := ""
			if d.Year != nil {
				year = fmt.Sprint(d.Year)
			}
			scope := ""
			if d.ScopeZh != "" {
				scope = data.Tr(d.ScopeZh, CL)
			}
			vm.Disruptors = append(vm.Disruptors, disVM{
				Name: d.Name, URL: d.URL, HasURL: d.URL != "",
				Type: data.DisType(d.Type, CL), LevelCls: lvlCls, Level: data.DisLevel(d.Level, CL),
				Year: year, Scope: scope,
			})
		}
		for _, j := range ai.Adjacent {
			name := j.NameEn
			if g := data.JobBySlug(j.Slug); g != nil {
				name = data.Name(g.Rep, CL)
			}
			vm.Adjacent = append(vm.Adjacent, adjVM{Name: name, Href: ctx.HrefJob(j.Slug)})
		}
	}

	// country tabs
	for _, o := range countries {
		vm.Tabs = append(vm.Tabs, tabVM{
			Flag: data.CountryFlag(o.Country), Name: data.CountryName(o.Country, CL),
			// 加 #region-data 锚点：切换国家后新页面直接定位到"按国家本地数据"板块，
			// 而非停在页面顶部。
			Href: i18n.HrefJob(ctx.Loc, slug, o.Country) + "#region-data", On: o.Country == cc,
		})
	}

	// active panel stats
	if active.OverallScore.Set {
		vm.OverallScore = fmt.Sprintf("%g/10", active.OverallScore.V)
	}
	if active.WorkforceSize.Set {
		vm.Workforce = data.FmtNum(active.WorkforceSize.Ptr())
	}
	if active.AvgSalary.Set {
		vm.AvgSalary = data.FmtSalary(active.AvgSalary.Ptr(), cc)
	}
	// 移民档位：full=经典逐职业块 / info=一段话 / none=不显示。
	vm.MigMode = data.MigrationTier(cc)
	// 移民徽章仅经典移民国显示（其余国家的 is_migration 多为占位默认，会误导）。
	vm.ShowMigBadge = vm.MigMode == "full"
	if vm.ShowMigBadge {
		switch active.IsMigration {
		case 1:
			vm.MigBadge = badgeVM{"low", data.Tr("Skilled migration occupation", CL)}
		case 2:
			vm.MigBadge = badgeVM{"moderate", data.MigRestrictedOccOf(cc, CL)}
		default:
			vm.MigBadge = badgeVM{"verylow", data.Tr("Not a skilled migration occupation", CL)}
		}
	}

	// radar（非经典移民国去掉 pr_friendliness / pr_difficulty 两个永居维度）
	vm.RadarSVG = RadarSVG(data.RadarLabelsFor(cc, CL),
		[]RadarSeries{{Name: nm, Color: "#2563eb", Values: data.RadarValuesFor(cc, active)}}, 10, data.Tr("rating radar", CL))

	// salary
	for _, s := range active.Salaries {
		vm.Salaries = append(vm.Salaries, salRow{
			Label: data.Tr(s.Label, CL),
			Pay:   data.Money(s.Min.Ptr(), cc) + " ~ " + data.Money(s.Max.Ptr(), cc),
			Note:  data.Tr(s.Note, CL),
		})
	}
	// education
	for _, e := range active.Education {
		cost := "—"
		if e.CostMin.Set {
			cost = data.Money(e.CostMin.Ptr(), cc) + " ~ " + data.Money(e.CostMax.Ptr(), cc)
		} else if t := data.Tr(e.CostNote, CL); t != "" {
			cost = t
		}
		dur := data.Tr(e.Duration, CL)
		if dur == "" {
			dur = "—"
		}
		vm.Education = append(vm.Education, eduRow{Stage: data.Tr(e.Stage, CL), Duration: dur, Cost: cost})
	}
	// qualifications
	for _, q := range active.Qualifications {
		iss := data.Tr(q.Issuer, CL)
		if iss == "" {
			iss = "—"
		}
		vm.Qualifications = append(vm.Qualifications, qualRow{Name: data.Tr(q.Name, CL), Issuer: iss, Mandatory: q.Mandatory})
	}
	// migration —— 分档渲染
	switch vm.MigMode {
	case "full": // 经典移民国：逐职业签证块
		if active.IsMigration == 2 {
			vm.MigNote = data.MigRestrictedNoteOf(cc, CL)
		}
		if active.IsMigration != 0 {
			for _, v := range active.Visa {
				desc := data.Tr(v.Desc, CL)
				if v.MinScore.Set {
					desc += fmt.Sprintf(" · ~%d %s (%s, %s)", int(v.MinScore.V), data.Tr("pts competitive cut-off", CL), v.ScoreAsof, data.Tr("indicative", CL))
				}
				vm.Visas = append(vm.Visas, visaRow{Subclass: v.Subclass, Name: data.Tr(v.Name, CL), Desc: desc})
			}
		} else {
			vm.NonMigVisa = data.Tr("Not a skilled migration occupation.", CL) + " " + data.NonMigVisaOf(cc, CL)
		}
	case "info": // 一段话 + 官方链接（不随职业变）
		if mi, ok := data.MigrationInfoOf(cc, CL); ok {
			vm.MigInfoBody = mi.Body
			vm.MigInfoURL = data.SafeURL(mi.URL)
			vm.MigInfoLink = mi.LinkText
		}
	}
	// case "none": 不显示移民板块

	// FAQ（2030 + active.faqs）——非经典移民国过滤掉移民/签证诱导问答
	// suitability
	if active.Suitability != nil {
		for _, x := range active.Suitability.Fit {
			vm.SuitFit = append(vm.SuitFit, data.Tr(x, CL))
		}
		for _, x := range active.Suitability.Unfit {
			vm.SuitUnfit = append(vm.SuitUnfit, data.Tr(x, CL))
		}
	}
	// outlook
	z := active.Zh()
	vm.Trend = data.Tr(z.TrendSummary, CL)
	vm.Forecast = data.Tr(z.ForecastNote, CL)
	vm.GrowthAreas = active.GrowthAreas
	vm.Outlook = buildOutlookChart(active.Outlook, ctx)
	vm.SalaryChart = buildSalaryChart(active.SalaryHistory, active.Country)
	vm.Loss = buildJobLossOcc(active, ctx)

	// FAQ（2030 + active.faqs）
	q2030, a2030 := data.Build2030(ctx.Loc, dispName, band.Cls, band.Label, aioe, exposure, moat)
	vm.FAQ = append(vm.FAQ, faqRow{Q: q2030, A: a2030, Open: true})
	for _, ff := range active.Faqs {
		// 非经典移民国：过滤掉签证/移民诱导问答（原文英文母本判定）。
		if vm.MigMode != "full" && isMigrationFAQ(ff.Question, ff.Answer) {
			continue
		}
		vm.FAQ = append(vm.FAQ, faqRow{Q: data.Tr(ff.Question, CL), A: data.Tr(ff.Answer, CL)})
	}

	// 投票组件（baked 取全球 rep 的 polls）
	vm.Poll = buildPollWidget(slug, dispName, CL, rep)

	ctx.Active = "occupations"
	ctx.Title = data.Tr("Will AI replace", CL) + " " + dispName + "? — " + data.Tr("AI risk, salary & outlook", CL) + " | AI Job Risk"
	ctx.Description = data.Tr("AI replacement risk, task exposure and the human moat for this occupation, plus local salary, licensing and outlook.", CL) + " — " + dispName
	renderPage(w, "job.html", vm)
}

// outlookChartVM 从业人数预估折线图视图模型（历史实线 + 预测虚线，JS 端可切换绝对/指数）。
type outlookChartVM struct {
	SourceLabel string        // 数据来源（专有名词，不翻译）
	IsGroup     bool          // ISCO 2位大组共享曲线（需注明非本职业单独测算）
	GrowthLabel string        // 头条增长率，如 "+5.5%"
	YearFrom    int           // 展示窗起始年
	YearTo      int           // 展示窗结束年
	DataJSON    template.JS   // {"pts":[[year,value,isProjected],...],"base":基准年}
}

// buildOutlookChart 依"过去5+未来5"目标窗裁剪序列；窗内无未来点则前扩纳入最近的未来锚点。
func buildOutlookChart(o *model.Outlook, ctx *Ctx) *outlookChartVM {
	if o == nil || len(o.Points) < 2 {
		return nil
	}
	// 基准年 = 最后一个历史点（is_projected==0）；若全为预测则取首点。
	base := int(o.Points[0][0])
	hasHist := false
	for _, p := range o.Points {
		if p[2] == 0 {
			base = int(p[0])
			hasHist = true
		}
	}
	if !hasHist {
		base = int(o.Points[0][0])
	}
	lo, hi := base-5, base+5
	var win []model.OutlookPoint
	for _, p := range o.Points {
		if y := int(p[0]); y >= lo && y <= hi {
			win = append(win, p)
		}
	}
	// 窗内无未来点但序列更远处仍有（如 US 两锚点 2024/2034）→ 前扩纳入最近的未来点。
	hasFuture := false
	for _, p := range win {
		if int(p[0]) > base {
			hasFuture = true
			break
		}
	}
	if !hasFuture {
		for _, p := range o.Points {
			if int(p[0]) > base {
				win = append(win, p)
				break
			}
		}
	}
	if len(win) < 2 {
		return nil
	}
	pts := make([][3]float64, 0, len(win))
	for _, p := range win {
		pts = append(pts, [3]float64{p[0], p[1], p[2]})
	}
	b, _ := json.Marshal(map[string]any{"pts": pts, "base": base})
	label := o.Source
	if o.Edition != "" {
		label += " " + o.Edition
	}
	vm := &outlookChartVM{
		SourceLabel: label,
		IsGroup:     o.Granularity == "group",
		YearFrom:    int(win[0][0]),
		YearTo:      int(win[len(win)-1][0]),
		DataJSON:    template.JS(b),
	}
	if o.GrowthPct != nil {
		sign := "+"
		if *o.GrowthPct < 0 {
			sign = ""
		}
		vm.GrowthLabel = fmt.Sprintf("%s%.1f%%", sign, *o.GrowthPct)
	}
	return vm
}

// salaryChartVM 历年薪资 + 5年预测折线图（历史实线 + 预测虚线；名义本币）。
type salaryChartVM struct {
	Currency    string      // ISO 币种码（用于前端 Intl 货币格式化）
	Measure     string      // median / average（英文母本，模板 .Tr）
	Period      string      // monthly
	GrowthLabel string      // 预测名义年增速，如 "+2.7%/yr"
	YearFrom    int
	YearTo      int
	DataJSON    template.JS  // {"pts":[[year,value,isProjected],...]}
}

// buildSalaryChart 历史取最近 5 年 + 预测点全保留。
func buildSalaryChart(s *model.SalaryHistory, country string) *salaryChartVM {
	if s == nil || len(s.Points) < 2 {
		return nil
	}
	var hist, proj []model.OutlookPoint
	for _, p := range s.Points {
		if p[2] == 1 {
			proj = append(proj, p)
		} else {
			hist = append(hist, p)
		}
	}
	if len(hist) > 5 { // 只保留最近 5 年历史
		hist = hist[len(hist)-5:]
	}
	win := append(hist, proj...)
	if len(win) < 2 {
		return nil
	}
	pts := make([][3]float64, 0, len(win))
	for _, p := range win {
		pts = append(pts, [3]float64{p[0], p[1], p[2]})
	}
	b, _ := json.Marshal(map[string]any{"pts": pts})
	cur := data.CURRENCY[country]
	if cur == "" {
		cur = "USD"
	}
	vm := &salaryChartVM{
		Currency: cur, Measure: s.Measure, Period: s.Period,
		YearFrom: int(win[0][0]), YearTo: int(win[len(win)-1][0]),
		DataJSON: template.JS(b),
	}
	if s.GPct != nil {
		sign := "+"
		if *s.GPct < 0 {
			sign = ""
		}
		vm.GrowthLabel = fmt.Sprintf("%s%.1f%%/yr", sign, *s.GPct)
	}
	return vm
}

// isMigrationFAQ 判定一条 FAQ 是否为签证/移民诱导问答（按英文母本关键词）。
func isMigrationFAQ(q, a string) bool {
	s := strings.ToLower(q + " " + a)
	for _, kw := range []string{"migrat", "immigra", "visa", "work permit", "permanent resid", "green card", "pr pathway", "skilled migration"} {
		if strings.Contains(s, kw) {
			return true
		}
	}
	return false
}
