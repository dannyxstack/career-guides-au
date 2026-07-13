"""英文母本 v2 入库通用函数。所有字段均为英文母本；非英文译文由 collect/translate 走新 TM 产生。
复用 occupations 主表（数值/代码），文本写入各 *_v2 表。幂等：按 (country_code, occ_code) 或 (country_code, anzsco_title) 定位。
"""
import json


def _occ_upsert(cur, OCC):
    country = OCC.get("country_code", "AU")
    occ_code = OCC.get("occ_code", OCC.get("anzsco_code", "")) or ""
    if occ_code:
        cur.execute("SELECT id FROM occupations WHERE country_code=%s AND occ_code=%s", (country, occ_code))
    else:
        cur.execute("SELECT id FROM occupations WHERE country_code=%s AND occ_code='' AND anzsco_title=%s",
                    (country, OCC["anzsco_title"]))
    row = cur.fetchone()
    ga = OCC.get("growth_areas")
    if not isinstance(ga, str):
        ga = json.dumps(ga or [], ensure_ascii=False)
    fields = (occ_code, OCC.get("occ_code_type", "ISCO08"), OCC.get("anzsco_code", "") or occ_code,
              OCC["anzsco_title"], OCC["category"], OCC.get("currency", "AUD"), OCC.get("workforce_size"),
              OCC.get("shortage_listed", 0), OCC.get("is_migration", 1), OCC.get("is_public_servant", 0), ga)
    if row:
        occ_id = row["id"]
        cur.execute("UPDATE occupations SET occ_code=%s,occ_code_type=%s,anzsco_code=%s,anzsco_title=%s,"
                    "category=%s,currency=%s,workforce_size=%s,shortage_listed=%s,is_migration=%s,"
                    "is_public_servant=%s,growth_areas=%s WHERE id=%s", fields + (occ_id,))
    else:
        cur.execute("INSERT INTO occupations (country_code,occ_code,occ_code_type,anzsco_code,anzsco_title,"
                    "category,currency,workforce_size,shortage_listed,is_migration,is_public_servant,growth_areas) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (country,) + fields)
        occ_id = cur.lastrowid
    return occ_id


def seed_occupation_en(cur, OCC, TEXT, EDUCATION, QUALIFICATIONS, SALARIES, VISA,
                       RATINGS, FIT, UNFIT, FAQS, AI=None):
    """写 occupations 主表 + 全部 *_v2 英文母本表。返回 occ_id。"""
    occ_id = _occ_upsert(cur, OCC)
    currency = OCC.get("currency", "AUD")

    cur.execute("INSERT INTO occupations_text_v2 (occupation_id,name,summary,forecast_note,trend_summary) "
                "VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name),summary=VALUES(summary),"
                "forecast_note=VALUES(forecast_note),trend_summary=VALUES(trend_summary)",
                (occ_id, TEXT["name"], TEXT.get("summary"), TEXT.get("forecast_note"), TEXT.get("trend_summary")))

    cur.execute("DELETE FROM occupation_education_v2 WHERE occupation_id=%s", (occ_id,))
    for i, e in enumerate(EDUCATION):
        cur.execute("INSERT INTO occupation_education_v2 (occupation_id,stage,duration,cost_min,cost_max,cost_note,sort_order) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (occ_id, e["stage"], e.get("duration"), e.get("cost_min"), e.get("cost_max"),
                     e.get("cost_note"), e.get("sort_order", i)))

    cur.execute("DELETE FROM occupation_qualifications_v2 WHERE occupation_id=%s", (occ_id,))
    for i, q in enumerate(QUALIFICATIONS):
        cur.execute("INSERT INTO occupation_qualifications_v2 (occupation_id,qual_name,issuer,note,is_mandatory,sort_order) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    (occ_id, q["qual_name"], q.get("issuer"), q.get("note"), q.get("is_mandatory", 1), q.get("sort_order", i)))

    cur.execute("DELETE FROM occupation_salaries_v2 WHERE occupation_id=%s", (occ_id,))
    for i, s in enumerate(SALARIES):
        cur.execute("INSERT INTO occupation_salaries_v2 (occupation_id,experience,salary_min,salary_max,salary_note,currency,sort_order) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (occ_id, s["experience"], s.get("salary_min"), s.get("salary_max"), s.get("salary_note"),
                     s.get("currency", currency), s.get("sort_order", i)))

    cur.execute("DELETE FROM occupation_visa_v2 WHERE occupation_id=%s", (occ_id,))
    for i, v in enumerate(VISA):
        cur.execute("INSERT INTO occupation_visa_v2 (occupation_id,visa_subclass,visa_name,description,sort_order) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (occ_id, v["visa_subclass"], v.get("visa_name"), v.get("description"), v.get("sort_order", i)))

    cur.execute("DELETE FROM occupation_suitability_v2 WHERE occupation_id=%s", (occ_id,))
    for i, item in enumerate(FIT):
        cur.execute("INSERT INTO occupation_suitability_v2 (occupation_id,type,item,sort_order) VALUES(%s,'fit',%s,%s)", (occ_id, item, i))
    for i, item in enumerate(UNFIT):
        cur.execute("INSERT INTO occupation_suitability_v2 (occupation_id,type,item,sort_order) VALUES(%s,'unfit',%s,%s)", (occ_id, item, i))

    cur.execute("DELETE FROM occupation_ratings_v2 WHERE occupation_id=%s", (occ_id,))
    for r in RATINGS:
        cur.execute("INSERT INTO occupation_ratings_v2 (occupation_id,dimension,label,stars,note) VALUES (%s,%s,%s,%s,%s)",
                    (occ_id, r["dimension"], r["label"], r["stars"], r.get("note")))

    cur.execute("DELETE FROM occupation_faqs_v2 WHERE occupation_id=%s", (occ_id,))
    for i, f in enumerate(FAQS):
        cur.execute("INSERT INTO occupation_faqs_v2 (occupation_id,faq_type,question,answer,sort_order) VALUES (%s,%s,%s,%s,%s)",
                    (occ_id, f.get("faq_type"), f["question"], f["answer"], f.get("sort_order", i)))

    if AI:
        def _j(v):
            return json.dumps(v or [], ensure_ascii=False)
        cur.execute("INSERT INTO occupation_ai_v2 (occupation_id,verdict_type,verdict,entry_narrowing,upgrade_path,"
                    "replaced,augmented,moat,skills,adjacent,cluster,automation_exposure,human_moat,entry_risk,"
                    "ai_upside,aioe_score,aioe_pct,aioe_soc,aioe_method) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE verdict_type=VALUES(verdict_type),verdict=VALUES(verdict),"
                    "entry_narrowing=VALUES(entry_narrowing),upgrade_path=VALUES(upgrade_path),replaced=VALUES(replaced),"
                    "augmented=VALUES(augmented),moat=VALUES(moat),skills=VALUES(skills),adjacent=VALUES(adjacent)",
                    (occ_id, AI.get("verdict_type", "mixed"), AI.get("verdict"), AI.get("entry_narrowing"),
                     AI.get("upgrade_path"), _j(AI.get("replaced")), _j(AI.get("augmented")), _j(AI.get("moat")),
                     _j(AI.get("skills")), _j(AI.get("adjacent")), AI.get("cluster"), AI.get("automation_exposure"),
                     AI.get("human_moat"), AI.get("entry_risk"), AI.get("ai_upside"), AI.get("aioe_score"),
                     AI.get("aioe_pct"), AI.get("aioe_soc"), AI.get("aioe_method")))
    return occ_id
