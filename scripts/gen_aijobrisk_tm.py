"""用 DB 已有翻译（translations_v2）为 aijobrisk 站生成 translations-v2 分片。
不调用任何翻译 API：仅导出 DB 现有译文。仅收录 aijobrisk 站实际渲染的源串，
按 md5(源串)%N 分片，键为英文源串 -> 目标语译文，供 data.ts 的 tr() 消费。

用法：PYTHONIOENCODING=utf-8 python scripts/gen_aijobrisk_tm.py
"""
import os, sys, json, glob, re, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

ROOT = os.path.join(os.path.dirname(__file__), "..", "aijobrisk", "src", "data")
OUT = os.path.join(ROOT, "translations-v2")
N_SHARDS = 8
# 站点显示语 -> DB locale（ko 在 i18n.ts 映射到 en，不生成；fr 已有完整引用集译文）
LOCALES = ["es", "pt", "fr", "ja", "de", "zh-CN"]

_HAS_ALPHA = re.compile(r"[A-Za-z]")


def need(s):
    return bool(s and s.strip() and _HAS_ALPHA.search(s))


def site_src_set():
    """收集 aijobrisk 站实际经 tr() 渲染的英文源串（trim 后）。"""
    srcs = set()

    def add(s):
        if need(s):
            srcs.add(s.strip())

    d = json.load(open(os.path.join(ROOT, "occupations_v2.json"), encoding="utf-8"))
    for o in d["occupations"]:
        z = o.get("i18n", {}).get("zh-CN", {})
        for k in ("name", "summary", "forecast_note", "trend_summary"):
            add(z.get(k))
        for s in o.get("salaries", []) or []:
            add(s.get("label")); add(s.get("note"))
        # lean 的 AI 文案（verdict_zh 等在 lean，不在 detail）
        lai = o.get("ai") or {}
        add(lai.get("verdict_zh")); add(lai.get("entry_narrowing_zh")); add(lai.get("upgrade_path_zh"))
        for key in ("replaced_zh", "augmented_zh", "moat_zh", "skills_zh"):
            for x in (lai.get(key) or []):
                add(x)
    for f in glob.glob(os.path.join(ROOT, "occ-detail-v2", "*.json")):
        for _, det in json.load(open(f, encoding="utf-8")).items():
            for e in det.get("education", []) or []:
                add(e.get("stage")); add(e.get("duration")); add(e.get("cost_note"))
            for q in det.get("qualifications", []) or []:
                add(q.get("name")); add(q.get("issuer")); add(q.get("note"))
            for v in det.get("visa", []) or []:
                add(v.get("name")); add(v.get("desc"))
            su = det.get("suitability") or {}
            for x in (su.get("fit") or []) + (su.get("unfit") or []):
                add(x)
            for f2 in det.get("faqs", []) or []:
                add(f2.get("question")); add(f2.get("answer"))
            ai = det.get("ai") or {}
            add(ai.get("verdict_zh")); add(ai.get("entry_narrowing_zh")); add(ai.get("upgrade_path_zh"))
            for key in ("replaced_zh", "augmented_zh", "moat_zh", "skills_zh"):
                for x in (ai.get(key) or []):
                    add(x)
            for ds in (ai.get("disruptors") or []):
                add(ds.get("summary")); add(ds.get("scope"))
    # 页面 UI 源串（tr('字面量')，见 collect_ui_strings.py）
    ui_path = os.path.join(ROOT, "ui_source_strings.json")
    if os.path.exists(ui_path):
        for s in json.load(open(ui_path, encoding="utf-8")):
            add(s)
    return srcs


def main():
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "*.json")):
        os.remove(old)

    site = site_src_set()
    print(f"[gen-tm] 站点源串 {len(site):,} 条")

    with get_cursor() as cur:
        for loc in LOCALES:
            cur.execute(
                "SELECT s.src_text, t.text FROM translations_v2 t "
                "JOIN translation_src_v2 s ON s.src_hash=t.src_hash WHERE t.locale=%s", (loc,))
            shards = [dict() for _ in range(N_SHARDS)]
            kept = 0
            for r in cur.fetchall():
                src = (r["src_text"] or "").strip()
                txt = r["text"]
                if not src or not txt or src not in site:
                    continue
                h = int(hashlib.md5(src.encode("utf-8")).hexdigest(), 16) % N_SHARDS
                shards[h][src] = txt
                kept += 1
            for i, sh in enumerate(shards):
                with open(os.path.join(OUT, f"{loc}.{i}.json"), "w", encoding="utf-8") as fp:
                    json.dump(sh, fp, ensure_ascii=False)
            print(f"[gen-tm] {loc:<6} {kept:,} 条 -> {loc}.0..{N_SHARDS-1}.json")


if __name__ == "__main__":
    main()
