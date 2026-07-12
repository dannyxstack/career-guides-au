# -*- coding: utf-8 -*-
"""基准：P0+P1 命中串用本地 gemma3:12b 重译(zh->en)，再用 DeepSeek 验证质量。
分层抽 300：覆盖 R1(残留中文)/R2a-c(万系列)/R5/R6，重点压 gemma 的『万』弱点。
输出：每条 zh / 旧en(有错) / gemma新en / DeepSeek判定；汇总各规则修复成功率。
只读库，不回写。"""
import sys, os, json, time, random, argparse, threading
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.connection import get_cursor
from video_pipeline import config
from scripts.translate_strings import system_prompt
from scripts.en_rule_probe import CJK, EN_THOUSAND, MODELS, SUBJ_PAY, wan_dropped
from scripts.audit_en_quality import SYS_PROMPT as JUDGE_SYS, CATS
from openai import OpenAI

OUT = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "bench_gemma_retrans.jsonl")
GEMMA = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=300)
DS = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL, timeout=120, max_retries=2)

# 规则判定（primary rule 取最稀有优先，保证小规则被抽到）
def rules_of(z, e):
    r = []
    if CJK.search(e): r.append("R1_cjk")
    if "万" in z and EN_THOUSAND.search(e): r.append("R2c_thousand")
    if MODELS.search(e) and "模" not in z: r.append("R5_models")
    if wan_dropped(z, e): r.append("R2b_wandrop")
    if SUBJ_PAY.search(e): r.append("R6_pay")
    if "万" in z: r.append("R2a_wan")
    return r

PRIORITY = ["R2c_thousand", "R5_models", "R1_cjk", "R2b_wandrop", "R6_pay", "R2a_wan"]
QUOTA = {"R2c_thousand": 20, "R5_models": 25, "R1_cjk": 55, "R2b_wandrop": 55, "R6_pay": 55, "R2a_wan": 90}


def collect_sample(n=300):
    with get_cursor() as cur:
        cur.execute("SELECT s.src_hash, s.src_text zh, s.field, t.text en FROM translations t "
                    "JOIN translation_src s ON s.src_hash=t.src_hash WHERE t.locale='en'")
        rows = cur.fetchall()
    buckets = {k: [] for k in PRIORITY}
    for r in rows:
        z, e = r["zh"] or "", r["en"] or ""
        rs = rules_of(z, e)
        if not rs:
            continue
        primary = min(rs, key=lambda x: PRIORITY.index(x))
        r["rules"] = rs; r["primary"] = primary
        buckets[primary].append(r)
    random.seed(7)
    picked, seen = [], set()
    for k in PRIORITY:
        random.shuffle(buckets[k])
        for r in buckets[k][:QUOTA[k]]:
            if r["src_hash"] in seen: continue
            picked.append(r); seen.add(r["src_hash"])
    # 不足 300 用 R2a 补
    for r in buckets["R2a_wan"]:
        if len(picked) >= n: break
        if r["src_hash"] in seen: continue
        picked.append(r); seen.add(r["src_hash"])
    print("分层命中:", {k: len(v) for k, v in buckets.items()})
    print("抽样构成:", {k: sum(p["primary"] == k for p in picked) for k in PRIORITY}, "总", len(picked))
    return picked[:n]


def gemma_translate(zh_list):
    """用与生产一致的 en system prompt，gemma3:12b 批量重译。"""
    user = ("Translate these strings (JSON array) and return {\"t\": [...]} with the same length:\n"
            + json.dumps(zh_list, ensure_ascii=False))
    resp = GEMMA.chat.completions.create(model="gemma3:12b", max_tokens=3000,
        messages=[{"role": "system", "content": system_prompt("English", "en")},
                  {"role": "user", "content": user}],
        response_format={"type": "json_object"})
    t = json.loads(resp.choices[0].message.content).get("t", [])
    if len(t) != len(zh_list): raise ValueError(f"len {len(t)}!={len(zh_list)}")
    return t


def ds_judge(items):
    """items: [{i, zh, en(=gemma新译)}] -> DeepSeek 判定 category/severity/note。"""
    user = "Review these items (JSON) and return the r array:\n" + json.dumps(items, ensure_ascii=False)
    resp = DS.chat.completions.create(model=config.DEEPSEEK_MODEL, max_tokens=3000,
        messages=[{"role": "system", "content": JUDGE_SYS}, {"role": "user", "content": user}],
        response_format={"type": "json_object"})
    r = json.loads(resp.choices[0].message.content).get("r", [])
    if len(r) != len(items): raise ValueError(f"judge len {len(r)}!={len(items)}")
    return r


def run(n, tbatch, jbatch):
    sample = collect_sample(n)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # 1) gemma 重译
    print(f"\n[gemma] 重译 {len(sample)} 条 ...")
    t0 = time.time(); new_en = [None]*len(sample); lock = threading.Lock(); done=[0]
    def tw(idx):
        chunk = sample[idx:idx+tbatch]
        try: out = gemma_translate([r["zh"] for r in chunk])
        except Exception:
            out = []
            for r in chunk:
                try: out.append(gemma_translate([r["zh"]])[0])
                except Exception: out.append(None)
        with lock:
            for j, v in enumerate(out): new_en[idx+j] = v
            done[0]+=len(chunk)
            if done[0] % 50 < tbatch: print(f"  gemma {done[0]}/{len(sample)} ({time.time()-t0:.0f}s)", flush=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(as_completed([ex.submit(tw, i) for i in range(0, len(sample), tbatch)]))
    print(f"[gemma] 完成 {time.time()-t0:.0f}s")
    # 2) DeepSeek 判定新译
    print(f"[deepseek] 验证 {len(sample)} 条 ...")
    verdicts = [None]*len(sample); t1=time.time(); done[0]=0
    def jw(idx):
        chunk = [(k, sample[k], new_en[k]) for k in range(idx, min(idx+jbatch, len(sample)))]
        items = [{"i": p, "zh": s["zh"], "en": ne or ""} for p,(k,s,ne) in enumerate(chunk)]
        try: rr = ds_judge(items)
        except Exception as e: rr = [{"category":"judge_error","severity":"none","note":str(e)[:60]}]*len(chunk)
        with lock:
            for (k,s,ne), v in zip(chunk, rr):
                cat = v.get("category") if v.get("category") in CATS else "ok"
                verdicts[k] = {"category": cat, "severity": v.get("severity","none"), "note": (v.get("note") or "")[:120]}
            done[0]+=len(chunk)
            if done[0] % 60 < jbatch: print(f"  judge {done[0]}/{len(sample)} ({time.time()-t1:.0f}s)", flush=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(as_completed([ex.submit(jw, i) for i in range(0, len(sample), jbatch)]))
    # 3) 落盘 + 汇总
    with open(OUT, "w", encoding="utf-8") as fh:
        for i, s in enumerate(sample):
            rec = {"src_hash": s["src_hash"], "field": s["field"], "primary": s["primary"],
                   "zh": s["zh"], "old_en": s["en"], "new_en": new_en[i], "verdict": verdicts[i]}
            fh.write(json.dumps(rec, ensure_ascii=False)+"\n")
    summarize()


def summarize():
    from collections import Counter, defaultdict
    recs = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    n = len(recs)
    ok = sum(r["verdict"] and r["verdict"]["category"] == "ok" for r in recs)
    je = sum(r["verdict"] and r["verdict"]["category"] == "judge_error" for r in recs)
    judged = n - je
    catc = Counter(r["verdict"]["category"] for r in recs if r["verdict"])
    byrule = defaultdict(lambda: [0,0])  # primary -> [ok, judged]
    for r in recs:
        v = r["verdict"]
        if not v or v["category"] == "judge_error": continue
        byrule[r["primary"]][1]+=1
        if v["category"]=="ok": byrule[r["primary"]][0]+=1
    print(f"\n===== gemma 重译质量（DeepSeek 判，n={n}，有效判定 {judged}）=====")
    print(f"整体 OK: {ok}/{judged} = {ok/judged*100:.1f}%  (judge_error={je})")
    print("\n按类别（新译仍存在的问题）:")
    for c in CATS:
        if catc.get(c) and c!="ok": print(f"  {c:16} {catc[c]:>4} ({catc[c]/judged*100:.1f}%)")
    print("\n按规则的重译成功率:")
    for k in ["R2c_thousand","R5_models","R1_cjk","R2b_wandrop","R6_pay","R2a_wan"]:
        o,t = byrule[k]
        if t: print(f"  {k:14} OK {o}/{t} = {o/t*100:.0f}%")
    # 重点：数值串是否仍错『万』
    print("\n===== 仍有问题的样例（前12）=====")
    bad = [r for r in recs if r["verdict"] and r["verdict"]["category"] not in ("ok","judge_error")]
    for r in bad[:12]:
        print(f"  [{r['primary']}/{r['verdict']['category']}] {r['verdict']['note']}")
        print(f"    zh : {r['zh'][:70]}")
        print(f"    new: {(r['new_en'] or '')[:88]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--tbatch", type=int, default=5)
    ap.add_argument("--jbatch", type=int, default=8)
    ap.add_argument("--summarize-only", action="store_true")
    a = ap.parse_args()
    summarize() if a.summarize_only else run(a.n, a.tbatch, a.jbatch)
