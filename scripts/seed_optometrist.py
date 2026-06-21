"""澳洲验光师（251411）数据入库。数据来源：JSA、AHPRA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "251411", "anzsco_title": "Optometrist",
    "category": "医疗健康", "workforce_size": 8000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Therapeutic Optometry (Prescribing)","Myopia Control & Paediatric Optometry","Rural & Remote Eye Care","Aged Care Eye Health","Telehealth & Remote Optometry"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "验光师",
    "summary": "验光师检查和评估视觉系统，开具眼镜/隐形眼镜处方，并诊断和管理眼部疾病（治疗性验光）。澳大利亚验光师执业范围持续扩大（处方滴眼液权限），是从业人数少、收入高且PR友好的医疗职业。",
    "forecast_note": "JSA 预测验光师至2035年就业增长约15%。人口老龄化（白内障、黄斑变性增加）、青少年近视流行和治疗性验光执业范围扩大是主要驱动力。",
    "trend_summary": "治疗性验光（含处方滴眼液权限）在全国各州普及，大幅提升验光师的诊疗价值。农村眼科服务严重短缺，验光师享PR快速通道。",
}
I18N_EN = {
    "locale": "en", "name": "Optometrist",
    "summary": "Optometrists examine and assess the visual system, prescribe glasses/contact lenses and diagnose/manage eye diseases (therapeutic optometry). With therapeutic prescribing rights expanding nationally, optometrists are increasingly valuable.",
    "forecast_note": "JSA projects ~15% employment growth for optometrists by 2035. Ageing population (cataracts, macular degeneration), myopia epidemic and therapeutic scope expansion are key drivers.",
    "trend_summary": "Therapeutic optometry (prescribing eye drops) is now available nationally, significantly increasing optometrist clinical value. Rural eye care faces critical shortages.",
}
EDUCATION = [
    {"stage": "Bachelor of Optometry / Master of Optometry（4~5年）", "duration": "4~5年（全日制）", "cost_min": 25000, "cost_max": 200000, "cost_note": "澳洲国际生约 $40,000~$48,000/年；政府补贴名额约 $8,000~$10,000/年", "sort_order": 0},
    {"stage": "海外资历评估（OBA + AHPRA注册）", "duration": "6~18个月", "cost_min": 2000, "cost_max": 7000, "cost_note": "含 Optometry Board of Australia 评估和AHPRA注册费", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor/Master of Optometry", "issuer": "认可大学", "note": "AHPRA注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Optometrist Registration", "issuer": "AHPRA / Optometry Board of Australia", "note": "全国统一注册，无此注册不得执业", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Therapeutic Endorsement（治疗性验光认证）", "issuer": "AHPRA / Optometry Board", "note": "全国各州现已普及，增强诊疗权限", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 400,  "count_max": 900,  "note": "全国，含眼镜零售连锁、独立诊所、医院和农村岗"},
    {"platform": "Indeed",   "count_min": 250,  "count_max": 600,  "note": "含兼职和合同工"},
    {"platform": "LinkedIn", "count_min": 100,  "count_max": 300,  "note": "偏诊所合伙人和眼科连锁管理岗"},
]
SALARIES = [
    {"experience": "新注册验光师（0~2年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "眼镜零售连锁（OPSM/Specsavers），含基本薪", "sort_order": 0},
    {"experience": "中级验光师（2~8年）", "salary_min": 95000, "salary_max": 125000, "salary_note": "Indeed 平均 $106,055；SEEK 区间 $90k~$125k（2026）", "sort_order": 1},
    {"experience": "资深验光师 / 诊所主任（8年+）", "salary_min": 125000, "salary_max": 175000, "salary_note": "独立诊所持股或主任职位，薪资显著提升", "sort_order": 2},
    {"experience": "农村/偏远地区验光师", "salary_min": 110000, "salary_max": 165000, "salary_note": "农村眼科服务极度短缺，津贴和签约奖金显著", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，验光师为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，农村眼科服务优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区眼科服务，提名加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "视觉光学、眼部解剖和临床诊断综合要求高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学位4~5年+OBA评估约6~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "OBA评估主要是学历审核，不需要高难度临床考试"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "从业人数少（约8,000），老龄化和近视流行双重驱动"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "供不应求，特别是农村眼科服务极度短缺"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "工作环境舒适（室内），无夜班，工作节奏规律"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中位数约 $95k~$125k，Indeed平均$106k；农村津贴更高"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 4, "note": "老龄化、近视流行和治疗性验光扩权三重驱动"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI眼底扫描诊断辅助发展快，但验光测量和处方开具仍需执照"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，189/190/491/482多路径，农村优先"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "OBA评估和OET英语是主要门槛，周期约6~18个月"},
]
SUITABILITY_FIT = ["已持有国内眼视光学/验光配镜学位（4~5年制）", "英语能力达到 OET B / IELTS 7.0", "接受农村就业以快速获取PR和额外补贴", "对眼科诊断和视觉健康管理有深厚兴趣", "目标是独立验光诊所合伙人或农村眼科服务"]
SUITABILITY_UNFIT = ["英语能力较弱，OBA评估困难", "无法接受农村派驻", "只想从事纯配镜零售（澳洲更重视临床诊断）"]
SOURCES = [
    {"source_name": "AHPRA / Optometry Board", "content": "验光师注册和治疗性认证要求", "url": "https://www.optometryboard.gov.au/"},
    {"source_name": "Indeed AU", "content": "验光师平均薪资 $106,055（2026）", "url": "https://au.indeed.com/career/optometrist/salaries"},
    {"source_name": "Optometry Australia", "content": "验光师行业协会和职业发展", "url": "https://www.optometry.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲验光师工资多少？", "answer": "中级验光师年薪约 $95,000~$125,000（Indeed平均$106,055）；资深验光师/诊所主任约 $125k~$175k；农村地区含补贴约 $110k~$165k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲验光师容易找工作吗？", "answer": "容易。从业人数仅约8,000，农村眼科服务极度短缺，持证后几乎立即入职，Specsavers等连锁集团主动招募海外验光师。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国验光学位澳洲认可吗？", "answer": "通过 OBA（澳洲验光委员会）学历评估，确认标准后申请AHPRA注册。主要门槛是英语成绩（OET B/IELTS 7.0+）。部分顶尖院校（如中山大学）的眼视光专业评估较容易通过。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "验光师会被AI替代吗？", "answer": "替代风险较低。AI眼底扫描诊断（如糖尿病视网膜病变筛查）发展迅速，但处方开具、接触镜适配和患者咨询仍需执照。治疗性验光扩权反而增加了验光师价值。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲验光师有年龄限制吗？", "answer": "无执业年龄上限。工作环境舒适，无夜班，对年龄无明显限制，是医疗类职业中工作强度最低的之一。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲验光师需要什么学历？", "answer": "需要眼视光学位（Bachelor/Master of Optometry，4~5年制）。国内眼视光学/验光配镜本科（4~5年制）可申请OBA评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲验光师认证难吗？", "answer": "难度中等。OBA评估主要是学历审核，不需要像牙医ADC那样的高难度临床考试。英语是最主要门槛。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "验光师和牙医哪个更适合移民澳洲？", "answer": "验光师从业人数更少（~8,000 vs ~18,000），供需缺口相近；牙医薪资更高（$130k~$220k vs $95k~$125k），但ADC临床考试更难。验光师工作强度低、无夜班，整体生活质量更高。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 验光师数据入库完成")

if __name__ == "__main__":
    run()
