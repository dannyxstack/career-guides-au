"""
初始化数据库：
1. 创建 database（若不存在）
2. 执行 db/schema.sql 建表
用法：python init_db.py
"""

import os
import re
import pymysql
from dotenv import load_dotenv

load_dotenv()


def create_database_if_not_exists():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        charset=os.getenv("MYSQL_CHARSET", "utf8mb4"),
    )
    db_name = os.getenv("MYSQL_DATABASE", "career_guides_au")
    with conn.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    conn.commit()
    conn.close()
    print(f"[OK] Database `{db_name}` ready.")


def run_schema():
    schema_path = os.path.join(os.path.dirname(__file__), "db", "schema.sql")
    with open(schema_path, encoding="utf-8") as f:
        sql = f.read()

    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "career_guides_au"),
        charset=os.getenv("MYSQL_CHARSET", "utf8mb4"),
    )

    # 按分号切割逐条执行，跳过空语句和纯注释块
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    created = 0
    with conn.cursor() as cursor:
        for stmt in statements:
            # 跳过纯注释行
            if all(line.startswith("--") for line in stmt.splitlines() if line.strip()):
                continue
            cursor.execute(stmt)
            m = re.search(
                r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?',
                stmt, re.IGNORECASE
            )
            if m:
                print(f"  [table] {m.group(1)}")
                created += 1
    conn.commit()
    conn.close()
    print(f"[OK] Schema applied. {created} tables created/verified.")


if __name__ == "__main__":
    create_database_if_not_exists()
    run_schema()
