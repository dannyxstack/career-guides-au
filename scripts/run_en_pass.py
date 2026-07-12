# -*- coding: utf-8 -*-
"""DeepSeek zh->en 合并 pass：补缺 + 修规则错 + 重译判分命中，写入 translations(locale='en')。
- 补缺：所有缺 en 的源串。
- 修规则错：en_rule_probe 检测器命中(R1/R2b/R2c/R5/R6/R2a)的既有英文，覆盖重译。
- 重译判分命中：.codex_tmp/judge_highvalue_flagged.json。
- 幂等/断点续跑(done 边表)；每 20% 汇报；完成后本地规则简查新英文报残留。
用法： python -m scripts.run_en_pass [--batch 12 --workers 10 --limit N --dry --resume]
"""
import sys, os, json, argparse, threading, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.connection import get_cursor
from video_pipeline import config
from scripts.translate_strings import system_prompt, SCHEMA
from scripts.en_rule_probe import CJK, EN_THOUSAND, MODELS, SUBJ_PAY, wan_dropped
from openai import OpenAI

DS = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL, timeout=120, max_retries=2)
MODEL = config.DEEPSEEK_MODEL
FLAGGED_JSON = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "judge_highvalue_flagged.json")
DONE = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "en_pass_done.txt")
CHECK = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "en_pass_residual.json")


def rule_flagged(cur):
    """扫既有英文，返回规则命中的 src_hash 集合(需覆盖重译)。"""
    cur.execute("SELECT s.src_hash, s.src_text zh, t.text en FROM translations t "
                "JOIN translation_src s ON s.src_hash=t.src_hash WHERE t.locale='en'")
    hit = set()
    for r in cur.fetchall():
        z, e = r["zh"] or "", r["en"] or ""
        if (CJK.search(e) or ("万" in z and EN_THOUSAND.search(e)) or (MODELS.search(e) and "模" not in z)
                or wan_dropped(z, e) or SUBJ_PAY.search(e) or "万" in z):
            hit.add(r["src_hash"])
    return hit


def build_worklist():
    with get_cursor() as cur:
        # 补缺
        cur.execute("SELECT s.src_hash, s.src_text FROM translation_src s "
                    "LEFT JOIN translations t ON t.src_hash=s.src_hash AND t.locale='en' WHERE t.src_hash IS NULL")
        missing = {r["src_hash"]: r["src_text"] for r in cur.fetchall()}
        # 规则命中
        rf = rule_flagged(cur)
        # 判分命中
        jf = set(json.load(open(FLAGGED_JSON, encoding="utf-8"))) if os.path.exists(FLAGGED_JSON) else set()
        reflag = (rf | jf) - set(missing)  # 缺口不重复计
        texts = dict(missing)
        if reflag:
            ids = list(reflag)
            for i in range(0, len(ids), 1000):
                chunk = ids[i:i+1000]
                ph = ",".join(["%s"]*len(chunk))
                cur.execute(f"SELECT src_hash, src_text FROM translation_src WHERE src_hash IN ({ph})", chunk)
                for r in cur.fetchall():
                    texts[r["src_hash"]] = r["src_text"]
    print(f"工作集：补缺 {len(missing):,} + 重译(规则 {len(rf):,}∪判分 {len(jf):,} 去缺口后 {len(reflag):,}) "
          f"= 合计 {len(texts):,}")
    return list(texts.items())  # [(src_hash, src_text)]


def translate_ds(texts):
    user = ("Translate these strings (JSON array) and return {\"t\": [...]} with the same length:\n"
            + json.dumps(texts, ensure_ascii=False))
    resp = DS.chat.completions.create(model=MODEL, max_tokens=4000, timeout=120,
        messages=[{"role": "system", "content": system_prompt("English", "en")},
                  {"role": "user", "content": user}],
        response_format={"type": "json_object"})
    t = json.loads(resp.choices[0].message.content).get("t", [])
    if len(t) != len(texts):
        raise ValueError(f"len {len(t)}!={len(texts)}")
    return t


def translate_robust(pairs):
    """pairs:[(hash,text)] -> [(hash, en|None)]，批失败拆半重试到单条。"""
    try:
        out = translate_ds([p[1] for p in pairs])
        return [(h, o) for (h, _), o in zip(pairs, out)]
    except Exception:
        if len(pairs) == 1:
            try:
                return [(pairs[0][0], translate_ds([pairs[0][1]])[0])]
            except Exception:
                return [(pairs[0][0], None)]
        mid = len(pairs)//2
        return translate_robust(pairs[:mid]) + translate_robust(pairs[mid:])


def run(batch, workers, limit, dry, resume):
    work = build_worklist()
    if limit:
        work = work[:limit]
    done = set()
    if resume and os.path.exists(DONE):
        done = set(l.strip() for l in open(DONE, encoding="utf-8") if l.strip())
        work = [w for w in work if w[0] not in done]
        print(f"[resume] 已完成 {len(done):,}，剩 {len(work):,}")
    N = len(work)
    print(f"本次待翻译 {N:,} 条 (model={MODEL}, dry={dry})")
    if dry or N == 0:
        return
    os.makedirs(os.path.dirname(DONE), exist_ok=True)
    if not resume:
        open(DONE, "w").close()
    lock = threading.Lock(); cnt = [0]; t0 = time.time(); marks = {int(N*p/100) for p in (20, 40, 60, 80, 100)}

    def work_batch(pairs):
        res = translate_robust(pairs)
        rows = [(h, "en", en, MODEL) for h, en in res if en]
        with lock:
            with get_cursor() as cur:
                cur.executemany(
                    "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", rows)
            with open(DONE, "a", encoding="utf-8") as fh:
                for h, en in res:
                    if en: fh.write(h + "\n")
            cnt[0] += len(res)
            for m in sorted(marks):
                if cnt[0] >= m and m > 0:
                    marks.discard(m)
                    dt = time.time()-t0
                    print(f"PROGRESS {cnt[0]/N*100:.0f}%  {cnt[0]:,}/{N:,}  {dt:.0f}s  "
                          f"{cnt[0]/dt:.1f} 串/秒  ETA {(N-cnt[0])/(cnt[0]/dt)/60:.0f}min", flush=True)

    batches = [work[i:i+batch] for i in range(0, N, batch)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(as_completed([ex.submit(work_batch, b) for b in batches]))
    print(f"翻译完成，用时 {time.time()-t0:.0f}s，写入 {cnt[0]:,}")
    local_check([w[0] for w in work])


def local_check(hashes):
    """本地规则简查新写入的英文，报残留系统性问题。"""
    hs = set(hashes)
    with get_cursor() as cur:
        cur.execute("SELECT s.src_hash, s.src_text zh, t.text en FROM translations t "
                    "JOIN translation_src s ON s.src_hash=t.src_hash WHERE t.locale='en'")
        rows = [r for r in cur.fetchall() if r["src_hash"] in hs]
    res = {"cjk": [], "wan_thousand": [], "wan_drop": [], "models": [], "pay": []}
    for r in rows:
        z, e = r["zh"] or "", r["en"] or ""
        if CJK.search(e): res["cjk"].append(r["src_hash"])
        if "万" in z and EN_THOUSAND.search(e): res["wan_thousand"].append(r["src_hash"])
        if wan_dropped(z, e): res["wan_drop"].append(r["src_hash"])
        if MODELS.search(e) and "模" not in z: res["models"].append(r["src_hash"])
        if SUBJ_PAY.search(e): res["pay"].append(r["src_hash"])
    json.dump({k: v for k, v in res.items()}, open(CHECK, "w"), ensure_ascii=False)
    print("\n===== 本地规则简查(新英文残留) =====")
    for k, v in res.items():
        print(f"  {k:14} {len(v)}")
    print(f"残留清单 -> {CHECK}（可二次重译）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=12)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    run(a.batch, a.workers, a.limit, a.dry, a.resume)
