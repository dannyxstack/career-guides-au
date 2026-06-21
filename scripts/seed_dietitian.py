"""澳洲营养师（251111）数据入库。数据来源：JSA、DAA、AHPRA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "251111", "anzsco_title": "Dietitian",
    "category": "医疗健康", "workforce_size": 10000, "shortage_listed": 1,
    "growth_areas": json.dumps(["NDIS Nutrition Support","Aged Care Nutrition Management","Sports & Performance Dietetics","Oncology & Clinical Dietetics","Telehealth Dietetics"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "营养师",
    "summary": "营养师（Dietitian）提供临床营养评估、个性化饮食方案和疾病管理服务，服务于医院、老年护理、NDIS、癌症中心和社区健康机构。MLTSSL在列，是医疗辅助职业中增长最快的方向之一。",
    "forecast_note": "JSA 预测营养师至2035年就业增长约20%。NDIS营养支持需求、老年护理改革（强制营养管理）和慢性病（糖尿病/肥胖）流行是主要驱动力。",
    "trend_summary": "NDIS将营养服务纳入可报销范畴，为营养师创造大量新就业机会。体育营养和癌症营养是薪资溢价最高的专科方向。",
}
I18N_EN = {
    "locale": "en", "name": "Dietitian",
    "summary": "Dietitians provide clinical nutrition assessments, personalised dietary plans and disease management across hospitals, aged care, NDIS, cancer centres and community health. MLTSSL listed, fast-growing allied health career.",
    "forecast_note": "JSA projects ~20% employment growth for dietitians by 2035. NDIS nutrition support, aged care mandatory nutrition management and chronic disease prevalence (diabetes/obesity) are the primary drivers.",
    "trend_summary": "NDIS inclusion of nutrition services creates major new employment opportunities. Sports and oncology dietetics command salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor/Master of Nutrition and Dietetics（4年）", "duration": "4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "澳洲国际生约 $37,000~$42,000/年；政府补贴名额约 $7,000~$9,000/年", "sort_order": 0},
    {"stage": "海外资历评估（DAA + APD注册）", "duration": "6~18个月", "cost_min": 1000, "cost_max": 5000, "cost_note": "含 Dietitians Australia 评估和 Accredited Practising Dietitian (APD) 注册费", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor/Master of Nutrition and Dietetics", "issuer": "认可大学", "note": "APD认证基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "APD（Accredited Practising Dietitian）认证", "issuer": "Dietitians Australia", "note": "行业认证，NDIS和Medicare报销强制要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "海外资历评估", "issuer": "Dietitians Australia", "note": "海外营养师学历评估，确认是否达到澳洲标准", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 500,  "count_max": 1000, "note": "全国，含医院、老年护理、NDIS、社区和运动营养岗"},
    {"platform": "Indeed",   "count_min": 300,  "count_max": 700,  "note": "含兼职和合同工"},
    {"platform": "LinkedIn", "count_min": 150,  "count_max": 400,  "note": "偏管理、研究和专科岗"},
]
SALARIES = [
    {"experience": "新注册营养师（0~2年）", "salary_min": 65000, "salary_max": 80000, "salary_note": "医院或社区健康，含基本薪", "sort_order": 0},
    {"experience": "中级营养师（2~8年）", "salary_min": 80000, "salary_max": 105000, "salary_note": "Indeed 平均 $94,475；SEEK 区间 $75k~$105k（2026）", "sort_order": 1},
    {"experience": "资深/专科营养师（8年+）", "salary_min": 105000, "salary_max": 140000, "salary_note": "癌症、重症监护和肾脏营养专科薪资较高", "sort_order": 2},
    {"experience": "私人执业/NDIS自营（5年+）", "salary_min": 100000, "salary_max": 180000, "salary_note": "NDIS自营服务商可大幅提升收入", "sort_order": 3},
    {"experience": "农村/偏远地区营养师", "salary_min": 88000, "salary_max": 120000, "salary_note": "农村医疗津贴和签约奖金，实际待遇好于城市", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，营养师为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NDIS和农村营养服务优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区医疗，提名加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "营养科学和临床技能综合要求，学习难度适中"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 3, "note": "学位4年+DAA评估约6~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "DAA评估主要是学历审核，APD认证有继续教育要求"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "NDIS+老年护理+慢性病三重驱动，MLTSSL在列"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，持证后通常可较快入职"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "工作环境多样，无夜班，节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位数约 $80k~$105k；NDIS自营潜力更高"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 4, "note": "NDIS+慢性病管理+老龄化持续推高需求"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI可提供饮食建议，但临床营养评估和个性化方案需执照"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，189/190/491/482多路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "DAA评估和OET英语是主要门槛，周期约6~18个月"},
]
SUITABILITY_FIT = ["已持有国内营养学/临床营养学位（4年制以上）", "英语能力达到 OET B / IELTS 7.0", "对慢性病管理和NDIS残障营养有兴趣", "接受农村派驻以快速获取PR", "目标是NDIS自营服务商或体育营养师"]
SUITABILITY_UNFIT = ["英语能力较弱，DAA评估困难", "只有营养学理论背景（无临床营养实践），APD认证有实习要求", "期望立即高薪（入门薪资相对其他医疗类较低）"]
SOURCES = [
    {"source_name": "Dietitians Australia (DAA)", "content": "营养师APD认证和海外评估", "url": "https://dietitiansaustralia.org.au/"},
    {"source_name": "Indeed AU", "content": "营养师平均薪资 $94,475（2026）", "url": "https://au.indeed.com/career/dietitian/salaries"},
    {"source_name": "NDIS", "content": "NDIS营养支持服务报销政策", "url": "https://www.ndis.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲营养师工资多少？", "answer": "中级营养师年薪约 $80,000~$105,000（Indeed平均$94,475）；NDIS自营和专科营养师可达 $100k~$180k；农村地区含补贴约 $88k~$120k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲营养师容易找工作吗？", "answer": "容易。NDIS纳入营养服务报销后创造大量新岗位，Seek 挂牌 500~1,000 个职位，MLTSSL在列，持证后较快入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国营养学学位澳洲认可吗？", "answer": "通过 Dietitians Australia（DAA）学历评估，确认标准后申请APD认证。主要门槛是英语成绩（OET B/IELTS 7.0+）和临床实践时间要求。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "营养师会被AI替代吗？", "answer": "替代风险较低。AI营养App提供基础饮食建议，但临床营养评估（如癌症/肾病/重症）、NDIS个性化支持计划和Medicare报销服务均需持证营养师。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲营养师有年龄限制吗？", "answer": "无执业年龄上限。工作环境多样、无夜班，对年龄无明显限制，适合各年龄段转行。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲营养师需要什么学历？", "answer": "需要营养与饮食学学位（Bachelor/Master，4年制）。国内临床营养学或公共营养学本科（4年制）可申请DAA评估，但部分情况需补修学分。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲营养师认证难吗？", "answer": "难度中等。DAA评估主要是学历审核，不需要高难度临床考试。APD认证有继续教育要求（每年维持），英语是最主要门槛。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "营养师和物理治疗师哪个更适合技术移民澳洲？", "answer": "两者PR路径和认证难度相近。物理治疗师就业量更大（Seek ~2,500 vs 营养师 ~800），薪资略高；营养师NDIS自营潜力更高，适合有商业意愿的从业者。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 营养师数据入库完成")

if __name__ == "__main__":
    run()
