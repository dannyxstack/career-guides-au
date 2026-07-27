"""用 build_cn_workforce.py 的结果覆盖 CN 的 workforce_size（downloads/cn/cn_by_isco_workforce.json）。

只改 workforce_size（有官方映射值则写入；None=军职则跳过保持原值）。其余字段不动。--dry 只看不写。
运行：python -m scripts.apply_cn_workforce [--dry]
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "downloads", "cn", "cn_by_isco_workforce.json")


def main(dry):
    data = json.load(open(SRC, encoding="utf-8"))
    n = skip = 0
    with get_cursor() as cur:
        cur.execute("SELECT id, occ_code FROM occupations WHERE country_code='CN'")
        for o in cur.fetchall():
            wf = (data.get(str(o["occ_code"])) or {}).get("workforce")
            if wf is None:
                skip += 1
                continue
            n += 1
            if not dry:
                cur.execute("UPDATE occupations SET workforce_size=%s WHERE id=%s", (wf, o["id"]))
    print(f"[apply_cn_wf] {'DRY ' if dry else ''}覆盖 workforce {n} 条（跳过 {skip}：军职/无映射）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    main(ap.parse_args().dry)
