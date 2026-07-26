package web

import (
	"fmt"
	"net/http"

	"aijobrisk/internal/data"
	"aijobrisk/internal/i18n"
)

var rkBoardIcon = map[string]string{
	"most-exposed": "fa-circle-exclamation", "least-exposed": "fa-shield-halved", "highest-paying": "fa-star",
	"largest-workforce": "fa-users", "strongest-demand": "fa-arrow-trend-up", "deepest-moat": "fa-chess-rook",
}
var rkBoardTone = map[string]string{
	"most-exposed": "high", "least-exposed": "low", "highest-paying": "gold",
	"largest-workforce": "slate", "strongest-demand": "brand", "deepest-moat": "moat",
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

	// board 模式
	b := data.BoardByID(cc, board, 50, CL)
	if b == nil {
		notFound(w, ctx)
		return
	}
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
	vm.ItemsLen = len(b.Items)

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
		rank := i + 1
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
	vm.FAQ = []qaVM{
		{data.Tr("How is the AI exposure percentile calculated?", CL), data.Tr(`It comes from two open studies — the ILO Working Paper 140 and Eloundou et al. "GPTs are GPTs" (OpenAI) — mapped onto official occupation classifications. It is a percentile (0–100): higher means more exposed to generative AI.`, CL)},
		{data.Tr("Does high exposure mean the job disappears?", CL), data.Tr("No. High exposure means a larger share of the tasks can be done or assisted by AI — the task mix is reshaped, entry-level roles may shrink, and AI-fluent workers gain leverage. It is not a prediction of unemployment.", CL)},
		{data.Tr("What is the human moat?", CL), data.Tr("The capabilities AI struggles to replace: complex judgement, on-site work, licensed accountability, empathy and care, and face-to-face trust. A deeper moat makes an occupation more resilient.", CL)},
		{data.Tr("How is this ranking produced?", CL), data.Tr("Rankings are computed automatically by transparent rules from official labour statistics and the exposure scores — not hand-picked. Figures are estimates, updated periodically, and indicative only.", CL)},
	}
	ctx.Title = b.Title + " — " + data.Tr("full ranking", CL) + " (" + vm.CountryName + ") | AI Job Risk"
	ctx.Description = b.Title + ": " + b.Desc + " · " + vm.CountryName
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
