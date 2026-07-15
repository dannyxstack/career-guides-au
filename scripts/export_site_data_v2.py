"""导出 v2 英文母本数据为新 JSON（不覆盖旧文件，写 *_v2 命名，供前端硬切时切换）。
产物：occupations_v2.json / occ-detail-v2/{cc}.json / translations-v2/{loc}.{i}.json / categories_v2.json
i18n 母本=英文；其余语言前端经 tr(英文) 解析（键为英文源串）。
运行：python -m scripts.export_site_data_v2
"""
import sys, os, json, re, hashlib, glob
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._i18n_fields_v2 import fetch_bundles

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "src", "data")
N_TR_SHARDS = 8
POLARITY = {"income_level": 1, "job_demand": 1, "future_prospect": 1, "pr_friendliness": 1,
            "ai_risk": -1, "learning_difficulty": -1, "learning_duration": -1,
            "certification_difficulty": -1, "competition": -1, "work_intensity": -1, "pr_difficulty": -1}
AVG_LABELS = {"average salary", "average", "mean", "avg salary"}


def _ai_legacy(ai):
    """把 v2 的英文命名 ai 字段重映射为前端沿用的旧键名（*_zh 现装英文母本，过渡期不改前端）。"""
    if not ai:
        return None
    a = dict(ai)
    a["verdict_zh"] = a.pop("verdict", None)
    a["entry_narrowing_zh"] = a.pop("entry_narrowing", None)
    a["upgrade_path_zh"] = a.pop("upgrade_path", None)
    a["replaced_zh"] = a.pop("replaced", [])
    a["augmented_zh"] = a.pop("augmented", [])
    a["moat_zh"] = a.pop("moat", [])
    a["skills_zh"] = a.pop("skills", [])
    for d in (a.get("disruptors") or []):
        d["scope_zh"] = d.pop("scope", None)
        d["summary_zh"] = d.pop("summary", None)
    return a


def slug(name):
    s = re.sub(r"[/()\[\]]", " ", (name or "occ").lower())
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", "-", s.strip()) or "occ"


def overall_score(ratings):
    vals = []
    for r in ratings:
        if r["stars"] is None:
            continue
        s = float(r["stars"])
        vals.append(12 - s if POLARITY.get(r["dimension"], 1) < 0 else s)
    return round(sum(vals) / len(vals), 1) if vals else None


def build():
    with get_cursor() as cur:
        bundles = fetch_bundles(cur)
        inv = {}
        try:
            cur.execute("SELECT occupation_id, visa_subclass, min_score, asof, note FROM occupation_invitation_scores")
            for r in cur.fetchall():
                inv.setdefault(r["occupation_id"], {})[r["visa_subclass"]] = {"min_score": r["min_score"], "asof": r["asof"]}
        except Exception as e:
            print(f"[export_v2] 警告：invitation_scores 跳过（{e}）")
        out = []
        for b in bundles:
            o = b["o"]
            t = b["text"]
            en_name = t.get("name") or o["anzsco_title"]
            sg = slug(en_name)
            ratings = [{"dimension": r["dimension"], "stars": r["stars"]} for r in b["ratings"]]
            out.append({
                "id": b["id"], "country": o["country_code"], "occ_code": o["occ_code"],
                "occ_code_type": o["occ_code_type"], "anzsco_code": o["anzsco_code"],
                "category": o["category"], "currency": o.get("currency") or "AUD",
                "is_migration": int(o["is_migration"] or 0),
                "is_public_servant": bool(o.get("is_public_servant")),
                "shortage_listed": bool(o["shortage_listed"]), "workforce_size": o["workforce_size"],
                "slug": sg, "name_en": en_name, "growth_areas": b["growth"],
                # 母本=英文，但沿用旧键名（i18n['zh-CN'] / training_zh）装英文，前端零改动（过渡期）
                "i18n": {"zh-CN": {"name": t.get("name"), "summary": t.get("summary"),
                                   "forecast_note": t.get("forecast_note"), "trend_summary": t.get("trend_summary")}},
                "training_zh": b["training_en"],
                "salaries": [{"label": s["label"], "min": s["min"], "max": s["max"], "note": s["note"]} for s in b["salaries"]],
                "ratings": ratings, "overall_score": overall_score(ratings),
                "avg_salary": next((s["min"] for s in b["salaries"] if (s["label"] or "").strip().lower() in AVG_LABELS), None),
                "visa": [{**v, **({"min_score": inv[b["id"]][v["subclass"]]["min_score"],
                                   "score_asof": inv[b["id"]][v["subclass"]]["asof"]}
                                  if inv.get(b["id"], {}).get(v["subclass"]) else {})} for v in b["visa"]],
                "education": b["education"], "qualifications": b["qualifications"],
                "suitability": {"fit": b["suitability_fit"], "unfit": b["suitability_unfit"]},
                "faqs": [{"type": f["type"], "question": f["question"], "answer": f["answer"]} for f in b["faqs"]],
                "ai": _ai_legacy(b.get("ai")),
            })

        # 相邻职业 & disruptor also（同旧逻辑）
        code_map = {(o["country"], o["occ_code"]): o for o in out}
        for o in out:
            ai = o.get("ai")
            if not ai:
                continue
            ai["adjacent"] = [{"slug": tgt["slug"], "name_en": tgt["name_en"], "category": tgt["category"]}
                              for code in (ai.get("adjacent") or [])
                              for tgt in [code_map.get((o["country"], code))] if tgt]
        dis_occ = {}
        for o in out:
            for d in (o.get("ai") or {}).get("disruptors", []):
                dis_occ.setdefault((o["country"], d["id"]), []).append(o)
        for o in out:
            for d in (o.get("ai") or {}).get("disruptors", []):
                d["also"] = [{"slug": x["slug"], "name_en": x["name_en"], "category": x["category"]}
                             for x in dis_occ.get((o["country"], d["id"]), []) if x["id"] != o["id"]]
                d.pop("id", None)

        # 翻译记忆：{英文源串: {locale: text}}
        tr = {}
        try:
            cur.execute("SELECT s.src_text, t.locale, t.text FROM translations_v2 t JOIN translation_src_v2 s ON s.src_hash=t.src_hash")
            for r in cur.fetchall():
                tr.setdefault(r["src_text"], {})[r["locale"]] = r["text"]
        except Exception as e:
            print(f"[export_v2] 警告：translations_v2 跳过（{e}）")

    os.makedirs(OUT, exist_ok=True)
    # lean/detail 拆分（同旧）
    DETAIL_FIELDS = ["visa", "qualifications", "suitability", "faqs", "growth_areas"]
    AI_DETAIL = ["entry_narrowing_zh", "replaced_zh", "augmented_zh", "moat_zh", "skills_zh",
                 "upgrade_path_zh", "adjacent", "disruptors"]
    detail_by_country = {}
    for o in out:
        det = {k: o.pop(k) for k in DETAIL_FIELDS if k in o}
        ai = o.get("ai")
        if ai:
            det["ai"] = {k: ai.pop(k) for k in AI_DETAIL if k in ai}
        detail_by_country.setdefault(o["country"], {})[o["id"]] = det
    det_dir = os.path.join(OUT, "occ-detail-v2")
    os.makedirs(det_dir, exist_ok=True)
    for old in glob.glob(os.path.join(det_dir, "*.json")):
        os.remove(old)
    for cc, m in detail_by_country.items():
        with open(os.path.join(det_dir, f"{cc}.json"), "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, default=str)

    payload = {"generated_at": str(date.today()), "count": len(out), "master": "en", "occupations": out}
    with open(os.path.join(OUT, "occupations_v2.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, default=str)

    tr_dir = os.path.join(OUT, "translations-v2")
    os.makedirs(tr_dir, exist_ok=True)

    def _retry_io(fn, path, tries=6):
        # Windows 上 Defender 实时扫描会短暂锁住刚写出的大 JSON，导致 remove/open 报
        # PermissionError(WinError 5)。退避重试；删除类失败最终可容忍(写阶段用 'w' 覆盖)。
        import time as _t
        for k in range(tries):
            try:
                return fn()
            except PermissionError:
                if k == tries - 1:
                    raise
                _t.sleep(0.5 * (k + 1))

    for old in glob.glob(os.path.join(tr_dir, "*.json")):
        try:
            _retry_io(lambda: os.remove(old), old)
        except PermissionError:
            pass  # 文件名确定({loc}.{i}.json)，写阶段会覆盖；删不掉的留着无害
    by_locale = {}
    for src, locs in tr.items():
        for loc, text in locs.items():
            by_locale.setdefault(loc, {})[src] = text
    for loc, mp in by_locale.items():
        shards = [dict() for _ in range(N_TR_SHARDS)]
        for src, text in mp.items():
            h = int(hashlib.md5(src.encode("utf-8")).hexdigest(), 16) % N_TR_SHARDS
            shards[h][src] = text
        for i, sh in enumerate(shards):
            p = os.path.join(tr_dir, f"{loc}.{i}.json")
            def _w():
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(sh, f, ensure_ascii=False, default=str)
            _retry_io(_w, p)

    cats = sorted({o["category"] for o in out if o["category"]})
    with open(os.path.join(OUT, "categories_v2.json"), "w", encoding="utf-8") as f:
        json.dump({"category_slug": {c: slug(c) for c in cats}, "categories": cats}, f, ensure_ascii=False)

    print(f"[export_v2] {len(out)} occupations -> occupations_v2.json (detail×{len(detail_by_country)})")
    print(f"[export_v2] {len(tr)} 英文源串带译文 -> translations-v2/<loc>.<i>.json × {len(by_locale)} locale")
    print(f"[export_v2] {len(cats)} categories")


if __name__ == "__main__":
    build()
