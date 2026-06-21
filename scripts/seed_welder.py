"""
直接将澳洲焊工（322313）真实数据写入 MySQL。
数据来源：Jobs and Skills Australia、Glassdoor、Indeed、ERI SalaryExpert、
         TAFE NSW/SA/WA/QLD、Trades Recognition Australia（TRA）、
         Department of Home Affairs（2025-2026）。
"""
import sys, os, json
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

TODAY = date.today()

# ─────────────────────────────────────────────────────────────
# 结构化数据
# ─────────────────────────────────────────────────────────────

OCCUPATION = {
    "anzsco_code":     "322313",
    "anzsco_title":    "Welder (First Class)",
    "category":        "技工",
    "workforce_size":  70000,   # ABS / JSA 估算（含 Boilermaker/Metal Fabricator），~2025
    "shortage_listed": 1,       # MLTSSL + CSOL 双榜在列
    "growth_areas":    json.dumps([
        "Mining & Resources Infrastructure",
        "Defence & Shipbuilding (BAE Systems, ASC)",
        "Renewable Energy Structures (Wind Towers, Solar Frames)",
        "Construction & Structural Steel",
        "Oil & Gas Pipelines",
    ], ensure_ascii=False),
}

I18N_ZH = {
    "locale":        "zh-CN",
    "name":          "焊工",
    "summary":       "焊工（Welder / Boilermaker）负责切割、成型、连接和修复金属构件，"
                     "广泛应用于建筑结构钢、矿业、船舶制造、国防工业和管道工程。"
                     "在澳大利亚，焊工同时列入 MLTSSL 和 CSOL，是技术移民的热门路径之一。",
    "forecast_note": "Jobs and Skills Australia 预测至2035年技工类新增就业约195,800人（+9.8%）。"
                     "国防造船计划（AUKUS潜艇、护卫舰）和可再生能源基础设施建设将持续拉动焊工需求。",
    "trend_summary":  "澳大利亚国防工业扩张（AUKUS协议）、矿业自动化改造和可再生能源结构件制造"
                      "是三大需求驱动力。高级焊工（特种焊接、压力容器）稀缺性持续上升。",
}

I18N_EN = {
    "locale":        "en",
    "name":          "Welder",
    "summary":       "Welders cut, shape, join and repair metal components for structural steel, "
                     "mining, shipbuilding, defence and pipeline industries. "
                     "In Australia, welders are listed on both MLTSSL and CSOL, "
                     "providing multiple skilled migration pathways.",
    "forecast_note": "JSA projects ~195,800 new Technicians & Trades Worker jobs by 2035 (+9.8%). "
                     "AUKUS defence shipbuilding and renewable energy infrastructure drive "
                     "sustained demand for qualified welders through 2030.",
    "trend_summary":  "Defence expansion (AUKUS submarines and frigates), mining infrastructure upgrades, "
                      "and renewable energy fabrication are the key demand drivers. "
                      "Specialist welders (pressure vessels, coded welding) command premium rates.",
}

# ── 教育路径 ───────────────────────────────────────────────────
EDUCATION = [
    {
        "stage":      "学徒制 Apprenticeship（含 MEM30319 TAFE 课程）",
        "duration":   "42~48个月（约3.5~4年）",
        "cost_min":   0,
        "cost_max":   1200,
        "cost_note":  "各州补贴差异：WA Lower Fees 计划上限 $1,200（25岁以下仅 $400）；"
                      "NSW Smart & Skilled 补贴大部分学费；QLD 约 $1.60/课时。另需工具费约 $500~$1,000",
        "sort_order": 0,
    },
    {
        "stage":      "海外资质互认（TRA Job Ready Program）",
        "duration":   "12~24个月",
        "cost_min":   2500,
        "cost_max":   6000,
        "cost_note":  "含 TRA 评估费、补考费、实习期行政费；焊接编码测试费另计（约 $500~$1,500）",
        "sort_order": 1,
    },
    {
        "stage":      "特种焊接认证（Coded Welding / AS2980）",
        "duration":   "1~3个月",
        "cost_min":   500,
        "cost_max":   2000,
        "cost_note":  "压力容器、管道等特种焊接须持有 AS2980/ASME 焊接编码证书，按焊接方法分类",
        "sort_order": 2,
    },
]

# ── 从业资质 ───────────────────────────────────────────────────
QUALIFICATIONS = [
    {
        "qual_name":    "Certificate III in Engineering – Fabrication Trade (MEM30319)",
        "issuer":       "TAFE / RTO",
        "note":         "全国统一课程，含焊接/钣金/锅炉/结构钢多个专攻方向，执业基础资质",
        "is_mandatory": 1,
        "sort_order":   0,
    },
    {
        "qual_name":    "Coded Welding Certificate (AS/NZS 2980 / ASME IX)",
        "issuer":       "认可第三方检测机构（如 NATA 实验室）",
        "note":         "压力容器、管道和船舶焊接的行业标准资质，大型项目通常强制要求",
        "is_mandatory": 0,
        "sort_order":   1,
    },
    {
        "qual_name":    "Working at Heights / Confined Space Certificates",
        "issuer":       "各州 SafeWork / WorkSafe 认可 RTO",
        "note":         "施工现场高空或密闭空间焊接作业的强制安全资质",
        "is_mandatory": 0,
        "sort_order":   2,
    },
    {
        "qual_name":    "Certificate IV in Engineering – Fabrication Trade（可选）",
        "issuer":       "TAFE / RTO",
        "note":         "晋升工程设计、质检或工地管理岗位的进阶资质",
        "is_mandatory": 0,
        "sort_order":   3,
    },
    {
        "qual_name":    "TRA Skills Assessment",
        "issuer":       "Trades Recognition Australia (TRA)",
        "note":         "海外学历移民必须，国内学历豁免",
        "is_mandatory": 0,
        "sort_order":   4,
    },
]

# ── 招聘平台挂牌量（2025~2026 区间估算）──────────────────────
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 2500,
     "note": "全国，含Boilermaker/Metal Fabricator/Welder，矿业和建筑需求为主"},
    {"platform": "Indeed",   "count_min": 900,  "count_max": 1600,
     "note": "含兼职、合同工，去重后略低"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 900,
     "note": "偏企业直招、国防/矿业工程类岗位"},
]

# ── 收入范围（来源：Indeed Apr 2026、Glassdoor 2026、ERI SalaryExpert 2026、
#             SEEK Apr 2026、Jobted AU 2026）──────────────────────────────────
SALARIES = [
    {
        "experience":  "学徒 1年级",
        "salary_min":  22000,
        "salary_max":  29000,
        "salary_note": "Fair Work Award 最低工资，按年级递增",
        "sort_order":  0,
    },
    {
        "experience":  "学徒 2~4年级",
        "salary_min":  29000,
        "salary_max":  46000,
        "salary_note": "约 $24~$30/hr（成人学徒），政府补贴另计",
        "sort_order":  1,
    },
    {
        "experience":  "初级焊工（持证后 1~3年）",
        "salary_min":  60000,
        "salary_max":  75000,
        "salary_note": "Glassdoor 25th percentile ~$57,817；ERI 初级 $62,552",
        "sort_order":  2,
    },
    {
        "experience":  "中级焊工（3~8年）",
        "salary_min":  75000,
        "salary_max":  95000,
        "salary_note": "Indeed 全国平均 $42.95/hr（约 $89k/yr）；ERI 平均 $84,556；Glassdoor 中位 ~$80,000",
        "sort_order":  3,
    },
    {
        "experience":  "资深焊工 / 编码焊工（8年+）",
        "salary_min":  95000,
        "salary_max":  120000,
        "salary_note": "ERI 资深 $94,716；Coded Welder（压力容器/管道）薪资显著高于通用焊工",
        "sort_order":  4,
    },
    {
        "experience":  "矿业 FIFO 焊工（WA/QLD）",
        "salary_min":  120000,
        "salary_max":  170000,
        "salary_note": "包含轮班津贴、FIFO 补贴，国防造船（BAE Systems等）薪资亦较高",
        "sort_order":  5,
    },
]

# ── 签证路径 ───────────────────────────────────────────────────
VISA_PATHWAYS = [
    {
        "visa_subclass": "482",
        "visa_name":     "TSS（Skills in Demand）",
        "description":   "雇主担保，中期技能流最长4年，2年后可转186",
        "sort_order":    0,
    },
    {
        "visa_subclass": "186",
        "visa_name":     "ENS",
        "description":   "雇主担保永久居留，TRT流需持482满2年，直接流需3年相关工作经验",
        "sort_order":    1,
    },
    {
        "visa_subclass": "189",
        "visa_name":     "SkillSelect Independent",
        "description":   "无需雇主，邀请制，MLTSSL和CSOL双榜在列，竞争激烈建议搭配190/491",
        "sort_order":    2,
    },
    {
        "visa_subclass": "190",
        "visa_name":     "Skilled Nominated",
        "description":   "州政府提名，加5分，永居，SA/WA/QLD对焊工需求旺盛，提名机会较多",
        "sort_order":    3,
    },
    {
        "visa_subclass": "491",
        "visa_name":     "Skilled Work Regional",
        "description":   "偏远地区提名加15分，临居5年转PR，矿业重点州（WA/QLD）机会较多",
        "sort_order":    4,
    },
]

# ── 评级 ───────────────────────────────────────────────────────
RATINGS = [
    {"dimension": "learning_difficulty",       "label_zh": "中等", "stars": 3,
     "note": "基础焊接技能上手较快；高端编码焊接（压力容器/管道）难度显著提升"},
    {"dimension": "learning_duration",         "label_zh": "较长", "stars": 4,
     "note": "学徒制约3.5~4年；TRA互认12~24个月（焊接编码测试为额外门槛）"},
    {"dimension": "certification_difficulty",  "label_zh": "中等", "stars": 3,
     "note": "基础 Certificate III 考核可备考通过；Coded Welding 技能测试有一定难度"},
    {"dimension": "job_demand",                "label_zh": "很高", "stars": 5,
     "note": "MLTSSL + CSOL 双榜在列；国防造船、矿业、可再生能源基建持续拉动"},
    {"dimension": "competition",               "label_zh": "较低", "stars": 2,
     "note": "供不应求，持证焊工尤其是编码焊工极度短缺，薪资溢价明显"},
    {"dimension": "work_intensity",            "label_zh": "较高", "stars": 4,
     "note": "体力劳动，涉及高温、烟尘、高空/密闭空间；FIFO轮班强度大"},
    {"dimension": "income_level",              "label_zh": "中高", "stars": 4,
     "note": "中位数约 $80,000~$89,000；矿业FIFO和编码焊工可达 $120,000~$170,000"},
    {"dimension": "future_prospect",           "label_zh": "极佳", "stars": 5,
     "note": "AUKUS国防扩张、可再生能源基建、矿业改造三重驱动，2030前缺口持续扩大"},
    {"dimension": "ai_risk",                   "label_zh": "低",   "stars": 2,
     "note": "自动焊接机器人已在部分重复性工序中应用，但复杂结构焊接和现场修复仍依赖人工"},
    {"dimension": "pr_friendliness",           "label_zh": "极高", "stars": 5,
     "note": "MLTSSL + CSOL 双榜，189/190/491/482/186 全路径可申请"},
    {"dimension": "pr_difficulty",             "label_zh": "中等", "stars": 3,
     "note": "TRA评估周期较长（12~24个月）；编码焊接测试为额外门槛"},
]

# ── 适合人群 ───────────────────────────────────────────────────
SUITABILITY_FIT = [
    "有焊接/钣金/机械加工背景（国内职校或相关工作经验），希望通过技能移民来澳",
    "接受体力劳动、高温和烟尘工作环境，不抵触户外或工业场所",
    "目标是矿业高薪（FIFO）或国防造船（BAE Systems、ASC等大型项目）",
    "希望走职业技能移民路线，SA/WA/QLD 州提名机会较多",
    "愿意持续考取编码焊接证书（Coded Welder），以获取更高薪资溢价",
]

SUITABILITY_UNFIT = [
    "对高温、烟尘、高噪音工作环境有明显生理抵触",
    "期望1~2年内快速取得资质（学徒至少4年，TRA互认约12~24个月）",
    "完全无金属加工或机械基础，且不愿投入时间学习实操技能",
    "担忧自动化替代（自动焊接机器人在部分场景已有渗透，需关注行业动向）",
]

# ── 数据来源 ───────────────────────────────────────────────────
SOURCES = [
    {"source_name": "Jobs and Skills Australia",
     "content":     "ANZSCO 322313 职业档案、MLTSSL+CSOL短缺状态、2025~2035就业预测",
     "url":         "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/322313-welders-first-class"},
    {"source_name": "training.gov.au",
     "content":     "MEM30319 Certificate III in Engineering – Fabrication Trade 课程标准",
     "url":         "https://training.gov.au/training/details/MEM30319"},
    {"source_name": "Department of Home Affairs",
     "content":     "MLTSSL / CSOL / 签证子类 482、186、189、190、491 条件",
     "url":         "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA (Trades Recognition Australia)",
     "content":     "海外焊工技能评估流程、Job Ready Program、2025 Assessment Standards Policy",
     "url":         "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Indeed AU",
     "content":     "焊工平均时薪 $42.95（Apr 2026）",
     "url":         "https://au.indeed.com/career/welder/salaries"},
    {"source_name": "ERI SalaryExpert",
     "content":     "焊工平均年薪 $84,556；资深 $94,716（2026）",
     "url":         "https://www.salaryexpert.com/salary/job/welder/australia"},
    {"source_name": "Glassdoor AU",
     "content":     "焊工薪资区间 $57,817~$87,379（2026）",
     "url":         "https://www.glassdoor.com/Salaries/australia-welder-salary-SRCH_IL.0,9_IN16_KO10,16.htm"},
    {"source_name": "SEEK AU",
     "content":     "焊工薪资及职位需求数据（Apr 2026）",
     "url":         "https://www.seek.com.au/career-advice/role/welder/salary"},
]

# ── FAQ ────────────────────────────────────────────────────────
FAQS = [
    {
        "faq_type":   "salary",
        "sort_order": 0,
        "question":   "澳洲焊工工资多少？",
        "answer":     "中级持证焊工年薪（AUD）约 $75,000~$95,000，Indeed 全国平均 $42.95/hr（约 $89k）。"
                      "矿业FIFO焊工和编码焊工可达 $120,000~$170,000。学徒期间约 $22,000~$46,000（按年级递增）。",
    },
    {
        "faq_type":   "demand",
        "sort_order": 1,
        "question":   "澳洲焊工容易找工作吗？",
        "answer":     "容易。焊工同时列入 MLTSSL 和 CSOL，Seek 常年挂牌 1,500~2,500 个职位。"
                      "国防造船（AUKUS）和矿业项目创造大量持续需求，编码焊工尤其稀缺。",
    },
    {
        "faq_type":   "recognition",
        "sort_order": 2,
        "question":   "中国焊工证澳洲认可吗？",
        "answer":     "不直接认可，需通过 TRA Job Ready Program 进行技能评估，周期约12~24个月。"
                      "有国内焊工经验者可适当缩短评估周期，同时建议备考澳洲 Coded Welding 认证以提升竞争力。",
    },
    {
        "faq_type":   "ai_risk",
        "sort_order": 3,
        "question":   "焊工会被AI和机器人替代吗？",
        "answer":     "部分替代，但整体风险偏低。自动焊接机器人已在重复性生产线上广泛应用，"
                      "但复杂结构焊接、现场修复、压力容器编码焊接仍高度依赖熟练工人，"
                      "有特种资质的焊工薪资不降反升。",
    },
    {
        "faq_type":   "age_limit",
        "sort_order": 4,
        "question":   "澳洲焊工有年龄限制吗？",
        "answer":     "法律上无明确年龄上限。学徒招募偏好35岁以下，但35~45岁可走TRA互认路径，"
                      "跳过学徒期。技术移民打分中年龄45岁以上无加分，建议尽早启动。",
    },
    {
        "faq_type":   "education_limit",
        "sort_order": 5,
        "question":   "澳洲焊工需要大学学历吗？",
        "answer":     "不需要。完成 Certificate III（MEM30319）即可执业，"
                      "高中毕业即可直接申请学徒。国内技校/职校焊接专业学历可通过TRA评估路径直接互认。",
    },
    {
        "faq_type":   "difficulty",
        "sort_order": 6,
        "question":   "澳洲焊工难学吗？",
        "answer":     "基础焊接（MIG/TIG/弧焊）难度中等，有国内基础者3~6个月可进入生产状态。"
                      "高端编码焊接（压力容器/管道 AS2980/ASME IX）则需专项培训和技能测试，难度较高但薪资溢价丰厚。",
    },
    {
        "faq_type":   "comparison",
        "sort_order": 7,
        "question":   "焊工和电工哪个更适合移民澳洲？",
        "answer":     "两者均在 MLTSSL，PR路径相近。电工薪资略高（中位 ~$94k vs 焊工 ~$85k），"
                      "但持牌考试和跨州认证更复杂；焊工竞争更低、国防/矿业需求旺盛，"
                      "有编码焊接资质者薪资可超越普通电工。有金属加工背景者首选焊工路径。",
    },
]


# ─────────────────────────────────────────────────────────────
# 写库逻辑
# ─────────────────────────────────────────────────────────────

def run():
    with get_cursor() as cur:

        # 1. occupations 主表
        cur.execute("""
            INSERT INTO occupations
              (anzsco_code, anzsco_title, category, workforce_size, shortage_listed, growth_areas)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              anzsco_title    = VALUES(anzsco_title),
              category        = VALUES(category),
              workforce_size  = VALUES(workforce_size),
              shortage_listed = VALUES(shortage_listed),
              growth_areas    = VALUES(growth_areas)
        """, (
            OCCUPATION["anzsco_code"],
            OCCUPATION["anzsco_title"],
            OCCUPATION["category"],
            OCCUPATION["workforce_size"],
            OCCUPATION["shortage_listed"],
            OCCUPATION["growth_areas"],
        ))
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s", (OCCUPATION["anzsco_code"],))
        occ_id = cur.fetchone()["id"]
        print(f"[occupations]       id={occ_id}  {OCCUPATION['anzsco_code']} {OCCUPATION['anzsco_title']}")

        # 2. i18n（zh-CN + en）
        for i18n in [I18N_ZH, I18N_EN]:
            cur.execute("""
                INSERT INTO occupations_i18n
                  (occupation_id, locale, name, summary, forecast_note, trend_summary)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                  name=VALUES(name), summary=VALUES(summary),
                  forecast_note=VALUES(forecast_note), trend_summary=VALUES(trend_summary)
            """, (occ_id, i18n["locale"], i18n["name"],
                  i18n["summary"], i18n["forecast_note"], i18n["trend_summary"]))
        print(f"[occupations_i18n]  2 locales (zh-CN, en)")

        # 3. 评级
        cur.execute("DELETE FROM occupation_ratings WHERE occupation_id=%s", (occ_id,))
        for r in RATINGS:
            cur.execute("""
                INSERT INTO occupation_ratings
                  (occupation_id, dimension, label_zh, stars, note)
                VALUES (%s,%s,%s,%s,%s)
            """, (occ_id, r["dimension"], r["label_zh"], r["stars"], r.get("note")))
        print(f"[occupation_ratings] {len(RATINGS)} dimensions")

        # 4. 教育路径
        cur.execute("DELETE FROM occupation_education WHERE occupation_id=%s", (occ_id,))
        for e in EDUCATION:
            cur.execute("""
                INSERT INTO occupation_education
                  (occupation_id, stage, duration, cost_min, cost_max, cost_note, sort_order)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (occ_id, e["stage"], e["duration"],
                  e["cost_min"], e["cost_max"], e["cost_note"], e["sort_order"]))
        print(f"[occupation_education] {len(EDUCATION)} rows")

        # 5. 从业资质
        cur.execute("DELETE FROM occupation_qualifications WHERE occupation_id=%s", (occ_id,))
        for q in QUALIFICATIONS:
            cur.execute("""
                INSERT INTO occupation_qualifications
                  (occupation_id, qual_name, issuer, note, is_mandatory, sort_order)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (occ_id, q["qual_name"], q.get("issuer"),
                  q.get("note"), q["is_mandatory"], q["sort_order"]))
        print(f"[occupation_qualifications] {len(QUALIFICATIONS)} rows")

        # 6. 平台挂牌量
        cur.execute("DELETE FROM occupation_job_listings WHERE occupation_id=%s", (occ_id,))
        for jl in JOB_LISTINGS:
            cur.execute("""
                INSERT INTO occupation_job_listings
                  (occupation_id, platform, count_min, count_max, note, snapshot_date)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (occ_id, jl["platform"], jl["count_min"], jl["count_max"], jl["note"], TODAY))
        print(f"[occupation_job_listings] {len(JOB_LISTINGS)} platforms  snapshot={TODAY}")

        # 7. 收入范围
        cur.execute("DELETE FROM occupation_salaries WHERE occupation_id=%s", (occ_id,))
        for s in SALARIES:
            cur.execute("""
                INSERT INTO occupation_salaries
                  (occupation_id, experience, salary_min, salary_max, salary_note, sort_order)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (occ_id, s["experience"], s["salary_min"],
                  s["salary_max"], s["salary_note"], s["sort_order"]))
        print(f"[occupation_salaries] {len(SALARIES)} rows")

        # 8. 签证路径
        cur.execute("DELETE FROM occupation_visa_pathways WHERE occupation_id=%s", (occ_id,))
        for v in VISA_PATHWAYS:
            cur.execute("""
                INSERT INTO occupation_visa_pathways
                  (occupation_id, visa_subclass, visa_name, description, sort_order)
                VALUES (%s,%s,%s,%s,%s)
            """, (occ_id, v["visa_subclass"], v["visa_name"], v["description"], v["sort_order"]))
        print(f"[occupation_visa_pathways] {len(VISA_PATHWAYS)} rows")

        # 9. 适合/不适合人群
        cur.execute("DELETE FROM occupation_suitability WHERE occupation_id=%s", (occ_id,))
        for i, item in enumerate(SUITABILITY_FIT):
            cur.execute(
                "INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'fit',%s,%s)",
                (occ_id, item, i))
        for i, item in enumerate(SUITABILITY_UNFIT):
            cur.execute(
                "INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'unfit',%s,%s)",
                (occ_id, item, i))
        print(f"[occupation_suitability] {len(SUITABILITY_FIT)} fit, {len(SUITABILITY_UNFIT)} unfit")

        # 10. 数据来源
        cur.execute("DELETE FROM occupation_sources WHERE occupation_id=%s", (occ_id,))
        for s in SOURCES:
            cur.execute("""
                INSERT INTO occupation_sources (occupation_id, source_name, content, url)
                VALUES (%s,%s,%s,%s)
            """, (occ_id, s["source_name"], s.get("content"), s.get("url")))
        print(f"[occupation_sources] {len(SOURCES)} rows")

        # 11. FAQ
        cur.execute("DELETE FROM occupation_faqs WHERE occupation_id=%s", (occ_id,))
        for faq in FAQS:
            cur.execute(
                "INSERT INTO occupation_faqs (occupation_id, faq_type, sort_order) VALUES(%s,%s,%s)",
                (occ_id, faq["faq_type"], faq["sort_order"]))
            faq_id = cur.lastrowid
            cur.execute("""
                INSERT INTO occupation_faqs_i18n (faq_id, locale, question, answer)
                VALUES (%s,'zh-CN',%s,%s)
                ON DUPLICATE KEY UPDATE question=VALUES(question), answer=VALUES(answer)
            """, (faq_id, faq["question"], faq["answer"]))
        print(f"[occupation_faqs]    {len(FAQS)} items (zh-CN)")

    print("\n[OK] 焊工数据入库完成")


if __name__ == "__main__":
    run()
