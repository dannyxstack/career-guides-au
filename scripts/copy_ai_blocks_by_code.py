"""按 occ_code 从源国（默认 IT）拷贝 occupation_ai_v2 到目标国（默认 IN）。

用途：ISCO-08/NCO2015 等码对齐的国家，AI 暴露块（含 country-neutral 的 AIOE 分）可直接复用，
无需重新调用 LLM。幂等：occupation_ai_v2 以 occupation_id 唯一，ON DUPLICATE KEY UPDATE 覆盖。

运行：python -m scripts.copy_ai_blocks_by_code --to IN --from IT
"""
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

COLS = ["verdict_type", "verdict", "entry_narrowing", "upgrade_path", "replaced", "augmented",
        "moat", "skills", "adjacent", "cluster", "automation_exposure", "human_moat",
        "entry_risk", "ai_upside", "aioe_score", "aioe_pct", "aioe_soc", "aioe_method"]


def run(to_cc, from_cc):
    with get_cursor() as cur:
        # 源国 occ_code -> ai 行
        cur.execute(
            "SELECT o.occ_code, a.* FROM occupation_ai_v2 a "
            "JOIN occupations o ON o.id=a.occupation_id WHERE o.country_code=%s", (from_cc,))
        src = {r["occ_code"]: r for r in cur.fetchall()}
        # 目标国职业
        cur.execute("SELECT id, occ_code FROM occupations WHERE country_code=%s", (to_cc,))
        tgt = cur.fetchall()
        cols_sql = ",".join(COLS)
        upd_sql = ",".join(f"{c}=VALUES({c})" for c in COLS)
        placeholders = ",".join(["%s"] * (len(COLS) + 1))
        copied = miss = 0
        missing_codes = []
        for t in tgt:
            s = src.get(t["occ_code"])
            if not s:
                miss += 1
                missing_codes.append(t["occ_code"])
                continue
            vals = [t["id"]] + [s[c] for c in COLS]
            cur.execute(
                f"INSERT INTO occupation_ai_v2 (occupation_id,{cols_sql}) VALUES ({placeholders}) "
                f"ON DUPLICATE KEY UPDATE {upd_sql}", vals)
            copied += 1
    print(f"[copy_ai] {from_cc}->{to_cc}: 拷贝 {copied}，源无对应码 {miss}")
    if missing_codes:
        print("  未命中码:", ", ".join(missing_codes))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--from", dest="frm", default="IT")
    a = ap.parse_args()
    run(a.to, a.frm)
