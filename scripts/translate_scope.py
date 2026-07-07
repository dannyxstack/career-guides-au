# -*- coding: utf-8 -*-
"""限定国家范围的增量翻译：只翻「出现在指定国家职业里」的待翻源串。

用于按国家分批补译（例如先翻 6 国新增岗，暂缓 FR/ES 全量）。源串范围从
occupations.json 重建（含 CJK 的 zh 母本，与 collect_from_bundle 同口径），
与 DB translation_src ∩，再对每个目标语言取尚缺译文者，走现有 translate_batch
（后端优先级 百度 -> Azure -> DeepSeek），写入 translations（幂等）。

运行：
  PYTHONIOENCODING=utf-8 python -m scripts.translate_scope \
    --countries AU,CA,UK,DE,US,NZ --locales en,es,pt,vi,th,ms,id,zh-Hant,ja,de \
    --workers 8 --batch 20 [--dry]
"""
import sys, os, json, re, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import baidu_translate
from scripts.translate_strings import LANG_NAME, translate_batch

OCC_JSON = os.path.join(os.path.dirname(__file__), "..", "site", "src", "data", "occupations.json")
_CJK = re.compile(r"[一-鿿]")
_print_lock = threading.Lock()


def log(m):
    with _print_lock:
        print(m, flush=True)


def in_scope_src(countries):
    """从 occupations.json 收集指定国家职业里所有含 CJK 的 zh 母本源串（去重集合）。"""
    occ = json.load(open(OCC_JSON, encoding="utf-8"))["occupations"]
    cc_set = set(countries)
    src = set()

    def add(s):
        if s and _CJK.search(s):
            src.add(s.strip())

    for o in occ:
        if o["country"] not in cc_set:
            continue
        z = o["i18n"].get("zh-CN", {})
        for k in ("name", "summary", "forecast_note", "trend_summary"):
            add(z.get(k))
        for s in o.get("salaries", []):
            add(s.get("label")); add(s.get("note"))
        for e in o.get("education", []):
            add(e.get("stage")); add(e.get("duration")); add(e.get("cost_note"))
        for q in o.get("qualifications", []):
            add(q.get("name")); add(q.get("issuer")); add(q.get("note"))
        for v in o.get("visa", []):
            add(v.get("name")); add(v.get("desc"))
        su = o.get("suitability", {})
        for x in (su.get("fit", []) + su.get("unfit", [])):
            add(x)
        for r in o.get("ratings", []):
            add(r.get("label_zh"))
        for f in o.get("faqs", []):
            add(f.get("question")); add(f.get("answer"))
        add(o.get("training_zh"))
        ai = o.get("ai") or {}
        add(ai.get("verdict_zh")); add(ai.get("entry_narrowing_zh")); add(ai.get("upgrade_path_zh"))
        for key in ("replaced_zh", "augmented_zh", "moat_zh", "skills_zh"):
            for x in (ai.get(key) or []):
                add(x)
        for d in (ai.get("disruptors") or []):
            add(d.get("summary_zh")); add(d.get("scope_zh"))
    src.discard("")
    return src


def pending(loc, scope):
    """该 locale 尚缺译文、且在 scope 内的 (src_hash, src_text)。"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT s.src_hash, s.src_text FROM translation_src s "
            "LEFT JOIN translations t ON t.src_hash=s.src_hash AND t.locale=%s "
            "WHERE t.src_hash IS NULL", (loc,))
        rows = cur.fetchall()
    return [r for r in rows if r["src_text"].strip() in scope]


def do_chunk(loc, chunk):
    texts = [r["src_text"] for r in chunk]
    try:
        res = translate_batch(texts, LANG_NAME[loc], loc)
    except Exception as e:
        if len(chunk) == 1:
            log(f"    单条失败跳过({e})")
            return 0
        mid = len(chunk) // 2
        return do_chunk(loc, chunk[:mid]) + do_chunk(loc, chunk[mid:])
    used = baidu_translate.MODEL_LABEL if baidu_translate.enabled() else "mt"
    rows = [(r["src_hash"], loc, t, used) for r, t in zip(chunk, res) if t]
    if rows:
        with get_cursor() as cur:
            cur.executemany(
                "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", rows)
    return len(rows)


def run(countries, locales, workers, batch, dry):
    scope = in_scope_src(countries)
    log(f"[scope] 国家={','.join(countries)} 范围内唯一源串 {len(scope):,}")
    units = []
    for loc in locales:
        todo = pending(loc, scope)
        log(f"[{loc}] 待翻 {len(todo):,}")
        for i in range(0, len(todo), batch):
            units.append((loc, todo[i:i + batch]))
    if dry:
        log("[dry] 只统计不翻译"); return
    total = sum(len(c) for _, c in units)
    done = [0]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(do_chunk, loc, ch): (loc, len(ch)) for loc, ch in units}
        for fu in as_completed(futs):
            n = fu.result()
            done[0] += n
            log(f"  进度 {done[0]:,}/{total:,}")
    log(f"[完成] 写入 {done[0]:,} 条译文")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", required=True)
    ap.add_argument("--locales", default="en,es,pt,vi,th,ms,id,zh-Hant,ja,de")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    run([x.strip() for x in a.countries.split(",") if x.strip()],
        [x.strip() for x in a.locales.split(",") if x.strip()],
        a.workers, a.batch, a.dry)
