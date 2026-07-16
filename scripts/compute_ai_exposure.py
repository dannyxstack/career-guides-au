#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compute a unified, generative-AI-era GenAI-exposure index for every occupation
and write it to occupation_ai_v2 (aioe_score / aioe_pct / aioe_soc / aioe_method).

Supersedes compute_aioe.py (Felten 2021, pre-generative-AI). Sources & method:

  * ILO WP140 (2025, CC BY 4.0) -- authoritative anchor for the 112 ISCO-08
    occupations with meaningful GenAI exposure (mean 0-1).
  * Eloundou "GPTs are GPTs" (2023, MIT) -- continuous task-based LLM-exposure
    "beta" (0-1) across ~800 SOC occupations; also the fixed GLOBAL reference
    distribution used to turn a raw 0-1 score into a 0-100 percentile.

Per occupation the raw 0-1 exposure is chosen as (ILO takes precedence, then
Eloundou fills continuously):
  US                         -> Eloundou beta by SOC-6 (group-mean fallback)
  ISCO-reachable countries   -> national code -> ISCO-08 4-digit, then
                                ILO mean  (if any mapped ISCO is in ILO's 112)
                                else Eloundou beta via the ESCO/O*NET ISCO->SOC bridge
  no crosswalk yet (ES/FR/JP/KR) -> left NULL, method 'pending_crosswalk'
                                (downstream falls back to the LLM exposure score)

The raw score is mapped to aioe_pct (0-100) by its percentile in the fixed
Eloundou reference distribution -- one global anchor for all countries, so the
numbers stay cross-country comparable. aioe_score stores the raw 0-1 value.

Reads .codex_tmp/genai_ref.json (built by build_genai_refs.py) + national->ISCO
crosswalk JSONs. Idempotent. Use --dry to preview without writing.
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


REF = J('genai_ref.json')
ILO = REF['ilo']                       # {isco4: mean}
SOC_BETA = REF['soc_beta']             # {soc6: beta}
ISCO_BETA = REF['isco_beta']           # {isco4: beta}
REF_DIST = REF['ref_dist']             # sorted global reference CDF
N_REF = len(REF_DIST)

# SOC group means (for US SOC codes missing from Eloundou) at decreasing detail.
SOC_GRP = {}
for n in (5, 2):
    acc = collections.defaultdict(list)
    for soc6, b in SOC_BETA.items():
        acc[soc6[:n]].append(b)
    SOC_GRP[n] = {k: statistics.mean(v) for k, v in acc.items()}


def raw_to_pct(raw):
    return round(100 * bisect.bisect_right(REF_DIST, raw) / N_REF)


# ---- national -> ISCO-08 4-digit -------------------------------------------
# Countries whose stored occ_code IS ISCO-08 already need no crosswalk.
ISCO_NATIVE = {'IE', 'IT', 'NL', 'CH'}
XWALK = {
    'AU': J('anzsco_isco.json'),
    'NZ': J('anzsco_isco.json'),
    'DE': J('xwalk_de.json'),
    'UK': J('xwalk_uk.json'),
    'CA': J('xwalk_ca.json'),
}
try:
    XWALK['CA'] = dict(XWALK['CA'])
    XWALK['CA'].update({k: v for k, v in J('xwalk_ca_noc4.json').items()
                        if k not in XWALK['CA']})
except FileNotFoundError:
    pass
# Optional national->ISCO bridges for the remaining countries (added when sourced).
#   ES : official INE CNO-11 <-> ISCO-08 correspondence table.
#   FR/JP/KR : LLM-assisted map to the official ISCO-08 structure (no clean official
#              statistical-office table was obtainable in this environment); the score
#              itself is still ILO/Eloundou, but the ISCO routing is LLM-sourced -> tagged
#              with a '_llmmap' suffix so downstream/about pages can disclose it.
LLM_XWALK = {'FR', 'JP', 'KR'}
for cc, fname in (('ES', 'xwalk_es.json'), ('FR', 'xwalk_fr.json'),
                  ('JP', 'xwalk_jp.json'), ('KR', 'xwalk_kr.json')):
    try:
        XWALK[cc] = J(fname)
    except FileNotFoundError:
        pass

PREFIX = {}
for cc, m in XWALK.items():
    idx = collections.defaultdict(set)
    for code, iscos in m.items():
        for n in (4, 2, 1):
            idx[code[:n]].update(iscos)
    PREFIX[cc] = idx


def to_iscos(cc, code):
    """Return (list_of_isco4, how) or (None, None)."""
    if cc in ISCO_NATIVE:
        iso = code.strip()[:4]
        return ([iso], 'direct') if iso.isdigit() else (None, None)
    m = XWALK.get(cc)
    if not m:
        return None, None
    if code in m:
        return m[code], 'direct'
    idx = PREFIX[cc]
    for n in (4, 2, 1):
        if len(code) > n and code[:n] in idx:
            return sorted(idx[code[:n]]), f'prefix{n}'
    return None, None


def soc_to_beta(soc6):
    if soc6 in SOC_BETA:
        return SOC_BETA[soc6], 'eloundou_soc', soc6
    for n in (5, 2):
        b = SOC_GRP[n].get(soc6[:n])
        if b is not None:
            return b, f'eloundou_socgrp{n}', soc6
    return None, None, None


def occ_exposure(cc, code):
    """Return (raw01, method, ref_key) or (None, None, None)."""
    if cc == 'US':
        return soc_to_beta(code)
    iscos, how = to_iscos(cc, code)
    if not iscos:
        return None, None, None
    ilo_hits = {i: ILO[i] for i in iscos if i in ILO}
    if ilo_hits:                                     # ILO precedence (authoritative)
        raw = max(ilo_hits.values())
        return raw, 'ilo_genai', 'ISCO:' + ','.join(sorted(ilo_hits))
    elo_hits = [ISCO_BETA[i] for i in iscos if i in ISCO_BETA]
    if elo_hits:                                     # Eloundou continuous fill
        return round(statistics.mean(elo_hits), 4), 'eloundou_isco', \
            'ISCO:' + ','.join(sorted(i for i in iscos if i in ISCO_BETA))
    return None, None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--country', help='limit to one country code')
    ap.add_argument('--dry', action='store_true', help='compute only, no DB writes')
    args = ap.parse_args()

    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST'), port=int(os.getenv('MYSQL_PORT')),
        user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'), charset='utf8mb4')
    cur = conn.cursor()

    if args.country:
        countries = [args.country]
    else:
        cur.execute("select distinct country_code from occupations order by country_code")
        countries = [r[0] for r in cur.fetchall()]

    grand = collections.Counter()
    for cc in countries:
        # anzsco_code holds the clean national code (occ_code may be a synthesised
        # "parent-role" code that would miss the crosswalk); fall back to occ_code.
        cur.execute("select o.id, coalesce(nullif(o.anzsco_code,''), o.occ_code) "
                    "from occupations o where o.country_code=%s", (cc,))
        rows = cur.fetchall()
        by_method = collections.Counter()
        n_ok = n_pending = 0
        for oid, code in rows:
            code = str(code)
            raw, method, key = occ_exposure(cc, code)
            if raw is None:
                n_pending += 1
                by_method['pending_crosswalk'] += 1
                if not args.dry:
                    cur.execute("update occupation_ai_v2 set aioe_score=NULL, aioe_pct=NULL, "
                                "aioe_soc=NULL, aioe_method='pending_crosswalk' "
                                "where occupation_id=%s", (oid,))
                continue
            if cc in LLM_XWALK and method in ('ilo_genai', 'eloundou_isco'):
                method += '_llmmap'
            pct = raw_to_pct(raw)
            n_ok += 1
            by_method[method] += 1
            if not args.dry:
                cur.execute(
                    "update occupation_ai_v2 set aioe_score=%s, aioe_pct=%s, "
                    "aioe_soc=%s, aioe_method=%s where occupation_id=%s",
                    (round(raw, 4), pct, (key or '')[:20], method, oid))
        if not args.dry:
            conn.commit()
        print(f"{cc:3} n={len(rows):4} scored={n_ok:4} pending={n_pending:4}  "
              + ' '.join(f'{k}={v}' for k, v in sorted(by_method.items())))
        grand['n'] += len(rows); grand['ok'] += n_ok; grand['pending'] += n_pending
    print(f"ALL n={grand['n']} scored={grand['ok']} pending={grand['pending']}")
    conn.close()


if __name__ == '__main__':
    main()
