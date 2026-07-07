# -*- coding: utf-8 -*-
"""热门职业搜索量建表。

occ_search_hits：首页「热门职业搜索」板块的数据源。
- (country_code, slug) 唯一 → 每行=某国的某职业。
- hits      : 未来真实搜索/点击量累加（入库端点上线后写）。
- seed_score: 启发式预填充分（临时热度，见 seed_hot_occupations.py）。
- 热度 = hits + seed_score；构建期按此降序取 top-N。

运行：python -m scripts.seed_hot_occupations_schema
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

DDL = [
    """CREATE TABLE IF NOT EXISTS occ_search_hits (
        country_code VARCHAR(4)   NOT NULL,
        slug         VARCHAR(160)  NOT NULL,
        hits         BIGINT UNSIGNED NOT NULL DEFAULT 0,
        seed_score   INT UNSIGNED    NOT NULL DEFAULT 0,
        updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (country_code, slug),
        KEY idx_score (seed_score)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热门职业搜索量(真实hits+启发式seed)'""",
]


def run():
    with get_cursor() as cur:
        for ddl in DDL:
            cur.execute(ddl)
    print("[OK] occ_search_hits 建表完成")


if __name__ == "__main__":
    run()
