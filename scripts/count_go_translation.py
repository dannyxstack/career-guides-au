"""统计 aijobrisk-go 站的剩余翻译量（按目标 locale）。不写库、不翻译，只报数。

源串口径 = gen_aijobrisk_tm.site_src_set 的提取逻辑，但 ROOT 指向 aijobrisk-go/data，
即 go 站实际经 Tr() 渲染的全部英文源串（职业名/摘要/薪资 note/教育/资质/签证/FAQ/AI 文案/UI）。
「已译」判定与站点 tr() 一致：translations_v2 里该 locale 有该英文源串（trim 后）的译文即算已译。

输出：全站 + 新增 4 国(BR/CN/IN/MX)子集，各目标 locale 的 缺译条数 / 缺译字符数。
运行：PYTHONIOENCODING=utf-8 python scripts/count_go_translation.py
"""
import os, sys, json, glob, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

GO = os.path.join(os.path.dirname(__file__), "..", "aijobrisk-go", "data")
TARGETS = ["zh-CN", "ja", "es", "pt", "fr"]  # en=母本免翻；zh-CN 即 zh-hans
NEW4 = {"BR", "CN", "IN", "MX"}
NEW25 = {"NO", "SE", "FI", "DK", "IS",
         "BE", "AT", "PL", "PT", "GR", "HU", "CZ", "RO", "LU", "SK", "SI", "HR", "TR",
         "AR", "CL", "MY", "ID", "TH", "VN", "SG"}
_ALPHA = re.compile(r"[A-Za-z]")


def need(s):
    return bool(s and s.strip() and _ALPHA.search(s))


def collect(only_countries=None):
    """收集 go 站渲染源串；only_countries 非空时仅统计这些国家的记录/明细文件。"""
    srcs = set()

    def add(s):
        if need(s):
            srcs.add(s.strip())

    d = json.load(open(os.path.join(GO, "occupations_v2.json"), encoding="utf-8"))
    keep_ids = set()
    for o in d["occupations"]:
        if only_countries and o["country"] not in only_countries:
            continue
        keep_ids.add(o["id"])
        z = o.get("i18n", {}).get("zh-CN", {})
        for k in ("name", "summary", "forecast_note", "trend_summary"):
            add(z.get(k))
        for s in o.get("salaries", []) or []:
            add(s.get("label")); add(s.get("note"))
        lai = o.get("ai") or {}
        add(lai.get("verdict_zh")); add(lai.get("entry_narrowing_zh")); add(lai.get("upgrade_path_zh"))
        for key in ("replaced_zh", "augmented_zh", "moat_zh", "skills_zh"):
            for x in (lai.get(key) or []):
                add(x)
    files = glob.glob(os.path.join(GO, "occ-detail-v2", "*.json"))
    if only_countries:
        files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in only_countries]
    for f in files:
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
    if not only_countries:
        ui = os.path.join(GO, "ui_source_strings.json")
        if os.path.exists(ui):
            for s in json.load(open(ui, encoding="utf-8")):
                add(s)
    return srcs


def have_set(cur, loc):
    cur.execute("SELECT s.src_text FROM translations_v2 t JOIN translation_src_v2 s "
                "ON s.src_hash=t.src_hash WHERE t.locale=%s AND t.text IS NOT NULL AND t.text<>''", (loc,))
    return {(r["src_text"] or "").strip() for r in cur.fetchall()}


def report(name, S, cur):
    tot_chars = sum(len(x) for x in S)
    print(f"\n### {name}：源串 {len(S):,} 条 / {tot_chars:,} 字符")
    print(f"{'locale':<8}{'已译':>10}{'缺译条数':>12}{'缺译字符':>14}{'完成度':>9}")
    for loc in TARGETS:
        have = have_set(cur, loc)
        miss = [x for x in S if x not in have]
        mc = sum(len(x) for x in miss)
        done = (len(S) - len(miss)) / len(S) * 100 if S else 0
        tag = "zh-hans" if loc == "zh-CN" else loc
        print(f"{tag:<8}{len(S)-len(miss):>10,}{len(miss):>12,}{mc:>14,}{done:>8.1f}%")


def main():
    S_all = collect()
    S_new = collect(only_countries=NEW25)
    with get_cursor() as cur:
        report("aijobrisk-go 全站（43 国）", S_all, cur)
        report("本次新增 25 国（北欧5 + 批次20）子集", S_new, cur)


if __name__ == "__main__":
    main()
