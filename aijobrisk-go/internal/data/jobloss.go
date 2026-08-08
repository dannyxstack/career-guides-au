package data

import "aijobrisk/internal/model"

// AI job loss by 2030 —— A1 情景带模型（与 job-treemap/build.py 同口径）。
//
//	职业流失率 = aioe_score × 自动化占比 × 情景系数 r（低/中/高）
//	自动化占比 = automation_exposure /(automation_exposure + ai_upside)
//	r 全站标定：中档使合计流失 ≈ LossMidTarget（锚 Goldman ~2.5% 美 / WEF 9200 万全球 ≈ 2.7%）。
//
// 绝非单一预言，仅作情景估算。CalibrateLoss 须在 Load 时（Occupations 就绪后）调用一次。
const (
	LossMidTarget = 0.03 // 标定旋钮：中档≈覆盖工作人口的 3%
	lossCap       = 0.9  // 单职业流失率上限 90%
)

var lossSpread = map[string]float64{"low": 0.5, "mid": 1.0, "high": 2.2}
var lossRates = map[string]float64{"low": 0, "mid": 0, "high": 0}

// Loss 单职业 2030 流失估算。
type Loss struct {
	Jobs                          int
	RateLow, RateMid, RateHigh    float64
	CountLow, CountMid, CountHigh int
}

func lossBaseFrac(o *model.Occ) (float64, bool) {
	if o == nil || o.AI == nil || !o.AI.AioeScore.Set {
		return 0, false
	}
	sc := o.AI.AioeScore.V
	ae, up := o.AI.AutomationExposure.V, o.AI.AIUpside.V
	auto := 0.0
	if ae+up > 0 {
		auto = ae / (ae + up)
	}
	return sc * auto, true
}

// CalibrateLoss 标定情景系数，使中档全站合计流失 ≈ LossMidTarget。
func CalibrateLoss(occs []*model.Occ) {
	var totWf, totW float64
	for _, o := range occs {
		wf := float64(o.WorkforceSize.Int())
		bf, ok := lossBaseFrac(o)
		if !ok || wf <= 0 {
			continue
		}
		totWf += wf
		totW += wf * bf
	}
	base, mid := 0.0, 0.0
	if totWf > 0 {
		base = totW / totWf
	}
	if base > 0 {
		mid = LossMidTarget / base
	}
	for k, m := range lossSpread {
		lossRates[k] = mid * m
	}
}

// OccLoss 单职业流失估算（须先 CalibrateLoss）。无暴露返回 nil。
func OccLoss(o *model.Occ) *Loss {
	bf, ok := lossBaseFrac(o)
	if !ok {
		return nil
	}
	wf := o.WorkforceSize.Int()
	clamp := func(r float64) float64 {
		if r > lossCap {
			return lossCap
		}
		return r
	}
	rl, rm, rh := clamp(bf*lossRates["low"]), clamp(bf*lossRates["mid"]), clamp(bf*lossRates["high"])
	return &Loss{
		Jobs:      wf,
		RateLow:   rl,
		RateMid:   rm,
		RateHigh:  rh,
		CountLow:  int(float64(wf)*rl + 0.5),
		CountMid:  int(float64(wf)*rm + 0.5),
		CountHigh: int(float64(wf)*rh + 0.5),
	}
}

// LossAgg 某国/全局合计流失。
type LossAgg struct {
	Jobs                          int
	CountLow, CountMid, CountHigh int
	RateLow, RateMid, RateHigh    float64
}

// AggregateLoss 汇总一组职业的流失（人数 + 占比）。
func AggregateLoss(occs []*model.Occ) LossAgg {
	var a LossAgg
	for _, o := range occs {
		a.Jobs += o.WorkforceSize.Int()
		if l := OccLoss(o); l != nil {
			a.CountLow += l.CountLow
			a.CountMid += l.CountMid
			a.CountHigh += l.CountHigh
		}
	}
	if a.Jobs > 0 {
		a.RateLow = float64(a.CountLow) / float64(a.Jobs)
		a.RateMid = float64(a.CountMid) / float64(a.Jobs)
		a.RateHigh = float64(a.CountHigh) / float64(a.Jobs)
	}
	return a
}
