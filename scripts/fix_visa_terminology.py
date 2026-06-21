"""把全库 482 签证的旧术语 TSS 统一规范为 Skills in Demand（保留'旧称 TSS'历史说明）。
覆盖 visa_pathways(visa_name/description)、i18n.summary、faqs.answer。可重复运行（幂等）。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor


def normalize(t: str) -> str:
    if not t or "TSS" not in t:
        return t
    # 保护：清单术语 MLTSSL/STSOL 含子串 TSS；"旧称 TSS" 为有意保留的历史说明
    t = t.replace("MLTSSL", "\x00M").replace("STSOL", "\x00S")
    t = t.replace("旧称 TSS", "\x00A").replace("旧称TSS", "\x00B")
    t = t.replace("TSS（Skills in Demand）", "Skills in Demand")
    t = t.replace("（TSS）", "")
    t = t.replace("TSS", "Skills in Demand")
    t = t.replace("\x00A", "旧称 TSS").replace("\x00B", "旧称TSS")
    t = t.replace("\x00M", "MLTSSL").replace("\x00S", "STSOL")
    return t


def run():
    n = 0
    with get_cursor() as cur:
        # visa_pathways
        cur.execute("SELECT id, visa_name, description FROM occupation_visa_pathways "
                    "WHERE visa_name LIKE '%TSS%' OR description LIKE '%TSS%'")
        for r in cur.fetchall():
            nm, de = normalize(r["visa_name"]), normalize(r["description"])
            if nm != r["visa_name"] or de != r["description"]:
                cur.execute("UPDATE occupation_visa_pathways SET visa_name=%s, description=%s WHERE id=%s",
                            (nm, de, r["id"])); n += 1
        # i18n.summary
        cur.execute("SELECT occupation_id, locale, summary FROM occupations_i18n WHERE summary LIKE '%TSS%'")
        for r in cur.fetchall():
            s = normalize(r["summary"])
            if s != r["summary"]:
                cur.execute("UPDATE occupations_i18n SET summary=%s WHERE occupation_id=%s AND locale=%s",
                            (s, r["occupation_id"], r["locale"])); n += 1
        # faqs.answer
        cur.execute("SELECT faq_id, locale, answer FROM occupation_faqs_i18n WHERE answer LIKE '%TSS%'")
        for r in cur.fetchall():
            a = normalize(r["answer"])
            if a != r["answer"]:
                cur.execute("UPDATE occupation_faqs_i18n SET answer=%s WHERE faq_id=%s AND locale=%s",
                            (a, r["faq_id"], r["locale"])); n += 1
    print(f"[fix_visa] 更新 {n} 行")
    # 复查（排除保留的"旧称 TSS"）
    with get_cursor() as cur:
        bad = 0
        for tbl, col in [("occupation_visa_pathways", "visa_name"), ("occupation_visa_pathways", "description"),
                         ("occupations_i18n", "summary"), ("occupation_faqs_i18n", "answer")]:
            cur.execute(f"SELECT {col} v FROM {tbl} WHERE {col} LIKE '%TSS%'")
            for r in cur.fetchall():
                if "旧称" not in (r["v"] or ""):
                    bad += 1
        print(f"[fix_visa] 非'旧称'残留 TSS: {bad}")


if __name__ == "__main__":
    run()
