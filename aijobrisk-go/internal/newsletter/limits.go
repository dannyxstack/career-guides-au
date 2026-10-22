package newsletter

import (
	"sync"
	"time"
)

// limiter 滑动窗口计数器（内存）。进程重启会清零——对这里的用途可接受：
// 它挡的是短时间内的滥用（轰炸某个邮箱、暴力试码、刷光 Resend 当日额度）。
type limiter struct {
	mu        sync.Mutex
	max       int
	win       time.Duration
	hits      map[string][]time.Time
	lastSweep time.Time
}

func newLimiter(max int, win time.Duration) *limiter {
	return &limiter{max: max, win: win, hits: map[string][]time.Time{}}
}

// prune 去掉窗口外的记录，并定期清理过期 key（内存不随访问者无限增长）。调用方需持有 l.mu。
func (l *limiter) prune(key string, now time.Time) []time.Time {
	cut := now.Add(-l.win)
	if now.Sub(l.lastSweep) > l.win {
		for k, ts := range l.hits {
			if len(ts) == 0 || !ts[len(ts)-1].After(cut) {
				delete(l.hits, k)
			}
		}
		l.lastSweep = now
	}
	ts := l.hits[key]
	i := 0
	for i < len(ts) && !ts[i].After(cut) {
		i++
	}
	ts = ts[i:]
	l.hits[key] = ts
	return ts
}

func (l *limiter) wouldAllow(key string, now time.Time) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	return len(l.prune(key, now)) < l.max
}

func (l *limiter) record(key string, now time.Time) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.hits[key] = append(l.prune(key, now), now)
}

// allow 单个限流器：未超限则记一次并返回 true。
func (l *limiter) allow(key string, now time.Time) bool { return allowAll(now, check{l, key}) == -1 }

type check struct {
	l   *limiter
	key string
}

var allMu sync.Mutex

// allowAll 多个限流器「全过才记」：任何一个超限就一个都不记，返回它的下标；全部通过返回 -1。
// 否则被冷却拦下的请求也会白白消耗同一 IP 的额度（用户重复点一下「发送」就少一次）。
func allowAll(now time.Time, cs ...check) int {
	allMu.Lock()
	defer allMu.Unlock()
	for i, c := range cs {
		if !c.l.wouldAllow(c.key, now) {
			return i
		}
	}
	for _, c := range cs {
		c.l.record(c.key, now)
	}
	return -1
}

// 各项上限。发码比校验严：发码会真的发出一封邮件、消耗额度，还可能被用来骚扰别人的邮箱。
var (
	sendPerIP       = newLimiter(5, time.Hour)    // 同一 IP 每小时最多申请 5 次
	sendCooldown    = newLimiter(1, time.Minute)  // 同一邮箱 60 秒冷却
	sendPerEmailDay = newLimiter(5, 24*time.Hour) // 同一邮箱每天最多 5 封
	verifyPerEmail  = newLimiter(5, codeWindow)   // 同一邮箱每个时间窗最多试 5 次（6 位码，暴力破解概率 ≈ 5/10^6）
	verifyPerIP     = newLimiter(30, time.Hour)   // 同一 IP 每小时最多试 30 次
	sendGlobal      *limiter                      // 全站 24 小时发码上限，见 globalLimiter
	globalOnce      sync.Once
)

func globalLimiter() *limiter {
	globalOnce.Do(func() { sendGlobal = newLimiter(cfg.dailyCap, 24*time.Hour) })
	return sendGlobal
}
