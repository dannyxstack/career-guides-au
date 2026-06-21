"""澳洲餐厅经理（141111）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "141111", "anzsco_title": "Cafe or Restaurant Manager",
    "category": "餐饮/酒店/旅游", "workforce_size": 65000, "shortage_listed": 1,
    "growth_areas": json.dumps(["高端餐厅运营管理","连锁餐饮区域经理","外卖平台整合运营（Uber Eats/DoorDash）","活动餐饮承包管理","可持续餐饮（植物性菜单）管理"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "餐厅经理/咖啡馆经理",
    "summary": "餐厅经理负责餐饮场所的日常运营、人员管理、食品安全合规、成本控制和顾客体验。澳洲有超过 45,000 家咖啡馆和 65,000 家餐厅，对有经验的餐饮管理人员需求持续旺盛。MLTSSL在列，是餐饮行业技术移民最便捷的管理职业之一。",
    "forecast_note": "JSA预测餐厅经理就业至2030年净增约8,000人。旅游业反弹、CBD商业区餐饮复苏和高端餐饮市场扩张是主要增长驱动力。",
    "trend_summary": "澳洲餐饮业COVID后全面恢复并持续扩张，尤其是外卖平台整合和高端餐饮体验需求增长。有运营管理经验（人员调配/库存/POS系统/食品安全）的餐厅经理短缺，雇主担保482在餐饮行业非常活跃。",
}
I18N_EN = {
    "locale": "en", "name": "Restaurant / Cafe Manager",
    "summary": "Restaurant managers oversee daily operations, staff management, food safety compliance, cost control and customer experience at food service venues. With over 45,000 cafes and 65,000 restaurants in Australia, demand for experienced food service managers is sustained. MLTSSL-listed, making this one of the most accessible management occupations in hospitality for skilled migration.",
    "forecast_note": "JSA projects net new demand for ~8,000 restaurant managers by 2030. Tourism rebound, CBD commercial district hospitality recovery and premium dining market expansion are the main growth drivers.",
    "trend_summary": "Australia's hospitality industry has fully recovered post-COVID and continues expanding, especially delivery platform integration and premium dining experience demand growth. Restaurant managers with operational experience (rostering/inventory/POS/food safety) are in short supply, with employer-sponsored 482 visas very active in hospitality.",
}
EDUCATION = [
    {"stage": "Certificate IV in Hospitality（SIT40422）", "duration": "12个月（全日制）", "cost_min": 3000, "cost_max": 15000, "cost_note": "餐厅经理资质的主流路径；TAFE或私立酒店管理学院", "sort_order": 0},
    {"stage": "Diploma of Hospitality Management（SIT50422）", "duration": "18~24个月", "cost_min": 5000, "cost_max": 25000, "cost_note": "酒店管理文凭，提升管理岗竞争力", "sort_order": 1},
    {"stage": "实际工作经验（至少2年餐饮管理经历）", "duration": "持续", "cost_min": 0, "cost_max": 0, "cost_note": "TRA/Vetassess评估需要工作经验证明；经验比学历更重要", "sort_order": 2},
    {"stage": "Food Safety Supervisor + RSA证书", "duration": "1~2天", "cost_min": 150, "cost_max": 500, "cost_note": "餐饮场所法律必须的食品安全和酒精负责任服务资质", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate IV/Diploma of Hospitality Management", "issuer": "TAFE / 认可私立机构", "note": "餐厅经理技术移民评估的核心学历要求", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Food Safety Supervisor Certificate", "issuer": "各州认可培训机构", "note": "所有餐饮场所管理者的法律要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "RSA（Responsible Service of Alcohol）", "issuer": "各州认可机构", "note": "服务酒精饮料的餐饮场所大多数州的法律要求", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "Vetassess 技能评估（ANZSCO 141111）", "issuer": "Vetassess", "note": "189/190/491技术移民申请必须的技能评估", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 5000, "note": "全国，含餐厅经理/咖啡馆经理/酒吧经理岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 4000, "note": "含连锁餐饮、独立餐厅和咖啡馆管理岗"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 3000, "note": "连锁餐饮集团和酒店餐饮部直招"},
]
SALARIES = [
    {"experience": "助理餐厅经理（0~2年）", "salary_min": 62000, "salary_max": 75000, "salary_note": "助理或副经理起薪", "sort_order": 0},
    {"experience": "餐厅经理（2~8年）", "salary_min": 72000, "salary_max": 92000, "salary_note": "SEEK 区间 $80k~$90k；Indeed 均值 $73,915；Glassdoor 均值 $83,400（2026）", "sort_order": 1},
    {"experience": "高级餐厅经理 / 区域经理（8~15年）", "salary_min": 90000, "salary_max": 120000, "salary_note": "连锁餐饮区域运营经理；高端餐厅总经理约 $100k~$120k", "sort_order": 2},
    {"experience": "餐饮总监 / F&B Director（12年+）", "salary_min": 120000, "salary_max": 200000, "salary_note": "五星酒店餐饮总监或大型餐饮集团总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，餐厅和连锁餐饮集团最常见路径", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，需满足2年担保期", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，Vetassess评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，各州均有通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区餐饮管理人员严重短缺，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要运营管理+人员管理+食品安全+成本控制综合能力"},
    {"dimension": "learning_duration",        "label_zh": "中低", "stars": 2, "note": "Certificate IV约12个月；实际工作经验比学历更重要"},
    {"dimension": "certification_difficulty", "label_zh": "中低", "stars": 2, "note": "Vetassess评估难度中等偏低；经验和食品安全证书是关键"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，全国餐饮管理人员持续短缺，雇主担保极活跃"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "有资格的餐饮经理供不应求；偏远地区竞争极低"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "长时间工作（含周末和节假日）、多任务处理；餐饮高峰期压力大"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "餐厅经理 $72k~$92k；区域经理 $90k~$120k；整体薪资中等"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "旅游业扩张和高端餐饮增长推动持续需求；数字化餐饮运营是新技能方向"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "餐饮运营管理中人际协调、临场决策和顾客关系不可替代；POS系统AI化影响有限"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，是餐饮类移民路径最清晰的管理职业，雇主担保极活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "Vetassess评估清晰；雇主担保482路径非常活跃；偏远491更容易"},
]
SUITABILITY_FIT = ["有2年以上餐厅/咖啡馆管理工作经验，持有食品安全监督员证书", "有澳洲或国际餐饮品牌管理经验（连锁或独立高端餐厅）", "英语沟通能力达到基本运营要求（IELTS 5.5~6.0 即可），可进行日常管理和顾客沟通", "已有澳洲雇主担保意向或正在经营餐饮业务", "愿意接受偏远地区任职（签证更容易，薪资有加成）"]
SUITABILITY_UNFIT = ["无正规餐饮管理经验（仅有服务员或收银经验）", "期望在大城市高端餐厅直接担任总经理（通常需要10年以上资深经验）", "不适应包括周末和节假日的不规律工作时间"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "餐厅经理薪资 $80k~$90k（2026）", "url": "https://au.seek.com/career-advice/role/restaurant-manager/salary"},
    {"source_name": "Indeed AU", "content": "餐厅经理平均薪资 $73,915（2026）", "url": "https://au.indeed.com/career/restaurant-manager/salaries"},
    {"source_name": "Glassdoor AU", "content": "餐厅经理平均薪资 $83,400（2026）", "url": "https://www.glassdoor.com/Salaries/australia-restaurant-manager-salary-SRCH_IL.0,9_IN16_KO10,28.htm"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲餐厅经理工资多少？", "answer": "餐厅经理约 $72,000~$92,000（SEEK $80k~$90k；Indeed $73,915；Glassdoor $83,400）；区域经理/高端总经理约 $90k~$120k；五星酒店餐饮总监约 $120k~$200k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲餐厅经理容易找工作吗？", "answer": "容易。MLTSSL短缺职业，全澳餐饮管理人员持续短缺，SEEK 挂牌约 2,000~5,000 个职位。偏远地区更紧缺，雇主主动为海外经理提供签证担保，是体验型服务业移民路径最顺畅的职业之一。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国餐厅管理经验澳洲认可吗？", "answer": "通过Vetassess技能评估（ANZSCO 141111），中国餐饮管理经验可以认可。需要提供英文雇主证明信、工作职责描述和食品安全培训记录。澳洲雇主特别重视食品安全合规和人员调配能力。建议补考Food Safety Supervisor Certificate（$100~$300，1天课程）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "餐厅经理会被AI替代吗？", "answer": "不会。餐饮运营管理的核心在于实时人员协调、现场问题处理和顾客关系管理，是AI无法替代的。AI工具可以优化排班和库存预测，但这提升了管理效率而不是替代管理者。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲餐厅经理有年龄限制吗？", "answer": "无。有丰富运营经验和稳定性的中年餐饮经理（35~55岁）在澳洲非常受欢迎。餐饮行业年轻员工流动率高，雇主特别重视有经验、稳定的管理者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲餐厅经理需要什么学历？", "answer": "Certificate IV in Hospitality或Diploma of Hospitality Management是技术移民评估的基础；但实际就业中，有2年以上管理经验+食品安全证书比学历更重要。雇主担保482甚至不要求学历，只需要工作经验和食品安全合规能力。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲餐厅经理认证（移民）难吗？", "answer": "难度较低。MLTSSL在列，Vetassess评估路径清晰，雇主担保482非常活跃。建议同时持有Food Safety Supervisor Certificate和RSA，大幅提升评估成功率。偏远地区491路径更容易，多州主动招募餐饮管理人员。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "餐厅经理和厨师哪个更适合移民澳洲？", "answer": "两者都是MLTSSL短缺职业；厨师技术移民路径更清晰（TRA评估成熟），薪资相近；餐厅经理管理类岗位更稳定（坐班/站班比例较厨师合理），职业发展路径（区域经理/总监）更宽广。有烹饪背景者选厨师，有运营管理背景者选餐厅经理。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 餐厅经理数据入库完成")

if __name__ == "__main__":
    run()
