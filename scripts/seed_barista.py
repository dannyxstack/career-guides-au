"""澳洲咖啡师/咖啡馆经理（431511）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "431511", "anzsco_title": "Cafe Worker",
    "category": "餐饮/酒店/旅游", "workforce_size": 95000, "shortage_listed": 0,
    "growth_areas": json.dumps(["精品咖啡师（Specialty Coffee/Q Grader）","咖啡馆经理/店长","冷萃/氮气咖啡专业技术","咖啡烘焙和咖啡豆采购","咖啡培训师（Barista Trainer）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "咖啡师/咖啡馆经理",
    "summary": "澳洲是全球最成熟的精品咖啡市场之一，墨尔本被誉为世界咖啡之都。咖啡师负责制作意式浓缩饮品，在精品咖啡馆担任技术核心角色；咖啡馆经理负责日常运营、人员和成本管理。咖啡馆经理（Cafe Manager）是MLTSSL在列的短缺职业，移民路径清晰；初级咖啡师则不在短缺清单。",
    "forecast_note": "JSA预测咖啡和餐饮服务就业至2030年基本稳定。精品咖啡市场持续增长，精品咖啡师（SCA认证/Q Grader）需求旺盛；标准连锁咖啡馆岗位增速放缓。",
    "trend_summary": "澳洲精品咖啡行业持续高端化，消费者对咖啡知识和品质要求显著提升。植物性奶制品（燕麦奶/杏仁奶）已占澳洲咖啡馆饮品点单量的30%+。有SCA（精品咖啡协会）认证的咖啡师薪资溢价约15~25%；有经验的咖啡馆经理在大城市供不应求。",
}
I18N_EN = {
    "locale": "en", "name": "Barista / Cafe Manager",
    "summary": "Australia is one of the world's most sophisticated specialty coffee markets, with Melbourne renowned as a global coffee capital. Baristas make espresso-based beverages and play the technical core role in specialty cafes; cafe managers oversee daily operations, staffing and cost management. Cafe Manager is MLTSSL-listed (short supply), providing a clear migration pathway; entry-level baristas are not on the shortage list.",
    "forecast_note": "JSA projects broadly stable coffee and food service employment through 2030. The specialty coffee market continues growing with strong demand for specialty baristas (SCA certified/Q Graders); standard chain cafe position growth is slowing.",
    "trend_summary": "Australia's specialty coffee industry continues premiumising, with consumers significantly raising their coffee knowledge and quality expectations. Plant-based milks (oat/almond) now account for over 30% of Australian cafe drink orders. SCA-certified baristas command a 15-25% salary premium; experienced cafe managers are in short supply in major cities.",
}
EDUCATION = [
    {"stage": "Certificate III in Hospitality（SIT30722，咖啡相关单元）", "duration": "6~12个月", "cost_min": 2000, "cost_max": 10000, "cost_note": "包含咖啡制作单元的酒店服务资质", "sort_order": 0},
    {"stage": "SCA（精品咖啡协会）咖啡技能认证", "duration": "各级别1~5天课程", "cost_min": 500, "cost_max": 5000, "cost_note": "SCA Coffee Skills Program：Barista Intermediate/Professional认证；全球认可", "sort_order": 1},
    {"stage": "咖啡馆经理证书（Certificate IV Hospitality + 管理经验）", "duration": "12个月+实践", "cost_min": 3000, "cost_max": 15000, "cost_note": "咖啡馆经理MLTSSL移民评估的基础资质路径", "sort_order": 2},
    {"stage": "Food Safety Supervisor + RSA证书", "duration": "1~2天", "cost_min": 150, "cost_max": 500, "cost_note": "餐饮场所法律必须", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "SCA Barista Skills（Intermediate/Professional）", "issuer": "Specialty Coffee Association", "note": "全球最具公信力的精品咖啡师认证，显著提升薪资", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Food Safety Supervisor Certificate", "issuer": "各州认可机构", "note": "所有餐饮场所从业者的法律要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "RSA（Responsible Service of Alcohol）", "issuer": "各州认可机构", "note": "提供酒精饮品的咖啡馆的法律要求", "is_mandatory": 0, "sort_order": 2},
        {"qual_name": "Vetassess 技能评估（咖啡馆经理 141111）", "issuer": "Vetassess", "note": "咖啡馆经理技术移民路径（ANZSCO 141111）必须的评估", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 4000, "note": "全国，含咖啡师/咖啡馆经理/店长/饮品吧台岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 3000, "note": "含独立精品咖啡馆和连锁咖啡品牌岗"},
    {"platform": "LinkedIn", "count_min": 500, "count_max": 1500, "note": "连锁品牌区域培训师和运营经理岗"},
]
SALARIES = [
    {"experience": "初级咖啡师（0~2年）", "salary_min": 52000, "salary_max": 64000, "salary_note": "全职咖啡师基础薪资；按小时计约 $25~$30/hr（含普通时）", "sort_order": 0},
    {"experience": "有经验咖啡师（2~5年）", "salary_min": 62000, "salary_max": 78000, "salary_note": "SEEK 咖啡师均值 $70k~$75k；Indeed 均值约 $64,979（$31.24/hr × 2080h，2026）", "sort_order": 1},
    {"experience": "咖啡馆经理 / 店长（3~8年）", "salary_min": 68000, "salary_max": 85000, "salary_note": "SEEK 咖啡馆经理均值 $70k~$80k；SCA认证资深咖啡师可超 $80k", "sort_order": 2},
    {"experience": "精品咖啡馆总监 / 区域经理（8年+）", "salary_min": 82000, "salary_max": 120000, "salary_note": "精品咖啡品牌区域经理或咖啡烘焙公司品质总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，咖啡馆经理（141111）是短缺职业，担保可行", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "咖啡馆经理（141111）MLTSSL在列，Vetassess评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，咖啡馆经理职位各州均有提名通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区咖啡馆经理加15分，需以经理身份申请", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中低", "stars": 2, "note": "咖啡技术可自学；精品咖啡SCA认证有一定学习深度"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "初级咖啡师技能约3~6个月可上岗；SCA认证约6~12个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "咖啡馆经理（141111）Vetassess评估：需要管理经验证明和食品安全资质"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "精品咖啡市场旺盛；咖啡馆经理MLTSSL在列；初级咖啡师不在短缺清单"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级咖啡师竞争一般；精品咖啡师（SCA认证）供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "早班（5am开始）、站立工作、快节奏高峰期；体力消耗中等"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "咖啡师 $62k~$78k；咖啡馆经理 $68k~$85k；整体薪资偏低"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "精品咖啡市场稳定增长；自动化咖啡机影响标准连锁市场，不影响精品市场"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "精品咖啡技艺和顾客体验抗AI；标准化咖啡机自动化影响连锁低端市场"},
    {"dimension": "pr_friendliness",          "label_zh": "中高", "stars": 4, "note": "咖啡馆经理（141111）MLTSSL在列；纯咖啡师（431511）不在短缺清单"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "以咖啡馆经理（非咖啡师）身份申请技术移民；需要管理经验和资质"},
]
SUITABILITY_FIT = ["有3年以上咖啡馆管理经验（以经理身份而非咖啡师），有意向以咖啡馆经理（ANZSCO 141111）申请技术移民", "持有SCA精品咖啡协会认证（Intermediate或以上），有精品咖啡馆工作背景", "有澳洲或国际知名咖啡品牌担保意向", "英语沟通能力达到基本运营要求", "愿意在咖啡行业密集的城市（墨尔本/悉尼/布里斯班）就业"]
SUITABILITY_UNFIT = ["无咖啡馆管理经验（仅有咖啡师技能），无法以经理身份申请技术移民", "期望通过初级咖啡师岗位获得技术移民（咖啡师431511不在MLTSSL）", "不适应早班（5am开始）和包含周末的工作时间"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "咖啡师薪资 $70k~$75k；咖啡馆经理 $70k~$80k（2026）", "url": "https://au.seek.com/career-advice/role/barista/salary"},
    {"source_name": "Indeed AU", "content": "咖啡师平均时薪 $31.24（约 $64,979/年，2026）", "url": "https://au.indeed.com/career/barista/salaries"},
    {"source_name": "SEEK AU", "content": "咖啡馆经理薪资（2026）", "url": "https://au.seek.com/career-advice/role/cafe-manager/salary"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲咖啡师/咖啡馆经理工资多少？", "answer": "有经验咖啡师约 $62,000~$78,000（SEEK $70k~$75k；Indeed约 $64,979）；咖啡馆经理约 $68,000~$85,000（SEEK $70k~$80k）；精品咖啡品牌区域经理约 $82k~$120k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲咖啡师容易找工作吗？", "answer": "容易找到工作，但竞争也相当激烈。精品咖啡师（SCA认证）供不应求；咖啡馆经理（MLTSSL在列）更容易获得签证支持。澳洲每年消费超过 16 亿杯咖啡，行业就业持续旺盛。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "咖啡师技能移民澳洲可行吗？", "answer": "初级咖啡师（431511）不在MLTSSL，直接以咖啡师身份技术移民难度大。建议以咖啡馆经理（ANZSCO 141111，MLTSSL在列）身份申请，需要至少3年管理经验。SCA精品咖啡认证可以大幅提升移民评估竞争力。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "咖啡师会被AI/自动化替代吗？", "answer": "标准连锁咖啡（麦当劳/便利店）自动化咖啡机影响低端市场；但精品咖啡馆的手工技艺、咖啡知识分享和顾客体验是自动化无法替代的核心价值。澳洲精品咖啡消费者特别推崇手工冲泡和咖啡师互动。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲咖啡师有年龄限制吗？", "answer": "无。有丰富精品咖啡知识和稳定性的中年咖啡师（35~50岁）担任培训师和经理非常受欢迎。精品咖啡馆特别重视稳定性和咖啡知识深度。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲咖啡师需要什么资质？", "answer": "纯咖啡师就业无强制学历要求；Food Safety Supervisor证书和RSA是从业法律要求。技术移民路径（咖啡馆经理141111）需要Certificate IV Hospitality+管理经验+Vetassess评估。SCA精品咖啡认证大幅提升就业竞争力和薪资。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲咖啡师认证（移民）难吗？", "answer": "以咖啡馆经理（141111）身份申请难度中等：Vetassess评估要求管理经验+食品安全证书+英语（IELTS 6.0+）。建议先通过学生签证就读Hospitality文凭，积累2~3年管理经验后以经理身份申请技术移民。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "澳洲咖啡师和餐厅经理哪个移民路径更好？", "answer": "两者都可以用ANZSCO 141111（Cafe or Restaurant Manager）申请，使用同一MLTSSL职业代码。区别在于薪资：餐厅经理通常略高（$80k~$90k vs 咖啡馆经理 $70k~$80k）。有咖啡行业背景者以咖啡馆经理路径申请；有正餐运营背景者以餐厅经理路径申请。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 咖啡师/咖啡馆经理数据入库完成")

if __name__ == "__main__":
    run()
