"""SG 四位 ISCO 官方薪资（零 LLM）→ 合并进 downloads/sg/sg_by_isco.json。

源：MOM Occupational Wage Survey 2025, Table 4 (All Industries)。
  - col1 = SSOC 2024 五位代码，col2 = 职业名，col4 = Median ($)（月度基本工资 SGD）。
SSOC 建于 ISCO-08 之上，前四位=ISCO-08 四位组；同一 ISCO 下多个 SSOC 取中位数聚合；×12 年化。
仅有 median 口径（无 mean）；salary_mean 留空，salary_note 注明。

运行：python -m scripts.build_sg_salary
"""
import json
import os
import statistics

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "..", "downloads", "sg")
SRC = os.path.join(DL, "mom_occupational_wages_by_industry_2025.xlsx")
SHEET = "T4"
COL_SSOC = 1
COL_MEDIAN = 4


def num(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def main():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb[SHEET]
    by_isco = {}  # isco4 -> [monthly_median, ...]
    for r in ws.iter_rows(values_only=True):
        ssoc = r[COL_SSOC]
        if ssoc is None:
            continue
        ssoc = str(ssoc).strip()
        if not (ssoc.isdigit() and len(ssoc) == 5):
            continue  # skip 1-digit category headers
        med = num(r[COL_MEDIAN])
        if med is None or med <= 0:
            continue
        by_isco.setdefault(ssoc[:4], []).append(med)
    wb.close()

    salary = {}
    for isco, meds in by_isco.items():
        m = round(statistics.median(meds))
        salary[isco] = {
            "avg_salary": m * 12,
            "salary_mean": None,
            "salary_note": (f"Official MOM Occupational Wage Survey 2025 median gross monthly "
                            f"basic wage (all industries), annualised ×12. "
                            f"{m:,} SGD/month ({len(meds)} SSOC occupation(s))."),
        }

    p = os.path.join(DL, "sg_by_isco.json")
    data = json.load(open(p, encoding="utf-8"))
    hit = 0
    for isco, v in data.items():
        s = salary.get(isco)
        if s:
            v.update(s)
            hit += 1
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[SG] parsed {len(salary)} four-digit ISCO salaries; matched {hit}/{len(data)} in by_isco.json")


if __name__ == "__main__":
    main()
