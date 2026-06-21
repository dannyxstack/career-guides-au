"""
从数据库读取职业数据，按 rules.md 规范生成 Markdown 文件（通用版，不含任何单职业硬编码）。

调用方式：
    from pipeline.generators.md_generator import generate_md
    path = generate_md("341111", locale="zh-CN")

输出：career-contents/au/{英文名slug}.md
"""

import json
import re
from pathlib import Path
from db.connection import get_cursor

OUTPUT_DIR = Path(__file__).parent.parent.parent / "career-contents" / "au"

# 评级维度 → 中文标签（用于显示）
DIMENSION_LABEL = {
    "learning_difficulty":      "学习难度",
    "learning_duration":        "学习周期",
    "certification_difficulty": "考证难度",
    "job_demand":               "职位需求量",
    "competition":              "竞争度",
    "work_intensity":           "工作强度",
    "income_level":             "收入水平",
    "future_prospect":          "发展前景",
    "ai_risk":                  "AI替代风险",
    "pr_friendliness":          "PR友好度",
    "pr_difficulty":            "PR难度",
}


def _stars(n) -> str:
    """10 分制数值 → 5 颗星（÷2 取最近半星，半星用 ½）。"""
    v = max(0.0, min(10.0, float(n or 0))) / 2     # 0..5
    r = round(v * 2) / 2                            # 取最近半星
    full = int(r); half = (r - full) == 0.5
    return "★" * full + ("½" if half else "") + "☆" * (5 - full - (1 if half else 0))


def _slug(name: str) -> str:
    """英文名 → slug：小写，/()[] 换空格，删非字母数字，空格合并为 -。见 rules.md。"""
    s = re.sub(r"[/()\[\]]", " ", (name or "occ").lower())
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", "-", s.strip()) or "occ"


# 国家码 -> 中文名（用于 markdown 标题与正文）
COUNTRY_CN = {"AU": "澳大利亚", "NZ": "新西兰", "CA": "加拿大", "US": "美国", "GB": "英国"}


def _fetch_occupation(cur, anzsco_code: str, country: str = None, occ_code: str = None) -> dict:
    # occ_code 用于消歧（同一 anzsco_code 下多个职业，如 Yoga 与 Fitness 共用 452111）
    if occ_code:
        cur.execute("SELECT * FROM occupations WHERE occ_code=%s AND country_code=%s", (occ_code, country or "AU"))
    elif country:
        cur.execute("SELECT * FROM occupations WHERE anzsco_code=%s AND country_code=%s", (anzsco_code, country))
    else:
        cur.execute("SELECT * FROM occupations WHERE anzsco_code=%s", (anzsco_code,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"职业 anzsco_code={anzsco_code} occ_code={occ_code} 不存在")
    return row


def _fetch_i18n(cur, occ_id: int, locale: str) -> dict:
    cur.execute(
        "SELECT * FROM occupations_i18n WHERE occupation_id=%s AND locale=%s",
        (occ_id, locale),
    )
    return cur.fetchone() or {}


def _fetch_ratings(cur, occ_id: int) -> dict:
    cur.execute(
        "SELECT dimension, label_zh, stars FROM occupation_ratings WHERE occupation_id=%s",
        (occ_id,),
    )
    return {r["dimension"]: r for r in cur.fetchall()}


def _fetch_table(cur, table: str, occ_id: int, order: str = "sort_order") -> list:
    cur.execute(f"SELECT * FROM {table} WHERE occupation_id=%s ORDER BY {order}", (occ_id,))
    return cur.fetchall()


def _r(ratings: dict, dim: str) -> str:
    """返回 '中高（★★★★☆）' 格式字符串，找不到返回空字符串。"""
    r = ratings.get(dim)
    if not r:
        return ""
    return f"{r['label_zh']}（{_stars(r['stars'])}）"


# ─────────────────────────────────────────────────────────────
# 各 Section 生成函数（通用，结论句由数据驱动，不含单职业硬编码）
# ─────────────────────────────────────────────────────────────

def _sec_education(rows: list, ratings: dict) -> str:
    lines = ["## 1. 教育路径 / 周期 / 费用", ""]
    r = _r(ratings, "learning_difficulty")
    if r:
        lines.append(f"**学习难度：{r}。**")
        lines.append("")
    if rows:
        lines += ["| 阶段 | 周期 | 费用（AUD） |", "|---|---|---:|"]
        for row in rows:
            cost = f"${row['cost_min']:,.0f}~${row['cost_max']:,.0f}" if row.get("cost_min") else "—"
            note = f"（{row['cost_note']}）" if row.get("cost_note") else ""
            lines.append(f"| {row['stage']} | {row['duration'] or '—'} | {cost}{note} |")
    else:
        lines.append("（暂无教育路径数据）")
    return "\n".join(lines)


def _sec_qualifications(rows: list, ratings: dict) -> str:
    lines = ["## 2. 考证难度 / 从业资质", ""]
    r = _r(ratings, "certification_difficulty")
    if r:
        lines.append(f"**考证难度：{r}。**")
        lines.append("")
    if rows:
        lines += ["| 资质 | 发证机构 | 是否必备 | 备注 |", "|---|---|---|---|"]
        for row in rows:
            mand = "必备" if row.get("is_mandatory") else "可选"
            lines.append(f"| {row['qual_name']} | {row['issuer'] or '—'} | {mand} | {row['note'] or '—'} |")
    else:
        lines.append("（暂无从业资质数据）")
    return "\n".join(lines)


def _sec_demand(occ: dict, listings: list, ratings: dict, i18n: dict) -> str:
    lines = ["## 3. 职位需求量 / 竞争度 / 工作强度", ""]
    r_demand = _r(ratings, "job_demand")
    workforce = f"{occ['workforce_size']:,}" if occ.get("workforce_size") else "—"
    forecast = i18n.get("forecast_note", "") or ""
    if r_demand:
        lines.append(f"**职位需求量：{r_demand}。** 全国从业人数约 {workforce}。" + forecast)
        lines.append("")
    if listings:
        lines += ["| 平台 | 实时挂牌量（约） | 备注 |", "|---|---:|---|"]
        for jl in listings:
            count = f"{jl['count_min']:,}~{jl['count_max']:,} 个" if jl.get("count_min") else "—"
            lines.append(f"| {jl['platform']} | {count} | {jl['note'] or '—'} |")
        lines.append("")
    r_comp = _r(ratings, "competition")
    r_work = _r(ratings, "work_intensity")
    if r_comp:
        lines.append(f"**竞争度：{r_comp}。**")
    if r_work:
        lines.append(f"**工作强度：{r_work}。**")
    return "\n".join(lines).rstrip()


def _sec_salaries(rows: list, currency: str = "AUD") -> str:
    lines = ["## 4. 收入范围（学徒 / 中级 / 资深）", "",
             f"| 经验水平 | 年薪（{currency}） | 备注 |", "|---|---:|---|"]
    if not rows:
        return "## 4. 收入范围（学徒 / 中级 / 资深）\n\n（暂无收入数据）"
    for row in rows:
        lo = f"${row['salary_min']:,.0f}" if row.get("salary_min") else "—"
        hi = f"${row['salary_max']:,.0f}" if row.get("salary_max") else "—"
        lines.append(f"| {row['experience']} | {lo}~{hi} | {row['salary_note'] or '—'} |")
    return "\n".join(lines)


def _sec_trends(occ: dict, i18n: dict, ratings: dict) -> str:
    lines = ["## 5. 未来趋势 / AI替代概率", ""]
    r_fp = _r(ratings, "future_prospect")
    r_ai = _r(ratings, "ai_risk")
    trend = i18n.get("trend_summary", "") or ""
    if r_fp:
        lines.append(f"**发展前景：{r_fp}。** {trend}".rstrip())
    if r_ai:
        lines.append(f"**AI替代风险：{r_ai}。**")
    growth = occ.get("growth_areas")
    if growth:
        areas = json.loads(growth) if isinstance(growth, str) else growth
        if areas:
            lines += ["", "主要增长方向：", ""]
            lines += [f"- {a}" for a in areas]
    return "\n".join(lines)


def _sec_visa(rows: list, ratings: dict, mig: int) -> str:
    """mig: 0=非技术移民；1=可直接技术移民(189/190/491)；2=受限(仅雇主担保/DAMA等)。"""
    lines = ["## 6. 移民路径 / PR难度", ""]
    if mig == 0:
        lines.append(
            "**本职业为非技术移民职业。** 通常不在澳洲技术移民职业清单"
            "（MLTSSL / STSOL / CSOL）上，不能作为独立的技术移民或雇主担保提名职业。"
            "如以移民为目标，建议考虑清单上的相关职业，或通过学生、毕业生工作、"
            "家庭团聚等其他签证类别。具体以 Department of Home Affairs 最新规定为准。"
        )
        if rows:
            lines += ["", "| 签证类别 | 说明 |", "|---|---|"]
            for row in rows:
                label = (f"Subclass {row['visa_subclass']}（{row['visa_name']}）"
                         if row.get("visa_name") else f"Subclass {row['visa_subclass']}")
                lines.append(f"| {label} | {row['description'] or '—'} |")
        return "\n".join(lines)

    if mig == 2:
        lines.append(
            "**本职业为受限技术移民职业（仅雇主担保 / DAMA）。** 不在独立技术移民清单"
            "（189 / 190 / 491）上，无法直接申请普通技术移民；但可通过雇主担保"
            "（482 / 494）、偏远地区指定移民协议（DAMA）或劳务协议等通道移民——"
            "通道与名额受限，具体以 Department of Home Affairs 最新规定及 CSOL 清单为准。"
        )

    r_pr = _r(ratings, "pr_friendliness")
    if r_pr:
        lines.append(f"**PR友好度：{r_pr}。** 签证路径需按具体职责匹配对应 ANZSCO，"
                     "并以 Department of Home Affairs 最新职业清单及相关评估机构评估结果为准。")
    lines += ["", "| 签证类别 | 说明 |", "|---|---|"]
    for row in rows:
        label = (f"Subclass {row['visa_subclass']}（{row['visa_name']}）"
                 if row.get("visa_name") else f"Subclass {row['visa_subclass']}")
        lines.append(f"| {label} | {row['description'] or '—'} |")
    lines.append("")
    r_diff = _r(ratings, "pr_difficulty")
    if r_diff:
        lines.append(f"**PR难度：{r_diff}。**")
    return "\n".join(lines).rstrip()


def _sec_suitability(fit: list, unfit: list, name_zh: str) -> str:
    lines = ["## 7. 适合人群 / 不适合人群", "", f"**谁适合学{name_zh}？**"]
    lines += [f"- {item['item']}" for item in fit] or ["- —"]
    lines += ["", f"**谁不适合学{name_zh}？**"]
    lines += [f"- {item['item']}" for item in unfit] or ["- —"]
    return "\n".join(lines)


def _sec_sources(rows: list) -> str:
    lines = ["## 8. 数据来源", "", "| 来源 | 内容 |", "|---|---|"]
    for row in rows:
        lines.append(f"| {row['source_name']} | {row['content'] or '—'} |")
    if not rows:
        lines.append("| — | — |")
    return "\n".join(lines)


def _sec_conclusion(ratings: dict) -> str:
    order = [
        "learning_duration", "learning_difficulty", "certification_difficulty",
        "job_demand", "competition", "income_level",
        "work_intensity", "future_prospect", "ai_risk",
        "pr_friendliness", "pr_difficulty",
    ]
    lines = ["## 快速结论", "", "| 维度 | 评级 |", "|---|---|"]
    for dim in order:
        r = ratings.get(dim)
        if r:
            lines.append(f"| {DIMENSION_LABEL.get(dim, dim)} | {r['label_zh']}（{_stars(r['stars'])}） |")
    return "\n".join(lines)


def _sec_faq(faqs: list) -> str:
    lines = ["## 9. FAQ 常见问题", ""]
    for row in faqs:
        q = row.get("question", "")
        a = (row.get("answer") or "").strip().replace("\n", " ")
        lines += [f"**问：{q}**", f"答：{a}", ""]
    return "\n".join(lines).rstrip()


# ─────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────

def generate_md(anzsco_code: str, locale: str = "zh-CN", country: str = "AU", occ_code: str = None) -> Path:
    """从数据库读取职业数据，生成 career-contents/{country}/{slug}.md，返回文件路径。
    occ_code：同一 anzsco_code 下多职业时用于消歧。"""
    with get_cursor() as cur:
        occ = _fetch_occupation(cur, anzsco_code, country, occ_code)
        occ_id = occ["id"]
        i18n = _fetch_i18n(cur, occ_id, locale)
        en = _fetch_i18n(cur, occ_id, "en")
        ratings = _fetch_ratings(cur, occ_id)

        edu = _fetch_table(cur, "occupation_education", occ_id)
        quals = _fetch_table(cur, "occupation_qualifications", occ_id)
        listings = _fetch_table(cur, "occupation_job_listings", occ_id, order="id")
        salaries = _fetch_table(cur, "occupation_salaries", occ_id)
        visas = _fetch_table(cur, "occupation_visa_pathways", occ_id)
        sources = _fetch_table(cur, "occupation_sources", occ_id, order="id")

        cur.execute("SELECT * FROM occupation_suitability WHERE occupation_id=%s AND type='fit' ORDER BY sort_order", (occ_id,))
        fit = cur.fetchall()
        cur.execute("SELECT * FROM occupation_suitability WHERE occupation_id=%s AND type='unfit' ORDER BY sort_order", (occ_id,))
        unfit = cur.fetchall()

        cur.execute(
            "SELECT f.faq_type, fi.question, fi.answer FROM occupation_faqs f "
            "JOIN occupation_faqs_i18n fi ON fi.faq_id = f.id AND fi.locale = %s "
            "WHERE f.occupation_id = %s ORDER BY f.sort_order",
            (locale, occ_id),
        )
        faqs = cur.fetchall()

    name_zh = i18n.get("name", occ["anzsco_title"])
    en_name = en.get("name") or occ["anzsco_title"]
    summary = i18n.get("summary", "") or ""
    mig = int(occ.get("is_migration", 1) or 0)   # 0=非移民 1=可直接技术移民 2=受限
    is_migration = mig != 0
    cc = occ.get("country_code") or country or "AU"
    country_cn = COUNTRY_CN.get(cc, cc)
    currency = occ.get("currency") or "AUD"

    code = occ.get("anzsco_code") or ""
    if code:
        code_line = f"**职业代码：{code} – {occ['anzsco_title']}。**"
    else:
        code_line = "**职业代码：暂无（非技术移民职业，无移民局指定代码）。**"

    head = [
        f"# {name_zh}（{occ['anzsco_title']}）职业分析 · {country_cn}",
        "",
        code_line,
        "",
        summary,
    ]
    if mig == 0:
        head += ["", f"> 注：本职业为**非技术移民职业**，不在{country_cn}技术移民职业清单上，以下内容主要面向本地就业与职业了解。"]
    elif mig == 2:
        head += ["", f"> 注：本职业为**受限技术移民职业**，不在{country_cn}独立技术移民清单（189/190）上，"
                     "但可通过雇主担保（482/494）、偏远地区指定协议（DAMA）或劳务协议移民——移民通道受限。"]

    if mig == 1:
        tail = (f"{name_zh}的移民路径与薪资见上表；建议结合自身背景与最新职业清单，"
                "提前规划技能评估与签证方案。")
    elif mig == 2:
        tail = (f"{name_zh}为受限技术移民职业，普通技术移民通道不可用；如以移民为目标，"
                "需重点考察雇主担保（482/494）与 DAMA / 劳务协议，并结合最新 CSOL 清单评估可行性。")
    else:
        tail = (f"{name_zh}属于非技术移民职业，更多面向本地就业；如以移民为目标，"
                "建议优先考虑技术移民清单上的相关职业。")

    sep = ["", "---", ""]
    sections = (
        head + sep
        + [_sec_education(edu, ratings)] + sep
        + [_sec_qualifications(quals, ratings)] + sep
        + [_sec_demand(occ, listings, ratings, i18n)] + sep
        + [_sec_salaries(salaries, currency)] + sep
        + [_sec_trends(occ, i18n, ratings)] + sep
        + [_sec_visa(visas, ratings, mig)] + sep
        + [_sec_suitability(fit, unfit, name_zh)] + sep
        + [_sec_sources(sources)] + sep
        + [_sec_conclusion(ratings)] + ["", tail] + sep
        + [_sec_faq(faqs)]
    )

    content = "\n".join(sections).rstrip() + "\n"

    out_dir = OUTPUT_DIR.parent / cc.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_slug(en_name)}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
