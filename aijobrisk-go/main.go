// aijobrisk Go SSR 服务：进程内加载数据，SSR 渲染 HTML，语言前缀路由。
// 架构对齐 aijobrisk/（Astro SSR），运行时更省内存。
package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"aijobrisk/internal/data"
	"aijobrisk/internal/polls"
	"aijobrisk/internal/pollsapi"
	"aijobrisk/internal/web"
)

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

func main() {
	dataDir := env("AIJOBRISK_DATA", "data")
	tmplDir := env("AIJOBRISK_TEMPLATES", "templates")
	staticDir := env("AIJOBRISK_STATIC", "static")
	site := env("AIJOBRISK_SITE", "https://aijobrisk.com")
	host := env("HOST", "127.0.0.1")
	port := env("PORT", "4332")

	t0 := time.Now()
	log.Printf("[boot] loading data from %s …", dataDir)
	if err := data.Load(dataDir); err != nil {
		log.Fatalf("load data: %v", err)
	}
	if err := polls.Load(dataDir); err != nil {
		log.Printf("[boot] polls disabled: %v", err)
	}
	if err := web.InitTemplates(tmplDir); err != nil {
		log.Fatalf("init templates: %v", err)
	}
	// 投票 API 与主站同端口同源（DB 懒连接：MySQL 挂了只影响投票，页面照常）。
	pollsapi.LoadDotEnv()
	pollsapi.ConfigureFromEnv()
	log.Printf("[boot] loaded %d occupations, %d job slugs in %s", len(data.Occupations), len(data.JobSlugs), time.Since(t0).Round(time.Millisecond))

	mux := http.NewServeMux()

	// 静态资源
	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir(staticDir))))
	mux.HandleFunc("/logo.svg", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, staticDir+"/logo.svg")
	})

	// sitemap / robots
	web.RegisterSitemap(mux, site)

	// 投票 API（同源 /api/*）
	pollsapi.Register(mux)

	// 页面（catch-all，内部剥语言前缀后分发）
	mux.Handle("/", web.Router(site))

	addr := host + ":" + port
	log.Printf("[serve] aijobrisk-go on http://%s (site=%s)", addr, site)
	srv := &http.Server{Addr: addr, Handler: mux, ReadHeaderTimeout: 10 * time.Second}
	log.Fatal(srv.ListenAndServe())
}
