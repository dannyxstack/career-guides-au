"""迁移：occupations 表新增 is_public_servant 标记（公职人员：政府/公共部门岗位，
类似公务员/事业编/国企）。幂等——已存在则跳过。运行：
    python -m scripts.migrate_public_servant
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor


def run():
    with get_cursor() as cur:
        cur.execute("SHOW COLUMNS FROM occupations LIKE 'is_public_servant'")
        if cur.fetchone():
            print("[migrate] is_public_servant 已存在，跳过")
            return
        cur.execute(
            "ALTER TABLE occupations "
            "ADD COLUMN is_public_servant TINYINT(1) NOT NULL DEFAULT 0 "
            "COMMENT '公职人员：政府/公共部门岗位 1=是' AFTER is_migration")
        print("[migrate] 已新增 occupations.is_public_servant")


if __name__ == "__main__":
    run()
