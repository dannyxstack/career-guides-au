"""CEDEFOP Skills Forecast 2026 -> occupation_outlook(逐年序列) + occupation_outlook_meta(头条).

数据源：downloads/outlook/EU/skills2026-country-occupations.json
  （国家 × ISCO-08 2位职业组 × 逐年就业人数 2015-2035，绝对人数）。
详见 downloads/outlook/EU/README.md。

编码对齐：CEDEFOP 只到 ISCO **2位**（职业组名），本地 occupations_v2.json 为 ISCO **4位**。
  仅处理 occ_code_type=='ISCO08' 的国家：取本地 occ_code 前 2 位 = ISCO2 组，绑定该国该组曲线。
  → 同一 2位组下多个 4位职业共用一条曲线（与 AU 4位 Unit Group 同理，粗粒度，note 标注）。
  排除 FR(ROME)/DE(KldB)/ES(CNO)：编码体系不同，前2位≠ISCO2，需另建 crosswalk（暂不入库）。

时间形态：逐年 2015-2035。is_projected：<=2024 实测(LFS)=0；>=2025 预测(nowcast/forecast)=1。
表结构复用 scripts/load_outlook.py（不改表）。按国先 DELETE 再插入，可重复运行。

用法：
  PYTHONIOENCODING=utf-8 python scripts/load_outlook_eu.py --dry-run
  PYTHONIOENCODING=utf-8 python scripts/load_outlook_eu.py
  PYTHONIOENCODING=utf-8 python scripts/load_outlook_eu.py --countries IT,NL
"""
import os, sys, json, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.connection import get_cursor
from scripts.load_outlook import DDL_SERIES, DDL_META, load_local_occ

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "downloads", "outlook", "EU", "skills2026-country-occupations.json")

SOURCE = "CEDEFOP Skills Forecast"
EDITION = "2026"
PROJ_FROM = 2025  # >=2025 记为预测（2025 nowcast, 2026+ forecast）

# CEDEFOP 国名 -> 本地国家码（仅本地存在且为 ISCO08 的国最终会入库）
CC_MAP = {
    "Austria": "AT", "Belgium": "BE", "Bulgaria": "BG", "Croatia": "HR", "Cyprus": "CY",
    "Czechia": "CZ", "Denmark": "DK", "Estonia": "EE", "Finland": "FI", "France": "FR",
    "Germany": "DE", "Greece": "GR", "Hungary": "HU", "Iceland": "IS", "Ireland": "IE",
    "Italy": "IT", "Latvia": "LV", "Lithuania": "LT", "Luxembourg": "LU", "Malta": "MT",
    "Netherlands": "NL", "North Macedonia": "MK", "Norway": "NO", "Poland": "PL",
    "Portugal": "PT", "Romania": "RO", "Slovakia": "SK", "Slovenia": "SI", "Spain": "ES",
    "Sweden": "SE", "Switzerland": "CH", "Türkiye": "TR",
    # "EU-27" 聚合不入库
}

# ISCO-08 2位子大组名 -> 2位码（对齐 CEDEFOP occupation 字段）
ISCO2 = {
    "Chief executives, senior officials and legislators": "11",
    "Administrative and commercial managers": "12",
    "Production and specialised services managers": "13",
    "Hospitality, retail and other services managers": "14",
    "Science and engineering professionals": "21",
    "Health professionals": "22",
    "Teaching professionals": "23",
    "Business and administration professionals": "24",
    "Information and communications technology professionals": "25",
    "Legal, social and cultural professionals": "26",
    "Science and engineering associate professionals": "31",
    "Health associate professionals": "32",
    "Business and administration associate professionals": "33",
    "Legal, social, cultural and related associate professionals": "34",
    "Information and communications technicians": "35",
    "General and keyboard clerks": "41",
    "Customer services clerks": "42",
    "Numerical and material recording clerks": "43",
    "Other clerical support workers": "44",
    "Personal service workers": "51",
    "Sales workers": "52",
    "Personal care workers": "53",
    "Protective services workers": "54",
    "Market-oriented skilled agricultural workers": "61",
    "Market-oriented skilled forestry, fishery and hunting workers": "62",
    "Subsistence farmers, fishers, hunters and gatherers": "63",
    "Building and related trades workers, excluding electricians": "71",
    "Metal, machinery and related trades workers": "72",
    "Handicraft and printing workers": "73",
    "Electrical and electronic trades workers": "74",
    "Food processing, wood working, garment and other craft and related trades": "75",
    "Stationary plant and machine operators": "81",
    "Assemblers": "82",
    "Drivers and mobile plant operators": "83",
    "Cleaners and helpers": "91",
    "Agricultural, forestry and fishery labourers": "92",
    "Labourers in mining, construction, manufacturing and transport": "93",
    "Food preparation assistants": "94",
    "Street and related sales and service workers": "95",
    "Refuse workers and other elementary workers": "96",
}


def load_cedefop():
    """{cc: {isco2: {year:int -> employment:float}}}"""
    rows = json.load(open(DATA, encoding="utf-8"))
    out = collections.defaultdict(dict)
    for r in rows:
        cc = CC_MAP.get(r.get("country_l2"))
        code = ISCO2.get(r.get("occupation"))
        if not cc or not code:
            continue  # EU-27 聚合 / Total 行 / 未识别
        yrs = {int(k): float(v) for k, v in r.items()
               if k.isdigit() and v is not None}
        out[cc][code] = yrs
    return out


def build(local, ced, only):
    all_series, all_meta = [], []
    report = []
    for cc, groups in sorted(ced.items()):
        if only and cc not in only:
            continue
        loc = local.get(cc)
        if not loc:
            report.append((cc, "skip: 本地无该国", 0, 0))
            continue
        # 仅 ISCO08 国：前2位映射
        types = set(loc.values())
        if types != {"ISCO08"}:
            report.append((cc, "skip: 非纯ISCO08(%s)" % ",".join(sorted(types)), 0, 0))
            continue
        matched = 0
        for occ_code in loc:
            code2 = str(occ_code)[:2]
            yrs = groups.get(code2)
            if not yrs:
                continue
            matched += 1
            for y in sorted(yrs):
                proj = 1 if y >= PROJ_FROM else 0
                all_series.append((cc, str(occ_code), "ISCO08", y, yrs[y], proj, SOURCE, code2))
            ys = sorted(yrs)
            e0, e1 = yrs.get(2024), yrs.get(ys[-1])
            g = ((e1 - e0) / e0 * 100.0) if (e0 and e1) else None
            e5 = yrs.get(2029)
            note = ("ISCO 2-digit group curve (shared by all %s occupations); "
                    "5yr growth %.1f%%" % (code2, (e5 - e0) / e0 * 100.0)) if (e0 and e5) \
                else "ISCO 2-digit group curve (shared)"
            all_meta.append((cc, str(occ_code), "ISCO08", SOURCE, EDITION, code2,
                             2024, ys[-1], g, None, note))
        report.append((cc, "ok", matched, len(loc)))
    return all_series, all_meta, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    only = {c.strip().upper() for c in args.countries.split(",") if c.strip()}

    local = load_local_occ()
    ced = load_cedefop()
    series, meta, report = build(local, ced, only)

    print("=== CEDEFOP EU outlook 入库计划 ===")
    for cc, status, matched, total in report:
        if status == "ok":
            print(f"  {cc}: matched {matched}/{total} local occ  ({100*matched/total:.0f}%)")
        else:
            print(f"  {cc}: {status}")
    ok_cc = sorted({s[0] for s in series})
    print(f"\n入库国家 {len(ok_cc)}: {ok_cc}")
    print(f"series={len(series)}  meta={len(meta)}")
    if args.dry_run:
        print("(dry-run, nothing written)")
        return

    with get_cursor() as cur:
        cur.execute(DDL_SERIES)
        cur.execute(DDL_META)
        for cc in ok_cc:
            cur.execute("DELETE FROM occupation_outlook WHERE country=%s AND source=%s", (cc, SOURCE))
            cur.execute("DELETE FROM occupation_outlook_meta WHERE country=%s AND source=%s", (cc, SOURCE))
        cur.executemany(
            "INSERT INTO occupation_outlook (country,occ_code,occ_code_type,year,employment,is_projected,source,source_code)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", series)
        cur.executemany(
            "INSERT INTO occupation_outlook_meta (country,occ_code,occ_code_type,source,source_edition,source_code,base_year,end_year,growth_pct,growth_desc,note)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", meta)
    print(f"[OK] wrote {len(series)} series + {len(meta)} meta rows for {ok_cc}")


if __name__ == "__main__":
    main()
