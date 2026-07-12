# -*- coding: utf-8 -*-
"""第①步：分层抽样英文译文 + DeepSeek 语义质检。

产出：
- 逐条判定 JSONL（.codex_tmp/en_audit_raw.jsonl，增量写，可断点续跑）
- 汇总：按类别/严重度/分层的错误率 + 每类样例（用于人工提炼"修复规则表"）

分层：
  A 数值层  = 含「万」或数字区间的串（系统性数值错误富集）
  B 通用层  = 全量随机（无偏长尾语义错误率）
类别枚举（映射 系统性 / 语义 / 轻微）：
  ok / number_unit / term_missing / cjk_leftover / desinify_fail   # ok + 系统性
  omission / mistranslation                                        # 语义（规则抓不到）
  fluency                                                          # 轻微
用法： python -m scripts.audit_en_quality --a 2500 --b 7500 --batch 15 --workers 8 [--limit N]
"""
import sys, os, json, argparse, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.connection import get_cursor
from video_pipeline import config
from openai import OpenAI

RAW = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "en_audit_raw.jsonl")
CATS = ["ok", "number_unit", "term_missing", "cjk_leftover", "desinify_fail",
        "omission", "mistranslation", "fluency"]
SYSTEMATIC = {"number_unit", "term_missing", "cjk_leftover", "desinify_fail"}
SEMANTIC = {"omission", "mistranslation"}

SYS_PROMPT = (
    "You are a strict bilingual QA reviewer for an Australian careers/immigration website. "
    "For each item you are given a Simplified Chinese SOURCE (zh) and its English translation (en). "
    "Judge whether the English faithfully and accurately conveys the Chinese, for a GENERAL international audience.\n"
    "Return JSON: {\"r\":[{\"i\":<int>,\"category\":<str>,\"severity\":\"major|minor|none\",\"note\":<short str>}]}, "
    "same length and order as input.\n"
    "category MUST be one of: ok, number_unit, term_missing, cjk_leftover, desinify_fail, omission, mistranslation, fluency.\n"
    "Definitions:\n"
    "- ok: faithful and natural, no issue.\n"
    "- number_unit: any number, unit (esp. Chinese 万=10,000), range, percentage or currency amount is WRONG or dropped. "
    "e.g. '8~12万澳元' must be ~80,000-120,000, not 8-12,000.\n"
    "- term_missing: a proper noun/code that must be kept (ANZSCO, visa subclass numbers like 189/190/482, MLTSSL, TAFE, "
    "AHPRA, ACS, VETASSESS, JSA, ABS, org names) is missing or mangled in the English.\n"
    "- cjk_leftover: English still contains Chinese characters, or is left partly/fully untranslated.\n"
    "- desinify_fail: English still explicitly targets 'Chinese/华人/Mandarin community' framing that should have been neutralised.\n"
    "- omission: a meaningful clause or fact present in zh is missing from en (not numbers/terms — those are above).\n"
    "- mistranslation: the meaning/word-sense is wrong or reversed.\n"
    "- fluency: meaning is correct but English is awkward/unnatural.\n"
    "Pick the SINGLE most important issue per item; use 'ok' with severity 'none' if fine. Keep note under 12 words. "
    "Output JSON only."
)


def fetch(cur, where_extra, n):
    cur.execute(
        "SELECT s.src_hash, s.src_text zh, s.field, t.text en "
        "FROM translation_src s JOIN translations t ON t.src_hash=s.src_hash AND t.locale='en' "
        f"WHERE 1=1 {where_extra} ORDER BY RAND() LIMIT %s", (n,))
    return cur.fetchall()


def sample(a, b):
    num_where = "AND (s.src_text LIKE '%%万%%' OR s.src_text REGEXP '[0-9][~～-][0-9]')"
    with get_cursor() as cur:
        A = fetch(cur, num_where, a)
        seen = {r["src_hash"] for r in A}
        B = fetch(cur, "", b + len(A))  # 多取些，去掉与 A 重叠
    B = [r for r in B if r["src_hash"] not in seen][:b]
    for r in A: r["stratum"] = "A_numeric"
    for r in B: r["stratum"] = "B_general"
    return A + B


def judge(client, batch):
    items = [{"i": j, "zh": r["zh"], "en": r["en"]} for j, r in enumerate(batch)]
    user = "Review these items (JSON) and return the r array:\n" + json.dumps(items, ensure_ascii=False)
    resp = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL, max_tokens=4000, timeout=120,
        messages=[{"role": "system", "content": SYS_PROMPT}, {"role": "user", "content": user}],
        response_format={"type": "json_object"})
    out = json.loads(resp.choices[0].message.content)
    r = out.get("r", [])
    if len(r) != len(batch):
        raise ValueError(f"len mismatch {len(r)}!={len(batch)}")
    res = []
    for x, src in zip(r, batch):
        cat = x.get("category") if x.get("category") in CATS else "ok"
        res.append({"src_hash": src["src_hash"], "field": src["field"], "stratum": src["stratum"],
                    "zh": src["zh"], "en": src["en"], "category": cat,
                    "severity": x.get("severity", "none"), "note": (x.get("note") or "")[:120]})
    return res


def run(a, b, batch, workers, limit):
    rows = sample(a, b)
    if limit:
        rows = rows[:limit]
    print(f"抽样 {len(rows)} 条（A数值 {sum(r['stratum']=='A_numeric' for r in rows)} / "
          f"B通用 {sum(r['stratum']=='B_general' for r in rows)}）")
    os.makedirs(os.path.dirname(RAW), exist_ok=True)
    open(RAW, "w").close()  # 清空重跑
    lock = threading.Lock()
    client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL,
                    timeout=120, max_retries=2)
    batches = [rows[i:i+batch] for i in range(0, len(rows), batch)]
    done = [0]; t0 = time.time()

    def work(bt):
        for attempt in range(2):
            try:
                return judge(client, bt)
            except Exception as e:
                if attempt == 1:
                    return [{"src_hash": r["src_hash"], "field": r["field"], "stratum": r["stratum"],
                             "zh": r["zh"], "en": r["en"], "category": "judge_error",
                             "severity": "none", "note": str(e)[:80]} for r in bt]

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(work, bt) for bt in batches]
        for f in as_completed(futs):
            res = f.result()
            with lock:
                with open(RAW, "a", encoding="utf-8") as fh:
                    for x in res:
                        fh.write(json.dumps(x, ensure_ascii=False) + "\n")
                done[0] += len(res)
                if done[0] % 300 < batch:
                    print(f"  {done[0]}/{len(rows)}  ({time.time()-t0:.0f}s)", flush=True)
    print(f"完成 {done[0]} 条，用时 {time.time()-t0:.0f}s。原始结果 -> {RAW}")
    summarize()


def summarize():
    from collections import Counter, defaultdict
    rows = [json.loads(l) for l in open(RAW, encoding="utf-8")]
    by_stratum = defaultdict(Counter)
    examples = defaultdict(list)
    for r in rows:
        by_stratum[r["stratum"]][r["category"]] += 1
        if r["category"] not in ("ok", "judge_error") and len(examples[r["category"]]) < 8:
            examples[r["category"]].append(r)
    print("\n===== 汇总（按分层 × 类别）=====")
    for st, c in by_stratum.items():
        tot = sum(c.values())
        sysn = sum(c[k] for k in SYSTEMATIC); semn = sum(c[k] for k in SEMANTIC)
        print(f"\n[{st}] n={tot}")
        print(f"  ok={c['ok']} ({c['ok']/tot*100:.1f}%) | 系统性={sysn} ({sysn/tot*100:.1f}%) | "
              f"语义={semn} ({semn/tot*100:.1f}%) | fluency={c['fluency']} | judge_error={c['judge_error']}")
        for cat in CATS:
            if c[cat] and cat != "ok":
                print(f"    {cat:16} {c[cat]:>4} ({c[cat]/tot*100:.1f}%)")
    print("\n===== 各类样例（供提炼修复规则表）=====")
    for cat in [c for c in CATS if c not in ("ok",)] + ["judge_error"]:
        if examples.get(cat):
            print(f"\n--- {cat} ---")
            for e in examples[cat][:6]:
                print(f"  zh: {e['zh'][:70]}")
                print(f"  en: {e['en'][:90]}")
                print(f"  ↳ [{e['severity']}] {e['note']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=int, default=2500)
    ap.add_argument("--b", type=int, default=7500)
    ap.add_argument("--batch", type=int, default=15)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--summarize-only", action="store_true")
    x = ap.parse_args()
    if x.summarize_only:
        summarize()
    else:
        run(x.a, x.b, x.batch, x.workers, x.limit)
