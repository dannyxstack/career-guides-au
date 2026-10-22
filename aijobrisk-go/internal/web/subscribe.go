package web

import (
	"net/http"

	"aijobrisk/internal/newsletter"
	"aijobrisk/internal/pollsapi"
)

// /subscribe 资讯订阅：两步——填邮箱收验证码，填验证码完成订阅。
// 纯服务端渲染的表单 POST，不依赖前端 JS（只有 Turnstile 组件需要 JS）。
// 与博客一样只出英文（其余语言前缀在 Router 里 301 回来），且整页 noindex、不进 sitemap——
// 这种薄页面被收录只会拉低全站质量评分。

// SubscribeVM 订阅页。Step: form | code | done。
type SubscribeVM struct {
	*Ctx
	Enabled bool
	Step    string
	Email   string
	Error   string
	SiteKey string
}

var subscribeMsg = map[newsletter.Result]string{
	newsletter.ErrDisabled:     "Subscriptions are temporarily unavailable. Please try again later.",
	newsletter.ErrInvalidEmail: "Please enter a valid email address.",
	newsletter.ErrHumanCheck:   "Please complete the verification check and try again.",
	newsletter.ErrTooMany:      "Too many attempts. Please wait a few minutes and try again.",
	newsletter.ErrBadCode:      "That code is incorrect or has expired. Check the latest email we sent, or start over to get a new code.",
	newsletter.ErrUpstream:     "We couldn't complete that just now. Please try again in a few minutes.",
}

// Subscribe GET 显示表单；POST 按 step 处理两步提交。
func Subscribe(w http.ResponseWriter, r *http.Request, ctx *Ctx) {
	ctx.Active = "blog"
	ctx.Title = "Subscribe to AI Job Risk updates | " + SiteName
	ctx.Description = "Get new analysis on AI and jobs by email. Confirm with a one-time code; unsubscribe anytime."
	ctx.Noindex = true
	ctx.EnglishOnly = true
	vm := &SubscribeVM{Ctx: ctx, Enabled: newsletter.SignupEnabled(), Step: "form", SiteKey: newsletter.TurnstileSiteKey()}
	w.Header().Set("Cache-Control", "no-store") // 页面里可能带着用户邮箱，任何一层都不要缓存

	switch r.Method {
	case http.MethodGet, http.MethodHead:
	case http.MethodPost:
		r.Body = http.MaxBytesReader(w, r.Body, 8<<10)
		if err := r.ParseForm(); err != nil {
			vm.Error = subscribeMsg[newsletter.ErrInvalidEmail]
			break
		}
		ip := pollsapi.ClientIP(r)
		switch r.PostFormValue("step") {
		case "verify":
			vm.Email = r.PostFormValue("email")
			if res := newsletter.Verify(vm.Email, r.PostFormValue("code"), ip); res == newsletter.OK {
				vm.Step = "done"
			} else {
				vm.Step, vm.Error = "code", subscribeMsg[res]
				if res == newsletter.ErrInvalidEmail || res == newsletter.ErrDisabled {
					vm.Step = "form"
				}
			}
		default: // "start"
			email, res := newsletter.Start(r.PostFormValue("email"), r.PostFormValue("cf-turnstile-response"), ip)
			vm.Email = email
			if res == newsletter.OK {
				vm.Step = "code"
			} else {
				vm.Error = subscribeMsg[res]
				if vm.Email == "" {
					vm.Email = r.PostFormValue("email")
				}
			}
		}
	default:
		w.Header().Set("Allow", "GET, POST")
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	renderPage(w, "subscribe.html", vm)
}
