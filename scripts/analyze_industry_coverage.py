"""
验证 occupation↔industry(NAICS 大类) 多对多关系对本站数据的覆盖度。

链路：
  US 职业   ── occ_code(SOC) ──► BLS 就业矩阵 ──► NAICS 大类集合  （直接）
  非 US 职业 ── aioe_soc(ISCO) ──► ISCO→行业表 ──► NAICS 大类集合  （桥接）
其中 ISCO→行业表由"美国职业本身同时带 SOC+ISCO"这一事实推出（自包含，无需再下载）。

用法：python scripts/analyze_industry_coverage.py
"""
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
IND = os.path.join(ROOT, "downloads", "onet-industry", "us_soc_industry.json")
PCT = 1.0   # 认定"属于该行业"的占比阈值（%）

SECTOR_NAME = {
    "11": "Agriculture, forestry, fishing & hunting", "21": "Mining, quarrying, oil & gas",
    "22": "Utilities", "23": "Construction", "31": "Manufacturing", "32": "Manufacturing",
    "33": "Manufacturing", "42": "Wholesale trade", "44": "Retail trade", "45": "Retail trade",
    "48": "Transportation & warehousing", "49": "Transportation & warehousing",
    "51": "Information", "52": "Finance & insurance", "53": "Real estate",
    "54": "Professional, scientific & technical", "55": "Management of companies",
    "56": "Administrative & waste services", "61": "Educational services",
    "62": "Health care & social assistance", "71": "Arts, entertainment & recreation",
    "72": "Accommodation & food services", "81": "Other services", "92": "Public administration",
    "90": "Government", "99": "Self-employed / special",
}


def iscos(o):
    raw = (o.get("ai") or {}).get("aioe_soc") or ""
    return [c for c in re.findall(r"\d{4}", raw)]


def sectors_at(entry, thr=PCT):
    return {s["naics"] for s in entry.get("sectors", []) if s.get("pct_of_occ", 0) >= thr}


def main():
    ind = json.load(open(IND, encoding="utf-8"))["data"]
    occ = json.load(open(os.path.join(DATA, "occupations_v2.json"), encoding="utf-8"))["occupations"]
    us = [o for o in occ if o["country"] == "US"]

    # ---- US 直接覆盖 ----
    us_any = us_thr = 0
    dens = 0
    for o in us:
        e = ind.get(o["occ_code"], {})
        allsec = {s["naics"] for s in e.get("sectors", [])}
        thrsec = sectors_at(e)
        if allsec:
            us_any += 1
        if thrsec:
            us_thr += 1
            dens += len(thrsec)
    print("=" * 64)
    print("US 直接覆盖 (occ_code=SOC → BLS 矩阵)")
    print(f"  US 职业数            : {len(us)}")
    print(f"  有 ≥1 行业(任意占比) : {us_any}  ({100*us_any/len(us):.1f}%)")
    print(f"  有 ≥1 行业(≥{PCT:.0f}%占比): {us_thr}  ({100*us_thr/len(us):.1f}%)")
    print(f"  平均所属行业数(≥{PCT:.0f}%): {dens/max(1,us_thr):.1f} 个 / 职业")

    # ---- ISCO→行业表：经 O*NET ESCO/ISCO→SOC 官方桥 + BLS SOC→行业 ----
    import openpyxl
    xlsx = os.path.join(ROOT, "downloads", "onet-industry", "ESCO_to_ONET-SOC.xlsx")
    wb = openpyxl.load_workbook(xlsx, read_only=True)
    ws = wb.active
    isco2soc = defaultdict(set)
    for r in ws.iter_rows(values_only=True):
        if not r or not r[0] or not isinstance(r[0], str):
            continue
        m = re.match(r"(\d{4})", r[0])          # ESCO/ISCO Code 前4位=ISCO单位组
        soc = (r[2] or "")
        ms = re.match(r"(\d{2}-\d{4})", str(soc))  # O*NET-SOC 去 .00 后缀
        if m and ms:
            isco2soc[m.group(1)].add(ms.group(1))
    # ISCO→行业：该 ISCO 对应的所有 SOC 的行业并集（≥阈值）
    isco2sec = defaultdict(set)
    for isc, socs in isco2soc.items():
        for s in socs:
            isco2sec[isc] |= sectors_at(ind.get(s, {}))
    isco2sec = {k: v for k, v in isco2sec.items() if v}
    print("\n" + "=" * 64)
    print("ISCO→行业 桥接表（O*NET 官方 ESCO/ISCO→SOC 桥 × BLS SOC→行业）")
    print(f"  ESCO 桥覆盖 ISCO 单位组: {len(isco2soc)} / 436")
    print(f"  可映射到行业的 ISCO 码数: {len(isco2sec)}")

    # ---- 各国桥接覆盖 ----
    percc = defaultdict(lambda: [0, 0, 0])  # total, has_isco, covered
    for o in occ:
        cc = o["country"]
        percc[cc][0] += 1
        ic = iscos(o)
        if ic:
            percc[cc][1] += 1
        if cc == "US":                       # 美国：occ_code=SOC 直连 BLS
            if sectors_at(ind.get(o["occ_code"], {})):
                percc[cc][2] += 1
        elif any(isc in isco2sec for isc in ic):   # 其余：ISCO 桥接
            percc[cc][2] += 1
    print("\n" + "=" * 64)
    print("各国覆盖（US=SOC直连；其余=ISCO桥接到上表）")
    print(f"  {'国':3} {'职业':>5} {'有ISCO':>7} {'可得行业':>9} {'覆盖率':>7}")
    gtot = gcov = 0
    for cc in sorted(percc):
        t, h, c = percc[cc]
        gtot += t; gcov += c
        tag = " (SOC直连)" if cc == "US" else ""
        print(f"  {cc:3} {t:5d} {h:7d} {c:9d} {100*c/t:6.1f}%{tag}")
    print(f"  {'ALL':3} {gtot:5d} {'':7} {gcov:9d} {100*gcov/gtot:6.1f}%")

    # ---- 关系密度（是否真多对多）----
    dist = defaultdict(int)
    for o in us:
        dist[len(sectors_at(ind.get(o["occ_code"], {})))] += 1
    print("\n" + "=" * 64)
    print(f"关系密度（US 职业所属行业数 ≥{PCT:.0f}% 分布）—— 验证是否真·多对多")
    for k in sorted(dist):
        print(f"  {k} 个行业: {dist[k]} 职业")

    # 存一份机读摘要
    out = {
        "us_total": len(us), "us_covered_any": us_any, "us_covered_thr": us_thr,
        "threshold_pct": PCT, "isco_bridge_codes": len(isco2sec),
        "per_country": {cc: {"total": v[0], "has_isco": v[1], "covered": v[2]}
                        for cc, v in percc.items()},
        "global_covered": gcov, "global_total": gtot,
    }
    p = os.path.join(ROOT, "downloads", "onet-industry", "coverage_summary.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n[已写] {p}")


if __name__ == "__main__":
    main()
