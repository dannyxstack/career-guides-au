"""
将职业分析 Markdown 文件解析为结构化 dict，供导入数据库使用。

解析结果结构：
{
  "anzsco_code": "341111",
  "anzsco_title": "Electrician (General)",
  "name_zh": "电工",
  "summary": "...",
  "shortage_listed": True,
  "growth_areas": ["Solar Installation", ...],
  "forecast_note": "...",
  "ratings": [{"dimension": "learning_difficulty", "label_zh": "中高", "stars": 4}, ...],
  "education": [{"stage": "学徒制（含 TAFE）", "duration": "4年", "cost_min": 3000, "cost_max": 8000, "cost_note": "政府补贴后"}, ...],
  "qualifications": [{"qual_name": "...", "issuer": "...", "note": "..."}, ...],
  "job_listings": [{"platform": "Seek", "count_min": 2500, "count_max": 4000, "note": "..."}, ...],
  "salaries": [{"experience": "...", "salary_min": 80000, "salary_max": 110000, "salary_note": "..."}, ...],
  "visa_pathways": [{"visa_subclass": "186", "visa_name": "ENS", "description": "..."}, ...],
  "suitability_fit": ["...", ...],
  "suitability_unfit": ["...", ...],
  "sources": [{"source_name": "...", "content": "..."}, ...],
  "faqs": [{"faq_type": "salary", "question": "...", "answer": "..."}, ...],
}
"""

import re
from pathlib import Path


# ── 评级维度：正则关键词 → dimension key ──────────────────────────────────────
DIMENSION_MAP = [
    (r"学习难度",       "learning_difficulty"),
    (r"学习周期",       "learning_duration"),
    (r"考证难度",       "certification_difficulty"),
    (r"职位需求量",     "job_demand"),
    (r"竞争度",         "competition"),
    (r"工作强度",       "work_intensity"),
    (r"收入水平",       "income_level"),
    (r"AI替代风险",     "ai_risk"),
    (r"发展前景",       "future_prospect"),
    (r"PR友好度",       "pr_friendliness"),
    (r"PR难度",         "pr_difficulty"),
]

# 评级描述 → 星数
STAR_MAP = {
    "极低": 1, "很低": 1,
    "较低": 2,
    "中等": 3,
    "中高": 4, "较高": 4,
    "极高": 5, "极佳": 5, "非常强": 5,
}

FAQ_TYPE_MAP = [
    (r"工资|薪资|薪水|收入",           "salary"),
    (r"找工作|容易|难找|就业",          "demand"),
    (r"认可|互认|证书|资质",            "recognition"),
    (r"AI|替代|自动化",                 "ai_risk"),
    (r"年龄",                           "age_limit"),
    (r"学历|学位",                      "education_limit"),
    (r"难学|难度|学习",                 "difficulty"),
    (r"哪个|比较|还是|vs|VS",          "comparison"),
]


def _infer_faq_type(question: str) -> str:
    for pattern, faq_type in FAQ_TYPE_MAP:
        if re.search(pattern, question):
            return faq_type
    return "other"


def _parse_stars(star_str: str) -> int:
    """从 ★★★☆☆ 计算星数。"""
    return star_str.count("★")


def _parse_amount(text: str):
    """从字符串提取金额数值，去掉 $ 和逗号后转 float，失败返回 None。"""
    m = re.search(r"\$?([\d,]+)", text.replace(",", ""))
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None
    return None


def _split_sections(content: str) -> dict[str, str]:
    """按二级标题 ## 切分文档，返回 {标题文字: 内容} 。"""
    sections = {}
    pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections[title] = content[start:end].strip()
    return sections


def _parse_table_rows(section_text: str) -> list[list[str]]:
    """提取 Markdown 表格的数据行（跳过表头和分隔行）。"""
    rows = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r"[-: ]+", c) for c in cells):
            continue  # 分隔行
        rows.append(cells)
    return rows[1:] if rows else []   # 跳过表头行


def parse_md(filepath: str | Path) -> dict:
    content = Path(filepath).read_text(encoding="utf-8")
    result = {}

    # ── 职业代码和标题 ──────────────────────────────────────────────────────
    code_match = re.search(r"\*\*职业代码[：:]\s*(\d+)\s*[–—-]\s*(.+?)[。\.]?\*\*", content)
    if code_match:
        result["anzsco_code"] = code_match.group(1).strip()
        result["anzsco_title"] = code_match.group(2).strip()

    # ── 职业中文名（从一级标题提取）──────────────────────────────────────────
    h1_match = re.search(r"^# (.+)", content, re.MULTILINE)
    if h1_match:
        # "电工（Electrician）职业分析 · 澳大利亚" → "电工"
        name_match = re.match(r"(.+?)[\s（(]", h1_match.group(1))
        result["name_zh"] = name_match.group(1).strip() if name_match else h1_match.group(1).strip()

    # ── 简介：职业代码行之后、第一个 --- 之前的段落 ──────────────────────────
    intro_match = re.search(
        r"\*\*职业代码.+?\*\*\s*\n+([\s\S]+?)\n+---",
        content
    )
    if intro_match:
        result["summary"] = intro_match.group(1).strip()

    sections = _split_sections(content)

    # ── 评级（从全文扫描所有 **XX：YY（★）** 模式）────────────────────────
    ratings = []
    rating_pattern = re.compile(r"\*\*([^*]+?)[：:]([^（(]+)[（(](★[★☆]{4})[）)][。.]?\*\*")
    for m in rating_pattern.finditer(content):
        label_raw = m.group(2).strip()
        star_str  = m.group(3)
        dimension = None
        for kw, dim in DIMENSION_MAP:
            if re.search(kw, m.group(1)):
                dimension = dim
                break
        if dimension:
            ratings.append({
                "dimension": dimension,
                "label_zh":  label_raw,
                "stars":     _parse_stars(star_str),
            })
    # 去重（同维度保留第一次出现）
    seen = set()
    result["ratings"] = []
    for r in ratings:
        if r["dimension"] not in seen:
            seen.add(r["dimension"])
            result["ratings"].append(r)

    # ── 第1部分：教育路径 ────────────────────────────────────────────────────
    edu_section = next((v for k, v in sections.items() if "教育路径" in k), "")
    result["education"] = []
    for row in _parse_table_rows(edu_section):
        if len(row) < 3:
            continue
        cost_text = row[2]
        cost_parts = re.findall(r"\$?([\d,]+)", cost_text.replace(",", ""))
        cost_min = float(cost_parts[0]) if len(cost_parts) > 0 else None
        cost_max = float(cost_parts[1]) if len(cost_parts) > 1 else cost_min
        cost_note_m = re.search(r"[（(]([^）)]+)[）)]", cost_text)
        result["education"].append({
            "stage":     row[0],
            "duration":  row[1],
            "cost_min":  cost_min,
            "cost_max":  cost_max,
            "cost_note": cost_note_m.group(1) if cost_note_m else None,
        })

    # ── 第2部分：从业资质 ────────────────────────────────────────────────────
    qual_section = next((v for k, v in sections.items() if "考证难度" in k), "")
    result["qualifications"] = []
    for row in _parse_table_rows(qual_section):
        if len(row) < 1:
            continue
        result["qualifications"].append({
            "qual_name": row[0],
            "issuer":    row[1] if len(row) > 1 else None,
            "note":      row[2] if len(row) > 2 else None,
        })

    # ── 第3部分：职位需求量 ──────────────────────────────────────────────────
    demand_section = next((v for k, v in sections.items() if "职位需求量" in k), "")

    # 从业人数
    wf_match = re.search(r"从业人数约\s*([\d,]+)", demand_section)
    result["workforce_size"] = int(wf_match.group(1).replace(",", "")) if wf_match else None

    # 缺口预测
    forecast_match = re.search(r"预计.{0,60}(缺口|需求).{0,80}", demand_section)
    result["forecast_note"] = forecast_match.group(0).strip() if forecast_match else None

    result["shortage_listed"] = bool(re.search(r"短缺清单", demand_section))

    # 平台挂牌量
    result["job_listings"] = []
    for row in _parse_table_rows(demand_section):
        if len(row) < 2:
            continue
        platform = row[0]
        if not re.search(r"Seek|Indeed|LinkedIn", platform):
            continue
        counts = re.findall(r"[\d,]+", row[1].replace(",", ""))
        result["job_listings"].append({
            "platform":  platform,
            "count_min": int(counts[0]) if len(counts) > 0 else None,
            "count_max": int(counts[1]) if len(counts) > 1 else None,
            "note":      row[2] if len(row) > 2 else None,
        })

    # ── 第4部分：收入范围 ────────────────────────────────────────────────────
    salary_section = next((v for k, v in sections.items() if "收入范围" in k), "")
    result["salaries"] = []
    for i, row in enumerate(_parse_table_rows(salary_section)):
        if len(row) < 2:
            continue
        amounts = re.findall(r"[\d,]+", row[1].replace(",", ""))
        result["salaries"].append({
            "experience":  row[0],
            "salary_min":  float(amounts[0]) if len(amounts) > 0 else None,
            "salary_max":  float(amounts[1]) if len(amounts) > 1 else None,
            "salary_note": row[2] if len(row) > 2 else None,
            "sort_order":  i,
        })

    # ── 第5部分：未来趋势 ────────────────────────────────────────────────────
    trend_section = next((v for k, v in sections.items() if "未来趋势" in k), "")
    result["trend_summary"] = re.sub(r"\*\*[^*]+\*\*\s*", "", trend_section).strip()[:500]

    # 增长方向列表
    growth = re.findall(r"^[-*]\s+(.+)$", trend_section, re.MULTILINE)
    result["growth_areas"] = growth if growth else []

    # ── 第6部分：移民路径 ────────────────────────────────────────────────────
    visa_section = next((v for k, v in sections.items() if "移民路径" in k), "")
    result["visa_pathways"] = []
    for i, row in enumerate(_parse_table_rows(visa_section)):
        if len(row) < 1:
            continue
        sub_match = re.search(r"(\d{3})", row[0])
        name_match = re.search(r"[（(](\w+)[）)]", row[0])
        result["visa_pathways"].append({
            "visa_subclass": sub_match.group(1) if sub_match else row[0],
            "visa_name":     name_match.group(1) if name_match else None,
            "description":   row[1] if len(row) > 1 else None,
            "sort_order":    i,
        })

    # ── 第7部分：适合/不适合人群 ─────────────────────────────────────────────
    suit_section = next((v for k, v in sections.items() if "适合人群" in k), "")
    fit_items, unfit_items = [], []
    current = None
    for line in suit_section.splitlines():
        if re.search(r"谁适合|适合人群", line):
            current = "fit"
        elif re.search(r"谁不应该|不适合", line):
            current = "unfit"
        elif line.strip().startswith("-") and current:
            item = line.strip().lstrip("-").strip()
            if item:
                (fit_items if current == "fit" else unfit_items).append(item)
    result["suitability_fit"]   = fit_items
    result["suitability_unfit"] = unfit_items

    # ── 第8部分：数据来源 ────────────────────────────────────────────────────
    source_section = next((v for k, v in sections.items() if "数据来源" in k), "")
    result["sources"] = []
    for row in _parse_table_rows(source_section):
        if len(row) < 1:
            continue
        result["sources"].append({
            "source_name": row[0],
            "content":     row[1] if len(row) > 1 else None,
        })

    # ── 第9部分：FAQ ──────────────────────────────────────────────────────────
    faq_section = next((v for k, v in sections.items() if "FAQ" in k), "")
    result["faqs"] = []
    qa_blocks = re.findall(
        r"\*\*问[：:](.+?)\*\*\s*答[：:](.+?)(?=\*\*问[：:]|\Z)",
        faq_section,
        re.DOTALL,
    )
    for i, (q, a) in enumerate(qa_blocks):
        question = q.strip()
        answer   = a.strip()
        result["faqs"].append({
            "faq_type":   _infer_faq_type(question),
            "question":   question,
            "answer":     answer,
            "sort_order": i,
        })

    return result
