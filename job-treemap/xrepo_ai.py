# -*- coding: utf-8 -*-
"""Cross-repo AI enrichment for job-treemap country reports.

job-treemap's own per-country data.json carries risk/pay/workforce/loss but
NOT the rich AI narrative. That lives in the aijobrisk-go dataset:
  - tasks AI is likely to automate   (replaced)   -> PDF ch.11
  - human moat / what stays human    (moat)        -> PDF ch.12
  - adjacent, more-resilient roles   (adjacent)    -> PDF ch.13

Join key: `slug` within a country (100% hit on AU); the AI block is an
occupation-intrinsic characteristic shared across countries for the same
occupation code, so it is not country-specific by design.

Field values are English master despite the historical *_zh field names.
Reads ../aijobrisk-go/data (local runtime data, gitignored) — confirmed
present on the build machine.
"""
import json
import os
import functools

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GO_DATA = os.path.join(REPO, "aijobrisk-go", "data")


@functools.lru_cache(maxsize=1)
def _lean():
    """occupations_v2.json record list (dict-wrapped under 'master')."""
    p = os.path.join(GO_DATA, "occupations_v2.json")
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, list):
        return d
    return d.get("occupations") or next(
        v for v in d.values() if isinstance(v, list))


@functools.lru_cache(maxsize=None)
def _detail(cc):
    """occ-detail-v2/{cc}.json: id(str) -> {..., ai:{...}}."""
    p = os.path.join(GO_DATA, "occ-detail-v2", f"{cc}.json")
    if not os.path.exists(p):
        return {}
    return json.load(open(p, encoding="utf-8"))


def _norm(ai):
    return {
        "replaced": ai.get("replaced_zh") or [],
        "augmented": ai.get("augmented_zh") or [],
        "moat": ai.get("moat_zh") or [],
        "skills": ai.get("skills_zh") or [],
        "adjacent": ai.get("adjacent") or [],
    }


@functools.lru_cache(maxsize=None)
def ai_index_for(cc):
    """slug -> normalised rich AI block for country cc (empty if unavailable)."""
    detail = _detail(cc)
    out = {}
    for r in _lean():
        if r.get("country") != cc:
            continue
        node = detail.get(str(r.get("id")))
        if not isinstance(node, dict):
            continue
        ai = node.get("ai")
        if not ai:
            continue
        out[r.get("slug")] = _norm(ai)
    return out


def coverage(cc, slugs):
    """(hit, total) — how many of the given slugs resolve to an AI block."""
    idx = ai_index_for(cc)
    hit = sum(1 for s in slugs if idx.get(s))
    return hit, len(slugs)


if __name__ == "__main__":
    import sys
    cc = sys.argv[1] if len(sys.argv) > 1 else "AU"
    idx = ai_index_for(cc)
    print(f"[{cc}] slugs with AI block: {len(idx)}")
    k = next(iter(idx))
    print("sample slug:", k)
    print(json.dumps(idx[k], ensure_ascii=False, indent=2)[:600])
