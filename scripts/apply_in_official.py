"""用 PLFS 官方数据覆盖 IN 的 workforce/salary（downloads/in/in_by_isco.json）。

- workforce_size：有官方值则覆盖；无（如军职）保留原 LLM 值。
- salary：有官方 mean/median 则删除原 LLM 档、写入 "Average salary"(mean, 喂 export 的 avg_salary)
  + "Median salary"(median)，currency INR，note 注明官方口径；无官方则保留原 LLM 档。
其余字段(评分/文案/AI块)不动。--dry 只看不写。
运行：python -m scripts.apply_in_official [--dry]
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "downloads", "in", "in_by_isco.json")
NOTE = "Official: PLFS 2023-24 unit-level microdata (MoSPI), NCO-2015 3-digit group, annualized"


def main(dry):
    data = json.load(open(SRC, encoding="utf-8"))
    wf_n = sal_n = skip_wf = skip_sal = 0
    with get_cursor() as cur:
        cur.execute("SELECT id, occ_code FROM occupations WHERE country_code='IN'")
        rows = cur.fetchall()
        for o in rows:
            oid, code = o["id"], str(o["occ_code"])
            off = data.get(code)
            if not off:
                continue
            wf = off.get("workforce")
            if wf is not None:
                wf_n += 1
                if not dry:
                    cur.execute("UPDATE occupations SET workforce_size=%s WHERE id=%s", (wf, oid))
            else:
                skip_wf += 1
            mean, med = off.get("mean_annual"), off.get("median_annual")
            if mean or med:
                sal_n += 1
                if not dry:
                    cur.execute("DELETE FROM occupation_salaries_v2 WHERE occupation_id=%s", (oid,))
                    so = 0
                    if mean:
                        cur.execute("INSERT INTO occupation_salaries_v2 (occupation_id,experience,salary_min,salary_max,salary_note,currency,sort_order) "
                                    "VALUES (%s,%s,%s,%s,%s,%s,%s)", (oid, "Average salary", mean, mean, NOTE, "INR", so)); so += 1
                    if med:
                        cur.execute("INSERT INTO occupation_salaries_v2 (occupation_id,experience,salary_min,salary_max,salary_note,currency,sort_order) "
                                    "VALUES (%s,%s,%s,%s,%s,%s,%s)", (oid, "Median salary", med, med, NOTE, "INR", so))
            else:
                skip_sal += 1
    print(f"[apply_in] {'DRY ' if dry else ''}workforce 覆盖 {wf_n}(保留LLM {skip_wf}) | salary 覆盖 {sal_n}(保留LLM {skip_sal})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    main(ap.parse_args().dry)
