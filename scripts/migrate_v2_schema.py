"""迁移：英文母本 v2 管线的全部新表（幂等，非破坏）。

设计（见会话交接 2026-07-13 之后的英文母本化决策）：
- 母本语言 = 英文；非英文译文走新 TM（translation_src_v2 / translations_v2，主键 sha1(英文)+locale）。
- 复用现有 occupations 主表与跨切面数值卫星表（invitation_scores / occ_search_hits / poll_agg）；
  文本类实体各建自包含 *_v2 镜像表（数值随文本一起进 v2，便于自洽与一次性迁移）。
- 旧的中文母本表与旧 TM 一律不动，后续逐步废弃。

运行：python -m scripts.migrate_v2_schema
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

DDL = [
    # ---- 主表文字（英文母本，1:1）----
    """
    CREATE TABLE IF NOT EXISTS occupations_text_v2 (
      occupation_id INT UNSIGNED NOT NULL PRIMARY KEY COMMENT '关联 occupations.id',
      name          VARCHAR(150) NOT NULL             COMMENT '职业名（英文母本）',
      summary       TEXT                              COMMENT '简介',
      forecast_note TEXT                              COMMENT '需求缺口预测（英文更长，用 TEXT）',
      trend_summary TEXT                              COMMENT '未来趋势',
      updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='职业主文字(英文母本)'
    """,
    # ---- 教育路径 ----
    """
    CREATE TABLE IF NOT EXISTS occupation_education_v2 (
      id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      occupation_id INT UNSIGNED NOT NULL,
      stage         VARCHAR(255) NOT NULL             COMMENT '阶段（英文）',
      duration      VARCHAR(120)                      COMMENT '周期（英文，如 "4 years"）',
      cost_min      DECIMAL(10,2),
      cost_max      DECIMAL(10,2),
      cost_note     VARCHAR(400)                      COMMENT '费用说明（英文）',
      sort_order    TINYINT DEFAULT 0,
      KEY idx_occ (occupation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教育路径(英文母本)'
    """,
    # ---- 从业资质 ----
    """
    CREATE TABLE IF NOT EXISTS occupation_qualifications_v2 (
      id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      occupation_id INT UNSIGNED NOT NULL,
      qual_name     VARCHAR(400) NOT NULL             COMMENT '资质名称（英文）',
      issuer        VARCHAR(400)                      COMMENT '发证机构（英文）',
      note          VARCHAR(400)                      COMMENT '备注（英文）',
      is_mandatory  TINYINT(1) DEFAULT 1,
      sort_order    TINYINT DEFAULT 0,
      KEY idx_occ (occupation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='从业资质(英文母本)'
    """,
    # ---- 收入范围 ----
    """
    CREATE TABLE IF NOT EXISTS occupation_salaries_v2 (
      id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      occupation_id INT UNSIGNED NOT NULL,
      experience    VARCHAR(255) NOT NULL             COMMENT '经验段/口径（英文，如 "Median" / "Mid (3-8 yrs)"）',
      salary_min    DECIMAL(10,2),
      salary_max    DECIMAL(10,2),
      salary_note   VARCHAR(400)                      COMMENT '备注（英文）',
      currency      VARCHAR(8)  DEFAULT 'AUD',
      sort_order    TINYINT DEFAULT 0,
      KEY idx_occ (occupation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收入范围(英文母本)'
    """,
    # ---- 签证/居留路径 ----
    """
    CREATE TABLE IF NOT EXISTS occupation_visa_v2 (
      id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      occupation_id INT UNSIGNED NOT NULL,
      visa_subclass VARCHAR(120) NOT NULL             COMMENT '子类/许可代码或短标签（英文母本）',
      visa_name     VARCHAR(200)                      COMMENT '简称（英文）',
      description   TEXT                              COMMENT '说明（英文）',
      sort_order    TINYINT DEFAULT 0,
      KEY idx_occ (occupation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='签证路径(英文母本)'
    """,
    # ---- 适合/不适合人群 ----
    """
    CREATE TABLE IF NOT EXISTS occupation_suitability_v2 (
      id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      occupation_id INT UNSIGNED NOT NULL,
      type          ENUM('fit','unfit') NOT NULL,
      item          TEXT NOT NULL                     COMMENT '条目（英文）',
      sort_order    TINYINT DEFAULT 0,
      KEY idx_occ (occupation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='适合/不适合(英文母本)'
    """,
    # ---- 评级（label 英文；stars 数值内联）----
    """
    CREATE TABLE IF NOT EXISTS occupation_ratings_v2 (
      id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      occupation_id INT UNSIGNED NOT NULL,
      dimension     VARCHAR(50) NOT NULL,
      label         VARCHAR(120) NOT NULL             COMMENT '档位描述（英文，如 "Moderate-high"）',
      stars         DECIMAL(3,1) NOT NULL             COMMENT '1.0~10.0（10 分制）',
      note          VARCHAR(240),
      UNIQUE KEY uq_occ_dim (occupation_id, dimension),
      KEY idx_occ (occupation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='各维度评级(英文母本)'
    """,
    # ---- FAQ（q/a 英文内联，扁平化 faqs+faqs_i18n）----
    """
    CREATE TABLE IF NOT EXISTS occupation_faqs_v2 (
      id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      occupation_id INT UNSIGNED NOT NULL,
      faq_type      VARCHAR(50),
      question      VARCHAR(600) NOT NULL             COMMENT '问题（英文）',
      answer        TEXT         NOT NULL             COMMENT '回答（英文）',
      sort_order    TINYINT DEFAULT 0,
      KEY idx_occ (occupation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='FAQ(英文母本)'
    """,
    # ---- AI 时代分析（英文文本 + AIOE/分数内联）----
    """
    CREATE TABLE IF NOT EXISTS occupation_ai_v2 (
      occupation_id      INT UNSIGNED NOT NULL PRIMARY KEY,
      verdict_type       ENUM('compressed','amplified','mixed') NOT NULL DEFAULT 'mixed',
      verdict            TEXT           COMMENT 'AI 时代结论一句话（英文）',
      entry_narrowing    TEXT           COMMENT '入门是否变窄（英文）',
      upgrade_path       TEXT           COMMENT '升级路线（英文）',
      replaced           JSON           COMMENT '会被替代任务（英文数组）',
      augmented          JSON           COMMENT '会被增强任务（英文数组）',
      moat               JSON           COMMENT '人类护城河（英文数组）',
      skills             JSON           COMMENT '建议补的技能（英文数组）',
      adjacent           JSON           COMMENT '相邻职业 occ_code 数组',
      cluster            VARCHAR(60),
      automation_exposure DECIMAL(6,3),
      human_moat          DECIMAL(6,3),
      entry_risk          DECIMAL(6,3),
      ai_upside           DECIMAL(6,3),
      aioe_score          DECIMAL(8,4),
      aioe_pct            SMALLINT,
      aioe_soc            VARCHAR(20),
      aioe_method         VARCHAR(40),
      updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='职业AI分析(英文母本)'
    """,
    # ---- AI 工具目录（英文 summary）----
    """
    CREATE TABLE IF NOT EXISTS ai_disruptors_v2 (
      id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      name        VARCHAR(120) NOT NULL              COMMENT '品牌/产品名（不翻译）',
      type        ENUM('tool','platform','product','model','research','news') NOT NULL DEFAULT 'tool',
      vendor      VARCHAR(120),
      url         VARCHAR(300),
      summary     TEXT                               COMMENT '它做什么（英文母本）',
      year        SMALLINT,
      maturity    ENUM('emerging','adopted','mainstream') NOT NULL DEFAULT 'adopted',
      updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      UNIQUE KEY uniq_name (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 工具目录(英文母本)'
    """,
    """
    CREATE TABLE IF NOT EXISTS occupation_ai_disruptor_v2 (
      occupation_id     INT UNSIGNED NOT NULL,
      disruptor_id      INT UNSIGNED NOT NULL,
      replacement_level ENUM('partial','major','full') NOT NULL DEFAULT 'partial',
      scope             TEXT                          COMMENT '替代了哪部分工作（英文母本）',
      evidence_url      VARCHAR(300),
      sort_order        INT NOT NULL DEFAULT 0,
      PRIMARY KEY (occupation_id, disruptor_id),
      KEY idx_disruptor (disruptor_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='职业-AI工具 多对多(英文母本)'
    """,
    # ---- 新翻译记忆（源=英文）----
    """
    CREATE TABLE IF NOT EXISTS translation_src_v2 (
      src_hash  CHAR(40) NOT NULL PRIMARY KEY         COMMENT 'sha1(英文源串)',
      src_text  TEXT NOT NULL                         COMMENT '英文源串',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='TM源串(英文母本)'
    """,
    """
    CREATE TABLE IF NOT EXISTS translations_v2 (
      id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      src_hash  CHAR(40) NOT NULL                     COMMENT '关联 translation_src_v2.src_hash',
      locale    VARCHAR(10) NOT NULL                  COMMENT '目标语（不含 en，en 即源）',
      text      TEXT NOT NULL,
      gen_model VARCHAR(50),
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      UNIQUE KEY uq_hash_locale (src_hash, locale),
      KEY idx_hash (src_hash)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='译文(英文母本 TM)'
    """,
]


def run():
    with get_cursor() as cur:
        for ddl in DDL:
            cur.execute(ddl)
        # 列出已建 v2 表确认
        cur.execute("SHOW TABLES LIKE '%\\_v2'")
        got = [list(r.values())[0] for r in cur.fetchall()]
    print(f"[migrate_v2] 就绪，v2 表 {len(got)} 张：")
    for t in sorted(got):
        print(f"  - {t}")


if __name__ == "__main__":
    run()
