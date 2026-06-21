"""澳洲建筑师（232111）数据入库。数据来源：JSA、SEEK、Indeed、AACA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "232111", "anzsco_title": "Architect",
    "category": "IT/工程", "workforce_size": 22000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Sustainable & Green Architecture","Social & Affordable Housing","Healthcare & Education Facilities","Urban Regeneration & Mixed-Use Development","Parametric Design & BIM Technology"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "建筑师",
    "summary": "建筑师规划和设计建筑物、城市综合体和基础设施，覆盖住宅、商业、工业和政府设施。澳洲住房危机（各州政府建设目标）和可持续建筑需求推动工作量持续增加，是设计类职业中移民友好度最高的职业之一。",
    "forecast_note": "JSA 预测建筑师至2035年就业增长约8%。各州政府社会住房计划（NSW/VIC/QLD各州均有10年建设目标）是主要驱动力。",
    "trend_summary": "参数化设计（Grasshopper/Rhino）和BIM（建筑信息模型，Revit）是2025-2026年薪资溢价最高的技能方向。可持续设计（绿色建筑/碳中和设计）资质显著提升竞争力。",
}
I18N_EN = {
    "locale": "en", "name": "Architect",
    "summary": "Architects plan and design buildings, urban developments and infrastructure across residential, commercial, industrial and government sectors. Australia's housing crisis and sustainable construction demand are driving sustained workload growth.",
    "forecast_note": "JSA projects ~8% employment growth for architects by 2035. State government social housing programs (NSW/VIC/QLD all have 10-year construction targets) are the primary demand driver.",
    "trend_summary": "Parametric design (Grasshopper/Rhino) and BIM (Revit) command the highest salary premiums in 2025-2026. Sustainable design credentials (green building/carbon-neutral design) significantly enhance competitiveness.",
}
EDUCATION = [
    {"stage": "Bachelor + Master of Architecture（5~6年）", "duration": "5~6年（全日制）", "cost_min": 40000, "cost_max": 250000, "cost_note": "澳洲建筑师注册要求：5年专业学位（AACA认证的Bachelors+Masters路径）", "sort_order": 0},
    {"stage": "两年实习记录（Graduate Experience Record）", "duration": "2年有监督的实践经验", "cost_min": 0, "cost_max": 0, "cost_note": "毕业后在注册建筑师监督下完成AACA规定的实践能力记录", "sort_order": 1},
    {"stage": "AACA架构师认证考试（APE）", "duration": "6~12个月准备", "cost_min": 1500, "cost_max": 4000, "cost_note": "澳洲建筑师注册的最终考试，通过后可在各州建筑师委员会注册", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "AACA认证建筑学位（Bachelor+Master of Architecture）", "issuer": "AACA认证大学", "note": "澳洲建筑师注册的基础学历要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AACA APE（Architectural Practice Exam）", "issuer": "Architects Accreditation Council of Australia", "note": "建筑师注册必须通过的专业实践考试", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "各州建筑师委员会注册（e.g. Architects Board WA）", "issuer": "各州建筑师委员会", "note": "州注册是独立执业和使用「建筑师」职称的法律要求", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Green Star AP / LEED AP（可持续建筑认证）", "issuer": "GBCA / USGBC", "note": "可持续建筑认证，显著提升政府和商业项目竞争力", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 800,  "count_max": 2000, "note": "全国，含注册建筑师、建筑设计师、项目建筑师和BIM专员岗"},
    {"platform": "Indeed",   "count_min": 600,  "count_max": 1500, "note": "含住宅、商业和政府项目建筑师岗"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 2500, "note": "大型建筑设计公司直招"},
]
SALARIES = [
    {"experience": "建筑师助理（毕业~注册前）", "salary_min": 60000, "salary_max": 82000, "salary_note": "注册前的实习阶段，需要2年实践记录", "sort_order": 0},
    {"experience": "注册建筑师（3~8年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "SEEK 区间 $90k~$110k；Indeed 平均 $92,411（2026）", "sort_order": 1},
    {"experience": "高级/项目建筑师（8~15年）", "salary_min": 115000, "salary_max": 155000, "salary_note": "BIM专精和可持续设计资质提升薪资竞争力", "sort_order": 2},
    {"experience": "合伙人 / 设计总监（15年+）", "salary_min": 155000, "salary_max": 270000, "salary_note": "设计事务所合伙人和大型开发商设计总监，Indeed 高端 $169k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，建筑师为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "AACA技能评估+EOI，邀请制", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NSW/VIC/QLD住房项目多", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区建筑岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "很高", "stars": 4, "note": "5~6年专业学位+2年实习+APE考试，是澳洲最长的专业学习路径之一"},
    {"dimension": "learning_duration",        "label_zh": "很长", "stars": 5, "note": "学位5~6年+实习2年+考试=总周期约8~10年"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "APE考试通过率约70~80%，需要系统准备"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "住房危机推高需求，但职业总人数较少（约22,000人）"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "注册建筑师竞争相对温和；初级未注册者竞争激烈"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "截止期密集，设计审查和客户沟通强度高"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "注册后约 $90k~$115k，高级约 $115k~$155k，与学习周期相比回报中等"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "住房危机提供短期需求，长期受建筑业周期性影响"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI生成设计方案，但创意决策、客户沟通和法规合规判断不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "MLTSSL在列，但AACA评估周期长且要求高；职位数少于工程类"},
    {"dimension": "pr_difficulty",            "label_zh": "较高", "stars": 4, "note": "AACA评估严格，需要提供详细学历和实践证明，周期6~18个月"},
]
SUITABILITY_FIT = ["持有建筑学本科+硕士学历（AACA认证路径或海外同等学历）", "有注册建筑师实践经验（2年以上有监督），英语能力强", "熟悉Revit/BIM和可持续设计（Green Star/LEED加分项）", "英语能力达到 IELTS 7.0+（建筑师客户沟通要求高）", "目标是住宅开发或政府项目（需求最旺盛的方向）"]
SUITABILITY_UNFIT = ["学历周期不够（5年以上才能满足AACA评估）", "英语能力较弱，无法胜任设计汇报和客户沟通", "不接受较长的注册前实习阶段（薪资偏低）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "建筑师薪资 $90k~$110k（2026）", "url": "https://au.seek.com/career-advice/role/architect/salary"},
    {"source_name": "Indeed AU", "content": "建筑师平均薪资 $92,411；高端 $169,000（2026）", "url": "https://au.indeed.com/career/architect/salaries"},
    {"source_name": "AACA（Architects Accreditation Council of Australia）", "content": "建筑师学历评估和APE考试", "url": "https://www.aaca.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲建筑师工资多少？", "answer": "注册建筑师约 $85,000~$115,000（Indeed均值 $92,411）；高级/项目建筑师约 $115k~$155k；设计总监/合伙人约 $155k~$270k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲建筑师容易找工作吗？", "answer": "中等难度。Seek 挂牌约 800~2000 个职位，住房危机推高需求，但注册前实习期岗位竞争较激烈。注册建筑师+BIM/可持续设计技能者供不应求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国建筑学学历澳洲认可吗？", "answer": "通过 AACA（Architects Accreditation Council of Australia）技能评估，周期约6~18个月，费用约 $770~$1,500。中国顶尖建筑院校（同济/清华/东南大学）的学历通常能通过AACA评估，但需要详细课程证明。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "建筑师会被AI替代吗？", "answer": "风险中等。AI辅助生成方案和BIM协调，但创意设计决策、客户关系管理和建筑法规合规判断需要注册建筑师负责，不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲建筑师有年龄限制吗？", "answer": "无。有丰富商业/政府项目经验的资深建筑师（40~55岁）在大型开发商和设计事务所备受青睐。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲建筑师需要什么学历？", "answer": "必须持有AACA认证的5年建筑学专业学位（Bachelor+Master路径），再加2年实践+APE考试，才能正式注册为注册建筑师。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲建筑师认证（移民）难吗？", "answer": "难度中高。AACA评估比EA（工程师）严格，周期较长；APE考试需要系统准备。但住房危机推高了雇主担保482签证的机会。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "建筑师和土木工程师哪个更适合移民澳洲？", "answer": "土木工程师就业量更大（Seek ~4000 vs 建筑师 ~1000），薪资相当，EA评估比AACA更简单。建筑师创意成分更高，适合设计型人才；土木工程师技术性更强，移民路径更顺畅。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 建筑师数据入库完成")

if __name__ == "__main__":
    run()
