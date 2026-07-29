"""装配丹麦(DK)官方薪资+就业 -> downloads/dk/dk_by_isco.json（零 LLM，确定性映射）。

官方源：Statistics Denmark LONS20《分职业收入》2024（长格式，ARBF×LØNMÅL 指标）。
筛全国总计（All sectors / All forms of pay / Employee group total / Men and women, total）：
- avg_salary = "STANDARDIZED MONTHLY EARNINGS" ×12（DKK/年；LONS20 无 median 月薪，仅标准化均值月薪）。
- workforce  = "Number of fulltime employees in the earnings statistics"（ANTAL）。
  ⚠️ ANTAL 是薪资统计覆盖的全职折算人数，非丹麦全体就业；salary_note/口径注明为覆盖近似。
DISCO-08 四位与 ISCO-08 四位一致，直接对齐。

本地名（丹麦语）官方英文表不提供 → 留空，由 gen_dk_official 的 DeepSeek 出 name_local(da)。

运行：python -m scripts.build_dk_official
产物：downloads/dk/dk_by_isco.json
"""
import os, csv, io, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UNIVERSE = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
SRC = os.path.join(REPO, "downloads", "dk", "lons20_occupation_earnings_2024.csv")
OUT = os.path.join(REPO, "downloads", "dk", "dk_by_isco.json")

CODE = re.compile(r'^(\d{4})\s')
MONTHLY = "STANDARDIZED MONTHLY EARNINGS"
ANTAL = "Number of fulltime employees in the earnings statistics"


def main():
    uni = {o["isco"]: o for o in json.load(open(UNIVERSE, encoding="utf-8"))}
    sal, wf = {}, {}
    for r in csv.DictReader(io.StringIO(open(SRC, "rb").read().decode("utf-8-sig")), delimiter=";"):
        if (r.get("SEKTOR") != "All sectors" or r.get("AFLOEN") != "All forms of pay"
                or r.get("LONGRP") != "Employee group total" or r.get("KØN") != "Men and women, total"):
            continue
        m = CODE.match(r.get("ARBF") or "")
        if not m or m.group(1) not in uni:
            continue
        code, ind, val = m.group(1), r.get("LØNMÅL"), r.get("INDHOLD")
        try:
            fv = float(val)
        except (TypeError, ValueError):
            continue
        if ind == MONTHLY:
            sal[code] = int(fv * 12)
        elif ind == ANTAL:
            wf[code] = int(round(fv))

    out = {}
    for isco, o in uni.items():
        sv = sal.get(isco)
        out[isco] = {
            "isco": isco, "label_en": o["label_en"],
            "avg_salary": sv,            # standardized monthly ×12 (DKK)，官方均值口径
            "salary_mean": sv,           # DK 仅一档标准化均值，median/mean 同源
            "workforce": wf.get(isco),   # ANTAL：薪资统计覆盖折算全职数（非全就业，粗口径）
            "name_local": None,          # 丹麦语名由 gen_dk_official 的 LLM 出 (da)
            "salary_note": ("Official: Statistics Denmark LONS20, standardized monthly earnings 2024 ×12 "
                            "(all sectors, both sexes). Workforce = full-time employees covered in the "
                            "earnings statistics (ANTAL), a coverage proxy, not total employment."
                            if sv else None),
        }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[build_dk_official] {len(out)} ISCO -> dk_by_isco.json | 薪资 "
          f"{sum(1 for v in out.values() if v['avg_salary'])} | workforce(ANTAL) "
          f"{sum(1 for v in out.values() if v['workforce'])}")


if __name__ == "__main__":
    main()
