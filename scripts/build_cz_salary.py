"""CZ 四位 ISCO 官方薪资（零 LLM）→ 合并进 downloads/cz/cz_by_isco.json。

源：ČSÚ/ISPV 2025 区域统计
  - ispv_private_sector_occupation_earnings_2025.xlsx（mzdová sféra，私营）
  - ispv_public_sector_occupation_earnings_2025.xlsx（platová sféra，公共）
每表：col0=四/五位 CZ-ISCO 代码+名称，col1=počet zaměstnanců(tis. osob，千人)，
      col2=medián(hrubá měsíční mzda/plat，CZK/月)，col7=průměr(均值 CZK/月)。
仅取四位 ISCO；两部门按就业人数加权合并；×12 年化。
avg_salary=年化中位数，salary_mean=年化均值（与北欧 avg_salary=median×12 口径一致）。

运行：python -m scripts.build_cz_salary
"""
import json
import os
import re

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "..", "downloads", "cz")
FILES = [
    ("ispv_private_sector_occupation_earnings_2025.xlsx", "MZS-M8r"),
    ("ispv_public_sector_occupation_earnings_2025.xlsx", "PLS-M8r"),
]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse(path, sheet):
    """→ {isco4: [(headcount_persons, median_monthly, mean_monthly), ...]}"""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    out = {}
    for r in ws.iter_rows(values_only=True):
        c0 = r[0]
        if c0 is None:
            continue
        m = re.match(r"\s*(\d+)\s+", str(c0))
        if not m or len(m.group(1)) != 4:
            continue
        hc, med, mean = num(r[1]), num(r[2]), num(r[7])
        if med is None:
            continue
        out.setdefault(m.group(1), []).append((hc, med, mean))
    wb.close()
    return out


def main():
    merged = {}  # isco4 -> list of (hc_persons, median, mean)
    for fn, sheet in FILES:
        for isco, recs in parse(os.path.join(DL, fn), sheet).items():
            merged.setdefault(isco, []).extend(recs)

    salary = {}
    for isco, recs in merged.items():
        # 人数(千人→人)加权；缺人数的记录退化为等权 1。
        tw = sum((hc or 0.001) for hc, _, _ in recs)
        med = sum((hc or 0.001) * m for hc, m, _ in recs) / tw
        means = [(hc, mn) for hc, _, mn in recs if mn is not None]
        mean = (sum((hc or 0.001) * mn for hc, mn in means) / sum((hc or 0.001) for hc, _ in means)
                if means else None)
        med_m, mean_m = round(med), (round(mean) if mean else None)
        salary[isco] = {
            "avg_salary": med_m * 12,
            "salary_mean": (mean_m * 12) if mean_m else None,
            "salary_note": (f"Official ČSÚ/ISPV 2025 gross monthly earnings "
                            f"(private + public sector, employment-weighted), annualised ×12. "
                            f"Median {med_m:,} CZK/month."),
        }

    # 合并回 by_isco.json（保留 workforce / name_local / label_en）
    p = os.path.join(DL, "cz_by_isco.json")
    data = json.load(open(p, encoding="utf-8"))
    hit = 0
    for isco, v in data.items():
        s = salary.get(isco)
        if s:
            v.update(s)
            hit += 1
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[CZ] parsed {len(salary)} four-digit ISCO salaries; matched {hit}/{len(data)} in by_isco.json")


if __name__ == "__main__":
    main()
