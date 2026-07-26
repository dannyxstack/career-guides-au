// 独立投票 API 服务（可选）。逻辑在 internal/pollsapi；主站也可把同一套端点挂到自己端口（见 main.go）。
// 用法：POLLS_PORT=8790 POLLS_CORS_ORIGINS=https://aijobrisk.com ./pollsapi.exe
package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"aijobrisk/internal/polls"
	"aijobrisk/internal/pollsapi"
)

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

func main() {
	pollsapi.LoadDotEnv()
	pollsapi.ConfigureFromEnv()

	if err := polls.Load(env("AIJOBRISK_DATA", "data")); err != nil {
		log.Fatalf("load polls.json: %v", err)
	}

	mux := http.NewServeMux()
	pollsapi.Register(mux)

	addr := env("HOST", "127.0.0.1") + ":" + env("POLLS_PORT", env("PORT", "8790"))
	log.Printf("[pollsapi] listening on http://%s (%d polls)", addr, len(polls.Polls))
	log.Fatal((&http.Server{Addr: addr, Handler: mux, ReadHeaderTimeout: 10 * time.Second}).ListenAndServe())
}
