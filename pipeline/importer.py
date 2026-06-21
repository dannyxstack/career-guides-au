"""
将解析后的职业数据写入 MySQL 数据库。
支持 upsert：若 anzsco_code 已存在则全量替换子表数据。
"""

import json
from datetime import date
from db.connection import get_cursor


def _upsert_occupation(cursor, data: dict) -> int:
    """插入或更新 occupations 主表，返回 occupation_id。"""
    cursor.execute(
        """
        INSERT INTO occupations
          (anzsco_code, anzsco_title, shortage_listed, workforce_size, growth_areas)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          anzsco_title    = VALUES(anzsco_title),
          shortage_listed = VALUES(shortage_listed),
          workforce_size  = VALUES(workforce_size),
          growth_areas    = VALUES(growth_areas)
        """,
        (
            data.get("anzsco_code"),
            data.get("anzsco_title"),
            1 if data.get("shortage_listed") else 0,
            data.get("workforce_size"),
            json.dumps(data.get("growth_areas", []), ensure_ascii=False),
        ),
    )
    cursor.execute(
        "SELECT id FROM occupations WHERE anzsco_code = %s",
        (data["anzsco_code"],),
    )
    return cursor.fetchone()["id"]


def _upsert_i18n(cursor, occupation_id: int, data: dict, locale: str = "zh-CN"):
    cursor.execute(
        """
        INSERT INTO occupations_i18n
          (occupation_id, locale, name, summary, forecast_note, trend_summary)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          name          = VALUES(name),
          summary       = VALUES(summary),
          forecast_note = VALUES(forecast_note),
          trend_summary = VALUES(trend_summary)
        """,
        (
            occupation_id,
            locale,
            data.get("name_zh"),
            data.get("summary"),
            data.get("forecast_note"),
            data.get("trend_summary"),
        ),
    )


def _replace_children(cursor, occupation_id: int, data: dict, today: date):
    """删除旧子表数据后重新插入（全量刷新策略）。"""

    # ── 评级 ────────────────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_ratings WHERE occupation_id = %s", (occupation_id,))
    for r in data.get("ratings", []):
        cursor.execute(
            "INSERT INTO occupation_ratings (occupation_id, dimension, label_zh, stars) VALUES (%s,%s,%s,%s)",
            (occupation_id, r["dimension"], r["label_zh"], r["stars"]),
        )

    # ── 教育路径 ─────────────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_education WHERE occupation_id = %s", (occupation_id,))
    for i, e in enumerate(data.get("education", [])):
        cursor.execute(
            """INSERT INTO occupation_education
               (occupation_id, stage, duration, cost_min, cost_max, cost_note, sort_order)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (occupation_id, e["stage"], e.get("duration"),
             e.get("cost_min"), e.get("cost_max"), e.get("cost_note"), i),
        )

    # ── 从业资质 ─────────────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_qualifications WHERE occupation_id = %s", (occupation_id,))
    for i, q in enumerate(data.get("qualifications", [])):
        cursor.execute(
            """INSERT INTO occupation_qualifications
               (occupation_id, qual_name, issuer, note, sort_order)
               VALUES (%s,%s,%s,%s,%s)""",
            (occupation_id, q["qual_name"], q.get("issuer"), q.get("note"), i),
        )

    # ── 平台挂牌量 ───────────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_job_listings WHERE occupation_id = %s", (occupation_id,))
    for jl in data.get("job_listings", []):
        cursor.execute(
            """INSERT INTO occupation_job_listings
               (occupation_id, platform, count_min, count_max, note, snapshot_date)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (occupation_id, jl["platform"], jl.get("count_min"),
             jl.get("count_max"), jl.get("note"), today),
        )

    # ── 收入范围 ─────────────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_salaries WHERE occupation_id = %s", (occupation_id,))
    for s in data.get("salaries", []):
        cursor.execute(
            """INSERT INTO occupation_salaries
               (occupation_id, experience, salary_min, salary_max, salary_note, sort_order)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (occupation_id, s["experience"], s.get("salary_min"),
             s.get("salary_max"), s.get("salary_note"), s.get("sort_order", 0)),
        )

    # ── 签证路径 ─────────────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_visa_pathways WHERE occupation_id = %s", (occupation_id,))
    for v in data.get("visa_pathways", []):
        cursor.execute(
            """INSERT INTO occupation_visa_pathways
               (occupation_id, visa_subclass, visa_name, description, sort_order)
               VALUES (%s,%s,%s,%s,%s)""",
            (occupation_id, v["visa_subclass"], v.get("visa_name"),
             v.get("description"), v.get("sort_order", 0)),
        )

    # ── 适合/不适合人群 ──────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_suitability WHERE occupation_id = %s", (occupation_id,))
    for i, item in enumerate(data.get("suitability_fit", [])):
        cursor.execute(
            "INSERT INTO occupation_suitability (occupation_id, type, item, sort_order) VALUES (%s,'fit',%s,%s)",
            (occupation_id, item, i),
        )
    for i, item in enumerate(data.get("suitability_unfit", [])):
        cursor.execute(
            "INSERT INTO occupation_suitability (occupation_id, type, item, sort_order) VALUES (%s,'unfit',%s,%s)",
            (occupation_id, item, i),
        )

    # ── 数据来源 ─────────────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_sources WHERE occupation_id = %s", (occupation_id,))
    for s in data.get("sources", []):
        cursor.execute(
            "INSERT INTO occupation_sources (occupation_id, source_name, content) VALUES (%s,%s,%s)",
            (occupation_id, s["source_name"], s.get("content")),
        )

    # ── FAQ ──────────────────────────────────────────────────────────────────
    cursor.execute("DELETE FROM occupation_faqs WHERE occupation_id = %s", (occupation_id,))
    for faq in data.get("faqs", []):
        cursor.execute(
            "INSERT INTO occupation_faqs (occupation_id, faq_type, sort_order) VALUES (%s,%s,%s)",
            (occupation_id, faq.get("faq_type"), faq.get("sort_order", 0)),
        )
        faq_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO occupation_faqs_i18n (faq_id, locale, question, answer)
               VALUES (%s, 'zh-CN', %s, %s)
               ON DUPLICATE KEY UPDATE question=VALUES(question), answer=VALUES(answer)""",
            (faq_id, faq["question"], faq["answer"]),
        )


def import_occupation(data: dict, locale: str = "zh-CN") -> int:
    """
    将解析好的职业 dict 写入数据库，返回 occupation_id。
    整个过程在一个事务内完成。
    """
    today = date.today()
    with get_cursor() as cursor:
        occupation_id = _upsert_occupation(cursor, data)
        _upsert_i18n(cursor, occupation_id, data, locale)
        _replace_children(cursor, occupation_id, data, today)
    return occupation_id
