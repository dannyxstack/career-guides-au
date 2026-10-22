// aijobrisk Go SSR 服务：进程内加载数据，SSR 渲染 HTML，语言前缀路由。
// 架构对齐 aijobrisk/（Astro SSR），运行时更省内存。
package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"aijobrisk/internal/data"
	"aijobrisk/internal/newsletter"
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
	newsletter.Configure()
	// AIJOBRISK_BLOG_DIR 可能只写在 .env 里，而上面 data.Load 时 .env 还没读——这里补一次。
	// 不把 LoadDotEnv 整体前移：线上 .env 里可能留着旧的 AIJOBRISK_DATA 等路径，
	// 它们现在被静默忽略、靠默认值运行，前移会让它们突然生效。
	if os.Getenv("AIJOBRISK_BLOG_DIR") != "" {
		if _, err := data.ReloadBlog(); err != nil {
			log.Printf("[blog] %v", err)
		}
	}
	if data.Updated != "" {
		web.DataUpdated = data.Updated
	}
	log.Printf("[boot] loaded %d occupations, %d job slugs in %s (data updated %s)",
		len(data.Occupations), len(data.JobSlugs), time.Since(t0).Round(time.Millisecond), web.DataUpdated)

	mux := http.NewServeMux()

	// 静态资源
	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir(staticDir))))
	// 博客头图单独挂：可指向独立镜像（AIJOBRISK_BLOG_STATIC_DIR），且禁止列目录以免暴露定时文章。
	blogStatic := env("AIJOBRISK_BLOG_STATIC_DIR", staticDir+"/blog")
	mux.Handle("/static/blog/", http.StripPrefix("/static/blog/", web.NoListing(http.FileServer(http.Dir(blogStatic)))))
	mux.HandleFunc("/logo.svg", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, staticDir+"/logo.svg")
	})

	// sitemap / robots
	web.RegisterSitemap(mux, site)

	// 投票 API（同源 /api/*）
	pollsapi.Register(mux)

	// Resend 收件 webhook → Telegram 提醒（未配签名密钥或 Telegram 时 404）
	mux.HandleFunc("/hooks/resend", newsletter.WebhookHandler)

	// 博客热重载（仅本机 + token；未配 AIJOBRISK_RELOAD_TOKEN 时整个接口 404）
	mux.HandleFunc("/internal/reload-blog", web.ReloadBlogHandler)

	// 页面（catch-all，内部剥语言前缀后分发）
	mux.Handle("/", web.Router(site))

	addr := host + ":" + port
	bs := data.BlogStatsNow()
	log.Printf("[blog] %d posts: %d visible, %d scheduled (next %q); dir=%s static=%s reload-endpoint=%v",
		bs.Total, bs.Visible, bs.Scheduled, bs.Next, data.BlogDir(), blogStatic, web.ReloadEnabled())
	log.Printf("[newsletter] %s", newsletter.Status())
	log.Printf("[serve] aijobrisk-go on http://%s (site=%s)", addr, site)
	srv := &http.Server{Addr: addr, Handler: mux, ReadHeaderTimeout: 10 * time.Second}
	log.Fatal(srv.ListenAndServe())
}
