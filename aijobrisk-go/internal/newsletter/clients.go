package newsletter

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"html"
	"io"
	"net/http"
	"net/url"
	"strings"
)

// —— Resend ——

// apiError Resend 返回的非 2xx 错误。
type apiError struct {
	Status  int
	Name    string
	Message string
}

func (e *apiError) Error() string {
	return fmt.Sprintf("resend %d %s: %s", e.Status, e.Name, e.Message)
}

func resendDo(method, path string, body any) error {
	b, err := json.Marshal(body)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(method, resendBase+path, bytes.NewReader(b))
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+cfg.resendKey)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "aijobrisk-newsletter/1")
	resp, err := httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(io.LimitReader(resp.Body, 64<<10))
	if resp.StatusCode/100 == 2 {
		return nil
	}
	var e struct {
		Name    string `json:"name"`
		Message string `json:"message"`
	}
	_ = json.Unmarshal(raw, &e)
	if e.Message == "" {
		e.Message = strings.TrimSpace(string(raw))
	}
	return &apiError{Status: resp.StatusCode, Name: e.Name, Message: e.Message}
}

// sendCodeEmail 发送验证码邮件。码放进主题，手机通知里一眼就能看到。
func sendCodeEmail(to, code string) error {
	subject := code + " is your AI Job Risk verification code"
	text := "Your verification code is " + code + "\n\n" +
		"Enter it on aijobrisk.com to confirm your subscription. It is valid for 10 minutes.\n\n" +
		"If you did not request this, ignore this email -- you will not be subscribed.\n\n" +
		"AI Job Risk · https://aijobrisk.com"
	body := `<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;color:#1f2937">` +
		`<p style="margin:0 0 16px">Your AI Job Risk verification code is</p>` +
		`<p style="font-size:32px;font-weight:700;letter-spacing:6px;margin:0 0 16px">` + html.EscapeString(code) + `</p>` +
		`<p style="margin:0 0 16px">Enter it on aijobrisk.com to confirm your subscription. It is valid for 10 minutes.</p>` +
		`<p style="margin:0;color:#6b7280;font-size:13px">If you did not request this, ignore this email &mdash; you will not be subscribed.</p>` +
		`</div>`
	msg := map[string]any{"from": cfg.from, "to": []string{to}, "subject": subject, "text": text, "html": body}
	if cfg.replyTo != "" {
		msg["reply_to"] = cfg.replyTo
	}
	return resendDo(http.MethodPost, "/emails", msg)
}

// isDuplicate Resend 文档没写重复创建联系人返回什么；按常见形态宽松识别。
func isDuplicate(err error) bool {
	var e *apiError
	if !errors.As(err, &e) {
		return false
	}
	if e.Status == http.StatusConflict {
		return true
	}
	m := strings.ToLower(e.Message + " " + e.Name)
	return (e.Status == 400 || e.Status == 422) && (strings.Contains(m, "exist") || strings.Contains(m, "duplicate"))
}

// addContact 把确认过的邮箱写进 Resend 联系人。已存在（例如之前退订过）则把它改回订阅状态，
// 否则重新订阅的人会一直停留在退订状态、收不到群发。
func addContact(email string) error {
	c := map[string]any{"email": email, "unsubscribed": false}
	if cfg.segmentID != "" {
		c["segments"] = []map[string]string{{"id": cfg.segmentID}}
	}
	err := resendDo(http.MethodPost, "/contacts", c)
	if err == nil || !isDuplicate(err) {
		return err
	}
	return resendDo(http.MethodPatch, "/contacts/"+url.PathEscape(email), map[string]any{"unsubscribed": false})
}

// —— Cloudflare Turnstile ——

func verifyTurnstile(token, ip string) bool {
	if !TurnstileOn() {
		return true
	}
	if token == "" {
		return false
	}
	resp, err := httpClient.PostForm(turnstileURL, url.Values{
		"secret": {cfg.turnstileSecret}, "response": {token}, "remoteip": {ip},
	})
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	var out struct {
		Success bool `json:"success"`
	}
	if json.NewDecoder(io.LimitReader(resp.Body, 16<<10)).Decode(&out) != nil {
		return false
	}
	return out.Success
}

// —— Telegram ——

// sendTelegram 纯文本消息（不用 parse_mode，邮件主题里的特殊字符不会弄坏格式或被解释成标记）。
// 出错时不把 URL 带进错误信息——URL 里含 bot token。
func sendTelegram(text string) error {
	b, _ := json.Marshal(map[string]any{
		"chat_id": cfg.tgChat, "text": text, "disable_web_page_preview": true,
	})
	resp, err := httpClient.Post(telegramBase+"/bot"+cfg.tgToken+"/sendMessage", "application/json", bytes.NewReader(b))
	if err != nil {
		var ue *url.Error
		if errors.As(err, &ue) {
			return fmt.Errorf("telegram request failed: %v", ue.Err)
		}
		return errors.New("telegram request failed")
	}
	defer resp.Body.Close()
	var out struct {
		OK          bool   `json:"ok"`
		Description string `json:"description"`
	}
	_ = json.NewDecoder(io.LimitReader(resp.Body, 16<<10)).Decode(&out)
	if resp.StatusCode/100 != 2 || !out.OK {
		return fmt.Errorf("telegram %d: %s", resp.StatusCode, out.Description)
	}
	return nil
}
