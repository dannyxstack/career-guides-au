"""i18n v2（英文母本）：读取 v2 表聚合职业 bundle + 抽取需翻译的英文串。
collect_strings_v2 与 export_site_data_v2 共用，保证字段一致。

约定：母本=英文；每个非空英文展示串都产出到 TM（目标语翻译时按语言各自保留专有名词/代码）。
纯代码/无字母串（visa_subclass、growth 关键词）不产出。
"""
import json
import re

_HAS_ALPHA = re.compile(r"[A-Za-z]")


def needs_translation(s):
    return bool(s and s.strip() and _HAS_ALPHA.search(s))


# --- 英文培训摘要派生（与前端展示一致的轻量版）---
def _dur_months_en(d):
    if not d:
        return 0
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:[-–~]\s*(\d+(?:\.\d+)?))?\s*year", d, re.I)
    if m:
        return float(m.group(2) or m.group(1)) * 12
    m = re.search(r"(\d+)\s*(?:[-–~]\s*(\d+))?\s*month", d, re.I)
    if m:
        return float(m.group(2) or m.group(1))
    return 0


def training_summary_en(education):
    if not education:
        return ""
    pick = [e for e in education if _dur_months_en(e.get("duration")) >= 12][:2] or education[:1]
    parts = []
    for e in pick:
        stage = re.sub(r"\s*\([^)]*\)", "", e.get("stage") or "").strip()
        dur = (e.get("duration") or "").strip()
        parts.append((stage + (" " + dur if dur else "")).strip())
    return " + ".join(p for p in parts if p)


def collect_from_bundle(b):
    """yield (field, english_text)；只产非空含字母英文串。"""
    t = b["text"]
    for k in ("name", "summary", "forecast_note", "trend_summary"):
        yield k, t.get(k)
    for s in b["salaries"]:
        yield "salary_label", s.get("label")
        yield "salary_note", s.get("note")
    for e in b["education"]:
        yield "edu_stage", e.get("stage")
        yield "edu_duration", e.get("duration")
        yield "edu_cost_note", e.get("cost_note")
    for q in b["qualifications"]:
        yield "qual_name", q.get("name")
        yield "qual_issuer", q.get("issuer")
        yield "qual_note", q.get("note")
    for v in b["visa"]:
        yield "visa_name", v.get("name")
        yield "visa_desc", v.get("desc")
    for x in b["suitability_fit"] + b["suitability_unfit"]:
        yield "suitability", x
    for r in b["ratings"]:
        yield "rating_label", r.get("label")
    for f in b["faqs"]:
        yield "faq_q", f.get("question")
        yield "faq_a", f.get("answer")
    yield "training", b.get("training_en")
    for g in (b.get("growth") or []):
        yield "growth", g
    ai = b.get("ai")
    if ai:
        yield "ai_verdict", ai.get("verdict")
        yield "ai_entry", ai.get("entry_narrowing")
        yield "ai_upgrade", ai.get("upgrade_path")
        for key in ("replaced", "augmented", "moat", "skills"):
            for x in (ai.get(key) or []):
                yield "ai_list", x
        for d in (ai.get("disruptors") or []):
            yield "ai_disruptor_summary", d.get("summary")
            yield "ai_disruptor_scope", d.get("scope")


def _rows(cur, sql, oid):
    cur.execute(sql, (oid,))
    return cur.fetchall()


def fetch_bundles(cur, country=None):
    """读取 v2 英文母本，返回 bundle 列表。country=None 取全部。"""
    if country:
        cur.execute("SELECT * FROM occupations WHERE country_code=%s ORDER BY category, id", (country,))
    else:
        cur.execute("SELECT * FROM occupations ORDER BY country_code, category, id")
    occs = cur.fetchall()
    bundles = []
    for o in occs:
        oid = o["id"]
        cur.execute("SELECT name,summary,forecast_note,trend_summary FROM occupations_text_v2 WHERE occupation_id=%s", (oid,))
        text = cur.fetchone()
        if not text:
            continue  # 未迁入 v2 的职业跳过（旧数据尚未迁移）
        education = [{"stage": r["stage"], "duration": r["duration"], "cost_min": r["cost_min"],
                     "cost_max": r["cost_max"], "cost_note": r["cost_note"]}
                    for r in _rows(cur, "SELECT stage,duration,cost_min,cost_max,cost_note FROM occupation_education_v2 WHERE occupation_id=%s ORDER BY sort_order", oid)]
        salaries = [{"label": r["experience"], "min": r["salary_min"], "max": r["salary_max"],
                     "note": r["salary_note"], "currency": r["currency"]}
                    for r in _rows(cur, "SELECT experience,salary_min,salary_max,salary_note,currency FROM occupation_salaries_v2 WHERE occupation_id=%s ORDER BY sort_order", oid)]
        quals = [{"name": r["qual_name"], "issuer": r["issuer"], "note": r["note"], "mandatory": bool(r["is_mandatory"])}
                 for r in _rows(cur, "SELECT qual_name,issuer,note,is_mandatory FROM occupation_qualifications_v2 WHERE occupation_id=%s ORDER BY is_mandatory DESC,sort_order", oid)]
        visa = [{"subclass": r["visa_subclass"], "name": r["visa_name"], "desc": r["description"]}
                for r in _rows(cur, "SELECT visa_subclass,visa_name,description FROM occupation_visa_v2 WHERE occupation_id=%s ORDER BY sort_order", oid)]
        suit = _rows(cur, "SELECT type,item FROM occupation_suitability_v2 WHERE occupation_id=%s ORDER BY type,sort_order", oid)
        ratings = [{"dimension": r["dimension"], "label": r["label"],
                    "stars": float(r["stars"]) if r["stars"] is not None else None}
                   for r in _rows(cur, "SELECT dimension,label,stars FROM occupation_ratings_v2 WHERE occupation_id=%s", oid)]
        faqs = [{"faq_id": r["id"], "type": r["faq_type"], "question": r["question"], "answer": r["answer"]}
                for r in _rows(cur, "SELECT id,faq_type,question,answer FROM occupation_faqs_v2 WHERE occupation_id=%s ORDER BY sort_order", oid)]
        ga = o["growth_areas"]
        growth = json.loads(ga) if isinstance(ga, str) else (ga or [])
        cur.execute("SELECT * FROM occupation_ai_v2 WHERE occupation_id=%s", (oid,))
        air = cur.fetchone()
        ai = None
        if air:
            def _j(v):
                return json.loads(v) if isinstance(v, str) else (v or [])
            def _f(v):
                return float(v) if v is not None else None
            ai = {"verdict_type": air["verdict_type"], "verdict": air["verdict"],
                  "entry_narrowing": air["entry_narrowing"], "upgrade_path": air.get("upgrade_path"),
                  "cluster": air.get("cluster"), "automation_exposure": _f(air.get("automation_exposure")),
                  "human_moat": _f(air.get("human_moat")), "entry_risk": _f(air.get("entry_risk")),
                  "ai_upside": _f(air.get("ai_upside")), "aioe_score": _f(air.get("aioe_score")),
                  "aioe_pct": (int(air["aioe_pct"]) if air.get("aioe_pct") is not None else None),
                  "aioe_soc": air.get("aioe_soc"), "aioe_method": air.get("aioe_method"),
                  "replaced": _j(air["replaced"]), "augmented": _j(air["augmented"]),
                  "moat": _j(air["moat"]), "skills": _j(air["skills"]), "adjacent": _j(air["adjacent"])}
            cur.execute(
                "SELECT d.id,d.name,d.type,d.vendor,d.url,d.year,d.maturity,d.summary,"
                "l.replacement_level,l.scope,l.evidence_url "
                "FROM occupation_ai_disruptor_v2 l JOIN ai_disruptors_v2 d ON d.id=l.disruptor_id "
                "WHERE l.occupation_id=%s ORDER BY l.sort_order,d.year", (oid,))
            ai["disruptors"] = [
                {"id": r["id"], "name": r["name"], "type": r["type"], "vendor": r["vendor"], "url": r["url"],
                 "year": r["year"], "maturity": r["maturity"], "summary": r["summary"],
                 "level": r["replacement_level"], "scope": r["scope"], "evidence_url": r["evidence_url"]}
                for r in cur.fetchall()]
        bundles.append({
            "ai": ai, "o": o, "id": oid, "text": text,
            "education": education, "salaries": salaries, "qualifications": quals, "visa": visa,
            "suitability_fit": [s["item"] for s in suit if s["type"] == "fit"],
            "suitability_unfit": [s["item"] for s in suit if s["type"] == "unfit"],
            "ratings": ratings, "faqs": faqs, "growth": growth,
            "training_en": training_summary_en(education),
        })
    return bundles
