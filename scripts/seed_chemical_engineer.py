"""澳洲化学工程师（233111）数据入库。数据来源：JSA、SEEK、Indeed、Engineers Australia（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "233111", "anzsco_title": "Chemical Engineer",
    "category": "IT/工程", "workforce_size": 14000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Green Hydrogen & Clean Energy","Critical Minerals Processing & Refining","Pharmaceutical & Biotech Manufacturing","Carbon Capture & Storage (CCS)","Polymer & Materials Engineering"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "化学工程师",
    "summary": "化学工程师设计和优化化学生产过程，覆盖矿物加工、石油化工、制药、食品工业和新兴清洁能源（绿氢/碳捕获）。澳洲绿氢产业发展（联邦$20亿绿氢投资）和关键矿产精炼本土化推动化学工程师需求显著增加。",
    "forecast_note": "JSA 预测化学工程师至2035年就业增长约8%。绿色氢能生产和关键矿产加工是2025-2030年增长最快的子领域。",
    "trend_summary": "绿氢和可再生能源化工是澳洲化工行业的最大投资方向。锂矿精炼（氢氧化锂生产）工程师是当前薪资溢价最高的方向，年薪可达 $130k~$160k。",
}
I18N_EN = {
    "locale": "en", "name": "Chemical Engineer",
    "summary": "Chemical engineers design and optimise chemical production processes across mineral processing, petrochemicals, pharmaceuticals, food industry and clean energy (green hydrogen/carbon capture). Federal $2B green hydrogen investment and onshoring of critical minerals processing are driving increased demand.",
    "forecast_note": "JSA projects ~8% employment growth for chemical engineers by 2035. Green hydrogen production and critical minerals processing are the fastest-growing sub-disciplines in 2025-2030.",
    "trend_summary": "Green hydrogen and renewable energy chemicals are the largest investment directions in Australian chemical engineering. Lithium refinery engineers (lithium hydroxide production) currently command the highest salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of Chemical Engineering（荣誉，4年）", "duration": "4年（全日制）", "cost_min": 30000, "cost_max": 185000, "cost_note": "澳洲化学工程师资质要求4年荣誉学位", "sort_order": 0},
    {"stage": "Engineers Australia（EA）技能评估", "duration": "3~12个月", "cost_min": 770, "cost_max": 3000, "cost_note": "189/190签证必须，约 $770 申请费", "sort_order": 1},
    {"stage": "CPEng（Chartered Professional Engineer）", "duration": "4~7年工作经验后申请", "cost_min": 1500, "cost_max": 5000, "cost_note": "专业注册工程师，高级岗位的重要资质", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Chemical Engineering (Honours)", "issuer": "认可大学（EA认证）", "note": "4年荣誉化学工程学位是EA评估基本要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Engineers Australia（EA）技能评估", "issuer": "Engineers Australia", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPEng（Chartered Professional Engineer）", "issuer": "Engineers Australia", "note": "大型化工/采矿项目的重要专业资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Process Safety Management Certification（PSM）", "issuer": "IChemE / AIOH", "note": "化工安全管理专业认证，大型工厂安全工程岗的重要加分项", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 500,  "count_max": 1500, "note": "全国，含化学工程师、工艺工程师、矿物加工工程师和绿氢工程师岗"},
    {"platform": "Indeed",   "count_min": 300,  "count_max": 900,  "note": "含制药、食品和能源化工岗"},
    {"platform": "LinkedIn", "count_min": 600,  "count_max": 1500, "note": "化工企业和绿氢初创公司直招"},
]
SALARIES = [
    {"experience": "毕业生化学工程师（0~2年）", "salary_min": 70000, "salary_max": 85000, "salary_note": "应届生起薪", "sort_order": 0},
    {"experience": "中级化学工程师（2~7年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "SEEK 区间 $85k~$105k；Indeed 平均 $90,681（2026）", "sort_order": 1},
    {"experience": "高级/锂矿精炼工程师（5年+）", "salary_min": 115000, "salary_max": 165000, "salary_note": "锂矿精炼和绿氢专精工程师，Indeed Senior 平均约 $126k", "sort_order": 2},
    {"experience": "总工程师 / 工艺总监（15年+）", "salary_min": 165000, "salary_max": 250000, "salary_note": "大型化工/矿业公司工艺技术总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，化学工程师为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，WA（锂矿加工）/ SA（绿氢）通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区化工项目，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "很高", "stars": 4, "note": "化学热力学、传质、反应工程等需要强理工科基础"},
    {"dimension": "learning_duration",        "label_zh": "中高", "stars": 4, "note": "4年本科+EA评估+CPEng累计约8~10年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "EA评估是学历审核，CPEng需工作经验"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "职位总量相对较小，但绿氢/锂矿精炼方向需求急剧增加"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "专精方向（绿氢/锂矿）工程师极度稀缺"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "化工生产现场有轮班和安全要求，办公岗节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级约 $85k~$115k，锂矿/绿氢专精高级岗 $130k~$165k"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "绿氢产业+锂矿本土精炼是10年以上的增长方向"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助工艺优化，但化工安全管理和现场工程判断不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，清洁能源政策支持下对化工工程师的长期需求"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "EA评估周期较长，但通过率较高；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["持有化学工程/化学工艺/材料工程学位（4年荣誉）", "有化工生产、矿物加工或制药制造实际工作经验", "英语能力达到 IELTS 6.0+（EA评估要求）", "对绿氢/锂矿加工有浓厚兴趣（薪资溢价最高的新兴方向）", "愿意在西澳（矿业化工）或南澳（绿氢重镇）工作"]
SUITABILITY_UNFIT = ["非化学/工程学位，无法通过EA评估", "对化工安全规程不重视（化工生产安全是核心要求）", "不接受部分化工岗的轮班/现场工作要求"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "化学工程师薪资 $85k~$105k（2026）", "url": "https://au.seek.com/career-advice/role/chemical-engineer/salary"},
    {"source_name": "Indeed AU", "content": "化学工程师平均薪资 $90,681；高级 $126k（2026）", "url": "https://au.indeed.com/career/chemical-engineer/salaries"},
    {"source_name": "Engineers Australia", "content": "EA技能评估和CPEng认证", "url": "https://www.engineersaustralia.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲化学工程师工资多少？", "answer": "中级约 $85,000~$115,000（Indeed均值 $90,681）；锂矿精炼/绿氢高级工程师约 $115k~$165k（高级均值 $126k）；总工程师可超 $165k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲化学工程师容易找工作吗？", "answer": "较容易（专精方向）。Seek 挂牌约 500~1500 个职位，绿氢产业和锂矿本土精炼推动需求增加，专精工程师供不应求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国化学工程学历澳洲认可吗？", "answer": "通过 Engineers Australia（EA）技能评估。中国化工/化学工程学历（985/211院校）通常能顺利通过，约 $770 申请费。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "化学工程师会被AI替代吗？", "answer": "风险较低。AI辅助工艺模拟和优化（Aspen Plus），但化工安全管理、设备设计判断和工艺放大（Scale-up）决策不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲化学工程师有年龄限制吗？", "answer": "无。资深工艺工程师（40~55岁）在大型化工/矿业公司备受重视，特别是有生产线管理和安全管理经验者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲化学工程师需要什么学历？", "answer": "必须持有4年荣誉化学工程学位（Bachelor of Chemical Engineering Honours），这是EA评估的基本要求。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲化学工程师认证（移民）难吗？", "answer": "难度中等。EA评估周期3~12个月，通过率较高；189/190 EOI分数对有经验者友好。绿氢方向雇主担保482也是快速路径。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "化学工程师和机械工程师哪个更适合移民澳洲？", "answer": "机械工程师就业量更大（Seek ~2000 vs 化工 ~700），薪资相当；化学工程师在绿氢/锂矿精炼方向有更高的薪资溢价。两者均在MLTSSL，建议根据学历背景选择。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 化学工程师数据入库完成")

if __name__ == "__main__":
    run()
