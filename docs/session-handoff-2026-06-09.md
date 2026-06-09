# 会话交接文档 · 2026-06-09

> 本文档供重置会话后继续项目使用，记录已完成工作、当前状态和待办事项。

---

## 项目概况

- **项目路径**：`E:/work/career-guides-au/`
- **数据库**：MySQL，库名 `career_contents`
- **内容目录**：`career-contents/au/`（职业 Markdown 文件，英文 slug 命名）
- **脚本目录**：`scripts/`（seed_*.py 入库脚本；`_seed_helper.py` 为公共入库函数）
- **规则文件**：`rules.md`（Markdown 写作规范）

---

## 已完成工作

### 1. 职业数据入库（所有类别）

共完成 92 个职业，已全部入库并生成 Markdown。最后一批为"其他"类（14条记录）：

| 脚本 | ANZSCO | 职业 |
|---|---|---|
| seed_flight_attendant.py | 451711 | 空乘 |
| seed_pilot.py | 231111 | 飞行员 |
| seed_seafarer.py | 231212 | 海员/引航员 |
| seed_firefighter.py | 441211 | 消防员 |
| seed_police_officer.py | 441111 | 警察 |
| seed_security_officer.py | 442217 | 保安 |
| seed_customs_officer.py | 441312 | 海关官员 |
| seed_land_surveyor.py | 232611 | 测量师/建筑测量师（合并） |
| seed_construction_manager.py | 133111 | 建筑项目经理 |
| seed_real_estate_agent.py | 612112 | 房地产经纪/物业管理（合并） |
| seed_hairdresser.py | 391111 | 理发师/美容师（合并） |
| seed_agricultural_technician.py | 311111 | 农业技术员/农艺师 |
| seed_arborist.py | 362211 | 树艺师 |
| seed_meat_worker.py | 362111 | 肉类加工工人 |

### 2. Markdown 文件重命名

所有 92 个文件从 ANZSCO 编号（如 `341111.md`）重命名为英文 slug（如 `electrician.md`），存放于 `career-contents/au/`。

Slug 转换规则：
```python
import re
def to_slug(name):
    s = name.lower()
    s = re.sub(r'[/()\[\]]', ' ', s)
    s = re.sub(r'[^a-z0-9 ]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'-+', '-', s)
    return s
```
英文名取 `occupations_i18n`（`locale='en'`）中的 `name` 字段。

### 3. rules.md 更新

- "PR难点" → "PR难度"（第4部分结构列表和表格列表）
- 新增"文件输出路径与命名规则"章节（`career-contents/au/`，英文 slug 命名）

### 4. 数据库多国扩展

已执行：
```sql
-- occupations 表新增多国字段
ALTER TABLE occupations
  ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'AU',
  ADD COLUMN occ_code VARCHAR(20) NOT NULL DEFAULT '',
  ADD COLUMN occ_code_type VARCHAR(20) NOT NULL DEFAULT 'ANZSCO';
UPDATE occupations SET occ_code = anzsco_code;
ALTER TABLE occupations DROP INDEX anzsco_code;
ALTER TABLE occupations ADD UNIQUE KEY uq_country_occ_code (country_code, occ_code);

-- 薪资和教育表新增货币字段
ALTER TABLE occupation_salaries ADD COLUMN currency CHAR(3) NOT NULL DEFAULT 'AUD';
ALTER TABLE occupation_education ADD COLUMN currency CHAR(3) NOT NULL DEFAULT 'AUD';
```

支持扩展：NZ（NZD/ANZSCO）、CA（CAD/NOC）、US（USD/O*NET）、UK（GBP/SOC）、DE（EUR/KldB）、FR（EUR/PCS）。

### 5. 可查询性优化 DDL（本次会话最后执行）

已执行（`scripts/migrate_queryability.py`），**新增 7 个字段，均未回填数据**：

| 表 | 新字段 | 类型 | 用途 |
|---|---|---|---|
| occupation_salaries | salary_band | ENUM('entry','mid','senior','peak') | Q1/Q6：跨职业同层级薪资对比 |
| occupation_salaries | exp_years_min | TINYINT UNSIGNED | Q1：最低经验年限 |
| occupation_salaries | exp_years_max | TINYINT UNSIGNED | Q1：最高经验年限（NULL=无上限） |
| occupation_education | duration_months_min | SMALLINT UNSIGNED | Q2：入行最快（数字化周期） |
| occupation_education | duration_months_max | SMALLINT UNSIGNED | Q2：入行周期上限 |
| occupation_education | is_core_path | TINYINT(1) DEFAULT 1 | Q5：是否主流必要路径 |
| occupation_ratings | score | DECIMAL(3,1) | Q3/Q4/Q6：细分评分（1.0~5.0） |

---

## 待办事项

### 优先级 1：回填新字段数据

这是重置会话后的**第一件事**。需要为 92 个职业的每条记录回填：

#### A. `occupation_salaries.salary_band`（最重要，Q6 核心）

标准化档位定义：
- `entry`：入门/学徒期（通常 0~3 年，无执照）
- `mid`：中级（通常 3~8 年，持牌/有经验）
- `senior`：资深（8 年+）
- `peak`：行业顶端/特殊场景（如 FIFO矿区、专科医生私诊）

回填策略：根据每条记录的 `experience` 字段文本判断档位。建议写一个 Python 脚本，用关键词匹配批量更新，然后人工复核异常项。

关键词参考：
```python
BAND_RULES = [
    ('peak',   ['fifo', 'mining', '矿区', '顶端', '专科私', '高端私']),
    ('senior', ['高级', 'senior', '8年', '10年', '15年', '资深', 'principal']),
    ('mid',    ['中级', 'mid', '3~8年', '3-8年', '持牌', '有经验', 'experienced']),
    ('entry',  ['初级', 'entry', '学徒', 'apprentice', '0~3年', '毕业', '新手']),
]
```

#### B. `occupation_salaries.exp_years_min / exp_years_max`

从 `experience` 字段提取年限数字。例：
- "初级（0~3年）" → min=0, max=3
- "中级（3~8年）" → min=3, max=8
- "高级（8年+）" → min=8, max=NULL
- "FIFO矿区" → min=NULL, max=NULL（特殊场景）

#### C. `occupation_education.duration_months_min / duration_months_max`

从 `duration` 字段提取数字并转换为月数。例：
- "3~4年" → min=36, max=48
- "6~24个月" → min=6, max=24
- "4年" → min=48, max=48
- "1~3天" → min=0, max=0（跳过，不计入从业周期）

#### D. `occupation_education.is_core_path`

默认已为 1（必要路径）。需要将**可选/加分项**改为 0。

通常设为 0 的情形：
- 技能移民评估（Vetassess/TRA/ANMAC 等）——移民工具，不是从业必须
- 驾驶执照（MR+/HR）——部分职业加分项
- 无人机执照、额外认证——非核心从业要求

建议：默认保持 1，只手动将评估机构和可选证书改为 0。

#### E. `occupation_ratings.score`

精度高于 `stars` 的细分评分（1.0~5.0）。可暂时用 `stars * 1.0` 作为初始值，之后精细调整。

初始回填 SQL（可直接执行）：
```sql
UPDATE occupation_ratings SET score = stars * 1.0 WHERE score IS NULL;
```

---

### 优先级 2：验证查询可用性

回填后，运行以下测试查询确认效果：

```sql
-- Q6：收入与电工相当（mid档）但竞争更低的职业
SELECT i.name, s.salary_min, s.salary_max, comp.stars AS comp_stars
FROM occupations ref
JOIN occupation_salaries ref_s ON ref_s.occupation_id = ref.id AND ref_s.salary_band = 'mid'
JOIN occupation_salaries s ON s.salary_band = 'mid'
  AND s.salary_max BETWEEN ref_s.salary_min * 0.85 AND ref_s.salary_max * 1.15
JOIN occupations o ON o.id = s.occupation_id
JOIN occupations_i18n i ON i.occupation_id = o.id AND i.locale = 'zh-CN'
JOIN occupation_ratings comp ON comp.occupation_id = o.id AND comp.dimension = 'competition'
WHERE ref.occ_code = '341111' AND ref.country_code = 'AU'
  AND o.occ_code != '341111'
  AND comp.stars < (
    SELECT r.stars FROM occupation_ratings r
    JOIN occupations x ON r.occupation_id = x.id
    WHERE x.occ_code = '341111' AND r.dimension = 'competition'
  )
ORDER BY comp.stars ASC, s.salary_max DESC
LIMIT 10;

-- Q2：入行最快（核心路径最短周期）
SELECT i.name, MIN(e.duration_months_min) AS min_months
FROM occupations o
JOIN occupations_i18n i ON i.occupation_id = o.id AND i.locale = 'zh-CN'
JOIN occupation_education e ON e.occupation_id = o.id AND e.is_core_path = 1
WHERE e.duration_months_min IS NOT NULL
GROUP BY o.id, i.name
ORDER BY min_months ASC
LIMIT 10;
```

---

### 优先级 3：内容生成继续（如有新职业类别）

目前已覆盖类别：
- IT / 医疗 / 工程 / 金融 / 教育 / 法律 / 建筑设计 / 交通运输 / 餐饮食品 / 零售服务 / 制造维修 / 农林渔牧 / 创意媒体 / 其他

如需扩展新西兰（NZ）内容，需要新建种子脚本，`country_code='NZ'`，`occ_code_type='ANZSCO'`（NZ 也用 ANZSCO），`currency='NZD'`。

---

## 数据库 Schema 速查

```sql
-- 核心表关系
occupations (id, country_code, occ_code, occ_code_type, anzsco_code, category, workforce_size, shortage_listed, growth_areas)
  → occupations_i18n        (locale, name, summary, forecast_note, trend_summary)
  → occupation_salaries      (currency, experience, salary_min, salary_max, salary_note, sort_order, salary_band, exp_years_min, exp_years_max)
  → occupation_education     (currency, stage, duration, cost_min, cost_max, cost_note, sort_order, duration_months_min, duration_months_max, is_core_path)
  → occupation_ratings       (dimension, label_zh, stars, score, note)
  → occupation_visa_pathways (visa_subclass, visa_name, description, sort_order)
  → occupation_qualifications(qual_name, issuer, note, is_mandatory, sort_order)
  → occupation_job_listings  (platform, count_min, count_max, note)
  → occupation_faqs          (faq_type, sort_order, question, answer)
  → occupation_suitability   (fit_type ENUM('fit','unfit'), description, sort_order)
  → occupation_sources       (source_name, content, url, sort_order)

-- 多国唯一键
UNIQUE KEY uq_country_occ_code (country_code, occ_code)

-- occupation_ratings.dimension 枚举值
learning_difficulty | learning_duration | certification_difficulty
job_demand | competition | work_intensity | income_level
future_prospect | ai_risk | pr_friendliness | pr_difficulty
```

---

## 文件命名约定

| 类型 | 位置 | 命名 |
|---|---|---|
| 职业 Markdown | `career-contents/au/` | 英文 slug + `.md`，如 `electrician.md` |
| 入库种子脚本 | `scripts/` | `seed_<英文slug下划线>.py` |
| 数据库迁移脚本 | `scripts/` | `migrate_<描述>.py` |
| 本文档 | `docs/` | `session-handoff-YYYY-MM-DD.md` |

---

## 快速恢复命令

```bash
# 验证数据库连接
cd E:/work/career-guides-au
python -c "from db.connection import get_cursor; print('DB OK')"

# 查看当前职业总数
python -c "
import sys; sys.path.insert(0,'.')
from db.connection import get_cursor
with get_cursor() as cur:
    cur.execute('SELECT COUNT(*) as n FROM occupations WHERE country_code=\"AU\"')
    print('AU occupations:', cur.fetchone()['n'])
"

# 回填 score 初始值（优先级2E，可直接执行）
python -c "
import sys; sys.path.insert(0,'.')
from db.connection import get_cursor
with get_cursor() as cur:
    cur.execute('UPDATE occupation_ratings SET score = stars * 1.0 WHERE score IS NULL')
    print('Updated:', cur.rowcount, 'rows')
"
```
