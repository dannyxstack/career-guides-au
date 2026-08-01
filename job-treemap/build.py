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
    "BR": ("Brazil", "BRL", "R$",
           "<strong>Data sources:</strong><br>IBGE PNAD Contínua microdata &mdash; ISCO-08 (COD) occupations"),
    "MX": ("Mexico", "MXN", "$",
           "<strong>Data sources:</strong><br>INEGI ENOE microdata &mdash; SINCO&rarr;ISCO-08 occupations"),
    "IN": ("India", "INR", "₹",
           "<strong>Data sources:</strong><br>MoSPI PLFS 2023-24 unit-level microdata &mdash; NCO-2015 (ISCO-08 aligned) occupations"),
    "CN": ("China", "CNY", "¥",
           "<strong>Data sources:</strong><br>National Bureau of Statistics &mdash; 2020 Census occupation employment &amp; post-category wages, CSCO&rarr;ISCO-08"),
    "NO": ("Norway", "NOK", "kr",
           "<strong>Data sources:</strong><br>Statistics Norway (SSB) &mdash; STYRK-08 (ISCO-08) occupations"),
    "SE": ("Sweden", "SEK", "kr",
           "<strong>Data sources:</strong><br>Statistics Sweden (SCB) &mdash; SSYK 2012&rarr;ISCO-08 occupations"),
    "FI": ("Finland", "EUR", "€",
           "<strong>Data sources:</strong><br>Statistics Finland &mdash; Classification of Occupations 2010 (ISCO-08) occupations"),
    "DK": ("Denmark", "DKK", "kr",
           "<strong>Data sources:</strong><br>Statistics Denmark &mdash; DISCO-08 (ISCO-08) occupations"),
    "IS": ("Iceland", "ISK", "kr",
           "<strong>Data sources:</strong><br>Statistics Iceland &mdash; ÍSTARF95 (ISCO-88)&rarr;ISCO-08 occupations"),
    "BE": ("Belgium", "EUR", "€",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "AT": ("Austria", "EUR", "€",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "PL": ("Poland", "PLN", "zł",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "PT": ("Portugal", "EUR", "€",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "GR": ("Greece", "EUR", "€",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "HU": ("Hungary", "HUF", "Ft",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "CZ": ("Czechia", "CZK", "Kč",
           "<strong>Data sources:</strong><br>ČSÚ (CZSO) &amp; Eurostat LFS — CZ-ISCO (ISCO-08)"),
    "RO": ("Romania", "RON", "lei",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "LU": ("Luxembourg", "EUR", "€",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "SK": ("Slovakia", "EUR", "€",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "SI": ("Slovenia", "EUR", "€",
           "<strong>Data sources:</strong><br>SURS &amp; Eurostat LFS — ISCO-08 (SKP-08)"),
    "HR": ("Croatia", "EUR", "€",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "TR": ("Turkey", "TRY", "₺",
           "<strong>Data sources:</strong><br>Eurostat LFS — ISCO-08 occupations"),
    "AR": ("Argentina", "ARS", "$",
           "<strong>Data sources:</strong><br>ILOSTAT (INDEC EPH) — ISCO-08 occupations"),
    "CL": ("Chile", "CLP", "$",
           "<strong>Data sources:</strong><br>ILOSTAT (INE ENE) — ISCO-08 occupations"),
    "MY": ("Malaysia", "MYR", "RM",
           "<strong>Data sources:</strong><br>ILOSTAT (DOSM LFS) — ISCO-08 occupations"),
    "ID": ("Indonesia", "IDR", "Rp",
           "<strong>Data sources:</strong><br>ILOSTAT (BPS Sakernas) — ISCO-08 occupations"),
    "TH": ("Thailand", "THB", "฿",
           "<strong>Data sources:</strong><br>ILOSTAT (NSO LFS) — ISCO-08 occupations"),
    "VN": ("Vietnam", "VND", "₫",
           "<strong>Data sources:</strong><br>ILOSTAT (GSO LFS) — ISCO-08 occupations"),
    "SG": ("Singapore", "SGD", "$",
           "<strong>Data sources:</strong><br>ILOSTAT / MOM — ISCO-08 occupations"),
    "CH": ("Switzerland", "CHF", "CHF ",
           "<strong>Data sources:</strong><br>Eurostat &amp; ILOSTAT — ISCO-08 occupations"),
    "EE": ("Estonia", "EUR", "€",
           "<strong>Data sources:</strong><br>Statistics Estonia PA633 — ISCO-08 occupations"),
    "LV": ("Latvia", "EUR", "€",
           "<strong>Data sources:</strong><br>CSB Latvia &amp; Eurostat SES — ISCO-08 occupations"),
    "LT": ("Lithuania", "EUR", "€",
           "<strong>Data sources:</strong><br>Statistics Lithuania &amp; Eurostat SES — LPK/ISCO-08 occupations"),
}
# Set of countries the site builds. Display order is derived alphabetically by
# English name at build time (see `present` below), not from this list's order.
# NOTE: keep NC (country count in the SEO copy below) in sync when adding/removing here.
ORDER = ["AU", "US", "UK", "CA", "NZ", "JP", "KR", "DE", "FR", "ES", "IT", "NL", "IE", "BR", "MX", "IN", "CN",
         "NO", "SE", "FI", "DK", "IS",
         "BE", "AT", "PL", "PT", "GR", "HU", "CZ", "RO", "LU", "SK", "SI", "HR", "TR", "AR", "CL", "MY", "ID", "TH", "VN", "SG",
         "CH", "EE", "LV", "LT"]

# Public site identity + per-country URL slug (lowercase full name).
DOMAIN = "https://aijobriskmap.com"
SITE_NAME = "AI Job Risk Map"
YEAR = datetime.now().year  # temporalCoverage + static-map filenames (…-2026.png)
DATASET_URL = f"{DOMAIN}/dataset.csv"
SLUG = {
    "AU": "australia", "US": "united-states", "UK": "united-kingdom",
    "CA": "canada", "NZ": "new-zealand", "JP": "japan", "KR": "south-korea",
    "DE": "germany", "FR": "france", "ES": "spain", "IT": "italy",
    "NL": "netherlands", "IE": "ireland", "BR": "brazil", "MX": "mexico",
    "IN": "india", "CN": "china", "NO": "norway", "SE": "sweden",
    "FI": "finland", "DK": "denmark", "IS": "iceland",
    "BE": "belgium", "AT": "austria", "PL": "poland", "PT": "portugal", "GR": "greece", "HU": "hungary", "CZ": "czechia", "RO": "romania", "LU": "luxembourg", "SK": "slovakia", "SI": "slovenia", "HR": "croatia", "TR": "turkey", "AR": "argentina", "CL": "chile", "MY": "malaysia", "ID": "indonesia", "TH": "thailand", "VN": "vietnam", "SG": "singapore",
    "CH": "switzerland", "EE": "estonia", "LV": "latvia", "LT": "lithuania",
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
    "BR": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#009B3A"/><path d="M60,6 L114,30 L60,54 L6,30 Z" fill="#FEDF00"/><circle cx="60" cy="30" r="13" fill="#002776"/></svg>',
    "MX": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="40" height="60" fill="#006847"/><rect x="40" width="40" height="60" fill="#fff"/><rect x="80" width="40" height="60" fill="#CE1126"/></svg>',
    "IN": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="20" fill="#FF9933"/><rect y="20" width="120" height="20" fill="#fff"/><rect y="40" width="120" height="20" fill="#138808"/><circle cx="60" cy="30" r="8" fill="none" stroke="#000080" stroke-width="1.4"/><circle cx="60" cy="30" r="1.6" fill="#000080"/></svg>',
    "CN": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#DE2910"/><polygon points="18,8 19.6,12.9 24.6,12.9 20.5,15.9 22.1,20.8 18,17.8 13.9,20.8 15.5,15.9 11.4,12.9 16.4,12.9" fill="#FFDE00"/><circle cx="30" cy="6" r="1.7" fill="#FFDE00"/><circle cx="36" cy="11" r="1.7" fill="#FFDE00"/><circle cx="36" cy="18" r="1.7" fill="#FFDE00"/><circle cx="30" cy="23" r="1.7" fill="#FFDE00"/></svg>',
    "NO": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#EF2B2D"/><rect x="36" width="12" height="60" fill="#fff"/><rect y="24" width="120" height="12" fill="#fff"/><rect x="39" width="6" height="60" fill="#002868"/><rect y="27" width="120" height="6" fill="#002868"/></svg>',
    "SE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#006AA7"/><rect x="36" width="12" height="60" fill="#FECC00"/><rect y="24" width="120" height="12" fill="#FECC00"/></svg>',
    "FI": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#fff"/><rect x="36" width="12" height="60" fill="#003580"/><rect y="24" width="120" height="12" fill="#003580"/></svg>',
    "DK": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#C8102E"/><rect x="36" width="12" height="60" fill="#fff"/><rect y="24" width="120" height="12" fill="#fff"/></svg>',
    "IS": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#02529C"/><rect x="36" width="12" height="60" fill="#fff"/><rect y="24" width="120" height="12" fill="#fff"/><rect x="39" width="6" height="60" fill="#DC1E35"/><rect y="27" width="120" height="6" fill="#DC1E35"/></svg>',
    "BE": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"40\" height=\"60\" fill=\"#000\"/><rect x=\"40\" width=\"40\" height=\"60\" fill=\"#FAE042\"/><rect x=\"80\" width=\"40\" height=\"60\" fill=\"#ED2939\"/></svg>",
    "AT": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#ED2939\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#fff\"/></svg>",
    "PL": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#fff\"/><rect y=\"30\" width=\"120\" height=\"30\" fill=\"#DC143C\"/></svg>",
    "PT": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#FF0000\"/><rect width=\"48\" height=\"60\" fill=\"#006600\"/><circle cx=\"48\" cy=\"30\" r=\"9\" fill=\"#FFCC00\" stroke=\"#fff\" stroke-width=\"1\"/></svg>",
    "GR": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#0D5EAF\"/><rect y=\"6\" width=\"120\" height=\"6.66\" fill=\"#fff\"/><rect y=\"19\" width=\"120\" height=\"6.66\" fill=\"#fff\"/><rect y=\"33\" width=\"120\" height=\"6.66\" fill=\"#fff\"/><rect y=\"46\" width=\"120\" height=\"6.66\" fill=\"#fff\"/><rect width=\"26.6\" height=\"33.3\" fill=\"#0D5EAF\"/><rect x=\"10\" width=\"6.6\" height=\"33.3\" fill=\"#fff\"/><rect y=\"13.3\" width=\"26.6\" height=\"6.6\" fill=\"#fff\"/></svg>",
    "HU": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#CD2A3E\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#fff\"/><rect y=\"40\" width=\"120\" height=\"20\" fill=\"#436F4D\"/></svg>",
    "CZ": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"30\" fill=\"#fff\"/><rect y=\"30\" width=\"120\" height=\"30\" fill=\"#D7141A\"/><path d=\"M0,0 L60,30 L0,60 Z\" fill=\"#11457E\"/></svg>",
    "RO": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"40\" height=\"60\" fill=\"#002B7F\"/><rect x=\"40\" width=\"40\" height=\"60\" fill=\"#FCD116\"/><rect x=\"80\" width=\"40\" height=\"60\" fill=\"#CE1126\"/></svg>",
    "LU": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#ED2939\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#fff\"/><rect y=\"40\" width=\"120\" height=\"20\" fill=\"#00A1DE\"/></svg>",
    "SK": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"20\" fill=\"#fff\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#0B4EA2\"/><rect y=\"40\" width=\"120\" height=\"20\" fill=\"#EE1C25\"/><path d=\"M18,14 h16 v20 q0,10 -8,14 q-8,-4 -8,-14 Z\" fill=\"#EE1C25\" stroke=\"#fff\" stroke-width=\"2\"/><rect x=\"24\" y=\"18\" width=\"4\" height=\"20\" fill=\"#fff\"/><rect x=\"20\" y=\"24\" width=\"12\" height=\"4\" fill=\"#fff\"/></svg>",
    "SI": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"20\" fill=\"#fff\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#005DA4\"/><rect y=\"40\" width=\"120\" height=\"20\" fill=\"#ED1C24\"/><path d=\"M14,30 q6,-14 12,0 q6,14 -12,20 q-18,-6 -6,-20 Z\" fill=\"#005DA4\" stroke=\"#fff\" stroke-width=\"1.2\"/></svg>",
    "HR": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"20\" fill=\"#FF0000\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#fff\"/><rect y=\"40\" width=\"120\" height=\"20\" fill=\"#171796\"/><g><rect x=\"52.0\" y=\"22.0\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/><rect x=\"55.2\" y=\"22.0\" width=\"3.2\" height=\"3.2\" fill=\"#fff\"/><rect x=\"58.4\" y=\"22.0\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/><rect x=\"61.6\" y=\"22.0\" width=\"3.2\" height=\"3.2\" fill=\"#fff\"/><rect x=\"64.8\" y=\"22.0\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/><rect x=\"52.0\" y=\"25.2\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/><rect x=\"55.2\" y=\"25.2\" width=\"3.2\" height=\"3.2\" fill=\"#fff\"/><rect x=\"58.4\" y=\"25.2\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/><rect x=\"61.6\" y=\"25.2\" width=\"3.2\" height=\"3.2\" fill=\"#fff\"/><rect x=\"64.8\" y=\"25.2\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/><rect x=\"52.0\" y=\"28.4\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/><rect x=\"55.2\" y=\"28.4\" width=\"3.2\" height=\"3.2\" fill=\"#fff\"/><rect x=\"58.4\" y=\"28.4\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/><rect x=\"61.6\" y=\"28.4\" width=\"3.2\" height=\"3.2\" fill=\"#fff\"/><rect x=\"64.8\" y=\"28.4\" width=\"3.2\" height=\"3.2\" fill=\"#FF0000\"/></g></svg>",
    "TR": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#E30A17\"/><circle cx=\"48\" cy=\"30\" r=\"15\" fill=\"#fff\"/><circle cx=\"53\" cy=\"30\" r=\"12\" fill=\"#E30A17\"/><polygon points=\"66,30 74,27 69,33 69,27 74,33\" fill=\"#fff\"/></svg>",
    "AR": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#74ACDF\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#fff\"/><circle cx=\"60\" cy=\"30\" r=\"6\" fill=\"#F6B40E\" stroke=\"#85340A\" stroke-width=\"0.8\"/></svg>",
    "CL": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#fff\"/><rect y=\"30\" width=\"120\" height=\"30\" fill=\"#D52B1E\"/><rect width=\"40\" height=\"30\" fill=\"#0039A6\"/><polygon points=\"20,8 22.4,15.2 30,15.2 23.8,19.8 26.2,27 20,22.4 13.8,27 16.2,19.8 10,15.2 17.6,15.2\" fill=\"#fff\"/></svg>",
    "MY": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#fff\"/><rect y=\"0\" width=\"120\" height=\"4.3\" fill=\"#CC0001\"/><rect y=\"8\" width=\"120\" height=\"4.3\" fill=\"#CC0001\"/><rect y=\"17\" width=\"120\" height=\"4.3\" fill=\"#CC0001\"/><rect y=\"25\" width=\"120\" height=\"4.3\" fill=\"#CC0001\"/><rect y=\"34\" width=\"120\" height=\"4.3\" fill=\"#CC0001\"/><rect y=\"42\" width=\"120\" height=\"4.3\" fill=\"#CC0001\"/><rect y=\"51\" width=\"120\" height=\"4.3\" fill=\"#CC0001\"/><rect width=\"60\" height=\"34.3\" fill=\"#010066\"/><circle cx=\"24\" cy=\"17\" r=\"9\" fill=\"#FFCC00\"/><circle cx=\"28\" cy=\"17\" r=\"7.5\" fill=\"#010066\"/><polygon points=\"37,17 41,12 40,18 45,20 40,22 41,28 37,23\" fill=\"#FFCC00\"/></svg>",
    "ID": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#FF0000\"/><rect y=\"30\" width=\"120\" height=\"30\" fill=\"#fff\"/></svg>",
    "TH": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#A51931\"/><rect y=\"10\" width=\"120\" height=\"40\" fill=\"#fff\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#2D2A4A\"/></svg>",
    "VN": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#DA251D\"/><polygon points=\"60,14 64.7,28.6 80,28.6 67.6,37.6 72.4,52.2 60,43.2 47.6,52.2 52.4,37.6 40,28.6 55.3,28.6\" fill=\"#FFFF00\"/></svg>",
    "SG": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#EF3340\"/><rect y=\"30\" width=\"120\" height=\"30\" fill=\"#fff\"/><circle cx=\"30\" cy=\"15\" r=\"11\" fill=\"#fff\"/><circle cx=\"35\" cy=\"15\" r=\"9\" fill=\"#EF3340\"/><g fill=\"#fff\"><circle cx=\"42\" cy=\"9\" r=\"1.6\"/><circle cx=\"47\" cy=\"9\" r=\"1.6\"/><circle cx=\"52\" cy=\"9\" r=\"1.6\"/><circle cx=\"42\" cy=\"16\" r=\"1.6\"/><circle cx=\"47\" cy=\"16\" r=\"1.6\"/></g></svg>",
    "CH": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#DA291C\"/><rect x=\"53\" y=\"15\" width=\"14\" height=\"30\" fill=\"#fff\"/><rect x=\"45\" y=\"23\" width=\"30\" height=\"14\" fill=\"#fff\"/></svg>",
    "EE": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"20\" fill=\"#0072CE\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#000\"/><rect y=\"40\" width=\"120\" height=\"20\" fill=\"#fff\"/></svg>",
    "LV": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"60\" fill=\"#9E3039\"/><rect y=\"24\" width=\"120\" height=\"12\" fill=\"#fff\"/></svg>",
    "LT": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 60\"><rect width=\"120\" height=\"20\" fill=\"#FDB913\"/><rect y=\"20\" width=\"120\" height=\"20\" fill=\"#006A44\"/><rect y=\"40\" width=\"120\" height=\"20\" fill=\"#C1272D\"/></svg>",
}

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
           '<rect width="32" height="32" rx="6" fill="#0a0a0f"/>'
           '<rect x="4" y="4" width="13" height="24" rx="1.5" fill="#e6961e"/>'
           '<rect x="19" y="4" width="9" height="11" rx="1.5" fill="#32a032"/>'
           '<rect x="19" y="17" width="9" height="11" rx="1.5" fill="#ff5014"/>'
           '</svg>')


# ── Per-country data source & authority registry ─────────────────
# Single source of truth for the "data sources & authority" copy shown on every
# country page and in the full sources table on the methodology page. Each country
# has a distinct provenance, so each description differs.
#   auth  – the national statistical authority (+ secondary agency) behind the data.
#   cls   – the occupation classification the country's data is expressed in.
#   tier  – authority level of the employment counts:
#             "A" national official statistics (own survey/register/census),
#             "B" via Eurostat's harmonised EU Labour Force Survey,
#             "C" via ILOSTAT (UN ILO harmonised database).
#   pay   – True when official occupation-level pay is available; False when the
#           source does not publish pay at occupation level (left blank, not estimated).
SOURCE_INFO = {
    "AU": ("Jobs and Skills Australia &amp; the Australian Bureau of Statistics (ABS)", "ANZSCO", "A", True),
    "US": ("the U.S. Bureau of Labor Statistics (BLS) Occupational Employment &amp; Wage Statistics and O*NET", "SOC", "A", True),
    "CA": ("Statistics Canada &amp; Job Bank (Employment and Social Development Canada)", "NOC", "A", True),
    "UK": ("the UK Office for National Statistics (ONS)", "SOC", "A", True),
    "NZ": ("Stats NZ &amp; the Ministry of Business, Innovation and Employment (MBIE)", "ANZSCO", "A", True),
    "DE": ("the Federal Statistical Office (Destatis) &amp; the Federal Employment Agency (Bundesagentur für Arbeit)", "KldB / ISCO-08", "A", True),
    "ES": ("the National Statistics Institute (INE) &amp; the Public Employment Service (SEPE)", "CNO / ISCO-08", "A", True),
    "FR": ("the National Institute of Statistics and Economic Studies (INSEE) &amp; France Travail", "ROME / PCS → ISCO-08", "A", True),
    "IE": ("the Central Statistics Office (CSO Ireland)", "ISCO-08", "A", True),
    "IT": ("the National Institute of Statistics (ISTAT)", "ISCO-08 (CP)", "A", True),
    "NL": ("Statistics Netherlands (CBS)", "ISCO-08 (BRC)", "A", True),
    "JP": ("the Statistics Bureau of Japan &amp; the Ministry of Health, Labour and Welfare (Basic Survey on Wage Structure)", "JSCO → ISCO-08", "A", True),
    "KR": ("the Korea Employment Information Service (KEIS) WorkNet/KNOW &amp; Statistics Korea", "KECO → ISCO-08", "A", True),
    "BR": ("the Brazilian Institute of Geography and Statistics (IBGE), PNAD Contínua microdata", "CBO → ISCO-08", "A", True),
    "MX": ("the National Institute of Statistics and Geography (INEGI), ENOE microdata", "SINCO → ISCO-08", "A", True),
    "IN": ("the Ministry of Statistics (MoSPI) Periodic Labour Force Survey 2023-24 unit-level microdata", "NCO-2015 (ISCO-08 aligned)", "A", True),
    "CN": ("the National Bureau of Statistics of China, 2020 Population Census", "CSCO → ISCO-08", "A", True),
    "NO": ("Statistics Norway (SSB)", "STYRK-08 (ISCO-08)", "A", True),
    "SE": ("Statistics Sweden (SCB)", "SSYK 2012 → ISCO-08", "A", True),
    "FI": ("Statistics Finland", "Classification of Occupations 2010 (ISCO-08)", "A", True),
    "DK": ("Statistics Denmark", "DISCO-08 (ISCO-08)", "A", True),
    "IS": ("Statistics Iceland", "ÍSTARF95 (ISCO-88) → ISCO-08", "A", True),
    "CZ": ("the Czech Statistical Office (ČSÚ) &amp; the ISPV Regional Wage Survey", "CZ-ISCO (ISCO-08)", "A", True),
    "HU": ("the Hungarian Central Statistical Office (KSH)", "HSCO'08 (ISCO-08 aligned)", "A", True),
    "SG": ("the Ministry of Manpower (MOM) Occupational Wage Survey &amp; the Department of Statistics", "SSOC 2024 (ISCO-08 based)", "A", True),
    "BE": ("Statistics Belgium (Statbel)", "ISCO-08", "B", False),
    "AT": ("Statistics Austria (Statistik Austria)", "ISCO-08", "B", False),
    "PL": ("Statistics Poland (GUS)", "ISCO-08", "B", False),
    "PT": ("Statistics Portugal (INE)", "ISCO-08", "B", False),
    "GR": ("the Hellenic Statistical Authority (ELSTAT)", "ISCO-08", "B", False),
    "RO": ("the National Institute of Statistics (INS)", "ISCO-08", "B", False),
    "LU": ("the National Institute of Statistics and Economic Studies (STATEC)", "ISCO-08", "B", False),
    "SK": ("the Statistical Office of the Slovak Republic (ŠÚSR)", "ISCO-08 (SK ISCO-08)", "B", False),
    "SI": ("the Statistical Office of the Republic of Slovenia (SURS)", "ISCO-08 (SKP-08)", "B", False),
    "HR": ("the Croatian Bureau of Statistics (DZS)", "ISCO-08", "B", False),
    "TR": ("the Turkish Statistical Institute (TÜİK)", "ISCO-08", "B", False),
    "AR": ("Argentina's INDEC (Permanent Household Survey, EPH)", "ISCO-08", "C", False),
    "CL": ("Chile's National Statistics Institute (INE), National Employment Survey (ENE)", "ISCO-08", "C", False),
    "MY": ("Malaysia's Department of Statistics (DOSM) Labour Force Survey", "ISCO-08", "C", False),
    "ID": ("BPS-Statistics Indonesia (Sakernas)", "ISCO-08", "C", False),
    "TH": ("Thailand's National Statistical Office (NSO) Labour Force Survey", "ISCO-08", "C", False),
    "VN": ("Vietnam's General Statistics Office (GSO) Labour Force Survey", "ISCO-08", "C", False),
    "CH": ("the Swiss Federal Statistical Office (FSO)", "ISCO-08", "B", False),
    "EE": ("Statistics Estonia (Statistikaamet), PA633 occupational earnings", "ISCO-08", "A", True),
    "LV": ("the Central Statistical Bureau of Latvia (CSB) &amp; Eurostat SES", "ISCO-08", "B", False),
    "LT": ("Statistics Lithuania (State Data Agency) &amp; Eurostat SES", "LPK 2023 (ISCO-08)", "B", False),
}

# AI-mapped (model-assisted ISCO placement) exposure scoring — clearly identified.
LLM_MAPPED = {"FR", "JP", "KR"}

TIER_LABEL = {"A": "National statistics", "B": "Eurostat EU-LFS", "C": "ILOSTAT (UN ILO)"}


def employment_basis(cc):
    """One phrase describing where the tile-area (employment) figures come from."""
    tier = SOURCE_INFO[cc][2]
    if tier == "A":
        return "official national statistics"
    if tier == "B":
        return "the EU Labour Force Survey (Eurostat)"
    return "ILOSTAT (UN ILO harmonised data)"


def source_paragraph(cc, name):
    """Per-country 'data sources & authority' prose for the country-page body."""
    auth, cls, tier, pay = SOURCE_INFO[cc]
    parts = [
        f"<strong>Employment (tile area)</strong> for {esc(name)} comes from {auth}, "
        f"classified in {cls}."]
    if tier == "A":
        parts.append(
            " These are official national statistics &mdash; the highest-authority source "
            "for the country&rsquo;s labour market.")
    elif tier == "B":
        parts.append(
            " Counts are drawn from the harmonised EU Labour Force Survey published by Eurostat "
            "(the European Union&rsquo;s official statistical authority); occupation detail is "
            "modelled from published major-group shares.")
    else:
        parts.append(
            " Counts are drawn from ILOSTAT, the UN International Labour Organization&rsquo;s "
            "harmonised database; occupation detail is modelled to 4-digit ISCO-08.")
    if pay:
        parts.append(
            " <strong>Pay</strong> is official occupation-level earnings from the same source, "
            "shown where the source publishes it.")
    else:
        parts.append(
            " <strong>Pay</strong> is not published at occupation level for this source, so salary "
            "is left blank rather than estimated.")
    if cc in LLM_MAPPED:
        parts.append(
            f" No clean official crosswalk from {esc(name)}&rsquo;s national classification to ISCO-08 "
            "was obtainable, so occupations are placed onto the ISCO-08 structure by a clearly "
            "identified model-assisted mapping for the exposure score only.")
    parts.append(
        " The <strong>AI-exposure score</strong> itself is identical in method for every country: "
        "the ILO Working Paper 140 index and OpenAI&rsquo;s <em>GPTs are GPTs</em> study, ranked on a "
        "single global percentile scale.")
    return "".join(parts)


def sidebar_source_html(cc):
    """Compact sidebar note (replaces the old static COUNTRY_META source line)."""
    auth, cls, tier, pay = SOURCE_INFO[cc]
    via = {"A": "", "B": " (via Eurostat EU-LFS)", "C": " (via ILOSTAT)"}[tier]
    pay_note = "" if pay else "<br><span style='opacity:.75'>Occupation-level pay not published &mdash; salary blank.</span>"
    return (f"<strong>Data sources:</strong><br>{auth}{via}<br>"
            f"<span style='opacity:.85'>{cls} occupations</span>{pay_note}")


def methodology_sources_section(present):
    """Full data-sources & authority table across all countries, for methodology.html."""
    order = sorted(present, key=lambda c: COUNTRY_META[c][0])
    rows = []
    for cc in order:
        auth, cls, tier, pay = SOURCE_INFO[cc]
        tag = {"A": "tag-a", "B": "tag-b", "C": "tag-c"}[tier]
        paycell = "Official" if pay else "&mdash;"
        rows.append(
            f"<tr><td>{esc(COUNTRY_META[cc][0])}</td>"
            f"<td>{auth}</td><td>{esc(cls)}</td>"
            f"<td><span class='tag {tag}'>{TIER_LABEL[tier]}</span></td>"
            f"<td>{paycell}</td></tr>")
    table = ("<table><thead><tr><th>Country</th><th>Statistical authority</th>"
             "<th>Classification</th><th>Employment basis</th><th>Occupation pay</th></tr></thead>"
             f"<tbody>{''.join(rows)}</tbody></table>")
    return f"""<h2>Data sources &amp; authority by country</h2>
<p>Tile <em>area</em> is the size of each occupation&rsquo;s workforce; tile <em>colour</em> is the AI-exposure
score. The exposure score is computed identically for every country (see above). The employment counts &mdash;
and, where available, occupation-level pay &mdash; come from each country&rsquo;s own authority, so provenance
differs country by country:</p>
<ul>
<li><span class="tag tag-a">National statistics</span> &mdash; official figures from the national statistical
office (own survey, register or census). Highest authority; occupation-level pay is generally published.</li>
<li><span class="tag tag-b">Eurostat EU-LFS</span> &mdash; the European Union&rsquo;s harmonised Labour Force
Survey (national data collected by each member state&rsquo;s statistics office). Occupation detail is modelled
from published major-group shares; occupation-level pay is not published, so salary is left blank.</li>
<li><span class="tag tag-c">ILOSTAT (UN ILO)</span> &mdash; the International Labour Organization&rsquo;s
harmonised database (national data collected by each country&rsquo;s statistics office). Occupation detail is
modelled to 4-digit ISCO-08; occupation-level pay is not published, so salary is left blank.</li>
</ul>
{table}
<p>Occupations in {esc(', '.join(COUNTRY_META[c][0] for c in order if c in LLM_MAPPED))} are placed onto the
ISCO-08 structure by a clearly identified model-assisted mapping (tagged <code>_llmmap</code>) for the exposure
score, pending an official crosswalk. Salary and workforce figures blend official data with estimates where a
source is incomplete; treat everything as indicative, not advice.</p>"""


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

__SOURCES_SECTION__

<h2>Download the data</h2>
<p>The full scored dataset &mdash; every occupation in all 46 countries, with its AI-exposure score
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


def median_salary(o):
    """官方"Median salary"档年薪（无则 None，不回退到均值，供薪资配色用）。"""
    for s in o.get("salaries") or []:
        if "median" in (s.get("label") or "").lower():
            return to_int(s.get("min"))
    return None


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
        "median": median_salary(o),
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


# 薪资配色（USD 阈值，高薪→绿）。与气泡 JS 的 salColor 同口径，供图例色块与气泡一致着色。
SAL_LO, SAL_HI = 8000, 80000


def sal_rgb(usd):
    t = max(0.0, min(1.0, (usd - SAL_LO) / (SAL_HI - SAL_LO)))
    return exp_rgb(10 * (1 - t))


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
    meds = sorted(r["median"] for r in rows if r.get("median") is not None)
    median_local = meds[len(meds) // 2] if meds else None
    return {
        "total_jobs": total_jobs, "scored": len(scored), "total": len(rows),
        "weighted_avg": (wsum / wcnt) if wcnt else 0.0,
        "median_local": median_local,
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


def country_faqs(name, st):
    """Deterministic Q&A for one country. Every figure comes from `st` (no invented
    numbers), so the same list can be rendered visibly and emitted as FAQPage schema.
    Returns a list of (question, plain-text answer)."""
    avg = st["weighted_avg"]
    band = ("low" if avg < 3 else "moderate" if avg < 5
            else "elevated" if avg < 6.5 else "high")
    band_art = "an" if band[0] in "aeiou" else "a"
    top5 = ", ".join(r["title"] for r in st["top"][:5])
    bot3 = ", ".join(r["title"] for r in st["bottom"][:3])
    top_inds = ", ".join(i["name"] for i in st["industries"][:3] if i["avg"] is not None)
    faqs = [
        (f"How much AI risk do jobs in {name} face?",
         f"Across {st['total']:,} occupations covering about {st['total_jobs']:,} workers, "
         f"{name} has an employment-weighted average generative-AI exposure of {avg:.1f} on a "
         f"0–10 scale — {band_art} {band} level. A higher score means a larger share of a role's "
         f"day-to-day tasks can already be performed or assisted by AI."),
        (f"Which jobs in {name} are most at risk from AI?",
         f"The most exposed occupations in {name} are {top5}. These are roles built around routine "
         f"information work — writing, data handling and analysis — that large language "
         f"models already handle well."),
        (f"Which jobs in {name} are least exposed to AI?",
         f"The least exposed occupations include {bot3}. Physical, hands-on and in-person tasks are "
         f"much harder for current AI to automate, so these roles score low."),
        ("Does a high AI exposure score mean the job will be lost?",
         "No. Exposure measures how much of a role's tasks AI can perform or assist with — not "
         "whether the job will disappear. A high score flags where AI is most likely to reshape tasks "
         "first, and where workers may benefit from building complementary skills."),
    ]
    if top_inds:
        faqs.append(
            (f"Which industries in {name} are most exposed to AI?",
             f"By employment-weighted average exposure, the most exposed industries in {name} are "
             f"{top_inds}."))
    faqs.append(
        ("How is the AI exposure score calculated?",
         f"Every occupation is scored 0–10 by combining two published research datasets — "
         f"the ILO's Working Paper 140 index and OpenAI's ‘GPTs are GPTs’ task-exposure "
         f"study — mapped onto {name}'s official occupation classification and ranked on a single "
         f"global percentile scale so scores stay comparable between countries."))
    return faqs


def faq_accordion(faqs):
    """Visible, crawlable FAQ block (native <details>, collapsed by default). Text
    matches country_faqs so it stays identical to the FAQPage schema."""
    items = "".join(
        f'<details class="faq-item"><summary>{esc(q)}</summary>'
        f'<div class="faq-a"><p>{esc(a)}</p></div></details>'
        for q, a in faqs)
    return (f'<h2 id="faq">Frequently asked questions</h2>\n'
            f'<div class="faq">{items}</div>')


def static_content(cc, name, st, summary_html, present, faqs):
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
    return f"""<h2>AI job risk in {esc(name)}</h2>
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

{faq_accordion(faqs)}

<h3>Data sources &amp; authority for {esc(name)}</h3>
<p>{source_paragraph(cc, name)} <a href="/methodology.html">Full methodology &amp; all-country data sources &rarr;</a></p>

{map_dl}
"""


# ── Landing hub + SEO assets ─────────────────────────────────────

# 货币→USD 近似汇率（2025 年中，静态值；仅用于气泡图跨国薪资排序着色，非精确换算）。
FX_USD = {
    "USD": 1.0, "AUD": 0.66, "CAD": 0.73, "GBP": 1.27, "NZD": 0.60, "EUR": 1.08,
    "JPY": 0.0067, "KRW": 0.00073, "BRL": 0.18, "MXN": 0.055, "INR": 0.012,
    "CNY": 0.138, "NOK": 0.093, "SEK": 0.095, "DKK": 0.145, "ISK": 0.0072,
    "PLN": 0.25, "HUF": 0.0027, "CZK": 0.043, "RON": 0.22, "TRY": 0.030,
    "ARS": 0.0011, "CLP": 0.00105, "MYR": 0.21, "IDR": 0.0000615, "THB": 0.028,
    "VND": 0.0000395, "SGD": 0.74, "CHF": 1.12,
}


# 各国平均年薪（USD）。口径：优先国家中位数——但中位数各国不可比/多缺，故按需求统一改用
# 平均薪资。OECD 成员用官方 Average Annual Wage（PPP，2023，OECD.Stat）；非 OECD 用国家统计/
# 调查平均年薪的近似值（市场汇率折 USD）；个别缺失者由人均 GDP 推算。仅用于气泡上半的跨国相对着色。
NATIONAL_WAGE_USD = {
    # —— OECD Average Annual Wage (PPP USD, 2023, OECD.Stat) ——
    "AU": 67101, "AT": 71167, "BE": 73206, "CA": 66211, "CL": 31000, "CZ": 37366,
    "DK": 69525, "EE": 37404, "FI": 57860, "FR": 59087, "DE": 65719, "GR": 30238,
    "HU": 31709, "IS": 87421, "IE": 56809, "IT": 48874, "JP": 46792, "KR": 49062,
    "LV": 38740, "LT": 48864, "LU": 89767, "MX": 20474, "NL": 70185, "NZ": 58097,
    "NO": 71972, "PL": 41050, "PT": 37500, "SK": 31733, "SI": 55660, "ES": 51336,
    "SE": 57996, "CH": 83332, "TR": 37000, "UK": 57617, "US": 80115,
    # —— 非 OECD：国家统计/调查平均年薪近似（市场汇率 USD）——
    "CN": 15000, "IN": 6000, "BR": 8300, "AR": 12000, "RO": 22000, "HR": 23000,
    "SG": 50000, "MY": 10500, "ID": 3500, "TH": 6000, "VN": 5000,
}


def median_usd(cc, st):
    """该国薪资中位数换算为 USD（无薪资数据则 None）。"""
    m = st.get("median_local")
    if m is None:
        return None
    return round(m * FX_USD.get(COUNTRY_META[cc][1], 0))


def build_landing(present, stats_by_cc):
    sections = load_longform()
    longform_html = ""
    if sections:
        blocks = "".join(
            f'<section class="lf"><h2>{esc(s.get("h2", ""))}</h2>'
            f'<div class="lf-body">{s.get("html", "")}</div>'
            f'<button type="button" class="lf-toggle">Read more</button></section>'
            for s in sections)
        longform_html = f'<div class="longform">{blocks}</div>'
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
    bubbles = [{
        "cc": cc, "name": COUNTRY_META[cc][0], "slug": SLUG[cc], "flag": FLAG.get(cc, ""),
        "workers": stats_by_cc[cc]["total_jobs"], "exp": round(stats_by_cc[cc]["weighted_avg"], 1),
        "usd": NATIONAL_WAGE_USD.get(cc), "medianUsd": median_usd(cc, stats_by_cc[cc]),
    } for cc in present]
    bubble_json = json.dumps(bubbles, ensure_ascii=False, separators=(",", ":"))
    # 图例分段色块：不同颜色对应不同取值范围（薪资按 USD 档，风险按 0-10 档）
    def _chip(rgb3, label):
        return f'<span class="dl-chip"><i style="background:rgb{rgb3}"></i>{label}</span>'
    pay_chips = "".join(_chip(sal_rgb(u), lab) for lab, u in
                        [("&lt; $15k", 12000), ("$15–30k", 22000), ("$30–50k", 40000),
                         ("$50–70k", 60000), ("&gt; $70k", 78000)])
    risk_chips = "".join(_chip(exp_rgb(s), lab) for lab, s in
                         [("0–1 minimal", 0.5), ("2–3 low", 2.5), ("4–5 moderate", 4.5),
                          ("6–7 high", 6.5), ("8–10 very high", 9)])
    title = "AI Job Risk Map — how exposed is every job to AI, across 46 countries"
    desc = ("An interactive map of how exposed jobs are to generative AI in 46 countries. "
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
.lead{{color:var(--fg2);font-size:17px;max-width:960px;margin:0 0 34px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px}}
.cc-card{{display:flex;flex-direction:column;gap:5px;padding:16px 18px;border:1px solid var(--line);border-radius:12px;background:var(--bg2);text-decoration:none;color:var(--fg);transition:border-color .15s,transform .15s}}
.cc-card:hover{{border-color:rgba(255,255,255,.28);transform:translateY(-2px)}}
.cc-head{{display:flex;align-items:center;gap:9px}}
.cc-flag svg{{width:26px;height:auto;display:block;border-radius:3px;box-shadow:0 0 0 1px rgba(255,255,255,.14)}}
.cc-name{{font-size:17px;font-weight:600}}
.cc-meta{{font-size:12.5px;color:var(--fg2)}}
.cc-exp{{font-size:13px;margin-top:2px}}
.cc-scale{{color:var(--fg2)}}
.longform{{max-width:760px;margin:56px auto 0}}
.lf{{margin:0 0 26px;padding-bottom:22px;border-bottom:1px solid var(--line)}}
.lf:last-child{{border-bottom:none}}
.lf h2{{font-size:22px;line-height:1.25;letter-spacing:-.01em;margin:0 0 12px}}
/* Long-form copy: only the first ~2 lines show; the rest stays in the DOM
   (crawlable) but is clipped and faded until the reader clicks Read more. */
.lf-body{{position:relative;max-height:3.2em;overflow:hidden}}
.lf-body::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:2em;background:linear-gradient(rgba(10,10,15,0),#0a0a0f);pointer-events:none}}
.lf.open .lf-body{{max-height:none}}
.lf.open .lf-body::after{{display:none}}
.lf-body p{{color:var(--fg2);margin:0 0 15px}}
.lf-body p:last-child{{margin-bottom:0}}
.lf-toggle{{margin-top:12px;background:none;border:none;color:var(--accent);font:inherit;font-size:14px;font-weight:600;cursor:pointer;padding:0}}
.lf-toggle:hover{{text-decoration:underline}}
.tabs{{display:flex;gap:8px;margin:0 0 20px}}
.tab-btn{{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:8px 16px;color:var(--fg2);font:inherit;font-size:14px;font-weight:600;cursor:pointer}}
.tab-btn:hover{{color:var(--fg)}}
.tab-btn.active{{background:var(--accent);color:#0a0a0f;border-color:var(--accent)}}
.tab-panel{{display:none}}
.tab-panel.active{{display:block}}
.bubble-legend{{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:12px;color:var(--fg2);margin:0 0 22px}}
.bubble-legend .lg{{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:middle}}
.bubble-legend .lg-sal{{background:linear-gradient(90deg,#e63c14,#32a032)}}
.bubble-legend .lg-exp{{background:linear-gradient(90deg,#32a032,#e63c14)}}
#bubbleChart{{position:relative;width:100%;margin:0 auto}}
.bubble{{position:absolute;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;box-shadow:inset 0 0 0 1px rgba(255,255,255,.14),0 2px 8px rgba(0,0,0,.3);transition:transform .12s}}
.bubble:hover{{transform:scale(1.06);z-index:5;box-shadow:inset 0 0 0 1px rgba(255,255,255,.3),0 4px 16px rgba(0,0,0,.5)}}
.bubble .bflag{{width:46%;line-height:0;opacity:.96}}
.bubble .bflag svg{{width:100%;height:auto;border-radius:2px;box-shadow:0 0 0 1px rgba(0,0,0,.25)}}
/* 宽屏时气泡群宽度取正文(.wrap)内容区的 90%，居中；窄屏/手机保持满宽不变 */
@media(min-width:1100px){{#bubbleChart{{width:90%}}}}
.dual-legend{{display:flex;align-items:center;justify-content:center;gap:16px;margin:30px auto 4px;flex-wrap:wrap;max-width:660px}}
.dl-side{{flex:1;min-width:150px}}
.dl-left{{text-align:right}}
.dl-right{{text-align:left}}
.dl-title{{font-size:12.5px;color:var(--fg);font-weight:600;margin-bottom:5px}}
.dl-chips{{display:flex;flex-direction:column;gap:3px}}
.dl-chip{{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--fg2);white-space:nowrap}}
.dl-left .dl-chip{{flex-direction:row-reverse}}
.dl-chip i{{width:13px;height:13px;border-radius:3px;flex:0 0 auto}}
.dl-sample{{position:relative;width:70px;height:56px;flex:0 0 auto;display:flex;align-items:center;justify-content:center}}
.dl-ball{{width:46px;height:46px;border-radius:50%;background:linear-gradient(to bottom,rgb(50,160,50) 0 50%,rgb(255,40,20) 50% 100%);box-shadow:inset 0 0 0 1px rgba(255,255,255,.22),0 2px 6px rgba(0,0,0,.3)}}
.dl-arrow{{position:absolute;font-size:17px;font-weight:700;line-height:1}}
.dl-arr-top{{left:-2px;top:7px;color:rgb(60,180,75)}}
.dl-arr-bot{{right:-2px;bottom:7px;color:rgb(240,70,40)}}
#bubbleTip{{position:fixed;z-index:50;pointer-events:none;opacity:0;transition:opacity .1s;background:#12121a;border:1px solid rgba(255,255,255,.14);border-radius:10px;padding:11px 13px;font-size:12.5px;line-height:1.5;box-shadow:0 8px 28px rgba(0,0,0,.5);max-width:240px}}
#bubbleTip.on{{opacity:1}}
#bubbleTip .bt-title{{display:flex;align-items:center;gap:7px;font-weight:600;font-size:13.5px;color:#fff;margin-bottom:7px}}
#bubbleTip .bt-title svg{{width:20px;height:auto;border-radius:2px}}
#bubbleTip .bt-row{{display:flex;justify-content:space-between;gap:16px}}
#bubbleTip .bt-row .k{{color:var(--fg2)}}
#bubbleTip .bt-row .v{{color:var(--fg);font-variant-numeric:tabular-nums}}
</style>
</head>
<body>
<div class="wrap">
<div class="brand"><img src="favicon.svg" alt=""><b>{SITE_NAME}</b></div>
<h1>Which jobs are most at risk from AI?</h1>
<p class="lead">An interactive treemap of every occupation in 46 countries. We score each job&rsquo;s
<b>AI risk</b> by its <b>exposure</b> to generative AI &mdash; how much of its day-to-day tasks AI can
already do &mdash; on a 0&ndash;10 scale, computed from open ILO and OpenAI research and mapped onto
each country's official statistics. Pick a country:</p>
<div class="tabs" id="viewTabs">
<button class="tab-btn active" data-tab="bubbles" type="button">Bubble view</button>
<button class="tab-btn" data-tab="grid" type="button">Grid view</button>
</div>
<div class="tab-panel active" id="tab-bubbles">
<div class="bubble-legend">
<span><i class="lg lg-sal"></i>Top = avg pay (by USD, greener = higher)</span>
<span><i class="lg lg-exp"></i>Bottom = avg AI exposure (redder = higher)</span>
<span>Circle area &prop; workforce</span>
</div>
<div id="bubbleChart"></div>
<div class="dual-legend">
<div class="dl-side dl-left">
<div class="dl-title">Average pay (USD)</div>
<div class="dl-chips">{pay_chips}</div>
</div>
<div class="dl-sample" title="Top half = pay · Bottom half = AI exposure">
<span class="dl-arrow dl-arr-top">&larr;</span>
<span class="dl-ball"></span>
<span class="dl-arrow dl-arr-bot">&rarr;</span>
</div>
<div class="dl-side dl-right">
<div class="dl-title">AI exposure (risk)</div>
<div class="dl-chips">{risk_chips}</div>
</div>
</div>
</div>
<div id="bubbleTip"></div>
<div class="tab-panel" id="tab-grid">
<div class="grid">
{''.join(cards)}
</div>
</div>
{longform_html}
</div>
{build_footer()}
<script>
document.querySelectorAll(".lf-toggle").forEach(function(b){{
  b.addEventListener("click",function(){{
    var open=b.closest(".lf").classList.toggle("open");
    b.textContent=open?"Show less":"Read more";
  }});
}});
// ── Country bubble chart (tab 1) ──────────────────────────────
var BUBBLES={bubble_json};
(function(){{
  function expColor(score){{
    if(score==null) return [128,128,128];
    var t=Math.max(0,Math.min(10,score))/10,r,g,b;
    if(t<0.5){{var s=t/0.5;r=Math.round(50+s*180);g=Math.round(160-s*10);b=Math.round(50-s*20);}}
    else{{var s=(t-0.5)/0.5;r=Math.round(230+s*25);g=Math.round(150-s*110);b=Math.round(30-s*10);}}
    return [r,g,b];
  }}
  function rgb(a){{return "rgb("+a[0]+","+a[1]+","+a[2]+")";}}
  var SAL_LO=8000,SAL_HI=80000;                       // 与 Python sal_rgb / 图例同口径
  function salColor(usd){{
    if(usd==null) return [128,128,128];
    var t=Math.max(0,Math.min(1,(usd-SAL_LO)/(SAL_HI-SAL_LO)));
    return expColor(10*(1-t));                        // 高薪→绿
  }}
  // 直径 ∝ sqrt(workforce)（圆面积正比于就业人数，标准比例气泡）；最大径 211（原 132 的 160%）
  var ws=BUBBLES.map(function(d){{return d.workers||0;}}).filter(function(v){{return v>0;}});
  var smin=Math.sqrt(Math.min.apply(null,ws)),smax=Math.sqrt(Math.max.apply(null,ws)),DMIN=38,DMAX=211;
  function diam(w){{if(!w||w<=0)return DMIN;var t=(Math.sqrt(w)-smin)/((smax-smin)||1);return Math.round(DMIN+t*(DMAX-DMIN));}}
  function fmtInt(n){{return n==null?"—":n.toLocaleString();}}
  var host=document.getElementById("bubbleChart");
  // 多行悬浮弹层：avg exposure 用与 grid view 一致的分级色
  var tip=document.getElementById("bubbleTip");
  function tipHTML(d){{
    var ec=rgb(expColor(d.exp));
    return '<div class="bt-title">'+d.flag+'<span>'+d.name+'</span></div>'
      +'<div class="bt-row"><span class="k">Workforce</span><span class="v">'+fmtInt(d.workers)+'</span></div>'
      +'<div class="bt-row"><span class="k">Avg annual pay</span><span class="v">'+(d.usd!=null?"$"+fmtInt(d.usd)+" USD":"n/a")+'</span></div>'
      +(d.medianUsd!=null?'<div class="bt-row"><span class="k">Median pay</span><span class="v">$'+fmtInt(d.medianUsd)+' USD</span></div>':"")
      +'<div class="bt-row"><span class="k">Avg AI exposure</span><span class="v" style="color:'+ec+';font-weight:600">'+d.exp+'<span style="color:var(--fg2);font-weight:400">/10</span></span></div>';
  }}
  function moveTip(e){{
    var x=e.clientX+16,y=e.clientY+16;
    if(x+250>window.innerWidth)x=e.clientX-250;
    if(y+130>window.innerHeight)y=e.clientY-130;
    tip.style.left=x+"px";tip.style.top=y+"px";
  }}
  // 按人数降序（最大的 CN/IN 在最中间），中心向外无重叠圆填充（贪心切向放置，取离中心最近的合法位）
  var items=BUBBLES.map(function(d,i){{return {{i:i,d:d,r:diam(d.workers)/2}};}}).sort(function(a,b){{return b.r-a.r;}});
  var PAD=2.5;
  (function pack(){{
    var placed=[];
    for(var n=0;n<items.length;n++){{
      var it=items[n],r=it.r+PAD;
      if(n===0){{it.x=0;it.y=0;it._r=r;placed.push(it);continue;}}
      var best=null,bestD=Infinity;
      for(var j=0;j<placed.length;j++){{
        var pj=placed[j],dist=pj._r+r;
        for(var a=0;a<360;a+=5){{
          var ang=a*Math.PI/180,x=pj.x+dist*Math.cos(ang),y=pj.y+dist*Math.sin(ang),ok=true;
          for(var k=0;k<placed.length;k++){{
            var pk=placed[k],dx=x-pk.x,dy=y-pk.y,rr=pk._r+r-0.5;
            if(dx*dx+dy*dy<rr*rr){{ok=false;break;}}
          }}
          if(ok){{var dc=x*x+y*y;if(dc<bestD){{bestD=dc;best={{x:x,y:y}};}}}}
        }}
      }}
      if(!best)best={{x:0,y:0}};
      it.x=best.x;it.y=best.y;it._r=r;placed.push(it);
    }}
  }})();
  var minX=1e9,maxX=-1e9,minY=1e9,maxY=-1e9;
  items.forEach(function(it){{minX=Math.min(minX,it.x-it.r);maxX=Math.max(maxX,it.x+it.r);minY=Math.min(minY,it.y-it.r);maxY=Math.max(maxY,it.y+it.r);}});
  var W=maxX-minX,H=maxY-minY;
  function renderPacked(){{
    var avail=host.clientWidth||900,scale=W>0?avail/W:1,offX=(avail-W*scale)/2;  // 始终按容器宽度缩放（可放大撑满，非仅缩小）
    host.style.height=Math.ceil(H*scale)+"px";
    host.innerHTML=items.map(function(it){{
      var d=it.d,dd=it.r*2*scale;
      var left=(it.x-it.r-minX)*scale+offX,top=(it.y-it.r-minY)*scale;
      var bg="linear-gradient(to bottom,"+rgb(salColor(d.usd))+" 0 50%,"+rgb(expColor(d.exp))+" 50% 100%)";
      var fl=dd>=42?'<span class="bflag">'+d.flag+'</span>':"";
      return '<a class="bubble" href="/country/'+d.slug+'/" data-i="'+it.i+'" aria-label="'+d.name+'" style="left:'+left+'px;top:'+top+'px;width:'+dd+'px;height:'+dd+'px;background:'+bg+'">'+fl+'</a>';
    }}).join("");
    host.querySelectorAll(".bubble").forEach(function(el){{
      var d=BUBBLES[+el.dataset.i];
      el.addEventListener("mouseenter",function(e){{tip.innerHTML=tipHTML(d);tip.classList.add("on");moveTip(e);}});
      el.addEventListener("mousemove",moveTip);
      el.addEventListener("mouseleave",function(){{tip.classList.remove("on");}});
    }});
  }}
  renderPacked();
  window.addEventListener("resize",renderPacked);
  document.querySelectorAll("#viewTabs .tab-btn").forEach(function(b){{
    b.addEventListener("click",function(){{
      var t=b.dataset.tab;
      document.querySelectorAll("#viewTabs .tab-btn").forEach(function(x){{x.classList.toggle("active",x===b);}});
      document.getElementById("tab-bubbles").classList.toggle("active",t==="bubbles");
      document.getElementById("tab-grid").classList.toggle("active",t==="grid");
    }});
  }});
}})();
</script>
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
    d.text((90, 438), "How exposed is every job to AI — 46 countries, one 0–10 scale.",
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
    desc = ("AI Job Risk Map is a free, independent atlas of how exposed 5,000+ jobs in 42 "
            "countries are to generative AI, on one comparable 0–10 scale.")
    body = f"""<body><div class="wrap">
<a class="back" href="/">&larr; Back to the map</a>
<h1>About AI Job Risk Map</h1>
<p class="lead">A free, independent atlas of how exposed the world&rsquo;s jobs are to generative AI &mdash;
5,000+ occupations across 46 countries, on one comparable 0&ndash;10 scale.</p>

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
<p>Instead of one country or one headline number, the map puts 42 national labour markets on a single global
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
    desc = ("Download free high-resolution AI job risk maps for 46 countries (CC BY 4.0), embed the "
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
46 countries, an interactive embed, and ready-to-paste citations. Free to use with attribution.</p>

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
        "across 46 countries. Every occupation is scored 0–10 by combining two open research "
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
        f"- [Full dataset (CSV)]({DATASET_URL}): every occupation in all 46 countries with its "
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
        "name": "AI Job Risk Map — 42 Countries, 5000+ Occupations",
        "description": ("Interactive treemap of AI exposure for 5000+ occupations across 42 "
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


def faq_ld(faqs):
    # FAQPage schema; answer text matches the visible faq_accordion (Google requires
    # the FAQ content to be visible on the page).
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs],
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


def load_longform():
    """Optional LLM-written long-form homepage copy: job-treemap/longform.json ->
    {"sections": [{"h2": str, "html": str}, ...]}. Absent -> homepage renders without it."""
    p = os.path.join(HERE, "longform.json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8")).get("sections", [])
        except Exception as e:
            print("  [longform] failed to read, skipping:", e)
    return []


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

    # Display order across the whole site (landing cards, country switcher,
    # footer "Other countries", embed hub, sitemap, CSV): alphabetical by
    # English country name.
    present = sorted((cc for cc in ORDER if cc in by_country),
                     key=lambda c: COUNTRY_META[c][0])
    # 可选：命令行传国家码（如 `python build.py US`）只重建这些国家，便于单国预览。
    # 传参时跳过下方清理旧目录的步骤，避免误删其他国家已生成的页面。
    only = [a.upper() for a in sys.argv[1:] if a.upper() in present]
    partial = bool(only)
    if only:
        present = only
    os.makedirs(DIST, exist_ok=True)

    # Remove legacy output from older layouts so rebuilds don't leave stale,
    # unlinked pages: uppercase per-country dirs (very old), lowercase per-country
    # dirs at the root (previous /slug/ layout) and the old overview data/ copies.
    # NB: static/ is preserved — the Playwright-shot PNG maps live there.
    import shutil
    if not partial:
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
            "sourceHtml": sidebar_source_html(cc), "dataUrl": "data.json", "aboutUrl": "/methodology.html",
            "ver": VER, "embedSnippet": embed_snippet,
            "countries": [{"cc": c, "name": COUNTRY_META[c][0], "url": f"/country/{SLUG[c]}/",
                           "flag": FLAG.get(c, "")}
                          for c in present],
        }
        summary = summaries.get(cc) or fallback_summary(name, st)
        faqs = country_faqs(name, st)
        content = static_content(cc, name, st, summary, present, faqs)

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
                  + ld_script(breadcrumb_ld(cc, name))
                  + ld_script(faq_ld(faqs)))
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
                .replace("__H1__", esc(f"AI Job Risk in {name}"))
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
            "sourceHtml": sidebar_source_html(cc), "dataUrl": f"/country/{slug}/data.json",
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

    if partial:
        # 单国预览模式：只重建 /country/{slug}/ 与 /embed/{slug}，不碰全站页
        # （landing/methodology/embed hub/CSV 仍用整站数据，须走完整构建刷新）。
        print(f"  [partial] 仅重建 {','.join(present)}，跳过全站页")
        return

    # ── Landing hub at root ───────────────────────────────────────
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_landing(present, stats_by_cc))
    with open(os.path.join(DIST, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON)

    # ── Methodology + About pages (distinct: how it's computed vs what it is) ──
    with open(os.path.join(DIST, "methodology.html"), "w", encoding="utf-8") as f:
        f.write(METHODOLOGY_HTML.replace("__DOMAIN__", DOMAIN)
                .replace("__SOURCES_SECTION__", methodology_sources_section(present))
                .replace("__FOOTER__", build_footer()))
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
