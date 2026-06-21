"""
直接将澳洲空调技术员（342111）真实数据写入 MySQL。
数据来源：Jobs and Skills Australia、Glassdoor、Indeed、PayScale、ERI SalaryExpert、
         TAFE QLD/NSW/SA/WA、ARC（Australian Refrigeration Council）、
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
    "anzsco_code":     "342111",
    "anzsco_title":    "Airconditioning and Refrigeration Mechanic",
    "category":        "技工",
    "workforce_size":  55000,   # Jobs and Skills Australia ANZSCO 3421 估算，~2025
    "shortage_listed": 1,       # MLTSSL 确认在列
    "growth_areas":    json.dumps([
        "Commercial & Industrial Refrigeration",
        "Data Centre Cooling Systems",
        "Heat Pump & Green Refrigerants Transition",
        "Mining & Resources HVAC",
        "Residential & Commercial Construction Boom",
    ], ensure_ascii=False),
}

I18N_ZH = {
    "locale":        "zh-CN",
    "name":          "空调技术员",
    "summary":       "空调技术员（HVAC/制冷技术员）负责安装、调试、维护和维修工业、商业及住宅空调和制冷系统。"
                     "在澳大利亚，该职业需持有 ARCtick 制冷剂处理许可证，长期位居技术短缺清单，"
                     "是气候变暖背景下需求持续增长的热门技工职业之一。",
    "forecast_note": "Jobs and Skills Australia 预测技工类（含HVAC）至2035年新增就业约195,800人（+9.8%）。"
                     "气候变化导致夏季高温天数增加，澳洲HVAC技术员长期供不应求，各州均有短缺。",
    "trend_summary":  "绿色制冷剂转型（HFO替代HFC）、数据中心冷却爆发、新建住宅和商业项目持续推高需求。"
                      "AI与自动化对现场施工和制冷剂处理替代率极低，职业稳定性强。",
}

I18N_EN = {
    "locale":        "en",
    "name":          "HVAC Technician",
    "summary":       "HVAC/Refrigeration Mechanics install, commission, maintain and repair air conditioning "
                     "and refrigeration systems across residential, commercial and industrial sectors. "
                     "In Australia, practitioners must hold an ARCtick Refrigerant Handling Licence and "
                     "are listed on the national skills shortage list.",
    "forecast_note": "JSA projects ~195,800 new Technicians & Trades Worker jobs by 2035 (+9.8%). "
                     "Rising temperatures and data centre expansion are key demand drivers, "
                     "with HVAC vacancies remaining consistently unfilled across all states.",
    "trend_summary":  "Green refrigerant transition (HFOs replacing HFCs), data centre cooling boom, "
                      "and residential construction drive sustained demand through 2030. "
                      "AI replacement risk is very low for on-site installation and maintenance work.",
}

# ── 教育路径（来源：TAFE QLD/NSW/SA/WA, CDU, 2025）────────────
EDUCATION = [
    {
        "stage":      "学徒制 Apprenticeship（含 UEE32220 TAFE 课程）",
        "duration":   "42~48个月（约3.5~4年）",
        "cost_min":   0,
        "cost_max":   1200,
        "cost_note":  "各州补贴差异：NSW Smart & Skilled 补贴学费；WA 上限约 $1,200；QLD 约 $1.60/课时。另需书本/资源费约 $300~$600",
        "sort_order": 0,
    },
    {
        "stage":      "海外资质互认（TRA Job Ready Program / VETASSESS）",
        "duration":   "12~18个月",
        "cost_min":   2000,
        "cost_max":   5000,
        "cost_note":  "含 TRA/VETASSESS 评估费、技能补考费、实习期行政费",
        "sort_order": 1,
    },
    {
        "stage":      "ARCtick 制冷剂处理许可证（Refrigerant Handling Licence）",
        "duration":   "1~3个月（含培训和考试）",
        "cost_min":   400,
        "cost_max":   900,
        "cost_note":  "全国统一颁发，持牌后方可合法操作制冷剂，每3年更新一次",
        "sort_order": 2,
    },
]

# ── 从业资质 ───────────────────────────────────────────────────
QUALIFICATIONS = [
    {
        "qual_name":    "Certificate III in Air Conditioning and Refrigeration (UEE32220)",
        "issuer":       "TAFE / RTO",
        "note":         "全国统一课程，执业基础资质，学徒期间完成",
        "is_mandatory": 1,
        "sort_order":   0,
    },
    {
        "qual_name":    "ARCtick Refrigerant Handling Licence（RHL）",
        "issuer":       "Australian Refrigeration Council (ARC)",
        "note":         "法定强制持牌，无证操作制冷剂违法，适用所有 RAC 工作",
        "is_mandatory": 1,
        "sort_order":   1,
    },
    {
        "qual_name":    "各州电气许可证（部分州要求）",
        "issuer":       "各州 Fair Trading / Energy Safety 部门",
        "note":         "从事电气接线（含 HVAC 电气部分）须持有州级 Electrical Licence",
        "is_mandatory": 0,
        "sort_order":   2,
    },
    {
        "qual_name":    "Certificate IV in Air Conditioning and Refrigeration（可选）",
        "issuer":       "TAFE / RTO",
        "note":         "晋升工程设计或管理岗位的进阶资质",
        "is_mandatory": 0,
        "sort_order":   3,
    },
    {
        "qual_name":    "TRA / VETASSESS Skills Assessment",
        "issuer":       "Trades Recognition Australia / VETASSESS",
        "note":         "海外学历移民必须，国内学历豁免",
        "is_mandatory": 0,
        "sort_order":   4,
    },
]

# ── 招聘平台挂牌量（2025~2026 区间估算）──────────────────────
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1200, "count_max": 2000,
     "note": "全国，含学徒岗、商业及工业冷冻岗"},
    {"platform": "Indeed",   "count_min": 800,  "count_max": 1400,
     "note": "含兼职、合同工，去重后略低"},
    {"platform": "LinkedIn", "count_min": 300,  "count_max": 700,
     "note": "偏企业直招、工程设计及管理类岗位"},
]

# ── 收入范围（来源：Glassdoor May 2026、Indeed May 2026、ERI SalaryExpert 2026、
#             SEEK Career Insights 2026、PayScale 2026）──────────────────────────
SALARIES = [
    {
        "experience":  "学徒 1年级",
        "salary_min":  22000,
        "salary_max":  30000,
        "salary_note": "Fair Work Award 最低工资，按年级递增",
        "sort_order":  0,
    },
    {
        "experience":  "学徒 2~4年级",
        "salary_min":  30000,
        "salary_max":  48000,
        "salary_note": "约 $25~$31/hr（成人学徒），政府补贴另计",
        "sort_order":  1,
    },
    {
        "experience":  "初级技术员（持牌后 1~3年）",
        "salary_min":  65000,
        "salary_max":  82000,
        "salary_note": "Indeed/Glassdoor 25th percentile，住宅及小型商业项目为主",
        "sort_order":  2,
    },
    {
        "experience":  "中级技术员（3~8年）",
        "salary_min":  82000,
        "salary_max":  105000,
        "salary_note": "ERI SalaryExpert 平均 $96,426；Indeed 全国平均 $88,107；SEEK 区间 $95,000~$115,000",
        "sort_order":  3,
    },
    {
        "experience":  "资深技术员 / 承包商（8年+）",
        "salary_min":  105000,
        "salary_max":  130000,
        "salary_note": "ERI 高端 $116,483+，含大型商业/工业项目承包利润",
        "sort_order":  4,
    },
    {
        "experience":  "矿业 FIFO 技术员（WA/QLD）",
        "salary_min":  130000,
        "salary_max":  180000,
        "salary_note": "包含轮班津贴、FIFO 补贴，矿业制冷维护岗薪资显著高于城市",
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
        "description":   "无需雇主，邀请制，MLTSSL在列，当前竞争激烈建议搭配190/491",
        "sort_order":    2,
    },
    {
        "visa_subclass": "190",
        "visa_name":     "Skilled Nominated",
        "description":   "州政府提名，加5分，永居，建议首选路线",
        "sort_order":    3,
    },
    {
        "visa_subclass": "491",
        "visa_name":     "Skilled Work Regional",
        "description":   "偏远地区提名加15分，临居5年转PR，适合189分数不够者",
        "sort_order":    4,
    },
]

# ── 评级 ───────────────────────────────────────────────────────
RATINGS = [
    {"dimension": "learning_difficulty",       "label_zh": "中等", "stars": 3,
     "note": "理论涉及制冷循环和制冷剂法规；实操为主，有电气背景上手更快"},
    {"dimension": "learning_duration",         "label_zh": "较长", "stars": 4,
     "note": "学徒制约3.5~4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty",  "label_zh": "中等", "stars": 3,
     "note": "ARCtick考试可备考通过；跨州电气持牌要求增加一定难度"},
    {"dimension": "job_demand",                "label_zh": "很高", "stars": 5,
     "note": "MLTSSL在列，气候变化驱动需求持续上升，各州均有缺口"},
    {"dimension": "competition",               "label_zh": "较低", "stars": 2,
     "note": "供不应求，持牌技术员通常数周内可找到工作"},
    {"dimension": "work_intensity",            "label_zh": "中等", "stars": 3,
     "note": "体力劳动，但以室内/设备间工作为主，强度低于室外施工类工种"},
    {"dimension": "income_level",              "label_zh": "较高", "stars": 4,
     "note": "中位数约 $88,000~$96,000；矿业FIFO可达 $130,000~$180,000"},
    {"dimension": "future_prospect",           "label_zh": "极佳", "stars": 5,
     "note": "气候变暖、数据中心爆发、绿色制冷转型三重驱动，2030前需求持续增长"},
    {"dimension": "ai_risk",                   "label_zh": "极低", "stars": 1,
     "note": "现场安装、制冷剂操作和故障排查无法自动化替代"},
    {"dimension": "pr_friendliness",           "label_zh": "极高", "stars": 5,
     "note": "MLTSSL在列，189/190/491/482/186 多路径均可申请"},
    {"dimension": "pr_difficulty",             "label_zh": "中等", "stars": 3,
     "note": "TRA评估周期长、ARCtick培训为额外门槛，跨州电气持牌不统一"},
]

# ── 适合人群 ───────────────────────────────────────────────────
SUITABILITY_FIT = [
    "有制冷/空调/电气背景（国内职校或相关工作经验），希望通过技能移民来澳",
    "不排斥体力劳动，能接受商业厨房、机房、屋顶等工作环境",
    "目标是矿业高薪（FIFO）或自建空调承包公司",
    "希望走职业技能移民路线，年龄30~40岁，有足够时间完成TRA评估",
    "对绿色能源和环保技术感兴趣（新型制冷剂、热泵、节能系统是增长方向）",
]

SUITABILITY_UNFIT = [
    "完全无制冷、电气或机械背景，且不愿意从学徒期重新开始（至少4年）",
    "对密闭空间（机房）或高温/严寒工作环境有明显生理或心理抵触",
    "期望1~2年内快速取得执业资质",
    "英语能力极弱且无改善计划（ARCtick考试、工地沟通和法规均需英语）",
]

# ── 数据来源 ───────────────────────────────────────────────────
SOURCES = [
    {"source_name": "Jobs and Skills Australia",
     "content":     "ANZSCO 342111 职业档案、短缺清单、2025~2035就业预测",
     "url":         "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/3421-airconditioning-and-refrigeration-mechanics"},
    {"source_name": "training.gov.au",
     "content":     "UEE32220 Certificate III in Air Conditioning and Refrigeration 课程标准",
     "url":         "https://training.gov.au/Training/Details/UEE32220"},
    {"source_name": "ARC（Australian Refrigeration Council）",
     "content":     "ARCtick 制冷剂处理许可证强制要求、2025 Code of Practice",
     "url":         "https://www.arctick.org/refrigerant-handling-licence/"},
    {"source_name": "Department of Home Affairs",
     "content":     "MLTSSL / 签证子类 482、186、189、190、491 条件",
     "url":         "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA / VETASSESS",
     "content":     "海外技能评估流程、Job Ready Program",
     "url":         "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "ERI SalaryExpert",
     "content":     "HVAC技术员平均年薪 $96,426；区间 $68,752~$116,483（2026）",
     "url":         "https://www.salaryexpert.com/salary/job/heating-and-air-conditioning-technician-hvac/australia"},
    {"source_name": "Indeed AU",
     "content":     "空调技术员平均年薪 $88,107（May 2026）",
     "url":         "https://au.indeed.com/career/air-conditioning-technician/salaries"},
    {"source_name": "Glassdoor AU",
     "content":     "制冷空调技术员平均年薪 $79,000（May 2026）",
     "url":         "https://www.glassdoor.com.au/Salaries/refrigeration-and-air-conditioning-mechanic-salary-SRCH_KO0,43.htm"},
    {"source_name": "SEEK Career Insights",
     "content":     "空调制冷技术员薪资区间 $95,000~$115,000（2026）",
     "url":         "https://www.seek.com.au/career-advice/role/air-conditioning-and-refrigeration-technician/salary"},
]

# ── FAQ ────────────────────────────────────────────────────────
FAQS = [
    {
        "faq_type":   "salary",
        "sort_order": 0,
        "question":   "澳洲空调技术员工资多少？",
        "answer":     "中级持牌技术员年薪（AUD）约 $82,000~$105,000，ERI SalaryExpert 平均 $96,426（2026）。"
                      "矿业FIFO岗可达 $130,000~$180,000。学徒期间约 $22,000~$48,000（按年级递增）。",
    },
    {
        "faq_type":   "demand",
        "sort_order": 1,
        "question":   "澳洲空调技术员容易找工作吗？",
        "answer":     "容易。HVAC技术员长期供不应求，MLTSSL长期在列。"
                      "Seek 常年挂牌 1,200~2,000 个职位，持牌后通常数周内可入职。",
    },
    {
        "faq_type":   "recognition",
        "sort_order": 2,
        "question":   "中国制冷/空调证书澳洲认可吗？",
        "answer":     "不直接认可，需通过 TRA Job Ready Program 或 VETASSESS 进行技能评估，周期约12~18个月。"
                      "完成评估后还需考取 ARCtick 制冷剂处理许可证方可合法执业。",
    },
    {
        "faq_type":   "ai_risk",
        "sort_order": 3,
        "question":   "空调技术员会被AI替代吗？",
        "answer":     "替代风险极低。HVAC工作高度依赖现场判断、制冷剂操作和复杂故障排查，"
                      "目前无成熟自动化方案可替代，且制冷剂操作受法规强制要求持牌人工操作。",
    },
    {
        "faq_type":   "age_limit",
        "sort_order": 4,
        "question":   "澳洲空调技术员有年龄限制吗？",
        "answer":     "法律上无明确年龄上限。学徒招募偏好35岁以下，但35~45岁可走TRA互认路径，"
                      "跳过4年学徒期。技术移民打分中年龄45岁以上无加分。",
    },
    {
        "faq_type":   "education_limit",
        "sort_order": 5,
        "question":   "澳洲空调技术员需要大学学历吗？",
        "answer":     "不需要。完成 Certificate III（UEE32220）+ ARCtick 即可执业，"
                      "相当于国内技校水平，高中毕业即可直接申请学徒。",
    },
    {
        "faq_type":   "difficulty",
        "sort_order": 6,
        "question":   "澳洲空调技术员难学吗？",
        "answer":     "难度中等。理论涉及制冷循环、热力学原理和制冷剂法规；"
                      "实操比电工更侧重设备安装和维护，有制冷或机电背景者6~12个月可入门。",
    },
    {
        "faq_type":   "comparison",
        "sort_order": 7,
        "question":   "空调技术员和电工哪个更适合移民澳洲？",
        "answer":     "两者均在 MLTSSL，PR路径相近。电工整体薪资略高（中位 ~$94k vs HVAC ~$88k），"
                      "学习和考证难度更高；HVAC 竞争更低、工作环境相对舒适，更易从制冷背景转换。"
                      "有电气背景者可同时考取两项资质，拓宽就业面。",
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

    print("\n[OK] 空调技术员数据入库完成")


if __name__ == "__main__":
    run()
