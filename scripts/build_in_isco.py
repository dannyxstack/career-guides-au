"""把 PLFS 官方 NCO(3位) 聚合映射到站内 436 ISCO-08 四位 -> downloads/in/in_by_isco.json。

crosswalk：PLFS 2023-24 用 NCO-2015(对齐 ISCO-08)，NCO 3位 = ISCO-08 三位小类。
每个 ISCO 四位码取其三位前缀对应的 NCO 组：
- salary(mean/median)：直接继承三位组的 per-worker 官方年薪（准确）。
- workforce：三位组就业(份额×人口锚定标定) 按"各国现有4位workforce的组内份额"拆到四位(fallback 均分)。
标定：scale = 印度总人口 / PLFS 加权总人口(perv1)，使总就业落到官方量级。
运行：python -m scripts.build_in_isco
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
NCO = os.path.join(REPO, "downloads", "in", "in_by_nco.json")
UNI = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
OUT = os.path.join(REPO, "downloads", "in", "in_by_isco.json")
IN_POP = 1_420_000_000          # 印度 2023-24 约总人口（就业标定锚点）
TOT_WEIGHTED_PERSONS = 9_631_755_823   # build_in_official 打印的 perv1 加权总人口(/100)


def main():
    nco = json.load(open(NCO, encoding="utf-8"))
    uni = json.load(open(UNI, encoding="utf-8"))
    scale = IN_POP / TOT_WEIGHTED_PERSONS
    # 参考份额：各国现有 4 位 workforce 汇总 -> 每个四位码一个权重
    ref = {}
    with get_cursor() as cur:
        cur.execute("SELECT occ_code, SUM(workforce_size) w FROM occupations "
                    "WHERE occ_code_type='ISCO08' AND workforce_size>0 GROUP BY occ_code")
        for r in cur.fetchall():
            ref[str(r["occ_code"])] = float(r["w"] or 0)
    # 按三位组归拢四位兄弟
    from collections import defaultdict
    sibs = defaultdict(list)
    for o in uni:
        sibs[o["isco"][:3]].append(o["isco"])
    out = {}
    for o in uni:
        code = o["isco"]; g = code[:3]
        grp = nco.get(g)
        if not grp:
            out[code] = {"isco": code, "nco_group": g, "workforce": None,
                         "mean_annual": None, "median_annual": None, "basis": "no NCO group (e.g. armed forces)"}
            continue
        # 组内份额（参考各国四位 workforce；全 0 则均分）
        sib = sibs[g]
        rw = {c: ref.get(c, 0.0) for c in sib}
        tot = sum(rw.values())
        share = (rw[code] / tot) if tot > 0 else (1.0 / len(sib))
        grp_emp = (grp.get("workforce") or 0) * scale
        wf = round(grp_emp * share) if grp.get("workforce") else None
        out[code] = {"isco": code, "nco_group": g,
                     "workforce": wf,
                     "mean_annual": grp.get("mean_annual"),
                     "median_annual": grp.get("median_annual"),
                     "basis": f"PLFS NCO {g} (3-digit official); wage inherited, workforce=group×share"}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    wf_tot = sum(v["workforce"] or 0 for v in out.values())
    cov_w = sum(1 for v in out.values() if v["mean_annual"])
    cov_e = sum(1 for v in out.values() if v["workforce"])
    print(f"[build_in_isco] 436 ISCO | scale={scale:.4f} | 有官方薪资 {cov_w} | 有就业 {cov_e} | 就业合计 {wf_tot:,}")
    for c in ("2512", "2411", "5120", "6111", "9412"):
        if c in out:
            v = out[c]; print(f"   {c}: wf={v['workforce']} mean={v['mean_annual']} median={v['median_annual']}")


if __name__ == "__main__":
    main()
