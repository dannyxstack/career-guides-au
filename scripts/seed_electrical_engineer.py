"""澳洲电气工程师（233311）数据入库。数据来源：JSA、SEEK、Indeed、Engineers Australia（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "233311", "anzsco_title": "Electrical Engineer",
    "category": "IT/工程", "workforce_size": 72000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Renewable Energy & Grid Integration","EV Charging Infrastructure","AUKUS Defence Electronics","Power Systems & Substations","Smart Grid & IoT Engineering"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "电气工程师",
    "summary": "电气工程师设计和监督电力系统、配电网络、可再生能源接入和国防电子设备。澳洲可再生能源转型（2030年82%可再生电力目标）和电网现代化工程推动对电气工程师的需求急剧增加，是工程类增速最快的职业之一。",
    "forecast_note": "JSA 预测电气工程师至2035年就业增长约15%。国家电力市场改革（NEM Reform）、大规模储能项目和EV充电基础设施是主要驱动力。",
    "trend_summary": "可再生能源（太阳能/风能）接入电网工程师是2025-2030年薪资增速最快的方向。AUKUS国防电子（雷达/通信系统）是薪资最高的专精方向，年薪可超 $160k。",
}
I18N_EN = {
    "locale": "en", "name": "Electrical Engineer",
    "summary": "Electrical engineers design and oversee power systems, distribution networks, renewable energy grid integration and defence electronics. Australia's renewable energy transition (82% renewable by 2030 target) and grid modernisation are driving acute demand.",
    "forecast_note": "JSA projects ~15% employment growth for electrical engineers by 2035. National Electricity Market reform, large-scale battery storage and EV charging infrastructure are the primary drivers.",
    "trend_summary": "Renewable energy grid integration engineers are the fastest-growing sub-discipline in 2025-2030. AUKUS defence electronics (radar/comms systems) commands the highest salary premiums, with annual salaries exceeding $160k.",
}
EDUCATION = [
    {"stage": "Bachelor of Electrical Engineering（荣誉，4年）", "duration": "4年（全日制）", "cost_min": 30000, "cost_max": 185000, "cost_note": "澳洲工程师资质要求4年荣誉学位；部分大学提供专业方向（电力/通信/控制）", "sort_order": 0},
    {"stage": "Engineers Australia（EA）技能评估", "duration": "3~12个月", "cost_min": 770, "cost_max": 3000, "cost_note": "189/190签证必须，约 $770 申请费", "sort_order": 1},
    {"stage": "注册电气工程师（REng/CPEng）", "duration": "4~7年工作经验后申请", "cost_min": 1500, "cost_max": 5000, "cost_note": "部分州的公共电网工程要求注册工程师签名", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Electrical Engineering (Honours)", "issuer": "认可大学（EA认证）", "note": "行业基础学历，4年荣誉学位是EA评估的基本要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Engineers Australia（EA）技能评估", "issuer": "Engineers Australia", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPEng（Chartered Professional Engineer）", "issuer": "Engineers Australia", "note": "专业注册工程师，高级岗位薪资溢价 $20k~$40k", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Electrical Contractor License（各州）", "issuer": "各州电气许可机构", "note": "现场施工监督和独立执业需要，与工程师资质不同", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 5000, "note": "全国，含电气工程师、电力系统工程师、可再生能源工程师岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 3500, "note": "含国防、电网公司和顾问岗"},
    {"platform": "LinkedIn", "count_min": 2500, "count_max": 5000, "note": "能源和国防企业直招"},
]
SALARIES = [
    {"experience": "毕业生电气工程师（0~2年）", "salary_min": 70000, "salary_max": 88000, "salary_note": "应届生起薪，能源/电力公司高于均值", "sort_order": 0},
    {"experience": "中级电气工程师（2~7年）", "salary_min": 95000, "salary_max": 130000, "salary_note": "SEEK 区间 $105k~$125k；Indeed 平均 $106,550（2026）", "sort_order": 1},
    {"experience": "高级电气工程师（7~15年，CPEng）", "salary_min": 130000, "salary_max": 165000, "salary_note": "Indeed Senior平均 $146,601（2026）；CPEng溢价明显", "sort_order": 2},
    {"experience": "国防/航空电气工程师（安全许可）", "salary_min": 150000, "salary_max": 200000, "salary_note": "AUKUS项目电气专家，持安全许可薪资溢价 $20k~$40k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，电气工程师为核心短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，SA/VIC可再生能源和QLD电网项目多", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区能源项目，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "电路理论、电磁学、电力系统和控制理论需要系统学习"},
    {"dimension": "learning_duration",        "label_zh": "中高", "stars": 4, "note": "4年本科+EA评估+CPEng累计约8~10年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "EA评估是学历审核，CPEng需工作经验积累"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "可再生能源转型和国防电子推动需求急剧增加，是增速最快的工程职业之一"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "可再生能源和国防方向工程师极度供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "电网工程有现场工作要求，但总体工作节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "中位数约 $105k~$130k；高级CPEng可达 $165k；国防专精 $200k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "2030年82%可再生电力目标+AUKUS国防电子=20年以上持续旺盛需求"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助电网优化，但系统设计、安全合规和现场管理不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，可再生能源政策推高各州对电气工程师的需求"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "EA评估周期较长；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["有电气/电力/能源工程经验（2年以上）", "有电力系统、可再生能源接入或国防电子专业背景", "英语能力达到 IELTS 6.0+（EA评估和工程报告要求）", "有意向可再生能源行业（太阳能/风能/储能）或AUKUS国防项目", "有电气设计软件（ETAP/PowerWorld/AutoCAD Electrical）经验"]
SUITABILITY_UNFIT = ["非工程学位，无法通过EA技能评估", "不愿意接受现场工作（发电站/变电站/施工现场）", "完全无电气安全意识（高压电气工作安全是核心要求）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "电气工程师薪资 $105k~$125k（2026）", "url": "https://au.seek.com/career-advice/role/electrical-engineer/salary"},
    {"source_name": "Indeed AU", "content": "电气工程师平均薪资 $106,550；高级 $146,601（2026）", "url": "https://au.indeed.com/career/electrical-engineer/salaries"},
    {"source_name": "Engineers Australia", "content": "EA技能评估和CPEng认证", "url": "https://www.engineersaustralia.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲电气工程师工资多少？", "answer": "中级约 $95,000~$130,000（Indeed均值 $106,550）；高级CPEng约 $130k~$165k（高级均值 $146,601）；国防/航空专精可达 $150k~$200k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲电气工程师容易找工作吗？", "answer": "极容易。Seek 挂牌约 2000~5000 个职位，可再生能源转型（2030年82%目标）和AUKUS国防电子推动需求急剧增加，是工程类增速最快的职业。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国电气工程学位澳洲认可吗？", "answer": "通过 Engineers Australia（EA）技能评估。中国985/211大学的电气工程学位通过率较高，需要确保课程覆盖电力系统、控制和电磁学等核心内容。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "电气工程师会被AI替代吗？", "answer": "风险较低。AI辅助电网优化和故障预测，但电气系统设计、安全合规（AS/NZS标准）和高压现场管理需要持牌工程师负责，不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲电气工程师有年龄限制吗？", "answer": "无。有大型电网或国防项目经验的资深工程师（40~55岁）备受能源企业和国防承包商青睐。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲电气工程师需要什么学历？", "answer": "必须持有4年荣誉电气工程学位，这是EA评估和CPEng的基本要求。3年学位需要加一年荣誉年。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲电气工程师认证（移民）难吗？", "answer": "难度中等。EA评估周期3~12个月，通过率较高；189/190 EOI分数对有5年以上经验者友好。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "电气工程师和土木工程师哪个更适合移民澳洲？", "answer": "电气工程师薪资更高（中级 $105k~$130k vs 土木 $95k~$115k），可再生能源推动增速更快；土木工程师就业量更大（基础设施项目更广泛）。有电气背景者坚定选电气工程师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 电气工程师数据入库完成")

if __name__ == "__main__":
    run()
