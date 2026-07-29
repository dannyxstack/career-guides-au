"""从 PNAD-C 微数据(IBGE)按职业(V4010=COD=ISCO-08 4位)聚合官方薪资+从业人数。
定宽布局(1-based，来自 input_PNADC_trimestral.txt）：
  V1028 @50 w15  个人权重(6整+8小数 → ÷1e8)
  V4010 @152 w4  职业码(COD，直接=ISCO-08 4位)
  VD4002 @410 w1 在业状态(=1 为 Pessoas ocupadas)
  VD4016 @427 w8 主职月习惯收入(reais，空=无现金收入)
输出 downloads/br/br_by_isco.json = { isco: {mean_annual, median_annual, workforce, n} }
薪资年化=月×12；仅用有正收入者算薪资；workforce=在业者权重和。
运行：python -m scripts.build_br_salary
"""
import os, io, json, zipfile
from collections import defaultdict

ZIP = os.path.join("downloads", "br", "PNADC_042025.zip")
OUT = os.path.join("downloads", "br", "br_by_isco.json")
NAMES = os.path.join("downloads", "br", "cod_to_name_pt.json")


def wmedian(pairs):
    """pairs=[(value, weight)] 加权中位数。"""
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
    names = json.load(open(NAMES, encoding="utf-8")) if os.path.exists(NAMES) else {}
    z = zipfile.ZipFile(ZIP)
    txt = [n for n in z.namelist() if n.lower().endswith(".txt")]
    assert txt, f"zip 内无 txt: {z.namelist()}"
    print(f"[br] 读取 {txt[0]}")
    wf = defaultdict(float)          # isco -> 在业权重和(workforce)
    sal = defaultdict(list)          # isco -> [(月收入, 权重)]
    n = defaultdict(int)
    total = 0
    with z.open(txt[0]) as f:
        for line in io.TextIOWrapper(f, encoding="latin-1"):
            total += 1
            occ = line[151:155].strip()
            if not occ or not occ.isdigit():
                continue
            vd4002 = line[409:410].strip()
            if vd4002 != "1":            # 只取在业
                continue
            try:
                w = float(line[49:64])   # V1028 字符串自带小数点(6整.8小数)
            except ValueError:
                continue
            wf[occ] += w
            inc = line[426:434].strip()
            if inc.isdigit() and int(inc) > 0:
                sal[occ].append((int(inc), w))
                n[occ] += 1
    out = {}
    for occ in sorted(wf):
        pairs = sal.get(occ, [])
        mean = (sum(v * w for v, w in pairs) / sum(w for _, w in pairs) * 12) if pairs else None
        med = (wmedian(pairs) * 12) if pairs else None
        out[occ] = {
            "mean_annual": round(mean) if mean else None,
            "median_annual": round(med) if med else None,
            "workforce": round(wf[occ]),
            "n": n.get(occ, 0),
            "name_pt": names.get(occ, ""),
        }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    withsal = sum(1 for v in out.values() if v["mean_annual"])
    print(f"[br] 读 {total} 行；聚合职业 {len(out)}，其中有薪资 {withsal} -> {OUT}")
    ex = next((k for k in out if out[k]["mean_annual"]), None)
    if ex:
        print(f"[br] 样例 {ex} {out[ex]}")


if __name__ == "__main__":
    run()
