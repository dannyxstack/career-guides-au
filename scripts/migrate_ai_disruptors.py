"""迁移：AI「已替代/部分替代」工具目录 + 职业多对多关联。

- ai_disruptors：全站共享的工具/产品/研究/新闻目录（品牌名不翻译，summary_zh 走 TM）。
- occupation_ai_disruptor：职业 ↔ 工具 关联，记录"替代了该职业的哪部分工作"与影响程度。
一个工具可挂多个职业；前端据此显示"也影响：XX"。幂等。
运行：python -m scripts.migrate_ai_disruptors
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor


def run():
    with get_cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_disruptors (
          id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          name        VARCHAR(120) NOT NULL                COMMENT '品牌/产品名（不翻译）',
          type        ENUM('tool','platform','product','model','research','news') NOT NULL DEFAULT 'tool'
                                                           COMMENT '类型',
          vendor      VARCHAR(120)                         COMMENT '厂商/机构',
          url         VARCHAR(300)                         COMMENT '官网/产品链接',
          summary_zh  VARCHAR(400)                         COMMENT '它做什么（中文母本，走 TM）',
          year        SMALLINT                             COMMENT '出现/走红年份',
          maturity    ENUM('emerging','adopted','mainstream') NOT NULL DEFAULT 'adopted'
                                                           COMMENT '成熟度',
          updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uniq_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 替代工具/产品目录'
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS occupation_ai_disruptor (
          occupation_id     INT UNSIGNED NOT NULL          COMMENT '关联 occupations.id',
          disruptor_id      INT UNSIGNED NOT NULL          COMMENT '关联 ai_disruptors.id',
          replacement_level ENUM('partial','major','full') NOT NULL DEFAULT 'partial'
                                                           COMMENT '对该职业的替代程度',
          scope_zh          VARCHAR(400)                   COMMENT '替代了该职业的哪部分工作（中文母本，走 TM）',
          evidence_url      VARCHAR(300)                   COMMENT '证据/新闻/研究链接',
          sort_order        INT NOT NULL DEFAULT 0,
          PRIMARY KEY (occupation_id, disruptor_id),
          KEY idx_disruptor (disruptor_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='职业-AI工具 多对多'
        """)
        print("[migrate] ai_disruptors / occupation_ai_disruptor 就绪")


if __name__ == "__main__":
    run()
