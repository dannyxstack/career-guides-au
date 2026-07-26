package data

// 精选对比配对（对齐 data.ts RAW_PAIRS），仅保留两端都存在的。
var rawPairs = [][2]string{
	{"web-developer", "software-engineer"},
	{"cook", "baker"},
	{"electrician", "plumber"},
	{"accountant-cpa-ca", "auditor"},
	{"bookkeeper", "accountant-cpa-ca"},
	{"data-analyst", "bi-analyst"},
	{"receptionist", "medical-receptionist"},
}

// ComparePairs 过滤后的精选对。
var ComparePairs [][2]string

func initComparePairs() {
	for _, p := range rawPairs {
		if JobBySlug(p[0]) != nil && JobBySlug(p[1]) != nil {
			ComparePairs = append(ComparePairs, p)
		}
	}
}

// PairKey 对比 URL 段。
func PairKey(a, b string) string { return a + "-vs-" + b }
