# -*- coding: utf-8 -*-
"""定向补译：薪资中位数/平均薪资的 label 与来源 note（median/mean 两档）。

背景：薪资中位数/均值入库时新增了 2 个展示 label（薪资中位数/平均薪资）与
各国来源 note，走全站统一的文件式 TM（按源中文串哈希翻译，前端 tr() 解析）。
这些串是新增的，尚未进 translation_src 也无译文。本脚本只处理这一小撮串，
避免误翻 de/id/ja 等语言里几十万的历史积压。

流程：DB 取 median/mean 的 distinct experience+salary_note → upsert
translation_src → 对每个目标语言只翻尚缺者，走现有 translate_batch
（后端优先级 百度 -> Azure -> DeepSeek）写入 translations（幂等）。

运行：
  PYTHONIOENCODING=utf-8 python -m scripts.translate_salary_labels [--dry]
"""
import sys, os, argparse, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts.translate_strings import LOCALES, LANG_NAME, translate_batch


def h(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def salary_strings():
    """median/mean 两档的 distinct (text, field)。label->salary_label，note->salary_note。"""
    seen = {}  # hash -> (text, field)
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT experience FROM occupation_salaries "
                    "WHERE salary_band IN ('median','mean') AND experience IS NOT NULL AND experience<>''")
        for r in cur.fetchall():
            t = r["experience"].strip()
            seen.setdefault(h(t), (t, "salary_label"))
        cur.execute("SELECT DISTINCT salary_note FROM occupation_salaries "
                    "WHERE salary_band IN ('median','mean') AND salary_note IS NOT NULL AND salary_note<>''")
        for r in cur.fetchall():
            t = r["salary_note"].strip()
            seen.setdefault(h(t), (t, "salary_note"))
    return seen


def run(locales, dry):
    seen = salary_strings()
    print(f"[scope] median/mean 待处理 distinct 源串 {len(seen)}")
    # upsert 到 translation_src
    rows = [(hh, t, f) for hh, (t, f) in seen.items()]
    if not dry:
        with get_cursor() as cur:
            cur.executemany(
                "INSERT INTO translation_src (src_hash, src_text, field) VALUES (%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE field=VALUES(field)", rows)
    hashes = list(seen.keys())
    fmt = ",".join(["%s"] * len(hashes))
    total = 0
    for loc in locales:
        with get_cursor() as cur:
            cur.execute(
                "SELECT src_hash FROM translations WHERE locale=%s AND src_hash IN (" + fmt + ")",
                [loc] + hashes)
            have = {r["src_hash"] for r in cur.fetchall()}
        todo = [(hh, seen[hh][0]) for hh in hashes if hh not in have]
        print(f"[{loc}] 待翻 {len(todo)}")
        if dry or not todo:
            continue
        texts = [t for _, t in todo]
        res = translate_batch(texts, LANG_NAME[loc], loc)
        out = [(hh, loc, t, "salary-labels") for (hh, _), t in zip(todo, res) if t]
        with get_cursor() as cur:
            cur.executemany(
                "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", out)
        total += len(out)
        print(f"[{loc}] 写入 {len(out)}")
    print(f"[完成] 共写入 {total} 条译文")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--locales", default=",".join(LOCALES))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    run([x.strip() for x in a.locales.split(",") if x.strip()], a.dry)
