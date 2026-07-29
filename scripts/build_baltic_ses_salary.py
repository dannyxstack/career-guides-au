"""LV / LT 薪资（零 LLM，宽口径）→ 合并进 downloads/{cc}/{cc}_by_isco.json。

无国家级四位官方薪资，降级用 Eurostat SES（earn_ses_monthly，downloads/{cc}/
eurostat_earnings_by_occupation_2022.json）：isco08 维仅 1 位大类 OC1..OC9（+OC0 军职）。
取 nace=B-S_X_O(全域)、worktime=TOTAL、age=TOTAL、sex=T 的
MED_E_EUR(月中位) 与 MEAN_E_EUR(月均值)，×12 年化，按四位 ISCO 首位摊到该大类下所有四位码。

avg_salary=中位×12，salary_mean=均值×12（与 CZ/北欧口径一致）。
salary_note 明确标注为「宽口径大类基线，非国家级明细」。

运行：python -m scripts.build_baltic_ses_salary --country LV
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def jsonstat_getter(d):
    """返回 get(**{dim:cat}) -> value（支持 value 为 dict 或 list）。"""
    ids = d["id"]
    size = d["size"]
    dim = d["dimension"]
    idxmap = {k: dim[k]["category"]["index"] for k in ids}
    # row-major strides
    strides = [1] * len(size)
    for i in range(len(size) - 2, -1, -1):
        strides[i] = strides[i + 1] * size[i + 1]
    val = d["value"]

    def get(**sel):
        flat = 0
        for i, k in enumerate(ids):
            cat = sel[k]
            pos = idxmap[k][cat]
            flat += pos * strides[i]
        if isinstance(val, dict):
            return val.get(str(flat))
        return val[flat] if 0 <= flat < len(val) else None
    return get


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    a = ap.parse_args()
    cc = a.country.lower()
    DL = os.path.join(HERE, "..", "downloads", cc)
    ses = json.load(open(os.path.join(DL, "eurostat_earnings_by_occupation_2022.json"), encoding="utf-8"))
    get = jsonstat_getter(ses)
    geo = list(ses["dimension"]["geo"]["category"]["index"].keys())[0]
    time = list(ses["dimension"]["time"]["category"]["index"].keys())[0]

    base = dict(freq="A", nace_r2="B-S_X_O", worktime="TOTAL", age="TOTAL", sex="T", geo=geo, time=time)

    # SES 仅提供极宽的 3 组聚合（无 1 位大类）：
    #   OC1-5 非体力(1-5) / OC6-8 技术体力(6-8) / OC7-9 体力(9)。
    # 四位 ISCO 首位 → 组：1-5→OC1-5，6/7/8→OC6-8，9→OC7-9。
    DIG2OC = {**{d: "OC1-5" for d in "12345"}, "6": "OC6-8", "7": "OC6-8", "8": "OC6-8", "9": "OC7-9"}
    grp = {}
    for oc in ("OC1-5", "OC6-8", "OC7-9"):
        med = get(isco08=oc, indic_se="MED_E_EUR", **base)
        mean = get(isco08=oc, indic_se="MEAN_E_EUR", **base)
        if med is not None or mean is not None:
            grp[oc] = (med, mean)

    by = json.load(open(os.path.join(DL, f"{cc}_by_isco.json"), encoding="utf-8"))
    hit = 0
    for code, v in by.items():
        oc = DIG2OC.get(code[0])
        g = grp.get(oc)
        if not g:
            continue
        med, mean = g
        avg = round(med * 12) if med is not None else (round(mean * 12) if mean is not None else None)
        if avg is None:
            continue
        v["avg_salary"] = avg
        v["salary_mean"] = round(mean * 12) if mean is not None else None
        gname = ses["dimension"]["isco08"]["category"]["label"][oc]
        v["salary_note"] = (f"Eurostat SES 2022 broad occupational baseline "
                            f"({gname}); median €{med:,.0f}/month ×12. Not a national four-digit estimate.")
        hit += 1
    json.dump(by, open(os.path.join(DL, f"{cc}_by_isco.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"[{cc.upper()}] SES major groups {sorted(grp)}; filled {hit}/{len(by)} four-digit rows (broad baseline)")


if __name__ == "__main__":
    main()
