package newsletter

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
	"unicode"
)

// Resend 收件 webhook：POST /hooks/resend
// 新邮件进 Resend Inbox（contact@aijobrisk.com）后，Resend 推送 inbox.email.received，
// 这里校验签名后给 Telegram 发一条提醒（发件人 + 主题 + 附件名）。正文不进 Telegram——
// payload 里本来就没有正文，也省得把来信内容散到第三方。回复在 Resend 后台 Inboxes 里做。
//
// Resend 的 webhook 由 Svix 投递：签名 = base64(HMAC-SHA256(key, "{svix-id}.{svix-timestamp}.{原始 body}"))，
// key 是 whsec_ 后面那段 base64 解码后的字节；svix-signature 头是空格分隔的 "v1,<签名>" 列表。

const (
	webhookMaxBody   = 1 << 20
	webhookTolerance = 5 * time.Minute // 时间戳偏差上限，挡重放
)

func verifySvix(key []byte, id, ts, sigHeader string, body []byte, at time.Time) bool {
	if len(key) == 0 || id == "" || ts == "" || sigHeader == "" {
		return false
	}
	sec, err := strconv.ParseInt(ts, 10, 64)
	if err != nil {
		return false
	}
	if d := at.Sub(time.Unix(sec, 0)); d > webhookTolerance || d < -webhookTolerance {
		return false
	}
	m := hmac.New(sha256.New, key)
	m.Write([]byte(id + "." + ts + "."))
	m.Write(body)
	want := base64.StdEncoding.EncodeToString(m.Sum(nil))
	ok := false
	for _, part := range strings.Fields(sigHeader) {
		ver, sig, found := strings.Cut(part, ",")
		if found && ver == "v1" && hmac.Equal([]byte(sig), []byte(want)) {
			ok = true
		}
	}
	return ok
}

// 已处理过的投递（svix-id），挡 Svix 重试造成的重复提醒。
var (
	seenMu sync.Mutex
	seen   = map[string]time.Time{}
)

func markSeen(id string, at time.Time) bool { // 首次见到返回 true
	seenMu.Lock()
	defer seenMu.Unlock()
	for k, t := range seen {
		if at.Sub(t) > 24*time.Hour {
			delete(seen, k)
		}
	}
	if _, dup := seen[id]; dup {
		return false
	}
	seen[id] = at
	return true
}

func unmarkSeen(id string) {
	seenMu.Lock()
	delete(seen, id)
	seenMu.Unlock()
}

type receivedEvent struct {
	Type string `json:"type"`
	Data struct {
		ThreadID string `json:"thread_id"`
		Thread   *struct {
			Subject string `json:"subject"`
			Folder  string `json:"folder"`
		} `json:"thread"`
		Email *struct {
			From        string   `json:"from"`
			To          []string `json:"to"`
			Subject     string   `json:"subject"`
			Attachments []struct {
				Filename string `json:"filename"`
			} `json:"attachments"`
		} `json:"email"`
		// 非 Inbox 的 email.received 事件把字段放在 data 顶层，一并兼容。
		From    string   `json:"from"`
		To      []string `json:"to"`
		Subject string   `json:"subject"`
	} `json:"data"`
}

// clean 去控制字符并截断，防止来信主题里的换行/超长内容把提醒弄乱。
func clean(s string, max int) string {
	s = strings.Map(func(r rune) rune {
		if unicode.IsControl(r) {
			return ' '
		}
		return r
	}, s)
	s = strings.Join(strings.Fields(s), " ")
	if r := []rune(s); len(r) > max {
		s = string(r[:max]) + "…"
	}
	if s == "" {
		return "(none)"
	}
	return s
}

func formatAlert(ev *receivedEvent) string {
	d := ev.Data
	from, subject, to := d.From, d.Subject, d.To
	var files []string
	if d.Email != nil {
		from, subject, to = d.Email.From, d.Email.Subject, d.Email.To
		for _, a := range d.Email.Attachments {
			files = append(files, clean(a.Filename, 60))
		}
	}
	if subject == "" && d.Thread != nil {
		subject = d.Thread.Subject
	}
	var b strings.Builder
	fmt.Fprintf(&b, "📬 New email to %s\n", clean(strings.Join(to, ", "), 120))
	fmt.Fprintf(&b, "From: %s\n", clean(from, 200))
	fmt.Fprintf(&b, "Subject: %s\n", clean(subject, 300))
	if len(files) > 0 {
		fmt.Fprintf(&b, "Attachments (%d): %s\n", len(files), strings.Join(files, ", "))
	}
	b.WriteString("Reply in Resend → Inboxes")
	return b.String()
}

// WebhookHandler 处理 Resend 收件 webhook。未配置时 404；签名不对 401；
// Telegram 发送失败回 502，让 Svix 稍后重试（届时不会被去重挡掉）。
func WebhookHandler(w http.ResponseWriter, r *http.Request) {
	if !WebhookEnabled() || r.Method != http.MethodPost {
		http.NotFound(w, r)
		return
	}
	body, err := io.ReadAll(io.LimitReader(r.Body, webhookMaxBody))
	if err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	id := r.Header.Get("svix-id")
	at := now()
	if !verifySvix(cfg.webhookSecret, id, r.Header.Get("svix-timestamp"), r.Header.Get("svix-signature"), body, at) {
		http.Error(w, "invalid signature", http.StatusUnauthorized)
		return
	}
	var ev receivedEvent
	if err := json.Unmarshal(body, &ev); err != nil {
		http.Error(w, "bad payload", http.StatusBadRequest)
		return
	}
	if ev.Type != "inbox.email.received" && ev.Type != "email.received" {
		w.WriteHeader(http.StatusNoContent) // 其它事件不关心
		return
	}
	if ev.Data.Thread != nil && ev.Data.Thread.Folder == "spam" {
		w.WriteHeader(http.StatusNoContent) // 进了垃圾箱的不提醒
		return
	}
	if !markSeen(id, at) {
		w.WriteHeader(http.StatusNoContent) // 重复投递
		return
	}
	if err := sendTelegram(formatAlert(&ev)); err != nil {
		unmarkSeen(id) // 让 Svix 重试时能再次发送
		log.Printf("[newsletter] telegram alert failed: %v", err)
		http.Error(w, "alert failed", http.StatusBadGateway)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
