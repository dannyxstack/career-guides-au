"""
从 v2 站点数据（site/src/data/）生成双语职业分析 Markdown。

- 英文（母本）  -> career-contents/{cc}/{slug}.md
- 中文（TM译文，缺失回退英文） -> career-contents-zh/{cc}/{slug}.md

数据源（与线上站点同源，不依赖数据库）：
  occupations_v2.json        英文母本 + 结构化字段（education/salaries/ratings/ai…）
  occ-detail-v2/{cc}.json    懒加载明细（visa/qualifications/suitability/faqs/growth_areas/ai明细）
  translations-v2/zh-CN.*.json  英文源串 -> 中文 翻译记忆

用法：
  python scripts/gen_career_md.py            # 全量两语言 + 全部 README
  python scripts/gen_career_md.py --cc AU    # 仅某国
  python scripts/gen_career_md.py --lang en  # 仅某语言
"""
import argparse
import glob
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
OUT = {"en": os.path.join(ROOT, "career-contents"),
       "zh": os.path.join(ROOT, "career-contents-zh")}

# ── 国家中英名 + 官方数据来源署名 ─────────────────────────────
COUNTRY = {
    "AU": ("Australia", "澳大利亚", "Jobs and Skills Australia (JSA), ABS, ANZSCO"),
    "NZ": ("New Zealand", "新西兰", "Stats NZ, Careers NZ, ANZSCO"),
    "CA": ("Canada", "加拿大", "Statistics Canada, Job Bank, NOC 2021"),
    "US": ("United States", "美国", "U.S. BLS OEWS, O*NET, SOC"),
    "UK": ("United Kingdom", "英国", "ONS, National Careers Service, SOC 2020"),
    "DE": ("Germany", "德国", "Bundesagentur für Arbeit, Destatis, KldB"),
    "FR": ("France", "法国", "INSEE, France Travail, ROME"),
    "ES": ("Spain", "西班牙", "INE, SEPE, CNO-11"),
    "IT": ("Italy", "意大利", "ISTAT, ISCO-08"),
    "NL": ("Netherlands", "荷兰", "CBS, ISCO-08"),
    "IE": ("Ireland", "爱尔兰", "CSO Ireland, ISCO-08"),
    "JP": ("Japan", "日本", "MHLW / e-Stat, JSCO (LLM→ISCO map)"),
    "KR": ("South Korea", "韩国", "KOSTAT, KECO, KSCO (LLM→ISCO map)"),
    "CH": ("Switzerland", "瑞士", "BFS, ISCO-08"),
}
AI_SOURCE = ("ILO Working Paper 140 (Generative AI exposure index, CC BY 4.0) + "
             "Eloundou et al. \"GPTs are GPTs\" (OpenAI, MIT)")

# ── 评级维度：中英标签 ───────────────────────────────────────
DIM = {
    "learning_difficulty":      ("Learning difficulty", "学习难度"),
    "learning_duration":        ("Learning duration", "学习周期"),
    "certification_difficulty": ("Certification difficulty", "考证难度"),
    "job_demand":               ("Job demand", "职位需求量"),
    "competition":              ("Competition", "竞争度"),
    "work_intensity":           ("Work intensity", "工作强度"),
    "income_level":             ("Income level", "收入水平"),
    "future_prospect":          ("Future prospect", "发展前景"),
    "ai_risk":                  ("AI replacement risk", "AI替代风险"),
    "pr_friendliness":          ("PR friendliness", "PR友好度"),
    "pr_difficulty":            ("PR difficulty", "PR难度"),
}
DIM_ORDER = ["learning_duration", "learning_difficulty", "certification_difficulty",
             "job_demand", "competition", "income_level", "work_intensity",
             "future_prospect", "ai_risk", "pr_friendliness", "pr_difficulty"]

# 0–10 分 → 档位词（中英）
BAND = [
    (2,  ("very low", "很低")), (4, ("low", "较低")), (5, ("medium-low", "中低")),
    (6,  ("medium", "中")), (8, ("medium-high", "中高")), (9, ("high", "较高")),
    (11, ("very high", "很高")),
]

# ── UI 文案（章节标题等），中英两套 ──────────────────────────
S = {
    "en": {
        "analysis": "career analysis", "code": "Occupation code",
        "sec_edu": "1. Education path / duration / cost",
        "sec_qual": "2. Qualifications & licensing",
        "sec_demand": "3. Job demand / competition / intensity",
        "sec_salary": "4. Salary range",
        "sec_trend": "5. Future outlook / AI exposure",
        "sec_visa": "6. Migration pathways / PR",
        "sec_fit": "7. Who is / isn't suited",
        "sec_faq": "8. FAQ",
        "sec_concl": "Quick summary",
        "th_stage": "Stage", "th_dur": "Duration", "th_cost": "Cost",
        "th_qual": "Qualification", "th_issuer": "Issuer", "th_must": "Required", "th_note": "Note",
        "th_exp": "Experience", "th_salary": "Annual salary", "th_visa": "Visa", "th_desc": "Description",
        "th_dim": "Dimension", "th_rating": "Rating",
        "must": "Required", "opt": "Optional",
        "workforce": "National workforce approx.",
        "fit": "Who is suited", "unfit": "Who is not suited",
        "growth": "Key growth areas", "replaced": "Tasks most exposed to AI",
        "augmented": "Where AI augments the role", "moat": "Human moat", "skills": "Skills to build",
        "none": "(no data)", "src": "Data sources",
        "mig0": "**This is a non-skilled-migration occupation.** It is generally not on the "
                "skilled occupation lists and cannot be used for independent skilled migration.",
        "mig2": "**This is a restricted skilled-migration occupation (employer-sponsored / regional "
                "agreements only).** It is not on the independent skilled lists (e.g. 189/190).",
    },
    "zh": {
        "analysis": "职业分析", "code": "职业代码",
        "sec_edu": "1. 教育路径 / 周期 / 费用",
        "sec_qual": "2. 考证难度 / 从业资质",
        "sec_demand": "3. 职位需求量 / 竞争度 / 工作强度",
        "sec_salary": "4. 收入范围",
        "sec_trend": "5. 未来趋势 / AI替代概率",
        "sec_visa": "6. 移民路径 / PR难度",
        "sec_fit": "7. 适合人群 / 不适合人群",
        "sec_faq": "8. FAQ 常见问题",
        "sec_concl": "快速结论",
        "th_stage": "阶段", "th_dur": "周期", "th_cost": "费用",
        "th_qual": "资质", "th_issuer": "发证机构", "th_must": "是否必备", "th_note": "备注",
        "th_exp": "经验水平", "th_salary": "年薪", "th_visa": "签证类别", "th_desc": "说明",
        "th_dim": "维度", "th_rating": "评级",
        "must": "必备", "opt": "可选",
        "workforce": "全国从业人数约",
        "fit": "谁适合", "unfit": "谁不适合",
        "growth": "主要增长方向", "replaced": "最易被 AI 替代的任务",
        "augmented": "AI 增强的环节", "moat": "人类护城河", "skills": "需构建的技能",
        "none": "（暂无数据）", "src": "数据来源",
        "mig0": "**本职业为非技术移民职业。** 通常不在技术移民职业清单上，不能作为独立技术移民提名职业。",
        "mig2": "**本职业为受限技术移民职业（仅雇主担保 / 偏远地区协议）。** 不在独立技术移民清单"
                "（如 189/190）上，可通过雇主担保（482/494）、DAMA 或劳务协议移民，通道受限。",
    },
}


def stars(n):
    v = max(0.0, min(10.0, float(n or 0))) / 2
    r = round(v * 2) / 2
    full = int(r); half = (r - full) == 0.5
    return "★" * full + ("½" if half else "") + "☆" * (5 - full - (1 if half else 0))


def band(n, lang):
    n = float(n or 0)
    for hi, (en, zh) in BAND:
        if n < hi:
            return en if lang == "en" else zh
    return "very high" if lang == "en" else "很高"


def money(v, cur):
    try:
        return f"{cur} {float(v):,.0f}"
    except (TypeError, ValueError):
        return "—"


# ── 加载数据 ─────────────────────────────────────────────────
def load():
    occ = json.load(open(os.path.join(DATA, "occupations_v2.json"), encoding="utf-8"))["occupations"]
    detail = {}
    for p in glob.glob(os.path.join(DATA, "occ-detail-v2", "*.json")):
        cc = os.path.basename(p)[:-5]
        detail[cc] = json.load(open(p, encoding="utf-8"))
    tm = {}
    for p in glob.glob(os.path.join(DATA, "translations-v2", "zh-CN.*.json")):
        tm.update(json.load(open(p, encoding="utf-8")))
    return occ, detail, tm


# ── 单文件渲染 ───────────────────────────────────────────────
def render(o, det, tm, lang):
    def T(s):
        if not s:
            return s
        return s if lang == "en" else tm.get(s, s)

    t = S[lang]
    lp, rp = ("（", "）") if lang == "zh" else (" (", ")")   # 备注括号
    ratings = {r["dimension"]: r for r in o.get("ratings", [])}

    def rate(dim):
        r = ratings.get(dim)
        if not r:
            return ""
        return f"{band(r['stars'], lang)}（{stars(r['stars'])}）" if lang == "zh" \
            else f"{band(r['stars'], lang)} ({stars(r['stars'])})"

    name = T(o["i18n"]["zh-CN"]["name"]) if lang == "zh" else o["name_en"]
    name = name or o["name_en"]
    cc = o["country"]
    cur = o.get("currency") or ""
    en_name, cn = COUNTRY[cc][0], COUNTRY[cc][1]
    country = cn if lang == "zh" else en_name
    L = []

    # 头部
    if lang == "zh":
        title = f"{name}（{o['name_en']}）" if name != o["name_en"] else o["name_en"] + " "
        L.append(f"# {title}{t['analysis']} · {country}")
    else:
        L.append(f"# {name} — {t['analysis']} · {country}")
    L.append("")
    code = o.get("occ_code") or ""
    ctype = o.get("occ_code_type") or ""
    L.append(f"**{t['code']}: {code} ({ctype})**" if code else f"**{t['code']}: —**")
    L.append("")
    summ = T(o["i18n"]["zh-CN"].get("summary"))
    if summ:
        L += [summ, ""]
    mig = int(o.get("is_migration") or 0)
    if mig == 0:
        L += ["> " + t["mig0"], ""]
    elif mig == 2:
        L += ["> " + t["mig2"], ""]

    def sep():
        L.extend(["", "---", ""])

    # 1. 教育
    sep(); L.append(f"## {t['sec_edu']}"); L.append("")
    edu = o.get("education") or []
    if edu:
        L += [f"| {t['th_stage']} | {t['th_dur']} | {t['th_cost']} ({cur}) |", "|---|---|---:|"]
        for e in edu:
            cost = "—"
            if e.get("cost_min"):
                cost = f"${float(e['cost_min']):,.0f}~${float(e['cost_max']):,.0f}"
            note = f"{lp}{T(e['cost_note'])}{rp}" if e.get("cost_note") else ""
            L.append(f"| {T(e.get('stage')) or '—'} | {T(e.get('duration')) or '—'} | {cost}{note} |")
    else:
        L.append(t["none"])

    # 2. 资质
    sep(); L.append(f"## {t['sec_qual']}"); L.append("")
    quals = det.get("qualifications") or []
    if quals:
        L += [f"| {t['th_qual']} | {t['th_issuer']} | {t['th_must']} | {t['th_note']} |", "|---|---|---|---|"]
        for q in quals:
            must = t["must"] if q.get("is_mandatory") or q.get("mandatory") else t["opt"]
            L.append(f"| {T(q.get('name')) or '—'} | {T(q.get('issuer')) or '—'} | {must} | {T(q.get('note')) or '—'} |")
    else:
        L.append(t["none"])

    # 3. 需求
    sep(); L.append(f"## {t['sec_demand']}"); L.append("")
    wf = f"{o['workforce_size']:,}" if o.get("workforce_size") else "—"
    fc = T(o["i18n"]["zh-CN"].get("forecast_note")) or ""
    rd = rate("job_demand")
    line = ""
    if rd:
        line = f"**{DIM['job_demand'][1 if lang=='zh' else 0]}: {rd}.** {t['workforce']} {wf}. {fc}".rstrip()
        L += [line, ""]
    for d in ("competition", "work_intensity"):
        r = rate(d)
        if r:
            L.append(f"**{DIM[d][1 if lang=='zh' else 0]}: {r}.**")

    # 4. 薪资
    sep(); L.append(f"## {t['sec_salary']}"); L.append("")
    sal = o.get("salaries") or []
    if sal:
        L += [f"| {t['th_exp']} | {t['th_salary']} ({cur}) | {t['th_note']} |", "|---|---:|---|"]
        for s in sal:
            lo = f"${float(s['min']):,.0f}" if s.get("min") else "—"
            hi = f"${float(s['max']):,.0f}" if s.get("max") else "—"
            rng = lo if lo == hi else f"{lo}~{hi}"
            L.append(f"| {T(s.get('label')) or '—'} | {rng} | {T(s.get('note')) or '—'} |")
    else:
        L.append(t["none"])

    # 5. 趋势 / AI
    sep(); L.append(f"## {t['sec_trend']}"); L.append("")
    for d in ("future_prospect", "ai_risk"):
        r = rate(d)
        if r:
            L.append(f"**{DIM[d][1 if lang=='zh' else 0]}: {r}.**")
    ai = o.get("ai") or {}
    verdict = T(ai.get("verdict_zh"))
    if verdict:
        L += ["", verdict]
    trend = T(o["i18n"]["zh-CN"].get("trend_summary"))
    if trend:
        L += ["", trend]
    aid = (det.get("ai") or {})
    for key, lab in (("replaced_zh", "replaced"), ("augmented_zh", "augmented"),
                     ("moat_zh", "moat"), ("skills_zh", "skills")):
        val = aid.get(key)
        if isinstance(val, list) and val:
            L += ["", f"**{t[lab]}:**", ""] + [f"- {T(x)}" for x in val]
        elif isinstance(val, str) and val.strip():
            L += ["", f"**{t[lab]}:** {T(val)}"]
    growth = det.get("growth_areas") or []
    if growth:
        L += ["", f"**{t['growth']}:**", ""] + [f"- {T(x)}" for x in growth]

    # 6. 移民
    sep(); L.append(f"## {t['sec_visa']}"); L.append("")
    if mig == 0:
        L.append(t["mig0"])
    elif mig == 2:
        L.append(t["mig2"])
    visa = det.get("visa") or []
    if visa:
        L += ["", f"| {t['th_visa']} | {t['th_desc']} |", "|---|---|"]
        for v in visa:
            label = f"Subclass {v.get('subclass')}" if v.get("subclass") else (v.get("name") or "—")
            if v.get("name") and v.get("subclass"):
                label = f"Subclass {v['subclass']} ({v['name']})"
            L.append(f"| {label} | {T(v.get('desc')) or '—'} |")
    for d in ("pr_friendliness", "pr_difficulty"):
        r = rate(d)
        if r:
            L.append(f"\n**{DIM[d][1 if lang=='zh' else 0]}: {r}.**")

    # 7. 适合人群
    sep(); L.append(f"## {t['sec_fit']}"); L.append("")
    su = det.get("suitability") or {}
    fit = su.get("fit") or []
    unfit = su.get("unfit") or []
    L.append(f"**{t['fit']}**")
    L += [f"- {T(x)}" for x in fit] or ["- —"]
    L += ["", f"**{t['unfit']}**"]
    L += [f"- {T(x)}" for x in unfit] or ["- —"]

    # 8. FAQ
    faqs = det.get("faqs") or []
    if faqs:
        sep(); L.append(f"## {t['sec_faq']}"); L.append("")
        for f in faqs:
            q = T(f.get("question") or f.get("q"))
            a = (T(f.get("answer") or f.get("a")) or "").strip().replace("\n", " ")
            if lang == "zh":
                L += [f"**问：{q}**", f"答：{a}", ""]
            else:
                L += [f"**Q: {q}**", f"A: {a}", ""]

    # 快速结论
    sep(); L.append(f"## {t['sec_concl']}"); L.append("")
    L += [f"| {t['th_dim']} | {t['th_rating']} |", "|---|---|"]
    for d in DIM_ORDER:
        r = ratings.get(d)
        if r:
            lab = DIM[d][1 if lang == "zh" else 0]
            L.append(f"| {lab} | {band(r['stars'], lang)}（{stars(r['stars'])}） |" if lang == "zh"
                     else f"| {lab} | {band(r['stars'], lang)} ({stars(r['stars'])}) |")

    # 数据来源脚注
    sep(); L.append(f"## {t['src']}"); L.append("")
    L.append(f"- {COUNTRY[cc][2]}")
    L.append(f"- AI exposure: {AI_SOURCE}")

    return "\n".join(L).rstrip() + "\n"


# ── README ───────────────────────────────────────────────────
def write_root_readme(lang, per_country):
    t = S[lang]
    p = os.path.join(OUT[lang], "README.md")
    L = []
    if lang == "zh":
        L += [
            "# 全球职业分析 · 中文版",
            "",
            "本目录收录多国职业的深度分析（教育路径、考证、需求、薪资、未来趋势与 AI 替代风险、"
            "移民路径、适合人群、FAQ）。中文为英文母本的译文，缺失处回退英文原文。",
            "",
            "## 数据来源",
            "",
            "- 各国官方统计与职业分类机构（见下表 / 各国 README）。",
            f"- AI 暴露度：{AI_SOURCE}。",
            "",
            "## 国家目录",
            "",
            "| 国家 | 目录 | 职业数 | 官方来源 |",
            "|---|---|---:|---|",
        ]
        for cc, n in per_country:
            L.append(f"| {COUNTRY[cc][1]} | [{cc}/](./{cc.lower()}/README.md) | {n} | {COUNTRY[cc][2]} |")
    else:
        L += [
            "# Global Career Analysis · English",
            "",
            "In-depth occupation guides across multiple countries: education path, licensing, demand, "
            "salary, future outlook & AI exposure, migration pathways, suitability, and FAQ. "
            "English is the master; other languages are translated from it.",
            "",
            "## Data sources",
            "",
            "- Official national statistics & occupation-classification bodies (see table / per-country README).",
            f"- AI exposure: {AI_SOURCE}.",
            "",
            "## Countries",
            "",
            "| Country | Folder | Occupations | Official source |",
            "|---|---|---:|---|",
        ]
        for cc, n in per_country:
            L.append(f"| {COUNTRY[cc][0]} | [{cc}/](./{cc.lower()}/README.md) | {n} | {COUNTRY[cc][2]} |")
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")


def write_country_readme(lang, cc, items):
    # items: list of (category, name, slug)
    p = os.path.join(OUT[lang], cc.lower(), "README.md")
    by_cat = defaultdict(list)
    for cat, name, slug in items:
        by_cat[cat or ("其他" if lang == "zh" else "Other")].append((name, slug))
    L = []
    if lang == "zh":
        L += [f"# {COUNTRY[cc][1]}职业分析索引", "",
              f"本目录收录 {COUNTRY[cc][1]} 共 **{len(items)}** 个职业的深度分析。中文为译文，缺失处回退英文。", "",
              "## 数据来源", "",
              f"- {COUNTRY[cc][2]}", f"- AI 暴露度：{AI_SOURCE}", "",
              "## 职业索引", ""]
    else:
        L += [f"# {COUNTRY[cc][0]} — Occupation Index", "",
              f"In-depth analysis of **{len(items)}** occupations in {COUNTRY[cc][0]}.", "",
              "## Data sources", "",
              f"- {COUNTRY[cc][2]}", f"- AI exposure: {AI_SOURCE}", "",
              "## Occupations", ""]
    for cat in sorted(by_cat):
        L.append(f"### {cat}")
        L.append("")
        for name, slug in sorted(by_cat[cat], key=lambda x: x[0].lower()):
            L.append(f"- [{name}](./{slug}.md)")
        L.append("")
    open(p, "w", encoding="utf-8").write("\n".join(L).rstrip() + "\n")


# ── 主流程 ───────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cc", help="仅某国，如 AU")
    ap.add_argument("--lang", choices=["en", "zh"], help="仅某语言")
    args = ap.parse_args()

    occ, detail, tm = load()
    langs = [args.lang] if args.lang else ["en", "zh"]
    ccs = [args.cc] if args.cc else None

    # 同国内 slug 撞车消歧（不同 occ_code 生成同 slug 时追加代码）；两语言共用同一 slug
    used = defaultdict(set)
    uslug = {}
    for o in sorted(occ, key=lambda x: x["id"]):
        cc = o["country"]; s = o["slug"]
        if s in used[cc]:
            s = f"{o['slug']}-{re.sub(r'[^a-z0-9]+', '-', (o.get('occ_code') or str(o['id'])).lower()).strip('-')}"
        used[cc].add(s)
        uslug[o["id"]] = s

    for lang in langs:
        # 清空旧 md（保留 README，稍后重写）
        for cc in (ccs or list(COUNTRY)):
            d = os.path.join(OUT[lang], cc.lower())
            if os.path.isdir(d):
                for f in glob.glob(os.path.join(d, "*.md")):
                    os.remove(f)

        idx = defaultdict(list)   # cc -> [(cat, name, slug)]
        n = 0
        for o in occ:
            cc = o["country"]
            if cc not in COUNTRY:
                continue
            if ccs and cc not in ccs:
                continue
            det = detail.get(cc, {}).get(str(o["id"])) or detail.get(cc, {}).get(o["id"]) or {}
            md = render(o, det, tm, lang)
            outd = os.path.join(OUT[lang], cc.lower())
            os.makedirs(outd, exist_ok=True)
            slug = uslug[o["id"]]
            open(os.path.join(outd, f"{slug}.md"), "w", encoding="utf-8").write(md)
            name = (tm.get(o["i18n"]["zh-CN"]["name"], o["name_en"]) if lang == "zh" else o["name_en"])
            idx[cc].append((o.get("category") or "", name or o["name_en"], slug))
            n += 1

        per_country = []
        for cc in sorted(idx):
            write_country_readme(lang, cc, idx[cc])
            per_country.append((cc, len(idx[cc])))
        if not ccs:
            write_root_readme(lang, per_country)
        print(f"[{lang}] {n} md 文件, {len(per_country)} 国 README + 根 README")


if __name__ == "__main__":
    main()
