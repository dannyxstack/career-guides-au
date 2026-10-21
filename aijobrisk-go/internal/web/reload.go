package web

import (
	"crypto/subtle"
	"encoding/json"
	"log"
	"net"
	"net/http"
	"os"
	"strings"

	"aijobrisk/internal/data"
)

// 博客热重载接口：POST /internal/reload-blog
//
// 由服务器上的 ops/blog-pull.sh 在同步完 data/blog/ 后调用，进程不重启、不停服。
// 用接口而不用 SIGHUP，是因为 Go 进程默认收到 SIGHUP 会直接退出，而 systemd 的
// Restart=on-failure 不会拉起被 SIGHUP 终止的进程——旧二进制一旦收到信号整站就挂了；
// 接口在旧二进制上只会 404，无害。
//
// 鉴权（任何一条不满足都回 404，不暴露接口存在）：
//   - 环境变量 AIJOBRISK_RELOAD_TOKEN 未设或短于 32 字符 -> 功能关闭
//   - 只接受 POST
//   - 只接受本机直连：nginx/Cloudflare 转发来的请求都带 X-Forwarded-For 等头，一律拒绝。
//     注意不能只看 RemoteAddr——经 nginx 反代时它永远是 127.0.0.1。
//   - X-Reload-Token 与环境变量常量时间比较

const reloadTokenMinLen = 32

func reloadToken() string {
	t := os.Getenv("AIJOBRISK_RELOAD_TOKEN")
	if len(t) < reloadTokenMinLen {
		return ""
	}
	return t
}

// ReloadEnabled 启动日志用：重载接口是否开启。
func ReloadEnabled() bool { return reloadToken() != "" }

func viaProxy(r *http.Request) bool {
	for _, h := range []string{"X-Forwarded-For", "X-Real-IP", "CF-Connecting-IP", "Forwarded"} {
		if r.Header.Get(h) != "" {
			return true
		}
	}
	return false
}

func fromLoopback(r *http.Request) bool {
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		host = r.RemoteAddr
	}
	ip := net.ParseIP(host)
	return ip != nil && ip.IsLoopback()
}

// ReloadBlogHandler 重读 data/blog/ 并原子替换；返回可见/定时文章统计。
func ReloadBlogHandler(w http.ResponseWriter, r *http.Request) {
	token := reloadToken()
	if token == "" || r.Method != http.MethodPost || viaProxy(r) || !fromLoopback(r) ||
		subtle.ConstantTimeCompare([]byte(r.Header.Get("X-Reload-Token")), []byte(token)) != 1 {
		http.NotFound(w, r)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	st, err := data.ReloadBlog()
	if err != nil {
		log.Printf("[blog] reload failed: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		_ = json.NewEncoder(w).Encode(map[string]any{"ok": false, "error": err.Error()})
		return
	}
	log.Printf("[blog] reloaded: total=%d visible=%d scheduled=%d next=%q (day %s UTC)",
		st.Total, st.Visible, st.Scheduled, st.Next, st.Day)
	_ = json.NewEncoder(w).Encode(map[string]any{"ok": true, "stats": st})
}

// NoListing 禁止目录列表：/static/blog/ 的目录页会列出所有头图文件名，
// 等于提前暴露尚未到发布日的文章 slug（SVG 里还写着标题）。只放行具体文件。
func NoListing(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "" || strings.HasSuffix(r.URL.Path, "/") {
			http.NotFound(w, r)
			return
		}
		h.ServeHTTP(w, r)
	})
}
