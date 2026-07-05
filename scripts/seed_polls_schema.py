# -*- coding: utf-8 -*-
"""投票功能建表（通用投票引擎，装 N 个投票，见 site/src/data/polls.json）。

- poll_votes    : 明细票，(poll_code, occ_key, client_token) 唯一 → 一人一票·可改票(upsert)
- poll_agg      : 单选聚合，供 O(1) 读 + 构建期烘焙（每次投票后按 occ_key 重算）
- poll_agg_num  : 数值(滑块)型聚合，本期两个投票都是单选，留给未来

occ_key = 职业 slug（跨国共享）。运行：python -m scripts.seed_polls_schema
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

DDL = [
    """CREATE TABLE IF NOT EXISTS poll_votes (
        id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        poll_code    VARCHAR(40)  NOT NULL,
        occ_key      VARCHAR(160) NOT NULL,
        client_token CHAR(32)     NOT NULL,
        answer_key   VARCHAR(40)  NULL,
        answer_num   SMALLINT     NULL,
        ip_hash      CHAR(64)     NULL,
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uq_vote (poll_code, occ_key, client_token),
        KEY idx_occ (poll_code, occ_key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投票明细'""",
    """CREATE TABLE IF NOT EXISTS poll_agg (
        poll_code  VARCHAR(40)  NOT NULL,
        occ_key    VARCHAR(160) NOT NULL,
        answer_key VARCHAR(40)  NOT NULL,
        cnt        INT UNSIGNED NOT NULL DEFAULT 0,
        PRIMARY KEY (poll_code, occ_key, answer_key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='单选投票聚合(供烘焙)'""",
    """CREATE TABLE IF NOT EXISTS poll_agg_num (
        poll_code VARCHAR(40)  NOT NULL,
        occ_key   VARCHAR(160) NOT NULL,
        n         INT UNSIGNED NOT NULL DEFAULT 0,
        sum       BIGINT       NOT NULL DEFAULT 0,
        PRIMARY KEY (poll_code, occ_key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数值(滑块)投票聚合'""",
]


def run():
    with get_cursor() as cur:
        for ddl in DDL:
            cur.execute(ddl)
    print("[OK] poll_votes / poll_agg / poll_agg_num 建表完成")


if __name__ == "__main__":
    run()
