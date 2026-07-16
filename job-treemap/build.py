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
YEAR = datetime.now().year  # temporalCoverage + static-map filenames (…-2026.png)
DATASET_URL = f"{DOMAIN}/dataset.csv"
SLUG = {
    "AU": "australia", "US": "united-states", "UK": "united-kingdom",
    "CA": "canada", "NZ": "new-zealand", "JP": "japan", "KR": "south-korea",
    "DE": "germany", "FR": "france", "ES": "spain", "IT": "italy",
    "NL": "netherlands", "IE": "ireland",
}

# Country pages live under /country/{slug}/ so the URL space reads as a hub.
def country_path(cc):
    return f"country/{SLUG[cc]}"


def country_url(cc):
    return f"{DOMAIN}/country/{SLUG[cc]}/"


def map_filename(cc):
    """Keyword+year PNG name for image SEO, e.g. ai-job-risk-map-united-states-2026.png."""
    return f"ai-job-risk-map-{SLUG[cc]}-{YEAR}.png"

# Inline SVG flags (mirrors site/src/lib/data.ts COUNTRY_FLAG; treemap is a
# self-contained deploy so the markup is duplicated here rather than imported).
FLAG = {
    "AU": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#00247D"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#CF142B" stroke-width="3"/><rect x="25" width="10" height="30" fill="#fff"/><rect y="10" width="60" height="10" fill="#fff"/><rect x="27" width="6" height="30" fill="#CF142B"/><rect y="12" width="60" height="6" fill="#CF142B"/><circle cx="30" cy="46" r="4.5" fill="#fff"/><circle cx="95" cy="13" r="2.6" fill="#fff"/><circle cx="106" cy="26" r="2.6" fill="#fff"/><circle cx="90" cy="36" r="2.6" fill="#fff"/><circle cx="101" cy="46" r="2.6" fill="#fff"/><circle cx="86" cy="49" r="1.7" fill="#fff"/></svg>',
    "CA": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#fff"/><rect width="30" height="60" fill="#D52B1E"/><rect x="90" width="30" height="60" fill="#D52B1E"/><path d="M60,11 l4,9 9,-2 -4,8 5,3 -8,4 1,6 -8,-2 -8,2 1,-6 -8,-4 5,-3 -4,-8 9,2 z" fill="#D52B1E"/></svg>',
    "NZ": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#00247D"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#CF142B" stroke-width="3"/><rect x="25" width="10" height="30" fill="#fff"/><rect y="10" width="60" height="10" fill="#fff"/><rect x="27" width="6" height="30" fill="#CF142B"/><rect y="12" width="60" height="6" fill="#CF142B"/><circle cx="100" cy="13" r="3" fill="#CF142B" stroke="#fff" stroke-width="1"/><circle cx="108" cy="31" r="3" fill="#CF142B" stroke="#fff" stroke-width="1"/><circle cx="91" cy="35" r="3" fill="#CF142B" stroke="#fff" stroke-width="1"/><circle cx="100" cy="49" r="3" fill="#CF142B" stroke="#fff" stroke-width="1"/></svg>',
    "US": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#fff"/><g fill="#B22234"><rect width="120" height="4.62"/><rect y="9.23" width="120" height="4.62"/><rect y="18.46" width="120" height="4.62"/><rect y="27.69" width="120" height="4.62"/><rect y="36.92" width="120" height="4.62"/><rect y="46.15" width="120" height="4.62"/><rect y="55.38" width="120" height="4.62"/></g><rect width="48" height="32.31" fill="#3C3B6E"/><g fill="#fff"><circle cx="6" cy="5" r="1.4"/><circle cx="16" cy="5" r="1.4"/><circle cx="26" cy="5" r="1.4"/><circle cx="36" cy="5" r="1.4"/><circle cx="11" cy="11" r="1.4"/><circle cx="21" cy="11" r="1.4"/><circle cx="31" cy="11" r="1.4"/><circle cx="41" cy="11" r="1.4"/><circle cx="6" cy="17" r="1.4"/><circle cx="16" cy="17" r="1.4"/><circle cx="26" cy="17" r="1.4"/><circle cx="36" cy="17" r="1.4"/><circle cx="11" cy="23" r="1.4"/><circle cx="21" cy="23" r="1.4"/><circle cx="31" cy="23" r="1.4"/><circle cx="41" cy="23" r="1.4"/><circle cx="6" cy="29" r="1.4"/><circle cx="16" cy="29" r="1.4"/><circle cx="26" cy="29" r="1.4"/><circle cx="36" cy="29" r="1.4"/></g></svg>',
    "UK": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><clipPath id="ukc"><rect width="120" height="60"/></clipPath><g clip-path="url(#ukc)"><rect width="120" height="60" fill="#012169"/><path d="M0,0 L120,60 M120,0 L0,60" stroke="#fff" stroke-width="12"/><path d="M0,0 L120,60 M120,0 L0,60" stroke="#C8102E" stroke-width="8" clip-path="url(#ukc)"/><rect x="50" width="20" height="60" fill="#fff"/><rect y="20" width="120" height="20" fill="#fff"/><rect x="54" width="12" height="60" fill="#C8102E"/><rect y="24" width="120" height="12" fill="#C8102E"/></g></svg>',
    "DE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="20" fill="#000"/><rect y="20" width="120" height="20" fill="#DD0000"/><rect y="40" width="120" height="20" fill="#FFCE00"/></svg>',
    "FR": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="40" height="60" fill="#0055A4"/><rect x="40" width="40" height="60" fill="#fff"/><rect x="80" width="40" height="60" fill="#EF4135"/></svg>',
    "ES": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#AA151B"/><rect y="15" width="120" height="30" fill="#F1BF00"/></svg>',
    "IT": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="40" height="60" fill="#008C45"/><rect x="40" width="40" height="60" fill="#F4F5F0"/><rect x="80" width="40" height="60" fill="#CD212A"/></svg>',
    "NL": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="20" fill="#AE1C28"/><rect y="20" width="120" height="20" fill="#fff"/><rect y="40" width="120" height="20" fill="#21468B"/></svg>',
    "IE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="40" height="60" fill="#169B62"/><rect x="40" width="40" height="60" fill="#fff"/><rect x="80" width="40" height="60" fill="#FF883E"/></svg>',
    "JP": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#fff"/><circle cx="60" cy="30" r="18" fill="#BC002D"/></svg>',
    "KR": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#fff"/><g transform="translate(60,30)"><clipPath id="krt"><circle r="12"/></clipPath><circle r="12" fill="#CD2E3A"/><path d="M-12,0 a6,6 0 0,1 12,0 a6,6 0 0,0 12,0 L12,12 L-12,12 Z" fill="#0047A0" clip-path="url(#krt)"/></g><g fill="#000"><g transform="translate(60,30) rotate(56.31)"><g transform="translate(-24.5,0)"><rect x="-4" y="-3.4" width="8" height="1.6"/><rect x="-4" y="-0.8" width="8" height="1.6"/><rect x="-4" y="1.8" width="8" height="1.6"/></g><g transform="translate(24.5,0)"><rect x="-4" y="-3.4" width="3.2" height="1.6"/><rect x="0.8" y="-3.4" width="3.2" height="1.6"/><rect x="-4" y="-0.8" width="3.2" height="1.6"/><rect x="0.8" y="-0.8" width="3.2" height="1.6"/><rect x="-4" y="1.8" width="3.2" height="1.6"/><rect x="0.8" y="1.8" width="3.2" height="1.6"/></g></g><g transform="translate(60,30) rotate(-56.31)"><g transform="translate(-24.5,0)"><rect x="-4" y="-3.4" width="8" height="1.6"/><rect x="-4" y="-0.8" width="3.2" height="1.6"/><rect x="0.8" y="-0.8" width="3.2" height="1.6"/><rect x="-4" y="1.8" width="8" height="1.6"/></g><g transform="translate(24.5,0)"><rect x="-4" y="-3.4" width="3.2" height="1.6"/><rect x="0.8" y="-3.4" width="3.2" height="1.6"/><rect x="-4" y="-0.8" width="8" height="1.6"/><rect x="-4" y="1.8" width="3.2" height="1.6"/><rect x="0.8" y="1.8" width="3.2" height="1.6"/></g></g></g></svg>',
}

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
           '<rect width="32" height="32" rx="6" fill="#0a0a0f"/>'
           '<rect x="4" y="4" width="13" height="24" rx="1.5" fill="#e6961e"/>'
           '<rect x="19" y="4" width="9" height="11" rx="1.5" fill="#32a032"/>'
           '<rect x="19" y="17" width="9" height="11" rx="1.5" fill="#ff5014"/>'
           '</svg>')


METHODOLOGY_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Methodology &amp; Data Sources &mdash; AI Job Risk Map</title>
<meta name="description" content="Full methodology behind the AI exposure score: ILO Working Paper 140 and OpenAI's GPTs-are-GPTs study, mapped onto each country's official occupation classification. Download the full dataset (CSV).">
<link rel="canonical" href="__DOMAIN__/methodology.html">
<meta name="robots" content="index,follow">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="article">
<meta property="og:site_name" content="AI Job Risk Map">
<meta property="og:title" content="Methodology &amp; Data Sources — AI Job Risk Map">
<meta property="og:url" content="__DOMAIN__/methodology.html">
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
<p class="lead">The colour of every tile on this map &mdash; the AI exposure score, 0&ndash;10 &mdash; is derived from
published exposure research, occupational crosswalks and, where official mappings are unavailable, clearly
identified model-assisted mappings. It combines two open, generative-AI-era research datasets, mapped onto
each country&rsquo;s official occupation classification.</p>

<h2>Data sources</h2>
<p>The exposure index draws on two published research datasets, both openly licensed for reuse:</p>

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
onto the official ISCO-08 structure by an LLM (a clearly identified model-assisted mapping), then scored as
above. Tagged separately (<code>_llmmap</code>); will be upgraded when the official table is wired in.</td></tr>
</tbody>
</table>

<h2>About the underlying job data</h2>
<p>Tile <em>area</em> is the size of the workforce in each occupation, from each country&rsquo;s official statistics
(see the &ldquo;Data sources&rdquo; note in the sidebar of every country page &mdash; e.g. Jobs and Skills Australia &amp; ABS,
US&nbsp;BLS &amp; O*NET, Statistics Canada, ONS, Destatis, and so on). Salary and workforce figures blend official
data with estimates; treat everything as indicative, not advice.</p>

<h2>Download the data</h2>
<p>The full scored dataset &mdash; every occupation in all 13 countries, with its AI-exposure score
(0&ndash;10), global percentile, workforce size and average pay &mdash; is available as a single CSV:</p>
<div class="src">
<strong><a href="dataset.csv" download>dataset.csv</a></strong> &mdash; one row per occupation across
every country (country, occupation, official code, category, AI-exposure 0&ndash;10, percentile,
average annual pay, workforce). Free to reuse with attribution to aijobriskmap.com.
</div>
<p>Per-country high-resolution PNG maps are linked from each country page and from the
<a href="index.html">home page</a>.</p>

<h2>Read the source papers</h2>
<ul>
<li>ILO Working Paper 140 &mdash; <a href="https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure">Generative AI and Jobs: A Refined Global Index of Occupational Exposure</a> (Gmyrek et&nbsp;al., 2025; CC&nbsp;BY&nbsp;4.0).</li>
<li>OpenAI &mdash; <a href="https://github.com/openai/GPTs-are-GPTs">GPTs are GPTs: An Early Look at the Labor Market Impact Potential of LLMs</a> (Eloundou et&nbsp;al., 2023; dataset MIT-licensed).</li>
</ul>

<p class="foot">Exposure is recomputed from the sources above. Contains public sector information licensed under
CC&nbsp;BY&nbsp;4.0 (ILO) and MIT (OpenAI); adapted by percentile normalisation and crosswalking. This site is
independent and not affiliated with, or endorsed by, the ILO or OpenAI.</p>
</div>
__FOOTER__
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


def fmt_big_jobs(n):
    """Match the template's statTotalJobs formatting (JS: >=1e6 -> X.XM)."""
    if not n:
        return "&mdash;"
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n:,}"


def build_noscript(name, st):
    """First-screen fallback for crawlers / no-JS: the canvas can't render, so
    surface in text what the map shows and point at the ranked tables below."""
    return (
        '<noscript><div class="noscript-map"><div class="ns-inner">'
        f'<h2>AI exposure of {esc(name)}&rsquo;s jobs</h2>'
        f'<p>This treemap is interactive and needs JavaScript. You can still read all the '
        f'underlying data below: {st["total"]} occupations in {esc(name)}, ranked by how exposed '
        f'they are to generative AI, with an industry breakdown and full methodology.</p>'
        '<p><a href="#industries">Jump to the rankings &darr;</a></p>'
        '</div></div></noscript>')


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
        head += "<th class='num'>Average annual pay</th>"
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


def collapsible_table(heading, table_html, count):
    """Full-width table with the first 5 rows shown; the rest stay in the DOM
    (crawlable) but are CSS-collapsed until the heading toggle expands them."""
    btn = (f'<button type="button" class="tbl-toggle">Show all {count}</button>'
           if count > 5 else "")
    return (f'<div class="tbl-wrap" data-count="{count}">'
            f'<h3 class="tbl-head"><span>{heading}</span>{btn}</h3>'
            f'{table_html}</div>')


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
        f'<a href="/country/{SLUG[c]}/">{esc(COUNTRY_META[c][0])}</a>'
        for c in present if c != cc)
    ind_links = " ".join(
        f'<a href="#ind-{i["slug"]}">{esc(i["name"])}</a>' for i in st["industries"])
    avg = st["weighted_avg"]
    map_alt = f"AI job risk map {name} {YEAR} - {st['total']} occupations by AI exposure risk"
    # Downloadable/shareable image asset (also the crawlable page-level <img> for image
    # SEO). Placed at the very bottom and framed as a download card, not a second copy
    # of the interactive map above, so it doesn't read as a redundant visualisation.
    map_dl = (
        f'<h3 id="download">Download / share this map</h3>'
        f'<figure class="map-download">'
        f'<a href="/static/maps/{map_filename(cc)}" target="_blank" rel="noopener">'
        f'<img src="/static/maps/{map_filename(cc)}" alt="{esc(map_alt)}" '
        f'width="800" height="600" loading="lazy"></a>'
        f'<figcaption>AI Job Risk Map for {esc(name)}: average AI exposure {avg:.1f}/10 across '
        f'{st["total"]} occupations. Free to reuse with attribution to aijobriskmap.com.</figcaption>'
        f'<div class="md-actions">'
        f'<a class="md-btn" href="/static/maps/{map_filename(cc)}" download>Download PNG</a>'
        f'<button type="button" class="md-btn sec" id="embedBtn">Embed this map</button></div>'
        f'</figure>')
    top_block = collapsible_table(
        f"{len(st['top'])} jobs most exposed to AI in {esc(name)}", top_tbl, len(st["top"]))
    bot_block = collapsible_table(
        f"{len(st['bottom'])} jobs least exposed to AI in {esc(name)}", bot_tbl, len(st["bottom"]))
    return f"""<h2>AI job automation risk in {esc(name)}</h2>
{summary_html}
<p class="meta-line">Data coverage: {st['scored']} of {st['total']} occupations scored &middot; Last updated {updated}</p>

{top_block}
{bot_block}

<h3 id="industries">AI exposure by industry</h3>
{ind_tbl}

<h3>Explore more</h3>
<p class="meta-line">Other countries</p>
<div class="link-row">{country_links}</div>
<p class="meta-line">Industries on this page</p>
<div class="link-row">{ind_links}</div>

<h3>Methodology &amp; sources</h3>
<p>Every occupation is scored 0&ndash;10 for generative-AI exposure by combining two open, published
research datasets &mdash; the ILO's Working Paper 140 index and OpenAI's <em>GPTs are GPTs</em> task-exposure study &mdash;
mapped onto {esc(name)}'s official occupation classification, then ranked on a single global percentile
scale so the numbers stay comparable between countries. Tile area is the size of each occupation's
workforce, from official statistics. <a href="/methodology.html">Full methodology &amp; data sources &rarr;</a></p>

{map_dl}
"""


# ── Landing hub + SEO assets ─────────────────────────────────────

def build_landing(present, stats_by_cc):
    cards = []
    for cc in present:
        name = COUNTRY_META[cc][0]
        st = stats_by_cc[cc]
        r, g, b = exp_rgb(st["weighted_avg"])
        cards.append(
            f'<a class="cc-card" href="/country/{SLUG[cc]}/">'
            f'<span class="cc-head"><span class="cc-flag">{FLAG.get(cc, "")}</span>'
            f'<span class="cc-name">{esc(name)}</span></span>'
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
{ld_script(dataset_ld_global(present))}
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
.cc-head{{display:flex;align-items:center;gap:9px}}
.cc-flag svg{{width:26px;height:auto;display:block;border-radius:3px;box-shadow:0 0 0 1px rgba(255,255,255,.14)}}
.cc-name{{font-size:17px;font-weight:600}}
.cc-meta{{font-size:12.5px;color:var(--fg2)}}
.cc-exp{{font-size:13px;margin-top:2px}}
.cc-scale{{color:var(--fg2)}}
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
</div>
{build_footer()}
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


# ── Shared document-page shell (about / embed hub) ───────────────

DOC_CSS = """<style>
:root{--bg:#0a0a0f;--bg2:#12121a;--fg:#e0e0e8;--fg2:#9a9aa6;--accent:#e6961e;--line:rgba(255,255,255,.09)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:0 auto;padding:40px 22px 80px}
a{color:var(--accent)}
.back{display:inline-block;margin-bottom:28px;font-size:14px;font-weight:600;text-decoration:none}
.back:hover{text-decoration:underline}
h1{font-size:30px;line-height:1.25;margin:0 0 10px}
.lead{color:var(--fg2);font-size:17px;margin:0 0 30px}
h2{font-size:20px;margin:38px 0 12px;padding-top:22px;border-top:1px solid var(--line)}
p{margin:10px 0}
ul,ol{padding-left:22px}li{margin:7px 0}
code{background:var(--bg2);padding:1px 6px;border-radius:4px;font-size:13px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
textarea{width:100%;min-height:110px;background:var(--bg2);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:12px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;line-height:1.5;resize:vertical}
.btn{display:inline-block;margin-top:8px;padding:8px 16px;background:var(--accent);color:#0a0a0f;border:none;border-radius:7px;font-weight:700;font-size:14px;cursor:pointer;text-decoration:none}
.btn.sec{background:var(--bg2);color:var(--fg);border:1px solid var(--line)}
.src{background:var(--bg2);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:12px 0}
.quote{border-left:3px solid var(--accent);padding:10px 14px;margin:12px 0;background:var(--bg2);border-radius:0 8px 8px 0}
.mgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:14px;margin:16px 0}
.mcard{border:1px solid var(--line);border-radius:12px;background:var(--bg2);overflow:hidden;margin:0}
.mcard img{width:100%;height:auto;display:block;background:#000;aspect-ratio:4/3;object-fit:cover}
.mcard .mc-body{padding:10px 12px}
.mcard .mc-name{font-weight:600;font-size:14px;margin-bottom:4px}
.mcard .mc-meta{font-size:11.5px;color:var(--fg2);margin-bottom:7px}
.mcard .mc-body a{font-size:12px;display:inline-block;margin-right:10px}
label{display:block;font-size:13px;color:var(--fg2);margin:12px 0 4px}
input,select{width:100%;padding:9px 11px;background:var(--bg2);color:var(--fg);border:1px solid var(--line);border-radius:7px;font-size:14px;font-family:inherit}
select option{background:var(--bg2)}
.foot{color:var(--fg2);font-size:13px;margin-top:44px;padding-top:18px;border-top:1px solid var(--line)}
</style>"""


def doc_head(title, desc, canonical_path, robots="index,follow"):
    og = f"{DOMAIN}/og-image.png"
    return (f'<!doctype html><html lang="en"><head>'
            f'<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title>'
            f'<meta name="description" content="{esc(desc)}">'
            f'<link rel="canonical" href="{DOMAIN}{canonical_path}">'
            f'<meta name="robots" content="{robots}">'
            f'<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE_NAME}">'
            f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
            f'<meta property="og:url" content="{DOMAIN}{canonical_path}"><meta property="og:image" content="{og}">'
            f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{og}">'
            f'{DOC_CSS}</head>')


def build_footer():
    """Shared site footer (nav link group + copyright) injected on every page.
    Self-contained (own scoped <style>) so it renders consistently across the
    landing, about, methodology, embed and country-page templates."""
    return f"""<style>
.site-footer{{max-width:1080px;margin:0 auto;padding:28px 22px 44px;border-top:1px solid rgba(255,255,255,.09);color:#9a9aa6;font:13px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}}
.site-footer nav{{display:flex;flex-wrap:wrap;gap:10px 20px;margin-bottom:12px}}
.site-footer nav a{{color:#e6961e;text-decoration:none;font-weight:600}}
.site-footer nav a:hover{{text-decoration:underline}}
.site-footer .copy{{margin:0}}
</style>
<footer class="site-footer">
<nav>
<a href="/">Home</a>
<a href="/embed">Download &amp; embed</a>
<a href="/methodology.html">Methodology</a>
<a href="/about.html">About</a>
<a href="/dataset.csv" download>Dataset (CSV)</a>
</nav>
<p class="copy">&copy; {YEAR} AI Job Risk Map &middot; aijobriskmap.com &middot; Maps &amp; data licensed
CC&nbsp;BY&nbsp;4.0 (ILO) and MIT (OpenAI). Independent; not affiliated with, or endorsed by, the ILO or OpenAI.</p>
</footer>"""


def map_card(cc, st):
    """One PNG map download card (embed / press-kit download grid)."""
    name = COUNTRY_META[cc][0]
    png = f"/static/maps/{map_filename(cc)}"
    alt = f"AI job risk map {name} {YEAR} - {st['total']} occupations by AI exposure risk"
    return (f'<figure class="mcard">'
            f'<img src="{png}" alt="{esc(alt)}" width="800" height="600" loading="lazy">'
            f'<figcaption class="mc-body"><div class="mc-name">{esc(name)}</div>'
            f'<div class="mc-meta">{st["total"]} occupations &middot; avg {st["weighted_avg"]:.1f}/10</div>'
            f'<a href="{png}" download>Download PNG</a></figcaption></figure>')


def build_about():
    title = "About — AI Job Risk Map"
    desc = ("AI Job Risk Map is a free, independent atlas of how exposed 5,000+ jobs in 13 "
            "countries are to generative AI, on one comparable 0–10 scale.")
    body = f"""<body><div class="wrap">
<a class="back" href="/">&larr; Back to the map</a>
<h1>About AI Job Risk Map</h1>
<p class="lead">A free, independent atlas of how exposed the world&rsquo;s jobs are to generative AI &mdash;
5,000+ occupations across 13 countries, on one comparable 0&ndash;10 scale.</p>

<h2>What it is</h2>
<p>AI Job Risk Map turns two open, generative-AI-era research datasets into an interactive picture of the
labour market. Every occupation in each country is coloured 0&ndash;10 by its AI-exposure score and sized by
how many people it employs, so you can see at a glance where generative AI is most likely to reshape work.</p>

<h2>Who it&rsquo;s for</h2>
<ul>
<li><strong>Workers &amp; students</strong> weighing where to invest their skills.</li>
<li><strong>Journalists &amp; researchers</strong> who need a comparable, source-backed exposure number
(see the <a href="/embed">embed &amp; press kit</a>).</li>
<li><strong>Policymakers &amp; educators</strong> looking at exposure across whole industries and countries.</li>
</ul>

<h2>How it&rsquo;s different</h2>
<p>Instead of one country or one headline number, the map puts 13 national labour markets on a single global
percentile scale, so an exposure score means the same thing whether you&rsquo;re looking at Australia or Japan.
Scores are recomputed from published research rather than asserted &mdash; see the
<a href="/methodology.html">full methodology</a>.</p>

<h2>Independence &amp; licensing</h2>
<p>This site is independent and not affiliated with, or endorsed by, the ILO or OpenAI. It builds on the ILO&rsquo;s
Working Paper 140 (CC&nbsp;BY&nbsp;4.0) and OpenAI&rsquo;s <em>GPTs are GPTs</em> dataset (MIT). The map, the
<a href="/dataset.csv" download>dataset</a> and the static images are free to reuse with attribution to
aijobriskmap.com.</p>

<h2>Learn more</h2>
<ul>
<li><a href="/methodology.html">Methodology &amp; data sources</a></li>
<li><a href="/dataset.csv" download>Download the full dataset (CSV)</a></li>
<li><a href="/embed">Embed the map / press kit</a></li>
</ul>
</div>
{build_footer()}
</body></html>"""
    return doc_head(title, desc, "/about.html") + body


def build_embed_hub(present, stats_by_cc):
    title = "Embed & Download AI Job Risk Maps — Free for Journalists & Bloggers"
    desc = ("Download free high-resolution AI job risk maps for 13 countries (CC BY 4.0), embed the "
            "interactive map, and grab ready-to-use citations. One minute to publish.")
    # Per-country data for the JS-driven snippet + citation builders.
    countries_js = json.dumps(
        [{"slug": SLUG[c], "name": COUNTRY_META[c][0],
          "total": stats_by_cc[c]["total"],
          "avg": round(stats_by_cc[c]["weighted_avg"], 1)} for c in present],
        ensure_ascii=False)
    grid = "".join(map_card(c, stats_by_cc[c]) for c in present)
    body = f"""<body><div class="wrap">
<a class="back" href="/">&larr; Back to the map</a>
<h1>Embed &amp; download AI Job Risk Maps &mdash; free for journalists &amp; bloggers</h1>
<p class="lead">Everything you need to publish in about a minute: free high-resolution maps for
13 countries, an interactive embed, and ready-to-paste citations. Free to use with attribution.</p>

<h2>1. Interactive embed</h2>
<label for="ctry">Country</label>
<select id="ctry"></select>
<textarea id="embedCode" readonly></textarea>
<button class="btn" id="copyEmbed">Copy code</button>

<h2>2. Static image download</h2>
<p>High-resolution PNG maps, one per country. Licensed <strong>CC&nbsp;BY&nbsp;4.0</strong> &mdash;
free to use with a link back to aijobriskmap.com.</p>
<div class="mgrid">{grid}</div>

<h2>3. How to cite</h2>
<p>Copy-paste, then adjust the country if needed:</p>
<p><strong>Plain text</strong></p>
<div class="quote" id="citeText"></div>
<button class="btn sec" id="copyCiteText">Copy text</button>
<p style="margin-top:18px"><strong>HTML (keeps the backlink)</strong></p>
<div class="quote"><code id="citeHtml"></code></div>
<button class="btn sec" id="copyCiteHtml">Copy HTML</button>

<h2>4. Data source</h2>
<p>All figures come from our recomputed exposure index. See the
<a href="/methodology.html">full methodology</a> or
<a href="/dataset.csv" download>download the complete dataset (CSV)</a>.</p>

<h2>5. Request a custom map</h2>
<p>Need a specific country, industry cut or resolution? Tell us and we&rsquo;ll get back to you.</p>
<form id="leadForm" class="src">
<label for="lf-email">Email</label><input id="lf-email" type="email" required placeholder="you@newsroom.com">
<label for="lf-country">Country / region of interest</label><input id="lf-country" type="text" placeholder="e.g. United States, or EU-wide">
<label for="lf-use">Use case</label><input id="lf-use" type="text" placeholder="e.g. feature on AI and accounting jobs">
<button class="btn" type="submit" style="margin-top:14px">Send request</button>
</form>

<p class="foot">Maps &amp; data licensed CC&nbsp;BY&nbsp;4.0. AI Job Risk Map is independent and not affiliated
with the ILO or OpenAI. &middot; aijobriskmap.com</p>
</div>
<script>
const COUNTRIES = {countries_js};
const DOMAIN = "{DOMAIN}";
const sel = document.getElementById("ctry");
COUNTRIES.forEach((c,i) => {{
  const o = document.createElement("option"); o.value = i; o.textContent = c.name; sel.appendChild(o);
}});
function render() {{
  const c = COUNTRIES[sel.value];
  const src = DOMAIN + "/embed/" + c.slug;
  document.getElementById("embedCode").value =
    '<iframe src="' + src + '" width="800" height="600" frameborder="0" ' +
    'title="AI Job Risk Map ' + c.name + ' {YEAR}" loading="lazy"></iframe>\\n' +
    '<p><a href="' + DOMAIN + '/country/' + c.slug + '/">Source: AI Job Risk Map &ndash; ' + c.name + '</a></p>';
  const t = "According to AI Job Risk Map, which analyzed " + c.total + " occupations in " + c.name +
    " using ILO and OpenAI data, the average AI exposure is " + c.avg + "/10.";
  document.getElementById("citeText").textContent = t;
  document.getElementById("citeHtml").textContent =
    'According to <a href="' + DOMAIN + '">AI Job Risk Map</a>, which analyzed ' + c.total +
    ' occupations in ' + c.name + ' using ILO and OpenAI data, the average AI exposure is ' + c.avg + '/10.';
}}
sel.addEventListener("change", render); render();
function copy(id, btn) {{
  const el = document.getElementById(id);
  const txt = el.value !== undefined ? el.value : el.textContent;
  navigator.clipboard.writeText(txt).then(() => {{
    const old = btn.textContent; btn.textContent = "Copied!"; setTimeout(() => btn.textContent = old, 1500);
  }});
}}
document.getElementById("copyEmbed").addEventListener("click", e => copy("embedCode", e.target));
document.getElementById("copyCiteText").addEventListener("click", e => copy("citeText", e.target));
document.getElementById("copyCiteHtml").addEventListener("click", e => copy("citeHtml", e.target));
// Custom-map request: opens the visitor's mail client (no third-party backend).
// TODO: point at a real endpoint (Formspree or api/polls_api.py) to auto-collect leads.
document.getElementById("leadForm").addEventListener("submit", e => {{
  e.preventDefault();
  const email = document.getElementById("lf-email").value;
  const country = document.getElementById("lf-country").value;
  const use = document.getElementById("lf-use").value;
  const body = encodeURIComponent("Email: " + email + "\\nCountry: " + country + "\\nUse case: " + use);
  window.location.href = "mailto:hello@aijobriskmap.com?subject=Custom%20map%20request&body=" + body;
}});
</script>
{build_footer()}
</body></html>"""
    return doc_head(title, desc, "/embed") + body


def build_sitemap(present):
    # /embed/{slug} pages are intentionally omitted (noindex iframe targets).
    date = datetime.now().strftime("%Y-%m-%d")
    urls = ([f"{DOMAIN}/", f"{DOMAIN}/about.html", f"{DOMAIN}/methodology.html",
             f"{DOMAIN}/embed"] + [country_url(cc) for cc in present])
    items = "".join(f"<url><loc>{u}</loc><lastmod>{date}</lastmod></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{items}</urlset>\n")


ROBOTS = f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n"


def build_llms(present, stats_by_cc):
    """Minimal Markdown summary for AI crawlers (llms.txt convention)."""
    lines = [
        f"# {SITE_NAME}",
        "",
        "> Interactive treemaps showing how exposed each occupation is to generative AI "
        "across 13 countries. Every occupation is scored 0–10 by combining two open research "
        "datasets — the ILO's Working Paper 140 index and OpenAI's \"GPTs are GPTs\" "
        "task-exposure study — mapped onto each country's official occupation classification "
        "and ranked on a single global percentile scale so the numbers stay comparable "
        "between countries. Tile area is the size of each occupation's workforce.",
        "",
        "## Country maps",
    ]
    for cc in present:
        name = COUNTRY_META[cc][0]
        st = stats_by_cc[cc]
        lines.append(
            f"- [{name}]({country_url(cc)}): {st['total']} occupations, "
            f"{st['total_jobs']:,} workers, average AI exposure {st['weighted_avg']:.1f}/10")
    lines += [
        "",
        "## About",
        f"- [Methodology & sources]({DOMAIN}/methodology.html): how the 0–10 AI exposure score is "
        "computed, data sources, and how each country is mapped to ISCO-08.",
        f"- [Full dataset (CSV)]({DATASET_URL}): every occupation in all 13 countries with its "
        "AI-exposure score, percentile, workforce and average pay.",
        "",
    ]
    return "\n".join(lines)


# ── Structured data (JSON-LD) ────────────────────────────────────

def ld_script(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>")


def dataset_ld_country(cc, name, st, has_png):
    dist = [{"@type": "DataDownload", "encodingFormat": "CSV", "contentUrl": DATASET_URL}]
    if has_png:
        dist.append({"@type": "DataDownload", "encodingFormat": "image/png",
                     "contentUrl": f"{DOMAIN}/static/maps/{map_filename(cc)}"})
    return {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": f"AI Job Risk Map — {name}: {st['total']} occupations by AI exposure",
        "description": (f"AI exposure scores (0–10) for {st['total']} occupations in {name}, "
                        f"covering about {st['total_jobs']:,} workers, based on ILO Working "
                        f"Paper 140 and OpenAI's GPTs are GPTs study."),
        "url": country_url(cc),
        "keywords": ["AI job risk map", f"AI exposure {name}", "jobs at risk from AI"],
        "creator": {"@type": "Organization", "name": SITE_NAME, "url": DOMAIN},
        "distribution": dist,
        "temporalCoverage": str(YEAR),
        "spatialCoverage": name,
        "isAccessibleForFree": True,
    }


def dataset_ld_global(present):
    return {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "AI Job Risk Map — 13 Countries, 5000+ Occupations",
        "description": ("Interactive treemap of AI exposure for 5000+ occupations across 13 "
                        "countries, based on ILO Working Paper 140 and OpenAI's GPTs are GPTs study."),
        "url": DOMAIN + "/",
        "keywords": ["AI job risk map", "AI exposure by country", "jobs at risk from AI"],
        "creator": {"@type": "Organization", "name": SITE_NAME, "url": DOMAIN},
        "distribution": [{"@type": "DataDownload", "encodingFormat": "CSV",
                          "contentUrl": DATASET_URL}],
        "temporalCoverage": str(YEAR),
        "spatialCoverage": [COUNTRY_META[c][0] for c in present],
        "isAccessibleForFree": True,
    }


def breadcrumb_ld(cc, name):
    # Schema only — no visible breadcrumb rendered on the page (per spec).
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": country_url(cc)},
        ],
    }


def write_dataset_csv(path, rows_by_cc, present):
    """One row per occupation across all countries — the /dataset.csv download."""
    import csv
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["country", "country_code", "occupation", "occupation_code", "category",
                    "ai_exposure_0_10", "ai_exposure_percentile", "avg_annual_pay", "workforce"])
        for cc in present:
            name = COUNTRY_META[cc][0]
            for r in rows_by_cc[cc]:
                w.writerow([name, cc, r["title"], r["anzsco"], r["category_name"],
                            r["exposure"] if r["exposure"] is not None else "",
                            r["aioe_pct"] if r["aioe_pct"] is not None else "",
                            r["pay"] if r["pay"] is not None else "",
                            r["jobs"] if r["jobs"] is not None else ""])


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

    # Remove legacy output from older layouts so rebuilds don't leave stale,
    # unlinked pages: uppercase per-country dirs (very old), lowercase per-country
    # dirs at the root (previous /slug/ layout) and the old overview data/ copies.
    # NB: static/ is preserved — the Playwright-shot PNG maps live there.
    import shutil
    for cc in COUNTRY_META:
        for legacy in (os.path.join(DIST, cc), os.path.join(DIST, SLUG.get(cc, cc))):
            if os.path.isdir(legacy):
                shutil.rmtree(legacy, ignore_errors=True)
    shutil.rmtree(os.path.join(DIST, "data"), ignore_errors=True)
    shutil.rmtree(os.path.join(DIST, "country"), ignore_errors=True)
    shutil.rmtree(os.path.join(DIST, "embed"), ignore_errors=True)

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

        cdir = os.path.join(DIST, "country", slug)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(cdir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)

        embed_snippet = (
            f'<iframe src="{DOMAIN}/embed/{slug}" width="800" height="600" frameborder="0" '
            f'title="AI Job Risk Map {name} {YEAR}" loading="lazy"></iframe>\n'
            f'<p><a href="{DOMAIN}/country/{slug}/">Source: AI Job Risk Map — {name}</a></p>')
        cfg = {
            "cc": cc, "countryName": name, "currency": currency, "symbol": symbol,
            "sourceHtml": source, "dataUrl": "data.json", "aboutUrl": "/methodology.html",
            "ver": VER, "embedSnippet": embed_snippet,
            "countries": [{"cc": c, "name": COUNTRY_META[c][0], "url": f"/country/{SLUG[c]}/"}
                          for c in present],
        }
        summary = summaries.get(cc) or fallback_summary(name, st)
        content = static_content(cc, name, st, summary, present)

        title = f"{name} AI Job Risk Map — which jobs are most exposed to AI"
        desc = (f"See how exposed {name}'s jobs are to generative AI: {st['total_jobs']:,} workers "
                f"across {st['total']} occupations, scored 0–10 using ILO and OpenAI research.")
        # Build-time first-screen chrome so crawlers / no-JS get real content instead
        # of the generic hardcoded H1, a "Loading..." subtitle and "—" placeholders.
        # JS re-sets the same values on load (applyCountryChrome/computeStats).
        r, g, b = exp_rgb(st["weighted_avg"])
        avg_html = f'<span style="color:rgb({r},{g},{b})">{st["weighted_avg"]:.1f}</span>'
        subtitle = (f"{st['total']} occupations &middot; area = employment &middot; color = AI exposure"
                    f"<br>{st['scored']} occupations scored")
        # Per-country PNG (shot separately by scripts/shoot_maps.mjs) doubles as the
        # og:image and a Dataset PNG distribution — only when it already exists on disk.
        has_png = os.path.exists(os.path.join(DIST, "static", "maps", map_filename(cc)))
        og_image = (f"{DOMAIN}/static/maps/{map_filename(cc)}" if has_png
                    else f"{DOMAIN}/og-image.png")
        jsonld = (ld_script(dataset_ld_country(cc, name, st, has_png))
                  + ld_script(breadcrumb_ld(cc, name)))
        page = (template
                .replace("__CONFIG__", json.dumps(cfg, ensure_ascii=False))
                .replace("__TITLE__", esc(title))
                .replace("__META_DESC__", esc(desc))
                .replace("__CANONICAL__", country_url(cc))
                .replace("__ROBOTS__", "index,follow")
                .replace("__BODYCLASS__", "")
                .replace("__SITE_NAME__", SITE_NAME)
                .replace("__OG_IMAGE__", og_image)
                .replace("__JSONLD__", jsonld)
                .replace("__ABOUT_URL__", "/methodology.html")
                .replace("__H1__", esc(f"AI Exposure of the {name} Job Market"))
                .replace("__SUBTITLE__", subtitle)
                .replace("__STAT_TOTALJOBS__", fmt_big_jobs(st["total_jobs"]))
                .replace("__STAT_AVGEXP__", avg_html)
                .replace("__NOSCRIPT__", build_noscript(name, st))
                .replace("__STATIC_CONTENT__", content)
                .replace("__FOOTER__", build_footer()))
        with open(os.path.join(cdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page)
        with open(os.path.join(cdir, "favicon.svg"), "w", encoding="utf-8") as f:
            f.write(FAVICON)

        # ── Bare embed page /embed/{slug} (iframe target; reuses this country's
        #    data.json, no sidebar/second-screen, noindex to avoid duplicate content) ──
        ecfg = {
            "cc": cc, "countryName": name, "currency": currency, "symbol": symbol,
            "sourceHtml": source, "dataUrl": f"/country/{slug}/data.json",
            "aboutUrl": "/methodology.html", "ver": VER, "embed": True, "countries": [],
        }
        epage = (template
                 .replace("__CONFIG__", json.dumps(ecfg, ensure_ascii=False))
                 .replace("__TITLE__", esc(f"AI Job Risk Map {name} {YEAR}"))
                 .replace("__META_DESC__", esc(f"Embeddable AI job risk map for {name}."))
                 .replace("__CANONICAL__", f"{DOMAIN}/embed/{slug}")
                 .replace("__ROBOTS__", "noindex,follow")
                 .replace("__BODYCLASS__", "embed")
                 .replace("__SITE_NAME__", SITE_NAME)
                 .replace("__OG_IMAGE__", og_image)
                 .replace("__JSONLD__", "")
                 .replace("__ABOUT_URL__", "/methodology.html")
                 .replace("__H1__", esc(f"AI Job Risk Map — {name}"))
                 .replace("__SUBTITLE__", "")
                 .replace("__STAT_TOTALJOBS__", fmt_big_jobs(st["total_jobs"]))
                 .replace("__STAT_AVGEXP__", avg_html)
                 .replace("__NOSCRIPT__", build_noscript(name, st))
                 .replace("__STATIC_CONTENT__", "")
                 .replace("__FOOTER__", ""))
        edir = os.path.join(DIST, "embed", slug)
        os.makedirs(edir, exist_ok=True)
        with open(os.path.join(edir, "index.html"), "w", encoding="utf-8") as f:
            f.write(epage)
        with open(os.path.join(edir, "favicon.svg"), "w", encoding="utf-8") as f:
            f.write(FAVICON)

        print(f"  {cc} -> /country/{slug}/ (+ /embed/{slug}): {len(rows)} occupations"
              + ("" if st["has_pay"] else " (no salary data — pay hidden)"))

    # ── Landing hub at root ───────────────────────────────────────
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_landing(present, stats_by_cc))
    with open(os.path.join(DIST, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON)

    # ── Methodology + About pages (distinct: how it's computed vs what it is) ──
    with open(os.path.join(DIST, "methodology.html"), "w", encoding="utf-8") as f:
        f.write(METHODOLOGY_HTML.replace("__DOMAIN__", DOMAIN).replace("__FOOTER__", build_footer()))
    with open(os.path.join(DIST, "about.html"), "w", encoding="utf-8") as f:
        f.write(build_about())
    print("  methodology.html, about.html written")

    # ── Embed / press-kit hub ─────────────────────────────────────
    os.makedirs(os.path.join(DIST, "embed"), exist_ok=True)
    with open(os.path.join(DIST, "embed", "index.html"), "w", encoding="utf-8") as f:
        f.write(build_embed_hub(present, stats_by_cc))
    with open(os.path.join(DIST, "embed", "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON)
    print("  embed/ hub written")

    # ── Dataset download ──────────────────────────────────────────
    write_dataset_csv(os.path.join(DIST, "dataset.csv"), rows_by_cc, present)
    print("  dataset.csv written")

    # ── SEO assets ────────────────────────────────────────────────
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(ROBOTS)
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap(present))
    with open(os.path.join(DIST, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(build_llms(present, stats_by_cc))
    build_og_image(os.path.join(DIST, "og-image.png"))
    print("  robots.txt, sitemap.xml, llms.txt written")

    print(f"\nBuilt landing + {len(present)} country sites -> {DIST}")
    print("Countries:", ", ".join(present))


if __name__ == "__main__":
    main()
