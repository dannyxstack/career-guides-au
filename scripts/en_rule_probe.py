# -*- coding: utf-8 -*-
"""第②步：把候选"修复规则"检测器跑到全量英文语料上，测真实命中数 + 抽样。
证据来自 audit_en_quality 的标红样例；这里验证每条规则在 202k 英文上的覆盖与误伤。
只读，不改库。"""
import sys, os, re, json, random
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

CJK = re.compile(r"[一-鿿]")
# zh 里「数字+万」，抓 8~12万 / 3-4万 / 1万 之类
WAN = re.compile(r"(\d+(?:\.\d+)?)\s*[~～\-至]?\s*(\d+(?:\.\d+)?)?\s*万")
ZH_CUR = re.compile(r"美元|欧元|纽币|加元|澳元|澳币|英镑|欧(?![盟洲])")
EN_CUR = re.compile(r"[$€£]|\b(USD|EUR|AUD|NZD|CAD|GBP|RMB|CNY)\b|[ACN]Z?\$"
                    r"|\b(dollars?|euros?|pounds?|yen|yuan|renminbi|francs?|kronor?)\b", re.I)
EN_NUM = re.compile(r"\d")
EN_THOUSAND = re.compile(r"\bthousand\b", re.I)
DESIN = re.compile(r"\b(chinese|mandarin|cantonese)\b", re.I)
MODELS = re.compile(r"\b(senior|mid-level|intermediate|entry-level|advanced|junior|high-level)\s+models?\b", re.I)
SUBJ_PAY = re.compile(r"\b(universit\w+|schools?|colleges?|centers?|centres?|establishments?|institut\w+|programs?)\s+pays?\b", re.I)


def wan_dropped(zh, en):
    """zh 有『x万』，但 en 里出现了同样的小数字却没放大（无 0,000 / k / 万 / million）。"""
    if "万" not in zh:
        return False
    for m in WAN.finditer(zh):
        for g in (m.group(1), m.group(2)):
            if not g:
                continue
            # en 里出现该裸数字，且其后不是 ,000 / 000 / k / 万 / m / 万级词
            for em in re.finditer(re.escape(g) + r"(?![\d.,])", en):
                tail = en[em.end():em.end()+7].lower()
                if not re.match(r"\s*(,?0{3}|k|万|m|million|thousand)", tail):
                    return True
    return False


def main():
    with get_cursor() as cur:
        cur.execute("SELECT s.src_text zh, s.field, t.text en FROM translations t "
                    "JOIN translation_src s ON s.src_hash=t.src_hash WHERE t.locale='en'")
        rows = cur.fetchall()
    total = len(rows)
    print(f"全量英文语料 n={total:,}\n")

    rules = {
        "R1 cjk_leftover  (en 残留中文字符)": lambda z, e: bool(CJK.search(e)),
        "R2a wan_source   (zh 含『万』· 高危超集)": lambda z, e: "万" in z,
        "R2b wan_dropped  (zh『万』但 en 数字未放大)": wan_dropped,
        "R2c wan_thousand (zh『万』· en 用 thousand · 10x错)": lambda z, e: "万" in z and bool(EN_THOUSAND.search(e)),
        "R3 currency_missing (zh 有币种 · en 有数字无币符)": lambda z, e: bool(ZH_CUR.search(z) and EN_NUM.search(e) and not EN_CUR.search(e)),
        "R4 desinify      (en 含 Chinese/Mandarin/Cantonese)": lambda z, e: bool(DESIN.search(e)),
        "R5 salary_models (zh 无『模』· en『senior models』误译)": lambda z, e: bool(MODELS.search(e)) and "模" not in z,
        "R6 subject_pay   (en『schools pay』类学费误译)": lambda z, e: bool(SUBJ_PAY.search(e)),
    }
    hits = {k: [] for k in rules}
    for r in rows:
        z, e = r["zh"] or "", r["en"] or ""
        for name, fn in rules.items():
            try:
                if fn(z, e):
                    hits[name].append(r)
            except Exception:
                pass

    print(f"{'规则':52} {'命中':>7} {'占比':>7}")
    print("-" * 70)
    for name in rules:
        n = len(hits[name])
        print(f"{name:52} {n:>7,} {n/total*100:>6.2f}%")

    print("\n===== 各规则抽样（核对精度/误伤）=====")
    random.seed(1)
    for name in rules:
        h = hits[name]
        if not h:
            continue
        print(f"\n--- {name}  (命中 {len(h):,}) ---")
        for r in random.sample(h, min(5, len(h))):
            print(f"  [{r['field']}] zh: {(r['zh'] or '')[:64]}")
            print(f"           en: {(r['en'] or '')[:88]}")


if __name__ == "__main__":
    main()
