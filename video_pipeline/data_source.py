"""从 MySQL 取职业数据，整理成视频流水线用的干净 dict。复用仓库现有 db.connection。"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.connection import get_cursor  # noqa: E402


def list_occupations(country_code: str = "AU") -> list[dict]:
    """列出所有职业（给 Web 界面的列表用），附中文名与已有内容状态。"""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT o.id, o.anzsco_code, o.category,
                   zh.name AS name_zh, en.name AS name_en
            FROM occupations o
            LEFT JOIN occupations_i18n zh
                   ON zh.occupation_id = o.id AND zh.locale = 'zh-CN'
            LEFT JOIN occupations_i18n en
                   ON en.occupation_id = o.id AND en.locale = 'en'
            WHERE o.country_code = %s
            ORDER BY o.category, o.id
            """,
            (country_code,),
        )
        return cur.fetchall()


def _loads(val):
    if not val:
        return []
    if isinstance(val, (list, dict)):
        return val
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return []


def get_occupation(occupation_id: int, locale: str = "zh-CN") -> dict:
    """取单个职业的完整结构化数据，供大纲生成与视频渲染共用。"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, anzsco_code, category, workforce_size, shortage_listed, growth_areas "
            "FROM occupations WHERE id = %s",
            (occupation_id,),
        )
        occ = cur.fetchone()
        if not occ:
            raise ValueError(f"找不到 occupation id={occupation_id}")

        cur.execute(
            "SELECT locale, name, summary, forecast_note, trend_summary "
            "FROM occupations_i18n WHERE occupation_id = %s",
            (occupation_id,),
        )
        i18n = {r["locale"]: r for r in cur.fetchall()}

        cur.execute(
            "SELECT experience, salary_min, salary_max, salary_note, salary_band, sort_order "
            "FROM occupation_salaries WHERE occupation_id = %s ORDER BY sort_order",
            (occupation_id,),
        )
        salaries = cur.fetchall()

        cur.execute(
            "SELECT dimension, label_zh, stars, score, note "
            "FROM occupation_ratings WHERE occupation_id = %s",
            (occupation_id,),
        )
        ratings = cur.fetchall()

        cur.execute(
            "SELECT visa_subclass, visa_name, description, sort_order "
            "FROM occupation_visa_pathways WHERE occupation_id = %s ORDER BY sort_order",
            (occupation_id,),
        )
        visas = cur.fetchall()

        cur.execute(
            "SELECT type, item FROM occupation_suitability WHERE occupation_id = %s "
            "ORDER BY type, sort_order",
            (occupation_id,),
        )
        suit = cur.fetchall()

        cur.execute(
            "SELECT stage, duration, cost_min, cost_max, cost_note "
            "FROM occupation_education WHERE occupation_id = %s ORDER BY sort_order",
            (occupation_id,),
        )
        edu = cur.fetchall()

        cur.execute(
            "SELECT qual_name, issuer, note, is_mandatory "
            "FROM occupation_qualifications WHERE occupation_id = %s "
            "ORDER BY is_mandatory DESC, sort_order",
            (occupation_id,),
        )
        quals = cur.fetchall()

    zh = i18n.get("zh-CN", {})
    en = i18n.get("en", {})
    primary = i18n.get(locale, zh)

    return {
        "occupation_id": occ["id"],
        "anzsco_code": occ["anzsco_code"],
        "category": occ["category"],
        "locale": locale,
        "name_zh": zh.get("name"),
        "name_en": en.get("name"),
        "summary": primary.get("summary"),
        "forecast_note": primary.get("forecast_note"),
        "trend_summary": primary.get("trend_summary"),
        "growth_areas": _loads(occ["growth_areas"]),
        "shortage_listed": bool(occ["shortage_listed"]),
        "salaries": [
            {
                "label": s["experience"],
                "min": s["salary_min"],
                "max": s["salary_max"],
                "note": s["salary_note"],
                "band": s["salary_band"],
            }
            for s in salaries
        ],
        "ratings": [
            {
                "dimension": r["dimension"],
                "label_zh": r["label_zh"],
                "stars": float(r["stars"]) if r["stars"] is not None else None,
            }
            for r in ratings
        ],
        "visa_pathways": [
            {"subclass": v["visa_subclass"], "name": v["visa_name"], "desc": v["description"]}
            for v in visas
        ],
        "suitability_fit": [r["item"] for r in suit if r["type"] == "fit"],
        "suitability_unfit": [r["item"] for r in suit if r["type"] == "unfit"],
        "education": [
            {"stage": e["stage"], "duration": e["duration"],
             "cost_min": e["cost_min"], "cost_max": e["cost_max"], "cost_note": e["cost_note"]}
            for e in edu
        ],
        "qualifications": [
            {"name": q["qual_name"], "issuer": q["issuer"], "note": q["note"],
             "mandatory": bool(q["is_mandatory"])}
            for q in quals
        ],
    }


if __name__ == "__main__":
    # 冒烟测试：打印一个职业的数据
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("occupation_id", type=int)
    args = ap.parse_args()
    print(json.dumps(get_occupation(args.occupation_id), ensure_ascii=False, indent=2, default=str))
