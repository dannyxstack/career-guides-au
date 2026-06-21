"""澳洲税务顾问（221113）数据入库。数据来源：JSA、SEEK、Indeed、ERI（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "221113", "anzsco_title": "Tax Accountant",
    "category": "商业/金融/法律", "workforce_size": 55000, "shortage_listed": 1,
    "growth_areas": json.dumps(["International Tax & Transfer Pricing","Crypto & Digital Asset Tax","GST & Indirect Tax","R&D Tax Incentive Consulting","ESG Tax & Carbon Credit Advisory"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "税务顾问",
    "summary": "税务顾问（税务会计师）为个人和企业提供税务规划、申报和合规服务，专精于澳洲联邦税务局（ATO）法规、GST、公司税和国际税务。澳洲复杂的税务法规体系和持续变化的税收政策确保税务专家的长期需求，是会计类别中独立执业路径最成熟的细分方向。",
    "forecast_note": "JSA预测税务顾问至2035年就业增长约7%。数字经济税务（加密货币、NFT、跨境电商）和ESG碳税顾问是2025-2030年增长最快的新兴方向。",
    "trend_summary": "ATO加强对加密货币资本利得征税和外籍人士跨境税务的监管，推动对数字资产税务顾问的急迫需求。研发税收激励（R&D Tax Incentive）专精顾问是薪资溢价最高方向之一。",
}
I18N_EN = {
    "locale": "en", "name": "Tax Consultant / Tax Accountant",
    "summary": "Tax consultants provide tax planning, lodgement and compliance services to individuals and businesses, specialising in ATO regulations, GST, corporate tax and international tax. Australia's complex and evolving tax legislation ensures sustained long-term demand for tax specialists, with the most mature independent practice pathway in the accounting sector.",
    "forecast_note": "JSA projects ~7% employment growth for tax accountants by 2035. Digital economy tax (crypto, NFTs, cross-border e-commerce) and ESG carbon credit advisory are the fastest-growing emerging directions in 2025-2030.",
    "trend_summary": "ATO's intensified enforcement of cryptocurrency CGT and cross-border expat tax drives urgent demand for digital asset tax advisers. R&D Tax Incentive specialists are one of the highest-premium specialisations.",
}
EDUCATION = [
    {"stage": "Bachelor of Accounting / Commerce（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "会计/商科相关学位是基础", "sort_order": 0},
    {"stage": "CPA Australia / CA（税务专项模块）", "duration": "3~4年+税务专项考试", "cost_min": 3000, "cost_max": 8000, "cost_note": "税务顾问通常持有CPA或CA资格；CPA税务专项是独立税务实践的重要资格", "sort_order": 1},
    {"stage": "Tax Agent Registration（税务代理注册）", "duration": "1~3个月申请流程", "cost_min": 300, "cost_max": 1000, "cost_note": "独立执业税务代理必须向TPB（Tax Practitioners Board）注册，需要相关学历+2年税务经验", "sort_order": 2},
    {"stage": "CPA Australia / CAANZ 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 2000, "cost_note": "技术移民必须，约 $500~$800 申请费", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "CPA（Certified Practising Accountant）/ CA", "issuer": "CPA Australia / CAANZ", "note": "税务顾问的主流专业资格，持有者薪资溢价显著", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Tax Agent Registration（注册税务代理）", "issuer": "Tax Practitioners Board (TPB)", "note": "独立执业税务代理法律必须；是自雇税务顾问的关键执照", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "BAS Agent Registration（GST/BAS代理）", "issuer": "Tax Practitioners Board (TPB)", "note": "GST和BAS申报服务提供者必须注册，是税务助理入门资格", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "CPA Australia / CAANZ 技能评估", "issuer": "CPA Australia / CAANZ", "note": "189/190签证技术移民必须，MLTSSL在列", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 5000, "note": "全国，含税务顾问、税务会计师、国际税务经理和转让定价分析师岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 4000, "note": "含Big 4、中型会计所和中小企业税务岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 5000, "note": "Big 4税务部门和跨国公司内部税务团队"},
]
SALARIES = [
    {"experience": "初级税务会计师（0~3年）", "salary_min": 60000, "salary_max": 80000, "salary_note": "税务助理和初级税务顾问", "sort_order": 0},
    {"experience": "中级税务顾问（3~7年）", "salary_min": 78000, "salary_max": 105000, "salary_note": "SEEK 区间 $80k~$100k；Indeed 均值 $82,415（2026）", "sort_order": 1},
    {"experience": "高级/专精税务顾问（7~12年）", "salary_min": 105000, "salary_max": 160000, "salary_note": "国际税务/R&D税务/转让定价专精，ERI senior $150k+", "sort_order": 2},
    {"experience": "税务合伙人 / 税务总监（12年+）", "salary_min": 160000, "salary_max": 350000, "salary_note": "Big 4税务合伙人或大型企业集团税务总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，税务顾问为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，CPA/CAANZ评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区税务岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "澳洲税法体系复杂，国际税务和转让定价需要深度专业知识"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "3年学位+CPA/CA资格约3~4年=总周期约6~7年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CPA考试难度中等；Tax Agent注册要求2年经验"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL短缺职业，各企业和会计所持续招聘税务专精人才"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级税务岗竞争较激烈；国际税务/R&D税务/数字资产税务专精者供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "报税截止期（10月/4月）强度高；大型企业税务合规常年繁忙"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级 $78k~$105k；专精方向 $105k~$160k；合伙人 $160k+"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "数字经济税务和ESG碳税顾问是20年以上的增长方向"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "标准税务申报受AI（Xero Tax/ATO prefill）冲击，但税务规划和复杂企业税务不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，CPA/CAANZ评估路径成熟，与会计师路径等同"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "评估和EOI路径清晰，雇主担保482是快速路径"},
]
SUITABILITY_FIT = ["持有会计/商科相关学位，有2年以上税务工作经验", "正在备考或已持有CPA/CA资格，了解ATO税法体系", "英语能力达到 IELTS 6.5+", "有国际税务、转让定价、R&D税收激励或数字资产税务专长（溢价最高）", "目标是Big 4税务部门或独立执业税务代理（自雇路径）"]
SUITABILITY_UNFIT = ["无会计/商科相关学历，无法通过CPA/CAANZ评估", "不适应高精度、规则密集的税务合规工作性质", "对澳洲税法体系缺乏学习意愿（持续变化的税法需要CPD学习）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "税务顾问薪资 $80k~$100k（2026）", "url": "https://au.seek.com/career-advice/role/tax-accountant/salary"},
    {"source_name": "Indeed AU", "content": "税务顾问平均薪资 $82,415（2026）", "url": "https://au.indeed.com/career/tax-accountant/salaries"},
    {"source_name": "Tax Practitioners Board", "content": "税务代理注册和资格要求", "url": "https://www.tpb.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲税务顾问工资多少？", "answer": "中级税务顾问约 $78,000~$105,000（Indeed均值 $82,415；SEEK $80k~$100k）；国际税务/专精顾问约 $105k~$160k；Big 4税务合伙人约 $160k~$350k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲税务顾问容易找工作吗？", "answer": "容易。Seek 挂牌约 2,000~5,000 个职位，MLTSSL短缺职业。数字资产税务（加密货币/NFT）和R&D税收激励专精顾问目前供不应求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国税务经验澳洲认可吗？", "answer": "通过CPA Australia或CAANZ技能评估，中国税务会计经验可以认可。澳洲税法与中国税法体系差异较大，建议同时自学ATO税法知识，特别是GST、FBT和PAYG体系。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "税务顾问会被AI替代吗？", "answer": "风险较低。标准税务申报（个人所得税）受ATO预填系统和AI工具影响；但企业税务规划、国际税务架构、R&D税收激励和税务争议处理需要深度专业判断，不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲税务顾问有年龄限制吗？", "answer": "无。资深税务顾问（40~55岁）凭借深厚的税务实践经验，特别是国际税务和复杂企业税务，在市场上备受重视，收入通常高于年轻同行。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲税务顾问需要什么学历？", "answer": "会计/商科相关本科学历是CPA/CAANZ评估基础。独立执业税务代理还需要TPB注册（需要2年税务经验）。持中国税务师（CTA）资格者可部分豁免CPA考试科目。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲税务顾问认证（移民）难吗？", "answer": "难度中等，是商业类移民路径最成熟的职业之一（同会计师）。CPA/CAANZ评估路径清晰；雇主担保482是快速路径，Big 4税务部门常对海外税务专家提供担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "税务顾问和普通会计师哪个更适合移民澳洲？", "answer": "两者移民路径相同（MLTSSL+CPA/CAANZ评估）；税务顾问有更清晰的独立执业路径（Tax Agent注册后可自雇），薪资溢价在专精方向更明显（$105k~$160k vs 会计师 $80k~$100k）。有税务工作经验者强烈建议走税务顾问路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 税务顾问数据入库完成")

if __name__ == "__main__":
    run()
