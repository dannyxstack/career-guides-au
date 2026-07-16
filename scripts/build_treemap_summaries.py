"""Generate per-country risk-summary copy for the job-treemap pages via DeepSeek.

Writes job-treemap/summaries.json = {cc: "<p>…</p><p>…</p>"} (HTML paragraphs),
consumed by job-treemap/build.py. Incremental + cached: already-written countries
are skipped unless --force, and the cache is flushed after each country so an
interrupted run (e.g. intermittent DNS) can simply be resumed.

Run:  python -m scripts.build_treemap_summaries [--force] [--countries AU,US]
"""
import argparse
import html
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "job-treemap"))
import build  # noqa: E402  (reuse build_record / country_stats / COUNTRY_META / SLUG)
from scripts._deepseek_rest import complete_json  # noqa: E402

OUT = os.path.join(REPO, "job-treemap", "summaries.json")

SYSTEM = (
    "You are a labour-market analyst writing neutral, factual explainer copy for a public "
    "data site about how exposed jobs are to generative AI. Write in clear British English, "
    "no hype, no bullet points, no markdown. Return strict JSON."
)

PROMPT = """Write a summary of generative-AI exposure across the {name} job market.

Rules:
- Exactly 150–300 words, in TWO paragraphs separated by a blank line.
- Plain prose only. No markdown, no lists, no headings.
- Use the figures below; do not invent numbers.
- Explain that the 0–10 score measures task exposure, and that exposure is NOT the same
  as job loss — it flags where AI is most likely to reshape tasks first.
- Paragraph 1: the overall picture (scale, the weighted-average exposure, what the scale means).
- Paragraph 2: which kinds of roles/industries are most vs least exposed and why.

Figures for {name}:
- Occupations covered: {total}
- Workers covered: {workers}
- Employment-weighted average exposure (0–10): {avg}
- Most exposed occupations: {top}
- Least exposed occupations: {bottom}
- Industries with the highest average exposure: {inds}

Return JSON: {{"summary": "<paragraph 1>\\n\\n<paragraph 2>"}}"""


def to_html(text):
    paras = [p.strip() for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]
    if not paras:  # single-block fallback
        paras = [text.strip()]
    return "\n".join(f"<p>{html.escape(p)}</p>" for p in paras)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="regenerate even if cached")
    ap.add_argument("--countries", help="comma-separated country codes, e.g. AU,US")
    args = ap.parse_args()

    occ = json.load(open(build.SRC, encoding="utf-8"))["occupations"]
    cat_slug = json.load(open(build.CATS, encoding="utf-8"))["category_slug"]

    by_country = {}
    for o in occ:
        cc = o.get("country")
        if cc in build.COUNTRY_META:
            by_country.setdefault(cc, []).append(build.build_record(o, cat_slug, {}))

    present = [cc for cc in build.ORDER if cc in by_country]
    if args.countries:
        want = {c.strip().upper() for c in args.countries.split(",")}
        present = [cc for cc in present if cc in want]

    cache = {}
    if os.path.exists(OUT):
        cache = json.load(open(OUT, encoding="utf-8"))

    for cc in present:
        if cc in cache and not args.force:
            print(f"  {cc}: cached, skip")
            continue
        name = build.COUNTRY_META[cc][0]
        st = build.country_stats(by_country[cc])
        top = "; ".join(f"{r['title']} ({r['exposure']}/10)" for r in st["top"][:8])
        bottom = "; ".join(f"{r['title']} ({r['exposure']}/10)" for r in st["bottom"][:8])
        inds = "; ".join(f"{i['name']} ({i['avg']:.1f}/10)"
                         for i in st["industries"][:5] if i["avg"] is not None)
        prompt = PROMPT.format(
            name=name, total=st["total"], workers=f"{st['total_jobs']:,}",
            avg=f"{st['weighted_avg']:.1f}", top=top, bottom=bottom, inds=inds)
        try:
            res = complete_json(SYSTEM, prompt)
            summary = (res.get("summary") or "").strip()
            if not summary:
                raise ValueError("empty summary")
        except Exception as e:
            print(f"  {cc}: FAILED ({e}) — leaving to fallback")
            continue
        cache[cc] = to_html(summary)
        json.dump(cache, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        wc = len(summary.split())
        print(f"  {cc}: ok ({wc} words)")

    print(f"\nWrote {len(cache)} summaries -> {OUT}")


if __name__ == "__main__":
    main()
