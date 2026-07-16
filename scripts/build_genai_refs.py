#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the GenAI-exposure reference tables used by compute_aioe.py.

Two authoritative, generative-AI-era sources (both openly licensed):

  ILO WP140 (2025, CC BY 4.0) -- "Generative AI and Jobs: A Refined Global
      Index of Occupational Exposure", Gmyrek et al. Annex Table A1 publishes a
      GenAI exposure MEAN (0-1) for the 112 ISCO-08 4-digit occupations with
      meaningful exposure (gradients 1-4). We use these as the authoritative
      anchor for the high-exposure band.

  Eloundou et al. (2023, MIT) -- "GPTs are GPTs", OpenAI. occ_level.csv gives a
      task-based LLM-exposure "beta" score (0-1) for ~800 O*NET-SOC occupations,
      continuous across the whole range. We use it as the continuous backbone
      (and as the fixed global reference distribution for percentile mapping).

Verified alignment: the two scales agree closely where they overlap
(Data Entry Clerks ILO 0.70 / Eloundou 0.696; Accountants 0.51 / 0.54), so the
raw values can be pooled on the same 0-1 scale without rescaling.

Output: .codex_tmp/genai_ref.json
  { "ilo":       {isco4: mean},                 # 112 anchors
    "soc_beta":  {soc6: beta},                  # ~800, continuous
    "isco_beta": {isco4: beta},                 # ISCO4 -> avg Eloundou beta via ESCO/O*NET bridge
    "ref_dist":  [sorted soc_beta values],      # fixed global reference CDF
    "meta": {...} }
"""
import os, re, csv, json, statistics, collections, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, '.codex_tmp')
os.makedirs(TMP, exist_ok=True)

ILO_PDF = 'https://www.ilo.org/sites/default/files/2025-05/WP140_web.pdf'
ELO_CSV = 'https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/occ_level.csv'


def _download(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"  cached {os.path.basename(dest)}")
        return dest
    print(f"  downloading {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, 'wb') as f:
        f.write(r.read())
    return dest


# ---- ILO WP140 Annex Table A1 (ISCO-08 4-digit -> GenAI exposure mean) -------
def build_ilo():
    import pdfplumber
    pdf_path = _download(ILO_PDF, os.path.join(TMP, 'WP140_web.pdf'))
    rows, pending = {}, None
    # "Gradient <1-4> <isco4> <name...> <mean> <sd>"; names sometimes wrap onto
    # the preceding line (no leading Gradient token) -> stitched via `pending`.
    line_re = re.compile(
        r'^Gradient\s+([1-4])\s+(\d{4})\s+(.*?)\s+(0?\.\d+|1(?:\.0+)?)\s+(0?\.\d+|1(?:\.0+)?)\s*$')
    with pdfplumber.open(pdf_path) as pdf:
        for i, pg in enumerate(pdf.pages):
            t = pg.extract_text() or ''
            if 'Gradient' not in t:
                continue
            for ln in t.splitlines():
                ln = ln.strip()
                m = line_re.match(ln)
                if m:
                    isco4, mean = m.group(2), float(m.group(4))
                    rows[isco4] = mean
                    pending = None
                elif ln and not ln.startswith(('Gradient', 'Exposure', 'ILO Working', '4-digit')) \
                        and not ln[0].isdigit():
                    pending = ln  # wrapped occupation-name prefix (unused, name not needed)
    if len(rows) < 100:
        raise SystemExit(f"ILO extraction looks wrong: only {len(rows)} rows")
    print(f"  ILO: {len(rows)} ISCO-08 occupations, mean range "
          f"{min(rows.values())}-{max(rows.values())}")
    return rows


# ---- Eloundou "GPTs are GPTs" (O*NET-SOC -> beta) ----------------------------
def build_soc_beta():
    csv_path = _download(ELO_CSV, os.path.join(TMP, 'gpts_occ_level.csv'))
    agg = collections.defaultdict(list)
    with open(csv_path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            soc6 = r['O*NET-SOC Code'][:7]              # '11-1011.03' -> '11-1011'
            beta = (float(r['dv_rating_beta']) + float(r['human_rating_beta'])) / 2
            agg[soc6].append(beta)
    beta = {k: round(statistics.mean(v), 4) for k, v in agg.items()}
    print(f"  Eloundou: {len(beta)} SOC-6 occupations, beta range "
          f"{min(beta.values())}-{max(beta.values())}")
    return beta


# ---- ISCO-08 4-digit -> avg Eloundou beta (via ESCO/O*NET-SOC bridge) --------
def build_isco_beta(soc_beta):
    import openpyxl
    wb = openpyxl.load_workbook(os.path.join(TMP, 'esco_onet.xlsx'), read_only=True)
    ws = wb.worksheets[0]
    isco2socs = collections.defaultdict(set)
    header_seen = False
    for r in ws.iter_rows(values_only=True):
        if not header_seen:
            if r and r[0] == 'ESCO/ISCO Code':
                header_seen = True
            continue
        esco, _t, onet = (r[0], r[1], r[2])
        if not esco or not onet:
            continue
        isco4 = str(esco).strip()[:4]
        if not isco4.isdigit():
            continue
        soc6 = str(onet).strip()[:7]
        isco2socs[isco4].add(soc6)
    isco_beta = {}
    for isco4, socs in isco2socs.items():
        bs = [soc_beta[s] for s in socs if s in soc_beta]
        if bs:
            isco_beta[isco4] = round(statistics.mean(bs), 4)
    print(f"  ISCO->beta bridge: {len(isco_beta)} ISCO-08 unit groups")
    return isco_beta


def main():
    print("Building GenAI exposure reference tables ...")
    ilo = build_ilo()
    soc_beta = build_soc_beta()
    isco_beta = build_isco_beta(soc_beta)
    ref_dist = sorted(soc_beta.values())          # fixed global reference CDF
    out = {
        'ilo': ilo,
        'soc_beta': soc_beta,
        'isco_beta': isco_beta,
        'ref_dist': ref_dist,
        'meta': {
            'ilo_source': 'ILO Working Paper 140 (2025), Table A1, CC BY 4.0',
            'ilo_n': len(ilo),
            'eloundou_source': 'Eloundou et al. "GPTs are GPTs" (2023), occ_level.csv, MIT',
            'eloundou_n': len(soc_beta),
            'isco_beta_n': len(isco_beta),
            'ref_dist_n': len(ref_dist),
        },
    }
    dest = os.path.join(TMP, 'genai_ref.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"wrote {dest}")


if __name__ == '__main__':
    main()
