package web

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"aijobrisk/internal/data"
	"aijobrisk/internal/model"
)

func TestResolveCCRejectsUnknownCountry(t *testing.T) {
	for _, tc := range []struct {
		in, want string
		ok       bool
	}{
		{"", "US", true},
		{"AU", "AU", true},
		{"ZZ", "", false},
		{"not-a-country", "", false},
	} {
		got, ok := resolveCC(tc.in)
		if got != tc.want || ok != tc.ok {
			t.Fatalf("resolveCC(%q) = (%q, %v), want (%q, %v)", tc.in, got, ok, tc.want, tc.ok)
		}
	}
}

func TestResolveJobCountryRejectsMissingCombination(t *testing.T) {
	us := &model.Occ{Country: "US"}
	au := &model.Occ{Country: "AU"}
	countries := []*model.Occ{us, au}

	if got, ok := resolveJobCountry(countries, ""); !ok || got != us {
		t.Fatalf("global page = (%v, %v), want first country", got, ok)
	}
	if got, ok := resolveJobCountry(countries, "AU"); !ok || got != au {
		t.Fatalf("AU page = (%v, %v), want AU", got, ok)
	}
	if got, ok := resolveJobCountry(countries, "ZZ"); ok || got != nil {
		t.Fatalf("unknown country = (%v, %v), want (nil, false)", got, ok)
	}
}

func TestSitemapPriorityJobUsesAggregateWorkforce(t *testing.T) {
	below := &data.JobGroup{Countries: []*model.Occ{
		{WorkforceSize: model.Num{Set: true, V: 4_000}},
		{WorkforceSize: model.Num{Set: true, V: 5_999}},
	}}
	atThreshold := &data.JobGroup{Countries: []*model.Occ{
		{WorkforceSize: model.Num{Set: true, V: 4_000}},
		{WorkforceSize: model.Num{Set: true, V: 6_000}},
	}}
	if sitemapPriorityJob(nil) || sitemapPriorityJob(below) || !sitemapPriorityJob(atThreshold) {
		t.Fatal("sitemap workforce threshold is not enforced")
	}
}

func TestSitemapUsesCanonicalURLsOnly(t *testing.T) {
	xml := buildURLSet([]sitemapURL{{"/", "2026-10-01"}, {"/jobs/example", ""}}, "https://aijobrisk.com")
	for _, forbidden := range []string{"xhtml:", "hreflang", "rel=\"alternate\""} {
		if strings.Contains(xml, forbidden) {
			t.Fatalf("sitemap unexpectedly contains %q", forbidden)
		}
	}
	if strings.Count(xml, "<loc>") != 2 {
		t.Fatalf("got %d loc entries, want 2", strings.Count(xml, "<loc>"))
	}
	if strings.Count(xml, "<lastmod>") != 1 {
		t.Fatalf("got %d lastmod entries, want only the verified one", strings.Count(xml, "<lastmod>"))
	}
	for _, child := range sitemapChildren() {
		if child.Path == "/sitemap-jobs-country.xml" {
			t.Fatal("bulk country-job sitemap must not be submitted")
		}
	}
}

func TestSitemapIndexUsesNewestChildContentDate(t *testing.T) {
	urls := []sitemapURL{{"/old", "2026-09-09"}, {"/unknown", ""}, {"/new", "2026-11-01"}}
	if got := latestURLUpdate(urls); got != "2026-11-01" {
		t.Fatalf("latestURLUpdate = %q, want 2026-11-01", got)
	}
}

func TestPermanentRedirectUsesProvidedCanonicalPath(t *testing.T) {
	w := httptest.NewRecorder()
	permanentRedirect(w, "/rankings?ref=test")
	if w.Code != http.StatusMovedPermanently || w.Header().Get("Location") != "/rankings?ref=test" {
		t.Fatalf("redirect = (%d, %q), want (301, /rankings?ref=test)", w.Code, w.Header().Get("Location"))
	}
}

func TestCacheControlPolicies(t *testing.T) {
	h := WithCacheControl(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	}), StaticCacheControl)
	w := httptest.NewRecorder()
	h.ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/static/app.css", nil))
	if got := w.Header().Get("Cache-Control"); got != StaticCacheControl {
		t.Fatalf("static Cache-Control = %q, want %q", got, StaticCacheControl)
	}
}

func TestCountryRiskMapLinksToCountryJobPage(t *testing.T) {
	layout := &data.RiskLayout{Occs: []data.OccMeta{{Slug: "accountant-cpa-ca", Risk: 5}}}
	if got := riskMeta(layout, "en", "en", "AU")[0].U; got != "/jobs/accountant-cpa-ca/AU" {
		t.Fatalf("country map job link = %q, want country-specific URL", got)
	}
	if got := riskMeta(layout, "en", "en", "")[0].U; got != "/jobs/accountant-cpa-ca" {
		t.Fatalf("global map job link = %q, want global URL", got)
	}
}
