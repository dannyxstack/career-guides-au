"""澳洲注册会计师（221111）数据入库。数据来源：CPA Australia、SEEK、Indeed、Terratern（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "221111", "anzsco_title": "Accountant (General)",
    "category": "商业/金融/法律", "workforce_size": 220000, "shortage_listed": 1,
    "growth_areas": json.dumps(["ESG & Sustainability Reporting","AI-Augmented Financial Analysis","Forensic & Fraud Accounting","Management Accounting & CFO Advisory","SME Business Advisory Services"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "注册会计师",
    "summary": "注册会计师负责财务报告、税务申报、审计和商业咨询，是澳洲就业量最大的专业职业之一。持有CPA（注册会计师）或CA（特许会计师）资格的会计师在政府、金融和大型企业中需求持续旺盛，是技术移民友好度最高的商业类职业。",
    "forecast_note": "JSA 预测会计师至2035年就业增长约8%。ESG强制报告（ASX上市公司）和AI辅助财务分析推动对高级管理会计和CFO顾问的需求增加。",
    "trend_summary": "ESG（环境、社会、治理）可持续报告是2025-2030年最大增长方向，ASX上市公司强制IFRS可持续披露。AI会计工具（Xero AI/Intuit Assist）提升日常核账效率，但管理会计和商业咨询价值上升。",
}
I18N_EN = {
    "locale": "en", "name": "Accountant (CPA/CA)",
    "summary": "Accountants prepare financial reports, tax returns, audits and business advisory services. One of Australia's largest professional occupations with sustained demand across government, finance and large enterprise. Among the most migration-friendly business professional roles.",
    "forecast_note": "JSA projects ~8% employment growth for accountants by 2035. Mandatory ESG reporting for ASX-listed companies and AI-assisted financial analysis are driving increased demand for senior management accountants and CFO advisory.",
    "trend_summary": "ESG sustainability reporting is the biggest growth area in 2025-2030, with mandatory IFRS sustainability disclosure for ASX-listed companies. AI accounting tools raise efficiency but elevate the value of management accounting and business advisory.",
}
EDUCATION = [
    {"stage": "Bachelor of Accounting / Commerce（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "或相关商科学位+会计专业方向；国际生约 $30,000~$42,000/年", "sort_order": 0},
    {"stage": "CPA Australia 会员资格（CPA Program）", "duration": "3~4年工作经验+6门考试", "cost_min": 3000, "cost_max": 8000, "cost_note": "CPA Program约 $1,200~$1,500/门；是澳洲最广泛认可的会计职业资格", "sort_order": 1},
    {"stage": "CPA Australia / CAANZ 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 2000, "cost_note": "技术移民必须，约 $500~$800 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "CPA（Certified Practising Accountant）", "issuer": "CPA Australia", "note": "澳洲最广泛认可的会计资格，持有者薪资溢价15~25%", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "CA（Chartered Accountant）", "issuer": "Chartered Accountants ANZ (CAANZ)", "note": "与CPA并列的顶级会计资格，Big 4会计师事务所偏好CA", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPA Australia / CAANZ 技能评估", "issuer": "CPA Australia / CAANZ", "note": "189/190签证技术移民必须，是MLTSSL职业", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Tax Agent Registration（税务代理注册）", "issuer": "Tax Practitioners Board (TPB)", "note": "独立执业税务代理必须注册，需要相关学历+2年经验", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 8000, "count_max": 15000, "note": "全国，是商业类挂牌量最大的职业，含初级/中级/高级/CFO等各层级"},
    {"platform": "Indeed",   "count_min": 5000, "count_max": 10000, "note": "含政府、Big 4和中小企业会计岗"},
    {"platform": "LinkedIn", "count_min": 6000, "count_max": 12000, "note": "Big 4直招和猎头岗比例高"},
]
SALARIES = [
    {"experience": "初级/毕业生会计师（0~2年）", "salary_min": 60000, "salary_max": 78000, "salary_note": "Big 4毕业生起薪约 $58k~$65k；中小会计所略低", "sort_order": 0},
    {"experience": "中级会计师（2~5年）", "salary_min": 75000, "salary_max": 100000, "salary_note": "SEEK 区间 $80k~$95k；持CPA溢价15~25%", "sort_order": 1},
    {"experience": "高级会计师 / CPA（5~10年）", "salary_min": 100000, "salary_max": 140000, "salary_note": "Indeed CPA平均 $121,271；ERI Senior $150,510（2026）", "sort_order": 2},
    {"experience": "财务经理 / CFO（10年+）", "salary_min": 140000, "salary_max": 280000, "salary_note": "企业CFO和Big 4合伙人路径，含奖金和分红", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，会计师为核心短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列，CPA/CAANZ评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，各州均有通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区会计岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "财务和税务知识需要系统学习，CPA考试需要备考"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "3年学位+CPA资格约3~4年=总周期约6~7年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CPA 6门考试难度中等，通过率约60~70%；持续学习要求（CPD）"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "220,000从业人数，是澳洲就业量最大的专业职业之一"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级岗竞争较激烈，持CPA的高级会计师和CFO路径供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "年末报税季和审计季强度高（3~5月），Big 4工时更长"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级 $75k~$100k；CPA高级 $100k~$140k；CFO $140k~$280k"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "ESG强制报告+AI工具推高对高级管理会计和商业顾问的需求"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "基础核账和报税受AI工具冲击，但管理决策和税务规划不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，CPA/CAANZ评估路径成熟，是最成熟的商业类移民职业"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "CPA/CAANZ评估和EOI分数是门槛，总体路径清晰"},
]
SUITABILITY_FIT = ["持有会计/商科相关学位，有2年以上会计工作经验", "正在备考或已持有CPA/CA资格", "英语能力达到 IELTS 6.5+（专业报告和客户沟通要求）", "有税务、管理会计或Big 4审计背景（薪资潜力最高）", "目标是Big 4（PwC/Deloitte/EY/KPMG）或大型金融机构"]
SUITABILITY_UNFIT = ["非会计/商科学历，无法通过CPA/CAANZ评估", "英语能力较弱，无法撰写英语财务报告", "不愿意持续参加CPD继续教育（CPA会员必须）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "会计师薪资区间 $80k~$95k（2026）", "url": "https://au.seek.com/career-advice/role/accountant/salary"},
    {"source_name": "Indeed AU", "content": "CPA注册会计师平均薪资 $122,439（2026）", "url": "https://au.indeed.com/career/certified-public-accountant/salaries"},
    {"source_name": "Terratern 2026", "content": "澳洲会计师薪资趋势分析", "url": "https://terratern.com/blog/accountant-salary-australia/"},
    {"source_name": "CPA Australia", "content": "CPA资格考试和会员信息", "url": "https://www.cpaaustralia.com.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲注册会计师工资多少？", "answer": "中级会计师约 $75,000~$100,000（SEEK $80k~$95k）；持CPA高级会计师约 $100k~$140k（Indeed均值 $122,439）；财务经理/CFO约 $140k~$280k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲注册会计师容易找工作吗？", "answer": "容易。Seek 挂牌约 8,000~15,000 个职位，是商业类挂牌量最大的职业，各行各业均有需求。持CPA的高级会计师和CFO路径供不应求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国会计学历澳洲认可吗？", "answer": "通过 CPA Australia 或 CAANZ 技能评估（约 $500~$800 申请费）。中国会计/商科学历通常能通过评估，但需要提供成绩单和课程大纲。持中国注册会计师（CPA China）资格者可部分豁免CPA Australia考试科目。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "会计师会被AI替代吗？", "answer": "基础核账、数据录入和标准报表生成受AI工具（Xero AI/Intuit）冲击；但管理决策支持、税务规划和ESG报告等高价值业务不可替代。建议向管理会计/商业顾问方向发展。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲注册会计师有年龄限制吗？", "answer": "无。资深CFO和财务总监（40~55岁）在上市公司和大型企业中备受重视。移民打分45岁以上无加分，建议35~42岁尽快申请。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲注册会计师需要什么学历？", "answer": "会计/商科相关本科学历是CPA/CAANZ评估的基本要求。中国会计学、财务管理、金融等相关学历通常可以通过评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲会计师认证（移民）难吗？", "answer": "难度中等，是商业类移民路径最成熟的职业之一。CPA/CAANZ评估和EOI分数是主要门槛；CPA考试需要时间准备但结构清晰。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "会计师和金融分析师哪个更适合移民澳洲？", "answer": "会计师就业量更大（Seek ~10000 vs 金融分析师 ~2000），移民路径更成熟；金融分析师薪资更高（SEEK $100k~$120k vs 会计师 $80k~$95k），但竞争更激烈（需要金融专业背景）。有会计背景者首选会计师，有金融/投资背景者可考虑金融分析师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 注册会计师数据入库完成")

if __name__ == "__main__":
    run()
