"""
职业数据入库通用函数，供所有 seed_*.py 脚本调用。
"""
from datetime import date
TODAY = date.today()


def seed_occupation_v2(cur, OCC, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS,
                       JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS,
                       SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS):
    """新 schema 版：支持 is_migration、occ_code 可空（唯一键已放开为普通索引）。
    幂等：occ_code 非空按 (country_code, occ_code) 定位，否则按 (country_code, anzsco_title)。"""
    country = OCC.get("country_code", "AU")
    occ_code = OCC.get("occ_code", OCC.get("anzsco_code", "")) or ""
    if occ_code:
        cur.execute("SELECT id FROM occupations WHERE country_code=%s AND occ_code=%s",
                    (country, occ_code))
    else:
        cur.execute("SELECT id FROM occupations WHERE country_code=%s AND occ_code='' AND anzsco_title=%s",
                    (country, OCC["anzsco_title"]))
    row = cur.fetchone()
    fields = (occ_code, OCC.get("occ_code_type", "ANZSCO"), OCC.get("anzsco_code", ""),
              OCC["anzsco_title"], OCC["category"], OCC.get("currency", "AUD"),
              OCC.get("workforce_size"),
              OCC.get("shortage_listed", 0), OCC.get("is_migration", 1),
              OCC.get("is_public_servant", 0), OCC.get("growth_areas"))
    if row:
        occ_id = row["id"]
        cur.execute(
            "UPDATE occupations SET occ_code=%s, occ_code_type=%s, anzsco_code=%s, anzsco_title=%s, "
            "category=%s, currency=%s, workforce_size=%s, shortage_listed=%s, is_migration=%s, is_public_servant=%s, "
            "growth_areas=%s WHERE id=%s",
            fields + (occ_id,))
    else:
        cur.execute(
            "INSERT INTO occupations (country_code, occ_code, occ_code_type, anzsco_code, anzsco_title, "
            "category, currency, workforce_size, shortage_listed, is_migration, is_public_servant, growth_areas) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (country,) + fields)
        occ_id = cur.lastrowid
    print(f"[occupations] id={occ_id}  occ_code={occ_code or '(空)'}  is_migration={OCC.get('is_migration',1)}  {OCC['anzsco_title']}")

    for i18n in [I18N_ZH, I18N_EN]:
        cur.execute(
            "INSERT INTO occupations_i18n (occupation_id,locale,name,summary,forecast_note,trend_summary) "
            "VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name),summary=VALUES(summary),"
            "forecast_note=VALUES(forecast_note),trend_summary=VALUES(trend_summary)",
            (occ_id, i18n["locale"], i18n["name"], i18n["summary"], i18n["forecast_note"], i18n["trend_summary"]))

    cur.execute("DELETE FROM occupation_ratings WHERE occupation_id=%s", (occ_id,))
    for r in RATINGS:
        cur.execute("INSERT INTO occupation_ratings (occupation_id,dimension,label_zh,stars,note) VALUES (%s,%s,%s,%s,%s)",
                    (occ_id, r["dimension"], r["label_zh"], r["stars"], r.get("note")))
    cur.execute("DELETE FROM occupation_education WHERE occupation_id=%s", (occ_id,))
    for e in EDUCATION:
        cur.execute("INSERT INTO occupation_education (occupation_id,stage,duration,cost_min,cost_max,cost_note,sort_order) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (occ_id, e["stage"], e["duration"], e["cost_min"], e["cost_max"], e["cost_note"], e["sort_order"]))
    cur.execute("DELETE FROM occupation_qualifications WHERE occupation_id=%s", (occ_id,))
    for q in QUALIFICATIONS:
        cur.execute("INSERT INTO occupation_qualifications (occupation_id,qual_name,issuer,note,is_mandatory,sort_order) VALUES (%s,%s,%s,%s,%s,%s)",
                    (occ_id, q["qual_name"], q.get("issuer"), q.get("note"), q["is_mandatory"], q["sort_order"]))
    cur.execute("DELETE FROM occupation_job_listings WHERE occupation_id=%s", (occ_id,))
    for jl in JOB_LISTINGS:
        cur.execute("INSERT INTO occupation_job_listings (occupation_id,platform,count_min,count_max,note,snapshot_date) VALUES (%s,%s,%s,%s,%s,%s)",
                    (occ_id, jl["platform"], jl["count_min"], jl["count_max"], jl["note"], TODAY))
    cur.execute("DELETE FROM occupation_salaries WHERE occupation_id=%s", (occ_id,))
    for s in SALARIES:
        cur.execute("INSERT INTO occupation_salaries (occupation_id,experience,salary_min,salary_max,salary_note,sort_order,currency) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (occ_id, s["experience"], s["salary_min"], s["salary_max"], s["salary_note"], s["sort_order"], OCC.get("currency", "AUD")))
    cur.execute("DELETE FROM occupation_visa_pathways WHERE occupation_id=%s", (occ_id,))
    for v in VISA_PATHWAYS:
        cur.execute("INSERT INTO occupation_visa_pathways (occupation_id,visa_subclass,visa_name,description,sort_order) VALUES (%s,%s,%s,%s,%s)",
                    (occ_id, v["visa_subclass"], v["visa_name"], v["description"], v["sort_order"]))
    cur.execute("DELETE FROM occupation_suitability WHERE occupation_id=%s", (occ_id,))
    for i, item in enumerate(SUITABILITY_FIT):
        cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'fit',%s,%s)", (occ_id, item, i))
    for i, item in enumerate(SUITABILITY_UNFIT):
        cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'unfit',%s,%s)", (occ_id, item, i))
    cur.execute("DELETE FROM occupation_sources WHERE occupation_id=%s", (occ_id,))
    for s in SOURCES:
        cur.execute("INSERT INTO occupation_sources (occupation_id,source_name,content,url) VALUES (%s,%s,%s,%s)",
                    (occ_id, s["source_name"], s.get("content"), s.get("url")))
    cur.execute("DELETE FROM occupation_faqs WHERE occupation_id=%s", (occ_id,))
    for faq in FAQS:
        cur.execute("INSERT INTO occupation_faqs (occupation_id,faq_type,sort_order) VALUES(%s,%s,%s)",
                    (occ_id, faq["faq_type"], faq["sort_order"]))
        faq_id = cur.lastrowid
        cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'zh-CN',%s,%s) ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",
                    (faq_id, faq["question"], faq["answer"]))
    return occ_id

def seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN,
                    EDUCATION, QUALIFICATIONS, JOB_LISTINGS,
                    SALARIES, VISA_PATHWAYS, RATINGS,
                    SUITABILITY_FIT, SUITABILITY_UNFIT,
                    SOURCES, FAQS):
    cur.execute("""
        INSERT INTO occupations (anzsco_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          anzsco_title=VALUES(anzsco_title), category=VALUES(category),
          workforce_size=VALUES(workforce_size), shortage_listed=VALUES(shortage_listed),
          growth_areas=VALUES(growth_areas)
    """, (OCCUPATION["anzsco_code"], OCCUPATION["anzsco_title"], OCCUPATION["category"],
          OCCUPATION["workforce_size"], OCCUPATION["shortage_listed"], OCCUPATION["growth_areas"]))
    cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s", (OCCUPATION["anzsco_code"],))
    occ_id = cur.fetchone()["id"]
    print(f"[occupations] id={occ_id}  {OCCUPATION['anzsco_code']} {OCCUPATION['anzsco_title']}")

    for i18n in [I18N_ZH, I18N_EN]:
        cur.execute("""
            INSERT INTO occupations_i18n (occupation_id,locale,name,summary,forecast_note,trend_summary)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE name=VALUES(name),summary=VALUES(summary),
              forecast_note=VALUES(forecast_note),trend_summary=VALUES(trend_summary)
        """, (occ_id, i18n["locale"], i18n["name"], i18n["summary"], i18n["forecast_note"], i18n["trend_summary"]))
    print("[occupations_i18n] 2 locales")

    cur.execute("DELETE FROM occupation_ratings WHERE occupation_id=%s", (occ_id,))
    for r in RATINGS:
        cur.execute("INSERT INTO occupation_ratings (occupation_id,dimension,label_zh,stars,note) VALUES (%s,%s,%s,%s,%s)",
                    (occ_id, r["dimension"], r["label_zh"], r["stars"], r.get("note")))
    print(f"[ratings] {len(RATINGS)}")

    cur.execute("DELETE FROM occupation_education WHERE occupation_id=%s", (occ_id,))
    for e in EDUCATION:
        cur.execute("INSERT INTO occupation_education (occupation_id,stage,duration,cost_min,cost_max,cost_note,sort_order) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (occ_id, e["stage"], e["duration"], e["cost_min"], e["cost_max"], e["cost_note"], e["sort_order"]))
    print(f"[education] {len(EDUCATION)}")

    cur.execute("DELETE FROM occupation_qualifications WHERE occupation_id=%s", (occ_id,))
    for q in QUALIFICATIONS:
        cur.execute("INSERT INTO occupation_qualifications (occupation_id,qual_name,issuer,note,is_mandatory,sort_order) VALUES (%s,%s,%s,%s,%s,%s)",
                    (occ_id, q["qual_name"], q.get("issuer"), q.get("note"), q["is_mandatory"], q["sort_order"]))
    print(f"[qualifications] {len(QUALIFICATIONS)}")

    cur.execute("DELETE FROM occupation_job_listings WHERE occupation_id=%s", (occ_id,))
    for jl in JOB_LISTINGS:
        cur.execute("INSERT INTO occupation_job_listings (occupation_id,platform,count_min,count_max,note,snapshot_date) VALUES (%s,%s,%s,%s,%s,%s)",
                    (occ_id, jl["platform"], jl["count_min"], jl["count_max"], jl["note"], TODAY))
    print(f"[job_listings] {len(JOB_LISTINGS)}")

    cur.execute("DELETE FROM occupation_salaries WHERE occupation_id=%s", (occ_id,))
    for s in SALARIES:
        cur.execute("INSERT INTO occupation_salaries (occupation_id,experience,salary_min,salary_max,salary_note,sort_order,currency) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (occ_id, s["experience"], s["salary_min"], s["salary_max"], s["salary_note"], s["sort_order"], OCC.get("currency", "AUD")))
    print(f"[salaries] {len(SALARIES)}")

    cur.execute("DELETE FROM occupation_visa_pathways WHERE occupation_id=%s", (occ_id,))
    for v in VISA_PATHWAYS:
        cur.execute("INSERT INTO occupation_visa_pathways (occupation_id,visa_subclass,visa_name,description,sort_order) VALUES (%s,%s,%s,%s,%s)",
                    (occ_id, v["visa_subclass"], v["visa_name"], v["description"], v["sort_order"]))
    print(f"[visa_pathways] {len(VISA_PATHWAYS)}")

    cur.execute("DELETE FROM occupation_suitability WHERE occupation_id=%s", (occ_id,))
    for i, item in enumerate(SUITABILITY_FIT):
        cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'fit',%s,%s)", (occ_id, item, i))
    for i, item in enumerate(SUITABILITY_UNFIT):
        cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'unfit',%s,%s)", (occ_id, item, i))
    print(f"[suitability] {len(SUITABILITY_FIT)} fit, {len(SUITABILITY_UNFIT)} unfit")

    cur.execute("DELETE FROM occupation_sources WHERE occupation_id=%s", (occ_id,))
    for s in SOURCES:
        cur.execute("INSERT INTO occupation_sources (occupation_id,source_name,content,url) VALUES (%s,%s,%s,%s)",
                    (occ_id, s["source_name"], s.get("content"), s.get("url")))
    print(f"[sources] {len(SOURCES)}")

    cur.execute("DELETE FROM occupation_faqs WHERE occupation_id=%s", (occ_id,))
    for faq in FAQS:
        cur.execute("INSERT INTO occupation_faqs (occupation_id,faq_type,sort_order) VALUES(%s,%s,%s)",
                    (occ_id, faq["faq_type"], faq["sort_order"]))
        faq_id = cur.lastrowid
        cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'zh-CN',%s,%s) ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",
                    (faq_id, faq["question"], faq["answer"]))
    print(f"[faqs] {len(FAQS)}")
