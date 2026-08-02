"""薪资历史 + 5年预测（按国×ISCO 1位大组）→ downloads/salary/_derived/salary_series_by_group.json。

数据源：
- 历史：downloads/salary/{cc}/chart_ready_salary_history.csv 中
  granularity=occupation 且 classification_code=OCU_ISCO08_N（N=0..9）的名义月薪
  （优先 median/monthly，其次 average/monthly）。本币、名义、不做币种换算/通胀调整。
- 预测（估算，标注 isProjected=1）：
  g（名义年增速）= 前瞻CPI(IMF WEO PCPIPCH 2026-2030 均值) + 该大组自身"实际工资趋势"
  实际工资趋势 = 历史名义 CAGR − 同期 CPI 均值，钳制到 [-2%, +3%]（去短窗噪声）。
  预测年 = 最后观测年+1 .. +5：value = last × (1+g)^n。
  说明：官方无分职业前瞻薪资；OECD 前瞻工资仅覆盖成员国且不易统一抓取，故实际工资分量
  取本序列自身趋势，前瞻通胀锚用 IMF WEO（覆盖全部国家）。

输出：{ "AU": { "2": {currency, measure, unit, source, g_pct, points:[[year,value,isProj]...]}, ... }, ... }
键为 App 国家码（大写），二级键为 ISCO 1位大组数字字符串。

用法：PYTHONIOENCODING=utf-8 python scripts/build_salary_history.py
"""
import os, sys, csv, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAL = os.path.join(ROOT, "downloads", "salary")
CPI_RAW = os.path.join(SAL, "_macro", "imf_pcpipch_raw.json")
OUT = os.path.join(SAL, "_derived", "salary_series_by_group.json")

# App 国家码(大写) -> (salary 目录名, IMF ISO3)
CC = {
    "AR": ("ar", "ARG"), "AT": ("at", "AUT"), "AU": ("au", "AUS"), "BE": ("be", "BEL"),
    "BR": ("br", "BRA"), "CA": ("ca", "CAN"), "CH": ("ch", "CHE"), "CL": ("cl", "CHL"),
    "CN": ("cn", "CHN"), "CZ": ("cz", "CZE"), "DE": ("de", "DEU"), "DK": ("dk", "DNK"),
    "EE": ("ee", "EST"), "ES": ("es", "ESP"), "FI": ("fi", "FIN"), "FR": ("fr", "FRA"),
    "GR": ("gr", "GRC"), "HR": ("hr", "HRV"), "HU": ("hu", "HUN"), "ID": ("id", "IDN"),
    "IE": ("ie", "IRL"), "IN": ("in", "IND"), "IS": ("is", "ISL"), "IT": ("it", "ITA"),
    "JP": ("jp", "JPN"), "KR": ("kr", "KOR"), "LT": ("lt", "LTU"), "LU": ("lu", "LUX"),
    "LV": ("lv", "LVA"), "MX": ("mx", "MEX"), "MY": ("my", "MYS"), "NL": ("nl", "NLD"),
    "NO": ("no", "NOR"), "NZ": ("nz", "NZL"), "PL": ("pl", "POL"), "PT": ("pt", "PRT"),
    "RO": ("ro", "ROU"), "SE": ("se", "SWE"), "SG": ("sg", "SGP"), "SI": ("si", "SVN"),
    "SK": ("sk", "SVK"), "TH": ("th", "THA"), "TR": ("tr", "TUR"), "UK": ("uk", "GBR"),
    "US": ("us", "USA"), "VN": ("vn", "VNM"),
}

MIN_YEARS = 3          # 至少 3 个不同年份才建历史线
MIN_LAST_YEAR = 2023   # 最后观测年不早于此（保证新鲜度）
FC_YEARS = 5           # 预测未来 5 年
REAL_TREND_LO, REAL_TREND_HI = -0.02, 0.03  # 实际工资趋势钳制区间


def load_cpi():
    d = json.load(open(CPI_RAW, encoding="utf-8"))
    return d["values"]["PCPIPCH"]  # {ISO3: {year(str): pct}}


def measure_rank(measure, period):
    m, p = (measure or "").lower(), (period or "").lower()
    if p != "monthly":
        return 9
    return {"median": 0, "average": 1, "mean": 1}.get(m, 5)


def load_group_series(cc_dir):
    """返回 {isco1(str): {"points":{year:value}, "currency":..., "measure":...}}，取最优月薪口径。"""
    f = os.path.join(SAL, cc_dir, "chart_ready_salary_history.csv")
    if not os.path.exists(f):
        return {}
    best = {}  # (isco1, year) -> (rank, priority, value, currency, measure, period)
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if r["granularity"] != "occupation":
            continue
        code = r["classification_code"]
        if not code.startswith("OCU_ISCO08_"):
            continue
        isco1 = code.split("_")[-1]
        if isco1 == "0":  # 武装部队，站内职业基本不含
            continue
        try:
            year = int(r["year"]); val = float(r["value"])
        except (ValueError, TypeError):
            continue
        rank = measure_rank(r["measure"], r["period"])
        if rank >= 9:
            continue
        try:
            prio = int(r.get("priority") or 99)
        except ValueError:
            prio = 99
        key = (isco1, year)
        cand = (rank, prio, val, r.get("currency_code") or "", r.get("measure") or "", r.get("period") or "")
        if key not in best or cand[:2] < best[key][:2]:
            best[key] = cand
    groups = collections.defaultdict(lambda: {"points": {}, "currency": "", "measure": "", "period": ""})
    for (isco1, year), (rank, prio, val, cur, meas, per) in best.items():
        g = groups[isco1]
        g["points"][year] = val
        g["currency"], g["measure"], g["period"] = cur, meas, per
    return groups


def cagr(points):
    """名义年复合增速（按首末观测年）。"""
    ys = sorted(points)
    if len(ys) < 2:
        return None
    y0, y1 = ys[0], ys[-1]
    v0, v1 = points[y0], points[y1]
    if v0 <= 0 or v1 <= 0 or y1 == y0:
        return None
    return (v1 / v0) ** (1.0 / (y1 - y0)) - 1.0


def avg_cpi(cpi_row, years):
    vals = [cpi_row[str(y)] / 100.0 for y in years if str(y) in cpi_row and cpi_row[str(y)] is not None]
    return sum(vals) / len(vals) if vals else None


def build():
    cpi = load_cpi()
    out = {}
    report = []
    for app_cc, (cc_dir, iso3) in sorted(CC.items()):
        groups = load_group_series(cc_dir)
        cpi_row = cpi.get(iso3, {})
        f_cpi = avg_cpi(cpi_row, range(2026, 2031))  # 前瞻通胀锚（2026-2030 均值）
        kept = {}
        for isco1, g in groups.items():
            pts = g["points"]
            ys = sorted(pts)
            if len(ys) < MIN_YEARS or ys[-1] < MIN_LAST_YEAR:
                continue
            c = cagr(pts)
            hist_cpi = avg_cpi(cpi_row, ys)
            # 实际工资趋势 = 名义CAGR − 同期CPI；缺 CPI 时退化为 0
            if c is not None and hist_cpi is not None:
                real_trend = c - hist_cpi
            else:
                real_trend = 0.0
            real_trend = max(REAL_TREND_LO, min(REAL_TREND_HI, real_trend))
            gr = (f_cpi if f_cpi is not None else (hist_cpi or 0.0)) + real_trend
            last_y, last_v = ys[-1], pts[ys[-1]]
            points = [[y, round(pts[y], 1), 0] for y in ys]
            for n in range(1, FC_YEARS + 1):
                fv = last_v * (1.0 + gr) ** n
                points.append([last_y + n, round(fv, 1), 1])
            kept[isco1] = {
                "currency": g["currency"], "measure": g["measure"], "period": g["period"],
                "source": "ILOSTAT", "g_pct": round(gr * 100.0, 2),
                "points": points,
            }
        if kept:
            out[app_cc] = kept
            report.append((app_cc, len(kept), min(len(load_group_series(cc_dir)), 10)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("=== salary history + forecast 构建 ===")
    for cc, ng, _ in report:
        print(f"  {cc}: {ng} 大组")
    print(f"\n入库国家 {len(out)} ; 写 {OUT}")


if __name__ == "__main__":
    build()
