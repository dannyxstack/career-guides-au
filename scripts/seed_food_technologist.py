"""澳洲食品技术师（234299）数据入库。数据来源：JSA、SEEK、Indeed、AIFST（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "234299", "anzsco_title": "Natural and Physical Science Professionals nec",
    "category": "IT/工程", "workforce_size": 12000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Plant-Based & Alternative Protein Development","Food Safety & Regulatory Compliance","Functional Foods & Nutraceuticals","Export Market Development (Asia-Pacific)","Sustainable Packaging & Circular Food Systems"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "食品技术师",
    "summary": "食品技术师开发新食品产品、改进生产工艺、确保食品安全和法规合规。澳洲是全球重要的食品出口国（对亚太市场的清洁食品出口持续增长），植物性食品和功能食品的产品创新推动对食品技术师的需求稳定增长。",
    "forecast_note": "JSA 预测食品技术师至2035年就业增长约6%。植物性蛋白食品（Impossible Foods/本土初创企业）和出口导向功能食品开发是主要驱动力。",
    "trend_summary": "植物基替代蛋白（大豆/豌豆蛋白）和精准发酵是2025-2030年食品科技最大投资方向。澳洲食品法典（FSANZ）的监管更新对食品安全合规专家的需求持续增加。",
}
I18N_EN = {
    "locale": "en", "name": "Food Technologist",
    "summary": "Food technologists develop new food products, improve production processes and ensure food safety and regulatory compliance. Australia is a major food export nation with growing Asia-Pacific clean food exports. Plant-based food and functional food innovation drive steady demand.",
    "forecast_note": "JSA projects ~6% employment growth for food technologists by 2035. Plant-based protein food and export-oriented functional food development are the primary drivers.",
    "trend_summary": "Plant-based alternative proteins and precision fermentation are the largest investment directions in food technology in 2025-2030. FSANZ regulatory updates are driving increased demand for food safety compliance specialists.",
}
EDUCATION = [
    {"stage": "Bachelor of Food Science / Food Technology（3~4年）", "duration": "3~4年（全日制）", "cost_min": 28000, "cost_max": 165000, "cost_note": "或食品工程/营养学/化学工程相关学位；澳洲主要大学：RMIT/UQ/UoM均提供食品科学学位", "sort_order": 0},
    {"stage": "AIFST（澳洲食品科技学会）会员资格", "duration": "工作经验积累后申请", "cost_min": 200, "cost_max": 600, "cost_note": "AIFST认证会员提升行业认可度，约 $200/年会员费", "sort_order": 1},
    {"stage": "技能移民评估（VETASSESS 或 Engineers Australia）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "食品技术师通常通过VETASSESS进行技能评估；约 $650 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Food Science / Food Technology", "issuer": "认可大学", "note": "行业基础学历，AIFST会员提升行业认可度", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "AIFST Certified Member（CPD培训）", "issuer": "Australian Institute of Food Science & Technology", "note": "澳洲食品科技行业专业认可资质", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "HACCP/食品安全管理体系认证", "issuer": "各认证机构", "note": "食品生产合规岗位的重要技能证明", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须，食品技术师通常使用VETASSESS评估", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 300,  "count_max": 800,  "note": "全国，含食品技术师、食品科学家、产品开发工程师和食品安全专员岗"},
    {"platform": "Indeed",   "count_min": 200,  "count_max": 600,  "note": "含食品生产、出口贸易和初创食品企业岗"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 900,  "note": "食品企业和植物性蛋白初创公司直招"},
]
SALARIES = [
    {"experience": "初级食品技术师（0~3年）", "salary_min": 60000, "salary_max": 76000, "salary_note": "含食品质量控制和产品开发助理岗", "sort_order": 0},
    {"experience": "中级食品技术师（3~7年）", "salary_min": 75000, "salary_max": 98000, "salary_note": "SEEK 区间 $80k~$90k；Indeed 平均 $80,110（2026）", "sort_order": 1},
    {"experience": "高级/食品安全专家（7年+）", "salary_min": 95000, "salary_max": 130000, "salary_note": "含HACCP/监管合规专家和产品开发经理", "sort_order": 2},
    {"experience": "研发总监 / 技术总监（15年+）", "salary_min": 130000, "salary_max": 200000, "salary_note": "大型食品企业（雀巢澳洲/乳制品公司）研发总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，食品技术师为专业技能岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "VETASSESS评估+EOI，邀请制", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，VIC/SA/QLD食品工业中心", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区食品企业岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "食品化学、微生物和工艺技术需要系统学习，但难度低于工程类"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "3~4年本科+VETASSESS评估，周期约4~5年"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "VETASSESS评估和AIFST会员资格难度均较低"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "植物基食品和出口功能食品推动稳定增长，但职位总量较小"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "植物性蛋白专精岗较供不应求；常规食品质控岗竞争一般"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "产品开发和推出期强度较高，质量控制岗节奏稳定"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "均值约 $75k~$95k，是工程/IT类中薪资较低的职业"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "植物基食品增长驱动行业扩张，但总体增速低于IT和工程类"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助配方优化，但食品安全判断和感官测试需要人工"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "STOL列表，VETASSESS评估路径较清晰，但职位少导致等待期长"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "VETASSESS评估相对简单；189/190 EOI等待期可能较长"},
]
SUITABILITY_FIT = ["持有食品科学/食品技术/化学/生物技术相关学位", "有食品产品开发、食品安全（HACCP）或生产工艺优化实际经验", "英语能力达到 IELTS 6.0+（VETASSESS和工作环境要求）", "有植物性蛋白或功能食品研发经验（2025-2030年溢价方向）", "目标是VIC/SA/QLD食品工业中心（就业机会最集中）"]
SUITABILITY_UNFIT = ["无食品科学相关学历，无法通过VETASSESS评估", "不接受部分食品生产岗的轮班工作安排", "薪资期望很高（食品技术师整体薪资低于IT/工程类）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "食品技术师薪资 $80k~$90k（2026）", "url": "https://au.seek.com/career-advice/role/food-technologist/salary"},
    {"source_name": "Indeed AU", "content": "食品技术师平均薪资 $80,110（2026）", "url": "https://au.indeed.com/career/food-technologist/salaries"},
    {"source_name": "Australian Institute of Food Science & Technology (AIFST)", "content": "行业认证和专业发展", "url": "https://www.aifst.asn.au/"},
    {"source_name": "Department of Home Affairs", "content": "STOL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲食品技术师工资多少？", "answer": "中级约 $75,000~$98,000（Indeed均值 $80,110）；高级食品安全专家约 $95k~$130k；研发总监约 $130k~$200k。整体薪资水平低于IT和工程类职业。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲食品技术师容易找工作吗？", "answer": "中等难度。Seek 挂牌约 300~800 个职位，植物基食品和出口食品推动稳定需求，但总量较少。有HACCP食品安全经验的专业人士相对容易找到岗位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国食品科学学历澳洲认可吗？", "answer": "通过 VETASSESS 技能评估（约 $650 申请费，3~6个月周期）。中国食品科学/食品工程相关学历通常能通过VETASSESS评估，通过率较高。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "食品技术师会被AI替代吗？", "answer": "风险较低。AI辅助配方优化和成分替换建议，但食品安全评估、感官测试（品尝）、消费者测试设计和法规申报需要人工判断。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲食品技术师有年龄限制吗？", "answer": "无。有丰富产品开发和食品安全管理经验的资深技术师在大型食品企业（雀巢/帝亚吉欧）备受重视。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲食品技术师需要什么学历？", "answer": "食品科学/食品技术/化学/生物技术相关学位是主流。VETASSESS对相关学历的认可范围较广，化学工程或生物技术背景的求职者通常也能通过评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲食品技术师认证（移民）难吗？", "answer": "难度中低。VETASSESS评估相对简单，通过率高；但职位数量少导致189/190 EOI邀请等待期可能较长，建议优先考虑雇主担保482签证路径。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "食品技术师和化学工程师哪个更适合移民澳洲？", "answer": "化学工程师薪资更高（$90k~$115k vs $75k~$95k），移民路径通过EA评估更成熟，绿氢/锂矿方向薪资溢价更高；食品技术师入门门槛略低，生活方式更稳定。建议根据学历背景选择，化学背景者优先考虑化学工程师路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 食品技术师数据入库完成")

if __name__ == "__main__":
    run()
