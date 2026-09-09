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
            "jobs": r.get("jobs") or 0,          # raw count, for workforce-ordered views
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

    # build.py's SOURCE_INFO is the single source of truth for who publishes a
    # country's employment counts and which classification it uses. Its strings
    # are pre-escaped for build.py's own HTML, so unescape them back to plain
    # text here and let each renderer (Jinja2 for the PDF, html.escape for the
    # landing) escape once.
    auth, classification, _tier, _pay = B.SOURCE_INFO[cc]
    src_full = html.unescape(auth)
    classification = html.unescape(classification)

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
        "n_occ": len(rows), "n_high": len(high),
        "workforce_h": fmt_wf(total_wf), "workforce_raw": total_wf,
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


# The report landing is the destination of the site-wide "Download the full
# report" CTA, so it wears the same dark chrome + footer as every other page
# (it used to be a stray white/purple sheet with no nav back into the site).
# The report landing is the destination of the site-wide "Download the full
# report" CTA, so it wears the same dark chrome + footer as every other page.
#
# It also has to carry real, country-specific substance. The first version was
# ~220 words of which 73% was boilerplate shared by all 46 landings, and Google
# responded exactly as you would expect: one page crawled-not-indexed, the rest
# discovered-not-indexed. build_model() already computes far more per-country
# material than the page used, so the sections below surface the dimensions the
# country page does NOT cover — the risk-band distribution, the quartiles, the
# pay-vs-risk split, the automatable tasks and the transition paths — while the
# depth (full rankings, group tables, scenarios, methodology) stays in the PDF.
LANDING = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{country} AI Job Risk Report {year} — download PDF | {site}</title>
<meta name="description" content="{hero} Download the free {year} PDF report: rankings, risk map, scenarios and methodology for {n} occupations.">
<link rel="canonical" href="{report_url}">
<meta name="robots" content="index,follow">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="article"><meta property="og:site_name" content="{site}">
<meta property="og:title" content="{country} AI Job Risk Report {year}">
<meta property="og:description" content="{hero}">
<meta property="og:url" content="{report_url}"><meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{og_image}">
{doc_css}
<style>
.crumb{{font-size:13px;color:#9a9aa6;margin:0 0 22px}}
.crumb a{{text-decoration:none;font-weight:600}}
.crumb a:hover{{text-decoration:underline}}
.hero{{background:#12121a;border-left:4px solid #e6961e;border-radius:0 9px 9px 0;padding:14px 17px;font-size:17px;line-height:1.55;margin:14px 0 20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:18px 0 22px}}
.stat{{border:1px solid rgba(255,255,255,.09);border-radius:10px;background:#12121a;padding:13px 15px;font-size:12.5px;color:#9a9aa6}}
.stat b{{display:block;font-size:1.5rem;color:#e0e0e8;line-height:1.2;margin-bottom:3px}}
.btn.big{{padding:13px 24px;font-size:15px}}
.dl-row{{display:flex;flex-wrap:wrap;align-items:center;gap:14px;margin:6px 0 4px}}
.dl-row .btn{{margin-top:0}}
.dl-note{{font-size:12.5px;color:#9a9aa6;margin:0 0 8px}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;margin:14px 0}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid rgba(255,255,255,.08);vertical-align:top}}
th{{color:#9a9aa6;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}}
td.num,th.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.tblwrap{{overflow-x:auto}}
.pill{{display:inline-block;padding:2px 8px;border-radius:999px;font-weight:700;font-size:12px;color:#0a0a0f}}
.bands{{display:flex;height:30px;border-radius:7px;overflow:hidden;margin:14px 0 8px;font-size:11.5px;font-weight:700;color:#0a0a0f}}
.bands span{{display:flex;align-items:center;justify-content:center;min-width:0}}
.bandkey{{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:12.5px;color:#9a9aa6;margin-bottom:6px}}
.bandkey i{{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:middle}}
.mapfig{{margin:16px 0;border:1px solid rgba(255,255,255,.09);border-radius:11px;overflow:hidden;background:#000}}
.mapfig img{{width:100%;height:auto;display:block}}
.mapfig figcaption{{padding:9px 13px;font-size:12.5px;color:#9a9aa6}}
.obs{{margin:10px 0 0;padding-left:20px}}
.obs li{{margin:5px 0;color:#9a9aa6}}
.trans{{list-style:none;padding:0;margin:12px 0}}
.trans li{{padding:9px 0;border-bottom:1px solid rgba(255,255,255,.08);font-size:13.5px}}
.trans .from{{font-weight:600}}
.trans .to{{color:#9a9aa6}}
.more{{font-size:13px;color:#9a9aa6;margin:10px 0 0}}
</style>
<script type="application/ld+json">{jsonld}</script></head><body><div class="wrap">
<p class="crumb"><a href="/">AI Job Risk Map</a> &rsaquo; <a href="/reports/">Country reports</a> &rsaquo; {country}</p>
<h1>{country} AI Job Risk Report {year}</h1>
<p class="hero">{hero}</p>
<div class="grid">
<div class="stat"><b>{n}</b>Occupations</div>
<div class="stat"><b>{risk_median}/100</b>Median AI exposure</div>
<div class="stat"><b>{high_occ_pct}%</b>High-risk occupations</div>
</div>
<div class="dl-row"><a class="btn big" href="{pdf_href}" download>Download the full PDF report</a>
<a href="{country_url}">or explore the interactive {country} map &rarr;</a></div>
<p class="dl-note">Free PDF &middot; no sign-up &middot; CC&nbsp;BY&nbsp;4.0 &mdash; reuse it with a link back.</p>

<h2>How AI exposure is distributed in {country}</h2>
<p>{exec_lead}</p>
{bands_html}
<p>{quartile_line}</p>
{snapshot_html}

<h2>Where the risk concentrates</h2>
<p>{snapshot_note}</p>
<p>{salary_relation}</p>
{quadrant_html}

<h2>Where AI exposure hits the most {country} workers</h2>
<p>The high-exposure occupations that employ the most people in {country}, with the tasks generative
AI can already take on. {n_high} occupations in total fall in the high-exposure band; these {n_shown}
are the ones with the largest workforces behind them.</p>
{risk_table}

{transitions_html}

{map_html}

<h2>What&rsquo;s inside the full report</h2>
<ul><li>Executive summary &amp; how to read the scores</li><li>National AI job risk map</li>
<li>Highest-risk and most-resilient occupations, ranked in full</li><li>Risk by occupational group</li>
{pay_line}<li>Tasks AI automates &amp; the human moat</li><li>Career transition paths</li>
<li>2030 adoption scenarios</li><li>Full methodology, sources &amp; citation</li></ul>

<h2>Data &amp; method</h2>
<p>{country} occupations are classified in <strong>{classification}</strong>, with employment counts
from {source_short}. AI exposure comes from ILO Working Paper 140 (calibrated with Eloundou et al.)
and is ranked on a single global percentile scale, so a score here means the same thing as the
same score anywhere else on this site &mdash; see the <a href="/methodology.html">full methodology</a>.
The complete occupation dataset is available as <a href="{dataset_url}">dataset.csv</a>
(CC&nbsp;BY&nbsp;4.0). Data year {data_year}; page updated {published}.</p>
<div class="quote">Suggested citation: {site} ({year}). <em>AI Job Risk Report: {country} {year}</em>. {report_url}</div>
<p class="foot">Looking for another country? <a href="/reports/">Browse all {nc} country reports &rarr;</a></p>
</div>
{footer}</body></html>"""


def _bands(m):
    """Risk-band split (share of occupations vs share of workers). The country
    page only shows a single weighted average, so this split is the landing's
    own material rather than a second copy of it."""
    d = m["dist"]
    key = (f'<div class="bandkey">'
           f'<span><i style="background:{RISK_HI}"></i>High exposure (&ge;{HIGH}/100)</span>'
           f'<span><i style="background:{RISK_MID}"></i>Moderate ({MID}&ndash;{HIGH - 1})</span>'
           f'<span><i style="background:{RISK_LO}"></i>Lower (&lt;{MID})</span></div>')

    def bar(label, hi, mid, lo):
        segs = "".join(
            (f'<span style="background:{c};flex:{max(v, 0.01)}">{v}%</span>' if v >= 7
             else f'<span style="background:{c};flex:{max(v, 0.01)}"></span>')
            for c, v in ((RISK_HI, hi), (RISK_MID, mid), (RISK_LO, lo)))
        return f'<p class="more"><strong>{label}</strong></p><div class="bands">{segs}</div>'

    return (key
            + bar("Share of occupations", d["occ_high"], d["occ_mid"], d["occ_low"])
            + bar("Share of workers", d["wf_high"], d["wf_mid"], d["wf_low"]))


def _snapshot(m):
    rows = "".join(f"<tr><td>{html.escape(k)}</td><td class='num'>{html.escape(str(v))}</td></tr>"
                   for k, v in m["snapshot_rows"])
    return f'<div class="tblwrap"><table><tbody>{rows}</tbody></table></div>'


def _risk_table(m, n):
    """High-exposure occupations ordered by WORKERS AFFECTED, with the tasks AI
    can already take on.

    Two reasons not to order by score here. Editorially, "which exposed jobs
    employ the most people" is the question a reader of a national report
    actually has. Practically, the ~40 countries that share the 427-occupation
    ISCO-08 set have an identical top-N-by-score, so a score-ordered table made
    their landings near-duplicates of each other; employment structure differs
    per country, so this ordering does not."""
    rows = ""
    for r in sorted(m["top_risk"], key=lambda x: -x["jobs"])[:n]:
        rows += (f'<tr><td><a href="{r["url"]}">{html.escape(r["title"])}</a></td>'
                 f'<td class="num"><span class="pill" style="background:{r["color"]};color:#fff">'
                 f'{r["risk"]}</span></td>'
                 f'<td class="num">{html.escape(r["workforce"])}</td>'
                 f'<td>{r["tasks"]}</td></tr>')
    return ('<div class="tblwrap"><table><thead><tr><th>Occupation</th>'
            '<th class="num">Exposure</th><th class="num">Workers affected</th>'
            '<th>Tasks AI can already do</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def _quadrant(m):
    """High-exposure work split by pay. Not shown anywhere else on the site."""
    q = m["quadrant"]
    if not q["hi_hi"] and not q["lo_hi"]:
        return ""
    out = []
    if q["hi_hi"]:
        out.append('<li><span class="from">Higher-paid and highly exposed:</span> '
                   f'<span class="to">{html.escape(", ".join(q["hi_hi"][:5]))}</span></li>')
    if q["lo_hi"]:
        out.append('<li><span class="from">Lower-paid and highly exposed:</span> '
                   f'<span class="to">{html.escape(", ".join(q["lo_hi"][:5]))}</span></li>')
    return ('<p class="more">Exposure does not track pay in one direction &mdash; the report plots '
            'every occupation on a pay &times; risk quadrant:</p>'
            f'<ul class="trans">{"".join(out)}</ul>')


def _transitions(m, n):
    """Adjacent, more-resilient roles per exposed occupation (from xrepo_ai).
    Country pages carry none of this."""
    if not m["transitions"]:
        return ""
    items = ""
    for t in m["transitions"][:n]:
        adj = ", ".join(f'<a href="{a["url"]}">{html.escape(a["name"] or "")}</a>'
                        for a in t["adj"] if a.get("name"))
        if not adj:
            continue
        items += (f'<li><span class="from"><a href="{t["url"]}">{html.escape(t["occ"])}</a></span> '
                  f'<span class="to">&rarr; {adj}</span></li>')
    if not items:
        return ""
    return (f'<h2>Where {html.escape(m["country"])}&rsquo;s exposed workers can move</h2>'
            '<p>Every high-exposure occupation in the report is paired with adjacent roles that '
            'share its skills but carry lower AI exposure. A few examples:</p>'
            f'<ul class="trans">{items}</ul>'
            f'<p class="more">The full report lists {len(m["transitions"])} such transition paths.</p>')


def _map(m):
    png = os.path.join(DIST, "static", "maps", B.map_filename(m["cc"]))
    if not os.path.exists(png):
        return ""
    obs = "".join(f"<li>{html.escape(o)}</li>" for o in m["map_observations"])
    alt = (f"AI job risk map {m['country']} {m['year']} - {m['n_occ']} occupations "
           f"by AI exposure risk")
    return (f'<h2>The {html.escape(m["country"])} risk map</h2>'
            '<figure class="mapfig">'
            f'<img src="/static/maps/{B.map_filename(m["cc"])}" alt="{html.escape(alt)}" '
            'width="800" height="600" loading="lazy">'
            '<figcaption>Tile area = employment, colour = AI exposure. Full-resolution version '
            'inside the report; free to reuse with attribution.</figcaption>'
            f'</figure><ul class="obs">{obs}</ul>')


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
    png = os.path.join(DIST, "static", "maps", B.map_filename(m["cc"]))
    og_image = (f"{B.DOMAIN}/static/maps/{B.map_filename(m['cc'])}" if os.path.exists(png)
                else f"{B.DOMAIN}/og-image.png")
    d = m["dist"]
    n_shown = min(6, len(m["top_risk"]))
    quartile_line = (
        f"Half of {html.escape(m['country'])}&rsquo;s occupations score between "
        f"<strong>{d['q1']}</strong> and <strong>{d['q3']}</strong> out of 100, around a median of "
        f"<strong>{m['risk_median']}</strong>. The wider that band, the more unevenly generative AI "
        "lands across the national workforce.")
    return LANDING.format(
        country=html.escape(m["country"]), year=m["year"], site=m["site_name"],
        hero=html.escape(m["hero_conclusion"]),
        n=m["n_occ"], risk_median=m["risk_median"], high_occ_pct=m["high_occ_pct"],
        report_url=m["report_url"], country_url=m["country_url"], dataset_url=m["dataset_url"],
        published=m["published"], jsonld=jsonld, pay_line=pay_line,
        pdf_href=f"{m['slug']}-ai-job-risk-{m['year']}.pdf",
        doc_css=B.DOC_CSS, footer=B.build_footer(), og_image=og_image,
        exec_lead=html.escape(m["exec_lead"]),
        bands_html=_bands(m), quartile_line=quartile_line, snapshot_html=_snapshot(m),
        snapshot_note=html.escape(m["snapshot_note"]),
        salary_relation=html.escape(m["salary_relation"]),
        quadrant_html=_quadrant(m), risk_table=_risk_table(m, n_shown),
        n_high=m["n_high"], n_shown=n_shown,
        transitions_html=_transitions(m, 4), map_html=_map(m),
        classification=html.escape(m["classification"]),
        source_short=html.escape(m["source_short"]),
        data_year=m["data_cutoff"], nc=len(B.SLUG),
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
