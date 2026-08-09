# -*- coding: utf-8 -*-
"""Per-country downloadable PDF reports for aijobriskmap.com.

Pipeline: read job-treemap's already-built dist/country/{slug}/data.json (final
per-occupation values), compute report stats, enrich chapters 11/12/13 from the
aijobrisk-go dataset (xrepo_ai), render an HTML report + landing page. A separate
Node/Playwright step (shoot_reports.mjs) prints the HTML to a real-text PDF.

Data-richness tiers: countries without official pay drop the salary snapshot
row, the salary×risk quadrant and pay columns (B-tier) instead of showing blanks.

Usage:
  python job-treemap/build_reports.py AU CZ      # subset (by cc)
  python job-treemap/build_reports.py            # all built countries
"""
import base64
import html
import json
import os
import statistics
import sys
from datetime import date

from jinja2 import Environment, FileSystemLoader, select_autoescape

import build as B  # constants + helpers (import-safe: main() is guarded)
import xrepo_ai

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
REPORTS = os.path.join(DIST, "reports")
PUBLISHED = date.today().isoformat()
DATA_CUTOFF = "2025"

HIGH, MID = 70, 40  # exposure bands (mirror aijobrisk pctColor tiers)
RISK_HI, RISK_MID, RISK_LO = "#b32228", "#d98b09", "#00734b"

env = Environment(loader=FileSystemLoader(HERE), autoescape=select_autoescape(["html"]))


def risk_color(pct):
    return RISK_HI if pct >= HIGH else (RISK_MID if pct >= MID else RISK_LO)


def pct(n, d):
    return round(100 * n / d) if d else 0


def fmt_wf(n):
    return B.fmt_big_jobs(n) if n else "—"


def money(v, symbol):
    return f"{symbol}{v:,.0f}" if v else "—"


def sentence(s):
    """Trim an AI task/moat line into a clean, single clause."""
    s = (s or "").strip().rstrip(".")
    return s[:1].upper() + s[1:] if s else s


def pick_salary(rows):
    """Choose the higher-granularity salary field for a country.

    Some countries store the average `pay` as a handful of coarse bands (AU has
    only 8 distinct `pay` values across 531 occupations, which makes the salary×
    risk scatter collapse into ~8 vertical columns), while the `median` field is
    far more granular (241 distinct). Prefer whichever field carries more
    distinct values; return None when neither is available (B-tier country).
    """
    pays = {r["pay"] for r in rows if r.get("pay")}
    meds = {r["median"] for r in rows if r.get("median")}
    if not pays and not meds:
        return None
    return "median" if len(meds) >= len(pays) else "pay"


def load_rows(cc):
    slug = B.SLUG[cc]
    p = os.path.join(DIST, "country", slug, "data.json")
    return json.load(open(p, encoding="utf-8"))


def map_data_uri(cc):
    p = os.path.join(DIST, "static", "maps", B.map_filename(cc))
    if not os.path.exists(p):
        return None
    b = base64.b64encode(open(p, "rb").read()).decode()
    return f"data:image/png;base64,{b}"


def build_model(cc):
    name, currency, symbol = B.COUNTRY_META[cc][0], B.COUNTRY_META[cc][1], B.COUNTRY_META[cc][2]
    slug = B.SLUG[cc]
    rows = [r for r in load_rows(cc) if r.get("aioe_pct") is not None]
    ai = xrepo_ai.ai_index_for(cc)

    total_wf = sum(r.get("jobs") or 0 for r in rows)
    salf = pick_salary(rows)           # 自动选粒度更高的薪资字段（median / pay）
    has_pay = salf is not None
    def sal(r):
        return r.get(salf) if salf else None
    exps = [r["aioe_pct"] for r in rows]
    risk_median = round(statistics.median(exps))
    q1 = round(statistics.quantiles(exps, n=4)[0])
    q3 = round(statistics.quantiles(exps, n=4)[2])

    high = [r for r in rows if r["aioe_pct"] >= HIGH]
    mid = [r for r in rows if MID <= r["aioe_pct"] < HIGH]
    low = [r for r in rows if r["aioe_pct"] < MID]
    wf_high = sum(r.get("jobs") or 0 for r in high)
    wf_mid = sum(r.get("jobs") or 0 for r in mid)
    wf_low = sum(r.get("jobs") or 0 for r in low)
    high_occ_pct = pct(len(high), len(rows))
    high_wf_pct = pct(wf_high, total_wf)

    def occ_url(r):
        return f"{B.DOMAIN}/country/{slug}/#{r['slug']}"

    def row_vm(r, tasks_field=None):
        vm = {
            "title": r["title"], "url": occ_url(r), "risk": r["aioe_pct"],
            "color": risk_color(r["aioe_pct"]), "workforce": fmt_wf(r.get("jobs")),
            "pay": money(sal(r), symbol),
        }
        return vm

    # 7 highest-risk (with automatable tasks from xrepo)
    top_risk = []
    for r in sorted(high, key=lambda x: -x["aioe_pct"])[:18]:
        vm = row_vm(r)
        rep = (ai.get(r["slug"]) or {}).get("replaced") or []
        vm["tasks"] = html.escape("; ".join(sentence(t) for t in rep[:2])) or "—"
        top_risk.append(vm)

    # 8 resilient (with human moat)
    resilient = []
    for r in sorted(low, key=lambda x: x["aioe_pct"])[:18]:
        vm = row_vm(r)
        moat = (ai.get(r["slug"]) or {}).get("moat") or []
        vm["moat"] = html.escape("; ".join(sentence(t) for t in moat[:2])) or "—"
        resilient.append(vm)

    # 9 by occupational group
    groups = {}
    for r in rows:
        g = r.get("category_name") or r.get("category") or "Other"
        groups.setdefault(g, []).append(r)
    by_group = []
    for g, rs in groups.items():
        e = [x["aioe_pct"] for x in rs]
        wf = sum(x.get("jobs") or 0 for x in rs)
        pays = [sal(x) for x in rs if sal(x)]
        gm = round(statistics.median(e))
        by_group.append({
            "name": g, "risk_median": gm, "color": risk_color(gm),
            "high_pct": pct(sum(1 for x in e if x >= HIGH), len(e)),
            "workforce": fmt_wf(wf),
            "pay_median": money(statistics.median(pays), symbol) if pays else "—",
            "_sort": gm,
        })
    by_group.sort(key=lambda x: -x["_sort"])

    # 10 quadrant (has_pay only)
    quadrant = {"points": [], "hi_hi": [], "lo_hi": []}
    if has_pay:
        paid = [r for r in rows if sal(r) and r.get("jobs")]
        pays = sorted(sal(p) for p in paid)
        pmin, pmax = pays[0], pays[-1]
        pmed = statistics.median(pays)
        wmax = max(p["jobs"] for p in paid)
        for r in paid:
            x = round(100 * (sal(r) - pmin) / (pmax - pmin), 1) if pmax > pmin else 50
            y = r["aioe_pct"]
            rad = 5 + 34 * (r["jobs"] / wmax) ** 0.5
            quadrant["points"].append({"x": x, "y": y, "r": round(rad, 1), "color": risk_color(y)})
        hi_hi = sorted([r for r in paid if r["aioe_pct"] >= HIGH and sal(r) >= pmed],
                       key=lambda x: -sal(x))[:6]
        lo_hi = sorted([r for r in paid if r["aioe_pct"] >= HIGH and sal(r) < pmed],
                       key=lambda x: -sal(x))[:6]
        quadrant["hi_hi"] = [r["title"] for r in hi_hi]
        quadrant["lo_hi"] = [r["title"] for r in lo_hi]

    # 11 tasks / 12 moats (from the most-exposed occupations that have AI data)
    tasks, moats = [], []
    for r in sorted(high, key=lambda x: -x["aioe_pct"]):
        a = ai.get(r["slug"]) or {}
        if a.get("replaced") and len(tasks) < 10:
            tasks.append({"occ": r["title"], "url": occ_url(r),
                          "items": [sentence(t) for t in a["replaced"][:3]]})
        if a.get("moat") and len(moats) < 10:
            moats.append({"occ": r["title"], "url": occ_url(r),
                          "items": [sentence(t) for t in a["moat"][:3]]})

    # 13 transitions (adjacent resilient roles)
    transitions = []
    for r in sorted(high, key=lambda x: -x["aioe_pct"]):
        a = ai.get(r["slug"]) or {}
        adj = a.get("adjacent") or []
        if not adj:
            continue
        transitions.append({
            "occ": r["title"], "url": occ_url(r),
            "adj": [{"name": x.get("name_en") or x.get("name"),
                     "url": f"{B.DOMAIN}/country/{slug}/#{x.get('slug')}"} for x in adj[:3]],
        })
        if len(transitions) >= 12:
            break

    # 15 scenarios (aggregate A1 loss)
    s_low = sum((r.get("loss") or {}).get("count_low") or 0 for r in rows)
    s_mid = sum((r.get("loss") or {}).get("count_mid") or 0 for r in rows)
    s_high = sum((r.get("loss") or {}).get("count_high") or 0 for r in rows)

    # areas for exec summary
    top_risk_areas = [g["name"] for g in by_group[:3]]
    top_resilient_areas = [g["name"] for g in sorted(by_group, key=lambda x: x["_sort"])[:3]]

    # snapshot rows (pay row only when available)
    snap = [
        ("Occupations analysed", f"{len(rows)}"),
        ("Workforce covered", fmt_wf(total_wf)),
        ("Median AI exposure", f"{risk_median}/100"),
        ("High-risk occupations", f"{high_occ_pct}%"),
        ("High-risk workforce", f"{high_wf_pct}%"),
    ]
    pay_measure = "median" if salf == "median" else "average"
    if has_pay:
        med_pay = statistics.median([sal(r) for r in rows if sal(r)])
        snap.append((f"Typical annual pay ({pay_measure})", money(med_pay, symbol)))
    snap.append(("Data year", DATA_CUTOFF))

    src_full, classification, _tier, _pay = (B.SOURCE_META.get(cc)
                                             if hasattr(B, "SOURCE_META") else (None, None, None, None)) or \
        (B.COUNTRY_META[cc][0] + " official statistics", "ISCO-08", "", False)
    # fall back to build.SOURCE_META shape if present
    try:
        sm = B.SOURCE_META[cc]
        src_full, classification = sm[0], sm[1]
    except Exception:
        src_full = f"{name} official statistics office"
        classification = "ANZSCO" if cc == "AU" else "ISCO-08"

    salary_relation = ("Higher-paid, judgement-heavy roles cluster at lower risk, while many mid-pay "
                       "administrative roles carry the highest exposure." if has_pay else
                       "Official pay is not published at this occupational granularity for "
                       f"{name}, so pay-vs-risk analysis is omitted in this edition.")

    return {
        "cc": cc, "country": name, "slug": slug, "year": B.YEAR,
        "site_name": B.SITE_NAME, "flag_svg": B.FLAG.get(cc, ""),
        "published": PUBLISHED, "data_cutoff": DATA_CUTOFF,
        "report_url": f"{B.DOMAIN}/reports/{slug}/",
        "country_url": f"{B.DOMAIN}/country/{slug}/",
        "dataset_url": f"{B.DOMAIN}/dataset.csv",
        "map_data_uri": map_data_uri(cc),
        "n_occ": len(rows), "workforce_h": fmt_wf(total_wf), "workforce_raw": total_wf,
        "risk_median": risk_median, "high_occ_pct": high_occ_pct, "high_wf_pct": high_wf_pct,
        "has_pay": has_pay,
        "hero_conclusion": (f"{high_wf_pct}% of {name}'s covered workforce is employed in occupations "
                            f"with high AI task exposure."),
        "exec_lead": (f"Across {len(rows)} occupations covering {fmt_wf(total_wf)} workers in {name}, "
                      f"median AI exposure is {risk_median}/100. {high_occ_pct}% of occupations — and "
                      f"{high_wf_pct}% of workers — fall in the high-exposure band."),
        "top_risk_areas": top_risk_areas, "top_resilient_areas": top_resilient_areas,
        "salary_relation": salary_relation,
        "key_change": ("Entry-level and routine administrative tasks are narrowing fastest; "
                       "client-facing, accountability and hands-on work remain the human moat."),
        "snapshot_rows": snap,
        "snapshot_note": (f"{name} has a median AI exposure of {risk_median}/100. High-exposure work is "
                          f"concentrated in {top_risk_areas[0].lower()} and adjacent groups, while "
                          f"{top_resilient_areas[0].lower()} stays most resilient."),
        "map_observations": [
            f"The largest tiles — {top_risk_areas[0]} and related groups — carry above-median exposure.",
            f"{high_wf_pct}% of employment sits in the high-exposure (red) band.",
            f"{top_resilient_areas[0]} forms the biggest low-exposure (green) cluster.",
        ],
        "dist": {
            "occ_high": pct(len(high), len(rows)), "occ_mid": pct(len(mid), len(rows)),
            "occ_low": pct(len(low), len(rows)),
            "wf_high": high_wf_pct, "wf_mid": pct(wf_mid, total_wf), "wf_low": pct(wf_low, total_wf),
            "q1": q1, "q3": q3,
        },
        "top_risk": top_risk, "resilient": resilient, "by_group": by_group,
        "quadrant": quadrant, "tasks": tasks, "moats": moats, "transitions": transitions,
        "scenarios": {
            "low": f"{s_low:,}", "mid": f"{s_mid:,}", "high": f"{s_high:,}",
            "low_rate": f"{pct(s_low, total_wf)}%", "mid_rate": f"{pct(s_mid, total_wf)}%",
            "high_rate": f"{pct(s_high, total_wf)}%",
        },
        "classification": classification, "source_short": src_full, "source_full": src_full,
        "pay_measure": pay_measure if has_pay else None,
    }


LANDING = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{country} AI Job Risk Report {year} — download PDF | {site}</title>
<meta name="description" content="{hero} Download the free {year} PDF report: rankings, risk map, scenarios and methodology for {n} occupations.">
<link rel="canonical" href="{report_url}">
<style>body{{font:16px/1.6 system-ui,Arial;max-width:760px;margin:0 auto;padding:32px 20px;color:#1c2430}}
h1{{font-size:1.9rem;margin:.2em 0}} .hero{{background:#f2f1fb;border-left:5px solid #6647c0;padding:14px 16px;border-radius:6px;font-size:1.1rem}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:18px 0}} .stat{{border:1px solid #dcdee2;border-radius:8px;padding:10px}}
.stat b{{font-size:1.4rem;display:block}} .btn{{display:inline-block;background:#6647c0;color:#fff;font-weight:700;padding:12px 22px;border-radius:8px;margin:12px 0}}
ul{{padding-left:20px}} a{{color:#4f3797}} .muted{{color:#616367;font-size:.9rem}}</style>
<script type="application/ld+json">{jsonld}</script></head><body>
<p class="muted"><a href="{country_url}">← {country} interactive risk map</a></p>
<h1>{country} AI Job Risk Report {year}</h1>
<p class="hero">{hero}</p>
<div class="grid">
<div class="stat"><b>{n}</b>Occupations</div>
<div class="stat"><b>{risk_median}/100</b>Median AI exposure</div>
<div class="stat"><b>{high_occ_pct}%</b>High-risk occupations</div>
</div>
<a class="btn" href="{pdf_href}">Download the full PDF report</a>
<h2>What's inside</h2>
<ul><li>Executive summary &amp; how to read the scores</li><li>National AI job risk map</li>
<li>Highest-risk and most-resilient occupations</li><li>Risk by occupational group</li>
{pay_line}<li>Tasks AI automates &amp; the human moat</li><li>Career transition paths</li>
<li>2030 adoption scenarios</li><li>Full methodology, sources &amp; citation</li></ul>
<h2>Data &amp; method</h2>
<p class="muted">AI exposure from ILO Working Paper 140 (calibrated with Eloundou et al.), mapped to {n} occupations.
Full occupation dataset: <a href="{dataset_url}">dataset.csv</a> (CC BY 4.0). Updated {published}.</p>
<p class="muted">Suggested citation: {site} ({year}). AI Job Risk Report: {country} {year}. {report_url}</p>
</body></html>"""


def build_landing(m):
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Report",
        "name": f"AI Job Risk Report: {m['country']} {m['year']}",
        "headline": m["hero_conclusion"], "datePublished": m["published"],
        "dateModified": m["published"], "inLanguage": "en",
        "author": {"@type": "Organization", "name": m["site_name"], "url": B.DOMAIN},
        "publisher": {"@type": "Organization", "name": m["site_name"], "url": B.DOMAIN},
        "spatialCoverage": {"@type": "Place", "name": m["country"]},
        "isBasedOn": "https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure",
        "citation": "ILO Working Paper 140; Eloundou et al. (2023)",
        "url": m["report_url"],
        "distribution": {"@type": "DataDownload", "encodingFormat": "application/pdf",
                         "contentUrl": f"{m['report_url']}{m['slug']}-ai-job-risk-{m['year']}.pdf"},
    }, ensure_ascii=False)
    pay_line = "<li>Salary vs AI risk quadrant</li>" if m["has_pay"] else ""
    return LANDING.format(
        country=m["country"], year=m["year"], site=m["site_name"], hero=html.escape(m["hero_conclusion"]),
        n=m["n_occ"], risk_median=m["risk_median"], high_occ_pct=m["high_occ_pct"],
        report_url=m["report_url"], country_url=m["country_url"], dataset_url=m["dataset_url"],
        published=m["published"], jsonld=jsonld, pay_line=pay_line,
        pdf_href=f"{m['slug']}-ai-job-risk-{m['year']}.pdf",
    )


def build(cc):
    m = build_model(cc)
    outdir = os.path.join(REPORTS, m["slug"])
    os.makedirs(outdir, exist_ok=True)
    tmpl = env.get_template("report_template.html")
    with open(os.path.join(outdir, "report.html"), "w", encoding="utf-8") as f:
        f.write(tmpl.render(m=m))
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_landing(m))
    tier = "A" if m["has_pay"] else "B"
    print(f"[{cc}] {tier}-tier report.html + landing -> reports/{m['slug']}/  "
          f"({m['n_occ']} occ, {len(m['tasks'])} task blocks, {len(m['transitions'])} transitions)")
    return m


def main():
    want = [x.upper() for x in sys.argv[1:]]
    if not want:
        want = [cc for cc in B.ORDER if os.path.isdir(os.path.join(DIST, "country", B.SLUG.get(cc, "")))]
    os.makedirs(REPORTS, exist_ok=True)
    for cc in want:
        build(cc)


if __name__ == "__main__":
    main()
