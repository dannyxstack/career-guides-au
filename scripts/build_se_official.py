"""装配瑞典(SE)官方薪资+就业 -> downloads/se/se_by_isco.json（零 LLM，确定性映射）。

官方源（Statistics Sweden）：
- 薪资：表 LoneSpridSektYrk4AN（TAB5932），2025，Median / Monthly salary(mean) 月薪 SEK，
        sector="0 all sectors", sex="total"。×12 得年薪 SEK。
- 就业：表 YREG50BAS（TAB4449），2024，各 SSYK 四位 employed，sector="all sectors"，
        sex 仅 men/women → 相加得总计。
- 分类：官方 SSYK 2012 → ISCO-08 crosswalk（ssyk2012_to_isco08.xlsx, sheet Grunden）。
        SSYK 基于 ISCO-08，多数四位同码；差异码经官方 crosswalk 归到 ISCO-08。

多对多聚合：对每 ISCO-08 四位，汇集所有映射到它的 SSYK；workforce=就业求和，
median/mean=按就业加权平均（官方 crosswalk 聚合，非估算）。

本地名（瑞典语）官方无干净的四位标准名（titles 为具体职业头衔索引）→ 留空，
由 gen_se_official 的 DeepSeek 出 name_local(sv)。

运行：python -m scripts.build_se_official
产物：downloads/se/se_by_isco.json
"""
import os, io, csv, json, re, zipfile, collections, openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UNIVERSE = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
SE = os.path.join(REPO, "downloads", "se")
OUT = os.path.join(SE, "se_by_isco.json")


def zip_rows(path):
    with zipfile.ZipFile(path) as z:
        n = [x for x in z.namelist() if x.lower().endswith(".csv")][0]
        return list(csv.DictReader(io.StringIO(z.read(n).decode("utf-8-sig", errors="replace"))))


def four(s):
    m = re.match(r'^\s*(\d{4})\b', s or "")
    return m.group(1) if m else None


def main():
    uni = {o["isco"] for o in json.load(open(UNIVERSE, encoding="utf-8"))}

    # crosswalk: SSYK -> {ISCO}
    wb = openpyxl.load_workbook(os.path.join(SE, "ssyk2012_to_isco08.xlsx"), data_only=True)
    ws = wb["Grunden"]
    ssyk2isco = collections.defaultdict(set)
    for row in ws.iter_rows(min_row=2, values_only=True):
        s, i = row[0], row[1]
        if s is None or i is None:
            continue
        s, i = str(s).strip().zfill(4), str(i).strip().zfill(4)
        if re.fullmatch(r'\d{4}', s) and re.fullmatch(r'\d{4}', i):
            ssyk2isco[s].add(i)

    # salary by SSYK (2025, all sectors, total)
    med, mean = {}, {}
    for r in zip_rows(os.path.join(SE, "occupation_salary_2023_2025.zip")):
        if r.get("sector") != "0 all sectors" or r.get("sex") != "total" or r.get("year") != "2025":
            continue
        code = four(r.get("occupation (SSYK 2012)"))
        if not code:
            continue
        # 列名有误导：measure 名在 "observations" 列，数值在 "Average salary and salary dispersion" 列。
        measure = r.get("observations")
        v = (r.get("Average salary and salary dispersion") or "").replace(" ", "")
        try:
            iv = int(float(v)) * 12
        except (TypeError, ValueError):
            continue
        if measure == "Median":
            med[code] = iv
        elif measure == "Monthly salary":
            mean[code] = iv

    # employment by SSYK (2024, all sectors, men+women)
    emp = collections.defaultdict(int)
    have_emp = set()
    for r in zip_rows(os.path.join(SE, "occupation_employment_2020_2024.zip")):
        if r.get("sector") != "all sectors" or r.get("year") != "2024":
            continue
        code = four(r.get("occupation (SSYK 2012)"))
        if not code:
            continue
        try:
            emp[code] += int(float((r.get("Empoyed, number") or "").replace(" ", "")))
            have_emp.add(code)
        except (TypeError, ValueError):
            pass

    # 反向：ISCO -> [SSYK]，按就业加权聚合
    isco2ssyk = collections.defaultdict(list)
    for s, iscos in ssyk2isco.items():
        for i in iscos:
            isco2ssyk[i].append(s)

    uni_list = json.load(open(UNIVERSE, encoding="utf-8"))
    out = {}
    for o in uni_list:
        isco = o["isco"]
        ssyks = isco2ssyk.get(isco, [isco])  # 无 crosswalk 记录则尝试同码
        wf = sum(emp[s] for s in ssyks if s in have_emp) or None

        def wavg(src):
            num = den = 0
            for s in ssyks:
                if s in src:
                    w = emp.get(s, 1) or 1
                    num += src[s] * w
                    den += w
            return int(num / den) if den else None
        mv, mnv = wavg(med), wavg(mean)
        out[isco] = {
            "isco": isco, "label_en": o["label_en"],
            "avg_salary": mv,            # median 年薪 (SEK)，官方
            "salary_mean": mnv,          # mean 年薪 (SEK)，官方
            "workforce": wf,             # employed 2024 (men+women)，官方
            "name_local": None,          # 瑞典语名由 gen_se_official 的 LLM 出 (sv)
            "salary_note": ("Official: Statistics Sweden LoneSpridSektYrk4AN, median monthly salary 2025 "
                            "×12 (all sectors). Employment: YREG50BAS (2024). SSYK 2012→ISCO-08 via "
                            "official crosswalk." if mv else None),
        }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[build_se_official] {len(out)} ISCO -> se_by_isco.json | median薪资 "
          f"{sum(1 for v in out.values() if v['avg_salary'])} | mean {sum(1 for v in out.values() if v['salary_mean'])} | "
          f"workforce {sum(1 for v in out.values() if v['workforce'])}")


if __name__ == "__main__":
    main()
