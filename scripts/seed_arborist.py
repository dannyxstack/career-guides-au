"""澳洲林业工人/树艺师（362211）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "362211", "anzsco_title": "Arborist / Forestry Worker",
    "category": "其他", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["城市绿化和景观树木管理","建设工地树木保护咨询","林业可持续采伐和再种植","灌木火后环境修复","高空绳降树艺师（Climbing Arborist）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "林业工人/树艺师",
    "summary": "树艺师（Arborist）负责城市和郊区树木的修剪、移除、评估和养护，是城市景观管理和绿化基础设施维护的核心专业；林业工人在商业林区从事采伐、植树和森林管理工作。澳洲各大城市大规模城市绿化和基础设施树木保护计划推动树艺师需求旺盛，是MLTSSL短缺职业，PR路径顺畅。",
    "forecast_note": "JSA预测树艺师就业至2030年增长约9%。澳洲城市树木保护立法日趋严格（未经许可砍伐罚款高达 $1M+）、政府城市绿化预算增加和建设工地树木保护需求推动树艺师需求持续增长。高空攀爬树艺师（Climbing Arborist）全国短缺严重。",
    "trend_summary": "澳洲各大城市（悉尼/墨尔本）已颁布严格的城市树木保护法规，任何涉及树木的工程必须聘用持证树艺师。高空攀爬树艺师（Climbing Arborist with AQF Level 5+资质）是全国最紧缺的蓝领技术工之一，薪资显著高于普通林业工人。2019-2020年黑色夏天灌木火后澳洲启动了大规模林区修复，推动额外就业需求。",
}
I18N_EN = {
    "locale": "en", "name": "Arborist / Forestry Worker",
    "summary": "Arborists manage urban and suburban tree pruning, removal, assessment and maintenance — a core profession for urban landscape management and green infrastructure maintenance. Forestry workers in commercial forest areas handle logging, replanting and forest management. Large-scale urban greening and infrastructure tree protection plans in major Australian cities drive strong arborist demand — they appear on the MLTSSL with smooth PR pathways.",
    "forecast_note": "JSA projects ~9% arborist employment growth by 2030. Increasingly strict Australian urban tree protection legislation (unauthorised tree removal fines up to $1M+), increased government urban greening budgets and construction site tree protection requirements drive continued arborist demand growth. Climbing arborists are in acute shortage nationally.",
    "trend_summary": "Major Australian cities (Sydney/Melbourne) have enacted strict urban tree protection regulations requiring certified arborists for any tree-involving works. Climbing arborists (with AQF Level 5+ qualifications) are among the most critically short blue-collar tradespeople nationally, with salaries significantly above average forestry workers. The 2019-2020 Black Summer bushfires prompted large-scale forest rehabilitation across Australia, driving additional employment demand.",
}
EDUCATION = [
    {"stage": "Certificate III in Arboriculture（AHC30816）", "duration": "2~3年（学徒制）", "cost_min": 3000, "cost_max": 15000, "cost_note": "澳洲树艺师行业标准资质；学徒制（在职+课程）；学徒期间有收入", "sort_order": 0},
    {"stage": "Certificate IV in Arboriculture（高级）", "duration": "12~18个月", "cost_min": 3000, "cost_max": 12000, "cost_note": "树艺主管和树木顾问的进阶资质；薪资溢价显著", "sort_order": 1},
    {"stage": "Certificate III in Forest Operations（林业方向）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 10000, "cost_note": "商业林业采伐和林区管理资质", "sort_order": 2},
    {"stage": "安全培训（高空作业/链锯操作）", "duration": "2~5天", "cost_min": 300, "cost_max": 1000, "cost_note": "高空攀爬树艺师的实际必要资质（白卡+链锯+高空）", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Arboriculture（AHC30816）", "issuer": "TAFE / 认可RTO", "note": "独立从事树艺工作的行业标准资质；技术移民评估基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card（建设工地安全证）", "issuer": "TAFE / 认可RTO", "note": "进入建设工地（树木保护工作）的法定要求", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "链锯操作证书（Chainsaw Operation）", "issuer": "TAFE / 认可RTO", "note": "所有树艺/林业工作的实际必要资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Vetassess 技能评估（移民）", "issuer": "Vetassess", "note": "189/190/491技术移民的学历和经验评估", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 300, "count_max": 800, "note": "全国，含树艺师/林业技术员/景观树木维护岗"},
    {"platform": "Indeed",   "count_min": 200, "count_max": 600, "note": "含市政绿化、建设公司树木顾问和私人树艺公司"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 300, "note": "政府绿化部门和大型景观公司管理岗"},
]
SALARIES = [
    {"experience": "初级树艺学徒/林业工人（0~2年）", "salary_min": 55000, "salary_max": 68000, "salary_note": "学徒期薪资；林业工人起薪约 $4,913~$6,161/月（约 $59k~$74k/年）", "sort_order": 0},
    {"experience": "有经验树艺师（2~7年）", "salary_min": 70000, "salary_max": 92000, "salary_note": "SEEK树艺师 $75k~$85k；Indeed树艺师均值 $79,206；Glassdoor $72,743（2026）", "sort_order": 1},
    {"experience": "高级/攀爬树艺师（4~10年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "Climbing Arborist（高空攀爬）薪资溢价显著；全国极度短缺", "sort_order": 2},
    {"experience": "树木顾问/树艺主管（8年+）", "salary_min": 100000, "salary_max": 150000, "salary_note": "持证树木顾问（AQF5+）为建设项目提供树木保护报告", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，MLTSSL在列；树艺公司和市政绿化公司担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，满3年后申请", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列；Vetassess评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名（NSW/VIC/QLD等绿化重点州）", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区树艺师极度短缺；加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "树木知识（植物学/土壤）+高空作业安全+重型设备操作综合要求"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "Cert III学徒制约2~3年；高级资质需额外1~2年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Vetassess评估需工作经验；高空攀爬证书有实操考核"},
    {"dimension": "job_demand",               "label_zh": "较高", "stars": 4, "note": "MLTSSL短缺职业；城市树木保护法规推动持续需求；Climbing Arborist全国短缺"},
    {"dimension": "competition",              "label_zh": "低", "stars": 2, "note": "高空攀爬树艺师供不应求；持证树艺师就业率高"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 4, "note": "高空体力工作；安全风险高；季节性强度变化大"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "有经验 $70k~$92k；高空攀爬 $85k~$115k；顾问 $100k~$150k"},
    {"dimension": "future_prospect",          "label_zh": "较好", "stars": 4, "note": "城市绿化立法和基础设施保护推动稳定增长；环境修复需求持续"},
    {"dimension": "ai_risk",                  "label_zh": "很低", "stars": 1, "note": "高空体力作业和现场树木健康判断是AI无法替代的；AI辅助树木病害识别"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列；491偏远路径顺畅；雇主担保活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "MLTSSL短缺职业；持证Climbing Arborist PR最顺畅"},
]
SUITABILITY_FIT = ["持有Certificate III in Arboriculture或林业相关资质，有2年以上树艺/林业实操经验", "体能良好，无恐高症，适合高空作业（Climbing Arborist方向对体能要求较高）", "持有链锯操作证书和White Card（或愿意在入职前取得）", "有意向在城市绿化密集区（悉尼/墨尔本/布里斯班）或偏远林业区工作", "愿意在偏远地区（农村/林区）工作以加速PR（491路径偏远树艺师极度短缺）"]
SUITABILITY_UNFIT = ["对高空作业有严重恐高症或不适合体力密集型户外工作", "期望通过树艺/林业职业进入室内白领工作（树艺本质是户外体力职业）", "完全没有任何植物、树木或户外工作背景，且不愿参加2~3年的学徒培训"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "树艺师薪资 $75k~$85k（2026）", "url": "https://au.seek.com/career-advice/role/arborist/salary"},
    {"source_name": "Indeed AU", "content": "树艺师均值 $79,206（2026）", "url": "https://au.indeed.com/career/arborist/salaries"},
    {"source_name": "Glassdoor AU", "content": "树艺师均值 $72,743（2026）", "url": "https://www.glassdoor.com.au/Salaries/arborist-salary-SRCH_KO0,8.htm"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲树艺师/林业工人工资多少？", "answer": "初级树艺学徒/林业工人约 $55k~$68k；有经验树艺师约 $70k~$92k（SEEK $75k~$85k；Indeed $79,206；Glassdoor $72,743）；高空攀爬树艺师（Climbing Arborist）约 $85k~$115k；树木顾问约 $100k~$150k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲树艺师容易找工作吗？", "answer": "容易。MLTSSL短缺职业，高空攀爬树艺师全国极度短缺。城市树木保护法规严格（悉尼/墨尔本每个涉树工程必须聘用持证树艺师），SEEK常年300~800+职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国林业/园林经验澳洲认可吗？", "answer": "通过Vetassess技能评估，中国林业院校学历和园林绿化工作经验可以认可（需3年以上）。Certificate III in Arboriculture是澳洲的补充资质（2~3年学徒制）。中国的树木修剪和城市绿化经验在澳洲有参考价值。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "树艺师会被AI替代吗？", "answer": "风险极低。高空链锯修剪、树木移除和现场安全判断是需要实体体力操作的工作，完全无法自动化。AI辅助树木病害识别（图像分析）可提升诊断效率，但不影响树艺师的核心执行工作。树艺是公认的AI替代风险最低的职业之一。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲树艺师有年龄限制吗？", "answer": "无明确年龄上限，但高空攀爬（Climbing Arborist）对体能要求较高，通常适合35岁以下。有丰富经验的资深树木顾问（40~55岁）在建设项目树木报告方面非常受欢迎（主要坐办公室的顾问角色）。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲树艺师需要什么资质？", "answer": "Certificate III in Arboriculture是行业标准资质（2~3年学徒制）；链锯操作证书和White Card是实际工作的基础要求。无需大学学历。高空攀爬树艺师（AQF Level 5）薪资显著更高。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲树艺师认证（移民）难吗？", "answer": "难度较低。树艺师在MLTSSL，PR路径顺畅。偏远地区491是最便捷通道；NSW和VIC等城市绿化密集州积极提名190；雇主担保482也活跃。主要挑战是Vetassess评估时间（3~6个月）和Certificate III资质准备。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "树艺师和农业技术员哪个澳洲发展更好？", "answer": "农业技术员就业市场更大、薪资更高（$78k~$100k vs 树艺师 $70k~$92k），AgTech技术革命带来更多高薪晋升机会；树艺师AI替代风险更低，高空攀爬方向薪资也可观（$85k~$115k）。喜欢城市工作和树木护理选树艺师；有农学背景和技术兴趣选农业技术员。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 林业工人/树艺师数据入库完成")

if __name__ == "__main__":
    run()
