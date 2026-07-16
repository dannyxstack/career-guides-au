#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LLM-assisted national-code -> ISCO-08 crosswalk (fallback where no official
statistical-office correspondence table is downloadable in this environment).

Mirrors the ILO WP140 approach of using an AI assistant to place occupations onto
the official ISCO-08 structure. For each occupation we ask DeepSeek to pick the
single best ISCO-08 unit group *from the official 436-code list* (given in the
system prompt), then validate the answer is one of the 436 codes. Invalid/empty
answers are dropped (the occupation stays `pending_crosswalk` and falls back to
the LLM automation_exposure score downstream).

Output: .codex_tmp/xwalk_{cc}.json  ->  {national_code: [isco4]}
Method tag in compute_ai_exposure stays eloundou_isco/ilo_genai, but these are
sourced via an LLM map rather than an official table -- documented in the country
README and the about pages. Swap in an official table later and re-run to upgrade.

Usage:  LLM_PROVIDER=deepseek python -m scripts.build_llm_isco_xwalk --country JP
        (--limit N to trial-run; --batch 20)
"""
import os, sys, json, argparse, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import _deepseek_rest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, '.codex_tmp')
OCC = os.path.join(ROOT, 'site', 'src', 'data', 'occupations_v2.json')
ISCO = os.path.join(TMP, 'isco08_universe.json')


def load_isco():
    uni = json.load(open(ISCO, encoding='utf-8'))
    codes = {u['isco']: u['label_en'] for u in uni}
    listing = '\n'.join(f"{c} {t}" for c, t in sorted(codes.items()))
    return codes, listing


def load_occs(cc):
    occ = json.load(open(OCC, encoding='utf-8'))['occupations']
    out = []
    for o in occ:
        if o.get('country') != cc:
            continue
        code = (o.get('anzsco_code') or o.get('occ_code') or '').strip()
        name = o.get('name_en') or o.get('slug')
        if code and name:
            out.append((code, name, o.get('category') or ''))
    # de-dup by code (keep first)
    seen, uniq = set(), []
    for c, n, cat in out:
        if c not in seen:
            seen.add(c); uniq.append((c, n, cat))
    return uniq


SYSTEM = (
    "You are an expert in international occupational classification (ISCO-08). "
    "Map each given occupation to EXACTLY ONE ISCO-08 4-digit unit group, chosen "
    "ONLY from this official list of 436 unit groups (code then title):\n\n{listing}\n\n"
    "Rules: pick the single closest unit group by the occupation's tasks; the code "
    "MUST be one of the 436 above; if genuinely unclassifiable, use \"0000\". "
    "Return a JSON object mapping each input code to its chosen ISCO code, e.g. "
    "{{\"012\": \"2411\", \"013\": \"1211\"}}."
)


def build(cc, batch, limit, dry):
    codes, listing = load_isco()
    valid = set(codes)
    occs = load_occs(cc)
    if limit:
        occs = occs[:limit]
    system = SYSTEM.replace('{listing}', listing)
    xwalk, bad = {}, []
    for i in range(0, len(occs), batch):
        chunk = occs[i:i + batch]
        prompt = "Classify these occupations:\n" + '\n'.join(
            f"{c} | {n} | {cat}" for c, n, cat in chunk)
        for attempt in range(4):
            try:
                res = _deepseek_rest.complete_json(system, prompt)
                break
            except Exception as e:
                if attempt == 3:
                    print(f"  batch {i} failed: {e}"); res = {}
                else:
                    time.sleep(2 * (attempt + 1))
        for c, n, cat in chunk:
            iso = str(res.get(c, '')).strip()[:4]
            if iso in valid and iso != '0000':
                xwalk[c] = [iso]
            else:
                bad.append((c, n, iso))
        print(f"  {i+len(chunk)}/{len(occs)} mapped (running ok={len(xwalk)} bad={len(bad)})",
              flush=True)
    print(f"{cc}: mapped {len(xwalk)}/{len(occs)}  unmapped {len(bad)}")
    if bad[:8]:
        print("  sample unmapped:", bad[:8])
    if not dry:
        dest = os.path.join(TMP, f'xwalk_{cc.lower()}.json')
        json.dump(xwalk, open(dest, 'w', encoding='utf-8'), ensure_ascii=False)
        print(f"wrote {dest}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--country', required=True)
    ap.add_argument('--batch', type=int, default=20)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    build(a.country.upper(), a.batch, a.limit, a.dry)


if __name__ == '__main__':
    main()
