"""EE 官方四位 ISCO 薪资（零 LLM）→ 合并进 downloads/ee/ee_by_isco.json。

源：Statistics Estonia 表 PA633（downloads/ee/occupation_earnings_pa633.csv）。
  - 指标 "Average gross hourly earnings, euros"：各职业平均小时工资（EUR）。
  - 指标 "Hours of work per employee, ha"：各职业月工时（≈160 = 全职月）。
  取 2022 列（最新）。年化：annual = 小时工资 × 月工时 × 12（缺工时回退 160）。
PA633 用英文职业标签（无代码）、层级混合；按 label_en 归一化匹配四位 ISCO 骨架。
PA633 仅有均值（mean），无中位数：avg_salary=salary_mean=年化均值，note 标明为均值。

运行：python -m scripts.build_ee_salary
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "..", "downloads", "ee")
CSV = os.path.join(DL, "occupation_earnings_pa633.csv")
BYISCO = os.path.join(DL, "ee_by_isco.json")
COL_2022 = 5  # "Males and females 2022"
DEFAULT_HOURS = 160.0


def norm(s):
    s = s.lower().strip()
    s = s.replace("-", " ").replace("’", "'").replace("‑", " ")
    s = re.sub(r"[^a-z0-9' ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def num(v):
    if v is None:
        return None
    v = str(v).strip().replace(" ", "").replace(" ", "")
    if v in ("", ".", "..", "…"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def main():
    hourly, hours = {}, {}
    with open(CSV, encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            ind, label = row[0], row[1]
            v = num(row[COL_2022])
            if v is None:
                continue
            if ind.startswith("Average gross hourly"):
                hourly[label] = v
            elif ind.startswith("Hours of work"):
                hours[label] = v

    # 四位 ISCO 骨架 label_en → code（归一化）
    by = json.load(open(BYISCO, encoding="utf-8"))
    lbl2code = {norm(v["label_en"]): k for k, v in by.items()}

    salary, unmatched = {}, []
    for label, hr in hourly.items():
        code = lbl2code.get(norm(label))
        if not code:
            unmatched.append(label)
            continue
        h = hours.get(label, DEFAULT_HOURS) or DEFAULT_HOURS
        annual = round(hr * h * 12)
        salary[code] = {
            "avg_salary": annual,
            "salary_mean": annual,
            "salary_note": (f"Official Statistics Estonia PA633 2022 average gross hourly "
                            f"earnings €{hr:.2f}/h × {h:.0f} h/month × 12 (mean; no median published)."),
        }

    hit = 0
    for code, v in by.items():
        s = salary.get(code)
        if s:
            v.update(s)
            hit += 1
    json.dump(by, open(BYISCO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[EE] parsed {len(salary)} four-digit salaries; matched {hit}/{len(by)} in by_isco.json; "
          f"unmatched labels {len(unmatched)}")
    if unmatched:
        print("  unmatched sample:", unmatched[:12])


if __name__ == "__main__":
    main()
