"""Build per-country AI-exposure treemap sites from occupations_v2.json.

Reuses the exact same self-contained template (job-treemap/template.html) for
every country. Emits, under job-treemap/dist/:
  - {cc}/index.html + {cc}/data.json   -> standalone, independently deployable site per country
  - data/{cc}.json                     -> data for the overview switcher
  - index.html                         -> single overview page with a country dropdown

Run:  E:\\run\\Python3.13\\python.exe job-treemap/build.py
"""
import html
import json
import math
import os
import sys
from datetime import datetime

# 构建版本号：追加到数据 JSON 的 fetch URL（?v=VER）以防浏览器缓存陈旧 JSON。
# 每次重建都变→旧缓存自动失效；同一次构建内不变→仍可命中缓存。
VER = datetime.now().strftime("%Y%m%d%H%M%S")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)  # 使 `from db.connection import ...` 可用（读 outlook）
SRC = os.path.join(REPO, "site", "src", "data", "occupations_v2.json")
CATS = os.path.join(REPO, "site", "src", "data", "categories_v2.json")
TEMPLATE = os.path.join(HERE, "template.html")
DIST = os.path.join(HERE, "dist")

# name / currency symbol / official source line per country.
# Countries not listed (e.g. CH placeholder) are skipped.
COUNTRY_META = {
    "AU": ("Australia", "AUD", "$",
           "<strong>Data sources:</strong><br><a href='https://www.jobsandskills.gov.au'>Jobs and Skills Australia</a> &amp; ABS &mdash; ANZSCO occupations"),
    "US": ("United States", "USD", "$",
           "<strong>Data sources:</strong><br>US BLS OES &amp; O*NET &mdash; SOC occupations"),
    "CA": ("Canada", "CAD", "$",
           "<strong>Data sources:</strong><br>Statistics Canada &amp; Job Bank (ESDC) &mdash; NOC occupations"),
    "UK": ("United Kingdom", "GBP", "£",
           "<strong>Data sources:</strong><br>UK ONS &mdash; SOC occupations"),
    "NZ": ("New Zealand", "NZD", "$",
           "<strong>Data sources:</strong><br>Stats NZ &amp; MBIE &mdash; ANZSCO occupations"),
    "DE": ("Germany", "EUR", "€",
           "<strong>Data sources:</strong><br>Destatis &amp; Bundesagentur für Arbeit &mdash; ISCO occupations"),
    "ES": ("Spain", "EUR", "€",
           "<strong>Data sources:</strong><br>INE &amp; SEPE &mdash; CNO occupations"),
    "FR": ("France", "EUR", "€",
           "<strong>Data sources:</strong><br>INSEE &amp; France Travail &mdash; ROME occupations"),
    "IE": ("Ireland", "EUR", "€",
           "<strong>Data sources:</strong><br>CSO Ireland &mdash; ISCO occupations"),
    "IT": ("Italy", "EUR", "€",
           "<strong>Data sources:</strong><br>ISTAT &mdash; ISCO occupations"),
    "NL": ("Netherlands", "EUR", "€",
           "<strong>Data sources:</strong><br>CBS Netherlands &mdash; ISCO occupations"),
    "JP": ("Japan", "JPY", "¥",
           "<strong>Data sources:</strong><br>総務省統計局 &amp; 厚生労働省 賃金センサス &mdash; JSCO occupations"),
    "KR": ("South Korea", "KRW", "₩",
           "<strong>Data sources:</strong><br>한국고용정보원 (KEIS) WorkNet/KNOW &amp; 통계청 &mdash; KECO occupations"),
}
# Order shown in the country switcher / landing hub.
ORDER = ["AU", "US", "UK", "CA", "NZ", "JP", "KR", "DE", "FR", "ES", "IT", "NL", "IE"]

# Public site identity + per-country URL slug (lowercase full name).
DOMAIN = "https://aijobriskmap.com"
SITE_NAME = "AI Job Risk Map"
SLUG = {
    "AU": "australia", "US": "united-states", "UK": "united-kingdom",
    "CA": "canada", "NZ": "new-zealand", "JP": "japan", "KR": "south-korea",
    "DE": "germany", "FR": "france", "ES": "spain", "IT": "italy",
    "NL": "netherlands", "IE": "ireland",
}

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
           '<rect width="32" height="32" rx="6" fill="#0a0a0f"/>'
           '<rect x="4" y="4" width="13" height="24" rx="1.5" fill="#e6961e"/>'
           '<rect x="19" y="4" width="9" height="11" rx="1.5" fill="#32a032"/>'
           '<rect x="19" y="17" width="9" height="11" rx="1.5" fill="#ff5014"/>'
           '</svg>')


ABOUT_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>About &amp; Methodology &mdash; AI Job Risk Map</title>
<meta name="description" content="How the AI exposure score is measured: two open generative-AI-era datasets (ILO Working Paper 140 and OpenAI's GPTs-are-GPTs) mapped onto each country's official occupation classification.">
<link rel="canonical" href="__DOMAIN__/about.html">
<meta name="robots" content="index,follow">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="article">
<meta property="og:site_name" content="AI Job Risk Map">
<meta property="og:title" content="About &amp; Methodology — AI Job Risk Map">
<meta property="og:url" content="__DOMAIN__/about.html">
<meta property="og:image" content="__DOMAIN__/og-image.png">
<style>
:root{--bg:#0a0a0f;--bg2:#12121a;--fg:#e0e0e8;--fg2:#9a9aa6;--accent:#e6961e;--line:rgba(255,255,255,.09)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:820px;margin:0 auto;padding:40px 22px 80px}
a{color:var(--accent)}
.back{display:inline-block;margin-bottom:28px;font-size:14px;font-weight:600;text-decoration:none}
.back:hover{text-decoration:underline}
h1{font-size:30px;line-height:1.25;margin:0 0 10px}
.lead{color:var(--fg2);font-size:17px;margin:0 0 34px}
h2{font-size:20px;margin:38px 0 12px;padding-top:22px;border-top:1px solid var(--line)}
h3{font-size:16px;margin:22px 0 6px}
p{margin:10px 0}
ol,ul{padding-left:22px}
li{margin:7px 0}
code{background:var(--bg2);padding:1px 6px;border-radius:4px;font-size:13px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
table{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px;display:block;overflow-x:auto}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--fg2);font-weight:600;white-space:nowrap}
.tag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:99px}
.tag-a{background:rgba(50,160,50,.15);color:#63c563}
.tag-b{background:rgba(230,150,30,.15);color:var(--accent)}
.tag-c{background:rgba(150,150,160,.15);color:#a9a9b6}
.src{background:var(--bg2);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:12px 0}
.src .meta{color:var(--fg2);font-size:13px;margin-top:6px}
.foot{color:var(--fg2);font-size:13px;margin-top:40px;padding-top:18px;border-top:1px solid var(--line)}
</style>
</head>
<body>
<div class="wrap">
<a class="back" href="javascript:history.length>1?history.back():location.href='index.html'">&larr; Back to the map</a>

<h1>How the AI exposure is measured</h1>
<p class="lead">The colour of every tile on this map &mdash; the AI exposure score, 0&ndash;10 &mdash; is not our opinion.
It is computed from two open, authoritative, generative-AI-era research datasets, mapped onto each country&rsquo;s
official occupation classification.</p>

<h2>Data sources</h2>
<p>The exposure index draws on two peer-reviewed / institutional studies, both openly licensed for reuse:</p>

<div class="src">
<strong>1. ILO Working Paper 140 &mdash; <em>Generative AI and Jobs: A Refined Global Index of Occupational Exposure</em> (2025)</strong>
<p>Published by the International Labour Organization (a UN agency). Its Annex Table A1 gives a generative-AI
exposure mean (0&ndash;1) for the 112 <strong>ISCO-08</strong> occupations with meaningful exposure. We use these
as the authoritative anchor for the high-exposure band.</p>
<div class="meta">Gmyrek, P. et&nbsp;al. (2025). ILO. Licensed <a href="https://creativecommons.org/licenses/by/4.0/">CC&nbsp;BY&nbsp;4.0</a>.
&middot; <a href="https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure">Publication</a></div>
</div>

<div class="src">
<strong>2. Eloundou et&nbsp;al. &mdash; <em>&ldquo;GPTs are GPTs: An Early Look at the Labor Market Impact Potential of LLMs&rdquo;</em> (2023)</strong>
<p>From OpenAI. Provides a task-based LLM-exposure score (&ldquo;beta&rdquo;, 0&ndash;1) for ~800 <strong>O*NET-SOC</strong>
occupations, continuous across the whole range. We use it to resolve the low-to-mid exposure band continuously.</p>
<div class="meta">Eloundou, T., Manning, S., Mishkin, P., Rock, D. (2023). MIT-licensed.
&middot; <a href="https://github.com/openai/GPTs-are-GPTs">Dataset</a></div>
</div>

<p>The two 0&ndash;1 scales agree closely where they overlap (Data Entry Clerks: ILO&nbsp;0.70 / Eloundou&nbsp;0.696;
Accountants&nbsp;0.51 / 0.54), so their raw scores can be combined on the same scale without rescaling.</p>

<h2>How each occupation gets a score</h2>
<ol>
<li><strong>Raw 0&ndash;1 exposure</strong> &mdash; ILO takes precedence, Eloundou fills the rest:
  <ul>
  <li><strong>United States</strong>: Eloundou beta by SOC-6 code (group mean where a code is missing).</li>
  <li><strong>Other countries</strong>: national code &rarr; <strong>ISCO-08</strong> unit group, then the <strong>ILO</strong>
  mean if that ISCO group is one of the 112, otherwise the <strong>Eloundou</strong> beta via the ESCO/O*NET
  ISCO&rarr;SOC bridge.</li>
  </ul></li>
<li><strong>Global percentile</strong> &mdash; the raw score is ranked against a single fixed global reference
distribution and expressed as a <strong>0&ndash;100 percentile</strong>. One global anchor for every country, so the
numbers stay comparable across borders.</li>
<li><strong>Map colour</strong> &mdash; <code>exposure = round(percentile / 10)</code>, a 0&ndash;10 scale (green&nbsp;=&nbsp;low,
red&nbsp;=&nbsp;high).</li>
</ol>

<h2>Country coverage</h2>
<p>Each country&rsquo;s occupations are mapped to ISCO-08 (or, for the US, to SOC):</p>
<table>
<thead><tr><th>Method</th><th>Countries</th><th>How</th></tr></thead>
<tbody>
<tr><td><span class="tag tag-a">Direct</span></td><td>US &middot; IE &middot; IT &middot; NL</td>
<td>Occupation code is already SOC (US) or ISCO-08 (IE/IT/NL) &mdash; joined directly.</td></tr>
<tr><td><span class="tag tag-b">Crosswalk</span></td><td>AU &middot; NZ &middot; DE &middot; UK &middot; CA &middot; ES</td>
<td>Official classification correspondence (ANZSCO, KldB, SOC, NOC, and Spain&rsquo;s INE CNO-11&harr;ISCO-08) &rarr; ISCO-08.</td></tr>
<tr><td><span class="tag tag-c">AI-mapped</span></td><td>FR &middot; JP &middot; KR</td>
<td>No clean official ROME / JSCO / KECO &rarr; ISCO table was obtainable, so each occupation is placed
onto the official ISCO-08 structure by an LLM (the same approach the ILO study used), then scored as
above. Tagged separately (<code>_llmmap</code>); will be upgraded when the official table is wired in.</td></tr>
</tbody>
</table>

<h2>About the underlying job data</h2>
<p>Tile <em>area</em> is the size of the workforce in each occupation, from each country&rsquo;s official statistics
(see the &ldquo;Data sources&rdquo; note in the sidebar of every country page &mdash; e.g. Jobs and Skills Australia &amp; ABS,
US&nbsp;BLS &amp; O*NET, Statistics Canada, ONS, Destatis, and so on). Salary and workforce figures blend official
data with estimates; treat everything as indicative, not advice.</p>

<p class="foot">Exposure is recomputed from the sources above. Contains public sector information licensed under
CC&nbsp;BY&nbsp;4.0 (ILO) and MIT (OpenAI); adapted by percentile normalisation and crosswalking. This site is
independent and not affiliated with, or endorsed by, the ILO or OpenAI.</p>
</div>
</body>
</html>"""


def to_int(v):
    if v in (None, "", 0, "0", "0.00"):
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def load_outlook_map():
    """从 DB 读就业前景 outlook（AU/US/CA/UK 已入库）。
    返回 {(country, occ_code): {g,b,e,desc,src,s:[[year,emp,proj],...]}}。
    DB 不可用时返回 {} 并告警，不阻断构建。"""
    try:
        from db.connection import get_cursor
    except Exception as e:
        print("  [outlook] db module unavailable, skipping:", e)
        return {}
    m = {}
    try:
        with get_cursor() as cur:
            cur.execute("SELECT country,occ_code,base_year,end_year,growth_pct,growth_desc,source"
                        " FROM occupation_outlook_meta")
            for r in cur.fetchall():
                g = r["growth_pct"]
                m[(r["country"], str(r["occ_code"]))] = {
                    "g": round(g, 1) if g is not None else None,
                    "b": r["base_year"], "e": r["end_year"],
                    "desc": r["growth_desc"], "src": r["source"], "s": [],
                }
            cur.execute("SELECT country,occ_code,year,employment,is_projected"
                        " FROM occupation_outlook ORDER BY country,occ_code,year")
            for r in cur.fetchall():
                k = (r["country"], str(r["occ_code"]))
                if k in m:
                    e = r["employment"]
                    m[k]["s"].append([r["year"], int(round(e)) if e is not None else None,
                                      int(r["is_projected"])])
    except Exception as e:
        print("  [outlook] DB load failed, skipping:", e)
        return {}
    print(f"  [outlook] loaded {len(m)} occupations with outlook")
    return m


def build_record(o, cat_slug, outlook):
    ai = o.get("ai") or {}
    # AI exposure 首选权威 GenAI 指数 aioe_pct（0-100，ILO WP140 + Eloundou，见
    # scripts/compute_ai_exposure.py 与 job-treemap/README.md）：pct/10 → 0-10 刻度，
    # 天然铺满 1-9。仅当某职业尚无权威 aioe（ES/FR/JP/KR 待接 crosswalk、军职等）时，
    # 回退到 LLM 主观分 automation_exposure（round-half-up，避免 .5 刻度偶数舍入折叠成假山）。
    aioe_pct = ai.get("aioe_pct")
    if aioe_pct is not None:
        exposure = int(math.floor(aioe_pct / 10 + 0.5))
    else:
        exp_raw = ai.get("automation_exposure")
        exposure = int(math.floor(exp_raw + 0.5)) if exp_raw is not None else None
    if exposure is not None:
        exposure = max(0, min(10, exposure))
    edu = o.get("education") or []
    edu_stage = edu[0].get("stage") if edu and isinstance(edu[0], dict) else None
    cat_name = o.get("category")
    return {
        "title": o.get("name_en") or o.get("slug"),
        "slug": o.get("slug"),
        "anzsco": o.get("occ_code"),
        "category": cat_slug.get(cat_name, cat_name),
        "category_name": cat_name,
        "pay": to_int(o.get("avg_salary")),
        "jobs": to_int(o.get("workforce_size")),
        "education": edu_stage,
        "exposure": exposure,
        "exposure_rationale": ai.get("verdict_zh") or None,
        "aioe_pct": ai.get("aioe_pct"),
        "outlook": outlook.get((o.get("country"), str(o.get("occ_code")))),
        "url": None,
    }


# ── Static second-screen helpers ─────────────────────────────────

def esc(s):
    return html.escape(str(s), quote=True) if s not in (None, "") else ""


def exp_rgb(score):
    """Python port of the template's exposureColor (green→red, 0–10)."""
    if score is None:
        return (128, 128, 128)
    t = max(0, min(10, score)) / 10
    if t < 0.5:
        s = t / 0.5
        return (round(50 + s * 180), round(160 - s * 10), round(50 - s * 20))
    s = (t - 0.5) / 0.5
    return (round(230 + s * 25), round(150 - s * 110), round(30 - s * 10))


def exp_chip(score):
    r, g, b = exp_rgb(score)
    val = "&mdash;" if score is None else f"{score}/10"
    return (f'<span class="exp-chip" style="background:rgba({r},{g},{b},.18);'
            f'color:rgb({r},{g},{b})">{val}</span>')


def fmt_int(n):
    return "&mdash;" if n is None else f"{n:,}"


def country_stats(rows):
    total_jobs = sum(r["jobs"] or 0 for r in rows)
    scored = [r for r in rows if r["exposure"] is not None]
    wcnt = sum(r["jobs"] or 0 for r in scored)
    wsum = sum(r["exposure"] * (r["jobs"] or 0) for r in scored)
    inds = {}
    for r in rows:
        name = r["category_name"] or "Other"
        d = inds.setdefault(name, {"slug": r["category"] or "other",
                                   "n": 0, "jobs": 0, "wsum": 0, "wcnt": 0})
        d["n"] += 1
        d["jobs"] += r["jobs"] or 0
        if r["exposure"] is not None and r["jobs"]:
            d["wsum"] += r["exposure"] * r["jobs"]
            d["wcnt"] += r["jobs"]
    industries = [{
        "name": name, "slug": d["slug"], "n": d["n"], "jobs": d["jobs"],
        "avg": (d["wsum"] / d["wcnt"]) if d["wcnt"] else None,
    } for name, d in inds.items()]
    industries.sort(key=lambda x: (-(x["avg"] if x["avg"] is not None else -1), -x["jobs"]))
    return {
        "total_jobs": total_jobs, "scored": len(scored), "total": len(rows),
        "weighted_avg": (wsum / wcnt) if wcnt else 0.0,
        "has_pay": any(r["pay"] is not None for r in rows),
        "top": sorted(scored, key=lambda d: (-d["exposure"], -(d["jobs"] or 0)))[:20],
        "bottom": sorted(scored, key=lambda d: (d["exposure"], -(d["jobs"] or 0)))[:20],
        "industries": industries,
    }


def occ_table(items, has_pay, symbol):
    head = "<tr><th>#</th><th>Occupation</th><th>Code</th><th>Exposure</th>"
    if has_pay:
        head += "<th class='num'>Median pay</th>"
    head += "<th class='num'>Employed</th></tr>"
    body = []
    for i, r in enumerate(items, 1):
        pay = ""
        if has_pay:
            cell = (symbol + format(r["pay"], ",")) if r["pay"] is not None else "&mdash;"
            pay = f"<td class='num'>{cell}</td>"
        body.append(
            f"<tr><td>{i}</td><td>{esc(r['title'])}</td><td>{esc(r['anzsco'])}</td>"
            f"<td>{exp_chip(r['exposure'])}</td>{pay}"
            f"<td class='num'>{fmt_int(r['jobs'])}</td></tr>")
    return f"<table><thead>{head}</thead><tbody>{''.join(body)}</tbody></table>"


def fallback_summary(name, st):
    """Deterministic 150–300 word summary from the stats (used when no LLM copy)."""
    top_names = ", ".join(esc(r["title"]) for r in st["top"][:3])
    low_names = ", ".join(esc(r["title"]) for r in st["bottom"][:3])
    top_inds = ", ".join(esc(i["name"]) for i in st["industries"][:2] if i["avg"] is not None)
    avg = st["weighted_avg"]
    band = ("low" if avg < 3 else "moderate" if avg < 5
            else "elevated" if avg < 6.5 else "high")
    p1 = (f"Across {st['total']:,} occupations covering about {st['total_jobs']:,} workers, "
          f"{name}'s labour market carries a {band} average exposure to generative AI of "
          f"{avg:.1f} on a 0&ndash;10 scale, weighted by how many people each occupation employs. "
          f"Every score maps an occupation onto the ILO and OpenAI research indices, so a higher "
          f"number means more of the role's day-to-day tasks can already be performed or assisted by AI.")
    p2 = (f"The most exposed roles are {top_names} &mdash; jobs built around routine information "
          f"work that large language models handle well. The least exposed include {low_names}, "
          f"where physical, in-person or hands-on tasks dominate."
          + (f" By industry, {top_inds} sit toward the top of the range." if top_inds else "")
          + " Exposure is not the same as job loss: it flags where AI is most likely to reshape "
            "tasks first, and where workers may want to build complementary skills.")
    return f"<p>{p1}</p>\n<p>{p2}</p>"


def static_content(cc, name, st, summary_html, present):
    updated = datetime.now().strftime("%d %B %Y").lstrip("0")
    top_tbl = occ_table(st["top"], st["has_pay"], COUNTRY_META[cc][2])
    bot_tbl = occ_table(st["bottom"], st["has_pay"], COUNTRY_META[cc][2])
    irows = "".join(
        f'<tr id="ind-{i["slug"]}"><td>{esc(i["name"])}</td>'
        f'<td class="num">{i["n"]}</td>'
        f'<td class="num">{fmt_int(i["jobs"])}</td>'
        f'<td>{exp_chip(round(i["avg"]) if i["avg"] is not None else None)}</td></tr>'
        for i in st["industries"])
    ind_tbl = ("<table><thead><tr><th>Industry</th><th class='num'>Occupations</th>"
               "<th class='num'>Employed</th><th>Avg. exposure</th></tr></thead>"
               f"<tbody>{irows}</tbody></table>")
    country_links = " ".join(
        f'<a href="/{SLUG[c]}/">{esc(COUNTRY_META[c][0])}</a>'
        for c in present if c != cc)
    ind_links = " ".join(
        f'<a href="#ind-{i["slug"]}">{esc(i["name"])}</a>' for i in st["industries"])
    return f"""<h2>AI job automation risk in {esc(name)}</h2>
{summary_html}
<p class="meta-line">Data coverage: {st['scored']} of {st['total']} occupations scored &middot; Last updated {updated}</p>

<div class="two-col">
<div><h3>20 jobs most exposed to AI in {esc(name)}</h3>{top_tbl}</div>
<div><h3>20 jobs least exposed to AI in {esc(name)}</h3>{bot_tbl}</div>
</div>

<h3 id="industries">AI exposure by industry</h3>
{ind_tbl}

<h3>Explore more</h3>
<p class="meta-line">Other countries</p>
<div class="link-row">{country_links}</div>
<p class="meta-line">Industries on this page</p>
<div class="link-row">{ind_links}</div>

<h3>Methodology &amp; sources</h3>
<p>Every occupation is scored 0&ndash;10 for generative-AI exposure by combining two open, peer-reviewed
datasets &mdash; the ILO's Working Paper 140 index and OpenAI's <em>GPTs are GPTs</em> task-exposure study &mdash;
mapped onto {esc(name)}'s official occupation classification, then ranked on a single global percentile
scale so the numbers stay comparable between countries. Tile area is the size of each occupation's
workforce, from official statistics. <a href="../about.html">Full methodology &amp; data sources &rarr;</a></p>
"""


# ── Landing hub + SEO assets ─────────────────────────────────────

def build_landing(present, stats_by_cc):
    cards = []
    for cc in present:
        name = COUNTRY_META[cc][0]
        st = stats_by_cc[cc]
        r, g, b = exp_rgb(st["weighted_avg"])
        cards.append(
            f'<a class="cc-card" href="/{SLUG[cc]}/">'
            f'<span class="cc-name">{esc(name)}</span>'
            f'<span class="cc-meta">{fmt_int(st["total_jobs"])} workers &middot; {st["total"]} occupations</span>'
            f'<span class="cc-exp">Avg exposure '
            f'<b style="color:rgb({r},{g},{b})">{st["weighted_avg"]:.1f}</b><span class="cc-scale">/10</span></span>'
            f'</a>')
    title = "AI Job Risk Map — how exposed is every job to AI, across 13 countries"
    desc = ("An interactive map of how exposed jobs are to generative AI in 13 countries. "
            "Every occupation scored 0–10 using ILO and OpenAI research on each country's official data.")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{DOMAIN}/">
<meta name="robots" content="index,follow">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{DOMAIN}/">
<meta property="og:image" content="{DOMAIN}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{DOMAIN}/og-image.png">
<style>
:root{{--bg:#0a0a0f;--bg2:#12121a;--fg:#e0e0e8;--fg2:#9a9aa6;--accent:#e6961e;--line:rgba(255,255,255,.09)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1040px;margin:0 auto;padding:44px 22px 80px}}
.brand{{display:flex;align-items:center;gap:12px;margin-bottom:26px}}
.brand img{{width:38px;height:38px}}
.brand b{{font-size:19px;letter-spacing:-.01em}}
h1{{font-size:32px;line-height:1.2;letter-spacing:-.02em;margin:0 0 12px}}
.lead{{color:var(--fg2);font-size:17px;max-width:720px;margin:0 0 34px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px}}
.cc-card{{display:flex;flex-direction:column;gap:5px;padding:16px 18px;border:1px solid var(--line);border-radius:12px;background:var(--bg2);text-decoration:none;color:var(--fg);transition:border-color .15s,transform .15s}}
.cc-card:hover{{border-color:rgba(255,255,255,.28);transform:translateY(-2px)}}
.cc-name{{font-size:17px;font-weight:600}}
.cc-meta{{font-size:12.5px;color:var(--fg2)}}
.cc-exp{{font-size:13px;margin-top:2px}}
.cc-scale{{color:var(--fg2)}}
a.txt{{color:var(--accent)}}
.foot{{color:var(--fg2);font-size:13px;margin-top:40px;padding-top:18px;border-top:1px solid var(--line);line-height:1.6}}
</style>
</head>
<body>
<div class="wrap">
<div class="brand"><img src="favicon.svg" alt=""><b>{SITE_NAME}</b></div>
<h1>Which jobs are most exposed to AI?</h1>
<p class="lead">An interactive treemap of every occupation in 13 countries, coloured 0&ndash;10 by how
exposed it is to generative AI &mdash; computed from open ILO and OpenAI research, mapped onto each
country's official statistics. Pick a country:</p>
<div class="grid">
{''.join(cards)}
</div>
<p class="foot">Scores combine the ILO's Working Paper 140 index and OpenAI's <em>GPTs are GPTs</em>
task-exposure study. <a class="txt" href="about.html">How the AI exposure is measured &rarr;</a></p>
</div>
</body>
</html>"""


def build_og_image(path):
    """Simple 1200×630 branded share image (Pillow). SVG-free so scrapers render it."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as e:
        print("  [og] Pillow unavailable, skipping og-image.png:", e)
        return
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (10, 10, 15))
    d = ImageDraw.Draw(img)
    # logo mark: three rounded squares (matches favicon)
    d.rounded_rectangle([90, 96, 196, 262], radius=12, fill=(230, 150, 30))
    d.rounded_rectangle([212, 96, 318, 172], radius=12, fill=(50, 160, 50))
    d.rounded_rectangle([212, 186, 318, 262], radius=12, fill=(255, 80, 20))
    try:
        title_f = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 82)
        sub_f = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 34)
        dom_f = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
    except Exception:
        title_f = sub_f = dom_f = ImageFont.load_default()
    d.text((90, 330), "AI Job Risk Map", font=title_f, fill=(240, 240, 245))
    d.text((90, 438), "How exposed is every job to AI — 13 countries, one 0–10 scale.",
           font=sub_f, fill=(154, 154, 166))
    # exposure gradient strip
    for i in range(1020):
        t = i / 1019 * 10
        d.line([(90 + i, 520), (90 + i, 540)], fill=exp_rgb(t))
    d.text((90, 556), "aijobriskmap.com", font=dom_f, fill=(230, 150, 30))
    img.save(path, "PNG")
    print("  og-image.png written")


def build_sitemap(present):
    date = datetime.now().strftime("%Y-%m-%d")
    urls = [f"{DOMAIN}/", f"{DOMAIN}/about.html"] + [f"{DOMAIN}/{SLUG[cc]}/" for cc in present]
    items = "".join(f"<url><loc>{u}</loc><lastmod>{date}</lastmod></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{items}</urlset>\n")


ROBOTS = f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n"


def load_summaries():
    """Optional LLM-written summaries: job-treemap/summaries.json -> {cc: html}."""
    p = os.path.join(HERE, "summaries.json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print("  [summaries] failed to read, using fallback:", e)
    return {}


def main():
    occ = json.load(open(SRC, encoding="utf-8"))["occupations"]
    cat_slug = json.load(open(CATS, encoding="utf-8"))["category_slug"]
    template = open(TEMPLATE, encoding="utf-8").read()
    outlook = load_outlook_map()
    summaries = load_summaries()

    by_country = {}
    for o in occ:
        cc = o.get("country")
        if cc not in COUNTRY_META:
            continue
        by_country.setdefault(cc, []).append(build_record(o, cat_slug, outlook))

    present = [cc for cc in ORDER if cc in by_country]
    os.makedirs(DIST, exist_ok=True)

    # Remove legacy output from the old layout (uppercase per-country dirs +
    # the overview data/ copies) so rebuilds don't leave stale, unlinked pages.
    import shutil
    for cc in COUNTRY_META:
        legacy = os.path.join(DIST, cc)
        if os.path.isdir(legacy):
            shutil.rmtree(legacy, ignore_errors=True)
    shutil.rmtree(os.path.join(DIST, "data"), ignore_errors=True)

    # First pass: rows + stats per country (stats reused by pages + landing).
    rows_by_cc, stats_by_cc = {}, {}
    for cc in present:
        rows = sorted(by_country[cc], key=lambda d: (d["category"] or "", -(d["jobs"] or 0)))
        rows_by_cc[cc] = rows
        stats_by_cc[cc] = country_stats(rows)

    # ── Per-country standalone sites (own URL /slug/) ──────────────
    for cc in present:
        name, currency, symbol, source = COUNTRY_META[cc]
        rows, st = rows_by_cc[cc], stats_by_cc[cc]
        slug = SLUG[cc]

        cdir = os.path.join(DIST, slug)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(cdir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)

        cfg = {
            "cc": cc, "countryName": name, "currency": currency, "symbol": symbol,
            "sourceHtml": source, "dataUrl": "data.json", "aboutUrl": "../about.html",
            "ver": VER,
            "countries": [{"cc": c, "name": COUNTRY_META[c][0], "url": f"/{SLUG[c]}/"}
                          for c in present],
        }
        summary = summaries.get(cc) or fallback_summary(name, st)
        content = static_content(cc, name, st, summary, present)

        title = f"{name} AI Job Risk Map — which jobs are most exposed to AI"
        desc = (f"See how exposed {name}'s jobs are to generative AI: {st['total_jobs']:,} workers "
                f"across {st['total']} occupations, scored 0–10 using ILO and OpenAI research.")
        page = (template
                .replace("__CONFIG__", json.dumps(cfg, ensure_ascii=False))
                .replace("__TITLE__", esc(title))
                .replace("__META_DESC__", esc(desc))
                .replace("__CANONICAL__", f"{DOMAIN}/{slug}/")
                .replace("__SITE_NAME__", SITE_NAME)
                .replace("__OG_IMAGE__", f"{DOMAIN}/og-image.png")
                .replace("__STATIC_CONTENT__", content))
        with open(os.path.join(cdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page)
        with open(os.path.join(cdir, "favicon.svg"), "w", encoding="utf-8") as f:
            f.write(FAVICON)
        print(f"  {cc} -> /{slug}/: {len(rows)} occupations"
              + ("" if st["has_pay"] else " (no salary data — pay hidden)"))

    # ── Landing hub at root ───────────────────────────────────────
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_landing(present, stats_by_cc))
    with open(os.path.join(DIST, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON)

    # ── About / methodology page ──────────────────────────────────
    with open(os.path.join(DIST, "about.html"), "w", encoding="utf-8") as f:
        f.write(ABOUT_HTML.replace("__DOMAIN__", DOMAIN))
    print("  about.html written")

    # ── SEO assets ────────────────────────────────────────────────
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(ROBOTS)
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap(present))
    build_og_image(os.path.join(DIST, "og-image.png"))
    print("  robots.txt, sitemap.xml written")

    print(f"\nBuilt landing + {len(present)} country sites -> {DIST}")
    print("Countries:", ", ".join(present))


if __name__ == "__main__":
    main()
