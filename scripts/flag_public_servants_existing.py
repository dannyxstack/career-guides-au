"""给「已在库」的职业补打公职人员标记 is_public_servant=1。
当前仅 Procurement Officer（已存在，不重复入库，仅补标记）。
幂等。运行：python -m scripts.flag_public_servants_existing
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

# 按英文标准名匹配（anzsco_title）
TITLES = ["Procurement Officer"]


def run():
    with get_cursor() as cur:
        for t in TITLES:
            cur.execute(
                "UPDATE occupations SET is_public_servant=1 "
                "WHERE country_code='AU' AND anzsco_title=%s", (t,))
            print(f"[flag] {t}: {cur.rowcount} 行已标记公职")


if __name__ == "__main__":
    run()
