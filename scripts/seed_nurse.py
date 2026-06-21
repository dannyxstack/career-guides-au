"""澳洲注册护士（254422）数据入库。数据来源：JSA、AHPRA、SEEK、Indeed、ERI、ANMF（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "254422", "anzsco_title": "Registered Nurse (Medical Practice)",
    "category": "医疗健康", "workforce_size": 320000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Aged Care & Dementia Nursing","ICU & Critical Care","Rural & Remote Health","Mental Health Nursing","Oncology & Specialist Nursing"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "注册护士",
    "summary": "注册护士在医院、老年护理机构、社区卫生服务和门诊中提供临床护理、用药和患者评估服务。澳大利亚老龄化社会驱动护士需求持续旺盛，是技术移民最受欢迎的医疗健康职业之一。",
    "forecast_note": "JSA 预测护理类职业至2035年将新增约50,000个岗位（+18%）。老年护理改革（2023年起强制人手配比）和农村医疗服务扩张是主要驱动力。",
    "trend_summary": "老年护理立法强制每日直接护理时间（210分钟）大幅推高需求。心理健康和偏远地区护士的薪资溢价持续扩大。",
}
I18N_EN = {
    "locale": "en", "name": "Registered Nurse",
    "summary": "Registered nurses provide clinical care, medication administration and patient assessment in hospitals, aged care, community health and outpatient settings. Australia's ageing population sustains very high and growing demand.",
    "forecast_note": "JSA projects ~50,000 additional nursing jobs by 2035 (+18%). Aged care mandatory staffing ratios (210 mins direct care/day from 2023) and rural health expansion are primary drivers.",
    "trend_summary": "Aged care legislative mandates significantly boosted demand. Mental health and rural/remote nursing attract significant salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of Nursing（本科学历）", "duration": "3年（全日制）", "cost_min": 0, "cost_max": 30000, "cost_note": "澳洲公立大学约 $28,000~$34,000（海外留学生更高）；政府补贴名额学费约 $8,000~$10,000/年", "sort_order": 0},
    {"stage": "海外资历评估（AHPRA注册）", "duration": "3~12个月", "cost_min": 1500, "cost_max": 4000, "cost_note": "含AHPRA申请费、ANMAC评估费、英语考试（OET/IELTS）", "sort_order": 1},
    {"stage": "Bridging Program（海外护士英语能力培训）", "duration": "3~6个月", "cost_min": 3000, "cost_max": 8000, "cost_note": "海外护士来澳执业前的临床适应培训", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Nursing（或同等资历）", "issuer": "澳洲认可大学", "note": "AHPRA注册的基础学历要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Registered Nurse Registration", "issuer": "Australian Health Practitioner Regulation Agency", "note": "全国统一注册，无此注册不得以注册护士身份执业", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "OET / IELTS 英语成绩", "issuer": "OET / British Council", "note": "海外护士AHPRA注册强制要求（OET B级或IELTS 7.0+）", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "专科护士认证（ICU/急诊/肿瘤等）", "issuer": "ACCCN / 各专科学会", "note": "晋升专科护士或护士长的可选进阶资质", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 8000,  "count_max": 14000, "note": "全国，含医院、老年护理、社区和专科岗，是挂牌量最多的职业之一"},
    {"platform": "Indeed",   "count_min": 5000,  "count_max": 9000,  "note": "含兼职、夜班和合同工"},
    {"platform": "LinkedIn", "count_min": 2000,  "count_max": 4000,  "note": "偏管理、专科和教育护士岗"},
]
SALARIES = [
    {"experience": "新注册护士（RN Grade 1）", "salary_min": 70000, "salary_max": 78000, "salary_note": "NSW公立医院 Nurses Award 起薪 $70,235；各州起薪相近", "sort_order": 0},
    {"experience": "中级护士（RN Grade 2~4，3~8年）", "salary_min": 78000, "salary_max": 100000, "salary_note": "ERI SalaryExpert 平均 $114,868；Indeed 区间 $80k~$100k（2026）", "sort_order": 1},
    {"experience": "资深护士 / 老年护理（8年+）", "salary_min": 100000, "salary_max": 120000, "salary_note": "老年护理28%薪资涨幅（2024起）使部分老年护理护士薪资超医院", "sort_order": 2},
    {"experience": "专科护士（ICU/急诊/麻醉）", "salary_min": 110000, "salary_max": 135000, "salary_note": "ICU/麻醉护士薪资溢价 $15k~$25k", "sort_order": 3},
    {"experience": "护士长 / 主任护士（NUM/CNM）", "salary_min": 120000, "salary_max": 150000, "salary_note": "管理职责加薪，部分医院 NUM 超 $140k", "sort_order": 4},
    {"experience": "农村/偏远地区护士（Rural/Remote）", "salary_min": 90000, "salary_max": 130000, "salary_note": "偏远地区津贴 $10k~$30k+，额外房屋补贴", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，护士为核心紧缺岗位，审批快", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，老年护理和农村护士优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，农村护士岗位广泛", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "医学知识、临床技能和心理素质要求较高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "本科3年+AHPRA注册；海外互认约3~12个月"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "AHPRA注册要求严格；海外护士英语要求（OET B）较高"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "老龄化+老年护理立法双重驱动，全国供需缺口极大"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "护士极度供不应求，注册后通常可立即入职"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 5, "note": "夜班、轮班、情绪劳动和体力要求均高"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位数约 $80k~$100k；专科护士和老年护理上涨显著"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "老龄化+老年护理立法+心理健康改革三重驱动"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "护理工作高度依赖人际互动、情感支持和临床判断"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL长期在列，189/190/491/482多路径，老年护理和农村护士优先"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "AHPRA注册和OET英语是主要门槛，海外互认周期约3~12个月"},
]
SUITABILITY_FIT = [
    "有护理执业背景（国内注册护士/护士执照），希望技能移民来澳",
    "英语能力达到或接近 OET B / IELTS 7.0，愿意持续提升",
    "接受夜班、轮班和老年护理/农村偏远地区就业",
    "有耐心和同理心，适应高情绪劳动工作环境",
    "目标是老年护理管理、专科护士或护士长职业路径",
]
SUITABILITY_UNFIT = [
    "英语能力较弱，短期内无法达到 OET B 要求",
    "无法接受夜班、轮班或偶尔农村派驻",
    "情绪稳定性差，难以应对高压临床和患者去世情境",
]
SOURCES = [
    {"source_name": "AHPRA", "content": "注册护士注册要求和海外互认流程", "url": "https://www.ahpra.gov.au/Registration/Applying-for-registration.aspx"},
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 2544 注册护士职业档案与就业预测", "url": "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/2544-registered-nurses"},
    {"source_name": "ERI SalaryExpert", "content": "注册护士平均年薪 $114,868（2026）", "url": "https://www.erieri.com/salary/job/registered-nurse/australia"},
    {"source_name": "ANMF", "content": "澳洲护士协会薪资奖励标准（Nurses Award）", "url": "https://www.anmf.org.au/"},
    {"source_name": "Fair Work Commission", "content": "Nurses Award MA000034 薪资标准", "url": "https://portal.fairwork.gov.au/ArticleDocuments/872/nurses-award-ma000034-pay-guide.pdf.aspx"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲注册护士工资多少？", "answer": "新注册护士起薪约 $70,000~$78,000；中级护士约 $78,000~$100,000；专科护士（ICU/急诊）约 $110,000~$135,000。老年护理薪资因2024年立法大幅上涨，部分护士超越医院薪资水平。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲护士容易找工作吗？", "answer": "极容易。护士极度供不应求，Seek 常年挂牌 8,000~14,000 个职位，AHPRA注册后通常可立即入职，雇主常主动提供签证担保。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国护士执照澳洲认可吗？", "answer": "通过 AHPRA（ANMAC评估）流程可互认，周期约3~12个月。主要门槛是英语成绩（OET B或IELTS 7.0+），建议提前备考。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "护士会被AI替代吗？", "answer": "替代风险极低。护理工作高度依赖人际互动、情感支持、临床判断和体力操作，AI辅助诊断不会替代床旁护理的核心价值。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲护士有年龄限制吗？", "answer": "无法律上限。海外护士40~50岁来澳转注册的案例很多，但移民打分45岁以上无加分，建议尽早启动签证申请。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲护士需要本科学历吗？", "answer": "需要。AHPRA注册要求至少 Bachelor of Nursing（3年）或同等资历。国内护理专科毕业需额外评估，部分情况需补修学分。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "海外护士在澳洲执业难吗？", "answer": "主要难点是英语（OET B要求较高，口语和听力尤其严格）和临床适应期。通过后工作不难，雇主对有经验的海外护士非常欢迎。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "护士和全科医生哪个更适合技术移民澳洲？", "answer": "护士PR路径更简单快捷（无需AMC考试），薪资足够支撑体面生活；全科医生薪资远高于护士（$200k~$400k+ vs $80k~$120k），但注册和认证流程复杂得多，建议已有医生执照者走医生路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 注册护士数据入库完成")

if __name__ == "__main__":
    run()
