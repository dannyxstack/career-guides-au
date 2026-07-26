package data

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
)

// tmByLocale: DB locale -> (英文源串 -> 译文)。对齐 data.ts 的 TM_BY_LOCALE。
var tmByLocale = map[string]map[string]string{}

// loadTranslations 载入 translations-v2/{loc}.{i}.json 全部分片（进程内常驻）。
func loadTranslations() error {
	dir := filepath.Join(dataDir, "translations-v2")
	entries, err := os.ReadDir(dir)
	if err != nil {
		return err
	}
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
