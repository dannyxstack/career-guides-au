"""澳洲人力资源经理（223111）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor、Robert Half（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "223111", "anzsco_title": "Human Resource Manager",
    "category": "商业/金融/法律", "workforce_size": 75000, "shortage_listed": 1,
    "growth_areas": json.dumps(["HR Technology & People Analytics","Diversity, Equity & Inclusion (DEI)","Remote Work & Hybrid Workforce Management","Mental Health & Employee Wellbeing","AI-Augmented Talent Acquisition"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "人力资源经理",
    "summary": "人力资源经理负责招聘、员工关系、薪酬绩效、组织发展和劳动法合规，是各行各业都需要的管理职能。澳洲劳动法（Fair Work Act）的复杂性和企业对员工体验的日益重视推动HR专业人士的持续需求，特别是具备HR Tech（人事技术）能力的复合型HR经理薪资溢价显著。",
    "forecast_note": "JSA预测人力资源经理至2035年就业增长约9%。AI辅助招聘（ATS/人才分析）和DEI（多元、平等与包容）是2025-2030年增长最快的HR专业方向。",
    "trend_summary": "People Analytics（员工数据分析）和HR Technology（人事管理系统：Workday/SAP SuccessFactors）是2025年HR专业人士最紧缺的技能。精通HR Tech的人力资源经理薪资溢价约 $20k~$30k。",
}
I18N_EN = {
    "locale": "en", "name": "Human Resources Manager",
    "summary": "HR managers oversee recruitment, employee relations, compensation and performance management, organisational development and Fair Work compliance across all industries. The complexity of Australia's Fair Work Act and growing emphasis on employee experience drive sustained demand, with HR Tech-capable HR managers commanding significant salary premiums.",
    "forecast_note": "JSA projects ~9% employment growth for HR managers by 2035. AI-assisted recruitment (ATS/people analytics) and DEI are the fastest-growing HR professional directions in 2025-2030.",
    "trend_summary": "People Analytics and HR Technology (Workday/SAP SuccessFactors) are the most urgently needed HR skills in 2025. HR managers proficient in HR Tech command $20k~$30k salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of HR Management / Business / Psychology（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "HR/商科/心理学相关学位均可入行", "sort_order": 0},
    {"stage": "AHRI（澳洲人力资源学会）认证", "duration": "1~2年积累+考试", "cost_min": 1500, "cost_max": 4000, "cost_note": "AHRI Practising Certification考试，含CPHR（Certified Practitioner in HR）认证", "sort_order": 1},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须，约 $650 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "CPHR（Certified Practitioner in HR）", "issuer": "AHRI（Australian HR Institute）", "note": "澳洲最广泛认可的HR专业认证，持有者薪资溢价显著", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "SHRM-CP / SHRM-SCP", "issuer": "SHRM（美国）", "note": "国际HR认证，在澳洲也有一定认可度", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Workday / SAP SuccessFactors 认证", "issuer": "Workday / SAP", "note": "HR Tech认证，是HR经理薪资溢价最高的技术资格", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 5000, "note": "全国，含HR经理、HR Business Partner、招聘经理和薪酬分析师岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 4000, "note": "含政府、医疗、金融和大型企业HR岗"},
    {"platform": "LinkedIn", "count_min": 3000, "count_max": 7000, "note": "企业直招，HR猎头活跃"},
]
SALARIES = [
    {"experience": "HR专员 / HR Coordinator（0~3年）", "salary_min": 60000, "salary_max": 80000, "salary_note": "HR入门岗位起薪", "sort_order": 0},
    {"experience": "HR Business Partner / HR经理（3~8年）", "salary_min": 95000, "salary_max": 135000, "salary_note": "PayScale 均值 $102,297；Robert Half 均值 $118,000（2026）", "sort_order": 1},
    {"experience": "高级HR经理 / 悉尼（5~10年）", "salary_min": 120000, "salary_max": 160000, "salary_note": "Glassdoor 悉尼均值 $145,000（2026）", "sort_order": 2},
    {"experience": "HR Director / CHRO（10年+）", "salary_min": 160000, "salary_max": 350000, "salary_note": "大型企业Chief HR Officer，含奖金和股权激励", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，HR经理为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，VETASSESS评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NSW/VIC大型企业集中", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区政府HR岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要劳动法知识+人际管理能力，无高难度技术考试"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "3年学位+CPHR认证约1~2年；总周期约4~5年"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "CPHR难度较低；HR Tech认证（Workday/SAP）需要实操积累"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL短缺职业；所有行业均需要HR经理，就业稳定性高"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级HR岗竞争较激烈，持CPHR+HR Tech能力的HR经理供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "总体工作节奏合理，但员工关系纠纷和裁员期压力较高"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "HR BPHR经理 $95k~$135k；悉尼高级HR $120k~$160k；CHRO $160k+"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "People Analytics和AI辅助HR是10年以上的增长方向，需要复合型HR经理"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助简历筛选和薪酬分析，但员工关系、文化建设和复杂谈判不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，VETASSESS评估路径清晰，雇主担保482活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "VETASSESS评估对商科/HR学历友好；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["持有HR/商科/心理学相关学位，有3年以上HR工作经验", "熟悉澳洲Fair Work Act或有意深入学习劳动法", "英语沟通能力强（IELTS 7.0+，员工关系和管理沟通要求高）", "持有或正在备考CPHR认证，或具备Workday/SAP SuccessFactors技能", "目标是大型企业或政府的HRBP/HR经理岗位"]
SUITABILITY_UNFIT = ["英语沟通能力较弱，无法处理复杂员工关系和劳动纠纷", "不适应高度人际互动和内部政治协调的工作环境", "对澳洲劳动法缺乏学习意愿（Fair Work合规是HR经理的核心职责）"]
SOURCES = [
    {"source_name": "PayScale AU", "content": "人力资源经理平均薪资 $102,297（2026）", "url": "https://www.payscale.com/research/AU/Job=Human_Resources_(HR)_Manager/Salary"},
    {"source_name": "Robert Half AU", "content": "人力资源经理薪资均值 $118,000（2026）", "url": "https://www.roberthalf.com.au/insights/salary-guides"},
    {"source_name": "Glassdoor AU", "content": "悉尼人力资源经理平均薪资 $145,000（2026）", "url": "https://www.glassdoor.com.au/Salaries/sydney-human-resources-manager-salary-SRCH_IL.0,6_IM1226_KO7,30.htm"},
    {"source_name": "AHRI", "content": "澳洲人力资源学会CPHR认证信息", "url": "https://www.ahri.com.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲人力资源经理工资多少？", "answer": "HR Business Partner/HR经理约 $95,000~$135,000（Robert Half均值 $118k；PayScale $102k）；悉尼高级HR经理约 $120k~$160k（Glassdoor $145k）；HR Director/CHRO约 $160k~$350k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲人力资源经理容易找工作吗？", "answer": "容易。Seek 挂牌约 2,000~5,000 个职位，MLTSSL短缺职业，所有行业均有需求。具备People Analytics和HR Tech（Workday）能力的HR经理目前供不应求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国HR经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国HR工作经验可以认可。需要展示对Fair Work Act的理解（或学习计划），以及可量化的HR成果（如员工保留率提升、招聘周期缩短等）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "人力资源经理会被AI替代吗？", "answer": "风险较低。AI辅助简历筛选、薪酬基准分析和员工调查数据处理；但员工关系调查、文化建设、高管沟通和劳资谈判需要深度人际能力，不可替代。善用AI工具的HR经理价值反而更高。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲人力资源经理有年龄限制吗？", "answer": "无。资深CHRO和HR总监（40~55岁）在大型企业和上市公司中备受重视，特别是有组织变革和并购HR整合经验者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲人力资源经理需要什么学历？", "answer": "HR/商科/心理学相关本科学历是基础；VETASSESS评估对相关专业学历认可度较高。持CPHR认证可弥补学历不足。MBA对晋升HR Director路径有帮助。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲人力资源经理认证（移民）难吗？", "answer": "难度中等。VETASSESS评估路径清晰，CPHR认证难度较低。主要挑战是英语沟通能力（IELTS 7.0+）和澳洲劳动法知识。雇主担保482是最快路径。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "人力资源经理和商业分析师哪个更适合移民澳洲？", "answer": "商业分析师薪资相当（$104k~$130k vs HR $102k~$135k），职位数量相似；商业分析师更偏技术分析，英语沟通要求略低；HR经理更偏人际管理，英语沟通要求更高。有HR管理经验者选HR经理，有流程分析经验者选商业分析师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 人力资源经理数据入库完成")

if __name__ == "__main__":
    run()
