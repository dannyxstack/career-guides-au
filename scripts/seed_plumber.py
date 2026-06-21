"""
澳洲水管工（334111）数据入库脚本。
数据来源：Jobs and Skills Australia、Indeed、Glassdoor、ERI SalaryExpert、SEEK、
         Fair Work Commission、TRA、Department of Home Affairs（2025-2026）。
"""
import sys, os, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code":  "334111",
    "anzsco_title": "Plumber (General)",
    "category":     "技工",
    "workforce_size": 85000,
    "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential & Commercial Construction","Water Infrastructure Upgrades","Gas Fitting & Renewables","Stormwater & Drainage Systems","NDIS & Accessible Housing"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "水管工",
    "summary": "水管工负责安装、维护和修缮供水、排水、煤气和消防管道系统，广泛服务于住宅、商业和工业领域。在澳大利亚，水管工属于持牌强制行业，长期位居技术短缺清单，是技术移民的高频职业之一。",
    "forecast_note": "Jobs and Skills Australia 预测技工类至2035年新增就业约195,800人（+9.8%）。水管工技工填补率持续低位，全澳建筑业扩张驱动需求旺盛。",
    "trend_summary": "住宅建设热潮、老旧基础设施更新和绿色能源（热泵热水系统、氢气管道）持续拉动需求，AI替代风险极低。",
}
I18N_EN = {
    "locale": "en", "name": "Plumber",
    "summary": "Plumbers install, maintain and repair water supply, drainage, gas and fire protection piping systems across residential, commercial and industrial sectors. Licensing is mandatory in all Australian states.",
    "forecast_note": "JSA projects ~195,800 new Technicians & Trades Worker jobs by 2035 (+9.8%). Plumbers remain among the hardest trades to recruit nationally.",
    "trend_summary": "Residential construction boom, ageing infrastructure renewal, and green energy transitions (heat pump hot water, hydrogen piping) sustain strong demand through 2030.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（含 Certificate III in Plumbing CPC32420）", "duration": "42~48个月（约3.5~4年）", "cost_min": 0, "cost_max": 1500, "cost_note": "各州补贴差异：NSW Smart & Skilled 补贴大部分学费；WA 约上限 $1,200；QLD 约 $1.60/课时", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "含 TRA 评估费、补考费及行政费", "sort_order": 1},
    {"stage": "各州持牌考试（Plumbing Licence）", "duration": "1~3个月", "cost_min": 300, "cost_max": 800, "cost_note": "各州独立持牌，跨州需重新申请", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Plumbing (CPC32420)", "issuer": "TAFE / RTO", "note": "全国统一课程，执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Plumber Licence（各州）", "issuer": "各州 Fair Trading / Building Commission", "note": "合法施工强制持牌", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Gas Fitting Endorsement（可选）", "issuer": "各州", "note": "煤气接管额外资质，薪资溢价明显", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "Trades Recognition Australia", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1800, "count_max": 3000, "note": "全国，含学徒岗、住宅及商业管道岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 1800, "note": "含兼职、合同工"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 900,  "note": "偏企业直招及项目管理岗"},
]
SALARIES = [
    {"experience": "学徒 1年级", "salary_min": 22000, "salary_max": 30000, "salary_note": "Fair Work Award 最低工资", "sort_order": 0},
    {"experience": "学徒 2~4年级", "salary_min": 30000, "salary_max": 50000, "salary_note": "约 $27~$33/hr", "sort_order": 1},
    {"experience": "初级水管工（持牌后 1~3年）", "salary_min": 72000, "salary_max": 88000, "salary_note": "Indeed 25th percentile", "sort_order": 2},
    {"experience": "中级水管工（3~8年）", "salary_min": 88000, "salary_max": 108000, "salary_note": "SEEK 区间 $85k~$105k；ERI 平均 $99,866；Indeed $47.19/hr", "sort_order": 3},
    {"experience": "资深水管工 / 承包商（8年+）", "salary_min": 108000, "salary_max": 135000, "salary_note": "含煤气资质及承包利润", "sort_order": 4},
    {"experience": "矿业 FIFO 水管工（WA/QLD）", "salary_min": 130000, "salary_max": 180000, "salary_note": "轮班津贴 + FIFO 补贴", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，TRT流需持482满2年", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，永居，首选路线", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "理论+实操双线，涉及管道规范、煤气和消防系统"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒约4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "各州持牌独立，煤气资质额外考试"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL长期在列，填补率持续低位"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，持牌后数周可入职"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "体力劳动，密闭空间和高压管道作业常见"},
    {"dimension": "income_level",             "label_zh": "较高", "stars": 4, "note": "中位数约 $88k~$100k；矿业可达 $180k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "基建扩张、绿色热水系统、氢气管道均为增长方向"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场施工和密闭空间操作无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，多路径均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA周期长、跨州持牌不统一"},
]
SUITABILITY_FIT = [
    "有给排水/管道/水暖背景（国内职校或工作经验），希望技能移民来澳",
    "接受体力劳动和密闭空间作业，不抵触水、污水和煤气管道环境",
    "目标是矿业高薪（FIFO）或自建管道承包公司",
    "年龄30~42岁，有时间完成TRA评估并积累澳洲经验",
    "希望走职业技能移民而非学历路线",
]
SUITABILITY_UNFIT = [
    "对密闭空间或污水管道作业有明显生理抵触",
    "期望1~2年内快速取得资质",
    "英语能力极弱且无改善计划",
    "完全无管道或水暖基础，且不愿从学徒期开始",
]
SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 334111 职业档案、短缺清单、就业预测", "url": "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/334111-plumbers"},
    {"source_name": "training.gov.au", "content": "CPC32420 Certificate III in Plumbing 课程标准", "url": "https://training.gov.au/Training/Details/CPC32420"},
    {"source_name": "ERI SalaryExpert", "content": "水管工平均年薪 $99,866（2026）", "url": "https://www.salaryexpert.com/salary/job/plumber/australia"},
    {"source_name": "SEEK AU", "content": "水管工薪资区间 $85,000~$105,000（2026）", "url": "https://au.seek.com/career-advice/role/plumber/salary"},
    {"source_name": "Indeed AU", "content": "水管工平均时薪 $47.19（2026）", "url": "https://au.indeed.com/career/plumber/salaries"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外水管工技能评估流程", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲水管工工资多少？", "answer": "中级持牌水管工年薪约 $88,000~$108,000，SEEK 区间 $85k~$105k，ERI 平均 $99,866（2026）。矿业FIFO可达 $130k~$180k，学徒约 $22k~$50k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲水管工容易找工作吗？", "answer": "容易。MLTSSL长期在列，Seek 常年挂牌 1,800~3,000 个职位，持牌后通常数周内可入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国水管工证澳洲认可吗？", "answer": "不直接认可，需通过 TRA Job Ready Program 评估，周期约12~18个月。完成后须申请各州 Plumbing Licence 方可执业。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "水管工会被AI替代吗？", "answer": "替代风险极低。现场管道施工、密闭空间操作高度依赖人工，无成熟自动化方案。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲水管工有年龄限制吗？", "answer": "无法律上限。35岁以上可走TRA互认路径跳过4年学徒期，移民打分45岁以上无加分。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲水管工需要大学学历吗？", "answer": "不需要。完成 Certificate III（CPC32420）即可执业，高中毕业可直接申请学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲水管工难学吗？", "answer": "难度中高。理论涉及管道规范、煤气和污水系统；有国内给排水或水暖基础者适应较快。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "水管工和电工哪个更适合移民澳洲？", "answer": "两者均在MLTSSL，路径相近。电工薪资略高（中位~$94k vs 水管工~$88k），难度相仿；水管工学习周期略短，矿业和建筑需求同样旺盛。"},
]

def run():
    with get_cursor() as cur:
        cur.execute("""INSERT INTO occupations (anzsco_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE anzsco_title=VALUES(anzsco_title),category=VALUES(category),workforce_size=VALUES(workforce_size),shortage_listed=VALUES(shortage_listed),growth_areas=VALUES(growth_areas)""", (OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],OCCUPATION["category"],OCCUPATION["workforce_size"],OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"]))
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s", (OCCUPATION["anzsco_code"],))
        occ_id = cur.fetchone()["id"]
        print(f"[occupations] id={occ_id} {OCCUPATION['anzsco_code']} {OCCUPATION['anzsco_title']}")
        for i18n in [I18N_ZH, I18N_EN]:
            cur.execute("""INSERT INTO occupations_i18n (occupation_id,locale,name,summary,forecast_note,trend_summary) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name),summary=VALUES(summary),forecast_note=VALUES(forecast_note),trend_summary=VALUES(trend_summary)""", (occ_id,i18n["locale"],i18n["name"],i18n["summary"],i18n["forecast_note"],i18n["trend_summary"]))
        print("[occupations_i18n] 2 locales")
        cur.execute("DELETE FROM occupation_ratings WHERE occupation_id=%s", (occ_id,))
        for r in RATINGS:
            cur.execute("INSERT INTO occupation_ratings (occupation_id,dimension,label_zh,stars,note) VALUES (%s,%s,%s,%s,%s)", (occ_id,r["dimension"],r["label_zh"],r["stars"],r.get("note")))
        print(f"[ratings] {len(RATINGS)}")
        cur.execute("DELETE FROM occupation_education WHERE occupation_id=%s", (occ_id,))
        for e in EDUCATION:
            cur.execute("INSERT INTO occupation_education (occupation_id,stage,duration,cost_min,cost_max,cost_note,sort_order) VALUES (%s,%s,%s,%s,%s,%s,%s)", (occ_id,e["stage"],e["duration"],e["cost_min"],e["cost_max"],e["cost_note"],e["sort_order"]))
        print(f"[education] {len(EDUCATION)}")
        cur.execute("DELETE FROM occupation_qualifications WHERE occupation_id=%s", (occ_id,))
        for q in QUALIFICATIONS:
            cur.execute("INSERT INTO occupation_qualifications (occupation_id,qual_name,issuer,note,is_mandatory,sort_order) VALUES (%s,%s,%s,%s,%s,%s)", (occ_id,q["qual_name"],q.get("issuer"),q.get("note"),q["is_mandatory"],q["sort_order"]))
        print(f"[qualifications] {len(QUALIFICATIONS)}")
        cur.execute("DELETE FROM occupation_job_listings WHERE occupation_id=%s", (occ_id,))
        for jl in JOB_LISTINGS:
            cur.execute("INSERT INTO occupation_job_listings (occupation_id,platform,count_min,count_max,note,snapshot_date) VALUES (%s,%s,%s,%s,%s,%s)", (occ_id,jl["platform"],jl["count_min"],jl["count_max"],jl["note"],TODAY))
        print(f"[job_listings] {len(JOB_LISTINGS)}")
        cur.execute("DELETE FROM occupation_salaries WHERE occupation_id=%s", (occ_id,))
        for s in SALARIES:
            cur.execute("INSERT INTO occupation_salaries (occupation_id,experience,salary_min,salary_max,salary_note,sort_order) VALUES (%s,%s,%s,%s,%s,%s)", (occ_id,s["experience"],s["salary_min"],s["salary_max"],s["salary_note"],s["sort_order"]))
        print(f"[salaries] {len(SALARIES)}")
        cur.execute("DELETE FROM occupation_visa_pathways WHERE occupation_id=%s", (occ_id,))
        for v in VISA_PATHWAYS:
            cur.execute("INSERT INTO occupation_visa_pathways (occupation_id,visa_subclass,visa_name,description,sort_order) VALUES (%s,%s,%s,%s,%s)", (occ_id,v["visa_subclass"],v["visa_name"],v["description"],v["sort_order"]))
        print(f"[visa_pathways] {len(VISA_PATHWAYS)}")
        cur.execute("DELETE FROM occupation_suitability WHERE occupation_id=%s", (occ_id,))
        for i,item in enumerate(SUITABILITY_FIT):
            cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'fit',%s,%s)", (occ_id,item,i))
        for i,item in enumerate(SUITABILITY_UNFIT):
            cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'unfit',%s,%s)", (occ_id,item,i))
        print(f"[suitability] {len(SUITABILITY_FIT)} fit, {len(SUITABILITY_UNFIT)} unfit")
        cur.execute("DELETE FROM occupation_sources WHERE occupation_id=%s", (occ_id,))
        for s in SOURCES:
            cur.execute("INSERT INTO occupation_sources (occupation_id,source_name,content,url) VALUES (%s,%s,%s,%s)", (occ_id,s["source_name"],s.get("content"),s.get("url")))
        print(f"[sources] {len(SOURCES)}")
        cur.execute("DELETE FROM occupation_faqs WHERE occupation_id=%s", (occ_id,))
        for faq in FAQS:
            cur.execute("INSERT INTO occupation_faqs (occupation_id,faq_type,sort_order) VALUES(%s,%s,%s)", (occ_id,faq["faq_type"],faq["sort_order"]))
            faq_id = cur.lastrowid
            cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'zh-CN',%s,%s) ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)", (faq_id,faq["question"],faq["answer"]))
        print(f"[faqs] {len(FAQS)}")
    print("\n[OK] 水管工数据入库完成")

if __name__ == "__main__":
    run()
