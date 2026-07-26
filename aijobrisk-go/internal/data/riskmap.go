package data

import (
	"fmt"
	"math"
	"sort"
	"sync"

	"aijobrisk/internal/model"
)

// —— AI Job Risk Map 布局（对齐 aijobrisk/src/lib/riskmap.ts）——
// 几何与语言无关：按分类分块 + 块内 squarified treemap（面积∝人数，颜色∝automation_exposure）。
// 方案 B：几何在首次请求时算一次并缓存（RiskLayoutFor），每请求只本地化 meta（见 web/riskmap.go）。

type RiskRect struct {
	X, Y, W, H float64
	I          int // occs 下标
}

type OccMeta struct {
	Name      string // 英文母本名（per-request 再 tr）
	Cat       string // 英文分类名
	CatSlug   string
	Slug      string
	Country   string
	Risk      float64 // automation_exposure 1..10
	Workforce float64
	Score     *float64
	AvgSalary *float64
	Currency  string
}

type CatBlock struct {
	X, Y, W, H float64
	Text       string // 英文分类名
	Count      int
}

type RiskLayout struct {
	W, H      float64
	Rects     []RiskRect
	Occs      []OccMeta
	CatBlocks []CatBlock
	Total     int
	HasData   bool
}

// RiskColor automation_exposure(1..10) -> 绿→黄→红 rgb()。
func RiskColor(v float64) string {
	t := math.Max(0, math.Min(1, (v-1)/9))
	stops := [3][3]float64{{16, 185, 129}, {245, 158, 11}, {239, 68, 68}}
	seg := 0
	lt := t / 0.5
	if t >= 0.5 {
		seg = 1
		lt = (t - 0.5) / 0.5
	}
	a, b := stops[seg], stops[seg+1]
	c := [3]int{}
	for i := 0; i < 3; i++ {
		c[i] = int(math.Round(a[i] + (b[i]-a[i])*lt))
	}
	return fmt.Sprintf("rgb(%d,%d,%d)", c[0], c[1], c[2])
}

// —— squarified treemap（Bruls et al.）——
type sqItem struct {
	value float64
	ref   int
}
type sqRect struct {
	x, y, w, h float64
	ref        int
}

func worstRatio(row []sqItem, side float64) float64 {
	sum, mn, mx := 0.0, math.Inf(1), math.Inf(-1)
	for _, r := range row {
		sum += r.value
		mn = math.Min(mn, r.value)
		mx = math.Max(mx, r.value)
	}
	s2, side2 := sum*sum, side*side
	return math.Max((side2*mx)/s2, s2/(side2*mn))
}

func squarify(data []sqItem, x, y, w, h float64) []sqRect {
	out := []sqRect{}
	total := 0.0
	for _, d := range data {
		total += d.value
	}
	if total <= 0 || w <= 0 || h <= 0 {
		return out
	}
	scale := (w * h) / total
	items := make([]sqItem, len(data))
	for i, d := range data {
		items[i] = sqItem{value: math.Max(d.value*scale, 1e-6), ref: d.ref}
	}
	rx, ry, rw, rh, i := x, y, w, h, 0
	for i < len(items) {
		row := []sqItem{items[i]}
		side := math.Min(rw, rh)
		cur := worstRatio(row, side)
		j := i + 1
		for j < len(items) {
			test := append(append([]sqItem{}, row...), items[j])
			tr := worstRatio(test, side)
			if tr <= cur {
				row, cur, j = test, tr, j+1
			} else {
				break
			}
		}
		rowSum := 0.0
		for _, r := range row {
			rowSum += r.value
		}
		if rw >= rh {
			colW := rowSum / rh
			yy := ry
			for _, it := range row {
				hh := it.value / colW
				out = append(out, sqRect{rx, yy, colW, hh, it.ref})
				yy += hh
			}
			rx += colW
			rw -= colW
		} else {
			rowH := rowSum / rw
			xx := rx
			for _, it := range row {
				ww := it.value / rowH
				out = append(out, sqRect{xx, ry, ww, rowH, it.ref})
				xx += ww
			}
			ry += rowH
			rh -= rowH
		}
		i = j
	}
	return out
}

// splitAspect 把长宽比 > cap 的矩形沿长边等分成若干 ≤cap:1 的同 ref 小块。
func splitAspect(r sqRect, cap float64) []sqRect {
	long, short := math.Max(r.w, r.h), math.Min(r.w, r.h)
	if short <= 0 || long/short <= cap+1e-6 {
		return []sqRect{r}
	}
	n := int(math.Ceil(long / (short * cap)))
	out := []sqRect{}
	if r.w >= r.h {
		cw := r.w / float64(n)
		for k := 0; k < n; k++ {
			out = append(out, sqRect{r.x + float64(k)*cw, r.y, cw, r.h, r.ref})
		}
	} else {
		ch := r.h / float64(n)
		for k := 0; k < n; k++ {
			out = append(out, sqRect{r.x, r.y + float64(k)*ch, r.w, ch, r.ref})
		}
	}
	return out
}

const (
	rmW     = 1600.0
	rmH     = 720.0
	rmOuter = 6.0
	rmGap   = 12.0
	rmLabel = 22.0
	rmPad   = 5.0
)

func metaFromOcc(o *model.Occ, workforce float64, slug string) OccMeta {
	var score, avg *float64
	if o.OverallScore.Set {
		score = o.OverallScore.Ptr()
	}
	if o.AvgSalary.Set {
		avg = o.AvgSalary.Ptr()
	}
	cur := o.Currency
	if cur == "" {
		cur = "AUD"
	}
	return OccMeta{
		Name: Name(o, "en"), Cat: o.Category, CatSlug: CatSlug(o.Category), Slug: slug,
		Country: o.Country, Risk: o.AI.AutomationExposure.V, Workforce: workforce,
		Score: score, AvgSalary: avg, Currency: cur,
	}
}

// BuildRiskMap 单国：面积∝该国从业人数。
func BuildRiskMap(cc string) RiskLayout {
	var occs []OccMeta
	for _, o := range OccByCountry(cc) {
		if !o.WorkforceSize.Set || o.WorkforceSize.V <= 0 || o.AI == nil || !o.AI.AutomationExposure.Set {
			continue
		}
		occs = append(occs, metaFromOcc(o, o.WorkforceSize.V, o.Slug))
	}
	return layoutFromOccs(occs)
}

// BuildGlobalRiskMap 全球：按 slug 跨国聚合，人数=各国之和，代表副本取 AI/分类/名称。
func BuildGlobalRiskMap() RiskLayout {
	var occs []OccMeta
	for _, slug := range JobSlugs {
		g := JobBySlug(slug)
		if g == nil || g.Rep.AI == nil || !g.Rep.AI.AutomationExposure.Set {
			continue
		}
		wf := 0.0
		for _, o := range g.Countries {
			if o.WorkforceSize.Set {
				wf += o.WorkforceSize.V
			}
		}
		if wf <= 0 {
			continue
		}
		occs = append(occs, metaFromOcc(g.Rep, wf, slug))
	}
	return layoutFromOccs(occs)
}

func layoutFromOccs(occs []OccMeta) RiskLayout {
	if len(occs) == 0 {
		return RiskLayout{W: rmW, H: rmH, Occs: occs, HasData: false}
	}
	// 按分类聚合
	byCat := map[string][]int{}
	var catOrder []string
	for i, o := range occs {
		if _, ok := byCat[o.Cat]; !ok {
			catOrder = append(catOrder, o.Cat)
		}
		byCat[o.Cat] = append(byCat[o.Cat], i)
	}
	type catAgg struct {
		cat   string
		idxs  []int
		total float64
	}
	cats := make([]catAgg, 0, len(byCat))
	for _, cat := range catOrder {
		idxs := byCat[cat]
		tot := 0.0
		for _, i := range idxs {
			tot += occs[i].Workforce
		}
		cats = append(cats, catAgg{cat, idxs, tot})
	}
	sort.SliceStable(cats, func(a, b int) bool { return cats[a].total > cats[b].total })

	catItems := make([]sqItem, len(cats))
	for i, c := range cats {
		catItems[i] = sqItem{value: c.total, ref: i}
	}
	catRects := squarify(catItems, rmOuter, rmOuter, rmW-2*rmOuter, rmH-2*rmOuter)

	var rects []RiskRect
	var catBlocks []CatBlock
	for _, cr := range catRects {
		c := cats[cr.ref]
		bx, by, bw, bh := cr.x+rmGap/2, cr.y+rmGap/2, cr.w-rmGap, cr.h-rmGap
		if bw <= 2 || bh <= 2 {
			continue
		}
		catBlocks = append(catBlocks, CatBlock{bx, by, bw, bh, c.cat, len(c.idxs)})
		ix, iy, iw, ih := bx+rmPad, by+rmLabel, bw-2*rmPad, bh-rmLabel-rmPad
		if iw <= 2 || ih <= 2 {
			continue
		}
		floorV := (c.total / float64(len(c.idxs))) * 0.3
		idxs := append([]int{}, c.idxs...)
		sort.SliceStable(idxs, func(a, b int) bool { return occs[idxs[a]].Workforce > occs[idxs[b]].Workforce })
		items := make([]sqItem, len(idxs))
		for k, i := range idxs {
			items[k] = sqItem{value: math.Max(occs[i].Workforce, floorV), ref: i}
		}
		for _, r := range squarify(items, ix, iy, iw, ih) {
			for _, s := range splitAspect(r, 2) {
				rects = append(rects, RiskRect{s.x, s.y, s.w, s.h, s.ref})
			}
		}
	}
	return RiskLayout{W: rmW, H: rmH, Rects: rects, Occs: occs, CatBlocks: catBlocks, Total: len(occs), HasData: true}
}

// —— 缓存（方案 B）：几何与语言无关，按 key 首次计算后缓存 ——
var (
	riskCache   = map[string]*RiskLayout{}
	riskCacheMu sync.Mutex
)

// RiskLayoutFor key="WORLD" 全球图；否则国家码单国图。缓存复用。
func RiskLayoutFor(key string) *RiskLayout {
	riskCacheMu.Lock()
	defer riskCacheMu.Unlock()
	if l, ok := riskCache[key]; ok {
		return l
	}
	var l RiskLayout
	if key == "WORLD" {
		l = BuildGlobalRiskMap()
	} else {
		l = BuildRiskMap(key)
	}
	riskCache[key] = &l
	return &l
}

// —— 世界/国家轮廓（outline-paths.json）——
var (
	outlinePaths map[string]string
	outlineOnce  sync.Once
)

// OutlinePath 取某 key 的轮廓 SVG path（缺失返回 ""）。
func OutlinePath(key string) string {
	outlineOnce.Do(func() {
		outlinePaths = map[string]string{}
		_ = readJSON("outline-paths.json", &outlinePaths)
	})
	return outlinePaths[key]
}
