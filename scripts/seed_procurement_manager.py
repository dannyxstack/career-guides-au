"""澳洲采购经理（133612）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "133612", "anzsco_title": "Procurement Manager",
    "category": "商业/金融/法律", "workforce_size": 35000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Government Procurement & Commonwealth Contracts","ESG & Ethical Sourcing","Technology Category Management (SaaS/Cloud)","Defence & Critical Infrastructure Procurement","Indirect Spend Optimisation"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "采购经理",
    "summary": "采购经理负责采购战略制定、供应商评估与谈判、合同管理和类别管理，确保组织以最佳价格获取所需商品和服务。澳洲联邦和州政府采购支出庞大（每年约 $700 亿）是稳定的就业来源，政府采购专精人才供不应求，是商业类薪资较高的管理职业之一。",
    "forecast_note": "JSA预测采购经理至2035年就业增长约9%。政府基础设施投资（国防/NDIS/交通）和ESG强制采购合规是2025-2030年增长最快的方向。",
    "trend_summary": "政府采购（Government Procurement）是澳洲采购经理薪资最高的细分方向，联邦政府AusTender合规专精人才供不应求。ESG采购（道德供应链+碳足迹追踪）是各大ASX上市公司强制推行的新增合规要求。",
}
I18N_EN = {
    "locale": "en", "name": "Procurement Manager",
    "summary": "Procurement managers develop sourcing strategies, evaluate and negotiate with suppliers, manage contracts and category management to ensure organisations acquire goods and services at best value. Australia's large federal and state government procurement spend (~$70B/year) provides a stable employment base, with government procurement specialists in acute demand.",
    "forecast_note": "JSA projects ~9% employment growth for procurement managers by 2035. Government infrastructure investment (Defence/NDIS/Transport) and mandatory ESG procurement compliance are the fastest-growing directions.",
    "trend_summary": "Government procurement is the highest-salary specialisation for Australian procurement managers, with federal AusTender compliance specialists in acute demand. ESG procurement (ethical supply chain + carbon tracking) is a new mandatory compliance requirement for ASX-listed companies.",
}
EDUCATION = [
    {"stage": "Bachelor of Business / Commerce / Supply Chain（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "商科/供应链/法律相关学位均可入行", "sort_order": 0},
    {"stage": "MCIPS（Chartered Institute of Procurement & Supply）", "duration": "2~3年备考（MCIPS Level 4~6）", "cost_min": 3000, "cost_max": 10000, "cost_note": "全球最高认可的采购专业认证；Level 4考试费约 $300~$400/门", "sort_order": 1},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须，约 $650 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "MCIPS（Member of Chartered Institute of Procurement & Supply）", "issuer": "CIPS（英国采购与供应特许学会）", "note": "全球最高认可的采购认证，持有者薪资溢价约15~25%", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "FCIPS（Fellow）/ ACIPS（Associate）", "issuer": "CIPS", "note": "CIPS的进阶认证，Fellow级别是行业最高资质", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "AusTender合规培训", "issuer": "Department of Finance（澳洲联邦财政部）", "note": "政府采购专精必须了解AusTender流程和公共治理框架", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1000, "count_max": 3000, "note": "全国，含采购经理、类别经理、合同经理和商业总监岗"},
    {"platform": "Indeed",   "count_min": 800, "count_max": 2500, "note": "含政府、国防、基础设施和大型企业采购岗"},
    {"platform": "LinkedIn", "count_min": 1500, "count_max": 4000, "note": "政府机构直招和猎头，SaaS/Tech采购专精岗"},
]
SALARIES = [
    {"experience": "采购专员 / 合同专员（0~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "政府采购入门岗起薪相对较高", "sort_order": 0},
    {"experience": "采购经理 / 类别经理（3~8年）", "salary_min": 110000, "salary_max": 155000, "salary_note": "SEEK 区间 $140k~$160k；Indeed 均值 $115,116；Glassdoor 均值 $147,000（2026）", "sort_order": 1},
    {"experience": "高级采购经理 / 商业总监（8~15年）", "salary_min": 155000, "salary_max": 230000, "salary_note": "政府高级采购官或大型企业商业总监，含绩效奖金", "sort_order": 2},
    {"experience": "CPO（Chief Procurement Officer，15年+）", "salary_min": 230000, "salary_max": 500000, "salary_note": "大型企业首席采购官，含股权激励", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，采购经理为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，VETASSESS评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，ACT（堪培拉联邦政府集中）通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区政府采购岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要谈判技巧+合同法律知识+数据分析能力，综合要求较高"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "3年学位+MCIPS认证约2~3年；总周期约5~6年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CIPS Level 4~6难度中等，需要系统学习采购理论和实践"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL短缺职业，政府基础设施投资和ESG合规推动需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "高级采购经理（特别是政府采购和ESG采购专精）供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "采购截止期和供应商谈判期有压力，政府岗工作节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "采购经理 $110k~$155k（Glassdoor均值 $147k），是商业类薪资最高的管理职业之一"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "政府基础设施投资+国防供应链+ESG采购是未来10年的增长引擎"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助供应商分析和合同审查，但谈判策略、风险判断和关系管理不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，VETASSESS评估路径清晰；政府担保482通道顺畅"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "VETASSESS评估对商科/供应链学历友好；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["持有商科/供应链/法律相关学位，有3年以上采购或合同管理经验", "熟悉采购流程、RFT/RFQ文件撰写和合同谈判", "英语能力达到 IELTS 7.0+（政府采购文件和合同撰写要求高）", "持有或正在备考MCIPS认证（全球最高采购认证）", "目标是联邦/州政府采购岗（堪培拉/各州首府）或大型企业CPO路径"]
SUITABILITY_UNFIT = ["无采购、合同或供应链管理工作经验", "英语书面能力较弱，无法撰写英语采购规格说明书和合同文件", "不适应多利益相关方的谈判和合规审查环境"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "采购经理薪资 $140k~$160k（2026）", "url": "https://au.seek.com/career-advice/role/procurement-manager/salary"},
    {"source_name": "Indeed AU", "content": "采购经理平均薪资 $115,116（2026）", "url": "https://au.indeed.com/career/procurement-manager/salaries"},
    {"source_name": "Glassdoor AU", "content": "采购经理平均薪资 $147,000（2026）", "url": "https://www.glassdoor.com.au/Salaries/procurement-manager-salary-SRCH_KO0,19.htm"},
    {"source_name": "CIPS", "content": "MCIPS认证信息", "url": "https://www.cips.org/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲采购经理工资多少？", "answer": "采购经理约 $110,000~$155,000（Glassdoor均值 $147,000；SEEK $140k~$160k；Indeed $115,116）；高级商业总监约 $155k~$230k；首席采购官（CPO）可超 $230k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲采购经理容易找工作吗？", "answer": "容易。Seek 挂牌约 1,000~3,000 个职位，MLTSSL短缺职业。政府基础设施投资和ESG采购合规持续推动需求，高级政府采购专精人才极度短缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国采购经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国大型企业或政府机构采购经验可以认可。MCIPS是国际通用认证，在澳洲完全认可。建议强调可量化的采购节省成果（cost savings）和合同管理经验。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "采购经理会被AI替代吗？", "answer": "风险较低。AI辅助供应商分析、合同条款审查和价格基准比对，但战略采购决策、供应商关系管理、复杂谈判和合规风险判断需要深度专业判断，不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲采购经理有年龄限制吗？", "answer": "无。资深采购总监（40~55岁）在政府和大型企业中备受重视，特别是有重大政府合同谈判经验和行业专精（国防/医疗/基础设施）者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲采购经理需要什么学历？", "answer": "商科/供应链/法律相关本科学历是VETASSESS评估基础。MCIPS认证可显著弥补学历差异。政府采购岗通常对MCIPS持有者有明显偏好。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲采购经理认证（移民）难吗？", "answer": "难度中等。VETASSESS评估路径清晰；MCIPS考试难度中等，通过率较高。雇主担保482是快速路径，政府机构（ATO/ASD/Defence）常对高级采购专家提供担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "采购经理和供应链经理哪个更适合移民澳洲？", "answer": "采购经理薪资更高（Glassdoor $147k vs 供应链经理 $106k），政府机会更多；供应链经理职位总量更大、行业覆盖更广、SAP技术背景有优势。有强专项采购谈判经验者选采购经理，有全链条运营经验者选供应链经理。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 采购经理数据入库完成")

if __name__ == "__main__":
    run()
