package newsletter

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"testing"
	"time"
)

// ---------- 测试桩：Resend / Telegram / Turnstile ----------

type stubReq struct {
	Method, Path string
	Body         map[string]any
}

type stub struct {
	mu   sync.Mutex
	reqs []stubReq
	// 按 "METHOD /path" 前缀返回的状态码与 body；未命中返回 200 {}
	resp map[string]struct {
		code int
		body string
	}
}

func (s *stub) handler(w http.ResponseWriter, r *http.Request) {
	raw, _ := io.ReadAll(r.Body)
	var m map[string]any
	_ = json.Unmarshal(raw, &m)
	if m == nil && r.Header.Get("Content-Type") == "application/x-www-form-urlencoded" {
		_ = r.ParseForm()
	}
	s.mu.Lock()
	s.reqs = append(s.reqs, stubReq{r.Method, r.URL.Path, m})
	s.mu.Unlock()
	for k, v := range s.resp {
		if strings.HasPrefix(r.Method+" "+r.URL.Path, k) {
			w.WriteHeader(v.code)
			_, _ = w.Write([]byte(v.body))
			return
		}
	}
	_, _ = w.Write([]byte(`{"ok":true,"id":"x","success":true}`))
}

func (s *stub) calls(prefix string) []stubReq {
	s.mu.Lock()
	defer s.mu.Unlock()
	var out []stubReq
	for _, q := range s.reqs {
		if strings.HasPrefix(q.Method+" "+q.Path, prefix) {
			out = append(out, q)
		}
	}
	return out
}

var t0 = time.Date(2026, 10, 22, 12, 3, 0, 0, time.UTC)

// setup 直接设 cfg（不走环境变量），外部端点指向桩，清零所有限流器，固定时钟。
func setup(t *testing.T) *stub {
	t.Helper()
	s := &stub{resp: map[string]struct {
		code int
		body string
	}{}}
	srv := httptest.NewServer(http.HandlerFunc(s.handler))
	t.Cleanup(srv.Close)
	prevR, prevT, prevTS, prevNow, prevCfg := resendBase, telegramBase, turnstileURL, now, cfg
	t.Cleanup(func() { resendBase, telegramBase, turnstileURL, now, cfg = prevR, prevT, prevTS, prevNow, prevCfg })
	resendBase, telegramBase, turnstileURL = srv.URL, srv.URL, srv.URL+"/turnstile"
	cfg = config{
		resendKey: "re_test", from: "AI Job Risk <noreply@aijobrisk.com>", replyTo: "contact@aijobrisk.com",
		secret: []byte(strings.Repeat("k", 32)), tgToken: "TOKEN", tgChat: "42",
		webhookSecret: []byte("whsec-test-key-bytes"), dailyCap: 60,
	}
	sendPerIP, sendCooldown, sendPerEmailDay = newLimiter(5, time.Hour), newLimiter(1, time.Minute), newLimiter(5, 24*time.Hour)
	verifyPerEmail, verifyPerIP = newLimiter(5, codeWindow), newLimiter(30, time.Hour)
	globalOnce, sendGlobal = sync.Once{}, nil
	seen = map[string]time.Time{}
	now = func() time.Time { return t0 }
	return s
}

var codeInSubject = regexp.MustCompile(`^(\d{6}) is your`)

func sentCode(t *testing.T, s *stub) string {
	t.Helper()
	emails := s.calls("POST /emails")
	if len(emails) == 0 {
		t.Fatal("no email sent")
	}
	m := codeInSubject.FindStringSubmatch(emails[len(emails)-1].Body["subject"].(string))
	if m == nil {
		t.Fatalf("code not in subject: %v", emails[len(emails)-1].Body["subject"])
	}
	return m[1]
}

// ---------- 纯函数 ----------

func TestNormalizeEmail(t *testing.T) {
	cases := map[string]string{
		"  Alice@Example.COM ":                   "alice@example.com",
		"a.b+news@sub.example.co":                "a.b+news@sub.example.co",
		"":                                       "",
		"no-at-sign":                             "",
		"a@b":                                    "", // 域名没有点
		"a@.example.com":                         "",
		"a@example..com":                         "",
		"Alice <a@example.com>":                  "", // 只收裸地址
		"a@example.com\r\nBcc: x@y.com":          "",
		strings.Repeat("x", 65) + "@example.com": "", // local 超长
	}
	for in, want := range cases {
		if got := NormalizeEmail(in); got != want {
			t.Errorf("NormalizeEmail(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestCodeValidityWindow(t *testing.T) {
	setup(t)
	email := "a@example.com"
	code := issueCode(email, t0)
	if len(code) != 6 {
		t.Fatalf("code %q", code)
	}
	if !checkCode(email, code, t0) || !checkCode(email, " "+code+" ", t0) {
		t.Fatal("fresh code rejected")
	}
	if !checkCode(email, code, t0.Add(codeWindow)) {
		t.Fatal("code should still be valid in the next window")
	}
	if checkCode(email, code, t0.Add(2*codeWindow+time.Second)) {
		t.Fatal("code valid after two windows")
	}
	if checkCode("b@example.com", code, t0) {
		t.Fatal("code accepted for a different email")
	}
	for _, bad := range []string{"", "12345", "1234567", "12a456"} {
		if checkCode(email, bad, t0) {
			t.Fatalf("malformed code %q accepted", bad)
		}
	}
	cfg.secret = []byte(strings.Repeat("z", 32)) // 换密钥后旧码失效
	if checkCode(email, code, t0) {
		t.Fatal("code survived secret rotation")
	}
}

func TestLimiterSlidingWindow(t *testing.T) {
	l := newLimiter(2, time.Minute)
	if !l.allow("k", t0) || !l.allow("k", t0.Add(time.Second)) {
		t.Fatal("first two should pass")
	}
	if l.allow("k", t0.Add(2*time.Second)) {
		t.Fatal("third within window should fail")
	}
	if !l.allow("other", t0) {
		t.Fatal("keys must be independent")
	}
	if !l.allow("k", t0.Add(61*time.Second)) {
		t.Fatal("should pass after window slides")
	}
	l.allow("k", t0.Add(10*time.Minute)) // 触发清理
	if _, ok := l.hits["other"]; ok {
		t.Fatal("expired key not swept")
	}
}

// ---------- 订阅流程 ----------

func TestStartAndVerifyHappyPath(t *testing.T) {
	s := setup(t)
	cfg.segmentID = "seg_1"
	email, res := Start(" Reader@Example.com ", "", "203.0.113.5")
	if res != OK || email != "reader@example.com" {
		t.Fatalf("Start = %q, %v", email, res)
	}
	e := s.calls("POST /emails")[0].Body
	if e["from"] != cfg.from || e["reply_to"] != "contact@aijobrisk.com" {
		t.Fatalf("email headers wrong: %v", e)
	}
	if to := e["to"].([]any); len(to) != 1 || to[0] != "reader@example.com" {
		t.Fatalf("to = %v", e["to"])
	}
	code := sentCode(t, s)
	if !strings.Contains(e["text"].(string), code) || !strings.Contains(e["html"].(string), code) {
		t.Fatal("code missing from body")
	}

	if r := Verify("reader@example.com", "000000", "203.0.113.5"); r != ErrBadCode && code != "000000" {
		t.Fatalf("wrong code: %v", r)
	}
	if r := Verify("READER@example.com", code, "203.0.113.5"); r != OK {
		t.Fatalf("Verify = %v", r)
	}
	c := s.calls("POST /contacts")
	if len(c) != 1 || c[0].Body["email"] != "reader@example.com" || c[0].Body["unsubscribed"] != false {
		t.Fatalf("contact not created correctly: %+v", c)
	}
	if segs := c[0].Body["segments"].([]any); segs[0].(map[string]any)["id"] != "seg_1" {
		t.Fatalf("segment missing: %v", c[0].Body)
	}
}

func TestStartRejectsAndLimits(t *testing.T) {
	s := setup(t)
	if _, r := Start("not-an-email", "", "1.1.1.1"); r != ErrInvalidEmail {
		t.Fatalf("invalid email: %v", r)
	}
	if _, r := Start("a@example.com", "", "1.1.1.1"); r != OK {
		t.Fatalf("first send: %v", r)
	}
	if _, r := Start("a@example.com", "", "1.1.1.1"); r != ErrTooMany {
		t.Fatalf("60s cooldown not enforced: %v", r)
	}
	// 同一 IP 换邮箱：每小时 5 次
	for i := 0; i < 4; i++ {
		if _, r := Start("u"+strconv.Itoa(i)+"@example.com", "", "1.1.1.1"); r != OK {
			t.Fatalf("send %d: %v", i, r)
		}
	}
	if _, r := Start("u9@example.com", "", "1.1.1.1"); r != ErrTooMany {
		t.Fatalf("per-IP limit not enforced: %v", r)
	}
	if n := len(s.calls("POST /emails")); n != 5 {
		t.Fatalf("emails sent = %d, want 5", n)
	}
}

func TestDailyCapProtectsQuota(t *testing.T) {
	s := setup(t)
	cfg.dailyCap = 3
	for i := 0; i < 3; i++ {
		if _, r := Start("u"+strconv.Itoa(i)+"@example.com", "", "10.0.0."+strconv.Itoa(i)); r != OK {
			t.Fatalf("send %d: %v", i, r)
		}
	}
	if _, r := Start("u9@example.com", "", "10.0.0.9"); r != ErrTooMany {
		t.Fatalf("daily cap not enforced: %v", r)
	}
	if n := len(s.calls("POST /emails")); n != 3 {
		t.Fatalf("emails sent = %d", n)
	}
}

func TestVerifyBruteForceLimit(t *testing.T) {
	setup(t)
	if _, r := Start("a@example.com", "", "1.1.1.1"); r != OK {
		t.Fatal(r)
	}
	real := issueCode("a@example.com", t0)
	tries := 0
	for i := 0; i < 5; i++ {
		guess := strconv.Itoa(100000 + i)
		if guess == real {
			continue
		}
		Verify("a@example.com", guess, "1.1.1.1")
		tries++
	}
	if r := Verify("a@example.com", real, "1.1.1.1"); r != ErrTooMany && tries == 5 {
		t.Fatalf("6th attempt should be rate limited, got %v", r)
	}
}

func TestDuplicateContactIsReactivated(t *testing.T) {
	for _, dup := range []struct {
		code int
		body string
	}{
		{409, `{"statusCode":409,"name":"conflict","message":"Contact already exists"}`},
		{422, `{"statusCode":422,"name":"validation_error","message":"Contact with this email already exists"}`},
	} {
		s := setup(t)
		s.resp["POST /contacts"] = dup
		Start("back@example.com", "", "1.1.1.1")
		if r := Verify("back@example.com", sentCode(t, s), "1.1.1.1"); r != OK {
			t.Fatalf("duplicate %d not treated as success: %v", dup.code, r)
		}
		p := s.calls("PATCH /contacts/")
		if len(p) != 1 || p[0].Path != "/contacts/back@example.com" || p[0].Body["unsubscribed"] != false {
			t.Fatalf("re-subscribe PATCH missing for %d: %+v", dup.code, p)
		}
	}
}

func TestUpstreamFailures(t *testing.T) {
	s := setup(t)
	s.resp["POST /emails"] = struct {
		code int
		body string
	}{403, `{"statusCode":403,"name":"validation_error","message":"domain not verified"}`}
	if _, r := Start("a@example.com", "", "1.1.1.1"); r != ErrUpstream {
		t.Fatalf("send failure: %v", r)
	}

	s = setup(t)
	s.resp["POST /contacts"] = struct {
		code int
		body string
	}{401, `{"statusCode":401,"name":"validation_error","message":"API key is invalid"}`}
	Start("a@example.com", "", "1.1.1.1")
	if r := Verify("a@example.com", sentCode(t, s), "1.1.1.1"); r != ErrUpstream {
		t.Fatalf("non-duplicate contact error must fail: %v", r)
	}
	if len(s.calls("PATCH")) != 0 {
		t.Fatal("must not PATCH on auth error")
	}
}

func TestTurnstileEnforcedWhenConfigured(t *testing.T) {
	s := setup(t)
	cfg.turnstileSecret, cfg.turnstileSiteKey = "ts-secret", "ts-site"
	if _, r := Start("a@example.com", "", "1.1.1.1"); r != ErrHumanCheck {
		t.Fatalf("missing token: %v", r)
	}
	s.resp["POST /turnstile"] = struct {
		code int
		body string
	}{200, `{"success":false}`}
	if _, r := Start("a@example.com", "bad", "1.1.1.1"); r != ErrHumanCheck {
		t.Fatalf("failed token: %v", r)
	}
	delete(s.resp, "POST /turnstile") // 桩默认返回 success:true
	if _, r := Start("a@example.com", "good", "1.1.1.1"); r != OK {
		t.Fatalf("valid token: %v", r)
	}
	if len(s.calls("POST /emails")) != 1 {
		t.Fatal("failed human checks must not send email")
	}
}

func TestDisabledWithoutConfig(t *testing.T) {
	setup(t)
	cfg.resendKey = ""
	if _, r := Start("a@example.com", "", "1.1.1.1"); r != ErrDisabled {
		t.Fatalf("Start: %v", r)
	}
	if r := Verify("a@example.com", "123456", "1.1.1.1"); r != ErrDisabled {
		t.Fatalf("Verify: %v", r)
	}
}

// ---------- webhook ----------

func sign(key []byte, id, ts string, body []byte) string {
	m := hmac.New(sha256.New, key)
	m.Write([]byte(id + "." + ts + "."))
	m.Write(body)
	return "v1," + base64.StdEncoding.EncodeToString(m.Sum(nil))
}

func TestVerifySvix(t *testing.T) {
	key := []byte("secret-key")
	body := []byte(`{"type":"inbox.email.received"}`)
	ts := strconv.FormatInt(t0.Unix(), 10)
	good := sign(key, "msg_1", ts, body)
	if !verifySvix(key, "msg_1", ts, good, body, t0) {
		t.Fatal("valid signature rejected")
	}
	if !verifySvix(key, "msg_1", ts, "v1,AAAA "+good, body, t0) {
		t.Fatal("must accept when any listed signature matches")
	}
	if verifySvix(key, "msg_1", ts, good, append(body, ' '), t0) {
		t.Fatal("tampered body accepted")
	}
	if verifySvix([]byte("other"), "msg_1", ts, good, body, t0) {
		t.Fatal("wrong key accepted")
	}
	if verifySvix(key, "msg_2", ts, good, body, t0) {
		t.Fatal("signature bound to another id accepted")
	}
	if verifySvix(key, "msg_1", ts, good, body, t0.Add(6*time.Minute)) {
		t.Fatal("stale timestamp accepted (replay)")
	}
	if verifySvix(key, "msg_1", ts, strings.Replace(good, "v1,", "v2,", 1), body, t0) {
		t.Fatal("unknown signature version accepted")
	}
}

const inboxEvent = `{"type":"inbox.email.received","created_at":"2026-10-22T12:00:00.000Z","data":{
 "source":"system","inbox_id":"ib_1","thread_id":"th_1","email_id":"em_1",
 "thread":{"object":"inbox_thread","id":"th_1","subject":"Question about data","folder":"inbox","labels":[],"read":false},
 "email":{"id":"em_1","direction":"inbound","from":"Steve <steve@example.com>","to":["contact@aijobrisk.com"],
  "cc":[],"bcc":[],"reply_to":[],"subject":"Question about\r\ndata","message_id":"<x@y>",
  "attachments":[{"id":"a1","filename":"cv.pdf","size":1}],"read":false,"received_at":"2026-10-22T12:00:00.000Z"}}}`

func postHook(id, body string, mutate func(*http.Request)) *httptest.ResponseRecorder {
	ts := strconv.FormatInt(t0.Unix(), 10)
	r := httptest.NewRequest("POST", "/hooks/resend", strings.NewReader(body))
	r.Header.Set("svix-id", id)
	r.Header.Set("svix-timestamp", ts)
	r.Header.Set("svix-signature", sign(cfg.webhookSecret, id, ts, []byte(body)))
	if mutate != nil {
		mutate(r)
	}
	w := httptest.NewRecorder()
	WebhookHandler(w, r)
	return w
}

func TestWebhookSendsTelegramAlert(t *testing.T) {
	s := setup(t)
	if w := postHook("msg_1", inboxEvent, nil); w.Code != http.StatusNoContent {
		t.Fatalf("status %d", w.Code)
	}
	tg := s.calls("POST /botTOKEN/sendMessage")
	if len(tg) != 1 {
		t.Fatalf("telegram calls = %d", len(tg))
	}
	text := tg[0].Body["text"].(string)
	for _, want := range []string{"contact@aijobrisk.com", "Steve <steve@example.com>", "Subject: Question about data", "cv.pdf", "Resend"} {
		if !strings.Contains(text, want) {
			t.Fatalf("alert missing %q:\n%s", want, text)
		}
	}
	if strings.Contains(text, "\r") || tg[0].Body["chat_id"] != "42" || tg[0].Body["parse_mode"] != nil {
		t.Fatalf("alert not sanitised / wrong chat: %v", tg[0].Body)
	}

	// Svix 重试同一 id：不重复提醒
	postHook("msg_1", inboxEvent, nil)
	if n := len(s.calls("POST /botTOKEN")); n != 1 {
		t.Fatalf("duplicate delivery alerted again (%d)", n)
	}
}

func TestWebhookRejectsAndIgnores(t *testing.T) {
	s := setup(t)
	if w := postHook("m1", inboxEvent, func(r *http.Request) { r.Header.Set("svix-signature", "v1,forged") }); w.Code != http.StatusUnauthorized {
		t.Fatalf("forged signature: %d", w.Code)
	}
	if w := postHook("m2", `{"type":"email.sent","data":{}}`, nil); w.Code != http.StatusNoContent {
		t.Fatalf("other event: %d", w.Code)
	}
	spam := strings.Replace(inboxEvent, `"folder":"inbox"`, `"folder":"spam"`, 1)
	if w := postHook("m3", spam, nil); w.Code != http.StatusNoContent {
		t.Fatalf("spam: %d", w.Code)
	}
	if n := len(s.calls("POST /bot")); n != 0 {
		t.Fatalf("telegram should not be called, got %d", n)
	}
	r := httptest.NewRequest("GET", "/hooks/resend", nil)
	w := httptest.NewRecorder()
	WebhookHandler(w, r)
	if w.Code != http.StatusNotFound {
		t.Fatalf("GET: %d", w.Code)
	}
	cfg.tgToken = ""
	if w := postHook("m4", inboxEvent, nil); w.Code != http.StatusNotFound {
		t.Fatalf("unconfigured webhook must 404, got %d", w.Code)
	}
}

func TestWebhookRetriesWhenTelegramFails(t *testing.T) {
	s := setup(t)
	s.resp["POST /botTOKEN/sendMessage"] = struct {
		code int
		body string
	}{502, `{"ok":false,"description":"Bad Gateway"}`}
	if w := postHook("msg_9", inboxEvent, nil); w.Code != http.StatusBadGateway {
		t.Fatalf("telegram failure should return 502 for retry, got %d", w.Code)
	}
	delete(s.resp, "POST /botTOKEN/sendMessage")
	if w := postHook("msg_9", inboxEvent, nil); w.Code != http.StatusNoContent {
		t.Fatalf("retry: %d", w.Code)
	}
	if n := len(s.calls("POST /botTOKEN/sendMessage")); n != 2 {
		t.Fatalf("retry should send again, calls = %d", n)
	}
}

func TestPlainReceivedEventShape(t *testing.T) {
	s := setup(t)
	body := `{"type":"email.received","data":{"from":"a@b.com","to":["contact@aijobrisk.com"],"subject":"Hi"}}`
	if w := postHook("p1", body, nil); w.Code != http.StatusNoContent {
		t.Fatalf("status %d", w.Code)
	}
	text := s.calls("POST /botTOKEN/sendMessage")[0].Body["text"].(string)
	if !strings.Contains(text, "From: a@b.com") || !strings.Contains(text, "Subject: Hi") {
		t.Fatalf("plain event not formatted:\n%s", text)
	}
}
