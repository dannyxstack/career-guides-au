"""澳洲药剂师（251511）数据入库。数据来源：JSA、AHPRA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "251511", "anzsco_title": "Pharmacist",
    "category": "医疗健康", "workforce_size": 32000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Community Pharmacy","Hospital Clinical Pharmacy","Aged Care Pharmacy","Pharmacist Prescriber (Expanded Role)","Rural & Remote Pharmacy"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "药剂师",
    "summary": "药剂师负责配发药物、提供用药咨询和开展药物管理，服务于社区药房、医院、老年护理和诊所。澳大利亚药剂师执业范围持续扩大（包括疫苗接种和有限处方权），需求稳定且PR路径清晰。",
    "forecast_note": "JSA 预测药剂师至2035年就业增长约10%。老年护理强制配药审查和药剂师新扩展角色（包括初级护理处方权）持续推高需求。",
    "trend_summary": "药剂师处方权扩展（如口服避孕药、部分抗生素）是行业最大变革，增加了药剂师的就业价值。远程药剂服务和老年护理配药审查是增长方向。",
}
I18N_EN = {
    "locale": "en", "name": "Pharmacist",
    "summary": "Pharmacists dispense medications, provide medication counselling and conduct medication management reviews in community pharmacies, hospitals, aged care and clinics. Expanded prescribing roles are increasing their value.",
    "forecast_note": "JSA projects ~10% employment growth for pharmacists by 2035. Aged care mandatory medication reviews and expanded prescribing authority sustain demand.",
    "trend_summary": "Pharmacist prescribing expansion (oral contraceptives, some antibiotics) is the key industry change. Telepharmacy and aged care medication management are growth areas.",
}
EDUCATION = [
    {"stage": "Bachelor of Pharmacy / Master of Pharmacy（4~5年）", "duration": "4~5年（全日制）", "cost_min": 30000, "cost_max": 180000, "cost_note": "国内留学生约 $35,000~$40,000/年；政府补贴名额约 $7,000~$9,000/年", "sort_order": 0},
    {"stage": "海外资历评估（APC + AHPRA注册）", "duration": "6~18个月", "cost_min": 2000, "cost_max": 6000, "cost_note": "含 Australian Pharmacy Council 评估费、OET/IELTS和AHPRA注册费", "sort_order": 1},
    {"stage": "实习年（Intern Training Program）", "duration": "1年（有薪）", "cost_min": 0, "cost_max": 500, "cost_note": "在澳完成1年有薪实习后方可独立注册执业", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Pharmacy / Master of Pharmacy", "issuer": "认可大学", "note": "AHPRA注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Pharmacy Registration", "issuer": "AHPRA", "note": "全国统一药剂师注册，无此注册不得执业", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "APC（Australian Pharmacy Council）评估", "issuer": "Australian Pharmacy Council", "note": "海外药剂师必须，评估学历是否达到澳洲标准", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Immunisation Certificate（疫苗接种资质）", "issuer": "认可RTO", "note": "社区药剂师通常需持有，扩展执业范围", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 2800, "note": "全国，含社区药房、医院、老年护理和农村岗"},
    {"platform": "Indeed",   "count_min": 900,  "count_max": 1800, "note": "含兼职、合同和夜班"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 900,  "note": "偏医院临床药师和管理岗"},
]
SALARIES = [
    {"experience": "实习药剂师（Intern）", "salary_min": 50000, "salary_max": 65000, "salary_note": "全薪实习，各州略有差异", "sort_order": 0},
    {"experience": "初级药剂师（注册后 1~3年）", "salary_min": 75000, "salary_max": 92000, "salary_note": "社区药房，含 Pharmacy Award 基本薪", "sort_order": 1},
    {"experience": "中级药剂师（3~8年）", "salary_min": 92000, "salary_max": 115000, "salary_note": "SEEK 区间 $65k~$130k（广，含兼职）；Indeed 平均约 $90k；精英机构薪资约 $97,475", "sort_order": 2},
    {"experience": "资深药剂师 / 医院主任（8年+）", "salary_min": 115000, "salary_max": 145000, "salary_note": "医院高级临床药师和药房主任薪资较高", "sort_order": 3},
    {"experience": "农村/偏远地区药剂师", "salary_min": 100000, "salary_max": 140000, "salary_note": "偏远地区津贴和政府补贴推高实际收入", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，药剂师为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，农村药剂师享优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "药理学、临床药学和用药咨询要求较高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学位4~5年+实习1年+APC评估约6个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "APC评估和实习年是主要门槛，非考试制"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，老年护理和处方扩权持续推高需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，持证后通常可快速入职"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "工作环境相对舒适（室内），夜班主要在24小时药房"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位数约 $90k~$115k；医院临床药师和农村岗薪资更高"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 4, "note": "处方权扩展和老年护理需求持续推高药剂师职业价值"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "自动配药机在医院已应用，但药物咨询和临床审查仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，189/190/491/482多路径，农村药剂师PR优先"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "APC评估和实习年周期约1~2年，但有清晰路径"},
]
SUITABILITY_FIT = ["已持有国内药学学位（4~5年制，药学本科以上）", "英语能力达到或接近 OET B / IELTS 7.0", "接受1年有薪实习和农村就业以快速获取PR", "对用药咨询和患者教育有热情", "目标是医院临床药师或自营社区药房"]
SUITABILITY_UNFIT = ["英语能力较弱，短期无法达到AHPRA注册要求", "无法接受农村派驻（城市药剂师竞争更激烈）", "期望立即高薪（实习年薪资相对较低）"]
SOURCES = [
    {"source_name": "AHPRA", "content": "药剂师注册要求和海外互认流程", "url": "https://www.ahpra.gov.au/"},
    {"source_name": "Australian Pharmacy Council", "content": "海外药剂师学历评估", "url": "https://www.pharmacycouncil.org.au/"},
    {"source_name": "Indeed AU", "content": "药剂师薪资数据（2026）", "url": "https://au.indeed.com/career/pharmacist/salaries"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲药剂师工资多少？", "answer": "中级药剂师年薪约 $92,000~$115,000；医院主任药师约 $115k~$145k；农村地区含补贴约 $100k~$140k。实习药剂师约 $50k~$65k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲药剂师容易找工作吗？", "answer": "容易。MLTSSL在列，Seek 挂牌 1,500~2,800 个职位，处方扩权政策推高药剂师价值，农村地区几乎可立即入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国药学学位澳洲认可吗？", "answer": "通过 APC（澳洲药学委员会）评估，确认学历达到澳洲标准后申请AHPRA注册，并完成1年有薪实习。总周期约6~18个月。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "药剂师会被AI替代吗？", "answer": "部分替代，但整体风险偏低。自动配药机和AI处方审查已广泛应用，但用药咨询、慢性病管理和患者教育仍需人工。处方扩权反而增加了药剂师的不可替代性。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲药剂师有年龄限制吗？", "answer": "无执业年龄上限。35~45岁来澳注册的海外药剂师案例很多，移民打分45岁以上无加分，建议尽早启动。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲药剂师需要什么学历？", "answer": "需要药学学位（4~5年制）。国内药学本科（4年制）可申请APC评估，部分情况需补修学分。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲药剂师认证难吗？", "answer": "难度中等。主要是APC学历评估和1年有薪实习，没有像AMC/ADC那样的高难度资格考试，相对医生和牙医的认证更容易。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "药剂师和注册护士哪个更适合技术移民澳洲？", "answer": "护士就业量更大（Seek ~10,000+ vs 药剂师 ~2,500），两者PR路径相近。药剂师工作环境更舒适（室内），薪资相近但护士有更多农村偏远地区机会。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 药剂师数据入库完成")

if __name__ == "__main__":
    run()
