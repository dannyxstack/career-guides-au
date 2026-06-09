# 会话存档 · career-guides-au 项目

> 更新时间：2026-06-08
> 用途：重启会话后快速恢复上下文，继续任务。

---

## 项目目标

为澳大利亚 **100 个主流职业** 构建一套数据驱动的内容工厂流水线：

1. **搜索真实数据** → 直接入库（MySQL）
2. **从数据库生成** Markdown 职业分析文章
3. 后续扩展：生成网页文章、YouTube 脚本（5~20分钟）、TikTok 脚本（1~2分钟）、Reddit 帖子、X 推文
4. 生成视频，输出发布元信息（标题、简介、SEO 关键词、标签等）

---

## 当前进度

| 阶段 | 状态 | 说明 |
|---|---|---|
| 项目初始化 | ✅ 完成 | 目录结构、依赖、.env |
| 数据库设计 | ✅ 完成 | 18张表，3层架构，无外键 |
| 建库建表 | ✅ 完成 | `python init_db.py` 已执行 |
| 电工数据入库 | ✅ 完成 | `scripts/seed_electrician.py` |
| Markdown 生成器 | ✅ 完成 | 从DB生成，校验通过 |
| 内容生成层（平台脚本） | ⬜ 未开始 | platform_contents 表已建，待接入 AI |
| 视频生成层 | ⬜ 未开始 | video_jobs 表已建 |
| 剩余 99 个职业 | ⬜ 未开始 | 需按 seed_electrician.py 模板逐一搜索入库 |

---

## 工作流（已确认顺序）

```
① 搜索真实数据（WebSearch）
       ↓
② 直接写入 MySQL（scripts/seed_{occupation}.py）
       ↓
③ 从 DB 生成 Markdown（python generate_md.py {anzsco_code}）
       ↓
④ 校验 Markdown（python scripts/check_markdown.py）
       ↓
⑤ [待开发] 从 DB 生成平台内容（web article / YouTube / TikTok / Reddit / X）
       ↓
⑥ [待开发] 生成视频（HeyGen / Runway）
       ↓
⑦ [待开发] 输出发布元信息（标题 / SEO / 标签 / CTA）
```

---

## 项目目录结构

```
career-guides-au/
├── .env                          # MySQL 连接配置（已填写）
├── .env.example                  # 配置模板
├── requirements.txt              # PyMySQL==1.1.1, python-dotenv==1.0.1
├── rules.md                      # Markdown 写作规范（9个部分、评级、FAQ等规则）
├── SESSION_CONTEXT.md            # 本文件
│
├── init_db.py                    # 建库建表（执行一次即可）
├── generate_md.py                # 从DB生成Markdown入口
│   用法: python generate_md.py [anzsco_code] [locale]
│
├── db/
│   ├── connection.py             # get_cursor() 上下文管理器
│   └── schema.sql                # 完整建表语句（18张表，无外键）
│
├── pipeline/
│   ├── importer.py               # 旧流程：解析MD→入库（已被新流程取代，保留备用）
│   ├── parsers/
│   │   └── md_parser.py          # 旧流程：解析Markdown→dict
│   └── generators/
│       └── md_generator.py       # 新流程：从DB读取→生成Markdown
│
├── scripts/
│   ├── seed_electrician.py       # 电工数据（已入库）← 后续职业的模板
│   ├── check_markdown.py         # 格式校验
│   ├── test_db.py                # 数据库连接测试
│   ├── test_parser.py            # 解析器测试（旧流程）
│   └── verify_electrician.py     # 验证电工数据入库结果
│
└── output/
    ├── 341111.md                 # 从DB生成的电工文章（新流程产物）
    └── electrician.md            # 手写的旧版本（可删除或归档）
```

---

## 数据库

- **连接信息**：见 `.env`
- **数据库名**：`career_contents`
- **MySQL版本**：8.4.4

### 18张表（3层架构）

**层1 基础数据（11张）**

| 表名 | 说明 |
|---|---|
| `occupations` | 主表（含职业代码、从业人数、增长方向） |
| `occupations_i18n` | 多语言（名称、简介、趋势描述） |
| `occupation_ratings` | 各维度评级（★1~5） |
| `occupation_education` | 教育路径/费用 |
| `occupation_education_i18n` | 教育路径多语言 |
| `occupation_qualifications` | 从业资质 |
| `occupation_job_listings` | 招聘平台挂牌量快照 |
| `occupation_salaries` | 收入范围 |
| `occupation_salaries_i18n` | 收入范围多语言 |
| `occupation_visa_pathways` | 签证路径 |
| `occupation_suitability` | 适合/不适合人群 |
| `occupation_suitability_i18n` | 适合人群多语言 |
| `occupation_sources` | 数据来源 |
| `occupation_faqs` | FAQ主表 |
| `occupation_faqs_i18n` | FAQ多语言 |

**层2 内容生成（2张）**

| 表名 | 说明 |
|---|---|
| `platform_contents` | 各平台生成内容（web_article/youtube_long/tiktok_short/reddit_post/x_thread） |
| `publish_metadata` | 发布元信息（标题/SEO/标签/CTA） |

**层3 视频生成（1张）**

| 表名 | 说明 |
|---|---|
| `video_jobs` | 视频生成任务（HeyGen/Runway/Sora） |

### 评级维度说明

| dimension | 中文名 | 说明 |
|---|---|---|
| `learning_difficulty` | 学习难度 | |
| `learning_duration` | 学习周期 | |
| `certification_difficulty` | 考证难度 | |
| `job_demand` | 职位需求量 | |
| `competition` | 竞争度 | 星数=竞争激烈程度 |
| `work_intensity` | 工作强度 | |
| `income_level` | 收入水平 | |
| `future_prospect` | 发展前景 | |
| `ai_risk` | AI替代风险 | 星数=风险高低 |
| `pr_friendliness` | PR友好度 | |
| `pr_difficulty` | PR难度 | 星数=难度高低 |

---

## 已完成的职业（1/100）

| 序号 | ANZSCO | 职业 | 入库 | MD生成 |
|---|---|---|---|---|
| 1 | 341111 | 电工 Electrician | ✅ | ✅ |

---

## 待完成的职业列表（99个）

按大类排列，优先完成技工类（移民需求最强）：

**技工类**
水管工、空调技术员（HVAC）、焊工、木工、瓦工/泥水匠、油漆工、屋顶工、汽车技工、柴油机技工、钣金工、起重机操作员、叉车操作员、卡车司机、铁路驾驶员

**医疗健康类**
注册护士、全科医生、牙医、药剂师、兽医、物理治疗师、职业治疗师、放射科技师、验光师、营养师、救护员、心理咨询师

**IT / 工程类**
软件工程师、网络安全工程师、云计算工程师、机器学习工程师、DevOps工程师、数据分析师、IT项目经理、UI/UX设计师、土木工程师、机械工程师、电气工程师、建筑师、工业设计师、环境工程师、矿业工程师、化学工程师、食品工程师

**商业 / 金融 / 法律类**
注册会计师、审计师、税务顾问、金融分析师、保险精算师、抵押贷款经纪、商业分析师、人力资源经理、供应链管理、采购专员、企业培训师、律师、移民中介、房产律师、法务助理

**教育 / 社会服务类**
幼儿教师、小学教师、中学教师、社工、企业培训师

**创意 / 媒体类**
平面设计师、室内设计师、市场营销经理、数字营销专员、公关专员、广告创意、记者、翻译、UI/UX设计师（已在IT类）

**餐饮 / 酒店 / 旅游类**
厨师、面包师、咖啡师、调酒师、餐厅经理、酒店管理、旅游导游

**其他**
航空乘务员、飞行员、船员、消防员、警察、安全官、海关官员、测量师、建筑测量师、建筑工程师、房地产经纪、物业管理、理发师、农业技术员、林业工人、屠宰工

---

## Markdown 文章结构（rules.md 摘要）

每篇职业分析固定 **9个部分**：

1. 教育路径 / 周期 / 费用
2. 考证难度 / 从业资质
3. 职位需求量 / 竞争度 / 工作强度（含招聘平台挂牌量）
4. 收入范围（学徒 / 中级 / 资深）
5. 未来趋势 / AI替代概率
6. 移民路径 / PR难度
7. 适合人群 / 不适合人群（副标题格式：**谁适合学XX？**）
8. 数据来源
9. FAQ 常见问题（8类：薪资/就业/互认/AI/年龄/学历/难度/职业比较）

**关键格式规则：**
- 一级标题下方加 1~2 行职业简介
- 职业代码单行：`**职业代码：XXXXXX – Title。**`
- 结论性评级语句：`**学习难度：中高（★★★★☆）。** 说明文字（不加粗）`
- 所有金额带 `$`，评级带五角星 ★☆

---

## 下一步任务（重启会话后继续）

### 优先级1：批量入库剩余职业
1. 按 `scripts/seed_electrician.py` 模板，每次搜索 1 个职业的真实数据
2. 入库后执行 `python generate_md.py {code}` 生成 Markdown
3. 执行 `python scripts/check_markdown.py` 校验

### 优先级2：开发内容生成层（platform_contents）
- 接入 Claude API（claude-3-5-sonnet）
- 为每个职业生成：web_article / youtube_long / tiktok_short / reddit_post / x_thread
- 写入 `platform_contents` 表

### 优先级3：发布元信息生成
- 生成标题、SEO关键词、标签、CTA
- 写入 `publish_metadata` 表

### 优先级4：视频生成集成
- 对接 HeyGen / Runway API
- 写入 `video_jobs` 表

---

## 常用命令速查

```bash
# 环境
pip install -r requirements.txt

# 数据库
python scripts/test_db.py          # 测试连接
python init_db.py                  # 建库建表（幂等）

# 数据入库
python scripts/seed_electrician.py # 导入电工数据

# 生成 Markdown
python generate_md.py              # 全部职业
python generate_md.py 341111       # 指定职业代码
python generate_md.py 341111 en    # 英文版

# 校验
python scripts/check_markdown.py   # 校验 output/ 所有文件
```
