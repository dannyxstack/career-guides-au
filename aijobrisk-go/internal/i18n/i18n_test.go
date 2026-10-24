package i18n

import "testing"

func TestOnlyAuditedLocalesArePublicAndIndexable(t *testing.T) {
	want := map[string]bool{"en": true, "zh-Hans": true}
	got := map[string]bool{}
	for _, locale := range PublicDisplayLocales() {
		got[locale.Code] = true
		if !IsIndexable(locale.Code) {
			t.Fatalf("public locale %q is not indexable", locale.Code)
		}
	}
	if len(got) != len(want) {
		t.Fatalf("public locales = %v, want %v", got, want)
	}
	for locale := range want {
		if !got[locale] {
			t.Fatalf("missing public locale %q", locale)
		}
	}
	for _, locale := range []string{"es", "fr", "ja"} {
		if IsIndexable(locale) || !IsHidden(locale) {
			t.Fatalf("incomplete locale %q must remain hidden and noindex", locale)
		}
	}
}
