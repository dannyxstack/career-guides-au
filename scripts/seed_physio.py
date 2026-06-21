"""澳洲物理治疗师（252511）数据入库。数据来源：JSA、AHPRA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "252511", "anzsco_title": "Physiotherapist",
    "category": "医疗健康", "workforce_size": 36000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Aged Care Physiotherapy","Sports & Exercise Rehabilitation","Telehealth Physiotherapy","Rural & Remote Primary Health","Workplace Injury Rehabilitation"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "物理治疗师",
    "summary": "物理治疗师通过运动、手法和康复训练治疗肌肉骨骼、神经和心肺疾病，服务于医院、诊所、老年护理、体育俱乐部和社区健康机构。MLTSSL在列，需求稳定且持续增长。",
    "forecast_note": "JSA 预测物理治疗师至2035年就业增长约15%。老龄化人口（骨关节疾病增加）、运动健康意识提升和老年护理改革是主要驱动力。",
    "trend_summary": "运动物理治疗（NRL/AFL/NBL等职业联赛）和老年护理物理治疗是增长最快的方向。Telehealth物理治疗在COVID后迅速普及，创造新就业模式。",
}
I18N_EN = {
    "locale": "en", "name": "Physiotherapist",
    "summary": "Physiotherapists treat musculoskeletal, neurological and cardiorespiratory conditions through exercise therapy, manual techniques and rehabilitation. Strong demand across hospitals, clinics, aged care and sport.",
    "forecast_note": "JSA projects ~15% employment growth for physiotherapists by 2035. Ageing population (musculoskeletal disease increase), sports health awareness and aged care reform are key drivers.",
    "trend_summary": "Sports physiotherapy (professional leagues) and aged care physiotherapy are fastest-growing. Telehealth physiotherapy expanded rapidly post-COVID.",
}
EDUCATION = [
    {"stage": "Bachelor of Physiotherapy / Master of Physiotherapy（4年）", "duration": "4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "澳洲国际生约 $37,000~$42,000/年；政府补贴名额约 $7,000~$9,000/年", "sort_order": 0},
    {"stage": "海外资历评估（APC + AHPRA注册）", "duration": "6~12个月", "cost_min": 1500, "cost_max": 5000, "cost_note": "含 Australian Physiotherapy Council 评估、OET/IELTS和AHPRA注册费", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor/Master of Physiotherapy", "issuer": "认可大学", "note": "AHPRA注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Physiotherapy Registration", "issuer": "AHPRA", "note": "全国统一注册，无此注册不得执业", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "APC（Australian Physiotherapy Council）评估", "issuer": "Australian Physiotherapy Council", "note": "海外物理治疗师学历评估", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Sports Physiotherapy 专科资质", "issuer": "Sports Medicine Australia / APA", "note": "晋升运动物理治疗师的进阶资质", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 3000, "note": "全国，含医院、诊所、老年护理和运动机构岗"},
    {"platform": "Indeed",   "count_min": 900,  "count_max": 1800, "note": "含兼职和合同工"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 900,  "note": "偏管理、教育和专科岗"},
]
SALARIES = [
    {"experience": "新注册物理治疗师（0~2年）", "salary_min": 70000, "salary_max": 85000, "salary_note": "公立医院或初级诊所，含奖励调整", "sort_order": 0},
    {"experience": "中级物理治疗师（2~8年）", "salary_min": 85000, "salary_max": 110000, "salary_note": "Indeed 平均 $93,920；SEEK 区间 $85k~$110k（2026）", "sort_order": 1},
    {"experience": "资深/专科物理治疗师（8年+）", "salary_min": 110000, "salary_max": 145000, "salary_note": "运动物理治疗和专科诊所薪资较高", "sort_order": 2},
    {"experience": "私人诊所自营（5年+）", "salary_min": 120000, "salary_max": 200000, "salary_note": "自营诊所收益可超雇员2倍，视患者量而定", "sort_order": 3},
    {"experience": "农村/偏远地区物理治疗师", "salary_min": 95000, "salary_max": 130000, "salary_note": "偏远地区津贴和签约奖金显著提升总收入", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，物理治疗师为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，农村医疗机构享优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区医疗，提名加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "解剖学、运动学和临床技能要求较高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学位4年+APC评估约6~12个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "APC评估主要是学历审核，非高难度考试"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "老龄化+运动健康意识+老年护理改革三重驱动"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，持证后通常可较快入职"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "体力操作有一定要求，工作环境相对舒适"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位数约 $85k~$110k；自营诊所可达 $150k~$200k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 4, "note": "老龄化和运动健康趋势持续推动就业增长"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "手法治疗和个性化康复方案是AI无法替代的核心价值"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，189/190/491/482多路径，农村医疗优先"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "APC评估和OET英语是主要门槛，周期约6~12个月"},
]
SUITABILITY_FIT = ["已持有国内物理治疗/康复医学学位（4年制以上）", "英语能力达到 OET B / IELTS 7.0", "有运动健康或老年护理从业兴趣", "接受农村派驻以快速获取PR", "目标是自营私人诊所或运动物理治疗师"]
SUITABILITY_UNFIT = ["英语能力较弱，APC评估困难", "体力较差（手法操作有一定体力要求）", "不适应高强度的患者管理节奏"]
SOURCES = [
    {"source_name": "AHPRA", "content": "物理治疗师注册要求", "url": "https://www.ahpra.gov.au/"},
    {"source_name": "Australian Physiotherapy Council (APC)", "content": "海外物理治疗师学历评估", "url": "https://www.physiocouncil.com.au/"},
    {"source_name": "Indeed AU", "content": "物理治疗师平均薪资 $93,920（2026）", "url": "https://au.indeed.com/career/physical-therapist/salaries"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲物理治疗师工资多少？", "answer": "中级物理治疗师年薪约 $85,000~$110,000（Indeed平均$93,920）；资深专科物理治疗师约 $110k~$145k；自营诊所可达 $150k~$200k+。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲物理治疗师容易找工作吗？", "answer": "容易。Seek 挂牌 1,500~3,000 个职位，老龄化和运动健康持续推高需求，农村地区几乎可立即入职并享有额外津贴。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国物理治疗学位澳洲认可吗？", "answer": "通过 APC（澳洲物理治疗委员会）学历评估，确认标准后申请AHPRA注册。主要门槛是英语成绩（OET B/IELTS 7.0+）。总周期约6~12个月。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "物理治疗师会被AI替代吗？", "answer": "替代风险极低。个性化手法治疗、动态运动评估和患者激励是AI无法替代的核心服务。AI在评估辅助和远程监控上是辅助工具。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲物理治疗师有年龄限制吗？", "answer": "无执业年龄上限。手法操作要求一定体力，但老年护理和老年患者为主的诊所环境强度适中。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲物理治疗师需要什么学历？", "answer": "需要物理治疗学位（Bachelor/Master，通常4年制）。国内物理治疗或康复医学本科（4年制）可申请APC评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲物理治疗师认证难吗？", "answer": "难度中等。APC评估主要是学历审核，不需要像AMC/ADC那样的高难度临床考试，英语是最主要门槛。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "物理治疗师和注册护士哪个更适合技术移民澳洲？", "answer": "护士就业量更大（Seek ~10,000+ vs 物理治疗师 ~2,500），两者PR路径相近。物理治疗师工作节奏更规律（无夜班），薪资相近；护士需求量更大，入职更快。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 物理治疗师数据入库完成")

if __name__ == "__main__":
    run()
