"""迁移：新建 occupation_invitation_scores 表，记录各职业 190/491(及189)的
最近最低获邀分(EOI cut-off)。与 seed 脚本解耦——seed 会清空 occupation_visa_v2，
故获邀分单独存此表，供后续定时任务直接 upsert。幂等。
运行：python -m scripts.migrate_invitation_scores
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor


def run():
    with get_cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS occupation_invitation_scores (
          id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
          occupation_id INT UNSIGNED NOT NULL          COMMENT '关联 occupations.id',
          visa_subclass VARCHAR(20)  NOT NULL           COMMENT '189 / 190 / 491',
          min_score     INT                             COMMENT '最近最低获邀分(EOI cut-off)',
          asof          VARCHAR(40)                      COMMENT '数据时点，如 2025–26',
          note          VARCHAR(200)                     COMMENT '口径说明',
          source_url    VARCHAR(500),
          updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uq_occ_subclass (occupation_id, visa_subclass),
          KEY idx_occupation_id (occupation_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='各职业签证最低获邀分(供定时任务更新)'
        """)
        print("[migrate] occupation_invitation_scores 就绪")


if __name__ == "__main__":
    run()
