"""
固化 occupation → NAICS 行业大类 全量关系表并导出到 site/src/data/。

来源（见 downloads/onet-industry/README.md）：
  us_soc_industry.json      BLS 就业矩阵 SOC→NAICS（美国直连）
  ESCO_to_ONET-SOC.xlsx     O*NET 官方 ISCO→SOC 桥（其余国家）
  occupations_v2.json       本站职业（US 的 occ_code=SOC；其余 aioe_soc=ISCO）

输出：
  site/src/data/occ_industries_v2.json  {occ_id: [{s:sector_id, n:name, p:占该职业%}]}
  site/src/data/industries_v2.json      {sectors:[{id,name,naics,occ_total,by_country}], ...}
"""
import json
import os
import re
from collections import defaultdict

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
DL = os.path.join(ROOT, "downloads", "onet-industry")
PCT = 1.0   # 成员阈值：占该职业就业 ≥1% 才算属于该行业

# NAICS 2 位 → 规范行业（合并 31-33 制造 / 44-45 零售 / 48-49 运输；排除自雇特殊码 99）
CANON = {
    "11": ("agriculture", "Agriculture, forestry, fishing & hunting"),
    "21": ("mining", "Mining, quarrying, oil & gas"),
    "22": ("utilities", "Utilities"),
    "23": ("construction", "Construction"),
    "31": ("manufacturing", "Manufacturing"), "32": ("manufacturing", "Manufacturing"),
    "33": ("manufacturing", "Manufacturing"),
    "42": ("wholesale", "Wholesale trade"),
    "44": ("retail", "Retail trade"), "45": ("retail", "Retail trade"),
    "48": ("transport", "Transportation & warehousing"),
    "49": ("transport", "Transportation & warehousing"),
    "51": ("information", "Information"),
    "52": ("finance", "Finance & insurance"),
    "53": ("real-estate", "Real estate & rental"),
    "54": ("professional", "Professional, scientific & technical services"),
    "55": ("management", "Management of companies & enterprises"),
    "56": ("admin-support", "Administrative & support & waste services"),
    "61": ("education", "Educational services"),
    "62": ("health", "Health care & social assistance"),
    "71": ("arts", "Arts, entertainment & recreation"),
    "72": ("hospitality", "Accommodation & food services"),
    "81": ("other-services", "Other services (except public administration)"),
    "90": ("government", "Government & public sector"),
    "91": ("government", "Government & public sector"),
    "92": ("government", "Government & public sector"),
}


def iscos(o):
    return re.findall(r"\d{4}", (o.get("ai") or {}).get("aioe_soc") or "")


def main():
    ind = json.load(open(os.path.join(DL, "us_soc_industry.json"), encoding="utf-8"))["data"]
    occ = json.load(open(os.path.join(DATA, "occupations_v2.json"), encoding="utf-8"))["occupations"]

    # SOC → 规范行业占比
    #   2 位大类(xx0000)有汇总行 → 直接用；
    #   制造/零售/运输(31-33,44-45,48-49)无 2 位汇总 → 3 位子类(xxx000)求和。
    def canon_sectors(entry):
        two = {}                       # sid -> 2位汇总 pct
        three = defaultdict(float)     # sid -> 3位子类求和 pct
        name = {}
        for s in entry.get("sectors", []):
            c = CANON.get(s["naics"])
            if not c:
                continue
            sid, nm = c; name[sid] = nm
            code = s["naics6"]; p = s.get("pct_of_occ", 0)
            if code.endswith("0000"):
                two[sid] = max(two.get(sid, 0), p)
            else:                      # 3 位子类
                three[sid] += p
        out = {}
        for sid in set(two) | set(three):
            pct = two[sid] if sid in two else three[sid]   # 优先 2 位汇总，缺则子类求和
            if pct >= PCT:
                out[sid] = (round(pct, 1), name[sid])
        return out

    soc2sec = {soc: canon_sectors(e) for soc, e in ind.items()}

    # ISCO → 规范行业（经 ESCO 桥并集）
    wb = openpyxl.load_workbook(os.path.join(DL, "ESCO_to_ONET-SOC.xlsx"), read_only=True)
    isco2socs = defaultdict(set)
    for r in wb.active.iter_rows(values_only=True):
        if not r or not isinstance(r[0], str):
            continue
        mi = re.match(r"(\d{4})", r[0]); ms = re.match(r"(\d{2}-\d{4})", str(r[2] or ""))
        if mi and ms:
            isco2socs[mi.group(1)].add(ms.group(1))
    isco2sec = {}
    for isc, socs in isco2socs.items():
        agg = {}
        for soc in socs:
            for sid, (p, n) in soc2sec.get(soc, {}).items():
                if p > agg.get(sid, (0, n))[0]:
                    agg[sid] = (p, n)
        if agg:
            isco2sec[isc] = agg

    # 逐职业落地
    occ_ind = {}
    sector_meta = {}   # sid -> name
    sector_occ = defaultdict(lambda: defaultdict(int))   # sid -> cc -> count
    sector_total = defaultdict(int)
    for o in occ:
        if o["country"] == "US":
            sec = soc2sec.get(o["occ_code"], {})
        else:
            sec = {}
            for isc in iscos(o):
                for sid, (p, n) in isco2sec.get(isc, {}).items():
                    if p > sec.get(sid, (0, n))[0]:
                        sec[sid] = (p, n)
        if not sec:
            continue
        rows = sorted(([sid, n, p] for sid, (p, n) in sec.items()), key=lambda x: -x[2])
        occ_ind[o["id"]] = [{"s": sid, "n": n, "p": p} for sid, n, p in rows]
        for sid, n, p in rows:
            sector_meta[sid] = n
            sector_occ[sid][o["country"]] += 1
            sector_total[sid] += 1

    # 导出 occ→industry
    p1 = os.path.join(DATA, "occ_industries_v2.json")
    json.dump({"generated_from": "BLS National Employment Matrix + O*NET ESCO/ISCO→SOC bridge",
               "threshold_pct": PCT, "count": len(occ_ind), "occ": occ_ind},
              open(p1, "w", encoding="utf-8"), ensure_ascii=False)

    # 导出行业清单
    sectors = [{"id": sid, "name": sector_meta[sid], "occ_total": sector_total[sid],
                "by_country": dict(sorted(sector_occ[sid].items()))}
               for sid in sorted(sector_meta, key=lambda s: -sector_total[s])]
    p2 = os.path.join(DATA, "industries_v2.json")
    json.dump({"generated_from": "same as occ_industries_v2", "count": len(sectors),
               "sectors": sectors}, open(p2, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"[occ_industries_v2] {len(occ_ind)}/{len(occ)} 职业带行业 ({100*len(occ_ind)/len(occ):.1f}%)")
    print(f"[industries_v2] {len(sectors)} 个行业大类:")
    for s in sectors:
        print(f"  {s['occ_total']:5d}  {s['id']:14} {s['name']}")


if __name__ == "__main__":
    main()
