"""从 PLFS 2023-24 个人微数据聚合印度官方职业就业/工资 -> downloads/in/in_by_nco.json（不估算）。

源：downloads/in/CSV_data_PLFS_2023_2024.zip 内 perv1.csv（常用状态+个人访问1，418159 条/139 列）。
列（据 NADA 变量元数据）：
- b5pt1q3 常用主要活动状态码；b5pt1q6 常用主要职业 NCO(3位, NCO-2004)；b5pt1q5 NIC 行业
- b6q7 CWS 职业 NCO；b6q9 正规受雇/工资性月收入(INR)；mult 乘数(权重)
就业口径：常用主要状态在业码 {11,12,21,31,41,51} 按 NCO 3位 加权(mult/100)汇总。
工资口径：b6q9>0(正规工资)者，按 CWS 职业 b6q7 加权 mean/median，月×12 年化。
运行：python -m scripts.build_in_official
"""
import os, csv, zipfile, io, json, statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ZIP = os.path.join(REPO, "downloads", "in", "CSV_data_PLFS_2023_2024.zip")
MEMBER = "CSV_data_PLFS_2023_2024/perv1.csv"
OUT = os.path.join(REPO, "downloads", "in", "in_by_nco.json")
EMPLOYED = {"11", "12", "21", "31", "41", "51"}  # 常用主要状态：在业
WSCALE = 100.0  # PLFS 乘数 /100 = 代表人数（下方按全国总量校验）


def wmedian(pairs):
    """pairs=[(value, weight)]，加权中位数。"""
    pairs = sorted(pairs)
    tot = sum(w for _, w in pairs)
    if tot <= 0:
        return None
    acc = 0
    for v, w in pairs:
        acc += w
        if acc >= tot / 2:
            return v
    return pairs[-1][0]


def main():
    emp = defaultdict(float)                 # NCO3 -> 加权就业人数
    wage_rows = defaultdict(list)            # NCO3 -> [(月薪, 权重)]
    n_emp = defaultdict(int)
    with zipfile.ZipFile(ZIP) as z, z.open(MEMBER) as fh:
        rd = csv.reader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"))
        hdr = next(rd)
        ix = {n: i for i, n in enumerate(hdr)}
        c_st, c_nco, c_cwsocc, c_wage, c_mult = (ix["b5pt1q3_perv1"], ix["b5pt1q6_perv1"],
                                                 ix["b6q7_perv1"], ix["b6q9_perv1"], ix["mult_perv1"])
        tot_w = 0.0
        for r in rd:
            try:
                w = float(r[c_mult] or 0) / WSCALE
            except ValueError:
                continue
            tot_w += w
            st = r[c_st].strip()
            nco = r[c_nco].strip()
            if st in EMPLOYED and nco:
                emp[nco] += w
                n_emp[nco] += 1
            wg = r[c_wage].strip()
            occ = r[c_cwsocc].strip()
            if wg and occ and wg not in ("0", ""):
                try:
                    m = float(wg)
                except ValueError:
                    continue
                if m > 0:
                    wage_rows[occ].append((m * 12, w))
    out = {}
    for nco in sorted(set(emp) | set(wage_rows)):
        wr = wage_rows.get(nco, [])
        wtot = sum(w for _, w in wr)
        mean = round(sum(v * w for v, w in wr) / wtot) if wtot else None
        med = round(wmedian(wr)) if wr else None
        out[nco] = {"nco2004": nco, "workforce": round(emp.get(nco, 0)),
                    "mean_annual": mean, "median_annual": med,
                    "n_emp": n_emp.get(nco, 0), "n_wage": len(wr)}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total_emp = sum(v["workforce"] for v in out.values())
    print(f"[build_in] NCO3 组数 {len(out)} | 加权总人口 {tot_w:,.0f} | 加权总就业 {total_emp:,.0f} "
          f"| 有工资的组 {sum(1 for v in out.values() if v['mean_annual'])}")
    # 校验样例
    for nco in ("611", "512", "241", "251"):
        if nco in out:
            v = out[nco]; print(f"   NCO {nco}: 就业 {v['workforce']:,} | mean {v['mean_annual']} | median {v['median_annual']} (n_wage={v['n_wage']})")


if __name__ == "__main__":
    main()
