"""
直接将澳洲电工（341111）真实数据写入 MySQL。
数据来源：Jobs and Skills Australia、Glassdoor、Indeed、PayScale、
         TAFE NSW/SA/WA、Department of Home Affairs（2025-2026）。
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
    "anzsco_code":     "341111",
    "anzsco_title":    "Electrician (General)",
    "category":        "技工",
    "workforce_size":  128000,   # ABS Labour Force Survey, ~2025
    "shortage_listed": 1,        # MLTSSL 确认在列
    "growth_areas":    json.dumps([
        "Solar Installation & Battery Storage",
        "EV Charger Infrastructure",
        "Industrial Automation & Data Centres",
        "Renewable Energy Grid Upgrades",
        "Residential & Commercial Construction",
    ], ensure_ascii=False),
}

I18N_ZH = {
    "locale":       "zh-CN",
    "name":         "电工",
    "summary":      "电工负责安装、维护和修缮电气系统，广泛服务于住宅、商业、工业和矿业领域。"
                    "在澳大利亚，电工属于持牌强制行业，长期位居技术短缺清单，是技术移民的热门路径之一。",
    "forecast_note": "Jobs and Skills Australia 预计2025~2035年技工类（含电工）新增就业约195,800人（+9.8%）。"
                     "技工类（Skill Level 3）岗位填补率仅54.3%，是全澳最难招聘的工种之一。",
    "trend_summary": "可再生能源转型（Solar、Battery Storage、EV Chargers）持续拉动需求，"
                     "预计2030年前供需缺口进一步扩大。AI与自动化替代率极低，现场操作无法远程化。",
}

I18N_EN = {
    "locale":        "en",
    "name":          "Electrician",
    "summary":       "Electricians install, maintain and repair electrical systems across residential, "
                     "commercial, industrial and mining sectors. In Australia, electricians must hold a "
                     "state-issued licence and are listed on the national skills shortage list.",
    "forecast_note": "JSA projects ~195,800 new Technicians & Trades Worker jobs by 2035 (+9.8%). "
                     "Skill Level 3 (Trades) vacancy fill rate has dropped to 54.3%, "
                     "making electricians among the hardest roles to recruit nationally.",
    "trend_summary": "Driven by renewable energy transition (Solar, Battery Storage, EV Chargers), "
                     "the demand outlook remains strong through 2030. AI replacement risk is very low.",
}

# ── 教育路径（来源：TAFE NSW/SA/WA, CDU, 2025）────────────────
EDUCATION = [
    {
        "stage":      "学徒制 Apprenticeship（含 TAFE 课程）",
        "duration":   "48个月（约3.5~4年）",
        "cost_min":   0,
        "cost_max":   1200,
        "cost_note":  "各州差异大：NSW 免费；WA 上限 $1,200；QLD 约 $1.60/课时。另需书本/资源费约 $300~$600",
        "sort_order": 0,
    },
    {
        "stage":      "海外资质互认（TRA Job Ready Program）",
        "duration":   "12~18个月",
        "cost_min":   2000,
        "cost_max":   5000,
        "cost_note":  "含 TRA 评估费、补考费、实习期行政费",
        "sort_order": 1,
    },
    {
        "stage":      "各州持牌考试（Electrical Licence）",
        "duration":   "1~3个月",
        "cost_min":   300,
        "cost_max":   800,
        "cost_note":  "各州独立考试，跨州执业需重新申请",
        "sort_order": 2,
    },
]

# ── 从业资质 ───────────────────────────────────────────────────
QUALIFICATIONS = [
    {
        "qual_name":    "Certificate III in Electrotechnology Electrician (UEE30820)",
        "issuer":       "TAFE / RTO",
        "note":         "全国统一课程，3826学时，执业基础资质",
        "is_mandatory": 1,
        "sort_order":   0,
    },
    {
        "qual_name":    "Electrical Worker Licence（A级）",
        "issuer":       "各州 Fair Trading / Energy Safety 部门",
        "note":         "合法施工的强制持牌要求，无证操作违法",
        "is_mandatory": 1,
        "sort_order":   1,
    },
    {
        "qual_name":    "Electrical Contractor Licence",
        "issuer":       "各州独立颁发",
        "note":         "独立承接合同必须，雇主电工可豁免",
        "is_mandatory": 0,
        "sort_order":   2,
    },
    {
        "qual_name":    "Restricted Licence（如 Solar Grid Connect）",
        "issuer":       "Clean Energy Council / 各州",
        "note":         "太阳能安装、EV充电桩等专项工种额外资质",
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

# ── 招聘平台挂牌量（来源：Seek/Indeed/LinkedIn 2025~2026 区间估算）
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2500, "count_max": 4000,
     "note": "全国，含学徒岗及承包商招聘"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 2500,
     "note": "含兼职、合同工，实际去重后略低"},
    {"platform": "LinkedIn", "count_min": 600,  "count_max": 1200,
     "note": "偏企业直招、工程管理类电工岗"},
]

# ── 收入范围（来源：Glassdoor May 2026、Indeed May 2026、PayScale 2026、
#             Jobs & Skills Australia、ERI SalaryExpert 2026）──────────────
SALARIES = [
    {
        "experience":  "学徒 1年级",
        "salary_min":  24000,
        "salary_max":  32000,
        "salary_note": "Fair Work Award 最低工资，按年级递增",
        "sort_order":  0,
    },
    {
        "experience":  "学徒 2~4年级",
        "salary_min":  32000,
        "salary_max":  50000,
        "salary_note": "约 $27.32/hr（成人学徒），政府补贴另计",
        "sort_order":  1,
    },
    {
        "experience":  "初级电工（持牌后 1~3年）",
        "salary_min":  73000,
        "salary_max":  88000,
        "salary_note": "Glassdoor/Indeed 25th percentile，住宅施工为主",
        "sort_order":  2,
    },
    {
        "experience":  "中级电工（3~8年）",
        "salary_min":  88000,
        "salary_max":  115000,
        "salary_note": "Indeed 全国中位数 $53.11/hr；Glassdoor 平均 $94,000",
        "sort_order":  3,
    },
    {
        "experience":  "资深电工 / 承包商（8年+）",
        "salary_min":  115000,
        "salary_max":  140000,
        "salary_note": "ERI SalaryExpert 高端 $114,126~$125,000+，含加班及承包利润",
        "sort_order":  4,
    },
    {
        "experience":  "矿业 FIFO 电工（WA/QLD）",
        "salary_min":  140000,
        "salary_max":  220000,
        "salary_note": "包含轮班津贴、FIFO 补贴，部分岗位超 $200,000",
        "sort_order":  5,
    },
]

# ── 签证路径（来源：Department of Home Affairs、AVIE 2026）──────
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
        "description":   "无需雇主，邀请制，当前EOI分数线约65~75分（竞争激烈）",
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

# ── 评级（来源：综合以上各数据源判断）────────────────────────────
RATINGS = [
    {"dimension": "learning_difficulty",       "label_zh": "中高", "stars": 4,
     "note": "理论+实操双线，涉及AS/NZS 3000标准和安全规范"},
    {"dimension": "learning_duration",         "label_zh": "较长", "stars": 4,
     "note": "正式学徒4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty",  "label_zh": "中高", "stars": 4,
     "note": "各州持牌考试独立，跨州需重考"},
    {"dimension": "job_demand",                "label_zh": "极高", "stars": 5,
     "note": "MLTSSL在列，技工填补率仅54.3%（2025 JSA报告）"},
    {"dimension": "competition",               "label_zh": "较低", "stars": 2,
     "note": "供不应求，持牌后通常数周内可找到工作"},
    {"dimension": "work_intensity",            "label_zh": "中高", "stars": 4,
     "note": "体力劳动，高空/密闭/高温；FIFO轮班强度大"},
    {"dimension": "income_level",              "label_zh": "较高", "stars": 4,
     "note": "中位数 ~$94,000~$104,000；矿业可超 $200,000"},
    {"dimension": "future_prospect",           "label_zh": "极佳", "stars": 5,
     "note": "可再生能源转型驱动，2030前缺口持续扩大"},
    {"dimension": "ai_risk",                   "label_zh": "极低", "stars": 1,
     "note": "现场操作、安全判断无法自动化替代"},
    {"dimension": "pr_friendliness",           "label_zh": "极高", "stars": 5,
     "note": "189/190/491/482/186 多路径，MLTSSL长期在列"},
    {"dimension": "pr_difficulty",             "label_zh": "中等", "stars": 3,
     "note": "TRA评估周期长、各州持牌不统一是主要障碍"},
]

# ── 适合人群 ───────────────────────────────────────────────────
SUITABILITY_FIT = [
    "有电气背景（国内电工证/相关职校学历），希望通过技能移民路径来澳",
    "接受体力劳动和户外工作，不抵触高空、密闭空间和高温环境",
    "目标是矿业高薪（FIFO）或自建电气承包公司",
    "希望走职业技能移民，而非纯学历/英语路线",
    "年龄30~40岁，有足够时间完成TRA评估并积累澳洲工作经验",
]

SUITABILITY_UNFIT = [
    "不愿意做体力劳动，或无法接受FIFO轮班工作模式",
    "期望1~2年内快速取得正式资质（学徒至少4年）",
    "对高空、密闭空间、高温环境有明显生理或心理抵触",
    "英语能力极弱且无改善计划（持牌考试和工地沟通均需英语）",
]

# ── 数据来源 ───────────────────────────────────────────────────
SOURCES = [
    {"source_name": "Jobs and Skills Australia",
     "content":     "ANZSCO 341111 职业档案、短缺清单、2025~2035就业预测",
     "url":         "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/341111-electricians-general"},
    {"source_name": "Training.gov.au",
     "content":     "UEE30820 课程标准，3826学时，48个月",
     "url":         "https://training.gov.au/Training/Details/UEE30820"},
    {"source_name": "Department of Home Affairs",
     "content":     "MLTSSL / 签证子类 482、186、189、190、491 条件",
     "url":         "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA (Trades Recognition Australia)",
     "content":     "海外电工技能评估流程、Job Ready Program",
     "url":         "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Glassdoor AU",
     "content":     "电工平均年薪 $94,000（May 2026）",
     "url":         "https://www.glassdoor.com.au/Salaries/electrician-salary-SRCH_KO0,11.htm"},
    {"source_name": "Indeed AU",
     "content":     "电工平均时薪 $53.11（May 2026）",
     "url":         "https://au.indeed.com/career/electrician/salaries"},
    {"source_name": "ERI SalaryExpert",
     "content":     "电工平均年薪 $101,332；高端 $125,000+（2026）",
     "url":         "https://www.salaryexpert.com/salary/job/electrician/australia"},
    {"source_name": "Fair Work Commission",
     "content":     "学徒 Award 最低工资标准，成人学徒 $27.32/hr",
     "url":         "https://www.fairwork.gov.au/pay-and-wages/pay-guides"},
    {"source_name": "TAFE NSW / TAFE SA / WA TAFE",
     "content":     "UEE30820 各州学费及免费/补贴政策（2025）",
     "url":         "https://www.tafensw.edu.au/course-areas/electrotechnology/courses/certificate-iii-in-electrotechnology-electrician--UEE30820-01"},
]

# ── FAQ ────────────────────────────────────────────────────────
FAQS = [
    {
        "faq_type":   "salary",
        "sort_order": 0,
        "question":   "澳洲电工工资多少？",
        "answer":     "中级持牌电工年薪（AUD）约 $88,000~$115,000，全国中位数约 $94,000（Glassdoor 2026）。"
                      "矿业FIFO电工可达 $140,000~$220,000+。学徒期间约 $24,000~$50,000（按年级递增）。",
    },
    {
        "faq_type":   "demand",
        "sort_order": 1,
        "question":   "澳洲电工容易找工作吗？",
        "answer":     "容易。电工长期供不应求，技工类岗位填补率仅54.3%（JSA 2025）。"
                      "Seek 常年挂牌 2,500~4,000 个职位，持牌后通常数周内可入职。",
    },
    {
        "faq_type":   "recognition",
        "sort_order": 2,
        "question":   "中国电工证澳洲认可吗？",
        "answer":     "不直接认可，但可通过 TRA Job Ready Program 互认，周期约12~18个月。"
                      "完成评估后须申请各州 Electrical Licence 方可合法执业。",
    },
    {
        "faq_type":   "ai_risk",
        "sort_order": 3,
        "question":   "电工会被AI替代吗？",
        "answer":     "替代风险极低。电工高度依赖现场判断、手工接线和安全规范执行，"
                      "目前无成熟自动化方案可替代现场操作，且安全责任法律要求人工签核。",
    },
    {
        "faq_type":   "age_limit",
        "sort_order": 4,
        "question":   "澳洲电工有年龄限制吗？",
        "answer":     "法律上无明确年龄上限。学徒制招募偏好35岁以下，但40岁以上可走TRA互认路径，"
                      "跳过4年学徒期直接申请持牌。技术移民打分中年龄45岁以上无加分。",
    },
    {
        "faq_type":   "education_limit",
        "sort_order": 5,
        "question":   "澳洲电工有学历限制吗？",
        "answer":     "无大学学历要求。完成 Certificate III（职业技能证书）即可执业，"
                      "相当于国内中专/技校水平，高中毕业即可直接入读 TAFE 学徒课程。",
    },
    {
        "faq_type":   "difficulty",
        "sort_order": 6,
        "question":   "澳洲电工难学吗？",
        "answer":     "难度中高。理论涉及电气原理、AS/NZS 3000 澳洲电气标准和安全法规；"
                      "实操需大量现场训练。有国内电气基础者适应较快，零基础需约6~12个月入门。",
    },
    {
        "faq_type":   "comparison",
        "sort_order": 7,
        "question":   "电工和水管工（Plumber）哪个更适合移民澳洲？",
        "answer":     "两者均在 MLTSSL，PR路径相近。电工整体薪资略高（中位 $94k vs 水管工 ~$85k），"
                      "需求量更大；水管工学习周期相似，矿业和建筑需求同样旺盛。"
                      "详见「电工 vs 水管工」职业比较板块（即将上线）。",
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

    print("\n[OK] 电工数据入库完成")


if __name__ == "__main__":
    run()
