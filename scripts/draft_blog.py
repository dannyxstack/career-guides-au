# -*- coding: utf-8 -*-
"""Draft blog post(s) with DeepSeek, for HUMAN review (半自动工作流的起草端).

Two modes:
  1) Single topic:   --topic "..."  [--type news --source-name .. --source-url ..]
  2) Batch/rotation: --from-topics scripts/blog_topics.txt --count 2
       picks the least-recently-used topics (state in .blog_topics_used.json),
       honours --exclude-tags, and drafts each as --type (default post).

Each run writes markdown into aijobrisk-go/content/blog/. Default status is
`published` (generate-then-review: a human reviews live and retracts if needed);
pass `--status draft` for a review-before-publish gate instead. Either way a
human should verify facts & byline; a hero image is optional (build
auto-generates an SVG). Model-suggested related keys are validated against live
Go data; invalid ones are dropped (kept in a REVIEW comment).

Topics file format (one per line; blank / #-comment lines ignored):
    tag | Topic sentence
e.g.  augmentation | How AI copilots are reshaping what accountants do

Usage:
  python -m scripts.draft_blog --topic "..." --type post
  python -m scripts.draft_blog --from-topics scripts/blog_topics.txt --count 3 \
         --type post --exclude-tags layoffs --notes "constructive, upbeat"
"""
import argparse
import datetime
import json
import os
import re
import sys

import yaml

from scripts import build_blog
from scripts import _deepseek_rest

HERE = os.path.dirname(os.path.abspath(__file__))
TOPIC_STATE = os.path.join(HERE, ".blog_topics_used.json")


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


def build_prompt(topic, typ, source_name, source_url, notes, sectors, countries):
    kind = "news" if typ == "news" else "analysis"
    length = "300-450 words" if typ == "news" else "650-950 words"
    src = ""
    if typ == "news":
        src = (
            f"\nThis is a NEWS piece reacting to an external report from "
            f"'{source_name}' ({source_url}). Do NOT reproduce or quote the "
            "source at length. Write a SHORT original summary in your own words, "
            "then add our data angle and a takeaway. Attribution is handled "
            "separately, so do not paste the article text."
        )
    extra = f"\nExtra editor guidance: {notes}" if notes else ""
    return (
        f"Write a {kind} blog post ({length}) on this topic:\n\"{topic}\"\n"
        f"{src}{extra}\n\n"
        "Body must be Markdown using ## / ### headings (no H1 — the title is "
        "separate), short paragraphs, and at least one section connecting the "
        "topic to AI task-exposure of specific occupations. End with a clear "
        "takeaway. Avoid hype and unverifiable precise statistics.\n\n"
        "Also suggest internal links from these FIXED lists (pick only relevant, "
        "omit if none):\n"
        f"- related_sectors: choose from {sorted(sectors)}\n"
        f"- related_countries: ISO-like codes, choose from {sorted(countries)}\n"
        "- related_slugs: 2-5 occupation slugs in kebab-case (e.g. "
        "'software-developer', 'registered-nurse', 'financial-analyst'); we "
        "validate these, so use natural occupation names.\n\n"
        "Return STRICT JSON with keys: title (string, <=65 chars), dek (string, "
        "1 sentence), body_markdown (string), tags (array of 2-4 kebab-case, e.g. "
        "augmentation/new-roles/hiring/reskilling/research), related_slugs "
        "(array), related_sectors (array), related_countries (array)."
    )


def draft_one(topic, typ, notes, keys, authors, source_name="", source_url="",
              slug_override="", force=False, extra_tags=None, status="published"):
    """Generate one draft. Returns path written, or None if skipped/failed."""
    slugs, countries, sectors = keys
    try:
        d = _deepseek_rest.complete_json(SYSTEM, build_prompt(topic, typ, source_name, source_url, notes, sectors, countries))
    except Exception as e:
        print("  ERROR DeepSeek for %r: %s" % (topic[:50], str(e)[:80]))
        return None

    title = (d.get("title") or topic).strip()
    slug = slug_override.strip() or slugify(d.get("slug") or title)
    if not build_blog.SLUG_RE.match(slug):
        slug = slugify(slug)

    path = os.path.join(build_blog.CONTENT_DIR, slug + ".md")
    if os.path.exists(path) and not force:
        print("  skip (exists): %s" % slug)
        return None

    def keep(vals, valid):
        got, bad = [], []
        for x in vals or []:
            x = str(x).strip()
            (got if x in valid else bad).append(x)
        return got, bad

    rel_slugs, bad_slugs = keep(d.get("related_slugs"), slugs)
    rel_sect, bad_sect = keep(d.get("related_sectors"), sectors)
    rel_cc, bad_cc = keep(d.get("related_countries"), countries)

    tags = [str(t).strip() for t in (d.get("tags") or []) if str(t).strip()]
    for t in (extra_tags or []):
        if t not in tags:
            tags.append(t)

    today = datetime.date.today().isoformat()
    fm = {
        "slug": slug, "title": title, "dek": (d.get("dek") or "").strip(),
        "type": typ, "status": status, "published_at": today, "updated_at": today,
        "featured": False, "author": "editorial",
        "hero_image": "", "hero_alt": "", "hero_credit": "",
        "tags": tags, "related_slugs": rel_slugs,
        "related_sectors": rel_sect, "related_countries": rel_cc,
    }
    if typ == "news":
        fm["source_name"] = source_name
        fm["source_url"] = source_url

    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=100).strip()
    review = []
    for label, bad in (("related_slugs", bad_slugs), ("related_sectors", bad_sect), ("related_countries", bad_cc)):
        if bad:
            review.append("dropped invalid %s: %s" % (label, ", ".join(bad)))
    review_block = ("<!-- REVIEW: " + " | ".join(review) + " -->\n") if review else ""
    body = (d.get("body_markdown") or "").strip()

    os.makedirs(build_blog.CONTENT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("---\n%s\n---\n\n%s%s\n" % (front, review_block, body))

    print("  draft: %s  (related slugs=%d sectors=%d cc=%d)" % (slug, len(rel_slugs), len(rel_sect), len(rel_cc)))
    for r in review:
        print("    NOTE " + r)
    return path


def load_topics(path):
    out = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if "|" in ln:
            tag, topic = ln.split("|", 1)
            out.append((tag.strip(), topic.strip()))
        else:
            out.append(("general", ln))
    return out


def load_topic_state():
    if os.path.exists(TOPIC_STATE):
        try:
            return json.load(open(TOPIC_STATE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def pick_topics(topics, count, exclude_tags, state):
    """Least-recently-used first (never-used = ''); honour exclude_tags."""
    pool = [(tag, t) for tag, t in topics if tag not in exclude_tags]
    pool.sort(key=lambda x: state.get(x[1], ""))   # oldest / unused first
    return pool[:count]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default="")
    ap.add_argument("--from-topics", dest="from_topics", default="")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--exclude-tags", dest="exclude_tags", default="")
    ap.add_argument("--type", choices=["post", "news"], default="post")
    ap.add_argument("--status", choices=["draft", "published"], default="published",
                    help="生成即 published（默认）；后续人工审核撤稿。传 draft 则需人工放行")
    ap.add_argument("--source-name", default="")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--slug", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    if not a.topic and not a.from_topics:
        ap.error("provide --topic or --from-topics")
    if a.type == "news" and a.topic and not (a.source_name and a.source_url):
        ap.error("--type news requires --source-name and --source-url")

    keys = build_blog.load_valid_keys()
    authors = build_blog.load_authors()

    # single-topic mode
    if a.topic:
        print("Drafting 1 post with DeepSeek …")
        p = draft_one(a.topic, a.type, a.notes, keys, authors,
                      source_name=a.source_name, source_url=a.source_url,
                      slug_override=a.slug, force=a.force, status=a.status)
        _finish(1 if p else 0)
        return 0 if p else 1

    # batch/rotation mode
    exclude = {t.strip() for t in a.exclude_tags.split(",") if t.strip()}
    topics = load_topics(a.from_topics)
    state = load_topic_state()
    picks = pick_topics(topics, a.count, exclude, state)
    if not picks:
        print("No eligible topics (after exclude-tags).")
        return 1
    print("Drafting %d post(s) with DeepSeek (from %d topics, excluding %s) …"
          % (len(picks), len(topics), sorted(exclude) or "none"))

    today = datetime.date.today().isoformat()
    made = 0
    for tag, topic in picks:
        print("- [%s] %s" % (tag, topic))
        p = draft_one(topic, a.type, a.notes, keys, authors, extra_tags=[tag], status=a.status)
        if p:
            made += 1
            state[topic] = today          # mark used only on success
    json.dump(state, open(TOPIC_STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    _finish(made)
    return 0 if made else 1


def _finish(n):
    print("\nWrote %d draft(s) to %s" % (n, build_blog.CONTENT_DIR))
    if n:
        print("Next: review facts & byline, set status: published, then run:")
        print("      python scripts/build_blog.py")


if __name__ == "__main__":
    sys.exit(main())
