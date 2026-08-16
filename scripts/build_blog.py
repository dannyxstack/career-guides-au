# -*- coding: utf-8 -*-
"""Bake the aijobrisk-go blog: Markdown (+ YAML front-matter) -> pre-rendered HTML.

Pipeline (Python bakes, Go serves — same pattern as build_industry_ai_adoption.py):

    aijobrisk-go/content/blog/*.md      author-written Markdown + front-matter
              |  build_blog.py
              v
    aijobrisk-go/data/blog/index.json   metadata array (loaded into memory by Go)
    aijobrisk-go/data/blog/{slug}.html  pre-rendered body HTML (read per request)

English only. Draft / future-dated posts are excluded from the build.
The related_slugs / related_sectors / related_countries keys are validated
against the live Go data so the internal-link cards never dead-link.

Front-matter schema (see docs/blog-plan.md):
    slug, title, dek, type(post|news), status(draft|published),
    published_at, updated_at?, featured?, author?,
    hero_image?, hero_alt?, hero_credit?,
    tags[]?, related_slugs[]?, related_sectors[]?, related_countries[]?,
    source_name?(news), source_url?(news)

Usage:  python scripts/build_blog.py
Exit code is non-zero if any published post fails hard validation.
"""
import json
import math
import os
import re
import sys
from datetime import date, datetime

import yaml
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
GO = os.path.join(HERE, "..", "aijobrisk-go")
CONTENT_DIR = os.path.join(GO, "content", "blog")
DATA_DIR = os.path.join(GO, "data")
OUT_DIR = os.path.join(DATA_DIR, "blog")

REQUIRED = ("slug", "title", "dek", "type", "status", "published_at")
VALID_TYPE = {"post", "news"}
VALID_STATUS = {"draft", "published"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)
WORDS_PER_MIN = 200


# ── validation key sets (data-driven) ────────────────────────────────────────
def _load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def load_valid_keys():
    occ = _load_json("occupations_v2.json").get("occupations", [])
    slugs = {o["slug"] for o in occ if o.get("slug")}
    countries = {o["country"] for o in occ if o.get("country")}
    ind = _load_json("industries_v2.json")
    sect = ind.get("sectors", ind) if isinstance(ind, dict) else ind
    sectors = {s["id"] for s in sect if s.get("id")}
    return slugs, countries, sectors


def load_authors():
    p = os.path.join(OUT_DIR, "authors.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ── helpers ───────────────────────────────────────────────────────────────────
def parse_date(v, field, slug):
    if isinstance(v, date):
        return v
    if isinstance(v, datetime):
        return v.date()
    try:
        return datetime.strptime(str(v).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("[%s] %s must be YYYY-MM-DD, got %r" % (slug, field, v))


def as_list(v):
    if v is None:
        return []
    if isinstance(v, str):
        v = [x.strip() for x in v.split(",")]
    return [str(x).strip() for x in v if str(x).strip()]


def filter_valid(vals, valid, kind, slug, warns):
    out, bad = [], []
    for x in vals:
        (out if x in valid else bad).append(x)
    if bad:
        warns.append("[%s] dropped unknown %s: %s" % (slug, kind, ", ".join(bad)))
    return out


def reading_min(text):
    n = len(re.findall(r"\w+", text))
    return max(1, math.ceil(n / WORDS_PER_MIN)), n


# ── per-file processing ───────────────────────────────────────────────────────
def process(path, keys, authors, seen, warns):
    """Return (meta, body_html) or None to skip. Raises ValueError on hard error."""
    slugs, countries, sectors = keys
    raw = open(path, encoding="utf-8").read()
    m = FM_RE.match(raw)
    if not m:
        raise ValueError("%s: missing YAML front-matter (--- ... ---)" % os.path.basename(path))
    fm = yaml.safe_load(m.group(1)) or {}
    body_md = m.group(2)

    for k in REQUIRED:
        if not fm.get(k):
            raise ValueError("%s: missing required field '%s'" % (os.path.basename(path), k))

    slug = str(fm["slug"]).strip()
    if not SLUG_RE.match(slug):
        raise ValueError("%s: invalid slug %r (kebab-case a-z0-9-)" % (os.path.basename(path), slug))
    if slug in seen:
        raise ValueError("duplicate slug %r (also in %s)" % (slug, seen[slug]))
    seen[slug] = os.path.basename(path)

    typ = str(fm["type"]).strip()
    if typ not in VALID_TYPE:
        raise ValueError("[%s] type must be post|news, got %r" % (slug, typ))
    status = str(fm["status"]).strip()
    if status not in VALID_STATUS:
        raise ValueError("[%s] status must be draft|published, got %r" % (slug, status))

    pub = parse_date(fm["published_at"], "published_at", slug)
    upd = parse_date(fm["updated_at"], "updated_at", slug) if fm.get("updated_at") else pub

    # skip drafts and scheduled (future) posts
    if status != "published":
        print("  skip (draft): %s" % slug)
        return None
    if pub > date.today():
        print("  skip (scheduled %s): %s" % (pub.isoformat(), slug))
        return None

    if typ == "news" and not (fm.get("source_name") and fm.get("source_url")):
        raise ValueError("[%s] type:news requires source_name and source_url" % slug)

    author = str(fm.get("author") or "editorial").strip()
    if authors and author not in authors:
        warns.append("[%s] unknown author %r (not in authors.json)" % (slug, author))

    hero = str(fm.get("hero_image") or "").strip()
    hero_alt = str(fm.get("hero_alt") or "").strip()
    if hero and not hero_alt:
        warns.append("[%s] hero_image without hero_alt" % slug)

    rel_slugs = filter_valid(as_list(fm.get("related_slugs")), slugs, "related_slugs", slug, warns)
    rel_sect = filter_valid(as_list(fm.get("related_sectors")), sectors, "related_sectors", slug, warns)
    rel_cc = filter_valid(as_list(fm.get("related_countries")), countries, "related_countries", slug, warns)

    md = markdown.Markdown(extensions=["extra", "toc", "sane_lists"],
                           extension_configs={"toc": {"permalink": False}})
    body_html = md.convert(body_md)
    rmin, words = reading_min(body_md)

    meta = {
        "slug": slug,
        "title": str(fm["title"]).strip(),
        "dek": str(fm["dek"]).strip(),
        "type": typ,
        "published_at": pub.isoformat(),
        "updated_at": upd.isoformat(),
        "featured": bool(fm.get("featured", False)),
        "author": author,
        "hero_image": hero,
        "hero_alt": hero_alt,
        "hero_credit": str(fm.get("hero_credit") or "").strip(),
        "tags": as_list(fm.get("tags")),
        "related_slugs": rel_slugs,
        "related_sectors": rel_sect,
        "related_countries": rel_cc,
        "reading_min": rmin,
        "word_count": words,
        "toc": md.toc if md.toc.strip() else "",
    }
    if typ == "news":
        meta["source_name"] = str(fm["source_name"]).strip()
        meta["source_url"] = str(fm["source_url"]).strip()
    return meta, body_html


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.isdir(CONTENT_DIR):
        print("No content dir (%s); writing empty index." % CONTENT_DIR)
        with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as f:
            json.dump({"posts": []}, f, ensure_ascii=False, indent=2)
        return 0

    keys = load_valid_keys()
    authors = load_authors()
    files = sorted(f for f in os.listdir(CONTENT_DIR) if f.endswith(".md"))
    print("Found %d markdown file(s) in %s" % (len(files), CONTENT_DIR))

    posts, warns, errors, seen = [], [], [], {}
    for fn in files:
        path = os.path.join(CONTENT_DIR, fn)
        try:
            r = process(path, keys, authors, seen, warns)
        except ValueError as e:
            errors.append(str(e))
            continue
        if r is None:
            continue
        meta, body_html = r
        with open(os.path.join(OUT_DIR, meta["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(body_html)
        posts.append(meta)
        print("  ok: %s (%d words, %d min)" % (meta["slug"], meta["word_count"], meta["reading_min"]))

    # newest first
    posts.sort(key=lambda p: (p["published_at"], p["slug"]), reverse=True)
    with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"posts": posts, "authors": authors}, f, ensure_ascii=False, indent=2)

    print("\nWrote %d published post(s) -> %s" % (len(posts), os.path.join(OUT_DIR, "index.json")))
    for w in warns:
        print("  WARN " + w)
    for e in errors:
        print("  ERROR " + e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
