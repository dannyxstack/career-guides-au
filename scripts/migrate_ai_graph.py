"""迁移：occupation_ai 增加「AI 职业图谱」字段：cluster + 4 个 1-5 分。
幂等。运行：python -m scripts.migrate_ai_graph
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

COLS = [
    ("cluster", "VARCHAR(40) COMMENT '图谱类别：high_ai_exposure/ai_augmented/licensed_accountable/physical_site_based/human_trust_care/regulated_public_safety'"),
    ("automation_exposure", "TINYINT COMMENT 'AI可自动化程度 1-5，越高越危险'"),
    ("human_moat", "TINYINT COMMENT '人类护城河 1-5，越高越稳'"),
    ("entry_risk", "TINYINT COMMENT '入门岗位压缩程度 1-5，越高越难入门'"),
    ("ai_upside", "TINYINT COMMENT 'AI放大能力 1-5，越高越值得学AI工具'"),
]


def run():
    with get_cursor() as cur:
        for name, ddl in COLS:
            cur.execute("SHOW COLUMNS FROM occupation_ai LIKE %s", (name,))
            if not cur.fetchone():
                cur.execute(f"ALTER TABLE occupation_ai ADD COLUMN {name} {ddl}")
                print(f"[migrate] occupation_ai.{name} 已新增")
            else:
                print(f"[migrate] {name} 已存在")


if __name__ == "__main__":
    run()
