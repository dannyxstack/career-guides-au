package data

import (
	"encoding/json"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"aijobrisk/internal/i18n"
)

// tmByLocale: DB locale -> (英文源串 -> 译文)。对齐 data.ts 的 TM_BY_LOCALE。
var tmByLocale = map[string]map[string]string{}

// servedLocales 由 i18n.DisplayLocales 推导：Tr() 拿到的 locale 只可能是
// i18n.ContentLocale() 的返回值（未知一律回退 en），所以只有这些内容 locale 会被查到。
func servedLocales() map[string]bool {
	m := map[string]bool{}
	for _, d := range i18n.DisplayLocales {
		m[d.Content] = true
	}
	return m
}

// loadTranslations 载入 translations-v2/{loc}.{i}.json（仅显示语言，进程内常驻）。
// 目录里其余语言——已退役的 de/pt/ko、以及从未开放为显示语言的 id/ms/th/vi/zh-Hant 等
// ——URL 不可达、Tr() 永远查不到，载入纯占内存，故跳过。
func loadTranslations() error {
	dir := filepath.Join(dataDir, "translations-v2")
	entries, err := os.ReadDir(dir)
	if err != nil {
		return err
	}
	served := servedLocales()
	skipped := map[string]bool{}
	for _, e := range entries {
		name := e.Name()
		if e.IsDir() || !strings.HasSuffix(name, ".json") {
			continue
		}
		// 文件名形如 {loc}.{i}.json，取第一段之前的 locale（loc 可能含 '-'，如 zh-CN）。
		base := strings.TrimSuffix(name, ".json")
		dot := strings.LastIndex(base, ".")
		if dot < 0 {
			continue
		}
		loc := base[:dot]
		if !served[loc] {
			skipped[loc] = true
			continue
		}
		b, err := os.ReadFile(filepath.Join(dir, name))
		if err != nil {
			return err
		}
		var shard map[string]string
		if err := json.Unmarshal(b, &shard); err != nil {
			return err
		}
		m := tmByLocale[loc]
		if m == nil {
			m = make(map[string]string, len(shard))
			tmByLocale[loc] = m
		}
		for k, v := range shard {
			m[k] = v
		}
	}
	if len(skipped) > 0 {
		locs := make([]string, 0, len(skipped))
		for l := range skipped {
			locs = append(locs, l)
		}
		sort.Strings(locs)
		log.Printf("[boot] translations: skipped %d non-display locale(s): %s",
			len(locs), strings.Join(locs, ", "))
	}
	return nil
}

// Tr 把英文母本源串译到目标 locale；缺译回退英文母本（对齐 data.ts tr()）。
func Tr(s, locale string) string {
	if s == "" {
		return ""
	}
	if locale == "en" {
		return s
	}
	if m := tmByLocale[locale]; m != nil {
		if t, ok := m[strings.TrimSpace(s)]; ok && t != "" {
			return t
		}
	}
	return s
}

// HasTr 是否存在该源串译文（英文恒真）。
func HasTr(s, locale string) bool {
	if locale == "en" {
		return true
	}
	if m := tmByLocale[locale]; m != nil {
		_, ok := m[strings.TrimSpace(s)]
		return ok
	}
	return false
}
