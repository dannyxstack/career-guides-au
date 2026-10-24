package web

import (
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
	xml := buildUrlset([]string{"/", "/jobs/example"}, "https://aijobrisk.com")
	for _, forbidden := range []string{"xhtml:", "hreflang", "rel=\"alternate\""} {
		if strings.Contains(xml, forbidden) {
			t.Fatalf("sitemap unexpectedly contains %q", forbidden)
		}
	}
	if strings.Count(xml, "<loc>") != 2 {
		t.Fatalf("got %d loc entries, want 2", strings.Count(xml, "<loc>"))
	}
	for _, child := range sitemapChildren {
		if child == "/sitemap-jobs-country.xml" {
			t.Fatal("bulk country-job sitemap must not be submitted")
		}
	}
}
