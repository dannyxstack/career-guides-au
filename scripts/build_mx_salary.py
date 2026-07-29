"""从 ENOE 微数据(INEGI)按职业(p3=SINCO 4位 → ISCO-08)聚合官方薪资+从业人数。
需合并两表(个人主键 cd_a+cve_ent+con+v_sel+n_hog+h_mud+n_ren）：
  COE1: p3       职业 SINCO 4位码
  SDEM: clase2   在业(=1 población ocupada)；ingocup 月收入；fac_tri 季度扩样权重
SINCO→ISCO 用 downloads/mx/sinco_to_isco.json(含西语名)。
输出 downloads/mx/mx_by_isco.json = { isco: {mean_annual, median_annual, workforce, n, name_es} }
薪资年化=月×12。
运行：python -m scripts.build_mx_salary
"""
import os, io, csv, json, zipfile
from collections import defaultdict

ZIP = os.path.join("downloads", "mx", "enoe_2025_3t_csv.zip")
XWALK = os.path.join("downloads", "mx", "sinco_to_isco.json")
OUT = os.path.join("downloads", "mx", "mx_by_isco.json")
KEY = ["cd_a", "cve_ent", "con", "v_sel", "n_hog", "h_mud", "n_ren"]


def _member(z, key):
    return [x for x in z.namelist() if key in x and "/conjunto_de_datos/" in x and x.endswith(".csv")][0]


def wmedian(pairs):
    if not pairs:
        return None
    pairs = sorted(pairs)
    tot = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= tot / 2:
            return v
    return pairs[-1][0]


def run():
    xw = json.load(open(XWALK, encoding="utf-8"))  # sinco -> {name_es, isco, isco_name_es}
    z = zipfile.ZipFile(ZIP)

    # 1) COE1: 个人主键 -> p3(SINCO)
    occ_of = {}
    with z.open(_member(z, "coe1")) as f:
        rd = csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"))
        for r in rd:
            p3 = (r.get("p3") or "").strip()
            if p3:
                occ_of[tuple(r[k] for k in KEY)] = p3
    print(f"[mx] COE1 职业记录 {len(occ_of)}")

    # 2) SDEM: 合并，按 ISCO 聚合
    wf = defaultdict(float)
    sal = defaultdict(list)
    n = defaultdict(int)
    miss_occ = miss_xw = 0
    with z.open(_member(z, "sdem")) as f:
        rd = csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"))
        for r in rd:
            if (r.get("clase2") or "").strip() != "1":   # 只取在业
                continue
            p3 = occ_of.get(tuple(r[k] for k in KEY))
            if not p3:
                miss_occ += 1
                continue
            x = xw.get(p3)
            if not x or not x["isco"]:
                miss_xw += 1
                continue
            isco = x["isco"]
            try:
                w = float(r.get("fac_tri") or 0)
            except ValueError:
                continue
            wf[isco] += w
            try:
                inc = float(r.get("ingocup") or 0)
            except ValueError:
                inc = 0
            if inc > 0:
                sal[isco].append((inc, w))
                n[isco] += 1

    out = {}
    for isco in sorted(wf):
        pairs = sal.get(isco, [])
        mean = (sum(v * w for v, w in pairs) / sum(w for _, w in pairs) * 12) if pairs else None
        med = (wmedian(pairs) * 12) if pairs else None
        # 西语名:该 ISCO 下任一 SINCO 的 isco_name_es
        name_es = next((v["isco_name_es"] for v in xw.values() if v["isco"] == isco and v["isco_name_es"]), "")
        out[isco] = {
            "mean_annual": round(mean) if mean else None,
            "median_annual": round(med) if med else None,
            "workforce": round(wf[isco]),
            "n": n.get(isco, 0),
            "name_es": name_es,
        }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    withsal = sum(1 for v in out.values() if v["mean_annual"])
    print(f"[mx] 聚合 ISCO {len(out)}，有薪资 {withsal}；未命中职业 {miss_occ}，无交叉 {miss_xw} -> {OUT}")
    for k in ["2512", "2211", "7115", "1111"]:
        if k in out:
            print(f"[mx] {k} {out[k]}")


if __name__ == "__main__":
    run()
