"""澳洲审计师（221213）数据入库。数据来源：JSA、SEEK、Indeed、CAANZ（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "221213", "anzsco_title": "External Auditor",
    "category": "商业/金融/法律", "workforce_size": 45000, "shortage_listed": 1,
    "growth_areas": json.dumps(["IT/Cybersecurity Audit","ESG & Sustainability Assurance","Forensic & Fraud Investigation","Internal Audit & Risk Assurance","APRA Financial Compliance Audit"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "审计师",
    "summary": "审计师对企业财务报表和内部控制进行独立审查，确保财务信息的准确性和合规性。澳洲强制审计要求（ASX上市公司/ASIC监管实体）持续推动需求，IT审计和ESG保证审计是2025-2030年增长最快的新兴方向。",
    "forecast_note": "JSA预测审计师至2035年就业增长约7%。ESG可持续报告强制鉴证（ASIC 2026年起分批实施）和IT系统审计需求是主要增长驱动力。",
    "trend_summary": "ESG/可持续发展报告鉴证是澳洲审计行业2025-2030年最大增长方向，ASIC强制要求大型企业对可持续报告进行独立鉴证。IT审计和网络安全审计是薪资溢价最高的专精方向。",
}
I18N_EN = {
    "locale": "en", "name": "Auditor",
    "summary": "Auditors independently examine corporate financial statements and internal controls to verify accuracy and regulatory compliance. Mandatory audit requirements (ASX-listed / ASIC-regulated entities) sustain consistent demand, with IT audit and ESG assurance emerging as the fastest-growing specialisations.",
    "forecast_note": "JSA projects ~7% employment growth for auditors by 2035. Mandatory ESG sustainability assurance (ASIC phased roll-out from 2026) and IT systems audit demand are the primary growth drivers.",
    "trend_summary": "ESG/sustainability reporting assurance is the biggest growth area in Australian auditing in 2025-2030. IT audit and cybersecurity audit are the highest-premium specialisations.",
}
EDUCATION = [
    {"stage": "Bachelor of Accounting / Commerce（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "会计/商科相关学位是审计师职业的基础", "sort_order": 0},
    {"stage": "CA（特许会计师）资格 / CPA资格", "duration": "3~4年工作经验+考试", "cost_min": 3000, "cost_max": 8000, "cost_note": "Big 4审计偏好CA（CAANZ）资格；内部审计可用CPA", "sort_order": 1},
    {"stage": "CIA（Certified Internal Auditor）认证", "duration": "6~18个月备考", "cost_min": 1000, "cost_max": 4000, "cost_note": "内部审计师专业认证，CIA考试费约 $320~$400/门", "sort_order": 2},
    {"stage": "CPA Australia / CAANZ 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 2000, "cost_note": "技术移民必须，约 $500~$800 申请费", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "CA（Chartered Accountant）", "issuer": "Chartered Accountants ANZ (CAANZ)", "note": "Big 4审计偏好CA资格；是外部审计师最主流的专业资格", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "CPA（Certified Practising Accountant）", "issuer": "CPA Australia", "note": "内部审计和政府审计常见资格选择", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CIA（Certified Internal Auditor）", "issuer": "IIA（Institute of Internal Auditors）", "note": "内部审计师专业认证，提升薪资竞争力", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "CISA（Certified Information Systems Auditor）", "issuer": "ISACA", "note": "IT审计专业认证，是IT审计师溢价最高的资格", "is_mandatory": 0, "sort_order": 3},
    {"qual_name": "CPA Australia / CAANZ 技能评估", "issuer": "CPA Australia / CAANZ", "note": "189/190签证技术移民必须，MLTSSL在列", "is_mandatory": 0, "sort_order": 4},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 4000, "note": "全国，含外部审计师、内部审计师和IT审计师岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 3000, "note": "含Big 4、中型会计所和政府审计岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 5000, "note": "Big 4直招和猎头岗"},
]
SALARIES = [
    {"experience": "初级审计师（0~3年）", "salary_min": 60000, "salary_max": 80000, "salary_note": "Big 4毕业生审计师起薪", "sort_order": 0},
    {"experience": "中级审计师（3~7年，CA/CPA）", "salary_min": 80000, "salary_max": 110000, "salary_note": "SEEK 区间 $80k~$100k；Indeed 均值 $91,466（2026）", "sort_order": 1},
    {"experience": "高级/Manager审计师（7~12年）", "salary_min": 110000, "salary_max": 160000, "salary_note": "Big 4 Senior Manager，含年终奖金", "sort_order": 2},
    {"experience": "审计合伙人 / 首席内部审计师（12年+）", "salary_min": 160000, "salary_max": 350000, "salary_note": "Big 4合伙人路径或大型企业Chief Audit Executive", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，Big 4常直接担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，CPA/CAANZ评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区政府审计岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要会计基础+审计标准知识，CA考试有一定难度"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "3年学位+CA资格约3~4年；内部审计CIA约6~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CA考试难度中等，CISA（IT审计）需要专业IT背景"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "ESG强制鉴证（2026起分批）大幅增加对审计师的需求"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级外部审计竞争较激烈；IT审计和ESG审计专精者供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "年末审计季（6~9月）强度高；Big 4文化工时较长"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级 $80k~$110k；高级Manager $110k~$160k；Big 4合伙人 $160k+"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "ESG鉴证+IT审计是10年以上的增长方向，需求明确"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI辅助数据抽样和异常检测，但审计判断和职业怀疑态度不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，CPA/CAANZ评估路径成熟，是最便利的商业类移民职业之一"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "评估和EOI路径清晰，Big 4担保482是最快路径"},
]
SUITABILITY_FIT = ["持有会计/商科相关学位，有审计工作经验（Big 4优先）", "正在备考或已持有CA/CPA/CIA资格", "英语能力达到 IELTS 6.5+", "有IT审计（CISA/系统控制评估）或ESG审计经验（薪资溢价最高）", "目标是Big 4（PwC/Deloitte/EY/KPMG）或联邦政府审计岗"]
SUITABILITY_UNFIT = ["无会计/商科学历，无法通过CPA/CAANZ评估", "不适应规则导向、文档密集的工作方式", "不愿意接受Big 4审计季的高强度工作文化"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "审计师薪资 $80k~$100k（2026）", "url": "https://au.seek.com/career-advice/role/auditor/salary"},
    {"source_name": "Indeed AU", "content": "审计师平均薪资 $91,466（2026）", "url": "https://au.indeed.com/career/auditor/salaries"},
    {"source_name": "CAANZ", "content": "CA资格和审计专业信息", "url": "https://www.charteredaccountantsanz.com/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲审计师工资多少？", "answer": "中级审计师约 $80,000~$110,000（Indeed均值 $91,466；SEEK $80k~$100k）；高级Manager约 $110k~$160k；Big 4合伙人路径 $160k~$350k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲审计师容易找工作吗？", "answer": "容易。Seek 挂牌约 1,500~4,000 个职位，ESG强制鉴证（2026年起）大幅增加需求。IT审计师（CISA持有者）目前极度短缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国审计经验澳洲认可吗？", "answer": "通过CPA Australia或CAANZ技能评估，中国审计经验可以认可。Big 4在中国和澳洲共享审计标准（ISA），因此中国Big 4经验在澳洲具有较高认可度。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "审计师会被AI替代吗？", "answer": "AI辅助数据抽样、交易异常检测和自动化合规检查，但审计判断（职业怀疑态度）、与管理层沟通和审计意见撰写不可替代。AI反而提升了审计师的工作效率和覆盖深度。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲审计师有年龄限制吗？", "answer": "无。资深审计合伙人（40~55岁）是市场上最被重视的，特别是有行业专精（金融服务/政府/资源）经验者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲审计师需要什么学历？", "answer": "会计/商科相关本科学历是CPA/CAANZ评估基础；IT审计师可接受信息技术相关学位。Big 4偏好CA资格持有者。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲审计师认证（移民）难吗？", "answer": "难度中等。MLTSSL在列，CPA/CAANZ评估路径成熟，是商业类移民最便利的路径之一。Big 4担保482是大量海外审计师的快速入境路径。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "审计师和会计师哪个更适合移民澳洲？", "answer": "两者移民路径同样成熟（均为MLTSSL+CPA/CAANZ评估）；会计师就业总量更大，转行灵活性更高；审计师专精ESG和IT审计后薪资溢价更明显。有Big 4审计背景者优选审计路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 审计师数据入库完成")

if __name__ == "__main__":
    run()
