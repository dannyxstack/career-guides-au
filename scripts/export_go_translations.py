"""把 DB(translations_v2)里指定 locale 的译文导出到 aijobrisk-go 站的分片。

源串口径复用 count_go_translation.collect()（= Go 站经 Tr() 实际渲染的英文源串），
只保留站点用到的串以控制分片体积。**合并式写入**：并进现有 {loc}.{i}.json，
不删除既有键，从而保留 translate_go_new_strings.py 手加的 UI 译文。

用法：PYTHONIOENCODING=utf-8 python scripts/export_go_translations.py --locales es,fr
"""
import os, sys, json, hashlib, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts.count_go_translation import collect

GO = os.path.join(os.path.dirname(__file__), "..", "aijobrisk-go", "data")
TR = os.path.join(GO, "translations-v2")
N_SHARDS = 8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--locales", default="es,fr")
    a = ap.parse_args()
    locales = [x.strip() for x in a.locales.split(",") if x.strip()]

    os.makedirs(TR, exist_ok=True)
    S = collect()
    print(f"[export-go] Go 站源串 {len(S):,} 条")

    with get_cursor() as cur:
        for loc in locales:
            cur.execute(
                "SELECT s.src_text, t.text FROM translations_v2 t "
                "JOIN translation_src_v2 s ON s.src_hash=t.src_hash "
                "WHERE t.locale=%s AND t.text IS NOT NULL AND t.text<>''", (loc,))
            db = {}
            for r in cur.fetchall():
                src = (r["src_text"] or "").strip()
                if src in S and r["text"]:
                    db[src] = r["text"]

            added = updated = 0
            for i in range(N_SHARDS):
                p = os.path.join(TR, f"{loc}.{i}.json")
                sh = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
                for src, txt in db.items():
                    if int(hashlib.md5(src.encode("utf-8")).hexdigest(), 16) % N_SHARDS != i:
                        continue
                    if src not in sh:
                        added += 1
                    elif sh[src] != txt:
                        updated += 1
                    sh[src] = txt
                json.dump(sh, open(p, "w", encoding="utf-8"), ensure_ascii=False)
            cover = len([s for s in S if s in db]) / len(S) * 100 if S else 0
            print(f"[export-go] {loc:<6} 命中 {len(db):,}/{len(S):,}  覆盖 {cover:.1f}%  (新增 {added:,} / 更新 {updated:,})")


if __name__ == "__main__":
    main()
