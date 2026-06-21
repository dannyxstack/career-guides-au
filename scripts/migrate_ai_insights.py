"""迁移：新建 occupation_ai 表，记录每个职业的「AI 时代」分析字段。
中文母本列表/句子经翻译记忆(TM)翻成 10 语言；adjacent 存同国 occ_code 列表(前端转链接)。
幂等。运行：python -m scripts.migrate_ai_insights
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor


def run():
    with get_cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS occupation_ai (
          occupation_id      INT UNSIGNED NOT NULL PRIMARY KEY  COMMENT '关联 occupations.id',
          verdict_type       ENUM('compressed','amplified','mixed') NOT NULL DEFAULT 'mixed'
                                COMMENT '被自动化压缩 / 被AI放大 / 混合',
          verdict_zh         VARCHAR(400)   COMMENT 'AI时代风险结论(一句话)',
          entry_narrowing_zh VARCHAR(500)   COMMENT '入门岗位是否变窄(叙述)',
          replaced_zh        JSON           COMMENT 'AI会替代的任务(中文数组)',
          augmented_zh       JSON           COMMENT 'AI会增强的任务(中文数组)',
          moat_zh            JSON           COMMENT '人类护城河(中文数组)',
          skills_zh          JSON           COMMENT '未来5年建议补的技能(中文数组)',
          upgrade_path_zh    VARCHAR(600)   COMMENT 'AI时代升级路线(一段叙述)',
          adjacent           JSON           COMMENT '相邻职业推荐(同国 occ_code 数组)',
          updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='职业AI时代分析'
        """)
        # 已存在的旧表补列（幂等）
        cur.execute("SHOW COLUMNS FROM occupation_ai LIKE 'upgrade_path_zh'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE occupation_ai ADD COLUMN upgrade_path_zh VARCHAR(600) "
                        "COMMENT 'AI时代升级路线(一段叙述)' AFTER skills_zh")
            print("[migrate] occupation_ai.upgrade_path_zh 已补列")
        print("[migrate] occupation_ai 就绪")


if __name__ == "__main__":
    run()
