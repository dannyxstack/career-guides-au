"""澳洲数据分析师（262111）数据入库。数据来源：JSA、SEEK、Indeed、PayScale（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "262111", "anzsco_title": "ICT Business Analyst",
    "category": "IT/工程", "workforce_size": 95000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Business Intelligence & Reporting","Data Engineering & ETL Pipelines","AI/ML Data Preparation","Financial & Risk Analytics","Government & Healthcare Data Analytics"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "数据分析师",
    "summary": "数据分析师通过SQL、Python、Power BI和Tableau等工具分析业务数据，支持企业决策。澳洲数字经济转型和政府开放数据政策驱动持续高需求，是IT类就业量最大、入门门槛相对较低的职业之一，适合技术+商业双背景的人才。",
    "forecast_note": "JSA 预测数据和商业分析师至2035年就业增长约20%。AI增强分析（AI-assisted analytics）推动对能解读AI输出的高级分析师需求增加。",
    "trend_summary": "数据工程（DE）技能（Spark/dbt/Airflow）使数据分析师升级为数据工程师，薪资溢价 $20k~$35k。Power BI和Tableau技能是澳洲市场最广泛要求的BI工具。",
}
I18N_EN = {
    "locale": "en", "name": "Data Analyst",
    "summary": "Data analysts use SQL, Python, Power BI and Tableau to analyse business data and support decision-making. Australia's digital economy transformation and open data policy drive sustained high demand across government, finance and healthcare.",
    "forecast_note": "JSA projects ~20% employment growth for data and business analysts by 2035. AI-enhanced analytics is increasing demand for senior analysts who can interpret AI-generated insights.",
    "trend_summary": "Data engineering skills (Spark/dbt/Airflow) enable data analysts to transition to data engineer roles with $20k~$35k salary premiums. Power BI and Tableau are the most commonly required BI tools in Australia.",
}
EDUCATION = [
    {"stage": "Bachelor of Data Science / Statistics / Computer Science / Business（3~4年）", "duration": "3~4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "或相关本科学历+自学BI工具（Power BI/Tableau认证）", "sort_order": 0},
    {"stage": "Power BI / Tableau / Google Data Analytics 认证", "duration": "1~3个月", "cost_min": 200, "cost_max": 2000, "cost_note": "快速上手BI工具，Google Data Analytics Certificate约 $50/月", "sort_order": 1},
    {"stage": "ACS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民必须", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Data Science / Statistics / Computer Science", "issuer": "认可大学", "note": "行业通用基础学历", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Microsoft Power BI Data Analyst Associate (PL-300)", "issuer": "Microsoft", "note": "澳洲市场最广泛要求的BI分析认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Tableau Desktop Specialist / Certified Associate", "issuer": "Tableau/Salesforce", "note": "与Power BI并列最受欢迎的可视化工具认证", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "ACS 技能评估", "issuer": "Australian Computer Society", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2500, "count_max": 5000, "note": "全国，含BI分析师、数据工程师、报告分析师和业务系统分析师岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 3500, "note": "含政府、金融和医疗机构分析师岗"},
    {"platform": "LinkedIn", "count_min": 3000, "count_max": 6000, "note": "各行业BI和数据岗"},
]
SALARIES = [
    {"experience": "初级数据分析师（0~2年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "含毕业生和转行者，政府岗起薪略高", "sort_order": 0},
    {"experience": "中级数据分析师（2~5年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "SEEK 区间 $95k~$115k；Indeed 平均 $100,656（2026）", "sort_order": 1},
    {"experience": "高级数据分析师（5~8年）", "salary_min": 115000, "salary_max": 145000, "salary_note": "含团队Lead和BI架构师", "sort_order": 2},
    {"experience": "数据科学家 / 数据工程师（进阶）", "salary_min": 120000, "salary_max": 180000, "salary_note": "Python/Spark/ML技能升级后的薪资区间", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，数据分析为短缺类别", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NSW/VIC/QLD通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区IT/数据岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "SQL和BI工具门槛相对低，Python/统计学需要系统学习"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3~4年；转行路径6~18个月（含SQL+Power BI自学）"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Power BI PL-300和Google Data Analytics证书难度较低"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "各行业数字化转型驱动数据岗位爆发，是就业量最大的IT职业之一"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级岗竞争较激烈，高级+Python/ML技能者供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "报告截止期压力，但总体工作节奏较为规律"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位数约 $95k~$115k，进阶数据工程师后可提升至 $130k+"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "AI分析工具提升生产率，对能指导AI、解读结果的分析师需求增加"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "简单报告生成受AI工具冲击，但策略性数据解读和业务洞察需求增加"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，就业量大，雇主担保机会多"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "ACS评估和EOI分数是门槛，中等难度"},
]
SUITABILITY_FIT = ["有SQL和数据分析工作经验（2年以上）", "熟悉Power BI或Tableau，有数据可视化项目经验", "有Python/R统计分析能力（可显著提升薪资竞争力）", "英语能力达到 IELTS 6.0+ / PTE 50+", "目标是政府、金融或医疗行业数据岗（稳定且需求旺盛）"]
SUITABILITY_UNFIT = ["仅有Excel经验，无SQL基础", "不愿意学习Python/数据工程技能（长期发展受限）", "英语沟通能力较弱（数据分析需要向业务团队汇报）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "数据分析师薪资 $95k~$115k（2026）", "url": "https://au.seek.com/career-advice/role/data-analyst/salary"},
    {"source_name": "Indeed AU", "content": "数据分析师平均薪资 $100,656（2026）", "url": "https://au.indeed.com/career/data-analyst/salaries"},
    {"source_name": "ACS", "content": "技能评估机构", "url": "https://www.acs.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲数据分析师工资多少？", "answer": "中级数据分析师约 $85,000~$115,000（Indeed均值 $100,656）；高级分析师约 $115k~$145k；进阶数据科学家/工程师约 $120k~$180k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲数据分析师容易找工作吗？", "answer": "容易。Seek 挂牌约 2500~5000 个职位，各行业数字化驱动广泛需求，是IT类就业量最大的职业之一。初级岗竞争较激烈，SQL+Power BI+Python组合竞争力强。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国数据分析经验澳洲认可吗？", "answer": "通过 ACS 技能评估（学历审核），Power BI/Tableau/SQL等技能是国际通用的。建议提前考取Power BI PL-300认证以增强竞争力。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "数据分析师会被AI替代吗？", "answer": "简单的报告自动化受AI工具冲击，但将数据洞察转化为业务策略、管理数据质量和指导AI分析方向的能力不可替代。建议向数据工程师或AI分析师方向发展。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲数据分析师有年龄限制吗？", "answer": "无。具有行业背景（如金融+数据、医疗+数据）的分析师在市场上具有额外优势，年龄不是障碍。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲数据分析师需要什么学历？", "answer": "数据科学/统计/CS相关学位是主流，但具备SQL+Power BI+Python实战能力的非相关学历者也可通过雇主担保（482签证）入职。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲数据分析师认证（移民）难吗？", "answer": "难度中低。ACS评估不难；Power BI PL-300认证相对容易；189/190 EOI分数对有经验者友好。是IT类移民难度最低的职业之一。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "数据分析师和ML工程师哪个更适合移民澳洲？", "answer": "数据分析师就业量更大（Seek ~3000+ vs ML ~600），门槛更低，适合快速移民；ML工程师薪资更高（$131k~$165k vs $95k~$115k），门槛更高（通常需硕士）。建议先以数据分析师身份移民，再向ML方向发展。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 数据分析师数据入库完成")

if __name__ == "__main__":
    run()
