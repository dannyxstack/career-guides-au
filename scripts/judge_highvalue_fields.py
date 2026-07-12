# -*- coding: utf-8 -*-
"""DeepSeek 全判 3 个高价值字段(faq_a/visa_desc/suitability)的既有英文语义准确性。
目的：捞出规则抓不到的长尾语义错误(mistranslation/omission 等)，产出待重译清单。
- 全量选取(非抽样)：field ∈ 目标 且 已有 en。
- 批判失败(len mismatch)→拆单条重试，near-zero 丢失。
- 输出 JSONL(增量, 断点续跑)+汇总+待重译 src_hash 清单。
只读库，不回写。用法： python -m scripts.judge_highvalue_fields [--batch 8 --workers 10 --limit N --resume]
"""
import sys, os, json, argparse, threading, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.connection import get_cursor
from video_pipeline import config
from scripts.audit_en_quality import SYS_PROMPT, CATS, SYSTEMATIC, SEMANTIC
from openai import OpenAI

FIELDS = ("faq_a", "visa_desc", "suitability")
RAW = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "judge_highvalue.jsonl")
FLAGGED = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "judge_highvalue_flagged.json")
DS = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL, timeout=120, max_retries=2)


def fetch(limit=0):
    ph = ",".join(["%s"] * len(FIELDS))
    sql = (f"SELECT s.src_hash, s.src_text zh, s.field, t.text en FROM translations t "
           f"JOIN translation_src s ON s.src_hash=t.src_hash "
           f"WHERE t.locale='en' AND s.field IN ({ph})")
    with get_cursor() as cur:
        cur.execute(sql + (" LIMIT %s" % int(limit) if limit else ""), FIELDS)
        return cur.fetchall()


def judge(batch):
    items = [{"i": j, "zh": r["zh"], "en": r["en"]} for j, r in enumerate(batch)]
    user = "Review these items (JSON) and return the r array:\n" + json.dumps(items, ensure_ascii=False)
    resp = DS.chat.completions.create(model=config.DEEPSEEK_MODEL, max_tokens=4000, timeout=120,
        messages=[{"role": "system", "content": SYS_PROMPT}, {"role": "user", "content": user}],
        response_format={"type": "json_object"})
    r = json.loads(resp.choices[0].message.content).get("r", [])
    if len(r) != len(batch):
        raise ValueError(f"len {len(r)}!={len(batch)}")
    out = []
    for x, src in zip(r, batch):
        cat = x.get("category") if x.get("category") in CATS else "ok"
        out.append({"src_hash": src["src_hash"], "field": src["field"], "zh": src["zh"], "en": src["en"],
                    "category": cat, "severity": x.get("severity", "none"), "note": (x.get("note") or "")[:120]})
    return out


def judge_robust(batch):
    """批判失败则拆半重试，最终逐条，保证不丢。"""
    try:
        return judge(batch)
    except Exception:
        if len(batch) == 1:
            r = batch[0]
            return [{"src_hash": r["src_hash"], "field": r["field"], "zh": r["zh"], "en": r["en"],
                     "category": "judge_error", "severity": "none", "note": "single-fail"}]
        mid = len(batch) // 2
        return judge_robust(batch[:mid]) + judge_robust(batch[mid:])


def run(batch, workers, limit, resume):
    rows = fetch(limit)
    done_hashes = set()
    if resume and os.path.exists(RAW):
        for l in open(RAW, encoding="utf-8"):
            try: done_hashes.add(json.loads(l)["src_hash"])
            except Exception: pass
        rows = [r for r in rows if r["src_hash"] not in done_hashes]
        print(f"[resume] 已判 {len(done_hashes)}，剩 {len(rows)}")
    else:
        os.makedirs(os.path.dirname(RAW), exist_ok=True)
        open(RAW, "w").close()
    from collections import Counter
    fc = Counter(r["field"] for r in rows)
    print(f"待判 {len(rows)} 条  {dict(fc)}")
    lock = threading.Lock(); done = [0]; t0 = time.time()
    batches = [rows[i:i+batch] for i in range(0, len(rows), batch)]

    def work(bt):
        res = judge_robust(bt)
        with lock:
            with open(RAW, "a", encoding="utf-8") as fh:
                for x in res: fh.write(json.dumps(x, ensure_ascii=False) + "\n")
            done[0] += len(res)
            if done[0] % 2000 < batch:
                print(f"  {done[0]}/{len(rows)} ({time.time()-t0:.0f}s)", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(as_completed([ex.submit(work, bt) for bt in batches]))
    print(f"完成，用时 {time.time()-t0:.0f}s")
    summarize()


def summarize():
    from collections import Counter, defaultdict
    recs = [json.loads(l) for l in open(RAW, encoding="utf-8")]
    n = len(recs)
    byfield = defaultdict(Counter)
    for r in recs: byfield[r["field"]][r["category"]] += 1
    total = Counter(r["category"] for r in recs)
    je = total.get("judge_error", 0); judged = n - je
    sysn = sum(total[k] for k in SYSTEMATIC); semn = sum(total[k] for k in SEMANTIC)
    print(f"\n===== 高价值字段英文语义全判（n={n}, 有效 {judged}, judge_error={je}）=====")
    print(f"OK {total['ok']} ({total['ok']/judged*100:.1f}%) | 系统性 {sysn} ({sysn/judged*100:.1f}%) | "
          f"语义 {semn} ({semn/judged*100:.1f}%) | fluency {total['fluency']}")
    print("\n按字段:")
    for f in FIELDS:
        c = byfield[f]; t = sum(c.values()) - c.get("judge_error", 0)
        if not t: continue
        bad = sum(c[k] for k in SYSTEMATIC | SEMANTIC)
        print(f"  {f:14} n={t:>6}  OK {c['ok']/t*100:4.1f}%  错(系统+语义) {bad} ({bad/t*100:.1f}%)  "
              f"mistrans {c['mistranslation']} omission {c['omission']}")
    print("\n按类别:")
    for c in CATS:
        if total.get(c) and c != "ok": print(f"  {c:16} {total[c]:>5} ({total[c]/judged*100:.2f}%)")
    # 待重译清单：所有非 ok/fluency/judge_error（即系统性+语义 major/minor）
    flagged = [r["src_hash"] for r in recs if r["category"] in (SYSTEMATIC | SEMANTIC)]
    json.dump(flagged, open(FLAGGED, "w"), ensure_ascii=False)
    print(f"\n待重译 src_hash 清单 {len(flagged)} 条 -> {FLAGGED}")
    print("\n===== 语义错误样例（mistranslation/omission，前10）=====")
    bad = [r for r in recs if r["category"] in SEMANTIC][:10]
    for r in bad:
        print(f"  [{r['field']}/{r['category']}] {r['note']}")
        print(f"    zh : {r['zh'][:66]}")
        print(f"    en : {(r['en'] or '')[:84]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--summarize-only", action="store_true")
    a = ap.parse_args()
    summarize() if a.summarize_only else run(a.batch, a.workers, a.limit, a.resume)
