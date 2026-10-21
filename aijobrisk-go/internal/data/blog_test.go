package data

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
	"time"
)

// writeBlogFixture 在临时 data 目录里写一份 index.json（+ 每篇的正文 html）。
func writeBlogFixture(t *testing.T, dir string, posts []map[string]any) {
	t.Helper()
	bd := filepath.Join(dir, "blog")
	if err := os.MkdirAll(bd, 0o755); err != nil {
		t.Fatal(err)
	}
	b, _ := json.Marshal(map[string]any{"posts": posts, "authors": map[string]any{"editorial": map[string]any{"name": "Ed"}}})
	if err := os.WriteFile(filepath.Join(bd, "index.json"), b, 0o644); err != nil {
		t.Fatal(err)
	}
	for _, p := range posts {
		slug := p["slug"].(string)
		_ = os.WriteFile(filepath.Join(bd, slug+".html"), []byte("<p>"+slug+"</p>"), 0o644)
	}
}

// setBlogDay 把「今天」固定到某个 UTC 日期，测试结束后恢复。
func setBlogDay(t *testing.T, day string) {
	t.Helper()
	d, err := time.Parse("2006-01-02", day)
	if err != nil {
		t.Fatal(err)
	}
	prev := blogNow
	blogNow = func() time.Time { return d.Add(12 * time.Hour) }
	t.Cleanup(func() { blogNow = prev })
}

func withDataDir(t *testing.T) string {
	t.Helper()
	dir := t.TempDir()
	prev := dataDir
	dataDir = dir
	t.Cleanup(func() { dataDir = prev; blogCur.Store(nil) })
	return dir
}

func fixturePosts() []map[string]any {
	return []map[string]any{
		{"slug": "past", "title": "Past", "published_at": "2026-10-01", "tags": []string{"hiring"},
			"related_slugs": []string{"nurse"}, "related_sectors": []string{"health"}, "related_countries": []string{"AU"}},
		{"slug": "today", "title": "Today", "published_at": "2026-10-21", "tags": []string{"hiring"}},
		{"slug": "future", "title": "Future", "published_at": "2026-10-28", "tags": []string{"reskilling"},
			"related_slugs": []string{"nurse"}, "related_sectors": []string{"health"}, "related_countries": []string{"AU"}},
	}
}

func TestBlogHidesScheduledPostsUntilTheirDay(t *testing.T) {
	dir := withDataDir(t)
	writeBlogFixture(t, dir, fixturePosts())
	setBlogDay(t, "2026-10-21")
	loadBlog()

	if got := len(BlogPosts()); got != 2 {
		t.Fatalf("visible posts on 10-21 = %d, want 2 (past+today)", got)
	}
	if BlogPosts()[0].Slug != "today" {
		t.Fatalf("newest-first broken: first = %q", BlogPosts()[0].Slug)
	}
	// 未来文章不能通过任何入口泄露。
	if BlogBySlug("future") != nil {
		t.Fatal("future post reachable by slug before its day")
	}
	if len(BlogByTag("reskilling")) != 0 {
		t.Fatal("future post leaked via tag")
	}
	for _, tag := range BlogTags() {
		if tag == "reskilling" {
			t.Fatal("tag of a future-only post listed")
		}
	}
	if n := len(BlogForSlug("nurse")); n != 1 {
		t.Fatalf("related-by-occupation = %d, want 1 (future one hidden)", n)
	}
	if n := len(BlogForSector("health")) + len(BlogForCountry("AU")); n != 2 {
		t.Fatalf("related sector+country = %d, want 2", n)
	}

	st := BlogStatsNow()
	if st.Total != 3 || st.Visible != 2 || st.Scheduled != 1 || st.Next != "2026-10-28" {
		t.Fatalf("stats = %+v", st)
	}
}

func TestBlogScheduledPostAppearsOnItsDayWithoutReload(t *testing.T) {
	dir := withDataDir(t)
	writeBlogFixture(t, dir, fixturePosts())
	setBlogDay(t, "2026-10-27")
	loadBlog()
	if BlogBySlug("future") != nil {
		t.Fatal("visible a day early")
	}

	// 跨日：不重载、不重启，到日子就出现。
	setBlogDay(t, "2026-10-28")
	if BlogBySlug("future") == nil {
		t.Fatal("scheduled post did not appear on its publish day")
	}
	if BlogPosts()[0].Slug != "future" {
		t.Fatalf("newest post should be the one published today, got %q", BlogPosts()[0].Slug)
	}
	if st := BlogStatsNow(); st.Scheduled != 0 || st.Next != "" {
		t.Fatalf("stats after publish day = %+v", st)
	}
}

func TestReloadBlogPicksUpNewPosts(t *testing.T) {
	dir := withDataDir(t)
	setBlogDay(t, "2026-10-21")
	writeBlogFixture(t, dir, fixturePosts()[:1])
	loadBlog()
	if len(BlogPosts()) != 1 {
		t.Fatalf("initial visible = %d", len(BlogPosts()))
	}

	writeBlogFixture(t, dir, fixturePosts())
	st, err := ReloadBlog()
	if err != nil {
		t.Fatal(err)
	}
	if st.Total != 3 || st.Visible != 2 {
		t.Fatalf("after reload stats = %+v", st)
	}
	if p := BlogBySlug("today"); p == nil || p.Body != "<p>today</p>" {
		t.Fatalf("reloaded post missing or body not read: %+v", p)
	}
}

func TestReloadBlogKeepsPreviousOnError(t *testing.T) {
	dir := withDataDir(t)
	setBlogDay(t, "2026-10-21")
	writeBlogFixture(t, dir, fixturePosts())
	loadBlog()

	// 模拟同步途中 index.json 暂时缺失 / 写坏：线上博客不能被清空。
	if err := os.WriteFile(filepath.Join(dir, "blog", "index.json"), []byte("{not json"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := ReloadBlog(); err == nil {
		t.Fatal("expected error on corrupt index.json")
	}
	if len(BlogPosts()) != 2 {
		t.Fatalf("previous posts not kept after failed reload: %d", len(BlogPosts()))
	}
}

func TestBlogMissingIndexIsBestEffort(t *testing.T) {
	withDataDir(t) // 空目录，没有 blog/
	loadBlog()
	if BlogHas() || len(BlogTags()) != 0 || BlogBySlug("x") != nil {
		t.Fatal("missing blog dir should yield an empty, non-panicking blog")
	}
	if _, ok := BlogAuthorByID("editorial"); ok {
		t.Fatal("no authors expected")
	}
}

func TestBlogDirEnvOverridesDataDir(t *testing.T) {
	withDataDir(t) // data/blog 不存在
	mirror := t.TempDir()
	writeBlogFixture(t, mirror, fixturePosts()) // 写到 mirror/blog/
	t.Setenv("AIJOBRISK_BLOG_DIR", filepath.Join(mirror, "blog"))
	setBlogDay(t, "2026-10-21")

	if _, err := ReloadBlog(); err != nil {
		t.Fatalf("reload from AIJOBRISK_BLOG_DIR: %v", err)
	}
	if len(BlogPosts()) != 2 || BlogBySlug("today") == nil {
		t.Fatalf("posts not read from mirror dir: %d", len(BlogPosts()))
	}
}
