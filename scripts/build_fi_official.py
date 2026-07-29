"""装配芬兰(FI)官方薪资+就业 -> downloads/fi/fi_by_isco.json（零 LLM，确定性映射）。

官方源：
- 薪资：Statistics Finland 表 15au《Structure of Earnings》2024。取 total earnings 的
        median / average（Sector=S0 Total, Sex=Total），EUR/月 ×12 得年薪 EUR。
- 就业：Statistics Finland 表 115r，2023 各职业 employed，取 Level 4（四位）行。
芬兰 Classification of Occupations 2010 四位与 ISCO-08 四位一致，直接对齐。

本地名（芬兰语）官方英文表不提供 → 留空，由 gen_fi_official 的 DeepSeek 出 name_local(fi)。
avg_salary 取 median；mean 另存。

运行：python -m scripts.build_fi_official
产物：downloads/fi/fi_by_isco.json
"""
import os, csv, io, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UNIVERSE = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
EARN = os.path.join(REPO, "downloads", "fi", "occupation_earnings_2024.csv")
EMPL = os.path.join(REPO, "downloads", "fi", "occupation_employment_2023.csv")
OUT = os.path.join(REPO, "downloads", "fi", "fi_by_isco.json")

CODE = re.compile(r'^(\d{4})\s')
LVL4 = re.compile(r'^(\d{4})\s+.*\(Level 4\)\s*$')
MED_COL = "Median for total earnings of full-time wage and salary earners, EUR per month"
AVG_COL = "Average for total earnings of full-time wage and salary earners, EUR per month"
OCC_COL = "Classification of Occupations 2010"


def main():
    uni = {o["isco"]: o for o in json.load(open(UNIVERSE, encoding="utf-8"))}

    med, mean = {}, {}
    for r in csv.DictReader(open(EARN, encoding="utf-8-sig")):
        if r.get("Classification of Sectors 2023") != "S0 Total" or r.get("Sex") != "Total":
            continue
        m = CODE.match(r.get(OCC_COL) or "")
        if not m or m.group(1) not in uni:
            continue
        code = m.group(1)
        try:
            med[code] = int(float(r[MED_COL])) * 12
        except (TypeError, ValueError):
            pass
        try:
            mean[code] = int(float(r[AVG_COL])) * 12
        except (TypeError, ValueError):
            pass

    wf = {}
    for row in csv.reader(open(EMPL, encoding="utf-8-sig")):
        if not row:
            continue
        m = LVL4.match(row[0])
        if not m or m.group(1) not in uni:
            continue
        try:
            wf[m.group(1)] = int(float(row[1]))
        except (TypeError, ValueError):
            pass

    out = {}
    for isco, o in uni.items():
        mv, mnv = med.get(isco), mean.get(isco)
        out[isco] = {
            "isco": isco, "label_en": o["label_en"],
            "avg_salary": mv,            # median 年薪 (EUR)，官方
            "salary_mean": mnv,          # mean 年薪 (EUR)，官方
            "workforce": wf.get(isco),   # employed 2023 (Level 4)，官方
            "name_local": None,          # 芬兰语名由 gen_fi_official 的 LLM 出 (fi)
            "salary_note": ("Official: Statistics Finland table 15au, median total monthly earnings 2024 "
                            "×12 (all sectors, both sexes). Employment: table 115r (2023)."
                            if mv else None),
        }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[build_fi_official] {len(out)} ISCO -> fi_by_isco.json | median薪资 "
          f"{sum(1 for v in out.values() if v['avg_salary'])} | mean {sum(1 for v in out.values() if v['salary_mean'])} | "
          f"workforce {sum(1 for v in out.values() if v['workforce'])}")


if __name__ == "__main__":
    main()
