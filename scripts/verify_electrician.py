import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

with get_cursor() as cur:
    checks = [
        ("occupations",
         "SELECT anzsco_code, anzsco_title, workforce_size, shortage_listed FROM occupations WHERE anzsco_code='341111'"),
        ("i18n locales",
         "SELECT locale, name FROM occupations_i18n WHERE occupation_id=1"),
        ("ratings (11)",
         "SELECT dimension, label_zh, stars FROM occupation_ratings WHERE occupation_id=1 ORDER BY dimension"),
        ("salaries (6)",
         "SELECT experience, salary_min, salary_max FROM occupation_salaries WHERE occupation_id=1 ORDER BY sort_order"),
        ("job_listings (3)",
         "SELECT platform, count_min, count_max, snapshot_date FROM occupation_job_listings WHERE occupation_id=1"),
        ("visa_pathways (5)",
         "SELECT visa_subclass, visa_name, description FROM occupation_visa_pathways WHERE occupation_id=1 ORDER BY sort_order"),
        ("sources (9)",
         "SELECT source_name FROM occupation_sources WHERE occupation_id=1"),
        ("faqs (8)",
         "SELECT f.faq_type, fi.question FROM occupation_faqs f "
         "JOIN occupation_faqs_i18n fi ON fi.faq_id=f.id "
         "WHERE f.occupation_id=1 ORDER BY f.sort_order"),
    ]
    for label, sql in checks:
        cur.execute(sql)
        rows = cur.fetchall()
        print(f"--- {label} ({len(rows)}) ---")
        for r in rows:
            print(" ", r)
        print()
