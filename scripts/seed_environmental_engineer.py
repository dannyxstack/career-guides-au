"""澳洲环境工程师（233915）数据入库。数据来源：JSA、SEEK、Indeed、Engineers Australia（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "233915", "anzsco_title": "Environmental Engineer",
    "category": "IT/工程", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Climate Change Adaptation & Infrastructure Resilience","Renewable Energy Environmental Assessment","Mine Rehabilitation & Acid Drainage Management","Water Treatment & Circular Economy","ESG Compliance & Environmental Reporting"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "环境工程师",
    "summary": "环境工程师评估和减轻工程项目对环境的影响，负责水处理、废物管理、污染修复、环境影响评估（EIA）和气候变化适应工程。澳洲可再生能源转型、矿山修复义务和ESG监管趋严驱动需求增长，是最契合澳洲可持续发展战略的工程职业。",
    "forecast_note": "JSA 预测环境工程师至2035年就业增长约12%。联邦气候行动立法（Carbon Neutral 2050目标）和矿山关闭修复义务是主要驱动力。",
    "trend_summary": "ESG合规报告和气候风险评估是2025-2026年增长最快的环境工程子领域，资产管理公司和矿业公司对此需求急剧增加。水务环境工程（净水/污水）是稳定的常绿方向。",
}
I18N_EN = {
    "locale": "en", "name": "Environmental Engineer",
    "summary": "Environmental engineers assess and mitigate environmental impacts of engineering projects, covering water treatment, waste management, contamination remediation, environmental impact assessment (EIA) and climate change adaptation engineering.",
    "forecast_note": "JSA projects ~12% employment growth for environmental engineers by 2035. Federal climate action legislation (Carbon Neutral 2050) and mine closure rehabilitation obligations are the primary drivers.",
    "trend_summary": "ESG compliance reporting and climate risk assessment are the fastest-growing sub-disciplines in 2025-2026. Water engineering (potable/wastewater) is a stable evergreen direction.",
}
EDUCATION = [
    {"stage": "Bachelor of Environmental Engineering（荣誉，4年）", "duration": "4年（全日制）", "cost_min": 30000, "cost_max": 185000, "cost_note": "或 Civil/Chemical Engineering + 环境专业方向；4年荣誉学位是EA评估要求", "sort_order": 0},
    {"stage": "Engineers Australia（EA）技能评估", "duration": "3~12个月", "cost_min": 770, "cost_max": 3000, "cost_note": "189/190签证必须，约 $770 申请费", "sort_order": 1},
    {"stage": "CPEng（Chartered Professional Engineer）", "duration": "4~7年工作经验后申请", "cost_min": 1500, "cost_max": 5000, "cost_note": "高级环境工程师的专业注册认证", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Environmental Engineering (Honours)", "issuer": "认可大学（EA认证）", "note": "4年荣誉环境工程学位是EA评估的基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Engineers Australia（EA）技能评估", "issuer": "Engineers Australia", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPEng（Chartered Professional Engineer）", "issuer": "Engineers Australia", "note": "环境工程高级岗和独立执业的重要资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Green Star AP / LEED AP", "issuer": "GBCA / USGBC", "note": "可持续建筑和绿色项目认证，环境工程师的加分项", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600,  "count_max": 1800, "note": "全国，含环境工程师、EIA顾问、水务工程师和矿山修复工程师岗"},
    {"platform": "Indeed",   "count_min": 400,  "count_max": 1200, "note": "含政府环保机构和顾问公司岗"},
    {"platform": "LinkedIn", "count_min": 800,  "count_max": 2000, "note": "ESG顾问公司和资源企业直招"},
]
SALARIES = [
    {"experience": "毕业生环境工程师（0~2年）", "salary_min": 65000, "salary_max": 82000, "salary_note": "应届生起薪", "sort_order": 0},
    {"experience": "中级环境工程师（2~7年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "SEEK 区间 $95k~$115k；Indeed 平均 $94,387（2026）", "sort_order": 1},
    {"experience": "高级环境工程师（7~15年，CPEng）", "salary_min": 115000, "salary_max": 155000, "salary_note": "ESG/气候顾问专精薪资溢价明显", "sort_order": 2},
    {"experience": "环境总监 / ESG负责人（15年+）", "salary_min": 155000, "salary_max": 220000, "salary_note": "大型矿业公司/能源公司ESG总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，环境工程师为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，QLD/WA资源/环境项目多", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区环境项目，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "水文学、污染修复、生态评估和工程设计的综合知识"},
    {"dimension": "learning_duration",        "label_zh": "中高", "stars": 4, "note": "4年本科+EA评估+CPEng累计约8~10年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "EA评估是学历审核，CPEng需工作经验积累"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "ESG监管+可再生能源+矿山修复三重驱动，职位数稳步增长"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "专精方向（ESG/气候/水务）工程师较供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "顾问岗差旅较多，政府岗节奏相对稳定"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级约 $85k~$115k，ESG/气候专精高级岗可达 $155k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "气候立法+ESG强制报告+矿山修复义务是20年以上持续旺盛的需求"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助环境建模，但现场评估、法规合规判断和利益相关方咨询不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，可持续发展领域契合澳洲政策方向"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "EA评估周期较长，但环境工程学历多数能顺利通过"},
]
SUITABILITY_FIT = ["持有环境工程/土木工程/化学工程学位（4年荣誉）", "有EIA（环境影响评估）、水务或污染修复实际项目经验", "英语能力达到 IELTS 6.0+（EA评估和政府报告要求）", "有ESG报告或气候变化适应工程经验（2025-2030年溢价方向）", "愿意接受现场工作（野外调查、矿山现场等）"]
SUITABILITY_UNFIT = ["非工程/环境科学学位，无法通过EA评估", "不愿意接受顾问行业差旅多的工作节奏", "对可持续发展和环境保护缺乏热情（影响工作积极性和晋升）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "环境工程师薪资 $95k~$115k（2026）", "url": "https://au.seek.com/career-advice/role/environmental-engineer/salary"},
    {"source_name": "Indeed AU", "content": "环境工程师平均薪资 $94,387（2026）", "url": "https://au.indeed.com/career/environmental-engineer/salaries"},
    {"source_name": "Engineers Australia", "content": "EA技能评估和CPEng认证", "url": "https://www.engineersaustralia.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲环境工程师工资多少？", "answer": "中级约 $85,000~$115,000（Indeed均值 $94,387）；高级/ESG专精约 $115k~$155k；ESG总监约 $155k~$220k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲环境工程师容易找工作吗？", "answer": "较容易。Seek 挂牌约 600~1800 个职位，气候立法+矿山修复义务+ESG报告需求持续驱动增长，专精方向工程师供不应求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国环境工程学历澳洲认可吗？", "answer": "通过 Engineers Australia（EA）技能评估。中国环境工程/土木工程背景的学历通常能通过EA评估，约 $770 申请费。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "环境工程师会被AI替代吗？", "answer": "风险较低。AI辅助环境建模和数据分析，但野外调查、监管合规判断和社区咨询（FPIC）不可替代。可持续发展领域本身就是AI产业的环保监管方向。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲环境工程师有年龄限制吗？", "answer": "无。资深环境工程师（40~55岁）在大型矿业/能源公司的ESG和矿山关闭项目中备受重视。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲环境工程师需要什么学历？", "answer": "4年荣誉环境工程/土木工程/化学工程学位是EA评估基本要求。环境科学（非工程）学位可以从事环境顾问岗，但薪资和资质路径与工程师有所不同。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲环境工程师认证（移民）难吗？", "answer": "难度中等。EA评估周期3~12个月，通过率较高；189/190 EOI分数对有经验者友好。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "环境工程师和土木工程师哪个更适合移民澳洲？", "answer": "土木工程师就业量更大（Seek ~4000 vs 环境 ~1200），薪资相当；环境工程师更契合澳洲气候政策，ESG方向是长期增长高地。有环境专业背景者选环境工程师，有结构/岩土背景者选土木工程师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 环境工程师数据入库完成")

if __name__ == "__main__":
    run()
