# -*- coding: utf-8 -*-
"""定向修复 run_en_pass 本地简查残留(cjk/万/pay)：加固 prompt 重译 → 写库 → 复查前后。
只处理 .codex_tmp/en_pass_residual.json 里的 src_hash 集合。"""
import sys, os, json, time, threading
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.connection import get_cursor
from video_pipeline import config
from scripts.translate_strings import system_prompt
from scripts.en_rule_probe import CJK, EN_THOUSAND, MODELS, SUBJ_PAY, wan_dropped
from openai import OpenAI

DS = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL, timeout=120, max_retries=2)
MODEL = config.DEEPSEEK_MODEL
RES = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "en_pass_residual.json")

HARD = ("\nCRITICAL FIX RULES:\n"
        "- The output MUST contain ZERO Chinese characters. Translate EVERY character; if the source has "
        "stray fragments, render them in English.\n"
        "- Chinese '万' = ten-thousand (x10,000). '3万'=30,000; '3-4万'=30,000-40,000; '1.5万'=15,000. "
        "NEVER translate 万 as 'thousand' and NEVER drop the factor.\n"
        "- For tuition/fees, schools/universities/colleges do NOT 'pay'; use 'costs' / 'tuition is about'.")


def detectors(z, e):
    d = []
    if CJK.search(e): d.append("cjk")
    if "万" in z and EN_THOUSAND.search(e): d.append("wan_thousand")
    if wan_dropped(z, e): d.append("wan_drop")
    if MODELS.search(e) and "模" not in z: d.append("models")
    if SUBJ_PAY.search(e): d.append("pay")
    return d


def load_targets():
    res = json.load(open(RES, encoding="utf-8"))
    hashes = set()
    for v in res.values(): hashes.update(v)
    ids = list(hashes)
    rows = []
    with get_cursor() as cur:
        for i in range(0, len(ids), 1000):
            ch = ids[i:i+1000]; ph = ",".join(["%s"]*len(ch))
            cur.execute(f"SELECT s.src_hash, s.src_text zh, t.text en FROM translations t "
                        f"JOIN translation_src s ON s.src_hash=t.src_hash "
                        f"WHERE t.locale='en' AND s.src_hash IN ({ph})", ch)
            rows.extend(cur.fetchall())
    return rows


def translate(texts):
    user = ("Translate these Chinese strings (JSON array) into English and return {\"t\": [...]} same length:\n"
            + json.dumps(texts, ensure_ascii=False))
    resp = DS.chat.completions.create(model=MODEL, max_tokens=3000, timeout=120,
        messages=[{"role": "system", "content": system_prompt("English", "en") + HARD},
                  {"role": "user", "content": user}],
        response_format={"type": "json_object"})
    t = json.loads(resp.choices[0].message.content).get("t", [])
    if len(t) != len(texts): raise ValueError("len")
    return t


def robust(pairs):
    try:
        out = translate([p["zh"] for p in pairs])
        return [(p["src_hash"], o) for p, o in zip(pairs, out)]
    except Exception:
        if len(pairs) == 1:
            try: return [(pairs[0]["src_hash"], translate([pairs[0]["zh"]])[0])]
            except Exception: return [(pairs[0]["src_hash"], None)]
        m = len(pairs)//2
        return robust(pairs[:m]) + robust(pairs[m:])


def main():
    rows = load_targets()
    before = {}
    for r in rows:
        for d in detectors(r["zh"] or "", r["en"] or ""): before[d] = before.get(d, 0)+1
    print(f"目标残留 {len(rows)} 条；修复前: {before}")
    # 重译
    lock = threading.Lock(); newmap = {}
    def w(batch):
        for h, en in robust(batch):
            if en:
                with lock: newmap[h] = en
    batches = [rows[i:i+8] for i in range(0, len(rows), 8)]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(as_completed([ex.submit(w, b) for b in batches]))
    # 写库
    with get_cursor() as cur:
        cur.executemany("INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,'en',%s,%s) "
                        "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)",
                        [(h, en, MODEL+"-hardfix") for h, en in newmap.items()])
    print(f"重译写入 {len(newmap)} 条，用时 {time.time()-t0:.0f}s")
    # 复查
    after = {}; still = []
    for r in rows:
        e = newmap.get(r["src_hash"], r["en"])
        ds = detectors(r["zh"] or "", e or "")
        for d in ds: after[d] = after.get(d, 0)+1
        if ds: still.append({"src_hash": r["src_hash"], "flags": ds, "zh": r["zh"][:60], "en": (e or "")[:80]})
    print(f"修复后: {after}")
    print(f"\n仍残留 {len(still)} 条（多为 wan_drop 假阳/难例）:")
    for s in still[:12]:
        print(f"  {s['flags']} zh:{s['zh']}")
        print(f"           en:{s['en']}")


if __name__ == "__main__":
    main()
