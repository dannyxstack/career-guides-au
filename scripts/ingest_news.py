# -*- coding: utf-8 -*-
"""News radar: pull AI feeds, keep only career/job-development items, dedupe, and
emit a dated editorial shortlist for HUMAN topic selection.

This is an INTERNAL editorial aid — NOT a publisher. It stores only title +
short existing summary + link + date (facts/leads, no reproduction), so it stays
clear of the copyright/thin-content rules in blog-plan §8. A human scans the
shortlist, picks 1-2 leads, and writes an ORIGINAL post via draft_blog.py.

Pipeline: feeds (Google News queries + direct) -> parse -> keyword filter
(AI-term AND job-term) -> topic-tag -> dedupe across sources -> drop already-seen
-> write news-radar/{date}.md (+ .json). Keyword-only: no LLM, no API cost.

Usage:
  python scripts/ingest_news.py                 # last 7 days, skip seen
  python scripts/ingest_news.py --days 3
  python scripts/ingest_news.py --all           # ignore seen-state
  python scripts/ingest_news.py --out news-radar --config scripts/news_feeds.yaml
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time

import requests
import yaml
import feedparser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
UA = "Mozilla/5.0 (aijobrisk news-radar; +https://aijobrisk.com)"
SEEN_PATH = os.path.join(HERE, ".news_seen.json")

# —— relevance keywords ——
AI_TERMS = ["ai", "artificial intelligence", "generative ai", "genai", "gpt",
            "chatgpt", "llm", "large language model", "machine learning",
            "automation", "automate", "copilot", "ai agent"]
JOB_TERMS = ["job", "jobs", "layoff", "laid off", "job cut", "hiring", "hire",
             "employ", "workforce", "worker", "career", "occupation", "wage",
             "salary", "reskill", "upskill", "skills", "labor", "labour",
             "unemploy", "recruit", "headcount", "redundan", "staff"]
# topic tags (a matched term -> tag); first-match order matters for primary tag.
TAG_RULES = [
    ("layoffs", ["layoff", "laid off", "job cut", "headcount", "redundan", "downsiz", "job losses"]),
    ("hiring", ["hiring", "hire ", "recruit", "job opening", "vacanc", "new roles"]),
    ("wages", ["wage", "salary", "pay ", "compensation"]),
    ("policy", ["regulat", "policy", "legislat", "union", " act ", "government", "eu ai"]),
    ("research", ["study", "report", "research", "survey", "paper", "economist", "index"]),
    ("tools", ["launch", "release", "model", "copilot", "chatgpt", "agent"]),
]


def gnews_url(q):
    return "https://news.google.com/rss/search?q=" + requests.utils.quote(q) + "&hl=en-US&gl=US&ceid=US:en"


def fetch(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=25)
    r.raise_for_status()
    return feedparser.parse(r.content)


import html as _html


def strip_html(s):
    return _html.unescape(re.sub(r"<[^>]+>", "", s or "")).replace("\xa0", " ").strip()


def useful_summary(title, summary):
    """Google News summaries are usually just the title + source — drop those."""
    if not summary:
        return ""
    if norm_title(summary).startswith(norm_title(title)[:40]):
        return ""
    return summary


def norm_title(t):
    t = re.sub(r"\s+-\s+[^-]+$", "", t or "")      # drop " - Source" suffix (Google News)
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def hits(text, terms):
    return [w for w in terms if w in text]


def primary_tag(text):
    for tag, kws in TAG_RULES:
        if any(k in text for k in kws):
            return tag
    return "general"


def entry_date(e):
    for k in ("published_parsed", "updated_parsed"):
        v = e.get(k)
        if v:
            return dt.date(*v[:3])
    return None


def load_seen():
    if os.path.exists(SEEN_PATH):
        try:
            return json.load(open(SEEN_PATH, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_seen(seen):
    # prune entries older than 60 days
    cutoff = (dt.date.today() - dt.timedelta(days=60)).isoformat()
    seen = {k: v for k, v in seen.items() if v >= cutoff}
    json.dump(seen, open(SEEN_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


def jaccard(a, b):
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "news_feeds.yaml"))
    ap.add_argument("--days", type=int, default=7, help="only items within N days")
    ap.add_argument("--out", default=os.path.join(ROOT, "news-radar"))
    ap.add_argument("--all", action="store_true", help="ignore seen-state (show everything)")
    a = ap.parse_args()

    cfg = yaml.safe_load(open(a.config, encoding="utf-8"))
    sources = []
    for q in cfg.get("google_news", []):
        sources.append({"name": "GoogleNews: " + q, "url": gnews_url(q), "tier": "aggregator"})
    for d in cfg.get("direct", []):
        sources.append({"name": d["name"], "url": d["url"], "tier": d.get("tier", "media")})

    since = dt.date.today() - dt.timedelta(days=a.days)
    seen = load_seen()
    items, dropped_seen, scanned = [], 0, 0

    for s in sources:
        try:
            feed = fetch(s["url"])
        except Exception as e:
            print("  WARN fetch %s: %s" % (s["name"], str(e)[:70]))
            continue
        for e in feed.entries:
            scanned += 1
            title = strip_html(e.get("title", ""))
            summary = useful_summary(title, strip_html(e.get("summary", ""))[:300])
            link = e.get("link", "")
            d = entry_date(e)
            if d and d < since:
                continue
            blob = (title + " " + summary).lower()
            ai_h = hits(blob, AI_TERMS)
            job_h = hits(blob, JOB_TERMS)
            if not (ai_h and job_h):            # relevance: AI ∧ job
                continue
            key = norm_title(title)
            if not key:
                continue
            if not a.all and key in seen:
                dropped_seen += 1
                continue
            items.append({
                "title": title, "summary": summary, "link": link,
                "date": d.isoformat() if d else "", "source": s["name"],
                "tier": s["tier"], "tag": primary_tag(blob),
                "matched": sorted(set(job_h))[:6], "key": key,
            })
        time.sleep(0.3)

    # dedupe: cluster by normalized title, then merge near-duplicates (Jaccard>=0.75)
    clusters = []
    for it in sorted(items, key=lambda x: x["date"], reverse=True):
        placed = False
        for c in clusters:
            if it["key"] == c["rep"]["key"] or jaccard(it["key"], c["rep"]["key"]) >= 0.75:
                c["dupes"] += 1
                c["sources"].add(it["source"])
                # prefer a 'deep' tier representative
                if it["tier"] == "deep" and c["rep"]["tier"] != "deep":
                    it2 = dict(it); it2["dupes"] = c["dupes"]; it2["sources"] = c["sources"]
                    c["rep"] = it
                placed = True
                break
        if not placed:
            clusters.append({"rep": it, "dupes": 0, "sources": {it["source"]}})

    # order: by tag priority then date
    tag_order = {t: i for i, (t, _) in enumerate(TAG_RULES)}
    clusters.sort(key=lambda c: (tag_order.get(c["rep"]["tag"], 99), c["rep"]["date"]), reverse=False)
    clusters.sort(key=lambda c: c["rep"]["date"], reverse=True)

    # write digest
    os.makedirs(a.out, exist_ok=True)
    today = dt.date.today().isoformat()
    md_path = os.path.join(a.out, "%s.md" % today)
    json_path = os.path.join(a.out, "%s.json" % today)

    by_tag = {}
    for c in clusters:
        by_tag.setdefault(c["rep"]["tag"], []).append(c)

    lines = ["# News radar — %s" % today,
             "",
             "_Internal editorial shortlist (leads only). Pick 1-2, then write an original post via `draft_blog.py`._",
             "",
             "Sources: %d · scanned %d entries · %d relevant (deduped to %d) · %d already-seen skipped · window %d days"
             % (len(sources), scanned, len(items), len(clusters), dropped_seen, a.days),
             ""]
    tag_names = [t for t, _ in TAG_RULES] + ["general"]
    for tag in tag_names:
        cl = by_tag.get(tag)
        if not cl:
            continue
        lines.append("## %s (%d)" % (tag, len(cl)))
        for c in cl:
            r = c["rep"]
            extra = ""
            if c["dupes"]:
                extra = " · +%d more source(s)" % c["dupes"]
            tier = " ⭐" if r["tier"] == "deep" else ""
            lines.append("- **%s**%s" % (r["title"], tier))
            lines.append("  %s · %s%s" % (r["date"] or "?", r["source"], extra))
            if r["summary"]:
                lines.append("  > %s" % r["summary"][:220])
            lines.append("  %s" % r["link"])
            lines.append("")
        lines.append("")

    open(md_path, "w", encoding="utf-8").write("\n".join(lines))
    json.dump([{k: (sorted(c["sources"]) if k == "sources" else v)
                for k, v in {**c["rep"], "dupes": c["dupes"], "sources": c["sources"]}.items()}
               for c in clusters],
              open(json_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # update seen-state with everything surfaced
    if not a.all:
        for c in clusters:
            seen[c["rep"]["key"]] = today
        save_seen(seen)

    print("Scanned %d entries from %d sources; %d relevant -> %d after dedupe (%d seen skipped)."
          % (scanned, len(sources), len(items), len(clusters), dropped_seen))
    print("Digest: %s" % md_path)
    print("JSON  : %s" % json_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
