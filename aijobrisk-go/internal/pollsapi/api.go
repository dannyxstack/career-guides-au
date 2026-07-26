// Package pollsapi 提供投票 API 的 HTTP 处理器，可挂到主站同一 mux（同源、免 CORS），
// 也可由 cmd/pollsapi 独立起服务。DB 懒连接：sql.Open 不拨号，首个投票请求才真正连；
// 连不上则投票降级（GET 返回空票、POST 503），主站页面不受影响。凭据仅从环境变量读，不记日志。
package pollsapi

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"

	"aijobrisk/internal/polls"

	_ "github.com/go-sql-driver/mysql"
)

var (
	slugRe  = regexp.MustCompile(`^[a-z0-9][a-z0-9\-]{0,158}$`)
	tokenRe = regexp.MustCompile(`^[a-f0-9]{32}$`)

	dsn        string
	ipSalt     string
	turnstile  string
	corsSet    = map[string]bool{}
	rateMax    = 20
	rateWindow = 60 * time.Second

	dbOnce sync.Once
	db     *sql.DB
)

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

// ConfigureFromEnv 从环境变量读取投票 API 配置（不连 DB）。
func ConfigureFromEnv() {
	dsn = env("MYSQL_USER", "root") + ":" + os.Getenv("MYSQL_PASSWORD") +
		"@tcp(" + env("MYSQL_HOST", "127.0.0.1") + ":" + env("MYSQL_PORT", "3306") + ")/" +
		env("MYSQL_DATABASE", "career_guides_au") + "?charset=" + env("MYSQL_CHARSET", "utf8mb4") + "&parseTime=true"
	ipSalt = env("POLLS_IP_SALT", "change-me")
	turnstile = os.Getenv("POLLS_TURNSTILE_SECRET")
	rateMax, _ = strconv.Atoi(env("POLLS_RATE_MAX", "20"))
	rw, _ := strconv.Atoi(env("POLLS_RATE_WINDOW", "60"))
	rateWindow = time.Duration(rw) * time.Second
	corsSet = map[string]bool{}
	if v := os.Getenv("POLLS_CORS_ORIGINS"); v != "" {
		for _, o := range strings.Split(v, ",") {
			if o = strings.TrimSpace(o); o != "" {
				corsSet[o] = true
			}
		}
	}
}

// getDB 懒开连接池（sql.Open 不拨号；真正连接发生在首个查询）。
func getDB() *sql.DB {
	dbOnce.Do(func() {
		d, err := sql.Open("mysql", dsn)
		if err != nil {
			return
		}
		d.SetMaxOpenConns(16)
		d.SetConnMaxLifetime(5 * time.Minute)
		db = d
	})
	return db
}

// Register 把投票端点挂到 mux（/api/health、/api/polls、/api/polls/vote）。
func Register(mux *http.ServeMux) {
	mux.HandleFunc("/api/health", withCORS(health))
	mux.HandleFunc("/api/polls", withCORS(getPolls))
	mux.HandleFunc("/api/polls/vote", withCORS(vote))
}

func writeJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(v)
}
func httpErr(w http.ResponseWriter, code int, msg string) {
	writeJSON(w, code, map[string]string{"error": msg})
}

func withCORS(h http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		origin := r.Header.Get("Origin")
		if corsSet[origin] {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Vary", "Origin")
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
			w.Header().Set("Access-Control-Max-Age", "86400")
		}
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		h(w, r)
	}
}

func health(w http.ResponseWriter, r *http.Request) {
	codes := make([]string, 0, len(polls.Polls))
	for _, p := range polls.Polls {
		codes = append(codes, p.Code)
	}
	writeJSON(w, 200, map[string]any{"ok": true, "polls": codes})
}

// emptyViews DB 不可用时的降级视图（题目在、票为 0）。
func emptyViews() map[string]polls.View {
	out := map[string]polls.View{}
	for _, p := range polls.Polls {
		out[p.Code] = polls.View{Type: p.Type, Counts: map[string]int{}, Total: 0}
	}
	return out
}

func getPolls(w http.ResponseWriter, r *http.Request) {
	occ := strings.ToLower(r.URL.Query().Get("occ"))
	if !slugRe.MatchString(occ) {
		httpErr(w, 400, "bad occ")
		return
	}
	token := r.URL.Query().Get("token")
	if token != "" && !tokenRe.MatchString(token) {
		token = ""
	}
	d := getDB()
	if d == nil {
		writeJSON(w, 200, map[string]any{"polls": emptyViews()})
		return
	}
	views, err := polls.AllViews(d, occ, token)
	if err != nil {
		// DB 暂不可用：降级返回空票，页面照常（不 500）
		writeJSON(w, 200, map[string]any{"polls": emptyViews()})
		return
	}
	writeJSON(w, 200, map[string]any{"polls": views})
}

type voteIn struct {
	PollCode    string `json:"poll_code"`
	OccKey      string `json:"occ_key"`
	AnswerKey   string `json:"answer_key"`
	ClientToken string `json:"client_token"`
	Turnstile   string `json:"turnstile"`
}

func vote(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		httpErr(w, 405, "method not allowed")
		return
	}
	var v voteIn
	if err := json.NewDecoder(r.Body).Decode(&v); err != nil {
		httpErr(w, 400, "bad json")
		return
	}
	if _, ok := polls.ByCode[v.PollCode]; !ok {
		httpErr(w, 400, "unknown poll")
		return
	}
	occ := strings.ToLower(v.OccKey)
	if !slugRe.MatchString(occ) {
		httpErr(w, 400, "bad occ_key")
		return
	}
	if !tokenRe.MatchString(v.ClientToken) {
		httpErr(w, 400, "bad token")
		return
	}
	if !polls.OptionKeys(v.PollCode)[v.AnswerKey] {
		httpErr(w, 400, "bad answer")
		return
	}
	iph := ipHash(r)
	if !rateOK(iph) {
		httpErr(w, 429, "too many votes")
		return
	}
	if !verifyTurnstile(v.Turnstile) {
		httpErr(w, 403, "turnstile failed")
		return
	}
	d := getDB()
	if d == nil {
		httpErr(w, 503, "polls unavailable")
		return
	}
	view, err := polls.Vote(d, v.PollCode, occ, v.ClientToken, v.AnswerKey, iph)
	if err != nil {
		httpErr(w, 503, "polls unavailable")
		return
	}
	writeJSON(w, 200, map[string]any{"ok": true, "poll": view})
}

func clientIP(r *http.Request) string {
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		return strings.TrimSpace(strings.Split(xff, ",")[0])
	}
	host := r.RemoteAddr
	if i := strings.LastIndex(host, ":"); i >= 0 {
		host = host[:i]
	}
	return host
}
func ipHash(r *http.Request) string {
	h := sha256.Sum256([]byte(clientIP(r) + ipSalt))
	return hex.EncodeToString(h[:])
}

var (
	hitsMu sync.Mutex
	hits   = map[string][]time.Time{}
)

func rateOK(key string) bool {
	now := time.Now()
	hitsMu.Lock()
	defer hitsMu.Unlock()
	dq := hits[key]
	cut := now.Add(-rateWindow)
	i := 0
	for i < len(dq) && dq[i].Before(cut) {
		i++
	}
	dq = dq[i:]
	if len(dq) >= rateMax {
		hits[key] = dq
		return false
	}
	hits[key] = append(dq, now)
	return true
}

func verifyTurnstile(token string) bool {
	if turnstile == "" {
		return true
	}
	resp, err := http.PostForm("https://challenges.cloudflare.com/turnstile/v0/siteverify",
		url.Values{"secret": {turnstile}, "response": {token}})
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	var out struct {
		Success bool `json:"success"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return false
	}
	return out.Success
}

// LoadDotEnv 便捷：若存在 .env（AIJOBRISK_ENV / ./.env / ../.env / ../../.env）则加载缺省环境变量（不覆盖已设）。
func LoadDotEnv() {
	for _, p := range []string{os.Getenv("AIJOBRISK_ENV"), ".env", "../.env", "../../.env"} {
		if p == "" {
			continue
		}
		b, err := os.ReadFile(p)
		if err != nil {
			continue
		}
		for _, line := range strings.Split(string(b), "\n") {
			line = strings.TrimSpace(line)
			if line == "" || strings.HasPrefix(line, "#") {
				continue
			}
			kv := strings.SplitN(line, "=", 2)
			if len(kv) != 2 {
				continue
			}
			k := strings.TrimSpace(kv[0])
			val := strings.Trim(strings.TrimSpace(kv[1]), `"'`)
			if _, ok := os.LookupEnv(k); !ok {
				os.Setenv(k, val)
			}
		}
		return
	}
}
