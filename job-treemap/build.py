"""Build per-country AI-exposure treemap sites from occupations_v2.json.

Reuses the exact same self-contained template (job-treemap/template.html) for
every country. Emits, under job-treemap/dist/:
  - {cc}/index.html + {cc}/data.json   -> standalone, independently deployable site per country
  - data/{cc}.json                     -> data for the overview switcher
  - index.html                         -> single overview page with a country dropdown

Run:  E:\\run\\Python3.13\\python.exe job-treemap/build.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
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
}
# Order shown in the overview dropdown.
ORDER = ["AU", "US", "UK", "CA", "NZ", "JP", "DE", "FR", "ES", "IT", "NL", "IE"]

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
           '<rect width="32" height="32" rx="6" fill="#0a0a0f"/>'
           '<rect x="4" y="4" width="13" height="24" rx="1.5" fill="#e6961e"/>'
           '<rect x="19" y="4" width="9" height="11" rx="1.5" fill="#32a032"/>'
           '<rect x="19" y="17" width="9" height="11" rx="1.5" fill="#ff5014"/>'
           '</svg>')


def to_int(v):
    if v in (None, "", 0, "0", "0.00"):
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def build_record(o, cat_slug):
    ai = o.get("ai") or {}
    exp_raw = ai.get("automation_exposure")
    exposure = int(round(exp_raw)) if exp_raw is not None else None
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
        "url": None,
    }


def main():
    occ = json.load(open(SRC, encoding="utf-8"))["occupations"]
    cat_slug = json.load(open(CATS, encoding="utf-8"))["category_slug"]
    template = open(TEMPLATE, encoding="utf-8").read()

    by_country = {}
    for o in occ:
        cc = o.get("country")
        if cc not in COUNTRY_META:
            continue
        by_country.setdefault(cc, []).append(build_record(o, cat_slug))

    countries_present = [cc for cc in ORDER if cc in by_country]
    os.makedirs(os.path.join(DIST, "data"), exist_ok=True)

    # ── Per-country standalone sites + overview data ──────────────
    switcher_meta = []
    for cc in countries_present:
        name, currency, symbol, source = COUNTRY_META[cc]
        rows = sorted(by_country[cc], key=lambda d: (d["category"] or "", -(d["jobs"] or 0)))

        # overview data copy
        with open(os.path.join(DIST, "data", f"{cc}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)

        # standalone folder
        cdir = os.path.join(DIST, cc)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(cdir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)
        cfg = {
            "countries": [], "cc": cc, "countryName": name,
            "currency": currency, "symbol": symbol,
            "sourceHtml": source, "dataUrl": "data.json",
        }
        html = template.replace("__CONFIG__", json.dumps(cfg, ensure_ascii=False))
        with open(os.path.join(cdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        with open(os.path.join(cdir, "favicon.svg"), "w", encoding="utf-8") as f:
            f.write(FAVICON)

        switcher_meta.append({
            "cc": cc, "name": name, "currency": currency,
            "symbol": symbol, "sourceHtml": source,
        })
        print(f"  {cc}: {len(rows)} occupations")

    # ── Overview page with country switcher ───────────────────────
    first = switcher_meta[0]
    cfg = {
        "countries": switcher_meta, "current": first["cc"],
        "countryName": first["name"], "currency": first["currency"],
        "symbol": first["symbol"], "sourceHtml": first["sourceHtml"],
        "dataUrl": "",
    }
    html = template.replace("__CONFIG__", json.dumps(cfg, ensure_ascii=False))
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(DIST, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON)

    print(f"\nBuilt overview + {len(countries_present)} standalone sites -> {DIST}")
    print("Countries:", ", ".join(countries_present))


if __name__ == "__main__":
    main()
