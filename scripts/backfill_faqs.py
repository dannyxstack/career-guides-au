"""用 DeepSeek 为"空壳"职业补 FAQ（每职业 2-3 条），英文母本写 occupation_faqs_v2。

移民话题按国家移民档位过滤（对齐 aijobrisk-go migration.go）：
- none 档（非移民国 AR CL ID MY TH VN TR…）：严禁任何移民/签证/永居/搬迁话题，
  只谈薪资、日常工作、技能、AI 影响、职业前景。避免被读者当作垃圾信息。
- info 档（EU Blue Card / 工签→永居 的国家）：可含 1 条工签/Blue Card 路径 FAQ。
- full 档不在补全范围（已有 FAQ）。

只补 0 FAQ 的职业；已有 FAQ 的跳过 → 幂等、可断点续跑。
12 路并发，逐职业独立提交。生成后需跑 scripts/collect_strings_v2.py 把英文串纳入 TM。

运行：DEEPSEEK_MODEL=... LLM_PROVIDER=deepseek PYTHONIOENCODING=utf-8 \
      python -m scripts.backfill_faqs [--limit N] [--country CH,BE] [--workers 12] [--dry]
"""
import sys, os, argparse, json, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts import _deepseek_rest

FULL = {"AU", "NZ", "CA", "US", "UK", "DE", "IE"}
INFO = {"FR", "ES", "IT", "NL", "BE", "AT", "PL", "PT", "GR", "HU", "CZ", "RO", "LU", "SK",
        "SI", "HR", "DK", "FI", "SE", "NO", "IS", "CH", "SG", "JP", "KR", "EE", "LV", "LT"}
CC_NAME = {
    "CH": "Switzerland", "BE": "Belgium", "AT": "Austria", "PL": "Poland", "PT": "Portugal",
    "GR": "Greece", "RO": "Romania", "LU": "Luxembourg", "SK": "Slovakia", "SI": "Slovenia",
    "HR": "Croatia", "EE": "Estonia", "LV": "Latvia", "LT": "Lithuania",
    "AR": "Argentina", "CL": "Chile", "MY": "Malaysia", "ID": "Indonesia", "TH": "Thailand",
    "VN": "Vietnam", "TR": "Turkey", "CN": "China",
}


def tier(cc):
    return "full" if cc in FULL else ("info" if cc in INFO else "none")


def build_prompt(cc, code, title):
    name = CC_NAME.get(cc, cc)
    if tier(cc) == "info":
        rule = (f"Include exactly ONE question about the work-visa / EU Blue Card route to working "
                f"in {name} (mention official routes only, no fabricated numbers). "
                f"faq_type values: one of salary, migration, career, ai.")
    else:  # none
        rule = (f"CRITICAL: {name} is NOT a migration destination for this audience. Do NOT mention "
                f"immigration, work visas, permanent residence, relocation, or moving to {name} in ANY "
                f"question or answer. Focus only on pay, day-to-day work, required skills, AI impact and "
                f"career outlook. faq_type values: one of salary, career, ai, skills, outlook.")
    return (f"Occupation FAQ for a careers website. Country: {name}. "
            f"ISCO-08 code: {code}. Occupation (English): {title}.\n"
            f"Write 2-3 frequently-asked questions with concise factual answers (each answer 40-90 words), "
            f"specific to {name}. Include one question about salary/pay.\n{rule}\n"
            f'Return JSON: {{"faqs":[{{"faq_type":"...","question":"...","answer":"..."}}]}} '
            f"ALL TEXT IN ENGLISH, natural and non-repetitive.")


SYS = ("You are a careers-website content writer. You produce accurate, concise, non-promotional FAQ "
       "content and strictly follow topic constraints. Output valid JSON only.")

_print_lock = threading.Lock()


def gen_one(occ):
    cc, code, title = occ["country_code"], occ["occ_code"], occ["anzsco_title"]
    v = _deepseek_rest.complete_json(SYS, build_prompt(cc, code, title))
    faqs = v.get("faqs") or []
    rows = []
    for i, f in enumerate(faqs[:3]):
        q, a = (f.get("question") or "").strip(), (f.get("answer") or "").strip()
        if not q or not a:
            continue
        rows.append((occ["id"], (f.get("faq_type") or "general")[:40], q, a, i))
    if not rows:
        raise ValueError("空 faqs")
    with get_cursor() as cur:
        # 双重保险：并发下若已被其他运行填过则跳过
        cur.execute("SELECT COUNT(*) c FROM occupation_faqs_v2 WHERE occupation_id=%s", (occ["id"],))
        if cur.fetchone()["c"] > 0:
            return 0
        cur.executemany("INSERT INTO occupation_faqs_v2 (occupation_id,faq_type,question,answer,sort_order) "
                        "VALUES (%s,%s,%s,%s,%s)", rows)
    return len(rows)


def main(limit, countries, workers, dry):
    with get_cursor() as cur:
        sql = ("SELECT o.id,o.country_code,o.occ_code,o.anzsco_title FROM occupations o "
               "WHERE NOT EXISTS(SELECT 1 FROM occupation_faqs_v2 f WHERE f.occupation_id=o.id)")
        params = []
        if countries:
            sql += " AND o.country_code IN (%s)" % ",".join(["%s"] * len(countries))
            params += countries
        sql += " ORDER BY o.country_code, o.occ_code"
        if limit:
            sql += " LIMIT %d" % int(limit)
        cur.execute(sql, params)
        todo = cur.fetchall()
    from collections import Counter
    print(f"待补 FAQ 职业 {len(todo)} 个；档位分布 {dict(Counter(tier(o['country_code']) for o in todo))}")
    if dry:
        for o in todo[:3]:
            print("---", o["country_code"], o["occ_code"], o["anzsco_title"], "tier=", tier(o["country_code"]))
            print(build_prompt(o["country_code"], o["occ_code"], o["anzsco_title"]))
        return

    done = ok = fail = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(gen_one, o): o for o in todo}
        for fut in as_completed(futs):
            o = futs[fut]
            done += 1
            try:
                n = fut.result()
                ok += 1
            except Exception as e:
                fail += 1
                with _print_lock:
                    print(f"  FAIL {o['country_code']}/{o['occ_code']}: {e}")
            if done % 50 == 0:
                with _print_lock:
                    print(f"  进度 {done}/{len(todo)}  ok={ok} fail={fail}")
    print(f"完成：ok={ok} fail={fail} / {len(todo)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--country", default="")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    cs = [x.strip().upper() for x in a.country.split(",") if x.strip()]
    main(a.limit, cs, a.workers, a.dry)
