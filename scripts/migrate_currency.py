"""迁移：occupations 表新增 currency 列（按国家的本币：AUD/NZD/CAD/USD）。
幂等。运行：python -m scripts.migrate_currency
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

# 国家 -> 默认货币（无 currency 时按 country_code 回填）
CC = {"AU": "AUD", "NZ": "NZD", "CA": "CAD", "US": "USD", "GB": "GBP"}


def run():
    with get_cursor() as cur:
        cur.execute("SHOW COLUMNS FROM occupations LIKE 'currency'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE occupations ADD COLUMN currency VARCHAR(8) NOT NULL DEFAULT 'AUD' "
                        "COMMENT '本币 AUD/NZD/CAD/USD' AFTER category")
            print("[migrate] 已新增 occupations.currency")
        else:
            print("[migrate] currency 已存在")
        # 按 country_code 回填（已有行默认都是 AUD，仅在出现其他国家行时纠正）
        for cc, cur_code in CC.items():
            cur.execute("UPDATE occupations SET currency=%s WHERE country_code=%s AND (currency IS NULL OR currency='')",
                        (cur_code, cc))
        print("[migrate] currency 回填完成")


if __name__ == "__main__":
    run()
