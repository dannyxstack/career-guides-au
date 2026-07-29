"""非 EU 国降级底座：ILOSTAT 大类(ISCO-08 1 位)就业 -> downloads/{cc}/{cc}_by_isco.json。

数据源：downloads/{cc}/ilostat_annual_all_labour.rds（Rilostat 导出，含 EMP_TEMP_SEX_OCU_NB）。
ILOSTAT 对这些国只到 ISCO-08 一位大类(OCU_ISCO08_1..9)。降级（零 LLM，同 Eurostat/CN 口径）：
- workforce : 大类就业(千人×1000) 按「各国现有四位 workforce 组内份额」拆到四位（跨国份额）。
- avg_salary: 留空（ILOSTAT 无四位职业薪资）。
- name_local: 留空（本底座）；有本国官方本地名的国另补。

选源规则：同一指标多来源/多年，取 OCU_ISCO08_TOTAL 最大的 source（真实全就业口径），
再取该 source 下最新、9 大类齐备的年份。

用法：python -m scripts.build_ilostat_official --country MY
产物：downloads/{cc}/{cc}_by_isco.json
"""
import os, sys, json, argparse
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.build_eurostat_official import ref_shares

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UNIVERSE = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
MAJORS = [str(i) for i in range(1, 10)]


def _read_rds(path):
    import rdata
    from rdata.conversion._conversion import DEFAULT_CLASS_MAP

    def safe_factor(obj, attrs):
        lv = list(attrs["levels"])
        out = []
        for c in np.asarray(obj).tolist():
            try:
                ci = int(c)
            except Exception:
                out.append(None); continue
            out.append(lv[ci - 1] if 1 <= ci <= len(lv) else None)
        return np.array(out, dtype=object)

    cmap = dict(DEFAULT_CLASS_MAP); cmap["factor"] = safe_factor
    d = rdata.read_rds(path, constructor_dict=cmap, default_encoding="utf-8")
    d.columns = [str(c) for c in d.columns]
    return d


def major_employment(cc):
    """返回 {major(str '1'..'9'): persons}，取真实全就业口径的最新年。"""
    path = os.path.join(REPO, "downloads", cc.lower(), "ilostat_annual_all_labour.rds")
    d = _read_rds(path)
    d = d[(d["sex"] == "SEX_T") & d["classif1"].astype(str).str.startswith("OCU_ISCO08_") & d["obs_value"].notna()]
    dm = d[d["classif1"].isin([f"OCU_ISCO08_{mj}" for mj in MAJORS])]
    if dm.empty:
        raise SystemExit(f"{cc}: 无 ISCO-08 大类数据")
    tots = d[d["classif1"] == "OCU_ISCO08_TOTAL"]["obs_value"]
    cap = float(tots.max()) * 1000.0 * 1.5 if not tots.empty else None   # 上限：剔除异常膨胀源

    def combo_map(src, yr):
        rows = dm[(dm["source"] == src) & (dm["time"] == yr)]
        mp = {}
        for mj in MAJORS:
            r = rows[rows["classif1"] == f"OCU_ISCO08_{mj}"]
            if not r.empty:
                mp[mj] = float(r["obs_value"].iloc[0]) * 1000.0   # 千人 -> 人
        return mp

    cands = []
    for src in sorted(set(dm["source"])):
        for yr in set(dm[dm["source"] == src]["time"]):
            mp = combo_map(src, yr)
            s = sum(mp.values())
            if len(mp) >= 8 and (cap is None or s <= cap):
                cands.append((src, yr, s, mp))
    if not cands:
        raise SystemExit(f"{cc}: 无合格大类分解 source/year")
    # best_src = 单年大类之和峰值最大的 source（真实全就业分解，已排除膨胀）
    peak = {}
    for src, yr, s, _ in cands:
        peak[src] = max(peak.get(src, 0), s)
    best_src = max(peak, key=peak.get)
    thr = 0.5 * peak[best_src]                                  # 剔除该源的残缺年
    src_cands = [c for c in cands if c[0] == best_src and c[2] >= thr]
    src_cands.sort(key=lambda c: (c[1], c[2]), reverse=True)    # 最新年优先
    src, yr, _, mp = src_cands[0]
    return mp, src, yr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    a = ap.parse_args()
    cc = a.country.lower()
    uni = json.load(open(UNIVERSE, encoding="utf-8"))
    shares = ref_shares()
    emp, src, yr = major_employment(cc)
    out = {}
    for o in uni:
        isco = o["isco"]; mj = isco[0]
        emp_tot = emp.get(mj)
        wf = int(emp_tot * shares[isco]) if (emp_tot and isco in shares) else None
        out[isco] = {
            "isco": isco, "label_en": o["label_en"],
            "avg_salary": None, "salary_mean": None,
            "workforce": wf, "name_local": None,
            "salary_note": None,
        }
    d = os.path.join(REPO, "downloads", cc)
    json.dump(out, open(os.path.join(d, f"{cc}_by_isco.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[build_ilostat_official {cc.upper()}] {len(out)} ISCO | source {src} year {yr} | "
          f"大类 {len(emp)}/9 | 有 workforce 四位 {sum(1 for v in out.values() if v['workforce'])}")


if __name__ == "__main__":
    main()
