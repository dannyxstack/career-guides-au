"""测试数据库连接，打印服务器版本和当前数据库名。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.connection import get_cursor

try:
    with get_cursor() as cur:
        cur.execute("SELECT VERSION() AS version, DATABASE() AS db")
        row = cur.fetchone()
    print(f"[OK] 连接成功")
    print(f"     MySQL 版本 : {row['version']}")
    print(f"     当前数据库 : {row['db']}")
except Exception as e:
    print(f"[FAIL] 连接失败: {e}")
    sys.exit(1)
