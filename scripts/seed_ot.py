"""澳洲职业治疗师（252411）数据入库。数据来源：JSA、AHPRA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "252411", "anzsco_title": "Occupational Therapist",
    "category": "医疗健康", "workforce_size": 25000, "shortage_listed": 1,
    "growth_areas": json.dumps(["NDIS Disability Support Services","Aged Care OT","Paediatric & Early Intervention OT","Mental Health OT","Workplace Injury Rehabilitation"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "职业治疗师",
    "summary": "职业治疗师帮助残障人士、老年人和伤病患者恢复日常生活和工作能力，服务于NDIS残障支持计划、老年护理、医院、学校和社区健康机构。NDIS改革是近5年最大需求驱动力。",
    "forecast_note": "JSA 预测职业治疗师至2035年就业增长约25%（医疗类增速最快之一）。NDIS计划（约100万参与者）和老年护理改革是主要驱动力。",
    "trend_summary": "NDIS是职业治疗师最大的就业增长引擎，参与者超过100万且持续增长。儿童早期干预和心理健康OT是薪资溢价最高的专科方向。",
}
I18N_EN = {
    "locale": "en", "name": "Occupational Therapist",
    "summary": "Occupational therapists help disabled individuals, elderly and injured people to restore daily living and work function. NDIS disability reform drives exceptional demand across community, aged care and paediatric settings.",
    "forecast_note": "JSA projects ~25% employment growth for OTs by 2035 — one of the fastest in healthcare. NDIS (1M+ participants) and aged care reform are the primary demand drivers.",
    "trend_summary": "NDIS is the largest OT employment growth engine. Paediatric early intervention and mental health OT command the highest salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor/Master of Occupational Therapy（4年）", "duration": "4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "澳洲国际生约 $37,000~$42,000/年；政府补贴名额约 $7,000~$9,000/年", "sort_order": 0},
    {"stage": "海外资历评估（OTC + AHPRA注册）", "duration": "6~12个月", "cost_min": 1500, "cost_max": 5000, "cost_note": "含 Occupational Therapy Council 评估和AHPRA注册费", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor/Master of Occupational Therapy", "issuer": "认可大学", "note": "AHPRA注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Occupational Therapy Registration", "issuer": "AHPRA", "note": "全国统一注册，无此注册不得执业", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "OTC（Occupational Therapy Council）评估", "issuer": "Occupational Therapy Council of Australia", "note": "海外OT学历评估", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "NDIS Provider Registration", "issuer": "NDIS Quality and Safeguards Commission", "note": "独立NDIS服务提供商必须注册", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1200, "count_max": 2500, "note": "全国，含NDIS、老年护理、儿童和医院岗"},
    {"platform": "Indeed",   "count_min": 700,  "count_max": 1500, "note": "含兼职和合同工"},
    {"platform": "LinkedIn", "count_min": 300,  "count_max": 700,  "note": "偏管理、专科和NDIS服务商岗"},
]
SALARIES = [
    {"experience": "新注册OT（0~2年）", "salary_min": 68000, "salary_max": 82000, "salary_note": "公立医院或初级NDIS，含奖励调整", "sort_order": 0},
    {"experience": "中级OT（2~8年）", "salary_min": 82000, "salary_max": 105000, "salary_note": "Indeed 平均 $97,965；SEEK 区间 $80k~$110k（2026）", "sort_order": 1},
    {"experience": "资深/专科OT（8年+）", "salary_min": 105000, "salary_max": 140000, "salary_note": "儿童早期干预和精神健康OT薪资溢价明显", "sort_order": 2},
    {"experience": "NDIS自营服务商（5年+）", "salary_min": 120000, "salary_max": 200000, "salary_note": "注册为NDIS服务提供商，自主接案可大幅提升收入", "sort_order": 3},
    {"experience": "农村/偏远地区OT", "salary_min": 90000, "salary_max": 125000, "salary_note": "农村医疗津贴和签约奖金，实际待遇高于城市", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，OT为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NDIS和农村OT享优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区OT，提名加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "涵盖解剖学、心理学和ADL评估，综合知识要求较高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学位4年+OTC评估约6~12个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "OTC评估主要是学历审核，无高难度考试"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "NDIS+老年护理双重改革，是增速最快的医疗职业之一"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "NDIS需求爆发，持证后立即入职，雇主主动招募"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "工作多样化，社区走访有一定体力要求"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位数约 $82k~$105k；NDIS自营可达 $150k~$200k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "NDIS持续增长（参与者超100万），老龄化持续推高需求"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "个性化功能评估和NDIS目标制定是AI无法替代的核心服务"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，189/190/491/482多路径，NDIS和农村优先"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "OTC评估和OET英语是主要门槛，周期约6~12个月"},
]
SUITABILITY_FIT = ["已持有国内职业治疗/康复医学学位（4年制以上）", "英语能力达到 OET B / IELTS 7.0", "有耐心、同理心和良好的沟通能力", "对NDIS残障支持或儿童早期干预有兴趣", "目标是NDIS自营服务商（高收入路径）"]
SUITABILITY_UNFIT = ["英语能力较弱，OTC评估困难", "不适应社区走访和高度多样化的工作场景", "缺乏耐心，难以应对长期慢性康复工作"]
SOURCES = [
    {"source_name": "AHPRA", "content": "OT注册要求", "url": "https://www.ahpra.gov.au/"},
    {"source_name": "Occupational Therapy Council", "content": "海外OT学历评估", "url": "https://www.otcouncil.com.au/"},
    {"source_name": "Indeed AU", "content": "OT平均薪资 $97,965（2026）", "url": "https://au.indeed.com/career/occupational-therapist/salaries"},
    {"source_name": "NDIS", "content": "NDIS参与者和服务商信息", "url": "https://www.ndis.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲职业治疗师工资多少？", "answer": "中级OT年薪约 $82,000~$105,000（Indeed平均$97,965）；资深专科OT约 $105k~$140k；NDIS自营服务商可达 $150k~$200k+。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲OT容易找工作吗？", "answer": "极容易。NDIS参与者超100万且持续增长，持证后几乎立即入职，NDIS机构主动招募且常提供签约奖金。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国职业治疗学位澳洲认可吗？", "answer": "通过 OTC（澳洲职业治疗委员会）学历评估，确认标准后申请AHPRA注册。主要门槛是英语成绩（OET B/IELTS 7.0+）。总周期约6~12个月。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "职业治疗师会被AI替代吗？", "answer": "替代风险极低。个性化功能评估、NDIS目标制定和患者互动是AI无法替代的核心服务。AI辅助评估工具是助手，不是替代品。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲OT有年龄限制吗？", "answer": "无执业年龄上限。OT工作多样化，从社区到老年护理均有，体力要求适中。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲OT需要什么学历？", "answer": "需要职业治疗学位（Bachelor/Master，通常4年制）。国内OT或康复医学本科（4年制）可申请OTC评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲OT认证难吗？", "answer": "难度中等。OTC评估主要是学历审核，不需要高难度临床考试。英语是最主要门槛，OET B要求口语和听力达标。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "OT和物理治疗师哪个更适合技术移民澳洲？", "answer": "两者PR路径和薪资相近。OT的独特优势是NDIS市场（百万参与者），自营服务商收入潜力更高；物理治疗师在体育和运动康复方向有独特机会。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 职业治疗师数据入库完成")

if __name__ == "__main__":
    run()
