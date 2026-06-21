"""澳洲土木工程师（233211）数据入库。数据来源：JSA、SEEK、Indeed、Engineers Australia（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "233211", "anzsco_title": "Civil Engineer",
    "category": "IT/工程", "workforce_size": 95000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Transport Infrastructure (Roads/Rail/Bridges)","Water Infrastructure & Treatment Plants","Renewable Energy Civil Works","Defence Infrastructure (AUKUS)","Urban Development & Building Works"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "土木工程师",
    "summary": "土木工程师规划、设计和监督建造道路、桥梁、隧道、水利设施和城市基础设施。澳洲联邦和州政府历史性基础设施投资（交通、能源、水务）和AUKUS国防设施建设推动需求持续旺盛，是工程类就业量最大的职业。",
    "forecast_note": "JSA 预测土木工程师至2035年就业增长约12%。联邦《澳洲未来基金》（AU$800亿）基础设施投资和州政府交通项目是主要驱动力。",
    "trend_summary": "绿色基础设施（Green Infrastructure）和可再生能源配套土建（太阳能/风电场土建）是2025-2030年增长最快的子领域。BIM（建筑信息模型）技能是高薪资溢价方向。",
}
I18N_EN = {
    "locale": "en", "name": "Civil Engineer",
    "summary": "Civil engineers plan, design and oversee construction of roads, bridges, tunnels, water infrastructure and urban development. Historic federal and state infrastructure investment ($800B Future Fund) and AUKUS defence facility construction drive sustained high demand.",
    "forecast_note": "JSA projects ~12% employment growth for civil engineers by 2035. Federal infrastructure investment and state transport projects are the primary demand drivers.",
    "trend_summary": "Green infrastructure and renewable energy civil works (solar/wind farm construction) are the fastest-growing sub-disciplines in 2025-2030. BIM proficiency commands salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of Civil Engineering（荣誉，4年）", "duration": "4年（全日制）", "cost_min": 30000, "cost_max": 180000, "cost_note": "澳洲工程师资质要求4年荣誉学位；国际生约 $38,000~$48,000/年", "sort_order": 0},
    {"stage": "Engineers Australia（EA）技能评估", "duration": "3~12个月", "cost_min": 800, "cost_max": 3000, "cost_note": "海外工程学历评估机构，是189/190签证的必要步骤；约 $770 申请费", "sort_order": 1},
    {"stage": "CPEng（Chartered Professional Engineer）认证", "duration": "4~7年工作经验后申请", "cost_min": 1500, "cost_max": 5000, "cost_note": "专业注册工程师认证，显著提升薪资和项目管理机会", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Civil Engineering (Honours)", "issuer": "认可大学（EA认证）", "note": "行业基础学历，EA认证的大学学位是移民评估的关键", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Engineers Australia（EA）技能评估", "issuer": "Engineers Australia", "note": "海外工程学历的189/190签证评估机构，是技术移民必须步骤", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPEng（Chartered Professional Engineer）", "issuer": "Engineers Australia", "note": "专业注册工程师认证，提升薪资天花板约 $20k~$40k", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "RPEQ（Queensland）/ RPEQ同等州注册", "issuer": "各州工程师委员会", "note": "部分州的公共基础设施项目要求注册工程师签名", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 5000, "note": "全国，含土木工程师、结构工程师、基础设施项目工程师岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 3500, "note": "含政府、建筑公司和顾问工程师岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 4000, "note": "大型基础设施公司（AECOM/WSP/Jacobs）直招"},
]
SALARIES = [
    {"experience": "毕业生土木工程师（0~2年）", "salary_min": 68000, "salary_max": 80000, "salary_note": "应届生起薪，联邦政府岗略高", "sort_order": 0},
    {"experience": "中级土木工程师（2~7年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "SEEK 区间 $95k~$115k；Indeed 平均 $101,707（2026）", "sort_order": 1},
    {"experience": "高级土木工程师（7~15年，含CPEng）", "salary_min": 115000, "salary_max": 160000, "salary_note": "CPEng持有者薪资溢价 $20k~$40k", "sort_order": 2},
    {"experience": "工程总监 / 项目总监（15年+）", "salary_min": 160000, "salary_max": 250000, "salary_note": "大型基础设施公司总监级别，含分红", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，土木工程师为核心短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，QLD/SA/WA基础设施项目多", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区工程项目，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "力学、材料、水文和结构设计需要系统学习，需4年荣誉学位"},
    {"dimension": "learning_duration",        "label_zh": "中高", "stars": 4, "note": "4年本科+EA评估+CPEng累计需约8~10年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "EA评估是学历审核，CPEng需要工作经验+能力证明"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "联邦$800亿基础设施投资和AUKUS推动持续高需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "基础设施项目多，持CPEng的高级工程师极度供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "现场监督有体力要求，但室内设计工作节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位数约 $95k~$115k，持CPEng可达 $130k~$160k"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "可再生能源和绿色基础设施是长期增长方向"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助设计优化，但工程判断、现场管理和监管合规不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，EA评估路径成熟，各州均有需求"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "EA评估周期较长（3~12个月）；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["有土木/结构工程学位（4年），理工科基础扎实", "有实际工程项目经验（2年以上）", "英语能力达到 IELTS 6.0+（EA评估和工程报告要求）", "有BIM/AutoCAD/Civil 3D等设计软件实操经验", "愿意接受工程师助理阶段（前2年）薪资较低的过渡期"]
SUITABILITY_UNFIT = ["非工程学位，无法通过EA技能评估", "仅有施工管理经验，无设计或分析背景", "完全排斥现场工作（工程项目不可避免有现场监督工作）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "土木工程师薪资 $95k~$115k（2026）", "url": "https://au.seek.com/career-advice/role/civil-engineer/salary"},
    {"source_name": "Indeed AU", "content": "土木工程师平均薪资 $101,707（2026）", "url": "https://au.indeed.com/career/civil-engineer/salaries"},
    {"source_name": "Engineers Australia", "content": "EA技能评估和CPEng认证", "url": "https://www.engineersaustralia.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲土木工程师工资多少？", "answer": "中级土木工程师约 $85,000~$115,000（Indeed均值 $101,707）；持CPEng高级工程师约 $115k~$160k；工程总监可超 $200k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲土木工程师容易找工作吗？", "answer": "容易。Seek 挂牌约 2000~5000 个职位，联邦$800亿基础设施投资和各州交通项目驱动持续高需求，持CPEng者主动被顾问公司猎头。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国工程学位澳洲认可吗？", "answer": "通过 Engineers Australia（EA）技能评估（约 $770 申请费，3~12个月周期）。大多数中国985/211大学的工程学位通过EA评估问题不大，但部分专业课程匹配度需要验证。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "土木工程师会被AI替代吗？", "answer": "风险较低。AI辅助结构优化和设计自动化，但工程判断、现场管理、安全监督和政府监管合规（RPEQ签名）不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲土木工程师有年龄限制吗？", "answer": "无。经验丰富的40~55岁土木工程师在大型基础设施项目中备受重视，特别是有项目总监经验者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲土木工程师需要什么学历？", "answer": "必须持有4年荣誉土木工程学位（Bachelor of Civil Engineering (Honours)），这是EA技能评估和澳洲工程师注册的基本要求。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲土木工程师认证（移民）难吗？", "answer": "难度中等。EA评估周期较长（3~12个月），但通过率较高；CPEng是可选晋升路径。189/190 EOI分数对有经验者友好。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "土木工程师和机械工程师哪个更适合移民澳洲？", "answer": "土木工程师就业量更大（Seek ~3000+ vs 机械 ~1500），需求更稳定（基础设施项目周期长）；机械工程师薪资潜力略高（资源/采矿行业高薪岗）。两者均在MLTSSL列表，PR友好度相当。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 土木工程师数据入库完成")

if __name__ == "__main__":
    run()
