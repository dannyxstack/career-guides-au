"""i18n 共享逻辑：培训摘要派生 + 可翻译字段提取。
collect_strings.py（采集源串）与 export_site_data.py（导出+解析）共用，避免逻辑分叉。

约定：
- 仅含 CJK 字符的串才需翻译；纯英文/代码（ANZSCO、Skills in Demand、growth 关键词等）全语言保留原文。
- training_zh 为派生展示串（与前端旧 JS 逻辑一致），单独翻译整串。
"""
import json
import re

# --- 培训摘要派生（与 site/src/lib/data.ts 的 trainingSummary 等价）---
EDU_SKIP = re.compile(r"海外|互认|\bTRA\b|技能评估|资历评估|注册评估|Bridging|桥梁|可选|替代|移民|\bAHPRA\b|\bACS\b|英语能力|雅思|\bPTE\b")


def dur_months(d):
    if not d:
        return 0
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:[~\-](\d+(?:\.\d+)?))?\s*年", d)
    if m:
        return float(m.group(2) or m.group(1)) * 12
    m = re.search(r"(\d+)\s*(?:[~\-](\d+))?\s*个?月", d)
    if m:
        return float(m.group(2) or m.group(1))
    return 0


def dur_short(d):
    if not d:
        return ""
    m = re.search(r"\d+(?:\.\d+)?(?:[~\-]\d+(?:\.\d+)?)?\s*年", d)
    if m:
        return re.sub(r"\s+", "", m.group(0))
    m = re.search(r"\d+(?:[~\-]\d+)?\s*个?月", d)
    if m:
        return re.sub(r"\s+", "", m.group(0))
    return d[:10] if len(d) > 10 else d


def edu_label(stage):
    s = re.sub(r"[（(][^)）]*[)）]", "", stage or "").strip()
    zh = re.sub(r"^[或、，,]+", "", re.sub(r"\s+", "", re.sub(r"[a-zA-Z0-9/.&'+\-]", "", s)))
    return zh if len(zh) >= 2 else s.split("/")[0].strip()


def training_summary(education):
    """education: list of dict(stage, duration) -> 中文展示串。"""
    if not education:
        return ""
    core = [e for e in education if not EDU_SKIP.search(e.get("stage") or "")]
    pool = core or education
    pick = [e for e in pool if dur_months(e.get("duration")) >= 12][:2]
    if not pick:
        pick = pool[:1]
    return " + ".join((edu_label(e["stage"]) + " " + dur_short(e.get("duration"))).strip() for e in pick)


# --- 可翻译串提取 ---
_CJK = re.compile(r"[一-鿿]")


def needs_translation(s):
    return bool(s and _CJK.search(s))


def collect_from_bundle(b):
    """b: 一个职业的聚合 dict（见 export 的结构）。yield (field, text)。
    只产出含 CJK 的串；growth_areas 与签证 subclass 等不产出。"""
    z = b["i18n_zh"]
    for k in ("name", "summary", "forecast_note", "trend_summary"):
        yield k, z.get(k)
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
        yield "rating_label", r.get("label_zh")
    for f in b["faqs"]:
        yield "faq_q", f.get("question")
        yield "faq_a", f.get("answer")
    yield "training", b.get("training_zh")
    ai = b.get("ai")
    if ai:
        yield "ai_verdict", ai.get("verdict_zh")
        yield "ai_entry", ai.get("entry_narrowing_zh")
        yield "ai_upgrade", ai.get("upgrade_path_zh")
        for key in ("replaced_zh", "augmented_zh", "moat_zh", "skills_zh"):
            for x in (ai.get(key) or []):
                yield "ai_list", x
        for d in (ai.get("disruptors") or []):
            yield "ai_disruptor_summary", d.get("summary_zh")
            yield "ai_disruptor_scope", d.get("scope_zh")


def _rows(cur, sql, oid):
    cur.execute(sql, (oid,))
    return cur.fetchall()


def fetch_bundles(cur, country=None):
    """读取职业的原始中文母本（zh-CN），返回 bundle 列表。
    country=None 表示所有国家；传国家码则只取该国。export 与 collect 共用，保证字段一致。"""
    if country:
        cur.execute("SELECT * FROM occupations WHERE country_code=%s ORDER BY category, id", (country,))
    else:
        cur.execute("SELECT * FROM occupations ORDER BY country_code, category, id")
    occs = cur.fetchall()
    bundles = []
    for o in occs:
        oid = o["id"]
        cur.execute("SELECT locale,name,summary,forecast_note,trend_summary FROM occupations_i18n WHERE occupation_id=%s", (oid,))
        i18n = {r["locale"]: r for r in cur.fetchall()}
        education = [{"stage": r["stage"], "duration": r["duration"], "cost_min": r["cost_min"],
                     "cost_max": r["cost_max"], "cost_note": r["cost_note"]}
                    for r in _rows(cur, "SELECT stage,duration,cost_min,cost_max,cost_note FROM occupation_education WHERE occupation_id=%s ORDER BY sort_order", oid)]
        salaries = [{"label": r["experience"], "min": r["salary_min"], "max": r["salary_max"], "note": r["salary_note"]}
                    for r in _rows(cur, "SELECT experience,salary_min,salary_max,salary_note FROM occupation_salaries WHERE occupation_id=%s ORDER BY sort_order", oid)]
        quals = [{"name": r["qual_name"], "issuer": r["issuer"], "note": r["note"], "mandatory": bool(r["is_mandatory"])}
                 for r in _rows(cur, "SELECT qual_name,issuer,note,is_mandatory FROM occupation_qualifications WHERE occupation_id=%s ORDER BY is_mandatory DESC,sort_order", oid)]
        visa = [{"subclass": r["visa_subclass"], "name": r["visa_name"], "desc": r["description"]}
                for r in _rows(cur, "SELECT visa_subclass,visa_name,description FROM occupation_visa_pathways WHERE occupation_id=%s ORDER BY sort_order", oid)]
        suit = _rows(cur, "SELECT type,item FROM occupation_suitability WHERE occupation_id=%s ORDER BY type,sort_order", oid)
        ratings = [{"dimension": r["dimension"], "label_zh": r["label_zh"],
                    "stars": float(r["stars"]) if r["stars"] is not None else None}
                   for r in _rows(cur, "SELECT dimension,label_zh,stars FROM occupation_ratings WHERE occupation_id=%s", oid)]
        cur.execute("SELECT f.id faq_id,f.faq_type,fi.question,fi.answer FROM occupation_faqs f JOIN occupation_faqs_i18n fi ON fi.faq_id=f.id AND fi.locale='zh-CN' WHERE f.occupation_id=%s ORDER BY f.sort_order", (oid,))
        faqs = [{"faq_id": r["faq_id"], "type": r["faq_type"], "question": r["question"], "answer": r["answer"]} for r in cur.fetchall()]
        ga = o["growth_areas"]
        growth = json.loads(ga) if isinstance(ga, str) else (ga or [])
        cur.execute("SELECT * FROM occupation_ai WHERE occupation_id=%s", (oid,))
        air = cur.fetchone()
        ai = None
        if air:
            def _j(v):
                return json.loads(v) if isinstance(v, str) else (v or [])
            def _f(v):
                return float(v) if v is not None else None
            ai = {"verdict_type": air["verdict_type"], "verdict_zh": air["verdict_zh"],
                  "entry_narrowing_zh": air["entry_narrowing_zh"],
                  "upgrade_path_zh": air.get("upgrade_path_zh"),
                  "cluster": air.get("cluster"),
                  "automation_exposure": _f(air.get("automation_exposure")),
                  "human_moat": _f(air.get("human_moat")),
                  "entry_risk": _f(air.get("entry_risk")),
                  "ai_upside": _f(air.get("ai_upside")),
                  "replaced_zh": _j(air["replaced_zh"]), "augmented_zh": _j(air["augmented_zh"]),
                  "moat_zh": _j(air["moat_zh"]), "skills_zh": _j(air["skills_zh"]),
                  "adjacent": _j(air["adjacent"])}
            cur.execute(
                "SELECT d.id,d.name,d.type,d.vendor,d.url,d.year,d.maturity,d.summary_zh,"
                "l.replacement_level,l.scope_zh,l.evidence_url "
                "FROM occupation_ai_disruptor l JOIN ai_disruptors d ON d.id=l.disruptor_id "
                "WHERE l.occupation_id=%s ORDER BY l.sort_order,d.year", (oid,))
            ai["disruptors"] = [
                {"id": r["id"], "name": r["name"], "type": r["type"], "vendor": r["vendor"],
                 "url": r["url"], "year": r["year"], "maturity": r["maturity"],
                 "summary_zh": r["summary_zh"], "level": r["replacement_level"],
                 "scope_zh": r["scope_zh"], "evidence_url": r["evidence_url"]}
                for r in cur.fetchall()]
        bundles.append({
            "ai": ai,
            "o": o, "id": oid, "i18n": i18n, "i18n_zh": i18n.get("zh-CN") or {},
            "education": education, "salaries": salaries, "qualifications": quals, "visa": visa,
            "suitability_fit": [s["item"] for s in suit if s["type"] == "fit"],
            "suitability_unfit": [s["item"] for s in suit if s["type"] == "unfit"],
            "ratings": ratings, "faqs": faqs, "growth": growth,
            "training_zh": training_summary(education),
        })
    return bundles
