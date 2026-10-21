package web

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

const testToken = "0123456789abcdef0123456789abcdef" // 32 chars

func reloadReq(method, token, remote string, hdr map[string]string) *httptest.ResponseRecorder {
	r := httptest.NewRequest(method, "/internal/reload-blog", nil)
	r.RemoteAddr = remote
	if token != "" {
		r.Header.Set("X-Reload-Token", token)
	}
	for k, v := range hdr {
		r.Header.Set(k, v)
	}
	w := httptest.NewRecorder()
	ReloadBlogHandler(w, r)
	return w
}

func TestReloadEndpointRejectsEverythingUnauthorised(t *testing.T) {
	cases := []struct {
		name, env, method, token, remote string
		hdr                              map[string]string
	}{
		{"feature off (no env)", "", "POST", testToken, "127.0.0.1:5000", nil},
		{"token too short", "short-token", "POST", "short-token", "127.0.0.1:5000", nil},
		{"GET not allowed", testToken, "GET", testToken, "127.0.0.1:5000", nil},
		{"wrong token", testToken, "POST", strings.Repeat("x", 32), "127.0.0.1:5000", nil},
		{"missing token", testToken, "POST", "", "127.0.0.1:5000", nil},
		{"via nginx (XFF)", testToken, "POST", testToken, "127.0.0.1:5000", map[string]string{"X-Forwarded-For": "203.0.113.9"}},
		{"via nginx (X-Real-IP)", testToken, "POST", testToken, "127.0.0.1:5000", map[string]string{"X-Real-IP": "203.0.113.9"}},
		{"via Cloudflare", testToken, "POST", testToken, "127.0.0.1:5000", map[string]string{"CF-Connecting-IP": "203.0.113.9"}},
		{"non-loopback peer", testToken, "POST", testToken, "203.0.113.9:5000", nil},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			t.Setenv("AIJOBRISK_RELOAD_TOKEN", c.env)
			if w := reloadReq(c.method, c.token, c.remote, c.hdr); w.Code != http.StatusNotFound {
				t.Fatalf("got %d, want 404 (endpoint must not reveal itself)", w.Code)
			}
		})
	}
}

func TestReloadEndpointAcceptsLocalAuthorisedPost(t *testing.T) {
	t.Setenv("AIJOBRISK_RELOAD_TOKEN", testToken)
	for _, remote := range []string{"127.0.0.1:5000", "[::1]:5000"} {
		w := reloadReq("POST", testToken, remote, nil)
		// 测试环境没有 data/blog，重载本身会失败（500）；这里只验证鉴权放行了，不是 404。
		if w.Code == http.StatusNotFound {
			t.Fatalf("authorised local POST from %s was rejected", remote)
		}
		if ct := w.Header().Get("Content-Type"); ct != "application/json" {
			t.Fatalf("content-type = %q", ct)
		}
	}
}

func TestNoListingHidesDirectoryButServesFiles(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "future-post.svg"), []byte("<svg/>"), 0o644); err != nil {
		t.Fatal(err)
	}
	h := http.StripPrefix("/static/blog/", NoListing(http.FileServer(http.Dir(dir))))
	get := func(path string) int {
		w := httptest.NewRecorder()
		h.ServeHTTP(w, httptest.NewRequest("GET", path, nil))
		return w.Code
	}
	if c := get("/static/blog/"); c != http.StatusNotFound {
		t.Fatalf("directory listing returned %d, want 404 (would leak scheduled slugs)", c)
	}
	if c := get("/static/blog/future-post.svg"); c != http.StatusOK {
		t.Fatalf("file returned %d, want 200", c)
	}
}
