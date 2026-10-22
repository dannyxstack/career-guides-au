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


def utc_today():
    """排期统一用 UTC 日期——与 Go 服务端的发布判定（internal/data/blog.go）和 CI cron 一致。"""
    return datetime.datetime.now(datetime.timezone.utc).date()


# ── 质量闸门：无人值守时替代人工审稿 ────────────────────────────────────────
# 只卡「新生成的草稿」，不进烘焙——早期种子文章只有 ~300 词，放进烘焙会把它们下架。
GATE_MIN_WORDS = 600
GATE_MAX_WORDS = 2500
GATE_MAX_PERCENT_FIGURES = 8        # prompt 要求避免无法核实的精确统计
GATE_BANNED = ("as an ai", "language model", "lorem ipsum", "[insert", "citation needed",
               "todo:", "tbd", "i cannot", "i'm sorry")


def quality_gate(d, typ, rel_slugs):
    """返回不通过的原因列表；空列表 = 通过。"""
    reasons = []
    title = (d.get("title") or "").strip()
    dek = (d.get("dek") or "").strip()
    body = (d.get("body_markdown") or "").strip()
    words = len(re.findall(r"[A-Za-z0-9'’-]+", body))

    if not 10 <= len(title) <= 70:
        reasons.append("title length %d not in 10..70" % len(title))
    if not dek or len(dek) > 300:
        reasons.append("dek missing or > 300 chars")
    if not GATE_MIN_WORDS <= words <= GATE_MAX_WORDS:
        reasons.append("body %d words not in %d..%d" % (words, GATE_MIN_WORDS, GATE_MAX_WORDS))
    if len(re.findall(r"^##\s", body, re.M)) < 2:
        reasons.append("fewer than 2 ## sections")
    if re.search(r"^#\s", body, re.M):
        reasons.append("body contains an H1 (title is separate)")
    low = body.lower()
    hit = [b for b in GATE_BANNED if b in low]
    if hit:
        reasons.append("placeholder / refusal text: %s" % ", ".join(hit))
    if typ == "post" and re.search(r"https?://", body):
        # 分析文不需要外链；无人审稿时 LLM 编造的「来源链接」是最伤可信度的错误。
        reasons.append("external URL in body (likely fabricated citation)")
    pct = len(re.findall(r"\d+(?:\.\d+)?\s?%", body))
    if pct > GATE_MAX_PERCENT_FIGURES:
        reasons.append("%d percentage figures (> %d; unverifiable precise stats)" % (pct, GATE_MAX_PERCENT_FIGURES))
    if not rel_slugs:
        # blog 的价值约八成在内链（docs/blog-plan.md §0），一条有效职业内链都没有就不发。
        reasons.append("no valid related_slugs (internal links)")
    return reasons


def draft_one(topic, typ, notes, keys, authors, source_name="", source_url="",
              slug_override="", force=False, extra_tags=None, status="published",
              publish_on=None, attempts=1, gate=False):
    """Generate one draft. Returns path written, or None if skipped/failed.

    attempts: 生成失败（接口异常 / 空返回 / 未过闸）时的总尝试次数。
    gate:     True 时套用 quality_gate，未通过则重试，最终仍不过就不写文件。
    publish_on: 发布日（date）；None = 今天（UTC）。
    """
    slugs, countries, sectors = keys

    def keep(vals, valid):
        got, bad = [], []
        for x in vals or []:
            x = str(x).strip()
            (got if x in valid else bad).append(x)
        return got, bad

    d = None
    for n in range(1, max(1, attempts) + 1):
        try:
            cand = _deepseek_rest.complete_json(
                SYSTEM, build_prompt(topic, typ, source_name, source_url, notes, sectors, countries))
        except Exception as e:
            # 不再截断：截断曾把「推理模型吃光 max_tokens -> 空返回」伪装成看不懂的 JSON 错误。
            print("  attempt %d/%d: DeepSeek error: %s: %s" % (n, attempts, type(e).__name__, e))
            continue
        if gate:
            rs, _ = keep(cand.get("related_slugs"), slugs)
            reasons = quality_gate(cand, typ, rs)
            if reasons:
                print("  attempt %d/%d: rejected by quality gate: %s" % (n, attempts, "; ".join(reasons)))
                continue
        d = cand
        break
    if d is None:
        print("  FAILED after %d attempt(s): %s" % (attempts, topic[:70]))
        return None

    title = (d.get("title") or topic).strip()
    slug = slug_override.strip() or slugify(d.get("slug") or title)
    if not build_blog.SLUG_RE.match(slug):
        slug = slugify(slug)

    path = os.path.join(build_blog.CONTENT_DIR, slug + ".md")
    if os.path.exists(path) and not force:
        print("  skip (exists): %s" % slug)
        return None

    rel_slugs, bad_slugs = keep(d.get("related_slugs"), slugs)
    rel_sect, bad_sect = keep(d.get("related_sectors"), sectors)
    rel_cc, bad_cc = keep(d.get("related_countries"), countries)

    tags = [str(t).strip() for t in (d.get("tags") or []) if str(t).strip()]
    for t in (extra_tags or []):
        if t not in tags:
            tags.append(t)

    day = (publish_on or utc_today()).isoformat()
    fm = {
        "slug": slug, "title": title, "dek": (d.get("dek") or "").strip(),
        "type": typ, "status": status, "published_at": day, "updated_at": day,
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
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("---\n%s\n---\n\n%s%s\n" % (front, review_block, body))

    print("  draft: %s  publish_on=%s  (related slugs=%d sectors=%d cc=%d)"
          % (slug, day, len(rel_slugs), len(rel_sect), len(rel_cc)))
    for r in review:
        print("    NOTE " + r)
    return path


# ── 排期：读 content/blog 里现有文章的发布日 ─────────────────────────────────
def scan_post_dates():
    """[(slug, status, published_at: date)]，读每篇 .md 的 front-matter。"""
    import glob
    out = []
    for p in glob.glob(os.path.join(build_blog.CONTENT_DIR, "*.md")):
        try:
            with open(p, encoding="utf-8") as fh:
                txt = fh.read()
            fm = yaml.safe_load(txt.split("---", 2)[1]) if txt.startswith("---") else {}
            day = datetime.date.fromisoformat(str(fm.get("published_at"))[:10])
        except Exception:
            continue
        out.append((os.path.splitext(os.path.basename(p))[0], str(fm.get("status", "")).strip(), day))
    return out


def next_publish_slot(posts, cadence_days, today):
    """在最后一篇已发布/已排期文章之后按节奏顺延；断更过久则从今天起补发。"""
    pub = [d for _, st, d in posts if st == "published"]
    if not pub:
        return today
    return max(max(pub) + datetime.timedelta(days=cadence_days), today)


def scheduled_ahead(posts, today):
    """已排期、尚未到发布日的文章数（队列深度）。"""
    return sum(1 for _, st, d in posts if st == "published" and d > today)


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


EXIT_OK, EXIT_FAILED, EXIT_POOL_EXHAUSTED = 0, 1, 3


def save_topic_state(state):
    with open(TOPIC_STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=0, sort_keys=True)


def run_queue(a, keys, authors):
    """无人值守模式：保证始终有 N 篇已排期、未到发布日的文章。

    每天跑一次即可：队列满了就什么都不做（不产生 commit）；某天接口挂了，
    缓冲里还有存货，第二天自动补上，读者看不到断更。
    """
    today = utc_today()
    posts = scan_post_dates()
    have = scheduled_ahead(posts, today)
    need = a.ensure_queue - have
    print("Queue: %d scheduled ahead (target %d), cadence %d days, today %s UTC"
          % (have, a.ensure_queue, a.cadence_days, today))
    if need <= 0:
        print("Queue full -- nothing to draft.")
        return EXIT_OK

    exclude = {t.strip() for t in a.exclude_tags.split(",") if t.strip()}
    state = load_topic_state()
    topics = load_topics(a.from_topics)
    # 无人审稿时绝不复用选题：轮换用完会从头再来，造出近似重复的文章。
    pool = [(g, t) for g, t in pick_topics(topics, len(topics), exclude, state) if t not in state]
    print("Topic pool: %d unused of %d" % (len(pool), len(topics)))

    written, failures = [], 0
    for tag, topic in pool:
        if need <= 0 or failures >= a.max_failures:
            break
        slot = next_publish_slot(posts, a.cadence_days, today)
        print("- [%s] %s  -> %s" % (tag, topic, slot))
        p = draft_one(topic, a.type, a.notes, keys, authors, extra_tags=[tag],
                      status="published", publish_on=slot, attempts=a.attempts, gate=True)
        if not p:
            failures += 1          # 失败的选题不标记已用，留待下次重试
            continue
        written.append(p)
        state[topic] = today.isoformat()
        save_topic_state(state)     # 逐篇落盘，中途崩溃也不会丢状态
        posts.append((os.path.splitext(os.path.basename(p))[0], "published", slot))
        if slot > today:
            need -= 1

    print("\nDrafted %d post(s); queue now %d ahead." % (len(written), scheduled_ahead(posts, today)))
    if need > 0 and not pool[len(written) + failures:] and failures < a.max_failures:
        print("ERROR: topic pool exhausted -- add topics to %s (queue short by %d)." % (a.from_topics, need))
        return EXIT_POOL_EXHAUSTED
    if need > 0:
        print("ERROR: %d draft failure(s); queue short by %d. Will retry on the next run." % (failures, need))
        return EXIT_FAILED
    return EXIT_OK


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
    # —— 定时 / 无人值守 ——
    ap.add_argument("--publish-on", dest="publish_on", default="",
                    help="发布日 YYYY-MM-DD（UTC）；服务端到日子才展示，无需再部署")
    ap.add_argument("--ensure-queue", dest="ensure_queue", type=int, default=0,
                    help="无人值守模式：补足到 N 篇已排期文章（需配合 --from-topics）")
    ap.add_argument("--cadence-days", dest="cadence_days", type=int, default=7)
    ap.add_argument("--max-failures", dest="max_failures", type=int, default=3)
    ap.add_argument("--attempts", type=int, default=3,
                    help="每篇的生成尝试次数（接口异常 / 空返回 / 未过质量闸门都会重试）")
    ap.add_argument("--gate", action="store_true", help="单篇/批量模式也套用质量闸门（队列模式总是套用）")
    ap.add_argument("--model", default=os.environ.get("BLOG_DRAFT_MODEL", "deepseek-chat"),
                    help="起草模型。默认 deepseek-chat：推理模型（如 deepseek-v4-flash）会把 "
                         "max_tokens 花在推理上、偶发返回空正文")
    a = ap.parse_args()

    if not a.topic and not a.from_topics:
        ap.error("provide --topic or --from-topics")
    if a.ensure_queue and not a.from_topics:
        ap.error("--ensure-queue requires --from-topics")
    if a.type == "news" and a.topic and not (a.source_name and a.source_url):
        ap.error("--type news requires --source-name and --source-url")
    publish_on = None
    if a.publish_on:
        try:
            publish_on = datetime.date.fromisoformat(a.publish_on)
        except ValueError:
            ap.error("--publish-on must be YYYY-MM-DD")

    # 只改起草用的模型，不动 .env 里给其它管线用的 DEEPSEEK_MODEL。
    _deepseek_rest.config.DEEPSEEK_MODEL = a.model
    print("Model: %s" % a.model)

    keys = build_blog.load_valid_keys()
    authors = build_blog.load_authors()

    if a.ensure_queue:
        return run_queue(a, keys, authors)

    # single-topic mode
    if a.topic:
        print("Drafting 1 post with DeepSeek …")
        p = draft_one(a.topic, a.type, a.notes, keys, authors,
                      source_name=a.source_name, source_url=a.source_url,
                      slug_override=a.slug, force=a.force, status=a.status,
                      publish_on=publish_on, attempts=a.attempts, gate=a.gate)
        _finish([p] if p else [])
        return EXIT_OK if p else EXIT_FAILED

    # batch/rotation mode
    exclude = {t.strip() for t in a.exclude_tags.split(",") if t.strip()}
    topics = load_topics(a.from_topics)
    state = load_topic_state()
    picks = pick_topics(topics, a.count, exclude, state)
    if not picks:
        print("No eligible topics (after exclude-tags).")
        return EXIT_FAILED
    print("Drafting %d post(s) with DeepSeek (from %d topics, excluding %s) …"
          % (len(picks), len(topics), sorted(exclude) or "none"))

    today = utc_today().isoformat()
    written = []
    for tag, topic in picks:
        print("- [%s] %s" % (tag, topic))
        p = draft_one(topic, a.type, a.notes, keys, authors, extra_tags=[tag], status=a.status,
                      publish_on=publish_on, attempts=a.attempts, gate=a.gate)
        if p:
            written.append(p)
            state[topic] = today          # mark used only on success
    save_topic_state(state)
    _finish(written)
    return EXIT_OK if written else EXIT_FAILED


def _pending_drafts():
    """content/blog 里尚未进 data/blog/index.json 的草稿。

    不限于本次运行——历史上失败重跑、或审校后搁置的草稿会堆在这里，
    下次烘焙时会一并产出。提交清单必须覆盖它们，否则 .md 进了 git 而
    对应的 .html 没进，线上就少文章。
    """
    import glob
    baked = set()
    idx = os.path.join(build_blog.OUT_DIR, "index.json")
    if os.path.exists(idx):
        try:
            with open(idx, encoding="utf-8") as f:
                baked = {p.get("slug") for p in json.load(f).get("posts", [])}
        except Exception:
            pass
    out = []
    for p in sorted(glob.glob(os.path.join(build_blog.CONTENT_DIR, "*.md"))):
        slug = os.path.splitext(os.path.basename(p))[0]
        if slug not in baked:
            out.append((slug, p))
    return out


def _finish(paths):
    """收尾摘要：列出本次产出，以及后续要提交 / 部署的文件。

    blog 是 data/ 里唯一进 git 的部分（aijobrisk-go/.gitignore 的 `!/data/blog/`），
    所以「要提交什么」和「要部署什么」不是同一份清单，分开列，省得每次翻文档。
    """
    n = len(paths)
    print("\nWrote %d draft(s) to %s" % (n, build_blog.CONTENT_DIR))

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def rel(p):
        try:
            r = os.path.relpath(os.path.abspath(p), root)
        except ValueError:          # Windows 跨盘符时 relpath 会抛错，退回绝对路径
            r = os.path.abspath(p)
        return r.replace("\\", "/")

    mine = {os.path.abspath(p) for p in paths}
    pending = _pending_drafts()
    if not pending:
        return

    print("\n" + "=" * 70)
    print("接下来要做的（按顺序）")
    print("=" * 70)

    print("\n[1] 人工审校（事实 / 署名 / 内链）。status 已是 published，")
    print("    发现问题改成 draft，烘焙会自动跳过：")
    for slug, p in pending:
        mark = "本次新增" if os.path.abspath(p) in mine else "之前遗留，未烘焙"
        print("      %-64s  <- %s" % (rel(p), mark))

    print("\n[2] 烘焙（离线，不需要网络）：")
    print("      python scripts/build_blog.py")
    print("    会产出 / 更新：")
    print("      aijobrisk-go/data/blog/index.json")
    for slug, _ in pending:
        print("      aijobrisk-go/data/blog/%s.html" % slug)

    print("\n[3] 提交（正文、烘焙产物、头图、轮换状态都要进 git）：")
    print("      git add aijobrisk-go/content/blog aijobrisk-go/data/blog aijobrisk-go/static/blog scripts/.blog_topics_used.json")
    if len(pending) == 1:
        print('      git commit -m "content(blog): %s"' % pending[0][0])
    else:
        print('      git commit -m "content(blog): %d posts"' % len(pending))

    print("\n[4] 部署 —— push 到 main 即可，不需要 rsync 或重启：")
    print("      git push")
    print("    服务器上的 ops/blog-pull.sh 每 10 分钟同步并热重载（见 deployment.md 第八节）。")
    print("    未来日期的文章会在发布日（UTC）自动出现，当天无需任何操作。")

    print("\n不用管的：")
    print("      aijobrisk-go/upload-data.sh       已排除 blog/，博客只走 git")


if __name__ == "__main__":
    sys.exit(main())
