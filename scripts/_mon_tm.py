"""翻译进度监视器：轮询 translations_v2 中某 locale 的已译数，
每跨过 10% 里程碑输出一行（Monitor 事件），全部完成或长时间停滞则退出。

用法：python scripts/_mon_tm.py <locale> <base_count> <target_count>
  base_count   任务开始前该 locale 已有译文数
  target_count 全部译完时该 locale 的译文数（= translation_src_v2 总数）
"""
import sys, time
sys.path.insert(0, ".")
from db.connection import get_cursor


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

LOC = sys.argv[1]
BASE = int(sys.argv[2])
TARGET = int(sys.argv[3])
TODO = TARGET - BASE
POLL = 60          # 秒
STALL = 1200       # 20 分钟无进展 -> 判定停滞并退出


def covered():
    with get_cursor() as c:
        c.execute("SELECT COUNT(*) n FROM translations_v2 WHERE locale=%s", (LOC,))
        return c.fetchone()["n"]


def main():
    print(f"[{LOC}] monitor start: base={BASE} target={TARGET} todo={TODO}", flush=True)
    next_pct = 10
    last_val = covered()
    last_change = time.time()
    # 若启动时已跨过若干里程碑（任务已跑了一会），先补报
    while last_val - BASE >= TODO * next_pct / 100 and next_pct <= 100:
        done = last_val - BASE
        print(f"[{LOC}] {next_pct}% — {done}/{TODO} translated (total {last_val}/{TARGET}) @ {now()}", flush=True)
        next_pct += 10
    while True:
        time.sleep(POLL)
        try:
            v = covered()
        except Exception as e:
            print(f"[{LOC}] db-error {e}", flush=True)
            continue
        if v != last_val:
            last_val = v
            last_change = time.time()
        done = v - BASE
        while TODO > 0 and done >= TODO * next_pct / 100 and next_pct <= 100:
            print(f"[{LOC}] {next_pct}% — {done}/{TODO} translated (total {v}/{TARGET}) @ {now()}", flush=True)
            next_pct += 10
        if v >= TARGET:
            print(f"[{LOC}] DONE — covered {v}/{TARGET} @ {now()}", flush=True)
            break
        if time.time() - last_change > STALL:
            print(f"[{LOC}] STALLED — no progress {STALL}s, covered {v}/{TARGET} ({done}/{TODO}) @ {now()}", flush=True)
            break


if __name__ == "__main__":
    main()
