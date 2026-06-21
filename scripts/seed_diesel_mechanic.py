"""澳洲柴油机技工（321212）数据入库。数据来源：JSA、Indeed、PayScale、SEEK、ERI、TRA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "321212", "anzsco_title": "Diesel Motor Mechanic", "category": "技工",
    "workforce_size": 45000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Mining Equipment Maintenance (FIFO)","Transport & Logistics Fleet","Agriculture & Earthmoving Equipment","Defence Vehicle Maintenance","Renewable Energy & Construction Equipment"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "柴油机技工",
    "summary": "柴油机技工负责诊断、维修和保养柴油发动机驱动的重型设备，包括矿业机械、运输卡车、农业设备和建筑机械。澳大利亚矿业和物流行业的庞大需求使柴油机技工长期列于技术短缺清单最高需求类别。",
    "forecast_note": "JSA 预测技工类至2035年新增约195,800个岗位。矿业自动化和新型重型电气设备的普及驱动柴油机技工的技能升级需求。",
    "trend_summary": "矿业FIFO是柴油机技工薪资最高的就业方向，WA和QLD矿区长期短缺。物流车队维修和农业设备市场同样旺盛。",
}
I18N_EN = {
    "locale": "en", "name": "Diesel Motor Mechanic",
    "summary": "Diesel motor mechanics diagnose, repair and maintain diesel-powered heavy equipment including mining machinery, trucks, agricultural and construction equipment. Mining and logistics sectors sustain very high and persistent demand.",
    "forecast_note": "JSA projects ~195,800 new trades jobs by 2035 (+9.8%). Mining automation and new electric heavy equipment create significant upskilling demand.",
    "trend_summary": "Mining FIFO roles offer the highest salaries. WA and QLD mine sites have chronic shortages. Transport logistics and agriculture also sustain strong demand.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（含 AUR31020 Certificate III in Heavy Commercial Vehicle Mechanical Technology）", "duration": "42~48个月", "cost_min": 0, "cost_max": 1200, "cost_note": "各州补贴，WA/QLD 矿业州补贴力度较强", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5500, "cost_note": "含TRA评估费及实习期费用；重型设备评估较轿车更复杂", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Heavy Commercial Vehicle Mechanical Technology (AUR31020)", "issuer": "TAFE / RTO", "note": "全国统一课程，重型柴油维修基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Certificate III in Mobile Plant Technology (AUR32720)", "issuer": "TAFE / RTO", "note": "矿业移动设备维修专项资质（可选）", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "High Voltage / Electrical Safety Certificate", "issuer": "认可RTO", "note": "矿业电气设备维修安全证书", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "Trades Recognition Australia", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 2800, "note": "全国，以矿业和运输物流为主，WA需求最强"},
    {"platform": "Indeed",   "count_min": 800,  "count_max": 1500, "note": "含学徒岗和合同工"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 900,  "note": "偏矿业公司直招和工程管理岗"},
]
SALARIES = [
    {"experience": "学徒 1年级", "salary_min": 21000, "salary_max": 28000, "salary_note": "Fair Work Award 最低工资", "sort_order": 0},
    {"experience": "学徒 2~4年级", "salary_min": 28000, "salary_max": 46000, "salary_note": "约 $23~$30/hr", "sort_order": 1},
    {"experience": "初级技工（持证后 1~3年）", "salary_min": 70000, "salary_max": 86000, "salary_note": "Indeed 25th percentile", "sort_order": 2},
    {"experience": "中级技工（3~8年）", "salary_min": 86000, "salary_max": 110000, "salary_note": "SEEK 区间 $90k~$110k；Indeed 平均 $46.93/hr（约 $97k）", "sort_order": 3},
    {"experience": "资深技工 / 主任（8年+）", "salary_min": 110000, "salary_max": 135000, "salary_note": "含工地主任职责和专业矿业设备资质", "sort_order": 4},
    {"experience": "矿业 FIFO 技工（WA/QLD）", "salary_min": 140000, "salary_max": 200000, "salary_note": "矿业轮班津贴+FIFO补贴，WA矿区顶级岗位超 $200k", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，WA/QLD对柴油机技工需求旺盛", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿业地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "重型设备诊断和电控系统复杂，矿业专项设备难度高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒约4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "矿业安全认证（如 Generic Induction）为额外门槛"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，矿业持续扩张，WA/QLD长期短缺"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "矿业FIFO柴油机技工极度稀缺，薪资溢价明显"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 5, "note": "重体力劳动，FIFO轮班（12hr）强度大；油污噪音环境"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "矿业FIFO中位数 $140k~$200k，是技工类薪资最高之一"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "矿业扩张持续，物流车队和农业设备需求旺盛"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助诊断已应用，但矿业设备重型维修仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，WA/QLD州提名机会多"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估周期长，但矿业雇主担保482路径较快"},
]
SUITABILITY_FIT = [
    "有重型机械/柴油发动机/矿业设备维修背景，希望技能移民来澳",
    "接受FIFO轮班（8/6或14/7）和重体力工作环境",
    "目标是WA/QLD矿业高薪岗位（$140k~$200k+）",
    "年龄25~42岁，体力好，能适应矿区生活",
    "愿意持续考取矿业安全认证以提升薪资竞争力",
]
SUITABILITY_UNFIT = [
    "无法接受FIFO轮班（长期离家）工作模式",
    "对油污、噪音和重体力有明显生理抵触",
    "完全无重型机械或柴油发动机维修基础",
]
SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 321212 职业档案与短缺清单", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "SEEK AU", "content": "柴油机技工薪资区间 $90k~$110k（2026）", "url": "https://www.seek.com.au/career-advice/role/heavy-diesel-mechanic/salary"},
    {"source_name": "Indeed AU", "content": "柴油机技工平均时薪 $46.93（2026）", "url": "https://au.indeed.com/career/diesel-mechanic/salaries"},
    {"source_name": "PayScale AU", "content": "柴油机技工薪资数据（2026）", "url": "https://www.payscale.com/research/AU/Job=Diesel_Mechanic/Hourly_Rate"},
    {"source_name": "TRA", "content": "海外柴油机技工技能评估", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲柴油机技工工资多少？", "answer": "中级技工年薪约 $86,000~$110,000，Indeed 平均 $46.93/hr（约 $97k）。矿业FIFO可达 $140k~$200k+，是技工类薪资最高之一，学徒约 $21k~$46k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲柴油机技工容易找工作吗？", "answer": "极容易。矿业柴油机技工极度短缺，MLTSSL长期在列，Seek 常年挂牌 1,500~2,800 个职位，WA/QLD矿区竞争极低。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国重型机械维修证澳洲认可吗？", "answer": "不直接认可，需通过 TRA Job Ready Program 评估，重型设备评估周期约12~18个月。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "柴油机技工会被AI替代吗？", "answer": "短期内风险较低。AI辅助诊断已在矿业广泛应用，但重型设备维修操作、矿区紧急抢修仍高度依赖人工。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲柴油机技工有年龄限制吗？", "answer": "无法律上限，但FIFO高强度作业建议42岁以下。45岁以上移民打分无加分，建议尽早启动签证申请。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲柴油机技工需要大学学历吗？", "answer": "不需要。完成 Certificate III（AUR31020）即可执业，高中毕业可直接申请学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲柴油机技工难学吗？", "answer": "难度中高。重型设备电控诊断和矿业专用机械（CAT/Komatsu）技术复杂，有国内重型设备维修基础者适应较快。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "柴油机技工和电工哪个更适合移民澳洲？", "answer": "柴油机技工矿业薪资更高（$140k~$200k+ vs 电工 $140k~$220k相近），但工作环境更恶劣；电工就业范围更广，不限于矿业。有矿业背景者首选柴油机技工。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 柴油机技工数据入库完成")

if __name__ == "__main__":
    run()
