package data

import (
	"path/filepath"
	"sync"

	"aijobrisk/internal/model"
)

// detail 对应 occ-detail-v2/{cc}.json 里每个 id 的懒加载详情。
type detail struct {
	Visa           []model.Visa          `json:"visa"`
	Qualifications []model.Qualification `json:"qualifications"`
	Suitability    *model.Suitability    `json:"suitability"`
	Faqs           []model.FAQItem       `json:"faqs"`
	GrowthAreas    []string              `json:"growth_areas"`
	Outlook        *model.Outlook        `json:"outlook"`
	SalaryHistory  *model.SalaryHistory  `json:"salary_history"`
	AI             *model.AI             `json:"ai"`
}

var (
	detailMu    sync.Mutex
	detailCache = map[string]map[string]detail{}
)

func loadDetail(country string) map[string]detail {
	detailMu.Lock()
	defer detailMu.Unlock()
	if m, ok := detailCache[country]; ok {
		return m
	}
	m := map[string]detail{}
	// 文件可能不存在（某些国家无详情）：忽略错误，返回空表。
	_ = func() error {
		var raw map[string]detail
		if err := readJSON(filepath.Join("occ-detail-v2", country+".json"), &raw); err != nil {
			return err
		}
		m = raw
		return nil
	}()
	detailCache[country] = m
	return m
}

// OccFull 合并 lean 对象与懒加载详情（对齐 data.ts occFull）。
func OccFull(o *model.Occ) *model.Occ {
	d, ok := loadDetail(o.Country)[itoa(o.ID)]
	if !ok {
		return o
	}
	merged := *o
	merged.Visa = d.Visa
	merged.Qualifications = d.Qualifications
	merged.Suitability = d.Suitability
	merged.Faqs = d.Faqs
	merged.GrowthAreas = d.GrowthAreas
	merged.Outlook = d.Outlook
	merged.SalaryHistory = d.SalaryHistory
	if d.AI != nil {
		var ai model.AI
		if o.AI != nil {
			ai = *o.AI // 保留 lean 的分数字段
		}
		ai.EntryNarrowingZh = d.AI.EntryNarrowingZh
		ai.UpgradePathZh = d.AI.UpgradePathZh
		ai.ReplacedZh = d.AI.ReplacedZh
		ai.AugmentedZh = d.AI.AugmentedZh
		ai.MoatZh = d.AI.MoatZh
		ai.SkillsZh = d.AI.SkillsZh
		ai.Adjacent = d.AI.Adjacent
		ai.Disruptors = d.AI.Disruptors
		merged.AI = &ai
	}
	return &merged
}
