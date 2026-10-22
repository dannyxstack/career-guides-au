// Package newsletter 资讯订阅（邮箱验证码确认）与新邮件 Telegram 提醒。
//
// 只用标准库：Resend（发验证码、写联系人）、Cloudflare Turnstile、Telegram Bot API
// 都走 net/http。不用数据库：验证码由 HMAC 推导（无状态，进程重启不影响已发出的码），
// 订阅者只存在 Resend 的联系人里，网站本身不保存任何用户数据。
//
// 任一外部依赖未配置时，对应功能关闭（订阅页显示「暂不可用」、webhook 返回 404），
// 其余页面照常渲染。
package newsletter

import (
	"encoding/base64"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

type config struct {
	resendKey string
	from      string // 验证码邮件发件人，如 "AI Job Risk <noreply@aijobrisk.com>"
	replyTo   string // 读者回信落到哪个收件箱
	segmentID string // 可选：订阅者同时加入的 Resend segment

	secret []byte // 验证码 HMAC 密钥（≥32 字节）

	turnstileSecret  string
	turnstileSiteKey string

	tgToken, tgChat string
	webhookSecret   []byte // Resend（Svix）webhook 签名密钥，已去掉 whsec_ 前缀并 base64 解码

	dailyCap int // 24 小时内最多发出的验证码数：Resend 免费版每天 100 封由验证码、收件、回信共用
}

var (
	cfg config

	// 外部端点：测试里替换成 httptest 服务器。RESEND_API_BASE 仅供本地联调指向桩服务。
	resendBase   = "https://api.resend.com"
	telegramBase = "https://api.telegram.org"
	turnstileURL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
	httpClient   = &http.Client{Timeout: 10 * time.Second}
)

const minSecretLen = 32

// Configure 从环境变量读取配置。须在 .env 载入之后调用（main 里紧跟 pollsapi.ConfigureFromEnv）。
func Configure() {
	cfg = config{
		resendKey:        os.Getenv("RESEND_API_KEY"),
		from:             envOr("NEWSLETTER_FROM", "AI Job Risk <noreply@aijobrisk.com>"),
		replyTo:          envOr("NEWSLETTER_REPLY_TO", "contact@aijobrisk.com"),
		segmentID:        os.Getenv("RESEND_SEGMENT_ID"),
		turnstileSecret:  envOr("TURNSTILE_SECRET", os.Getenv("POLLS_TURNSTILE_SECRET")),
		turnstileSiteKey: os.Getenv("TURNSTILE_SITE_KEY"),
		tgToken:          os.Getenv("TELEGRAM_BOT_TOKEN"),
		tgChat:           os.Getenv("TELEGRAM_CHAT_ID"),
		dailyCap:         envInt("NEWSLETTER_DAILY_CAP", 60),
	}
	if s := os.Getenv("NEWSLETTER_SECRET"); len(s) >= minSecretLen {
		cfg.secret = []byte(s)
	} else if s != "" {
		log.Printf("[newsletter] NEWSLETTER_SECRET shorter than %d chars -- signup disabled", minSecretLen)
	}
	if ws := os.Getenv("RESEND_WEBHOOK_SECRET"); ws != "" {
		if k, err := base64.StdEncoding.DecodeString(strings.TrimPrefix(ws, "whsec_")); err == nil && len(k) > 0 {
			cfg.webhookSecret = k
		} else {
			log.Printf("[newsletter] RESEND_WEBHOOK_SECRET is not a valid whsec_ secret -- webhook disabled")
		}
	}
	if b := os.Getenv("RESEND_API_BASE"); b != "" {
		resendBase = strings.TrimRight(b, "/")
	}
	if (cfg.turnstileSecret == "") != (cfg.turnstileSiteKey == "") {
		log.Printf("[newsletter] Turnstile needs both TURNSTILE_SITE_KEY and TURNSTILE_SECRET -- human check OFF")
	}
}

// SignupEnabled 订阅功能是否可用（Resend key + 验证码密钥都配好）。
func SignupEnabled() bool { return cfg.resendKey != "" && len(cfg.secret) > 0 }

// TurnstileOn 是否启用人机验证。站点 key 与密钥缺一不可：只有密钥时页面渲染不出组件，所有提交都会失败。
func TurnstileOn() bool { return cfg.turnstileSecret != "" && cfg.turnstileSiteKey != "" }

// TurnstileSiteKey 页面上渲染 Turnstile 组件用；未启用时为空。
func TurnstileSiteKey() string {
	if !TurnstileOn() {
		return ""
	}
	return cfg.turnstileSiteKey
}

// WebhookEnabled 收件提醒是否可用（签名密钥 + Telegram 都配好）。
func WebhookEnabled() bool {
	return len(cfg.webhookSecret) > 0 && cfg.tgToken != "" && cfg.tgChat != ""
}

// Status 启动日志用。
func Status() string {
	return "signup=" + strconv.FormatBool(SignupEnabled()) +
		" turnstile=" + strconv.FormatBool(TurnstileOn()) +
		" telegram-alerts=" + strconv.FormatBool(WebhookEnabled()) +
		" daily-cap=" + strconv.Itoa(cfg.dailyCap)
}

func envOr(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

func envInt(k string, def int) int {
	if n, err := strconv.Atoi(os.Getenv(k)); err == nil && n > 0 {
		return n
	}
	return def
}
