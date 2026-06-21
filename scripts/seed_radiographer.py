"""澳洲放射技师（251211）数据入库。数据来源：JSA、AHPRA、SEEK、AIR（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "251211", "anzsco_title": "Medical Diagnostic Radiographer",
    "category": "医疗健康", "workforce_size": 16000, "shortage_listed": 1,
    "growth_areas": json.dumps(["CT & MRI Advanced Imaging","Interventional Radiology","Nuclear Medicine & PET","Rural & Remote Radiology","AI-Assisted Medical Imaging"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "放射技师",
    "summary": "放射技师操作X射线、CT、MRI、超声和核医学设备，为医疗诊断提供影像服务。澳大利亚放射影像技术持续升级（AI辅助诊断），需求稳定且PR路径清晰，是MLTSSL在列的紧缺职业。",
    "forecast_note": "JSA 预测放射技师至2035年就业增长约12%。CT/MRI检查量增加（慢性病筛查和癌症诊断）和人口老龄化是主要驱动力。",
    "trend_summary": "AI辅助影像诊断快速发展（如乳腺癌AI筛查），但放射技师的设备操作和患者管理职能不受影响。PET/CT和介入放射治疗是薪资溢价最高的专科方向。",
}
I18N_EN = {
    "locale": "en", "name": "Medical Diagnostic Radiographer",
    "summary": "Radiographers operate X-ray, CT, MRI, ultrasound and nuclear medicine equipment to produce diagnostic medical images. Stable demand with MLTSSL listing and clear PR pathways.",
    "forecast_note": "JSA projects ~12% employment growth for radiographers by 2035. Rising CT/MRI volume (chronic disease screening and cancer diagnostics) and population ageing are the main drivers.",
    "trend_summary": "AI-assisted imaging diagnostics are expanding, but radiographer technical and patient-care roles remain essential. PET/CT and interventional radiology carry salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of Medical Radiation Science（3~4年）", "duration": "3~4年（全日制）", "cost_min": 25000, "cost_max": 140000, "cost_note": "澳洲国际生约 $35,000~$40,000/年；政府补贴名额约 $6,000~$8,000/年", "sort_order": 0},
    {"stage": "海外资历评估（MRPAS + AHPRA注册）", "duration": "6~12个月", "cost_min": 1500, "cost_max": 5000, "cost_note": "含 Medical Radiation Practice Accreditation Board 评估和AHPRA注册费", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Medical Radiation Science", "issuer": "认可大学", "note": "AHPRA注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Medical Radiation Practitioner Registration", "issuer": "AHPRA", "note": "全国统一注册，无此注册不得操作放射设备", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "MRPAB评估（Medical Radiation Practice Accreditation）", "issuer": "MRPAB", "note": "海外放射技师学历评估", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "PET/CT 或 MRI 专科资质", "issuer": "AIR（Australian Institute of Radiography）", "note": "核医学和专科影像方向进阶资质", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600,  "count_max": 1200, "note": "全国，含医院、私立影像中心、农村和核医学岗"},
    {"platform": "Indeed",   "count_min": 350,  "count_max": 750,  "note": "含兼职和合同工"},
    {"platform": "LinkedIn", "count_min": 150,  "count_max": 400,  "note": "偏专科和管理岗"},
]
SALARIES = [
    {"experience": "新注册放射技师（0~2年）", "salary_min": 68000, "salary_max": 82000, "salary_note": "医院或影像中心，含基本薪", "sort_order": 0},
    {"experience": "中级放射技师（2~8年）", "salary_min": 82000, "salary_max": 108000, "salary_note": "SEEK 区间 $95k~$110k；ERI SalaryExpert 约 $95k（2026）", "sort_order": 1},
    {"experience": "资深/专科放射技师（8年+）", "salary_min": 108000, "salary_max": 140000, "salary_note": "PET/CT、介入放射和核医学专科薪资较高", "sort_order": 2},
    {"experience": "农村/偏远地区放射技师", "salary_min": 90000, "salary_max": 125000, "salary_note": "农村影像服务短缺，偏远地区津贴显著", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，放射技师为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，农村放射技师享优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区医疗，提名加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "解剖学、放射物理和设备操作综合要求较高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 3, "note": "学位3~4年+MRPAB评估约6~12个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "MRPAB评估主要是学历审核，非高难度考试"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "CT/MRI检查量持续增加，MLTSSL在列"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，持证后通常可较快入职"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "放射防护规范严格，工作相对规律（无夜班急诊较少）"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位数约 $82k~$108k；专科方向（PET/CT）薪资更高"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 4, "note": "AI辅助诊断扩大了影像科的工作量，而非减少"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI影像诊断读片已商业化，但技师的设备操作和患者管理不受影响"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，189/190/491/482多路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "MRPAB评估和OET英语是主要门槛，周期约6~12个月"},
]
SUITABILITY_FIT = ["已持有国内放射/医学影像技术学位（3~4年制）", "英语能力达到 OET B / IELTS 7.0", "对医学影像技术和设备有浓厚兴趣", "接受农村/偏远地区就业以快速获取PR", "目标是PET/CT、核医学或介入放射专科方向"]
SUITABILITY_UNFIT = ["对放射防护要求感到不适或担忧", "英语能力较弱，MRPAB评估困难", "不适应固定轮班工作（含周末和夜班）"]
SOURCES = [
    {"source_name": "AHPRA", "content": "放射技师注册要求", "url": "https://www.ahpra.gov.au/"},
    {"source_name": "AIR（Australian Institute of Radiography）", "content": "放射技师行业协会和继续教育", "url": "https://www.air.asn.au/"},
    {"source_name": "SEEK AU", "content": "放射技师薪资区间 $95k~$110k（2026）", "url": "https://www.seek.com.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲放射技师工资多少？", "answer": "中级放射技师年薪约 $82,000~$108,000（SEEK区间$95k~$110k）；专科放射技师（PET/CT/核医学）约 $108k~$140k；农村地区含补贴约 $90k~$125k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲放射技师容易找工作吗？", "answer": "容易。CT/MRI检查量持续增加，MLTSSL在列，Seek 挂牌 600~1,200 个职位，农村影像服务严重短缺，持证后较快入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国放射技师资质澳洲认可吗？", "answer": "通过 MRPAB（医学放射实践认证委员会）学历评估，确认标准后申请AHPRA注册。主要门槛是英语成绩（OET B/IELTS 7.0+）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "放射技师会被AI替代吗？", "answer": "部分读片职能有AI渗透，但AI辅助诊断扩大了影像检查量（更多患者接受筛查），整体增加了放射技师需求。设备操作和患者管理职能无法被AI替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲放射技师有年龄限制吗？", "answer": "无执业年龄上限。放射防护规范保护从业者，长期职业健康风险可控。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲放射技师需要什么学历？", "answer": "需要医学放射科学学位（Bachelor of Medical Radiation Science，3~4年制）。国内医学影像技术专科（3~4年制）可申请MRPAB评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲放射技师认证难吗？", "answer": "难度中等。MRPAB评估主要是学历审核，不需要高难度临床考试。英语（OET B/IELTS 7.0+）是最主要门槛。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "放射技师和注册护士哪个更适合技术移民澳洲？", "answer": "护士就业量更大（Seek ~10,000+ vs 放射技师 ~1,000），薪资相近。放射技师工作相对规律（更少夜班急诊），专科方向薪资溢价明显。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 放射技师数据入库完成")

if __name__ == "__main__":
    run()
