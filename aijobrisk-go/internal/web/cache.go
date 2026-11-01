package web

import "net/http"

const (
	// 浏览器不保留陈旧 HTML；支持共享缓存的边缘节点可短缓存 5 分钟。
	PageCacheControl = "public, max-age=0, s-maxage=300, stale-while-revalidate=86400"
	// 文件名或查询串带内容版本，静态资源可长缓存；当前保守设为 7 天。
	StaticCacheControl = "public, max-age=604800"
	// sitemap/robots 会随数据或定时文章变化，边缘缓存 1 小时。
	DiscoveryCacheControl = "public, max-age=300, s-maxage=3600"
)

// WithCacheControl 给静态 handler 增加统一缓存策略；下游显式设置时不覆盖。
func WithCacheControl(next http.Handler, policy string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if w.Header().Get("Cache-Control") == "" {
			w.Header().Set("Cache-Control", policy)
		}
		next.ServeHTTP(w, r)
	})
}
