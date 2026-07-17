"""Generate the homepage long-form SEO copy for the job-treemap landing page via DeepSeek.

Writes job-treemap/longform.json = {"sections": [{"h2": str, "html": "<p>…</p>…"}, ...]}
(three ~1000-word sections), consumed by job-treemap/build.py -> build_landing().

The copy is grounded in real aggregate figures computed from occupations_v2.json and
passed to the model as a FACTS block; the prompt forbids inventing any number or claim.
Global content (not per country), so it is cheap to review once and lock in.

Incremental + cached: already-written sections are skipped unless --force, and the
cache is flushed to disk after each section so an interrupted run can be resumed.

Run:  python -m scripts.build_treemap_longform [--force] [--sections read,compare,advice]
"""
import argparse
import html
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "job-treemap"))
import build  # noqa: E402  (reuse build_record / country_stats / COUNTRY_META / ORDER)
from scripts._deepseek_rest import complete_json  # noqa: E402

OUT = os.path.join(REPO, "job-treemap", "longform.json")

SYSTEM = (
    "You are a labour-market analyst writing neutral, factual explainer copy for a public "
    "data site about how exposed jobs are to generative AI. Write in clear British English, "
    "no hype, no bullet points, no markdown, no headings inside the answer. Return strict JSON."
)

# Each section: (id, H2 shown on the page, focused instruction for that section).
SECTIONS = [
    ("read",
     "What “AI exposure” means — and what it doesn’t",
     "Explain, for a general reader, what the 0–10 AI-exposure score on this site measures: "
     "how much of an occupation's day-to-day tasks generative AI can already perform or assist "
     "with. Stress clearly and more than once that exposure is NOT the same as job loss or "
     "automation — it flags where AI is most likely to reshape tasks first. Explain how to read "
     "the treemap (tile area = size of the workforce, colour = exposure from green/low to red/high) "
     "and that scores are ranked on a single global percentile scale so countries are comparable. "
     "End by noting exposure is a starting point for thinking about complementary skills, not a "
     "prediction about any individual's job."),
    ("compare",
     "Which countries and industries are most exposed",
     "Using ONLY the per-country averages and industry figures in the FACTS block, describe how "
     "generative-AI exposure varies across the 13 countries and which kinds of industries sit at "
     "the top and bottom of the range. Explain WHY office- and information-heavy economies score "
     "higher while economies weighted toward physical, manual or in-person work score lower. Do "
     "not rank the countries beyond what the figures support, and do not state a difference is "
     "large or small unless the numbers show it."),
    ("advice",
     "What high exposure means for workers — and the limits of the data",
     "Explain what a worker in a highly exposed role should take from this, in practical, "
     "non-alarmist terms: which task types AI complements vs struggles with, and how to build "
     "complementary skills. Then be candid about the limitations of the data: it scores tasks not "
     "jobs, it is built from research indices mapped onto official occupation classifications, it "
     "cannot predict adoption speed, employer decisions, new job creation or regulation, and some "
     "mappings are model-assisted. Avoid any invented statistic."),
]

PROMPT = """Write one section of a long-form explainer for the homepage of an AI-job-exposure data site.

Section topic: {topic}

Rules:
- 900–1100 words, split into 4–6 plain-prose paragraphs.
- No markdown, no lists, no headings, no bold — just paragraphs of prose.
- Use ONLY the figures in the FACTS block below. Do NOT invent any number, percentage,
  proportion, or claim (e.g. never write things like "40% of tasks" or "human moat" unless
  that exact figure appears in FACTS). If you don't have a number, describe qualitatively.
- Neutral, factual, British English. Exposure is task exposure, NOT job loss.

FACTS (all figures already computed from official statistics; do not add to them):
{facts}

Return JSON: {{"paragraphs": ["<para 1>", "<para 2>", "..."]}}"""


def build_facts():
    """Aggregate the real figures the model is allowed to use."""
    occ = json.load(open(build.SRC, encoding="utf-8"))["occupations"]
    cat_slug = json.load(open(build.CATS, encoding="utf-8"))["category_slug"]

    by_country = {}
    for o in occ:
        cc = o.get("country")
        if cc in build.COUNTRY_META:
            by_country.setdefault(cc, []).append(build.build_record(o, cat_slug, {}))
    present = [cc for cc in build.ORDER if cc in by_country]

    per_country, tot_occ, tot_workers = [], 0, 0
    wsum_all, wcnt_all = 0.0, 0
    ind_agg = {}
    for cc in present:
        st = build.country_stats(by_country[cc])
        name = build.COUNTRY_META[cc][0]
        per_country.append((name, st["weighted_avg"], st["total"], st["total_jobs"]))
        tot_occ += st["total"]
        tot_workers += st["total_jobs"]
        for r in by_country[cc]:
            if r["exposure"] is not None and r["jobs"]:
                wsum_all += r["exposure"] * r["jobs"]
                wcnt_all += r["jobs"]
        for i in st["industries"]:
            if i["avg"] is None:
                continue
            d = ind_agg.setdefault(i["name"], {"wsum": 0.0, "wcnt": 0})
            d["wsum"] += i["avg"] * i["jobs"]
            d["wcnt"] += i["jobs"]

    global_avg = (wsum_all / wcnt_all) if wcnt_all else 0.0
    per_country.sort(key=lambda x: -x[1])
    inds = sorted(((n, d["wsum"] / d["wcnt"]) for n, d in ind_agg.items() if d["wcnt"]),
                  key=lambda x: -x[1])

    lines = [
        f"- Countries covered: {len(present)}",
        f"- Total occupations across all countries: {tot_occ:,}",
        f"- Total workers covered: {tot_workers:,}",
        f"- Global employment-weighted average exposure (0–10): {global_avg:.1f}",
        "- Employment-weighted average exposure by country (0–10), highest first:",
    ]
    lines += [f"    {name}: {avg:.1f} ({total:,} occupations, {workers:,} workers)"
              for name, avg, total, workers in per_country]
    top = inds[:6]
    top_names = {n for n, _ in top}
    low = [x for x in reversed(inds) if x[0] not in top_names][:6][::-1]
    lines.append("- Highest-exposure industries (global employment-weighted avg, 0–10):")
    lines += [f"    {n}: {a:.1f}" for n, a in top]
    lines.append("- Lowest-exposure industries (global employment-weighted avg, 0–10):")
    lines += [f"    {n}: {a:.1f}" for n, a in low]
    return "\n".join(lines)


def to_html(paras):
    out = [p.strip() for p in paras if isinstance(p, str) and p.strip()]
    return "\n".join(f"<p>{html.escape(p)}</p>" for p in out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="regenerate even if cached")
    ap.add_argument("--sections", help="comma-separated section ids, e.g. read,compare")
    args = ap.parse_args()

    want = None
    if args.sections:
        want = {s.strip() for s in args.sections.split(",")}

    cache = {}
    if os.path.exists(OUT):
        try:
            cache = {s["id"]: s for s in json.load(open(OUT, encoding="utf-8")).get("sections", [])}
        except Exception:
            cache = {}

    facts = build_facts()
    for sid, h2, instruction in SECTIONS:
        if want and sid not in want:
            continue
        if sid in cache and not args.force:
            print(f"  {sid}: cached, skip")
            continue
        prompt = PROMPT.format(topic=instruction, facts=facts)
        try:
            res = complete_json(SYSTEM, prompt)
            paras = res.get("paragraphs") or []
            htmlbody = to_html(paras)
            if not htmlbody:
                raise ValueError("empty body")
        except Exception as e:
            print(f"  {sid}: FAILED ({e}) — leaving to fallback (section omitted)")
            continue
        cache[sid] = {"id": sid, "h2": h2, "html": htmlbody}
        # Flush in canonical section order after each success (resumable).
        ordered = [cache[s[0]] for s in SECTIONS if s[0] in cache]
        json.dump({"sections": ordered}, open(OUT, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        wc = sum(len(p.split()) for p in paras)
        print(f"  {sid}: ok ({wc} words)")

    n = len([s for s in SECTIONS if s[0] in cache])
    print(f"\nWrote {n} sections -> {OUT}")


if __name__ == "__main__":
    main()
