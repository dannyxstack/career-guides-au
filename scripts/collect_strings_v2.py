"""采集 v2 英文母本的可翻译源串，写入 translation_src_v2（幂等，主键 sha1(英文)）。
运行：python -m scripts.collect_strings_v2 [--country CH]
"""
import sys, os, argparse, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._i18n_fields_v2 import fetch_bundles, collect_from_bundle, needs_translation


def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def run(country=None):
    with get_cursor() as cur:
        bundles = fetch_bundles(cur, country)
        srcs = {}
        for b in bundles:
            for _field, text in collect_from_bundle(b):
                if needs_translation(text):
                    srcs[sha1(text)] = text
        print(f"[collect_v2] {len(bundles)} 职业 -> {len(srcs)} 去重英文源串")
        rows = [(h, t) for h, t in srcs.items()]
        for i in range(0, len(rows), 1000):
            cur.executemany("INSERT INTO translation_src_v2 (src_hash,src_text) VALUES (%s,%s) "
                            "ON DUPLICATE KEY UPDATE src_text=VALUES(src_text)", rows[i:i + 1000])
        cur.execute("SELECT COUNT(*) c FROM translation_src_v2")
        print(f"[collect_v2] translation_src_v2 现有 {cur.fetchone()['c']} 条")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default="")
    a = ap.parse_args()
    run(a.country or None)
