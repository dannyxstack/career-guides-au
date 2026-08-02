"""CEDEFOP EU outlook 入库：需 crosswalk 的国家 FR / DE / ES。

这三国本地职业编码非 ISCO（FR=ROME, DE=KldB, ES=CNO），无法用 occ_code[:2] 直取 ISCO 2位组，
故各建 code→ISCO2 映射后，复用已下载的 CEDEFOP 国家×ISCO2×逐年曲线（同 load_outlook_eu）。

映射来源：
- DE：官方 `crosswalk/DE_KldB2010_ISCO08.xlsx`（KldB5→ISCO4）；本地 KldB4 取其 5位子级的多数 ISCO2。
- ES：官方 `crosswalk/ES_CNO11_ISCO08.xls`（CNO4→CIUO/ISCO4）；本地 CNO4→ISCO4→取前2位。
- FR：LLM 名称映射缓存 `crosswalk/FR_rome_isco2_llm.json`（ROME→ISCO2，由 build_fr_rome_isco2.py 生成）。
       无缓存则跳过 FR。

表结构/年份/is_projected 同 load_outlook_eu。按 country+source 先删后插，可重复运行。
用法：PYTHONIOENCODING=utf-8 python scripts/load_outlook_eu_xw.py [--dry-run] [--countries DE,ES]
"""
import os, sys, glob, json, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openpyxl, xlrd
from db.connection import get_cursor
from scripts.load_outlook import DDL_SERIES, DDL_META, load_local_occ
from scripts.load_outlook_eu import load_cedefop, SOURCE, EDITION, PROJ_FROM, ISCO2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XW = os.path.join(ROOT, "downloads", "outlook", "EU", "crosswalk")
VALID_ISCO2 = set(ISCO2.values())


def _norm(x):
    if x is None:
        return None
    s = str(x).strip()
    return s[:-2] if s.endswith(".0") else s


def map_DE():
    """本地 KldB4 -> ISCO2（取 5位子级多数）。"""
    f = os.path.join(XW, "DE_KldB2010_ISCO08.xlsx")
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True)["Umsteiger KldB üF 2020 auf ISCO"]
    k4 = collections.defaultdict(collections.Counter)
    for r in ws.iter_rows(min_row=6, values_only=True):
        cells = [_norm(c) for c in r]
        digs = [c for c in cells if c and c.isdigit()]
        k5 = next((c for c in digs if len(c) == 5), None)
        i4 = next((c for c in digs if len(c) == 4), None)
        if k5 and i4 and i4[:2] in VALID_ISCO2:
            k4[k5[:4]][i4[:2]] += 1
    return lambda code: (k4[str(code)[:4]].most_common(1)[0][0] if k4.get(str(code)[:4]) else None)


def map_ES():
    """本地 CNO4 -> ISCO2。"""
    sh = xlrd.open_workbook(os.path.join(XW, "ES_CNO11_ISCO08.xls")).sheet_by_index(0)
    m = {}
    for i in range(3, sh.nrows):
        cno = _norm(sh.cell_value(i, 0))
        ciuo = _norm(sh.cell_value(i, 3))
        if cno and ciuo and cno.isdigit() and ciuo.isdigit() and ciuo[:2] in VALID_ISCO2:
            m[cno] = ciuo[:2]
    return lambda code: m.get(str(code)) or m.get(str(code)[:4])


def map_FR():
    """ROME -> ISCO2，来自 LLM 缓存。无缓存返回 None-mapper。"""
    f = os.path.join(XW, "FR_rome_isco2_llm.json")
    if not os.path.exists(f):
        return None
    m = json.load(open(f, encoding="utf-8"))
    return lambda code: (m.get(str(code)) if m.get(str(code)) in VALID_ISCO2 else None)


MAPPERS = {"DE": map_DE, "ES": map_ES, "FR": map_FR}


def build(local, ced, mappers):
    series, meta = [], []
    report = []
    for cc, make in mappers.items():
        loc = local.get(cc)
        groups = ced.get(cc)
        if not loc or not groups:
            report.append((cc, "skip: 本地或CEDEFOP无数据", 0, 0))
            continue
        mapper = make()
        if mapper is None:
            report.append((cc, "skip: 无映射(FR需先跑 build_fr_rome_isco2.py)", 0, 0))
            continue
        matched = 0
        for occ_code in loc:
            code2 = mapper(occ_code)
            yrs = groups.get(code2) if code2 else None
            if not yrs:
                continue
            matched += 1
            for y in sorted(yrs):
                series.append((cc, str(occ_code), loc[occ_code], y, yrs[y],
                               1 if y >= PROJ_FROM else 0, SOURCE, code2))
            ys = sorted(yrs)
            e0, e1 = yrs.get(2024), yrs.get(ys[-1])
            g = ((e1 - e0) / e0 * 100.0) if (e0 and e1) else None
            note = "ISCO 2-digit group curve via %s crosswalk (shared by group)" % cc
            meta.append((cc, str(occ_code), loc[occ_code], SOURCE, EDITION, code2,
                         2024, ys[-1], g, None, note))
        report.append((cc, "ok", matched, len(loc)))
    return series, meta, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default="FR,DE,ES")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    only = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    mappers = {cc: MAPPERS[cc] for cc in only if cc in MAPPERS}

    local = load_local_occ()
    ced = load_cedefop()
    series, meta, report = build(local, ced, mappers)

    print("=== CEDEFOP EU(xw) 入库计划 ===")
    for cc, status, matched, total in report:
        print("  %s: %s" % (cc, "matched %d/%d (%.0f%%)" % (matched, total, 100 * matched / total)
                            if status == "ok" and total else status))
    ok_cc = sorted({s[0] for s in series})
    print("入库国家 %s ; series=%d meta=%d" % (ok_cc, len(series), len(meta)))
    if args.dry_run:
        print("(dry-run)")
        return
    if not series:
        print("无数据可写。")
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
    print("[OK] wrote %d series + %d meta rows for %s" % (len(series), len(meta), ok_cc))


if __name__ == "__main__":
    main()
