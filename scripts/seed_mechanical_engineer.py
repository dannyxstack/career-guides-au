"""澳洲机械工程师（233512）数据入库。数据来源：JSA、SEEK、Indeed、Engineers Australia（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "233512", "anzsco_title": "Mechanical Engineer",
    "category": "IT/工程", "workforce_size": 55000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Defence Manufacturing (AUKUS)","Renewable Energy Systems (Wind/Solar/Hydrogen)","Mining Equipment & Automation","Advanced Manufacturing & Industry 4.0","HVAC & Building Services Engineering"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "机械工程师",
    "summary": "机械工程师设计、分析和测试机械系统，覆盖制造业、采矿设备、可再生能源、国防和建筑服务。AUKUS国防制造计划和澳洲可再生能源转型推动对机械工程师的需求显著增加，是工程类薪资潜力最高的职业之一。",
    "forecast_note": "JSA 预测机械工程师至2035年就业增长约10%。AUKUS核潜艇计划（AU$368亿）和可再生能源设施建设是主要驱动力。",
    "trend_summary": "国防和航空航天机械工程师（需要澳洲安全许可）是薪资溢价最高的方向，年薪可超 $160k。工业4.0（机器人/自动化）专精的机械工程师需求急剧增加。",
}
I18N_EN = {
    "locale": "en", "name": "Mechanical Engineer",
    "summary": "Mechanical engineers design, analyse and test mechanical systems across manufacturing, mining equipment, renewable energy, defence and building services. AUKUS defence manufacturing and Australia's renewable energy transition are driving increased demand.",
    "forecast_note": "JSA projects ~10% employment growth for mechanical engineers by 2035. The AUKUS nuclear submarine program ($368B) and renewable energy facility construction are the primary demand drivers.",
    "trend_summary": "Defence and aerospace mechanical engineers (requiring security clearance) command the highest salary premiums, with annual salaries exceeding $160k. Industry 4.0 (robotics/automation) specialists are in acute demand.",
}
EDUCATION = [
    {"stage": "Bachelor of Mechanical Engineering（荣誉，4年）", "duration": "4年（全日制）", "cost_min": 30000, "cost_max": 185000, "cost_note": "澳洲工程师资质要求4年荣誉学位；国际生约 $38,000~$48,000/年", "sort_order": 0},
    {"stage": "Engineers Australia（EA）技能评估", "duration": "3~12个月", "cost_min": 770, "cost_max": 3000, "cost_note": "189/190签证必须，约 $770 申请费", "sort_order": 1},
    {"stage": "CPEng（Chartered Professional Engineer）认证", "duration": "4~7年工作经验后申请", "cost_min": 1500, "cost_max": 5000, "cost_note": "注册工程师认证，是高级岗位晋升的重要资质", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Mechanical Engineering (Honours)", "issuer": "认可大学（EA认证）", "note": "行业基础学历，EA认证的4年荣誉学位是工程师移民的基本要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Engineers Australia（EA）技能评估", "issuer": "Engineers Australia", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPEng（Chartered Professional Engineer）", "issuer": "Engineers Australia", "note": "专业注册工程师，高级岗位重要资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "NVH / ANSYS / SolidWorks专业认证", "issuer": "各认证机构", "note": "仿真软件专业认证，采矿/国防方向薪资溢价高", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 3500, "note": "全国，含机械工程师、设计工程师、项目工程师和国防岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 2500, "note": "含FIFO采矿岗和制造业岗"},
    {"platform": "LinkedIn", "count_min": 1500, "count_max": 3500, "note": "国防、航空和顾问公司直招"},
]
SALARIES = [
    {"experience": "毕业生机械工程师（0~2年）", "salary_min": 65000, "salary_max": 82000, "salary_note": "应届生起薪", "sort_order": 0},
    {"experience": "中级机械工程师（2~7年）", "salary_min": 85000, "salary_max": 120000, "salary_note": "SEEK 区间 $90k~$110k；Indeed 平均 $87,854（2026）", "sort_order": 1},
    {"experience": "资源/采矿FIFO机械工程师（3年+）", "salary_min": 110000, "salary_max": 155000, "salary_note": "FIFO远程现场工程师包含住宿和轮岗补贴", "sort_order": 2},
    {"experience": "高级/国防机械工程师（7年+，含安全许可）", "salary_min": 140000, "salary_max": 190000, "salary_note": "国防/航空航天工程师，持安全许可溢价 $20k~$40k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，机械工程师为核心短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，WA/QLD采矿和SA/VIC制造业通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区工程项目，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "热力学、材料力学、流体力学等需要系统工科学习"},
    {"dimension": "learning_duration",        "label_zh": "中高", "stars": 4, "note": "4年本科+EA评估+CPEng累计约8~10年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "EA评估是学历审核，CPEng需工作经验积累"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "AUKUS国防和可再生能源转型双重驱动"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "FIFO采矿岗和国防岗极度缺人"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "FIFO轮岗强度高，但轮休时间充足；办公岗节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位数约 $90k~$110k；采矿FIFO+国防专精 $140k~$190k"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "可再生能源、国防制造和工业自动化是长期增长方向"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助有限元分析和设计优化，但工程判断和现场经验不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，EA评估路径成熟，WA/QLD采矿方向特别受州欢迎"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "EA评估周期较长；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["有机械/制造/能源行业工程经验（2年以上）", "有SolidWorks/AutoCAD/ANSYS等设计软件实操经验", "英语能力达到 IELTS 6.0+（EA评估和工程报告要求）", "有意向FIFO采矿岗（西澳/昆士兰矿业薪资最高）", "或有意向国防/航空方向（AUKUS项目需求急剧增加）"]
SUITABILITY_UNFIT = ["非工程学位，无法通过EA技能评估", "完全排斥现场工作和FIFO生活方式", "不愿意考取CPEng（限制长期薪资天花板）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "机械工程师薪资 $90k~$110k（2026）", "url": "https://au.seek.com/career-advice/role/mechanical-engineer/salary"},
    {"source_name": "Indeed AU", "content": "机械工程师平均薪资 $87,854（2026）", "url": "https://au.indeed.com/career/mechanical-engineer/salaries"},
    {"source_name": "Engineers Australia", "content": "EA技能评估和CPEng认证", "url": "https://www.engineersaustralia.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲机械工程师工资多少？", "answer": "中级机械工程师约 $85,000~$120,000（Indeed均值 $87,854）；FIFO采矿工程师约 $110k~$155k（含远程补贴）；国防/航空工程师可达 $140k~$190k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲机械工程师容易找工作吗？", "answer": "容易。Seek 挂牌约 1500~3500 个职位，FIFO采矿岗（西澳/昆士兰）和国防制造岗（AUKUS）极度缺人，持工作经验者主动被猎头联系。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国机械工程学位澳洲认可吗？", "answer": "通过 Engineers Australia（EA）技能评估，约 $770 申请费，3~12个月周期。中国985/211大学的机械工程学位通过率较高，但需要确保课程覆盖度与EA要求匹配。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "机械工程师会被AI替代吗？", "answer": "风险较低。AI辅助有限元分析和设计优化（ANSYS/Simcenter），但工程判断、现场施工监督、实验测试和设备故障诊断不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲机械工程师有年龄限制吗？", "answer": "无。国防和资源行业特别重视有大型项目管理经验的资深工程师，40~55岁有经验者在市场上仍具竞争力。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲机械工程师需要什么学历？", "answer": "必须持有4年荣誉机械工程学位，这是EA技能评估的基本要求。澳洲不承认3年学士学位（需要荣誉年或补充课程）。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲机械工程师认证（移民）难吗？", "answer": "难度中等。EA评估周期较长（3~12个月），但通过率较高；189/190 EOI分数对有经验的工程师友好。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "机械工程师和土木工程师哪个更适合移民澳洲？", "answer": "土木工程师就业量更大（Seek ~3000+ vs 机械 ~1500），基础设施项目稳定；机械工程师在采矿/国防/可再生能源方向薪资潜力更高。两者均在MLTSSL列表，建议根据自身背景选择。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 机械工程师数据入库完成")

if __name__ == "__main__":
    run()
