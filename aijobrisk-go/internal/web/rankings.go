package web

import (
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"strings"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

var rkBoardIcon = map[string]string{
	"most-exposed": "fa-circle-exclamation", "least-exposed": "fa-shield-halved", "highest-paying": "fa-star",
	"largest-workforce": "fa-users", "strongest-demand": "fa-arrow-trend-up", "deepest-moat": "fa-chess-rook",
	"ai-proof-high-paying": "fa-sack-dollar",
}
var rkBoardTone = map[string]string{
	"most-exposed": "high", "least-exposed": "low", "highest-paying": "gold",
	"largest-workforce": "slate", "strongest-demand": "brand", "deepest-moat": "moat",
	"ai-proof-high-paying": "gold",
}

// rkBoardSEO 用户搜索措辞的 H1/<title>（覆盖内部术语标题，命中大白话关键词簇）。
var rkBoardSEO = map[string]string{
	"most-exposed":         "Jobs That AI Will Replace",
	"least-exposed":        "Jobs Least Likely to Be Replaced by AI",
	"deepest-moat":         "Jobs AI Can't Replace",
	"ai-proof-high-paying": "High-Paying AI-Proof Jobs",
}

// rkBoardFAQExtra 每个榜单追加的答案优先问答（问句直接命中关键词,并进 FAQPage schema）。
func rkBoardFAQExtra(board, CL string) []qaVM {
	switch board {
	case "most-exposed":
		return []qaVM{{data.Tr("What jobs are most likely to be replaced by AI?", CL),
			data.Tr("The occupations at the top of this list — where the largest share of day-to-day tasks can be automated or AI-assisted. Exposure reshapes the role and can shrink entry-level hiring; it is not a guarantee the job disappears.", CL)}}
	case "least-exposed", "deepest-moat":
		return []qaVM{{data.Tr("What jobs can AI not replace?", CL),
			data.Tr("Roles that depend on physical presence, licensed accountability, complex judgement, care and face-to-face trust — the human moat AI struggles to cross. The occupations ranked here have the lowest AI exposure or the deepest moat.", CL)}}
	case "ai-proof-high-paying":
		return []qaVM{{data.Tr("What are the highest-paying AI-proof jobs?", CL),
			data.Tr("Well-paid occupations with low generative-AI exposure — they combine strong salaries with a wide human moat, so a smaller share of their tasks is automatable. This board ranks them by average pay.", CL)}}
	}
	return nil
}

// qaToFAQ 把 []qaVM 适配成 faqPageLD 需要的 []faqRow。
func qaToFAQ(qs []qaVM) []faqRow {
	out := make([]faqRow, len(qs))
	for i, q := range qs {
		out[i] = faqRow{Q: q.Q, A: q.A}
	}
	return out
}

type rkHubItem struct{ N int; Name, Href, Primary, Secondary string }
type rkBoardCard struct {
	ID, Icon, Tone, Title, Desc, ViewHref string
	Items                                 []rkHubItem
}
type rkRow struct {
	Rank                        int
	Top1, Top2, Top3            bool
	Name, Href, Cat, CatIcon    string
	TagCls, TagLabel            string
	HasAioe                     bool
	AioeStr                     string
	AioeVal                     int
	BarColor, PctColor          string
	MoatCls, MoatLabel          string
	Metric                      string
	DataBand, DataName          string
}

// RankingsVM 榜单页（hub + board 双模式）。
type RankingsVM struct {
	*Ctx
	IsBoard     bool
	CC          string
	CountryName string
	CountryOpts []cOpt
	// hub
	Boards []rkBoardCard
	// board
	BoardTitle, BoardDesc, BoardIcon string
	ItemsLen, DistTotalNum           int
	DistTotal                        string
	PctHigh, PctMid, PctLow          int
	MetricLabel                      string
	Rows                             []rkRow
	FAQ                              []qaVM
	HrefRankingsCC                   string
	DataUpdated                      string
	// 分页
	Page, TotalPages         int
	HasPrev, HasNext         bool
	PrevHref, NextHref       string
	RangeFrom, RangeTo       int
	PageLinks                []rkPageLink
}

type rkPageLink struct {
	Num  int
	Href string
	On   bool
	Gap  bool // 省略号占位
}

func rkTag(aioe *float64, CL string) (cls, label string) {
	b := data.ExpBand(aioe)
	switch b.Cls {
	case "critical", "high":
		return "high", data.Tr(b.Label, CL)
	case "moderate":
		return "mid", data.Tr("moderate", CL)
	default:
		return "low", data.Tr(b.Label, CL)
	}
}
func rkBarColor(aioe *float64) string {
	if aioe == nil {
		return "#cbd5e1"
	}
	if *aioe >= 70 {
		return "linear-gradient(90deg,#f59e0b,#dc2626)"
	}
	if *aioe >= 40 {
		return "#f59e0b"
	}
	return "#059669"
}
func rkPctColor(aioe *float64) string {
	if aioe == nil {
		return "var(--text-muted)"
	}
	if *aioe >= 70 {
		return "var(--risk-high)"
	}
	if *aioe >= 40 {
		return "var(--risk-mid-fg)"
	}
	return "var(--risk-low)"
}
func rkMoat(v *float64, CL string) (cls, label string) {
	if v == nil {
		return "moderate", data.Tr("n/a", CL)
	}
	if *v >= 7 {
		return "strong", data.Tr("Strong", CL)
	}
	if *v >= 4 {
		return "moderate", data.Tr("Moderate", CL)
	}
	return "weak", data.Tr("Weak", CL)
}

// Rankings /rankings[/{board}][/{cc}] 或 /rankings/{cc}。segs = /rankings 之后的段。
func Rankings(w http.ResponseWriter, ctx *Ctx, segs []string) {
	CL := ctx.CL
	inCountries := func(s string) bool {
		for _, c := range data.COUNTRIES {
			if c == s {
				return true
			}
		}
		return false
	}
	board, cc := "", "US"
	switch {
	case len(segs) == 0:
	case rkBoardIcon[segs[0]] != "":
		board = segs[0]
		if len(segs) > 1 {
			if inCountries(segs[1]) {
				cc = segs[1]
			} else {
				notFound(w, ctx)
				return
			}
		}
	case len(segs) == 1 && inCountries(segs[0]):
		cc = segs[0]
	default:
		notFound(w, ctx)
		return
	}
	isBoard := board != ""

	vm := &RankingsVM{Ctx: ctx, IsBoard: isBoard, CC: cc, CountryName: data.CountryName(cc, CL),
		HrefRankingsCC: i18n.HrefRankings(ctx.Loc, cc), DataUpdated: DataUpdated}
	countryURL := func(c string) string {
		if isBoard {
			return i18n.HrefBoard(ctx.Loc, board, c)
		}
		return i18n.HrefRankings(ctx.Loc, c)
	}
	for _, c := range data.COUNTRIES {
		vm.CountryOpts = append(vm.CountryOpts, cOpt{Code: c, Name: data.CountryName(c, CL), Href: countryURL(c), On: c == cc})
	}
	ctx.Active = "rankings"

	if !isBoard {
		boards := data.BuildBoards(cc, 5, CL)
		for i := range boards {
			b := &boards[i]
			card := rkBoardCard{ID: b.ID, Icon: rkBoardIcon[b.ID], Tone: rkBoardTone[b.ID],
				Title: b.Title, Desc: b.Desc, ViewHref: i18n.HrefBoard(ctx.Loc, b.ID, cc)}
			for j, it := range b.Items {
				card.Items = append(card.Items, rkHubItem{
					N: j + 1, Name: it.Name, Href: ctx.HrefJob(it.Slug),
					Primary: rkPrimary(b, it, cc), Secondary: rkSecondary(b, it, cc, CL),
				})
			}
			vm.Boards = append(vm.Boards, card)
		}
		ctx.Title = data.Tr("Job risk & opportunity rankings", CL) + " | AI Job Risk"
		ctx.Description = data.Tr("How exposed is your job to generative AI? Compare salary, workforce, demand and human resilience across occupations.", CL) + " · " + vm.CountryName
		renderPage(w, "rankings.html", vm)
		return
	}

	// board 模式（全量取回后分页，每页 50）
	const pageSize = 50
	b := data.BoardByID(cc, board, 1<<30, CL)
	if b == nil {
		notFound(w, ctx)
		return
	}
	allItems := b.Items
	totalItems := len(allItems)
	totalPages := (totalItems + pageSize - 1) / pageSize
	if totalPages < 1 {
		totalPages = 1
	}
	page := 1
	if q, err := url.ParseQuery(strings.TrimPrefix(ctx.Query, "?")); err == nil {
		if p, e := strconv.Atoi(q.Get("page")); e == nil && p > 1 {
			page = p
		}
	}
	if page > totalPages {
		page = totalPages
	}
	offset := (page - 1) * pageSize
	end := offset + pageSize
	if end > totalItems {
		end = totalItems
	}
	b.Items = allItems[offset:end]
	// 分布统计
	high, mid, low, total := 0, 0, 0, 0
	for _, o := range data.OccByCountry(cc) {
		if o.AI == nil || !o.AI.AioePct.Set {
			continue
		}
		total++
		p := o.AI.AioePct.V
		if p >= 70 {
			high++
		} else if p >= 40 {
			mid++
		} else {
			low++
		}
	}
	pctOf := func(n int) int {
		if total == 0 {
			return 0
		}
		return int(float64(n)/float64(total)*100 + 0.5)
	}
	vm.DistTotalNum = total
	vm.DistTotal = data.FmtNum(f64(total))
	vm.PctHigh, vm.PctMid, vm.PctLow = pctOf(high), pctOf(mid), pctOf(low)
	vm.BoardTitle, vm.BoardDesc = b.Title, b.Desc
	vm.BoardIcon = rkBoardIcon[board]
	if vm.BoardIcon == "" {
		vm.BoardIcon = "fa-list-ol"
	}
	vm.ItemsLen = totalItems

	// metric 列
	switch b.Metric {
	case "workforce":
		vm.MetricLabel = data.Tr("Workforce", CL)
	case "demand":
		vm.MetricLabel = data.Tr("Demand", CL)
	default:
		vm.MetricLabel = data.Tr("Avg salary", CL)
	}
	for i, it := range b.Items {
		tagCls, tagLabel := rkTag(it.Aioe, CL)
		moatCls, moatLabel := rkMoat(it.Moat, CL)
		rank := offset + i + 1
		var metric string
		switch b.Metric {
		case "workforce":
			metric = data.FmtNum(it.Workforce)
		case "demand":
			if it.Demand != nil {
				metric = fmt.Sprintf("%g/10", *it.Demand)
			} else {
				metric = "—"
			}
		default:
			metric = data.FmtSalary(it.Salary, cc)
		}
		row := rkRow{
			Rank: rank, Top1: rank == 1, Top2: rank == 2, Top3: rank == 3,
			Name: it.Name, Href: ctx.HrefJob(it.Slug), Cat: data.Tr(it.Cat, CL), CatIcon: data.CategoryIcon(it.Cat),
			TagCls: tagCls, TagLabel: tagLabel, BarColor: rkBarColor(it.Aioe), PctColor: rkPctColor(it.Aioe),
			MoatCls: moatCls, MoatLabel: moatLabel, Metric: metric, DataBand: tagCls,
		}
		if it.Aioe != nil {
			row.HasAioe = true
			row.AioeStr = fmt.Sprintf("%d", int(*it.Aioe+0.5))
			row.AioeVal = int(*it.Aioe + 0.5)
		} else {
			row.AioeStr = "—"
		}
		row.DataName = lower(it.Name)
		vm.Rows = append(vm.Rows, row)
	}
	// 分页控件
	boardBase := i18n.HrefBoard(ctx.Loc, board, cc)
	pageHref := func(n int) string {
		if n <= 1 {
			return boardBase
		}
		return boardBase + "?page=" + strconv.Itoa(n)
	}
	vm.Page, vm.TotalPages = page, totalPages
	vm.RangeFrom, vm.RangeTo = offset+1, end
	if totalItems == 0 {
		vm.RangeFrom = 0
	}
	vm.HasPrev, vm.HasNext = page > 1, page < totalPages
	vm.PrevHref, vm.NextHref = pageHref(page-1), pageHref(page+1)
	if totalPages > 1 {
		add := func(n int) { vm.PageLinks = append(vm.PageLinks, rkPageLink{Num: n, Href: pageHref(n), On: n == page}) }
		gap := func() { vm.PageLinks = append(vm.PageLinks, rkPageLink{Gap: true}) }
		lo, hi := page-2, page+2
		if lo < 1 {
			lo = 1
		}
		if hi > totalPages {
			hi = totalPages
		}
		if lo > 1 {
			add(1)
			if lo > 2 {
				gap()
			}
		}
		for n := lo; n <= hi; n++ {
			add(n)
		}
		if hi < totalPages {
			if hi < totalPages-1 {
				gap()
			}
			add(totalPages)
		}
	}

	vm.FAQ = rkBoardFAQExtra(board, CL)
	vm.FAQ = append(vm.FAQ, []qaVM{
		{data.Tr("How is the AI exposure percentile calculated?", CL), data.Tr(`It comes from two open studies — the ILO Working Paper 140 and Eloundou et al. "GPTs are GPTs" (OpenAI) — mapped onto official occupation classifications. It is a percentile (0–100): higher means more exposed to generative AI.`, CL)},
		{data.Tr("Does high exposure mean the job disappears?", CL), data.Tr("No. High exposure means a larger share of the tasks can be done or assisted by AI — the task mix is reshaped, entry-level roles may shrink, and AI-fluent workers gain leverage. It is not a prediction of unemployment.", CL)},
		{data.Tr("What is the human moat?", CL), data.Tr("The capabilities AI struggles to replace: complex judgement, on-site work, licensed accountability, empathy and care, and face-to-face trust. A deeper moat makes an occupation more resilient.", CL)},
		{data.Tr("How is this ranking produced?", CL), data.Tr("Rankings are computed automatically by transparent rules from official labour statistics and the exposure scores — not hand-picked. Figures are estimates, updated periodically, and indicative only.", CL)},
	}...)

	// SEO：用搜索措辞覆盖 H1/<title>（命中 “jobs AI will replace / can't replace / AI-proof” 等大词）。
	headline := b.Title
	if h := rkBoardSEO[board]; h != "" {
		headline = data.Tr(h, CL)
		vm.BoardTitle = headline
	}
	ctx.Title = headline + " — " + vm.CountryName + " (2026) | AI Job Risk"
	ctx.Description = headline + " · " + b.Desc + " · " + vm.CountryName + ". " +
		data.Tr("Ranked by generative-AI exposure from ILO research; figures are indicative estimates.", CL)
	// 结构化数据：FAQPage（问句命中关键词）+ 面包屑。
	ctx.JSONLD = jsonLD(faqPageLD(qaToFAQ(vm.FAQ)), breadcrumbLD(ctx, cc, headline))
	renderPage(w, "rankings.html", vm)
}

func rkPrimary(b *data.Board, it data.RankItem, cc string) string {
	switch b.Metric {
	case "salary":
		return data.FmtSalary(it.Salary, cc)
	case "workforce":
		return data.FmtNum(it.Workforce)
	case "demand":
		if it.Demand != nil {
			return fmt.Sprintf("%g/10", *it.Demand)
		}
		return "—"
	case "moat":
		if it.Moat != nil {
			return fmt.Sprintf("%g/10", *it.Moat)
		}
		return "—"
	default:
		if it.Aioe != nil {
			return fmt.Sprintf("%d", int(*it.Aioe+0.5))
		}
		return "—"
	}
}
func rkSecondary(b *data.Board, it data.RankItem, cc, CL string) string {
	if b.Metric == "aioe" {
		return data.FmtSalary(it.Salary, cc)
	}
	if it.Aioe != nil {
		return data.Tr("exposure", CL) + " " + fmt.Sprintf("%d", int(*it.Aioe+0.5))
	}
	return ""
}

func f64(n int) *float64 { v := float64(n); return &v }
func lower(s string) string {
	b := []rune(s)
	for i, c := range b {
		if c >= 'A' && c <= 'Z' {
			b[i] = c + 32
		}
	}
	return string(b)
}
