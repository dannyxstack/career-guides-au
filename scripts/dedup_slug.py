# -*- coding: utf-8 -*-
"""职业 slug 去重的单一来源（方案 C1）：ISCO-08 跨国 canonical slug。

背景：36/46 国已对齐同一套 ISCO-08 四位码，但同一码在不同国家被存成了单/复数
等变体（436 码 → 1084 slug）。ISCO 码本身就是 canonical 概念主键，故按码归一即
无损。用户决策：**slug/URL 用单数**（name_en / 标题 / AI 文案 / FAQ 保持自然语言）。

规则：
- 仅对 ISCO08 记录归一；非 ISCO 国（ANZSCO/SOC/NOC/…）本次不动（C2 后置）。
- 每个 ISCO 码取"出现最多的英文名"slug 化后做确定性单数化 = canonical slug。
- 输出 旧slug→canonical 映射（供 301）。

被 export_site_data_v2.py 与离线校验脚本共用。
"""
import re
import collections

# 已经是单数/不该被剥 s 的词（避免误伤）：
# ① 无单数义的集合/领域名词（保持复数才自然）；② -ss/-us/-is 词形。
# 注意刻意不含 mechanics（"机械师"应单数化为 mechanic）。
_KEEP = {
    "goods", "sales", "news", "series", "species", "premises", "means",
    "gas", "bus", "plus", "analysis", "diagnosis", "prosthesis",
    # 固定词组 / 领域名词
    "forces", "electronics", "communications", "sports", "athletics",
    "economics", "mathematics", "statistics", "logistics", "ceramics",
    "optics", "politics", "ethics", "physics", "arts",
}


def slugify(name):
    """与 export_site_data_v2.slug 完全一致。"""
    s = re.sub(r"[/()\[\]]", " ", (name or "occ").lower())
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", "-", s.strip()) or "occ"


def singularize_token(w):
    if w in _KEEP or len(w) <= 3:
        return w
    if w.endswith("ies"):
        return w[:-3] + "y"           # fisheries->fishery, authorities->authority
    if w.endswith(("sses", "shes", "ches", "xes", "zes")):
        return w[:-2]                 # bosses->boss, watches->watch
    if w.endswith("s") and not w.endswith(("ss", "us", "is", "as", "os")):
        return w[:-1]                 # managers->manager, growers->grower
    return w


_STOP = {"and", "or", "of", "the", "a", "an", "in", "to", "for", "with"}


def singular_slug(sl):
    """对整个 hyphen-slug 逐词单数化（停用词/连接词保持不变）。"""
    return "-".join(t if t in _STOP else singularize_token(t) for t in sl.split("-"))


def build_canonical_map(records):
    """records: 可迭代的 dict，每个需含 occ_code_type / occ_code / name_en / slug。

    返回 (old_slug -> canonical_slug) 仅含 ISCO08 且 old != canonical 的条目，
    以及 code -> canonical 便于诊断。
    """
    # 每个 ISCO 码统计各英文名出现次数（用于取主导名）
    code_names = collections.defaultdict(collections.Counter)
    code_slugs = collections.defaultdict(set)
    for r in records:
        if r["occ_code_type"] != "ISCO08":
            continue
        code_names[r["occ_code"]][r["name_en"]] += 1
        code_slugs[r["occ_code"]].add(r["slug"])

    code_canon = {}
    for code, names in code_names.items():
        dominant = names.most_common(1)[0][0]
        code_canon[code] = singular_slug(slugify(dominant))

    remap = {}
    for code, slugs in code_slugs.items():
        canon = code_canon[code]
        for s in slugs:
            if s != canon:
                remap[s] = canon
    return remap, code_canon
