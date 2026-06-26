"""Phase 2 — ai-block 复用：把母体(AU/CA/US 等)的 occupation_ai + occupation_ai_disruptor
复制到匹配的目标国家职业（US / UK / …）。

读 .codex_tmp/{country}_ai_match.json（{occ_id: {country, occ_code, src_occ_id}}），
对每个有 src_occ_id 的目标职业，从母体复制 ai-block（adjacent 置空，幂等覆盖）。
未匹配 / 复制失败的职业不在此处理，留给回退脚本：
    python -m scripts.gen_ai_insights   --country <CC>
    python -m scripts.gen_ai_disruptors --country <CC>
（两脚本自动跳过已有 occupation_ai / disruptor 的职业。）

运行：python -m scripts.copy_ai_blocks --country UK [--redo]
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

TMP = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp")


def copy_ai_block(cur, src_id, dst_id):
    """复制母体 ai-block 到 dst（adjacent 置空，幂等覆盖）。母体无 occupation_ai 返回 False。"""
    cur.execute("SELECT 1 FROM occupation_ai WHERE occupation_id=%s", (src_id,))
    if not cur.fetchone():
        return False
    cur.execute("SHOW COLUMNS FROM occupation_ai")
    cols = [r["Field"] for r in cur.fetchall() if r["Field"] != "updated_at"]
    sel = []
    for c in cols:
        if c == "occupation_id":
            sel.append("%s")
        elif c == "adjacent":
            sel.append("NULL")
        else:
            sel.append(c)
    cur.execute("DELETE FROM occupation_ai WHERE occupation_id=%s", (dst_id,))
    cur.execute(f"INSERT INTO occupation_ai ({','.join(cols)}) "
                f"SELECT {','.join(sel)} FROM occupation_ai WHERE occupation_id=%s",
                (dst_id, src_id))
    # disruptor 链接
    cur.execute("SHOW COLUMNS FROM occupation_ai_disruptor")
    dcols = [r["Field"] for r in cur.fetchall()]
    dsel = ["%s" if c == "occupation_id" else c for c in dcols]
    cur.execute("DELETE FROM occupation_ai_disruptor WHERE occupation_id=%s", (dst_id,))
    cur.execute(f"INSERT INTO occupation_ai_disruptor ({','.join(dcols)}) "
                f"SELECT {','.join(dsel)} FROM occupation_ai_disruptor WHERE occupation_id=%s",
                (dst_id, src_id))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default="US", help="目标国家代码，如 US / UK")
    ap.add_argument("--redo", action="store_true", help="对已有 occupation_ai 的目标职业也重新复制")
    a = ap.parse_args()
    cc = a.country.strip().upper()

    match = json.load(open(os.path.join(TMP, f"{cc.lower()}_ai_match.json"), encoding="utf-8"))
    # 跳过已有 occupation_ai 的（除非 --redo）
    if not a.redo:
        with get_cursor() as cur:
            cur.execute("SELECT a.occupation_id FROM occupation_ai a "
                        "JOIN occupations o ON o.id=a.occupation_id WHERE o.country_code=%s", (cc,))
            done = {str(r["occupation_id"]) for r in cur.fetchall()}
    else:
        done = set()

    todo = [(k, v) for k, v in match.items() if v.get("src_occ_id") and k not in done]
    print(f"[{cc.lower()}-ai-copy] 待复制 {len(todo)} 个（match {len(match)}，已有 {len(done)}）", flush=True)

    ok = no_src = fail = 0
    for i, (dst_id, v) in enumerate(todo, 1):
        src_id = v["src_occ_id"]
        try:
            with get_cursor() as cur:
                copied = copy_ai_block(cur, src_id, int(dst_id))
            if copied:
                ok += 1
            else:
                no_src += 1
            if i % 25 == 0 or i == len(todo):
                print(f"  [{i}/{len(todo)}] ok={ok} no_src={no_src} fail={fail}", flush=True)
        except Exception as e:
            fail += 1
            print(f"  [{i}/{len(todo)}] dst={dst_id} src={src_id} 失败: {e}", flush=True)

    print(f"[OK] 复制完成：成功 {ok}，母体无ai-block {no_src}，失败 {fail}。"
          f"剩余未匹配 {cc} 职业请跑 gen_ai_insights/gen_ai_disruptors --country {cc} 补齐。", flush=True)


if __name__ == "__main__":
    main()
