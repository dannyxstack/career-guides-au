package web

import (
	"encoding/json"
	"html/template"
	"os"

	"aijobrisk/internal/data"
	"aijobrisk/internal/model"
	"aijobrisk/internal/polls"
)

type pollOptVM struct{ Key, Label string }
type pollVM struct {
	Code, Type, Q string
	HasAvg        bool
	SsrConcl      string
	Options       []pollOptVM
}

// PollWidget 投票组件数据（附在 JobVM 上）。
type PollWidget struct {
	Has        bool
	APIBase    string
	Slug       string
	Labels     map[string]string
	Polls      []pollVM
	BakedJSON  template.JS
	ConclTpls  template.JS
	LabelsJSON template.JS
}

func pollAPIBase() string {
	if v := os.Getenv("PUBLIC_POLLS_API"); v != "" {
		return v // 跨域部署时可指向独立 API 子域
	}
	return "/api" // 默认同源（投票 API 与主站同端口）
}

// buildPollWidget 服务端预备投票组件（对齐 PollBlock.astro）。
func buildPollWidget(slug, name, CL string, rep *model.Occ) PollWidget {
	if len(polls.Polls) == 0 {
		return PollWidget{}
	}
	baked := rep.Polls
	if baked == nil {
		baked = map[string]model.BakedPoll{}
	}
	labels := map[string]string{
		"title": data.Tr("What the community thinks", CL), "hint": data.Tr("Tap an option to vote (change anytime)", CL),
		"votes": data.Tr("votes", CL), "avg": data.Tr("Community avg", CL),
		"thanks": data.Tr("Thanks for voting!", CL), "you": data.Tr("Your pick", CL),
	}

	conclTpls := map[string]string{}
	var pvs []pollVM
	for _, p := range polls.Polls {
		conclTpl := polls.FillTpl(polls.LocText(p.Conclusion, CL), map[string]string{"name": name}, nil)
		conclTpls[p.Code] = conclTpl

		ssr := ""
		if bk, ok := baked[p.Code]; ok && bk.Total > 0 {
			vars := map[string]string{"name": name, "n": itoaInt(bk.Total)}
			if avg := polls.AvgFromCounts(p, bk.Counts); avg != nil {
				vars["avg"] = itoaInt(*avg)
			}
			ssr = polls.FillTpl(conclTpl, vars, polls.PctOf(bk.Counts))
		}

		hasAvg := true
		for _, o := range p.Options {
			if o.Mid == nil {
				hasAvg = false
				break
			}
		}
		var opts []pollOptVM
		for _, o := range p.Options {
			opts = append(opts, pollOptVM{Key: o.Key, Label: polls.LocText(o.Label, CL)})
		}
		pvs = append(pvs, pollVM{
			Code: p.Code, Type: p.Type, Q: polls.FillTpl(polls.LocText(p.Q, CL), map[string]string{"name": name}, nil),
			HasAvg: hasAvg, SsrConcl: ssr, Options: opts,
		})
	}

	return PollWidget{
		Has: true, APIBase: pollAPIBase(), Slug: slug, Labels: labels, Polls: pvs,
		BakedJSON: jsonJS(baked), ConclTpls: jsonJS(conclTpls), LabelsJSON: jsonJS(labels),
	}
}

func itoaInt(n int) string {
	b, _ := json.Marshal(n)
	return string(b)
}
