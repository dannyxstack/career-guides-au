-- ============================================================
-- career_guides_au  数据库 Schema
-- 层1：基础数据层（职业分析结构化存储）
-- 注：不使用外键约束，关联关系由应用层保证
-- ============================================================

-- ------------------------------------------------------------
-- 职业主表（语言无关字段 + 1:1 合并字段）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupations (
  id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  anzsco_code      VARCHAR(20)  NOT NULL UNIQUE COMMENT 'ANZSCO 职业代码，如 341111',
  anzsco_title     VARCHAR(100) NOT NULL        COMMENT '英文职业标准名',
  category         VARCHAR(50)                  COMMENT '职业大类：技工 / 医疗 / IT / 教育',
  workforce_size   INT                          COMMENT '全国从业人数估算',
  shortage_listed  TINYINT(1)   DEFAULT 0       COMMENT '是否在短缺清单 1=是',
  growth_areas     JSON                         COMMENT '主要增长方向，字符串数组',
  created_at       DATETIME     DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='职业主表';


-- ------------------------------------------------------------
-- 多语言翻译表（主表文字字段）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupations_i18n (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id   INT UNSIGNED NOT NULL         COMMENT '关联 occupations.id',
  locale          VARCHAR(10)  NOT NULL          COMMENT 'zh-CN / en / ko',
  name            VARCHAR(100) NOT NULL          COMMENT '职业名称',
  summary         TEXT                           COMMENT '标题下1~2行简介',
  forecast_note   VARCHAR(500)                   COMMENT '需求缺口预测描述',
  trend_summary   TEXT                           COMMENT '未来趋势描述',
  UNIQUE KEY uq_occ_locale (occupation_id, locale),
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='职业主表多语言';


-- ------------------------------------------------------------
-- 第1部分：教育路径 / 周期 / 费用
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_education (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL           COMMENT '关联 occupations.id',
  stage          VARCHAR(100) NOT NULL            COMMENT '阶段名，如：学徒制（含 TAFE）',
  duration       VARCHAR(50)                      COMMENT '周期，如：4年',
  cost_min       DECIMAL(10,2)                    COMMENT '最低费用 AUD',
  cost_max       DECIMAL(10,2)                    COMMENT '最高费用 AUD',
  cost_note      VARCHAR(200)                     COMMENT '补充说明，如：政府补贴后',
  sort_order     TINYINT      DEFAULT 0,
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教育路径';

CREATE TABLE IF NOT EXISTS occupation_education_i18n (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  education_id   INT UNSIGNED NOT NULL            COMMENT '关联 occupation_education.id',
  locale         VARCHAR(10)  NOT NULL,
  stage          VARCHAR(100) NOT NULL,
  cost_note      VARCHAR(200),
  UNIQUE KEY uq_edu_locale (education_id, locale),
  KEY idx_education_id (education_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教育路径多语言';


-- ------------------------------------------------------------
-- 第2部分：从业资质
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_qualifications (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  qual_name      VARCHAR(200) NOT NULL             COMMENT '资质名称',
  issuer         VARCHAR(200)                      COMMENT '发证机构',
  note           VARCHAR(200)                      COMMENT '备注',
  is_mandatory   TINYINT(1)   DEFAULT 1            COMMENT '是否必须',
  sort_order     TINYINT      DEFAULT 0,
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='从业资质';


-- ------------------------------------------------------------
-- 第3部分：招聘平台挂牌量快照
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_job_listings (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  platform       VARCHAR(50)  NOT NULL             COMMENT 'Seek / Indeed / LinkedIn',
  count_min      INT                               COMMENT '挂牌量下限',
  count_max      INT                               COMMENT '挂牌量上限',
  note           VARCHAR(200),
  snapshot_date  DATE                              COMMENT '数据采集日期',
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台职位挂牌量';


-- ------------------------------------------------------------
-- 第4部分：收入范围
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_salaries (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  experience     VARCHAR(100) NOT NULL             COMMENT '经验段，如：中级电工（3~8年）',
  salary_min     DECIMAL(10,2)                     COMMENT '薪资下限 AUD',
  salary_max     DECIMAL(10,2)                     COMMENT '薪资上限 AUD',
  salary_note    VARCHAR(200)                      COMMENT '备注',
  sort_order     TINYINT      DEFAULT 0,
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收入范围';

CREATE TABLE IF NOT EXISTS occupation_salaries_i18n (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  salary_id   INT UNSIGNED NOT NULL               COMMENT '关联 occupation_salaries.id',
  locale      VARCHAR(10)  NOT NULL,
  experience  VARCHAR(100) NOT NULL,
  salary_note VARCHAR(200),
  UNIQUE KEY uq_sal_locale (salary_id, locale),
  KEY idx_salary_id (salary_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收入范围多语言';


-- ------------------------------------------------------------
-- 第6部分：签证路径
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_visa_pathways (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  visa_subclass  VARCHAR(20)  NOT NULL             COMMENT '签证子类，如：186',
  visa_name      VARCHAR(100)                      COMMENT '签证简称，如：ENS',
  description    VARCHAR(300)                      COMMENT '说明',
  sort_order     TINYINT      DEFAULT 0,
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='签证路径';


-- ------------------------------------------------------------
-- 第7部分：适合 / 不适合人群
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_suitability (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  type           ENUM('fit','unfit') NOT NULL,
  item           VARCHAR(300) NOT NULL,
  sort_order     TINYINT      DEFAULT 0,
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='适合/不适合人群';

CREATE TABLE IF NOT EXISTS occupation_suitability_i18n (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  suitability_id  INT UNSIGNED NOT NULL           COMMENT '关联 occupation_suitability.id',
  locale          VARCHAR(10)  NOT NULL,
  item            VARCHAR(300) NOT NULL,
  UNIQUE KEY uq_suit_locale (suitability_id, locale),
  KEY idx_suitability_id (suitability_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='适合人群多语言';


-- ------------------------------------------------------------
-- 评级表（所有维度）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_ratings (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  dimension      VARCHAR(50)  NOT NULL             COMMENT 'learning_difficulty / job_demand / ai_risk ...',
  label_zh       VARCHAR(20)  NOT NULL             COMMENT '中文评级描述，如：中高',
  stars          TINYINT      NOT NULL             COMMENT '1~5',
  note           VARCHAR(200),
  UNIQUE KEY uq_occ_dim (occupation_id, dimension),
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='各维度评级';


-- ------------------------------------------------------------
-- 第8部分：数据来源
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_sources (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  source_name    VARCHAR(200) NOT NULL,
  content        VARCHAR(300),
  url            VARCHAR(500),
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据来源';


-- ------------------------------------------------------------
-- 第9部分：FAQ
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS occupation_faqs (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id  INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  faq_type       VARCHAR(50)                       COMMENT 'salary/demand/recognition/ai_risk/age_limit/education_limit/difficulty/comparison',
  sort_order     TINYINT      DEFAULT 0,
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='FAQ主表';

CREATE TABLE IF NOT EXISTS occupation_faqs_i18n (
  id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  faq_id    INT UNSIGNED NOT NULL                 COMMENT '关联 occupation_faqs.id',
  locale    VARCHAR(10)  NOT NULL,
  question  VARCHAR(300) NOT NULL,
  answer    TEXT         NOT NULL,
  UNIQUE KEY uq_faq_locale (faq_id, locale),
  KEY idx_faq_id (faq_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='FAQ多语言';


-- ============================================================
-- 层2：内容生成层
-- ============================================================

CREATE TABLE IF NOT EXISTS platform_contents (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  occupation_id   INT UNSIGNED NOT NULL            COMMENT '关联 occupations.id',
  locale          VARCHAR(10)  NOT NULL,
  platform        ENUM('web_article','youtube_long','tiktok_short','reddit_post','x_thread') NOT NULL,
  status          ENUM('draft','reviewing','approved','published') DEFAULT 'draft',
  gen_model       VARCHAR(50)                       COMMENT '生成模型，如：claude-3-7-sonnet',
  gen_prompt_ver  VARCHAR(20)                       COMMENT 'Prompt模板版本号',
  body            LONGTEXT                          COMMENT '正文 / 脚本全文',
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_occ_locale_platform (occupation_id, locale, platform),
  KEY idx_occupation_id (occupation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='各平台生成内容';

CREATE TABLE IF NOT EXISTS publish_metadata (
  id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  content_id       INT UNSIGNED NOT NULL            COMMENT '关联 platform_contents.id',
  title            VARCHAR(300),
  description      TEXT                              COMMENT '平台简介 / About',
  tags             JSON                              COMMENT '标签数组',
  seo_keywords     JSON                              COMMENT 'SEO关键词，针对 web_article',
  thumbnail_url    VARCHAR(500),
  cta              VARCHAR(300)                      COMMENT 'Call to Action 文案',
  publish_url      VARCHAR(500)                      COMMENT '发布后的链接',
  published_at     DATETIME,
  KEY idx_content_id (content_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='发布元信息';


-- ============================================================
-- 层3：视频生成层
-- ============================================================

CREATE TABLE IF NOT EXISTS video_jobs (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  content_id      INT UNSIGNED NOT NULL             COMMENT '关联 platform_contents.id',
  tool            VARCHAR(50)                        COMMENT 'HeyGen / Runway / Sora',
  status          ENUM('pending','processing','done','failed') DEFAULT 'pending',
  input_payload   JSON                               COMMENT '传给视频工具的参数',
  output_url      VARCHAR(500)                       COMMENT '生成视频存储地址',
  duration_sec    INT                                COMMENT '视频时长（秒）',
  error_msg       TEXT,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_content_id (content_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='视频生成任务';
