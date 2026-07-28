"""HU 四位 ISCO 官方薪资（零 LLM）→ 合并进 downloads/hu/hu_by_isco.json。

源：KSH 20.8.1.10. Full-time employees' gross monthly earnings by occupation (HSCO'08)。
  - col0 = HSCO'08 四位代码（对齐 ISCO-08），col26 = 2023 Total（最新年，全年龄合计）。
  - 值为月度税前平均总薪（HUF/月）；`…` 为保密→跳过；×12 年化。
avg_salary=salary_mean=年化平均总薪（官方仅提供平均口径，非中位数，salary_note 注明）。

运行：python -m scripts.build_hu_salary
"""
import json
import os

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "..", "downloads", "hu")
SRC = os.path.join(DL, "ksh_occupation_earnings_archive.xlsx")
SHEET = "20.8.1.10."
COL_CODE = 0
COL_TOTAL_2023 = 26  # "2023 Total" — latest year, all age groups


def num(v):
    if v is None:
        return None
    s = str(v).strip()
    if s in ("", "…", "..", "-"):
        return None
    try:
        return float(s.replace(" ", "").replace(",", ""))
    except ValueError:
        return None


def main():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb[SHEET]
    salary = {}
    for r in ws.iter_rows(min_row=3, values_only=True):
        code = r[COL_CODE]
        if code is None:
            continue
        code = str(code).strip()
        if not (code.isdigit() and len(code) == 4):
            continue
        monthly = num(r[COL_TOTAL_2023])
        if monthly is None:
            continue
        m = round(monthly)
        salary[code] = {
            "avg_salary": m * 12,
            "salary_mean": m * 12,
            "salary_note": (f"Official KSH 2023 gross monthly earnings, full-time employees "
                            f"(average, all age groups), annualised ×12. {m:,} HUF/month."),
        }
    wb.close()

    p = os.path.join(DL, "hu_by_isco.json")
    data = json.load(open(p, encoding="utf-8"))
    hit = 0
    for isco, v in data.items():
        s = salary.get(isco)
        if s:
            v.update(s)
            hit += 1
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[HU] parsed {len(salary)} four-digit ISCO salaries; matched {hit}/{len(data)} in by_isco.json")


if __name__ == "__main__":
    main()
