"""一次性迁移：旧中文母本数据 -> v2 英文母本表。
- 内容：逐职业读旧 bundle（中文），每个文本字段用旧 TM 的英文（translations locale='en'，按 sha1(中文)）替换，写入 *_v2。
- 已翻语言复用（--port-tm）：把旧 translations 的非英文译文按 sha1(英文) 重新入 translations_v2，避免重翻。

英文取不到时回退保留原串（计入 miss）。幂等：occupations_text_v2 已存在的 occupation_id 跳过（除非 --redo）。
运行：
  python -m scripts.migrate_to_v2 --country IE --limit 3        # 小批验证
  python -m scripts.migrate_to_v2 --country IE                  # 整国
  python -m scripts.migrate_to_v2 --port-tm                     # 复用旧译文到 v2 TM（全局）
"""
import sys, os, argparse, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._i18n_fields import fetch_bundles as fetch_old
from scripts._seed_helper_v2 import seed_occupation_en

CJK = re.compile(r"[一-鿿]")


def build_enmap(cur):
    """{中文源串: 英文译文}（旧 TM，0 缺口）。"""
    cur.execute("SELECT s.src_text, t.text FROM translations t "
                "JOIN translation_src s ON s.src_hash=t.src_hash WHERE t.locale='en'")
    return {r["src_text"]: r["text"] for r in cur.fetchall()}


class Tr:
    def __init__(self, enmap):
        self.enmap = enmap
        self.miss = 0

    def __call__(self, s):
        if not s or not CJK.search(s):
            return s  # 数字/代码/已英文，原样
        v = self.enmap.get(s)
        if v is None:
            self.miss += 1
            return s  # 英文缺失，回退原中文（后续可重译）
        return v


def _existing_v2(cur, cc):
    cur.execute("SELECT t.occupation_id FROM occupations_text_v2 t "
                "JOIN occupations o ON o.id=t.occupation_id WHERE o.country_code=%s", (cc,))
    return {r["occupation_id"] for r in cur.fetchall()}


def migrate_country(cc, limit, redo):
    with get_cursor() as cur:
        enmap = build_enmap(cur)
        print(f"[migrate] enmap 英文条目 {len(enmap)}")
        bundles = fetch_old(cur, cc)
        done = set() if redo else _existing_v2(cur, cc)
    tr = Tr(enmap)
    okc = skip = fail = 0
    for b in bundles:
        oid = b["id"]
        if oid in done:
            skip += 1
            continue
        try:
            _migrate_one(b, tr)  # 单职业独立事务，失败不拖垮整国
            okc += 1
        except Exception as e:
            fail += 1
            print(f"  [fail] id={oid} {b['o'].get('anzsco_title')}: {e}", flush=True)
        if limit and okc >= limit:
            break
    print(f"[migrate] {cc} 迁入 {okc}，跳过(已存在) {skip}，失败 {fail}，英文缺失回退 {tr.miss} 处")


def _migrate_one(b, tr):
    oid = b["id"]
    o = b["o"]
    z = b["i18n_zh"]
    en_row = (b["i18n"].get("en") or {})
    name = en_row.get("name") or tr(z.get("name")) or o["anzsco_title"]
    OCC = {"country_code": o["country_code"], "occ_code": o["occ_code"],
           "occ_code_type": o["occ_code_type"], "anzsco_code": o["anzsco_code"],
           "anzsco_title": name, "category": o["category"], "currency": o.get("currency") or "AUD",
           "workforce_size": o["workforce_size"], "shortage_listed": o["shortage_listed"],
           "is_migration": o["is_migration"], "is_public_servant": o.get("is_public_servant", 0),
           "growth_areas": b["growth"]}
    TEXT = {"name": name, "summary": tr(z.get("summary")),
            "forecast_note": tr(z.get("forecast_note")), "trend_summary": tr(z.get("trend_summary"))}
    EDU = [{"stage": tr(e["stage"]), "duration": tr(e["duration"]), "cost_min": e["cost_min"],
            "cost_max": e["cost_max"], "cost_note": tr(e["cost_note"])} for e in b["education"]]
    QUAL = [{"qual_name": tr(q["name"]), "issuer": tr(q["issuer"]), "note": tr(q["note"]),
             "is_mandatory": int(q["mandatory"])} for q in b["qualifications"]]
    SAL = [{"experience": tr(s["label"]), "salary_min": s["min"], "salary_max": s["max"],
            "salary_note": tr(s["note"]), "currency": o.get("currency") or "AUD"} for s in b["salaries"]]
    VISA = [{"visa_subclass": v["subclass"], "visa_name": tr(v["name"]), "description": tr(v["desc"])}
            for v in b["visa"]]
    RAT = [{"dimension": r["dimension"], "label": tr(r["label_zh"]), "stars": r["stars"]}
           for r in b["ratings"] if r["stars"] is not None]
    FIT = [tr(x) for x in b["suitability_fit"]]
    UNFIT = [tr(x) for x in b["suitability_unfit"]]
    FAQS = [{"faq_type": f["type"], "question": tr(f["question"]), "answer": tr(f["answer"])}
            for f in b["faqs"]]
    AI = None
    ai = b.get("ai")
    if ai:
        AI = {"verdict_type": ai["verdict_type"], "verdict": tr(ai.get("verdict_zh")),
              "entry_narrowing": tr(ai.get("entry_narrowing_zh")), "upgrade_path": tr(ai.get("upgrade_path_zh")),
              "replaced": [tr(x) for x in ai.get("replaced_zh") or []],
              "augmented": [tr(x) for x in ai.get("augmented_zh") or []],
              "moat": [tr(x) for x in ai.get("moat_zh") or []],
              "skills": [tr(x) for x in ai.get("skills_zh") or []],
              "adjacent": ai.get("adjacent") or [], "cluster": ai.get("cluster"),
              "automation_exposure": ai.get("automation_exposure"), "human_moat": ai.get("human_moat"),
              "entry_risk": ai.get("entry_risk"), "ai_upside": ai.get("ai_upside"),
              "aioe_score": ai.get("aioe_score"), "aioe_pct": ai.get("aioe_pct"),
              "aioe_soc": ai.get("aioe_soc"), "aioe_method": ai.get("aioe_method")}
    with get_cursor() as w:
        seed_occupation_en(w, OCC, TEXT, EDU, QUAL, SAL, VISA, RAT, FIT, UNFIT, FAQS, AI)
        if ai and ai.get("disruptors"):
            _migrate_disruptors(w, oid, ai["disruptors"], tr)


def _migrate_disruptors(cur, oid, disruptors, tr):
    for i, d in enumerate(disruptors):
        cur.execute("INSERT INTO ai_disruptors_v2 (name,type,vendor,url,summary,year,maturity) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE summary=VALUES(summary),"
                    "vendor=VALUES(vendor),url=VALUES(url),year=VALUES(year),maturity=VALUES(maturity)",
                    (d["name"], d.get("type", "tool"), d.get("vendor"), d.get("url"),
                     tr(d.get("summary_zh")), d.get("year"), d.get("maturity", "adopted")))
        cur.execute("SELECT id FROM ai_disruptors_v2 WHERE name=%s", (d["name"],))
        did = cur.fetchone()["id"]
        cur.execute("INSERT INTO occupation_ai_disruptor_v2 (occupation_id,disruptor_id,replacement_level,scope,evidence_url,sort_order) "
                    "VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE scope=VALUES(scope),"
                    "replacement_level=VALUES(replacement_level),evidence_url=VALUES(evidence_url),sort_order=VALUES(sort_order)",
                    (oid, did, d.get("level", "partial"), tr(d.get("scope_zh")), d.get("evidence_url"), i))


def port_tm():
    """把旧 translations 的非英文译文按 sha1(英文) 复用到 translations_v2（仅限已在 translation_src_v2 的英文串）。
    多个中文塌到同一英文时，唯一键去重保留其一（用户已接受 sha1(英文) 碰撞）。"""
    with get_cursor() as cur:
        cur.execute("""
            INSERT IGNORE INTO translations_v2 (src_hash, locale, text, gen_model)
            SELECT sv.src_hash, t.locale, t.text, t.gen_model
            FROM translation_src_v2 sv
            JOIN translations en ON en.locale='en' AND en.text = sv.src_text
            JOIN translations t ON t.src_hash = en.src_hash AND t.locale <> 'en'
        """)
        n = cur.rowcount
        cur.execute("SELECT locale, COUNT(*) c FROM translations_v2 GROUP BY locale ORDER BY c DESC")
        dist = cur.fetchall()
    print(f"[port_tm] 复用旧译文 {n} 行 -> translations_v2")
    for r in dist:
        print(f"  {r['locale']:8} {r['c']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--port-tm", action="store_true")
    a = ap.parse_args()
    if a.country:
        migrate_country(a.country, a.limit, a.redo)
    if a.port_tm:
        port_tm()
    if not a.country and not a.port_tm:
        print("用法：--country IE [--limit N] 迁内容；--port-tm 复用旧译文")
