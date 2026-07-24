"""采集 aijobrisk 页面里 tr('字面量') 形式的 UI 源串（英文母本），
写入 translation_src_v2（幂等，主键 sha1）+ 产出 ui_source_strings.json 供 gen_aijobrisk_tm 纳入分片。

只提取 tr() 的字符串字面量参数（单/双引号/模板串）；tr(变量) 的内容层调用不受影响。
用法：PYTHONIOENCODING=utf-8 python scripts/collect_ui_strings.py
"""
import os, sys, re, json, glob, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

SRC_DIR = os.path.join("aijobrisk", "src")
OUT_JSON = os.path.join("aijobrisk", "src", "data", "ui_source_strings.json")
_HAS_ALPHA = re.compile(r"[A-Za-z]")

# 经 tr(变量) 渲染、无法从 tr('字面量') 扫到的固定 UI 串（暴露档/风险档标签，见 lib/ui.ts）
_EXTRA = [
    "critical", "high", "moderate", "low", "very low", "n/a",  # expBand
    "High", "Moderate", "Lower", "Unknown",                     # riskBand10
    # 国家名（countryName 经 tr(en, loc) 渲染）
    "Australia", "New Zealand", "Canada", "United States", "United Kingdom",
    "Germany", "France", "Spain", "Italy", "Netherlands", "Ireland", "Japan", "South Korea",
]

# tr( 后紧跟字符串字面量（单引号/双引号/反引号），允许 \ 转义
_PATS = [
    re.compile(r"tr\(\s*'((?:\\.|[^'\\])*)'"),
    re.compile(r'tr\(\s*"((?:\\.|[^"\\])*)"'),
    re.compile(r"tr\(\s*`((?:\\.|[^`\\])*)`"),
]


def _unescape(s):
    return (s.replace("\\'", "'").replace('\\"', '"').replace("\\`", "`")
             .replace("\\n", "\n").replace("\\\\", "\\"))


def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def collect():
    files = (sorted(glob.glob(os.path.join(SRC_DIR, "**", "*.astro"), recursive=True))
             + sorted(glob.glob(os.path.join(SRC_DIR, "**", "*.ts"), recursive=True)))
    seen = {}
    for f in files:
        txt = open(f, encoding="utf-8").read()
        for pat in _PATS:
            for m in pat.finditer(txt):
                s = _unescape(m.group(1)).strip()
                if s and _HAS_ALPHA.search(s):
                    seen[s] = None
    # 分类名（categories_v2.json）：页面以 tr(cat, CL) 变量形式渲染，此处显式纳入源串
    cats_path = os.path.join(SRC_DIR, "data", "categories_v2.json")
    if os.path.exists(cats_path):
        for c in json.load(open(cats_path, encoding="utf-8")).get("categories", []):
            if c and _HAS_ALPHA.search(c):
                seen[c.strip()] = None
    # 行业名（industries_v2.json）：页面以 tr(s.name, CL) 变量形式渲染
    ind_path = os.path.join(SRC_DIR, "data", "industries_v2.json")
    if os.path.exists(ind_path):
        for s in json.load(open(ind_path, encoding="utf-8")).get("sectors", []):
            nm = s.get("name")
            if nm and _HAS_ALPHA.search(nm):
                seen[nm.strip()] = None
    for s in _EXTRA:
        seen[s] = None
    return list(seen.keys())


def main():
    strings = collect()
    with open(OUT_JSON, "w", encoding="utf-8") as fp:
        json.dump(strings, fp, ensure_ascii=False, indent=0)
    print(f"[collect-ui] 提取 UI 源串 {len(strings)} 条 -> {OUT_JSON}")

    rows = [(sha1(s), s) for s in strings]
    with get_cursor() as cur:
        for i in range(0, len(rows), 1000):
            cur.executemany(
                "INSERT INTO translation_src_v2 (src_hash,src_text) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE src_text=VALUES(src_text)", rows[i:i + 1000])
        cur.execute("SELECT COUNT(*) c FROM translation_src_v2")
        print(f"[collect-ui] translation_src_v2 现有 {cur.fetchone()['c']} 条")


if __name__ == "__main__":
    main()
