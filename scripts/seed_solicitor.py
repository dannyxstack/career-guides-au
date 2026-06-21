"""澳洲律师（271311）数据入库。数据来源：JSA、SEEK、Indeed、Law Society（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "271311", "anzsco_title": "Solicitor",
    "category": "商业/金融/法律", "workforce_size": 90000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Technology Law & AI Regulation","Cybersecurity & Data Privacy Law","Energy Transition & Climate Law","Immigration & Refugee Law","In-house Counsel (Technology Companies)"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "律师（事务律师）",
    "summary": "律师（Solicitor）为客户提供法律建议、合同起草、争议解决和法庭代理服务，覆盖商业法、房产、家庭、劳动法和刑事等多个法律领域。澳洲法律市场虽竞争激烈，但商业法（特别是科技/AI/能源转型方向）的律师和公司内部法律顾问（In-house Counsel）需求旺盛，是高门槛高薪资的顶级专业职业。",
    "forecast_note": "JSA预测律师至2035年就业增长约8%。AI监管法、数据隐私法（Privacy Act改革2025）和能源转型法律咨询是2025-2030年增长最快的法律专业方向。",
    "trend_summary": "科技法律（Technology Law）和AI监管咨询是2025年澳洲法律行业增速最快的专精方向，各大科技公司和政府机构急需科技律师。Privacy Act 2025改革推动对数据隐私律师的强劲需求。",
}
I18N_EN = {
    "locale": "en", "name": "Solicitor / Lawyer",
    "summary": "Solicitors provide legal advice, draft contracts, dispute resolution and court representation across commercial law, property, family, employment and criminal law. Despite competitive markets, commercial law (especially technology/AI/energy transition) and in-house counsel roles are in strong demand — a high-barrier, high-income elite profession.",
    "forecast_note": "JSA projects ~8% employment growth for solicitors by 2035. AI regulatory law, data privacy law (Privacy Act reform 2025) and energy transition legal advisory are the fastest-growing specialisations.",
    "trend_summary": "Technology law and AI regulatory advisory are the fastest-growing specialisations in Australian law in 2025, with technology companies and government urgently seeking tech lawyers. The Privacy Act 2025 reform drives strong demand for data privacy solicitors.",
}
EDUCATION = [
    {"stage": "LLB / JD 法律学位（3~4年）", "duration": "LLB 4~5年（本科），或 JD 3年（研究生）", "cost_min": 35000, "cost_max": 220000, "cost_note": "是澳洲律师资格的基本学历要求；国际生费用约 $35,000~$55,000/年", "sort_order": 0},
    {"stage": "PLT（Practical Legal Training）实习培训", "duration": "6~12个月", "cost_min": 3000, "cost_max": 15000, "cost_note": "完成学位后必须完成PLT+受监督执业期方可注册律师；费用约 $3,000~$8,000", "sort_order": 1},
    {"stage": "律师注册（Admission to the Bar）", "duration": "1~3个月申请", "cost_min": 500, "cost_max": 2000, "cost_note": "向各州最高法院申请律师注册，是合法执业的法律要求", "sort_order": 2},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须（使用VETASSESS评估海外法律学历）；注意澳洲法律资格认证门槛高", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Admission to Practice（律师注册）", "issuer": "各州最高法院（Supreme Court）", "note": "澳洲合法执业律师的法律要求，是所有律师的基础执照", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Practising Certificate（执业证书）", "issuer": "各州律师协会（Law Society / Law Institute）", "note": "每年更新的执业证书，是澳洲律师执业的法律要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Accredited Specialist（认证专家）", "issuer": "各州律师协会", "note": "在特定法律领域（商业法/家庭法等）的专业认证，提升信誉和薪资", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须（海外法律学历评估）", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 6000, "note": "全国，含律师、法律顾问、内部法律顾问和合规官岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 4000, "note": "含律所、政府法律部门和大型企业法律团队岗"},
    {"platform": "LinkedIn", "count_min": 3000, "count_max": 8000, "note": "律所直招和顶级法律猎头"},
]
SALARIES = [
    {"experience": "毕业律师 / 首年律师（0~2年）", "salary_min": 70000, "salary_max": 95000, "salary_note": "顶级律所（MinterEllison/Clayton Utz/Allens）毕业律师起薪", "sort_order": 0},
    {"experience": "执业律师（2~7年）", "salary_min": 90000, "salary_max": 130000, "salary_note": "SEEK 区间 $95k~$115k；Indeed 均值 $113,923（2026）", "sort_order": 1},
    {"experience": "高级律师 / Senior Associate（7~12年）", "salary_min": 130000, "salary_max": 200000, "salary_note": "顶级律所高级律师，含可能的合伙人路径加速分红", "sort_order": 2},
    {"experience": "合伙人 / 公司内部总法律顾问（12年+）", "salary_min": 200000, "salary_max": 600000, "salary_note": "顶级律所合伙人或大型上市公司General Counsel，含分红", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，律所可担保有本地化评估路径的候选人", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，VETASSESS评估（注意澳洲法律资格认证较复杂）", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "澳洲法律学位是最难的专业之一，需要精确的英语法律写作能力"},
    {"dimension": "learning_duration",        "label_zh": "极长", "stars": 5, "note": "LLB/JD 4~5年+PLT 6~12个月+受监督执业=总周期约6~8年"},
    {"dimension": "certification_difficulty", "label_zh": "极高", "stars": 5, "note": "Admission to the Bar需要通过复杂评估流程；海外法律学历额外需要VETASSESS评估"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "商业法、科技法和In-house Counsel需求旺盛；家庭法/刑事法律所招聘量较小"},
    {"dimension": "competition",              "label_zh": "很高", "stars": 4, "note": "顶级律所入职竞争极激烈（Top 10澳洲大学优先），科技法专精律师供不应求"},
    {"dimension": "work_intensity",           "label_zh": "极高", "stars": 5, "note": "顶级律所文化工作强度极高（60~80小时/周），特别是并购和IPO项目期间"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "执业律师 $90k~$130k；合伙人/GC $200k~$600k，是澳洲薪资最高的职业之一"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "科技法/AI监管/能源转型法律是10年以上的增长方向"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "合同审查和法律研究受AI（Harvey AI/Clio）影响，但法庭策略、谈判和复杂法律判断不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL核心短缺列表；海外法律学历认证复杂，澳洲本地法律学历更易直接执业"},
    {"dimension": "pr_difficulty",            "label_zh": "很高", "stars": 4, "note": "澳洲律师资格认证（Admission to the Bar）门槛高；海外法律学历需要额外评估和可能的补充学习"},
]
SUITABILITY_FIT = ["持有法律学位（LLB/JD/相当学历）并已在澳洲完成PLT+律师注册", "英语法律写作能力极强（IELTS 8.0+，商业法律文件和合同要求高）", "有商业法/科技法/能源转型法律方向专精（薪资溢价最高）", "目标是大型商业律所（MinterEllison/Allens/Herbert Smith Freehills）或上市公司In-house Counsel", "有中国国际业务法律背景（中澳交叉法律业务是独特优势）"]
SUITABILITY_UNFIT = ["英语法律写作能力不足以撰写复杂英语合同和法律意见书", "无意愿承担顶级律所的高强度工作文化（60~80小时/周）", "海外法律学历评估路径不明确，无意进行本地化认证补充学习"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "律师薪资 $95k~$115k（2026）", "url": "https://au.seek.com/career-advice/role/solicitor/salary"},
    {"source_name": "Indeed AU", "content": "律师平均薪资 $113,923（2026）", "url": "https://au.indeed.com/career/solicitor/salaries"},
    {"source_name": "Law Society NSW", "content": "律师注册和执业信息", "url": "https://www.lawsociety.com.au/"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲律师工资多少？", "answer": "执业律师约 $90,000~$130,000（Indeed均值 $113,923；SEEK $95k~$115k）；高级律师/Senior Associate约 $130k~$200k；合伙人/General Counsel约 $200k~$600k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲律师容易找工作吗？", "answer": "整体中等难度，但细分方向差异大。科技法、数据隐私法和能源转型法律律师供不应求；家庭法和刑事法岗位竞争较激烈。Seek 挂牌约 2,000~6,000 个职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国法律学历澳洲认可吗？", "answer": "复杂。中国法律学历需要通过VETASSESS技能评估，并可能需要额外补充澳洲法律课程（通常是Graduate Diploma of Australian Law）。完成后仍需申请Admission to the Bar（律师注册）。建议通过澳洲大学攻读JD（法律硕士）直接获取本地资格。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "律师会被AI替代吗？", "answer": "部分影响。AI（Harvey AI/Clio/LexisNexis AI）已能自动化合同初审和法律研究，影响初级律师工作量；但法庭策略、谈判技巧、复杂法律判断和客户关系完全不可替代。AI反而增加了对科技法律师（监管AI本身）的需求。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲律师有年龄限制吗？", "answer": "无。资深合伙人（40~60岁）是律所最核心的资产。转行成为律师的年龄门槛也无限制，有人在40岁后完成JD并成功执业。但投入产出比需要认真评估。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲律师需要什么学历？", "answer": "澳洲认可的法律学位（LLB/JD）+PLT+律师注册（Admission to the Bar）。海外法律学历需要额外评估，通常建议通过澳洲大学JD（通常2年制加速项目）获取本地资格。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲律师认证（移民）难吗？", "answer": "非常难，是商业类移民路径最复杂的职业。海外法律学历认证门槛高；移民后通常需要补充澳洲法律学习。建议通过雇主担保482（顶级律所直接担保）作为最可行的快速路径。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "律师和会计师哪个更适合移民澳洲？", "answer": "会计师移民路径更成熟（MLTSSL+CPA/CAANZ评估），门槛更低；律师薪资上限更高（合伙人 $200k~$600k），但移民路径更复杂，需要澳洲法律资格重新认证。有会计背景者首选会计师；有法律背景且英语极强者，可考虑JD路径重新获取澳洲律师资格。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 律师数据入库完成")

if __name__ == "__main__":
    run()
