"""澳洲金融分析师（222299）数据入库。数据来源：JSA、SEEK、Indeed、Hays（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "222299", "anzsco_title": "Financial Investment Advisers and Managers nec",
    "category": "商业/金融/法律", "workforce_size": 65000, "shortage_listed": 0,
    "growth_areas": json.dumps(["ESG & Sustainable Investment Analysis","Quantitative & Algorithmic Trading","Investment Banking M&A Advisory","Private Equity & Venture Capital","APRA Regulatory Compliance Analytics"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "金融分析师",
    "summary": "金融分析师评估投资机会、分析财务数据并为投资决策提供专业建议，覆盖证券、基金、银行、保险和企业财务。悉尼作为亚太金融中心的地位使金融分析师薪资持续领跑商业类职业，是高薪资潜力最强的商业职业之一。",
    "forecast_note": "JSA 预测金融分析师至2035年就业增长约7%。ESG强制报告和机构投资者的可持续投资需求推动对ESG金融分析师的需求急剧增加。",
    "trend_summary": "ESG投资（环境、社会、治理）是2025-2030年增长最快的分析方向，全球ESG资产预计超过US$50万亿。定量分析师（Quant）和AI增强的数据驱动投资分析是薪资溢价最高的专精方向。",
}
I18N_EN = {
    "locale": "en", "name": "Financial Analyst",
    "summary": "Financial analysts evaluate investment opportunities, analyse financial data and provide advisory for investment decisions across securities, funds, banking, insurance and corporate finance. Sydney's Asia-Pacific financial hub status supports sustained premium salaries — among the highest in the business sector.",
    "forecast_note": "JSA projects ~7% employment growth for financial analysts by 2035. Mandatory ESG reporting and institutional investor sustainable investment demand are driving acute need for ESG financial analysts.",
    "trend_summary": "ESG investing is the fastest-growing analysis direction in 2025-2030 with global ESG assets projected to exceed US$50T. Quantitative analysts and AI-enhanced data-driven investment analysis command the highest salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of Finance / Commerce / Economics（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "金融/经济/商科相关学位是行业入门基础", "sort_order": 0},
    {"stage": "CFA（特许金融分析师）", "duration": "2~4年，3级考试（Level I/II/III）", "cost_min": 3000, "cost_max": 8000, "cost_note": "CFA Level I 考试费约 $700~$1,300；是金融分析师的黄金认证，溢价显著", "sort_order": 1},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "金融分析师技术移民通常使用VETASSESS评估，约 $650 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "CFA（Chartered Financial Analyst）", "issuer": "CFA Institute", "note": "全球最高认可的投资分析资格，持有者薪资溢价约20~35%", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "FRM（Financial Risk Manager）", "issuer": "GARP", "note": "风险管理专精认证，银行和金融机构风险分析师重要资质", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CFP（Certified Financial Planner）", "issuer": "FPA Australia", "note": "个人理财规划师认证，RG146合规要求", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 4000, "note": "全国，含金融分析师、投资分析师、研究分析师和M&A顾问岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 2500, "note": "含银行、基金公司和企业财务岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 5000, "note": "投资银行和大型金融机构直招，猎头活跃"},
]
SALARIES = [
    {"experience": "初级/毕业生金融分析师（0~3年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "大型银行和基金公司毕业生起薪", "sort_order": 0},
    {"experience": "中级金融分析师（3~7年）", "salary_min": 95000, "salary_max": 135000, "salary_note": "SEEK 区间 $100k~$120k；Indeed 平均 $116,458；Hays $95k~$115k（2026）", "sort_order": 1},
    {"experience": "高级/CFA持有金融分析师（7~12年）", "salary_min": 135000, "salary_max": 200000, "salary_note": "CFA持有者和ESG专精分析师，含年终奖金", "sort_order": 2},
    {"experience": "投资银行家 / 基金经理（10年+）", "salary_min": 200000, "salary_max": 500000, "salary_note": "投资银行家含奖金总薪酬可超 $300k；基金经理含业绩分成", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，金融机构常直接担保优质候选人", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，VETASSESS技能评估+EOI", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NSW（悉尼金融中心）通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "很高", "stars": 4, "note": "需要扎实的财务建模、估值和量化分析能力；CFA考试难度高"},
    {"dimension": "learning_duration",        "label_zh": "很长", "stars": 4, "note": "3年学位+CFA 3级（通常需要3~4年）=总周期约6~7年"},
    {"dimension": "certification_difficulty", "label_zh": "很高", "stars": 4, "note": "CFA通过率仅约40~45%（Level I~III累计），是最难的金融认证之一"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "悉尼作为亚太金融中心，总量虽不及IT但薪资竞争力强"},
    {"dimension": "competition",              "label_zh": "中高", "stars": 4, "note": "顶尖投行岗竞争极激烈；ESG和量化分析专精岗供不应求"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "投行文化工作强度高（60~80小时/周），基金公司相对合理"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "是商业类薪资最高的职业之一；投行+奖金总薪可超 $300k~$500k"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "ESG投资+量化分析是20年以上的增长趋势"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "基础财务建模受AI影响，但投资判断、客户关系和复杂结构设计不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "VETASSESS评估路径可行，但职位数少于会计类，竞争分数高"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "VETASSESS评估对金融学历要求较严，EOI等待期可能较长"},
]
SUITABILITY_FIT = ["持有金融/经济/商科相关学位，有金融机构工作经验", "正在备考或已持有CFA/FRM认证", "英语能力达到 IELTS 7.0+（投行报告和路演要求高）", "有ESG/可持续投资、量化分析或M&A经验（薪资溢价最高）", "目标是悉尼（全澳最集中的金融机构）或大型投行/基金公司"]
SUITABILITY_UNFIT = ["仅有普通会计背景，无金融投资分析经验", "英语水平偏弱，无法撰写英语投资研究报告", "不接受高强度工作文化（特别是投行方向）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "金融分析师薪资 $100k~$120k（2026）", "url": "https://au.seek.com/career-advice/role/financial-analyst/salary"},
    {"source_name": "Indeed AU", "content": "金融分析师平均薪资 $116,458（2026）", "url": "https://au.indeed.com/career/financial-analyst/salaries"},
    {"source_name": "Hays AU", "content": "金融分析师薪资 $95k~$115k（2026）", "url": "https://www.hays.com.au/jobs/accountancy-finance/financial-analyst-jobs-australia/salary"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲金融分析师工资多少？", "answer": "中级金融分析师约 $95,000~$135,000（Indeed均值 $116,458；SEEK $100k~$120k）；持CFA高级分析师约 $135k~$200k；投资银行家含奖金总薪可超 $300k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲金融分析师容易找工作吗？", "answer": "中等难度。Seek 挂牌约 1500~4000 个职位，ESG分析师和量化分析师供不应求，但传统股票研究岗位竞争较激烈。悉尼集中了全澳约70%的金融分析岗。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国金融分析经验澳洲认可吗？", "answer": "CFA是国际通用认证，在澳洲完全认可。VETASSESS技能评估对金融学历认可度较高。有中国内资/合资金融机构工作经验者需要证明与澳洲市场的技能对应性。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "金融分析师会被AI替代吗？", "answer": "基础财务建模和数据整合受AI工具影响，但投资判断、客户关系、复杂交易结构和监管合规解读不可替代。量化分析师（管理AI模型）的需求反而增加。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲金融分析师有年龄限制吗？", "answer": "无。经验丰富的资深分析师和基金经理（40~55岁）在市场上具有高溢价，特别是拥有明星投资记录者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲金融分析师需要什么学历？", "answer": "金融/经济/商科相关本科学历是基础；顶级投行通常偏好名校金融/经济硕士（Master of Finance）。CFA持有者可弥补学历不足。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲金融分析师认证（移民）难吗？", "answer": "难度较高。CFA考试整体通过率仅约15%（3级均通过），VETASSESS评估对金融学历要求严格，EOI等待期可能较长。建议先持有CFA Level I+再申请。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "金融分析师和注册会计师哪个更适合移民澳洲？", "answer": "会计师就业量更大、移民路径更成熟（MLTSSL+CPA/CAANZ评估）；金融分析师薪资潜力更高（$116k~$200k+ vs $80k~$140k），但竞争更激烈。有会计背景者首选会计师路径，有金融投资背景者可选金融分析师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 金融分析师数据入库完成")

if __name__ == "__main__":
    run()
