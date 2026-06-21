"""澳洲汽车技工（321211）数据入库。数据来源：JSA、Indeed、PayScale、SEEK、ERI、TRA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "321211", "anzsco_title": "Motor Mechanic (General)", "category": "技工",
    "workforce_size": 75000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Electric Vehicle (EV) Servicing","Hybrid Vehicle Technology","Fleet & Mining Vehicle Maintenance","Diagnostics & Automotive Tech","4WD & Truck Servicing"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "汽车技工",
    "summary": "汽车技工负责诊断、维修和保养轿车、卡车及各类机动车辆，广泛服务于零售修车厂、汽车经销商、车队管理和矿业。在澳大利亚，汽车技工持 Certificate III 执业，列入技术短缺清单，EV和混合动力技术转型带来新增需求。",
    "forecast_note": "JSA 预测技工类至2035年新增约195,800个岗位。EV普及驱动大量旧技工转型升级需求，具备电动车技能的技工薪资溢价显著。",
    "trend_summary": "电动车（EV）和混合动力技术转型是最大变量，具备高压电气技能的汽车技工极度短缺。传统燃油车维修需求短期内不会消失。",
}
I18N_EN = {
    "locale": "en", "name": "Motor Mechanic",
    "summary": "Motor mechanics diagnose, repair and maintain motor vehicles across retail workshops, dealerships, fleet operations and mining. Certificate III is required for entry. EV transition is creating significant new demand.",
    "forecast_note": "JSA projects ~195,800 new trades jobs by 2035 (+9.8%). EV adoption is accelerating demand for mechanics with high-voltage electrical certification.",
    "trend_summary": "EV and hybrid technology transition is the key demand driver. Mechanics with EV high-voltage certification command significant salary premiums.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（含 AUR30620 Certificate III in Light Vehicle Mechanical Technology）", "duration": "42~48个月", "cost_min": 0, "cost_max": 1200, "cost_note": "各州补贴，NSW 大部分免费，WA 上限 $1,200", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "含TRA评估费及实习期费用", "sort_order": 1},
    {"stage": "电动车高压安全认证（EV HV Certificate）", "duration": "3~5天（短课程）", "cost_min": 500, "cost_max": 1500, "cost_note": "具备EV维修资质的溢价资质，建议持牌后尽早考取", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Light Vehicle Mechanical Technology (AUR30620)", "issuer": "TAFE / RTO", "note": "全国统一课程，轿车维修执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Certificate III in Heavy Commercial Vehicle Mechanical Technology (AUR31120)", "issuer": "TAFE / RTO", "note": "重型商业车维修资质（可选，扩展就业范围）", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "EV High Voltage Safety Certificate", "issuer": "认可RTO（如 NRSPP）", "note": "电动车维修安全强制要求，EV经销商必须", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "Trades Recognition Australia", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 3500, "note": "全国，含轿车、4WD、经销商和车队维修岗"},
    {"platform": "Indeed",   "count_min": 1200, "count_max": 2000, "note": "含学徒岗和兼职"},
    {"platform": "LinkedIn", "count_min": 500,  "count_max": 1000, "note": "偏经销商、车队和EV专业岗"},
]
SALARIES = [
    {"experience": "学徒 1年级", "salary_min": 20000, "salary_max": 27000, "salary_note": "Vehicle Repair Award 最低工资", "sort_order": 0},
    {"experience": "学徒 2~4年级", "salary_min": 27000, "salary_max": 44000, "salary_note": "约 $22~$28/hr", "sort_order": 1},
    {"experience": "初级技工（持证后 1~3年）", "salary_min": 60000, "salary_max": 75000, "salary_note": "Indeed 25th percentile；$28.05/hr（PayScale 2026）", "sort_order": 2},
    {"experience": "中级技工（3~8年）", "salary_min": 75000, "salary_max": 92000, "salary_note": "Indeed 平均 $75,440；SEEK 中位 ~$85k", "sort_order": 3},
    {"experience": "资深技工 / 主任技师（8年+）", "salary_min": 92000, "salary_max": 115000, "salary_note": "含EV高压资质溢价，经销商主任技师薪资更高", "sort_order": 4},
    {"experience": "矿业 FIFO 技工（WA/QLD）", "salary_min": 110000, "salary_max": 150000, "salary_note": "矿业车辆维修高薪岗，轮班津贴+FIFO补贴", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，永居", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "现代汽车诊断技术要求强；EV高压系统额外学习"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒约4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III 考核可备考通过；EV认证难度低"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 5, "note": "MLTSSL在列，EV转型驱动额外需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，EV技能技工尤其稀缺"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "体力劳动，汽油/油脂/噪音环境常见"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 3, "note": "中位数约 $75k~$85k，低于电工但高于油漆工"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "EV革命重构整个行业，具备EV技能者前景极佳"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助诊断已普及，但实际维修操作仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，189/190/491均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估周期长，竞争中等"},
]
SUITABILITY_FIT = [
    "有汽车维修/机械背景（国内职校或工作经验），希望技能移民来澳",
    "对新技术感兴趣，愿意持续学习EV高压电气技能",
    "目标是矿业车辆维修高薪（FIFO）或自建修车厂",
    "年龄28~42岁，有时间完成TRA评估",
]
SUITABILITY_UNFIT = [
    "对汽油、油脂气味或噪音有明显生理抵触",
    "完全无机械基础，且不愿投入时间学习",
    "期望高薪快速入职（汽车技工薪资起点低于电工）",
]
SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 321211 职业档案与短缺清单", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Indeed AU", "content": "汽车技工平均年薪 $75,440（2026）", "url": "https://au.indeed.com/career/automotive-mechanic/salaries"},
    {"source_name": "PayScale AU", "content": "汽车技工平均时薪 $28.05（2026）", "url": "https://www.payscale.com/research/AU/Job=Automobile_Mechanic/Hourly_Rate"},
    {"source_name": "TRA", "content": "海外汽车技工技能评估", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲汽车技工工资多少？", "answer": "中级技工年薪约 $75,000~$92,000，Indeed 平均 $75,440（2026）。矿业FIFO可达 $110k~$150k，具备EV高压资质者薪资溢价显著，学徒约 $20k~$44k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲汽车技工容易找工作吗？", "answer": "容易。MLTSSL在列，Seek 常年挂牌 2,000~3,500 个职位，EV技能技工尤其稀缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国汽车维修证澳洲认可吗？", "answer": "不直接认可，需通过 TRA Job Ready Program 评估，周期约12~18个月。有国内汽车维修经验者评估周期可缩短。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "汽车技工会被AI替代吗？", "answer": "部分替代，但整体风险较低。AI辅助诊断已广泛应用，但实际拆装维修和EV高压电气操作仍需人工，AI技工岗位不减反增。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲汽车技工有年龄限制吗？", "answer": "无法律上限。35岁以上可走TRA互认路径跳过学徒期，移民打分45岁以上无加分。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲汽车技工需要大学学历吗？", "answer": "不需要。完成 Certificate III（AUR30620）即可执业，高中毕业可直接申请学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲汽车技工难学吗？", "answer": "难度中等。现代汽车电子诊断技术要求日益提升，EV高压电气是额外挑战，有国内汽车维修基础者适应较快。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "汽车技工和柴油机技工哪个更适合移民澳洲？", "answer": "柴油机技工薪资更高（中位~$95k vs 汽车技工~$80k），矿业需求更旺；汽车技工就业量更大，更容易入门。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 汽车技工数据入库完成")

if __name__ == "__main__":
    run()
