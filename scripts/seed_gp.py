"""澳洲全科医生（253111）数据入库。数据来源：JSA、AHPRA、AMC、RACGP、SEEK、PayScale（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "253111", "anzsco_title": "General Medical Practitioner",
    "category": "医疗健康", "workforce_size": 40000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Rural & Remote GP Shortages","Aged Care Medical Services","Telehealth & Digital Health","Chronic Disease Management","Mental Health & MHCP"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "全科医生",
    "summary": "全科医生（GP）提供综合初级医疗服务，包括诊断、治疗、慢性病管理、预防保健和转诊。澳大利亚全科医生严重短缺，尤其在农村和偏远地区，是政府优先吸引海外医生的职业类别。",
    "forecast_note": "澳洲全科医生短缺预计至2030年达7,000人缺口，农村地区更为严峻。政府通过 DWS（Doctor Workforce Shortage）区域政策吸引海外医生。",
    "trend_summary": "远程医疗（Telehealth）和慢性病管理是增长最快的服务模式。农村地区GP享有额外政府补贴和永居快速通道。",
}
I18N_EN = {
    "locale": "en", "name": "General Practitioner (GP)",
    "summary": "General practitioners provide comprehensive primary care including diagnosis, treatment, chronic disease management, preventive health and referrals. Australia faces a chronic GP shortage, especially in rural and remote areas.",
    "forecast_note": "Australia's GP shortage is projected to reach 7,000 by 2030. The government prioritises recruiting overseas-trained doctors (OTDs) through DWS regional policies.",
    "trend_summary": "Telehealth and chronic disease management are the fastest-growing service models. Rural GPs receive additional government incentives and fast-tracked PR pathways.",
}
EDUCATION = [
    {"stage": "医学学位（MBBS/MD）", "duration": "5~6年（澳洲）或海外同等学位", "cost_min": 50000, "cost_max": 400000, "cost_note": "澳洲医学生学费（国际生）约 $60,000~$80,000/年；国内医学毕业生申请互认无需重读学位", "sort_order": 0},
    {"stage": "AMC 考试（澳洲医学委员会评估）", "duration": "6~18个月", "cost_min": 3000, "cost_max": 8000, "cost_note": "含 AMC MCQ 笔试（$2,900）和临床考试（$4,900+），总费用约 $5,000~$8,000", "sort_order": 1},
    {"stage": "AHPRA 注册 + 临床培训期（PGY）", "duration": "1~2年", "cost_min": 500, "cost_max": 2000, "cost_note": "AHPRA注册费约 $800；临床培训期通常为有薪岗位", "sort_order": 2},
    {"stage": "RACGP/ACRRM 全科培训（Fellowship）", "duration": "3~4年", "cost_min": 8000, "cost_max": 15000, "cost_note": "完成Fellowship后方可独立执业全科，农村培训享政府补贴", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "MBBS / MD（医学学士/博士）", "issuer": "认可大学", "note": "AHPRA注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AMC Certificate（澳洲医学委员会资质证书）", "issuer": "Australian Medical Council", "note": "海外医学毕业生在澳执业的强制评估", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "AHPRA Medical Registration", "issuer": "AHPRA", "note": "全国统一医生注册，无此注册不得执业", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "FRACGP / FACRRM（全科Fellowship）", "issuer": "RACGP / ACRRM", "note": "独立全科执业的行业标准资质，非强制但强烈建议", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1200, "count_max": 2500, "note": "全国，含诊所、农村、急诊和医院GP岗"},
    {"platform": "Indeed",   "count_min": 800,  "count_max": 1600, "note": "含兼职、合同和Telehealth岗"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 900,  "note": "偏诊所合伙人和医疗管理岗"},
]
SALARIES = [
    {"experience": "住院医/培训期GP（Registrar）", "salary_min": 85000, "salary_max": 130000, "salary_note": "RACGP培训期，已含奖金，农村培训享额外补贴", "sort_order": 0},
    {"experience": "初级GP（FRACGP后 1~3年）", "salary_min": 180000, "salary_max": 280000, "salary_note": "按诊疗量计费（Billings），首年通常约 $200k", "sort_order": 1},
    {"experience": "中级GP（3~8年）", "salary_min": 250000, "salary_max": 380000, "salary_note": "PayScale 平均 $132,103（基本薪），实际含 Medicare billings 约 $250k~$380k", "sort_order": 2},
    {"experience": "资深GP / 诊所合伙人（8年+）", "salary_min": 350000, "salary_max": 500000, "salary_note": "持股诊所收益叠加，高产GP年收入可超 $500k", "sort_order": 3},
    {"experience": "农村/偏远地区GP（DWS区域）", "salary_min": 280000, "salary_max": 450000, "salary_note": "政府 RHOSP/RDA 补贴 $60,000~$120,000+/年，实际收入显著高于城市", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，医生为核心短缺岗位，常由医院或诊所担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，医生通常较快获批", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，农村GP享优先提名", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，农村GP额外政府补贴", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "医学学位+AMC考试+Fellowship，总培训约10~12年"},
    {"dimension": "learning_duration",        "label_zh": "极长", "stars": 5, "note": "从医学学位到独立全科执业约10~14年"},
    {"dimension": "certification_difficulty", "label_zh": "极高", "stars": 5, "note": "AMC临床考试通过率约60%，RACGP Fellowship考核严格"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "全国GP短缺7,000人（2030年预测），农村地区尤为严峻"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "GP极度供不应求，通过AMC后诊所主动招募"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 5, "note": "高强度工作，每日20~30名患者，行政和文书负担重"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "成熟GP年收入 $250k~$500k+，农村GP可超 $450k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "GP短缺将持续20年以上，Telehealth和慢性病管理创造新需求"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助诊断快速发展，但医生判断、患者沟通和责任承担无法替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，农村GP享PR快速通道和政府补贴双重优惠"},
    {"dimension": "pr_difficulty",            "label_zh": "较高", "stars": 4, "note": "AMC考试难度高，Fellowship周期长，总体认证流程是医疗类最复杂的"},
]
SUITABILITY_FIT = ["已持有国内医生执照（5年制临床医学本科以上），希望来澳执业", "英语能力优秀（AMC临床考试全英语，OET A级或IELTS 7.5+）", "接受农村/偏远地区就业以快速获取PR和额外补贴", "有耐心完成较长认证流程（AMC+Fellowship 约3~5年）", "家庭支持农村生活或对澳洲医疗体系有浓厚兴趣"]
SUITABILITY_UNFIT = ["英语能力较弱，短期无法达到AMC临床考试要求", "期望1~2年内快速取得执业资格", "无法接受农村偏远地区就业（城市竞争更激烈）"]
SOURCES = [
    {"source_name": "AHPRA", "content": "医生注册要求和海外医生互认流程", "url": "https://www.ahpra.gov.au/Registration/Applying-for-registration.aspx"},
    {"source_name": "Australian Medical Council (AMC)", "content": "海外医学毕业生评估和AMC考试", "url": "https://www.amc.org.au/"},
    {"source_name": "RACGP", "content": "全科医生Fellowship培训计划", "url": "https://www.racgp.org.au/"},
    {"source_name": "PayScale AU", "content": "全科医生平均薪资 $132,103（基本薪，2026）", "url": "https://www.payscale.com/research/AU/Job=General_Practitioner/Salary"},
    {"source_name": "Department of Health", "content": "DWS农村医生补贴政策", "url": "https://www.health.gov.au/topics/doctors/rural-programs"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲全科医生工资多少？", "answer": "成熟GP年收入（含Medicare billings）约 $250,000~$500,000+；农村GP额外政府补贴 $60,000~$120,000+。是所有职业中薪资最高的类别之一。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲全科医生容易找工作吗？", "answer": "极容易。全国GP短缺预计2030年达7,000人，通过AMC评估后诊所和医院会主动联系，农村地区基本可立即入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国医生执照澳洲认可吗？", "answer": "通过AMC（澳洲医学委员会）考试评估，主要包括笔试（MCQ）和临床考试（OSCE）两部分，总费用约 $5,000~$8,000，通过率约 60%。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "全科医生会被AI替代吗？", "answer": "短期内风险较低。AI辅助诊断（如皮肤癌筛查）快速发展，但医患沟通、综合判断和法律责任承担是AI无法替代的核心价值。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲全科医生有年龄限制吗？", "answer": "无执业年龄上限，但移民打分45岁以上无加分。建议35~42岁的医生尽快启动AMC申请，完成Fellowship后仍有15~20年高薪执业年限。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲全科医生需要什么学历？", "answer": "需要医学学士学位（MBBS或MD，通常5年制）。国内临床医学（5年制）毕业可申请AMC评估，通过后取得AHPRA注册。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲全科医生认证难吗？", "answer": "是所有职业中认证流程最复杂的之一。AMC MCQ+临床考试+AHPRA注册+RACGP Fellowship，总周期约3~5年，但每一步都有清晰的路径和支持资源。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "全科医生和注册护士哪个更适合技术移民澳洲？", "answer": "护士PR路径更快捷简单（无需AMC），3~12个月可取得注册；医生认证流程复杂但薪资远高于护士（$250k~$500k+ vs $80k~$120k）。有医生执照者首选医生路径，有护理背景者走护士路径效率更高。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 全科医生数据入库完成")

if __name__ == "__main__":
    run()
