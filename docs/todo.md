# 项目待办总览

> 最后更新：2026-06-10（第一批92个+第二批99个，合计191个AU职业已全部入库）

---

## 已完成 ✅

### 第一批职业入库（92个，AU）

涵盖类别：IT/科技、工程、建筑管理、医疗健康、金融商业、教育/心理、餐饮/酒店、零售服务、维修制造、农林渔牧、创意媒体、交通运输、政府/其他。

完整名单见 `session-handoff-2026-06-09.md`。

---

## 数据库任务

### ✅ 已完成

- [x] 多国字段扩展（country_code / occ_code / occ_code_type / currency）
- [x] 可查询性字段新增（salary_band / exp_years_min/max / duration_months_min/max / is_core_path / score）
- [x] `stars` 精度升级：tinyint → decimal(3,1)
- [x] `score` 方案A回填：`score = stars`（1012条，全部完成）
- [x] `stars` 精度升级：tinyint → decimal(3,1)
- [x] **`salary_band` 全量回填**：411条（entry 121 / mid 106 / senior 140 / peak 44），脚本 `scripts/backfill_fields.py` + 27条手动补填
- [x] **`exp_years_min / exp_years_max` 全量回填**：353条文本提取 + 55条手动补填，全部非NULL
- [x] **`duration_months_min / duration_months_max` 回填**：273条文本提取，24条"持续/自主学习"类正确保持NULL
- [x] **`is_core_path` 复核**：59条可选路径（技能评估机构、可选证书等）改为 0

### 🔲 待办

- [ ] **（后期）**：针对 `competition`、`income_level`、`job_demand` 三个 dimension 做 score 精细化（方案B，Web检索），提升 Q6 跨职业比较精度

---

## 内容生成任务

### 第二批职业名单（约100个，AU）

> 来源：Jobs and Skills Australia 紧缺职业表（2025-26）、Core Skills Occupation List（CSOL 456职业）、Seek/LinkedIn/Indeed 高频招聘岗位、用户补充需求。
> 状态：**待入库**，尚未检索数据。

#### 建筑与施工 ✅（16/16 已入库）

| # | 职业（中文） | 职业（英文） | ANZSCO | 状态 |
|---|---|---|---|---|
| 1 | 钢筋工 | Steel Fixer | 821713 | ✅ |
| 2 | 脚手架工 | Scaffolder | 821712 | ✅ |
| 3 | 起重指挥/索具工 | Dogman / Construction Rigger | 821711 | ✅ |
| 4 | 混凝土工 | Concreter | 821211 | ✅ |
| 5 | 模板木工 | Formwork Carpenter | 331212 | ✅ |
| 6 | 抹灰工 | Plasterer | 333211 | ✅ |
| 7 | 贴砖工 | Wall and Floor Tiler | 333111 | ✅ |
| 8 | 玻璃工 | Glazier | 333311 | ✅ |
| 9 | 地板铺设工 | Floor Finisher | 394111 | ✅ |
| 10 | 燃气安装工 | Gas Fitter | 334112 | ✅ |
| 11 | 消防管道工 | Fire Protection Plumber | 334114 | ✅ |
| 12 | 建筑绘图师 | Building Draftsperson / Drafting Technician | 312111 | ✅ |
| 13 | 工程造价师/估价员 | Quantity Surveyor | 233213 | ✅ |
| 14 | 合同管理员 | Contract Administrator | 511112 | ✅ |
| 15 | 建筑检查员 | Building Inspector / Surveyor | 312116 | ✅ |
| 16 | 设施管理员 | Facilities Manager | 149913 | ✅ |

#### 电气 / 可再生能源 ✅（5/5 已入库）

| # | 职业（中文） | 职业（英文） | ANZSCO | 状态 |
|---|---|---|---|---|
| 17 | 太阳能安装工 | Solar Panel Installer / Solar PV Installer | 342113 | ✅ |
| 18 | 风力涡轮机技术员 | Wind Turbine Technician | 342114 | ✅ |
| 19 | 仪表技术员 | Instrumentation Technician | 312311 | ✅ |
| 20 | 电力线工 | Electrical Linesperson | 341112 | ✅ |
| 21 | 楼宇自动化技术员 | Building Automation / BMS Technician | 342115 | ✅ |

#### 制造 / 工业 ✅（9/9 已入库）

#### 采矿 / 资源 ✅（6/6 已入库）

#### 工程延伸 ✅（7/7 已入库）

#### IT/数字化延伸 ✅（8/8 已入库）

#### 医疗健康延伸 ✅（13/13 已入库）

#### 教育延伸 ✅（5/5 已入库）

#### 农业/环境 ✅（7/7 已入库）

#### 运输/物流延伸 ✅（5/5 已入库）

#### 商业/金融延伸 ✅（9/9 已入库）

#### 专业服务/其他 ✅（10/10 已入库）

| # | 职业（中文） | 职业（英文） | ANZSCO | 状态 |
|---|---|---|---|---|
| 22 | 锅炉工 | Boilermaker | 322111 | ✅ |
| 23 | 模具制造工 | Toolmaker | 323211 | ✅ |
| 24 | 数控机床操作工 | CNC Machinist / Precision Metal Trades Worker | 323214 | ✅ |
| 25 | 管道安装工（工业） | Pipefitter / Mechanical Services Plumber | 334115 | ✅ |
| 26 | 制冷/冷冻技师 | Refrigeration and Air Conditioning Mechanic | 342112 | ✅ |
| 27 | 工业设备维修工 | Industrial Machinery Mechanic | 323312 | ✅ |
| 28 | 汽车钣金工 | Panel Beater | 324111 | ✅ |
| 29 | 汽车喷漆工 | Motor Vehicle Body Painter | 324211 | ✅ |
| 30 | 电子技术员 | Electronics Technician | 315111 | ✅ |

#### 采矿 / 资源

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 31 | 地下矿工 | Underground Miner | 811511 |
| 32 | 钻探操作工 | Driller (Mining/Mineral Exploration) | 712212 |
| 33 | 采矿机械操作工 | Mining Machine Operator | 811611 |
| 34 | 爆破工 | Shot Firer / Blaster | 712611 |
| 35 | 矿山测量师 | Mine Surveyor | 232612 |
| 36 | 选矿/湿法冶金技术员 | Mineral Processing / Metallurgical Technician | 311411 |

#### 工程（延伸）

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 37 | 结构工程师 | Structural Engineer | 233214 |
| 38 | 岩土工程师 | Geotechnical Engineer | 233215 |
| 39 | 水资源工程师 | Water Resources / Hydraulic Engineer | 233911 |
| 40 | 过程/控制工程师 | Process / Control Systems Engineer | 233912 |
| 41 | 消防安全工程师 | Fire Safety / Fire Protection Engineer | 233999 |
| 42 | 项目工程师 | Project Engineer | 233215 |
| 43 | 测量/质量工程师 | Quality / NDT Engineer | 233916 |

#### IT / 数字化（延伸）

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 44 | 网络工程师 | Network Engineer / Administrator | 263211 |
| 45 | 数据库管理员 | Database Administrator | 262113 |
| 46 | IT技术支持 | ICT Support Technician / Helpdesk | 313113 |
| 47 | ERP顾问 | ERP / SAP Consultant | 225113 |
| 48 | 商业智能分析师 | Business Intelligence (BI) Analyst | 262112 |
| 49 | iOS/Android开发工程师 | Mobile App Developer | 261312 |
| 50 | 测试工程师 | QA / Software Test Engineer | 261314 |
| 51 | IT项目协调员 | IT Project Coordinator | 135111 |

#### 医疗健康（延伸）

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 52 | 助产士 | Midwife | 254111 |
| 53 | 老年护理工 | Aged Care Worker | 423111 |
| 54 | 残障支持工 | Disability Support Worker | 423312 |
| 55 | 言语治疗师 | Speech Pathologist | 252711 |
| 56 | 超声波技师 | Sonographer / Medical Ultrasonographer | 251213 |
| 57 | 放射治疗师 | Radiation Therapist | 251212 |
| 58 | 心理健康护士 | Mental Health Nurse | 254423 |
| 59 | 登记护士 | Enrolled Nurse | 411411 |
| 60 | 牙科治疗师/洁牙师 | Dental Therapist / Dental Hygienist | 411111 |
| 61 | 足科医师 | Podiatrist | 252611 |
| 62 | 脊椎/整骨治疗师 | Chiropractor | 252311 |
| 63 | 医疗实验室科学家 | Medical Laboratory Scientist | 234611 |
| 64 | 急诊/手术室技师 | Anaesthetic / Surgical Technician | 411211 |

#### 教育（延伸）

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 65 | 儿童护理工 | Childcare Worker | 421111 |
| 66 | 教学助理 | Teacher Aide | 422115 |
| 67 | 特殊教育教师 | Special Education Teacher | 241511 |
| 68 | TESOL/英语教师 | English as Second Language (ESL/TESOL) Teacher | 249111 |
| 69 | 职业培训师（TAFE） | VET / TAFE Trainer and Assessor | 242211 |

#### 农业 / 环境

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 70 | 农场经理 | Farm Manager | 121311 |
| 71 | 水产养殖工 | Aquaculture / Fishing Worker | 841211 |
| 72 | 葡萄种植工/酒庄员工 | Viticulture Worker / Vineyard Hand | 841211 |
| 73 | 园林工/景观设计师 | Landscaper / Landscape Gardener | 362312 |
| 74 | 自然保护区巡护员 | Park Ranger / Conservation Officer | 234412 |
| 75 | 水处理操作员 | Water / Wastewater Treatment Operator | 712914 |
| 76 | 环境顾问 | Environmental Consultant | 234312 |

#### 运输 / 物流（延伸）

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 77 | 航空维修工程师 | Aircraft Maintenance Engineer (LAME) | 321111 |
| 78 | 仓库/物流主管 | Warehouse Supervisor / Storeperson | 741111 |
| 79 | 快递/同城配送司机 | Delivery Driver / Courier | 732111 |
| 80 | 重型设备操作工（挖机/推土） | Earthmoving / Excavating Machine Operator | 721211 |
| 81 | 港口/码头操作员 | Stevedore / Port Operator | 741212 |

#### 商业 / 金融（延伸）

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 82 | 项目经理（通用） | Project Manager (General) | 511112 |
| 83 | 采购专员 | Purchasing / Procurement Officer | 591211 |
| 84 | 合规官员 | Compliance Officer | 221214 |
| 85 | 保险经纪人 | Insurance Broker | 611211 |
| 86 | 信贷分析师 | Credit Analyst | 222211 |
| 87 | 土地/房产估价师 | Property Valuer | 224511 |
| 88 | 劳资关系专员 | Employee / Industrial Relations Officer | 223213 |
| 89 | 城市/城镇规划师 | Urban and Regional Planner | 232212 |
| 90 | 统计学家 | Statistician | 224212 |

#### 专业服务 / 其他

| # | 职业（中文） | 职业（英文） | ANZSCO |
|---|---|---|---|
| 91 | 翻译/口译员 | Interpreter / Translator | 272413 |
| 92 | 按摩治疗师 | Massage Therapist | 411613 |
| 93 | 个人护理员 | Personal Care Worker | 423111 |
| 94 | 宠物美容师/宠物护理 | Pet Groomer / Animal Attendant | 361311 |
| 95 | 殡仪/葬礼主持 | Funeral Director | 451512 |
| 96 | 社区服务工作者 | Community Services Worker | 411215 |
| 97 | 职业健康与安全专员 | Work Health and Safety (WHS) Officer | 251311 |
| 98 | 图书馆员 | Librarian | 224611 |
| 99 | 档案管理员 | Records Manager / Archivist | 224212 |
| 100 | 法庭速记员/法律书记官 | Court Reporter / Registrar | 591113 |

---

## 未来扩展方向

### 新西兰（NZ）内容

- country_code = 'NZ'，occ_code_type = 'ANZSCO'（NZ 也用 ANZSCO），currency = 'NZD'
- 可复用 AU 的 seed 脚本结构，修改数据和 country_code 即可
- 状态：**未启动**，待 AU 内容完善后开展

### Score 精细化（方案B）

针对以下 3 个 dimension，通过 Web 检索填写真实小数评分（1.0~5.0），提升 Q6 查询准确度：
- `competition`（竞争激烈程度）
- `income_level`（收入水平）
- `job_demand`（岗位需求量）

涉及已入库的 92 个职业 × 3 个 dimension = 276 条记录。
- 状态：**待启动**，目前均为 `stars * 1.0` 占位值

### 查询功能验证

回填 salary_band 后，运行测试查询（见 `session-handoff-2026-06-09.md` 优先级2部分），验证 Q2 / Q6 可用性。
- 状态：**依赖 salary_band 回填完成**

---

Sources:
- [Jobs and Skills Australia – Occupation Shortage List](https://www.jobsandskills.gov.au/data/occupation-shortage/occupation-shortage-list)
- [Core Skills Occupation List – Opal Consulting](https://www.opalconsulting.com.au/blogs/core-skills-occupation-list-australia)
- [Skill Shortage List 2026 – PSS Removals](https://www.pssremovals.com/blog/most-in-demand-jobs-skilled-migration-australia)
- [5 Trades in Demand Australia 2026 – Major Training Group](https://major.edu.au/articles/trades-in-demand-australia-2026/)
- [Hays Jobs Report 2026](https://www.hays.com.au/industry-insights/jobs-report)
- [Scaffolder ANZSCO 821712 – Getting Down Under](https://gettingdownunder.com/scaffolder-anzsco-821712/)
- [Construction Rigger ANZSCO 821711 – ANZSCOsearch](https://www.anzscosearch.com/821711/)

---

## 待办（2026-06-18 新增）

- [ ] **189 获邀分采集**：189(独立技术移民)按职业公布每轮最低分(2025-11 技工65/专业80-90/IT90-110)，采集并写入 `occupation_invitation_scores`(visa_subclass='189')。后续与 190/491 一起由定时任务更新。
- [ ] 190/491 获邀分目前为「按大类竞争性参考值」，待定时任务接入各州/SkillSelect 精确数据覆盖。
- [ ] 多国扩展：已支持 country_code/currency/国家切换器；CA(NOC)/NZ(ANZSCO) 各 2 个样本已入库。后续批量采集 CA/NZ/US 职业。
