"""通用 EU 降级底座：Eurostat 大类(OC1-9)薪资/就业 -> downloads/{cc}/{cc}_by_isco.json。

Eurostat by-occupation 仅到 ISCO 一位大类。降级映射（零 LLM，同 CN 口径）：
- avg_salary : 该职业所属 ISCO 大类(OC{major}) 的 Eurostat median 月薪(欧元) ×12。整大类共用一值（粗口径）。
- workforce  : 该大类 Eurostat 就业总量(千人) 按「各国现有四位 workforce 的组内份额」拆到四位（跨国份额，同 CN）。
- name_local : 通用底座留空（EU 官方英文标签）；有本国本地名的国由各自增强脚本另补。

四位官方增强（CZ 薪资 / SI 就业 / HU 薪资）在本底座之上由 apply 脚本覆盖。

运行：python -m scripts.build_eurostat_official --country BE
产物：downloads/{cc}/{cc}_by_isco.json
"""
import os, sys, json, argparse, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UNIVERSE = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")


def jstat_getter(d):
    ids, sizes = d["id"], d["size"]
    strides = [1] * len(sizes)
    for i in range(len(sizes) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]
    val = d["value"]

    def get(sel):
        flat = 0
        for dim, stride in zip(ids, strides):
            idx = d["dimension"][dim]["category"]["index"]
            code = sel.get(dim)
            if code is None:
                code = next(iter(idx))          # size-1 维取唯一
            if code not in idx:
                return None
            flat += idx[code] * stride
        return val.get(str(flat), val.get(flat))
    return get


def latest_time(d):
    return list(d["dimension"]["time"]["category"]["index"])[-1]


def ref_shares():
    """各 ISCO 四位在其大类(major)内的跨国就业份额（用 DB 现有国四位 workforce）。"""
    with get_cursor() as cur:
        cur.execute("SELECT occ_code, SUM(workforce_size) w FROM occupations "
                    "WHERE workforce_size>0 GROUP BY occ_code")
        wf = {r["occ_code"]: float(r["w"]) for r in cur.fetchall()}
    by_major = collections.defaultdict(dict)
    for code, w in wf.items():
        if len(code) == 4 and code.isdigit():
            by_major[code[0]][code] = w
    shares = {}
    for major, codes in by_major.items():
        tot = sum(codes.values())
        if tot > 0:
            for c, w in codes.items():
                shares[c] = w / tot
    return shares


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    a = ap.parse_args()
    cc = a.country.lower()
    d = os.path.join(REPO, "downloads", cc)
    uni = json.load(open(UNIVERSE, encoding="utf-8"))
    shares = ref_shares()

    # earnings（可能缺，如 TR）
    med_by_major, mean_by_major = {}, {}
    ep = os.path.join(d, "eurostat_earnings_by_occupation_2022.json")
    if os.path.exists(ep):
        ed = json.load(open(ep, encoding="utf-8"))
        get = jstat_getter(ed)
        for mj in "123456789":
            base = {"nace_r2": "B-S_X_O", "isco08": f"OC{mj}", "worktime": "TOTAL",
                    "age": "TOTAL", "sex": "T"}
            mv = get({**base, "indic_se": "MED_E_EUR"})
            mnv = get({**base, "indic_se": "MEAN_E_EUR"})
            if mv:
                med_by_major[mj] = int(mv * 12)
            if mnv:
                mean_by_major[mj] = int(mnv * 12)

    # employment 大类总量（千人 -> 人）
    emp_by_major = {}
    pp = os.path.join(d, "eurostat_employment_by_occupation_2024_onward.json")
    if os.path.exists(pp):
        pd = json.load(open(pp, encoding="utf-8"))
        get = jstat_getter(pd)
        t = latest_time(pd)
        for mj in "123456789":
            v = get({"sex": "T", "age": "Y_GE15", "wstatus": "EMP", "isco08": f"OC{mj}", "time": t})
            if v:
                emp_by_major[mj] = v * 1000

    out = {}
    for o in uni:
        isco = o["isco"]
        mj = isco[0]
        mv, mnv = med_by_major.get(mj), mean_by_major.get(mj)
        emp_tot = emp_by_major.get(mj)
        wf = int(emp_tot * shares[isco]) if (emp_tot and isco in shares) else None
        out[isco] = {
            "isco": isco, "label_en": o["label_en"],
            "avg_salary": mv,            # 大类 median 月薪(EUR)×12（整大类共用，粗口径）
            "salary_mean": mnv,
            "workforce": wf,             # 大类就业按跨国份额拆四位
            "name_local": None,
            "salary_note": ("Official (major-group level): Eurostat Structure of Earnings 2022, median "
                            "monthly earnings ×12 for the ISCO-08 major group. Employment: Eurostat LFS, "
                            "major-group total split to four-digit by cross-country share." if mv else None),
        }
    outp = os.path.join(d, f"{cc}_by_isco.json")
    json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[build_eurostat_official {cc.upper()}] {len(out)} ISCO | 大类薪资档 {len(med_by_major)}/9 | "
          f"大类就业档 {len(emp_by_major)}/9 | 有薪资四位 {sum(1 for v in out.values() if v['avg_salary'])} | "
          f"有workforce四位 {sum(1 for v in out.values() if v['workforce'])}")


if __name__ == "__main__":
    main()
