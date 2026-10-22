package newsletter

import (
	"log"
	"time"
)

// Result 订阅流程的结果，页面据此显示对应提示。
type Result int

const (
	OK              Result = iota
	ErrDisabled            // 未配置，功能关闭
	ErrInvalidEmail        // 邮箱格式不对
	ErrHumanCheck          // Turnstile 未通过
	ErrTooMany             // 触发限流
	ErrBadCode             // 验证码错误或已过期
	ErrUpstream            // Resend 调用失败
)

var now = time.Now // 测试里替换

// Start 第一步：校验邮箱与人机验证、过限流，然后发出验证码。返回规范化后的邮箱。
// 检查顺序：先做不花钱的本地校验，最后才动全站当日额度，避免被无效请求耗掉。
func Start(rawEmail, turnstileToken, ip string) (string, Result) {
	if !SignupEnabled() {
		return "", ErrDisabled
	}
	email := NormalizeEmail(rawEmail)
	if email == "" {
		return "", ErrInvalidEmail
	}
	if !verifyTurnstile(turnstileToken, ip) {
		return email, ErrHumanCheck
	}
	t := now()
	// 全站上限放最后：只有其余检查都通过的请求才会占用当日额度。
	switch allowAll(t, check{sendCooldown, email}, check{sendPerEmailDay, email},
		check{sendPerIP, ip}, check{globalLimiter(), "all"}) {
	case -1:
	case 3:
		log.Printf("[newsletter] daily cap of %d verification emails reached", cfg.dailyCap)
		return email, ErrTooMany
	default:
		return email, ErrTooMany
	}
	if err := sendCodeEmail(email, issueCode(email, t)); err != nil {
		log.Printf("[newsletter] send code to %s failed: %v", maskEmail(email), err)
		return email, ErrUpstream
	}
	log.Printf("[newsletter] code sent to %s", maskEmail(email))
	return email, OK
}

// Verify 第二步：核对验证码，通过后把邮箱写进 Resend 联系人。
func Verify(rawEmail, code, ip string) Result {
	if !SignupEnabled() {
		return ErrDisabled
	}
	email := NormalizeEmail(rawEmail)
	if email == "" {
		return ErrInvalidEmail
	}
	t := now()
	if allowAll(t, check{verifyPerEmail, email}, check{verifyPerIP, ip}) != -1 {
		return ErrTooMany
	}
	if !checkCode(email, code, t) {
		return ErrBadCode
	}
	if err := addContact(email); err != nil {
		log.Printf("[newsletter] add contact %s failed: %v", maskEmail(email), err)
		return ErrUpstream
	}
	log.Printf("[newsletter] subscribed %s", maskEmail(email))
	return OK
}
