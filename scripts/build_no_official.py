"""装配挪威(NO)官方薪资+就业 -> downloads/no/no_by_isco.json（零 LLM，确定性映射）。

官方源：
- 薪资：Statistics Norway 表 11418《Monthly earnings, by measuring method, occupation…》2025。
        取 median / average 月薪（Sum all sectors, Both sexes, All employees），×12 得本币年薪。
- 就业：Statistics Norway 表 11658，2026 Q1 各职业 employees（Both sexes, All ages）。
STYRK-08 四位与 ISCO-08 四位一致，直接对齐（无需 crosswalk）。

本地名（挪威语）官方英文 API 不提供 → 留空，由 gen_no_official 的 DeepSeek 出 name_local(nb)。
avg_salary 取 median（对薪资分布更稳健）；mean 另存供后续 median/mean 双档入库。

运行：python -m scripts.build_no_official
产物：downloads/no/no_by_isco.json
"""
import os, csv, io, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UNIVERSE = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
SAL = os.path.join(REPO, "downloads", "no", "occupation_salary_2025.csv")
JOBS = os.path.join(REPO, "downloads", "no", "occupation_jobs_2026q1.csv")
OUT = os.path.join(REPO, "downloads", "no", "no_by_isco.json")

CODE = re.compile(r'^(\d{4})\s+(.*)')


def read(path):
    # SSB CSV 为 Windows-1252（挪威语 ø/å）。
    return list(csv.DictReader(io.StringIO(open(path, "rb").read().decode("latin-1"))))


def main():
    uni = {o["isco"]: o for o in json.load(open(UNIVERSE, encoding="utf-8"))}
    med, mean = {}, {}
    for r in read(SAL):
        if r.get("sector") != "Sum all sectors" or r.get("sex") != "Both sexes":
            continue
        if r.get("contractual/usual working hours per week") != "All employees":
            continue
        m = CODE.match(r.get("occupation") or "")
        if not m or m.group(1) not in uni:
            continue
        code = m.group(1)
        try:
            v = int(float(r["Monthly earnings (NOK) 2025"])) * 12
        except (TypeError, ValueError):
            continue
        if r["measuring method"] == "Median":
            med[code] = v
        elif r["measuring method"] == "Average":
            mean[code] = v

    wf = {}
    for r in read(JOBS):
        if r.get("sex") != "Both sexes" or r.get("age") != "All ages":
            continue
        m = CODE.match(r.get("occupation") or "")
        if not m or m.group(1) not in uni:
            continue
        try:
            wf[m.group(1)] = int(float(r["Number of employees 2026K1"]))
        except (TypeError, ValueError):
            continue

    out = {}
    for isco, o in uni.items():
        mv, mnv = med.get(isco), mean.get(isco)
        out[isco] = {
            "isco": isco, "label_en": o["label_en"],
            "avg_salary": mv,            # median 年薪 (NOK)，官方
            "salary_mean": mnv,          # mean 年薪 (NOK)，官方（后续 median/mean 双档）
            "workforce": wf.get(isco),   # employees 2026 Q1，官方
            "name_local": None,          # 挪威语名由 gen_no_official 的 LLM 出 (nb)
            "salary_note": ("Official: Statistics Norway table 11418, median monthly earnings 2025 "
                            "×12 (all sectors, both sexes). Employment: table 11658 (2026 Q1)."
                            if mv else None),
        }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    covered_s = sum(1 for v in out.values() if v["avg_salary"])
    covered_w = sum(1 for v in out.values() if v["workforce"])
    print(f"[build_no_official] {len(out)} ISCO -> no_by_isco.json | median薪资 {covered_s} | "
          f"mean {sum(1 for v in out.values() if v['salary_mean'])} | workforce {covered_w}")


if __name__ == "__main__":
    main()
