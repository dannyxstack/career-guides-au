"""标记 translation_src_v2 里各源串是否被 aijobrisk 站实际引用（in_aijobrisk）。

引用集 = gen_aijobrisk_tm.site_src_set()（站点渲染的英文源串，trim 后），与 gen_aijobrisk_tm 导出口径完全一致。
标记后 translate_v2 默认只翻 in_aijobrisk=1 的串（新语言跳过无用翻译）。

幂等：先全置 0，再把引用集置 1。每次站点内容/UI 有增删后重跑本脚本刷新标记。
运行：PYTHONIOENCODING=utf-8 python scripts/mark_aijobrisk_src.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts.gen_aijobrisk_tm import site_src_set


def run():
    site = site_src_set()  # trim 后的引用源串集合
    print(f"[mark] aijobrisk 引用源串 {len(site):,} 条")
    with get_cursor() as cur:
        cur.execute("SELECT src_hash, src_text FROM translation_src_v2")
        rows = cur.fetchall()
        ref_hashes = [r["src_hash"] for r in rows if (r["src_text"] or "").strip() in site]
        cur.execute("UPDATE translation_src_v2 SET in_aijobrisk=0")
        for i in range(0, len(ref_hashes), 1000):
            chunk = ref_hashes[i:i + 1000]
            cur.execute("UPDATE translation_src_v2 SET in_aijobrisk=1 WHERE src_hash IN (%s)"
                        % ",".join(["%s"] * len(chunk)), chunk)
        cur.execute("SELECT COUNT(*) c FROM translation_src_v2 WHERE in_aijobrisk=1")
        marked = cur.fetchone()["c"]
    print(f"[mark] 已标记引用 {marked:,} / 总 {len(rows):,}（未引用 {len(rows) - marked:,} 条将被新语言翻译跳过）")


if __name__ == "__main__":
    run()
