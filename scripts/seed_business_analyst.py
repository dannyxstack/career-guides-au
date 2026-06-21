"""澳洲商业分析师（225113）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "225113", "anzsco_title": "Management Consultant",
    "category": "商业/金融/法律", "workforce_size": 72000, "shortage_listed": 1,
    "growth_areas": json.dumps(["AI & Digital Transformation Advisory","Process Automation & RPA","Government Digital Services Consulting","Healthcare Operations Improvement","ESG & Sustainability Strategy"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "商业分析师",
    "summary": "商业分析师通过分析业务流程、识别需求和提供改进方案，协助组织实现数字化转型和运营优化。澳洲联邦政府数字化项目和大型企业AI转型推动需求持续旺盛，是结合了技术和商业思维的高薪复合型职业。",
    "forecast_note": "JSA 预测管理顾问/商业分析师至2035年就业增长约12%。AI工具驱动的流程再造和政府数字服务改革是主要增长动力。",
    "trend_summary": "AI驱动的商业流程分析（AI Business Process Analysis）是2025-2026年增速最快的方向，结合了数据分析和商业策略的复合型BA薪资溢价 $20k~$30k。RPA（机器人流程自动化）专精BA需求急增。",
}
I18N_EN = {
    "locale": "en", "name": "Business Analyst",
    "summary": "Business analysts analyse business processes, identify requirements and deliver improvement solutions supporting digital transformation and operational optimisation. Federal government digital programs and enterprise AI transformation drive sustained strong demand for this high-salary hybrid technical-commercial role.",
    "forecast_note": "JSA projects ~12% employment growth for management consultants/business analysts by 2035. AI-driven process re-engineering and government digital service reform are the primary growth drivers.",
    "trend_summary": "AI-driven Business Process Analysis is the fastest-growing direction in 2025-2026. Composite BAs combining data analysis and business strategy command $20k~$30k salary premiums. RPA specialist BAs are in acute demand.",
}
EDUCATION = [
    {"stage": "Bachelor of Commerce / IT / Business（3~4年）", "duration": "3~4年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "商科、IT或工程相关学位均可；BA是跨学科职业", "sort_order": 0},
    {"stage": "CBAP（Certified Business Analysis Professional）认证", "duration": "3~6个月备考（需要7,500小时经验）", "cost_min": 1500, "cost_max": 4000, "cost_note": "CBAP考试费约 $325（IIBA会员）/ $450；持有者薪资溢价显著", "sort_order": 1},
    {"stage": "ACS 技能评估（189/190签证，IT类BA）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "IT偏向的商业分析师可通过ACS评估；商业偏向通过VETASSESS", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "CBAP（Certified Business Analysis Professional）", "issuer": "IIBA（International Institute of Business Analysis）", "note": "国际最高认可的BA认证，持有者薪资溢价显著", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "PMI-PBA（Professional in Business Analysis）", "issuer": "Project Management Institute (PMI)", "note": "PMI发布的BA认证，适合有项目管理背景的BA", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "ACS 技能评估 / VETASSESS 技能评估", "issuer": "ACS / VETASSESS", "note": "189/190签证技术移民必须，IT类BA用ACS，商业类BA用VETASSESS", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Certified SAFe Product Owner/Manager", "issuer": "Scaled Agile Inc.", "note": "Agile转型BA的核心认证，与BA角色深度融合", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 3000, "count_max": 7000, "note": "全国，含商业分析师、IT商业分析师、系统分析师和流程分析师岗"},
    {"platform": "Indeed",   "count_min": 2000, "count_max": 5000, "note": "含政府、金融和大型企业BA岗"},
    {"platform": "LinkedIn", "count_min": 4000, "count_max": 8000, "note": "企业直招和咨询公司猎头"},
]
SALARIES = [
    {"experience": "初级商业分析师（0~3年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "含毕业生和转行者，政府岗略高", "sort_order": 0},
    {"experience": "中级商业分析师（3~7年）", "salary_min": 100000, "salary_max": 130000, "salary_note": "SEEK 区间 $110k~$130k；Indeed 均值 $104,806（2026）", "sort_order": 1},
    {"experience": "高级/Lead商业分析师（7~12年，CBAP）", "salary_min": 130000, "salary_max": 165000, "salary_note": "持CBAP+Agile认证的高级BA，大型咨询公司和政府数字岗", "sort_order": 2},
    {"experience": "合同商业分析师（Day Rate）", "salary_min": 120000, "salary_max": 220000, "salary_note": "合同BA日薪 $650~$1,100（年化约 $130k~$220k）", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，商业分析师为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，ACS（IT类）或VETASSESS（商业类）评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，ACT/NSW/VIC政府数字项目多", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区政府BA岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要商业思维+分析工具+沟通能力的综合能力，没有单一高难度考试"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "3~4年学位；CBAP需要7,500小时工作经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CBAP难度中等，需要系统备考；经验要求是主要门槛"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "政府数字化和企业AI转型推动持续高需求，是政府合同岗最多的职业之一"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级岗竞争较激烈，持CBAP+Agile的高级BA供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "项目交付截止期有压力，但总体工作节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "中级 $100k~$130k；高级 $130k~$165k；合同BA年化 $130k~$220k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "AI转型项目需要大量BA；政府数字化是持续10年以上的需求来源"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助需求分析文档生成，但stakeholder访谈、业务规则挖掘和变更管理不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，ACS或VETASSESS评估路径清晰"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "评估机构选择（ACS vs VETASSESS）需要确认；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["有商业分析、IT业务分析或流程改进工作经验（2年以上）", "熟悉Agile/Scrum方法论和需求分析工具（Jira/Confluence/Visio）", "英语沟通能力强（IELTS 7.0+，stakeholder访谈和报告汇报要求）", "持有或正在备考CBAP认证", "目标是联邦政府数字项目（堪培拉/Sydney）或大型银行/咨询公司"]
SUITABILITY_UNFIT = ["无法在英语环境中主持访谈和撰写分析报告", "仅有数据技术背景（开发/数据），无业务分析和沟通经验", "不适应多stakeholder环境下的政治协调和变更管理"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "商业分析师薪资 $110k~$130k（2026）", "url": "https://au.seek.com/career-advice/role/business-analyst/salary"},
    {"source_name": "Indeed AU", "content": "商业分析师平均薪资 $104,806（2026）", "url": "https://au.indeed.com/career/business-analyst/salaries"},
    {"source_name": "ACS", "content": "IT类商业分析师技能评估", "url": "https://www.acs.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲商业分析师工资多少？", "answer": "中级商业分析师约 $100,000~$130,000（Indeed均值 $104,806；SEEK $110k~$130k）；持CBAP高级BA约 $130k~$165k；合同BA日薪 $650~$1,100，年化约 $130k~$220k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲商业分析师容易找工作吗？", "answer": "容易。Seek 挂牌约 3,000~7,000 个职位，政府数字化项目和企业AI转型推动需求持续旺盛，是合同岗最多的商业职业之一。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国商业分析经验澳洲认可吗？", "answer": "通过 ACS（IT类BA）或 VETASSESS（商业类BA）技能评估。CBAP是国际通用认证，在澳洲完全认可。工作经验证明（STAR方法描述业务改进成果）是关键。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "商业分析师会被AI替代吗？", "answer": "风险较低。AI辅助需求文档生成和流程图绘制，但stakeholder访谈、业务规则挖掘、变更管理和与高层决策者的沟通不可替代。AI转型本身就需要大量BA来协调人员和技术变化。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲商业分析师有年龄限制吗？", "answer": "无。有行业领域知识（如金融BA、医疗BA）的资深分析师（40~55岁）在市场上具有高溢价，因为他们理解业务背景的深度远超年轻技术BA。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲商业分析师需要什么学历？", "answer": "商科/IT/工程相关本科学历是主流。持有CBAP认证的无相关学历者也可通过雇主担保（482签证）入职。ACS评估对IT相关学历认可较广。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲商业分析师认证（移民）难吗？", "answer": "难度中等。评估机构选择（ACS vs VETASSESS）需要根据个人背景确认；CBAP需要7,500小时经验积累；EOI分数对有经验者友好。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "商业分析师和IT项目经理哪个更适合移民澳洲？", "answer": "两者薪资相当（$104k~$130k），就业量相似；商业分析师更偏分析和文档，英语要求略低；IT PM更偏管理和协调，英语要求更高（IELTS 7.0+）。有分析背景者选BA，有管理经验者选IT PM。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 商业分析师数据入库完成")

if __name__ == "__main__":
    run()
