#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compute AI Occupational Exposure (AIOE, Felten-Raj-Seamans) for every occupation.

US  : occ_code is a US SOC -> direct join to AIOE (SOC 2010 keyed); SOC codes not
      present in AIOE (mostly 2018-only revisions) fall back to the SOC group average.
      Military (major group 55) has no AIOE and is left NULL by design.
Other countries: national code -> ISCO-08 (4-digit) -> AIOE.
      The ISCO->AIOE hub is built from the O*NET ESCO/ISCO crosswalk (ISCO 4-digit ->
      O*NET-SOC -> SOC -> AIOE, averaged). National -> ISCO crosswalks:
        AU/NZ : ANZSCO 2022 -> ISCO-08            (ABS correspondence Table 4)
        DE    : KldB 2010 (5-Steller) -> ISCO-08  (BA Umsteigeschluessel, agg to 4-Steller)
        UK    : SOC 2020 -> SOC 2010 -> ISCO-08    (ONS relationship + ONS SOC2010-ISCO08)
        CA    : NOC 2021 -> NOC 2016/2011 -> ISCO  (StatCan correspondence + NOC2011-ISCO)
      A national code with no direct ISCO match falls back to its broader group
      (shorter code prefix). Whatever still has no AIOE is left NULL.

Reads prepared crosswalk JSONs from .codex_tmp/ (built by the data-prep steps),
UPDATEs occupation_ai.aioe_score / aioe_pct / aioe_soc / aioe_method, idempotent.
"""
import os, json, bisect, statistics, collections, argparse
import pymysql
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, '.codex_tmp')
load_dotenv(os.path.join(ROOT, '.env'))


def J(name):
    with open(os.path.join(TMP, name), encoding='utf-8') as f:
        return json.load(f)


# ---- AIOE reference (SOC 2010 keyed) + percentile mapper -------------------
AIOE = J('aioe_soc.json')                 # {soc6: {title, aioe(z), pct}}
ISCO_AIOE = J('isco4_aioe.json')          # {isco4: {z, pct, n}}
_FB = J('aioe_fallback.json')
SOC_GRP = {int(k): v for k, v in _FB['fallback'].items()}   # {5|4|2: {prefix: meanz}}
ZS = sorted(_FB['zs'])


def z2pct(z):
    return round(100 * bisect.bisect_right(ZS, z) / len(ZS))


def soc_to_aioe(soc6):
    """US SOC6 -> (z, pct, matched_soc, granularity)."""
    if soc6 in AIOE:
        v = AIOE[soc6]
        return v['aioe'], int(v['pct']), soc6, 'exact'
    for n in (5, 4, 2):
        z = SOC_GRP[n].get(soc6[:n])
        if z is not None:
            return z, z2pct(z), soc6, f'grp{n}'
    return None, None, None, None


# ---- national -> ISCO crosswalks (+ prefix fallback index) -----------------
XWALK = {
    'AU': J('anzsco_isco.json'),
    'NZ': J('anzsco_isco.json'),
    'DE': J('xwalk_de.json'),
    'UK': J('xwalk_uk.json'),
    'CA': J('xwalk_ca.json'),
}
# CA: also allow 4-digit legacy NOC codes via the NOC2011->ISCO table directly.
try:
    XWALK['CA'] = dict(XWALK['CA'])
    XWALK['CA'].update({k: v for k, v in J('xwalk_ca_noc4.json').items()
                        if k not in XWALK['CA']})
except FileNotFoundError:
    pass

PREFIX = {}
for cc, m in XWALK.items():
    idx = collections.defaultdict(set)
    for code, iscos in m.items():
        for n in (4, 2, 1):
            idx[code[:n]].update(iscos)
    PREFIX[cc] = idx


def code_to_iscos(cc, code):
    m = XWALK[cc]
    if code in m:
        return m[code], 'direct'
    idx = PREFIX[cc]
    for n in (4, 2, 1):
        if code[:n] in idx and len(code) > n:
            return sorted(idx[code[:n]]), f'prefix{n}'
    return None, None


def iscos_to_aioe(iscos):
    zs = [ISCO_AIOE[i]['z'] for i in iscos if i in ISCO_AIOE]
    if not zs:
        return None, None
    z = round(statistics.mean(zs), 4)
    return z, z2pct(z)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--country', help='limit to one country code (AU/CA/NZ/UK/DE/US)')
    ap.add_argument('--dry', action='store_true', help='compute only, no DB writes')
    args = ap.parse_args()

    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST'), port=int(os.getenv('MYSQL_PORT')),
        user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'), charset='utf8mb4')
    cur = conn.cursor()

    countries = [args.country] if args.country else ['US', 'AU', 'NZ', 'UK', 'DE', 'CA']
    grand = collections.Counter()
    for cc in countries:
        cur.execute("select id, occ_code from occupations where country_code=%s", (cc,))
        rows = cur.fetchall()
        n_ok = n_fb = n_miss = 0
        for oid, code in rows:
            if cc == 'US':
                z, pct, soc, how = soc_to_aioe(code)
                method = 'direct'
                aioe_soc = soc if z is not None else None
            else:
                iscos, how = code_to_iscos(cc, code)
                if iscos is None:
                    z = pct = None
                    aioe_soc = None
                else:
                    z, pct = iscos_to_aioe(iscos)
                    aioe_soc = ('ISCO:' + ','.join(iscos))[:12] if z is not None else None
                method = 'crosswalk'
            if z is None:
                n_miss += 1
                continue
            if how in ('exact', 'direct'):
                n_ok += 1
            else:
                n_fb += 1
            if not args.dry:
                cur.execute(
                    "update occupation_ai set aioe_score=%s, aioe_pct=%s, "
                    "aioe_soc=%s, aioe_method=%s where occupation_id=%s",
                    (round(z, 4), pct, aioe_soc, method, oid))
        if not args.dry:
            conn.commit()
        print(f'{cc:3} total {len(rows):4}  direct {n_ok:4}  fallback {n_fb:4}  miss {n_miss:3}')
        grand['total'] += len(rows); grand['ok'] += n_ok
        grand['fb'] += n_fb; grand['miss'] += n_miss
    print(f'ALL total {grand["total"]}  direct {grand["ok"]}  fallback {grand["fb"]}  miss {grand["miss"]}')
    conn.close()


if __name__ == '__main__':
    main()
