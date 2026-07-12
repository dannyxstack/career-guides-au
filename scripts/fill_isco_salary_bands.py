"""为 IT/NL/IE（ISCO 职业）补 median/mean 汇总薪资档（估算基线）。

背景：gen_isco 只写了经验分档（salary_band=NULL），没有 median/mean 汇总行；
而 risk map 弹层的 avg_salary 取 band='mean'（experience='平均薪资'）行、职业页中位数取
band='median' 行。缺这两档 → 弹层薪资为空。

本脚本用各职业「经验档区间中点」估算：median=中点的统计中位数，mean=中点的均值。
作为**基线桩**，之后官方层（CBS/ISTAT/CSO）可 override band='median' 行（note 不含"估算"）。

幂等：只删本脚本写的估算行（note 含 EST_MARK），不动官方值。currency 取 occupations.currency。
运行：python -m scripts.fill_isco_salary_bands --country NL[,IT,IE] [--dry]
"""
import sys, os, argparse, statistics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

EST_MARK = "估算"
LABELS = {"median": "薪资中位数", "mean": "平均薪资"}
NOTE = {"median": "薪资中位数（估算：基于各经验档区间中值）",
        "mean": "平均薪资（估算：基于各经验档区间中值）"}
SORT = {"median": -1, "mean": 98}


def fill(country, dry):
    with get_cursor() as cur:
        cur.execute("SELECT id, currency FROM occupations WHERE country_code=%s", (country,))
        occs = cur.fetchall()
        rows = []
        for o in occs:
            cur.execute(
                "SELECT salary_min, salary_max FROM occupation_salaries "
                "WHERE occupation_id=%s AND (salary_band IS NULL OR salary_band NOT IN ('median','mean')) "
                "AND salary_min IS NOT NULL AND salary_max IS NOT NULL", (o["id"],))
            mids = [(float(r["salary_min"]) + float(r["salary_max"])) / 2 for r in cur.fetchall()]
            if not mids:
                continue
            med = int(round(statistics.median(mids)))
            mean = int(round(statistics.fmean(mids)))
            cur_ = o["currency"] or "EUR"
            rows.append((o["id"], cur_, LABELS["median"], med, med, NOTE["median"], SORT["median"], "median"))
            rows.append((o["id"], cur_, LABELS["mean"], mean, mean, NOTE["mean"], SORT["mean"], "mean"))
    print(f"[{country}] 可估算职业 {len(rows)//2}，写 {len(rows)} 行（median+mean）")
    if dry:
        print("[dry] 样本:", [(r[0], r[7], r[3]) for r in rows[:6]])
        return
    with get_cursor() as cur:
        cur.execute(
            "DELETE s FROM occupation_salaries s JOIN occupations o ON o.id=s.occupation_id "
            "WHERE o.country_code=%s AND s.salary_band IN ('median','mean') AND s.salary_note LIKE %s",
            (country, "%" + EST_MARK + "%"))
        deleted = cur.rowcount
        cur.executemany(
            "INSERT INTO occupation_salaries "
            "(occupation_id, currency, experience, salary_min, salary_max, salary_note, sort_order, salary_band) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", rows)
    print(f"[{country}] 删旧估算 {deleted} | 新写 {len(rows)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="国家码，逗号分隔，如 NL,IT,IE")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    for cc in [c.strip().upper() for c in a.country.split(",") if c.strip()]:
        fill(cc, a.dry)
