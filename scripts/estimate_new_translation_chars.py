"""只读评估：某国新增了多少「新的」可翻译英文母本字符（不写库、不翻译）。

「新」= 该国去重源串中，sha1 尚未存在于 translation_src_v2 的部分。已存在的串（如从他国
拷贝的 AI 块、跨国共享的通用标签）不再计入新增翻译量。

运行：python -m scripts.estimate_new_translation_chars --country IN [--locales 9]
"""
import sys, os, argparse, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._i18n_fields_v2 import fetch_bundles, collect_from_bundle, needs_translation


def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def run(country, locales):
    with get_cursor() as cur:
        bundles = fetch_bundles(cur, country)
        srcs = {}
        for b in bundles:
            for _f, text in collect_from_bundle(b):
                if needs_translation(text):
                    srcs[sha1(text)] = text
        hashes = list(srcs.keys())
        existing = set()
        for i in range(0, len(hashes), 1000):
            chunk = hashes[i:i + 1000]
            cur.execute("SELECT src_hash FROM translation_src_v2 WHERE src_hash IN (%s)"
                        % ",".join(["%s"] * len(chunk)), chunk)
            existing |= {r["src_hash"] for r in cur.fetchall()}

    new = {h: t for h, t in srcs.items() if h not in existing}
    tot_chars = sum(len(t) for t in srcs.values())
    new_chars = sum(len(t) for t in new.values())
    dup_chars = tot_chars - new_chars
    print(f"=== {country} 翻译量评估（{len(bundles)} 职业）===")
    print(f"去重源串   ：{len(srcs):>6} 条 / {tot_chars:>9,} 字符")
    print(f"  已在TM   ：{len(existing):>6} 条 / {dup_chars:>9,} 字符（拷贝的AI块/跨国共享标签，不算新增）")
    print(f"  新增源串 ：{len(new):>6} 条 / {new_chars:>9,} 字符  ← 每个目标语言需翻译的字符数")
    print(f"× {locales} 个目标语言（母本英文除外）总计约：{new_chars * locales:>12,} 字符")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--locales", type=int, default=9)
    a = ap.parse_args()
    run(a.country, a.locales)
