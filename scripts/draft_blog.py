# -*- coding: utf-8 -*-
"""Draft a blog post with DeepSeek, for HUMAN review (半自动工作流的起草端).

Produces a Markdown file with YAML front-matter and `status: draft` in
aijobrisk-go/content/blog/. A human then reviews/edits, adds a hero image,
verifies facts, byline & the related_* links, flips status to `published`, and
runs `python scripts/build_blog.py` to bake it.

This never publishes: drafts are excluded by build_blog until status=published.
Related keys suggested by the model are validated against the live Go data and
invalid ones are dropped (kept in a review comment), so the draft is buildable.

Usage:
  python scripts/draft_blog.py --topic "2026 H1 tech layoffs vs AI exposure"
  python scripts/draft_blog.py --type news --topic "..." \
      --source-name "Reuters" --source-url "https://…"
Options: --slug, --notes "extra guidance", --force (overwrite existing draft).

Copyright note (news): we NEVER reproduce the source. The model is instructed
to write a short original summary + our own data angle + attribution only.
"""
import argparse
import datetime
import os
import re
import sys

import yaml

from scripts import build_blog
from scripts import _deepseek_rest


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:80] or "untitled"


SYSTEM = (
    "You are the editorial writer for aijobrisk.com, a data site that measures "
    "generative-AI task exposure across occupations, industries and countries. "
    "You write clear, factual, non-sensational English for a general audience, "
    "with an evidence-led, E-E-A-T tone. You never fabricate specific numbers; "
    "if you are unsure of a figure, describe it qualitatively and add a "
    "[VERIFY] marker so the human editor checks it. You always tie the piece "
    "back to our own angle: how the topic maps onto AI task-exposure of real "
    "occupations. Output STRICT JSON only, no prose around it."
)


def build_prompt(a, sectors, countries):
    kind = "news" if a.type == "news" else "analysis"
    length = "300-450 words" if a.type == "news" else "650-950 words"
    src = ""
    if a.type == "news":
        src = (
            f"\nThis is a NEWS piece reacting to an external report from "
            f"'{a.source_name}' ({a.source_url}). Do NOT reproduce or quote the "
            "source at length. Write a SHORT original summary in your own words, "
            "then add our data angle and a takeaway. Attribution is handled "
            "separately, so do not paste the article text."
        )
    notes = f"\nExtra editor guidance: {a.notes}" if a.notes else ""
    return (
        f"Write a {kind} blog post ({length}) on this topic:\n\"{a.topic}\"\n"
        f"{src}{notes}\n\n"
        "Body must be Markdown using ## / ### headings (no H1 — the title is "
        "separate), short paragraphs, and at least one section connecting the "
        "topic to AI task-exposure of specific occupations. End with a clear "
        "takeaway. Avoid hype and unverifiable precise statistics.\n\n"
        "Also suggest internal links from these FIXED lists (pick only relevant, "
        "omit if none):\n"
        f"- related_sectors: choose from {sorted(sectors)}\n"
        f"- related_countries: ISO-like codes, choose from {sorted(countries)}\n"
        "- related_slugs: 2-5 occupation slugs in kebab-case (e.g. "
        "'software-developer', 'data-entry-clerk', 'customer-service-representative'); "
        "we validate these, so use natural occupation names.\n\n"
        "Return STRICT JSON with keys: title (string, <=65 chars), dek (string, "
        "1 sentence), body_markdown (string), tags (array of 2-4 kebab-case, e.g. "
        "layoffs/ai-tools/policy/research), related_slugs (array), "
        "related_sectors (array), related_countries (array)."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--type", choices=["post", "news"], default="post")
    ap.add_argument("--source-name", default="")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--slug", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--force", action="store_true", help="overwrite existing draft")
    a = ap.parse_args()

    if a.type == "news" and not (a.source_name and a.source_url):
        ap.error("--type news requires --source-name and --source-url")

    slugs, countries, sectors = build_blog.load_valid_keys()

    print("Drafting with DeepSeek …")
    d = _deepseek_rest.complete_json(SYSTEM, build_prompt(a, sectors, countries))

    title = (d.get("title") or a.topic).strip()
    slug = a.slug.strip() or slugify(d.get("slug") or title)
    if not build_blog.SLUG_RE.match(slug):
        slug = slugify(slug)

    def keep(vals, valid):
        got, bad = [], []
        for x in vals or []:
            x = str(x).strip()
            (got if x in valid else bad).append(x)
        return got, bad

    rel_slugs, bad_slugs = keep(d.get("related_slugs"), slugs)
    rel_sect, bad_sect = keep(d.get("related_sectors"), sectors)
    rel_cc, bad_cc = keep(d.get("related_countries"), countries)

    today = datetime.date.today().isoformat()
    fm = {
        "slug": slug,
        "title": title,
        "dek": (d.get("dek") or "").strip(),
        "type": a.type,
        "status": "draft",
        "published_at": today,
        "updated_at": today,
        "featured": False,
        "author": "editorial",
        "hero_image": "",
        "hero_alt": "",
        "hero_credit": "",
        "tags": [str(t).strip() for t in (d.get("tags") or []) if str(t).strip()],
        "related_slugs": rel_slugs,
        "related_sectors": rel_sect,
        "related_countries": rel_cc,
    }
    if a.type == "news":
        fm["source_name"] = a.source_name
        fm["source_url"] = a.source_url

    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=100).strip()
    review = []
    for label, bad in (("related_slugs", bad_slugs), ("related_sectors", bad_sect), ("related_countries", bad_cc)):
        if bad:
            review.append(f"dropped invalid {label}: {', '.join(bad)}")
    review_block = ""
    if review:
        review_block = "<!-- REVIEW: " + " | ".join(review) + " -->\n"

    body = (d.get("body_markdown") or "").strip()
    doc = f"---\n{front}\n---\n\n{review_block}{body}\n"

    os.makedirs(build_blog.CONTENT_DIR, exist_ok=True)
    path = os.path.join(build_blog.CONTENT_DIR, slug + ".md")
    if os.path.exists(path) and not a.force:
        print("Refusing to overwrite existing %s (use --force)." % path)
        return 1
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)

    print("\nDraft written: %s" % path)
    print("  title: %s" % title)
    print("  related: slugs=%d sectors=%d countries=%d" % (len(rel_slugs), len(rel_sect), len(rel_cc)))
    for r in review:
        print("  NOTE " + r)
    print("\nNext: review facts & byline, add a hero image, set status: published,")
    print("      then run:  python scripts/build_blog.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
