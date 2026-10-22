package newsletter

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"net/mail"
	"strings"
	"time"
)

// 验证码无状态：code = HMAC(密钥, 邮箱, 10 分钟时间窗) 取 6 位。校验时对当前窗与上一窗各算一次，
// 所以有效期为 10–20 分钟。不落库、不占内存，进程重启后已发出的码照样能用；
// 换密钥会让所有未用的码失效（预期行为）。防暴力破解靠 limits.go 的尝试次数上限。

const codeWindow = 10 * time.Minute

func windowOf(t time.Time) int64 { return t.Unix() / int64(codeWindow/time.Second) }

func codeFor(email string, window int64) string {
	m := hmac.New(sha256.New, cfg.secret)
	fmt.Fprintf(m, "aijobrisk-newsletter-v1|%s|%d", email, window)
	sum := m.Sum(nil)
	return fmt.Sprintf("%06d", binary.BigEndian.Uint32(sum[:4])%1000000)
}

// issueCode 当前时间窗的验证码。
func issueCode(email string, now time.Time) string { return codeFor(email, windowOf(now)) }

// checkCode 常量时间比较；接受当前窗与上一窗。
func checkCode(email, code string, now time.Time) bool {
	code = strings.TrimSpace(code)
	if len(code) != 6 || strings.Trim(code, "0123456789") != "" {
		return false
	}
	w := windowOf(now)
	ok := false
	for _, x := range []int64{w, w - 1} {
		if hmac.Equal([]byte(codeFor(email, x)), []byte(code)) {
			ok = true // 不提前 return，两窗都算，耗时一致
		}
	}
	return ok
}

// NormalizeEmail 校验并规范化邮箱：只接受裸地址（不接受 "Name <a@b>"），去空白、转小写；非法返回 ""。
// 转小写是为了同一个人不会因为大小写不同而收到两个不同的码、在 Resend 里存成两个联系人。
func NormalizeEmail(s string) string {
	s = strings.TrimSpace(s)
	if s == "" || len(s) > 254 || strings.ContainsAny(s, " \t\r\n<>\"") {
		return ""
	}
	a, err := mail.ParseAddress(s)
	if err != nil || a.Address != s {
		return ""
	}
	at := strings.LastIndexByte(s, '@')
	local, domain := s[:at], s[at+1:]
	if local == "" || len(local) > 64 || !strings.Contains(domain, ".") ||
		strings.HasPrefix(domain, ".") || strings.HasSuffix(domain, ".") || strings.Contains(domain, "..") {
		return ""
	}
	return strings.ToLower(s)
}

// maskEmail 日志用：只留域名，不把完整邮箱写进服务器日志。
func maskEmail(email string) string {
	if at := strings.LastIndexByte(email, '@'); at >= 0 {
		return "***" + email[at:]
	}
	return "***"
}
