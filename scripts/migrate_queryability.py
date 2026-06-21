"""
数据库可查询性优化 - DDL 迁移脚本
针对 Q1~Q6 查询能力不足的结构优化，不回填旧数据。
执行后使用 migrate_backfill.py 回填数据。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

ALTERS = [
    # ── occupation_salaries ──────────────────────────────────────────────────
    # salary_band: 标准化档位，跨职业同层级薪资对比（Q1/Q6 核心字段）
    """ALTER TABLE occupation_salaries
       ADD COLUMN salary_band ENUM('entry','mid','senior','peak') DEFAULT NULL
         COMMENT '标准化档位：entry=入门/学徒期，mid=3~8年中级，senior=8年+资深，peak=行业顶端/特殊场景'
       AFTER sort_order""",

    # exp_years_min/max: 对应经验年限，用于 Q1 同经验层级精确对比
    """ALTER TABLE occupation_salaries
       ADD COLUMN exp_years_min TINYINT UNSIGNED DEFAULT NULL
         COMMENT '该薪资档对应最低工作年限（年）'
       AFTER salary_band""",

    """ALTER TABLE occupation_salaries
       ADD COLUMN exp_years_max TINYINT UNSIGNED DEFAULT NULL
         COMMENT '该薪资档对应最高工作年限（年），NULL 表示无上限'
       AFTER exp_years_min""",

    # ── occupation_education ─────────────────────────────────────────────────
    # duration_months_min/max: Q2（入行最快）的数字化字段
    """ALTER TABLE occupation_education
       ADD COLUMN duration_months_min SMALLINT UNSIGNED DEFAULT NULL
         COMMENT '教育/培训周期最短月数（用于入行最快查询）'
       AFTER cost_note""",

    """ALTER TABLE occupation_education
       ADD COLUMN duration_months_max SMALLINT UNSIGNED DEFAULT NULL
         COMMENT '教育/培训周期最长月数'
       AFTER duration_months_min""",

    # is_core_path: Q5（学习成本）区分必须/可选路径
    """ALTER TABLE occupation_education
       ADD COLUMN is_core_path TINYINT(1) NOT NULL DEFAULT 1
         COMMENT '是否为主流必要路径：1=是（用于学习成本计算），0=可选/加分项'
       AFTER duration_months_max""",

    # ── occupation_ratings ───────────────────────────────────────────────────
    # score: 1.0~5.0 细分评分，解决同档内无法排序的问题（Q3/Q4/Q6）
    """ALTER TABLE occupation_ratings
       ADD COLUMN score DECIMAL(3,1) DEFAULT NULL
         COMMENT '细分评分 1.0~5.0，精度高于 stars（1~5整数），NULL 时退回 stars 值'
       AFTER stars""",
]

def run():
    with get_cursor() as cur:
        for sql in ALTERS:
            table = sql.split("TABLE")[1].split()[0]
            col   = sql.split("COLUMN")[1].split()[0]
            print(f"  ALTER {table} + {col} ...", end=" ")
            try:
                cur.execute(sql)
                print("OK")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("SKIP (already exists)")
                else:
                    print(f"ERROR: {e}")
                    raise

    print("\n[OK] 所有 DDL 执行完毕，共", len(ALTERS), "条语句")
    print("     下一步：运行 migrate_backfill.py 回填 salary_band / exp_years / duration_months / is_core_path / score")

if __name__ == "__main__":
    run()
