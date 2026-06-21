"""澳洲农业技术员/农艺师（311111）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "311111", "anzsco_title": "Agricultural Technician",
    "category": "其他", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["精准农业（无人机/遥感技术应用）","农艺师（大豆/棉花/谷物作物优化）","葡萄种植技术员（澳洲葡萄酒产业）","园艺技术员（温室/水培农业）","农业数据分析师（AgTech）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "农业技术员/农艺师",
    "summary": "农业技术员和农艺师为农业生产提供技术支持，涵盖土壤分析、作物管理、灌溉系统、病虫害防治和农业机械操作。澳洲是全球重要农产品出口国（牛肉/小麦/棉花/葡萄酒）。具备精准农业（无人机/GPS技术）和数字农业技能的农业技术员需求快速增长，华裔农业技术专家在中澳农业合作项目中具有独特价值。",
    "forecast_note": "JSA预测农业技术员就业至2030年增长约8%。精准农业技术（无人机/遥感/物联网传感器）的广泛应用和气候适应性农业需求推动对技术型农业人才的需求。乳业、葡萄酒和园艺是增速最快的细分方向。",
    "trend_summary": "澳洲农业正在经历技术革命（AgTech）——无人机施肥、土壤传感器、大数据作物分析和自动灌溉系统正在取代传统劳动密集型操作。具备数字技术和传统农业结合能力的农业技术员极为紧缺，薪资溢价显著。偏远农业区（WA/QLD/NSW内陆）技术人员短缺严重，491偏远签证路径顺畅。",
}
I18N_EN = {
    "locale": "en", "name": "Agricultural Technician / Agronomist",
    "summary": "Agricultural technicians and agronomists provide technical support for agricultural production — including soil analysis, crop management, irrigation systems, pest and disease control and agricultural machinery operation. Australia is a major global agricultural exporter (beef/wheat/cotton/wine). Demand for agricultural technicians with precision agriculture (drone/GPS technology) and digital farming skills is rapidly growing. Chinese-Australian agricultural technology experts have unique value in Australia-China agricultural cooperation projects.",
    "forecast_note": "JSA projects ~8% agricultural technician employment growth by 2030. Widespread adoption of precision agriculture technology (drones/remote sensing/IoT sensors) and climate-adaptive farming needs drive demand for technical agricultural talent. Dairy, wine and horticulture are the fastest-growing sub-sectors.",
    "trend_summary": "Australian agriculture is undergoing a technology revolution (AgTech) — drone fertilisation, soil sensors, big data crop analytics and automated irrigation are replacing traditional labour-intensive operations. Agricultural technicians combining digital technology and traditional farming expertise are in critical shortage with significant salary premiums. Remote agricultural areas (WA/QLD/NSW inland) have severe technician shortages, making the 491 regional visa pathway smooth.",
}
EDUCATION = [
    {"stage": "Diploma / Bachelor of Agricultural Science（3~4年）", "duration": "3~4年", "cost_min": 25000, "cost_max": 120000, "cost_note": "主要农业院校（CSU/UQ/UWA/Adelaide）；国际生约 $25,000~$38,000/年", "sort_order": 0},
    {"stage": "Certificate III/IV in Agriculture", "duration": "6~24个月", "cost_min": 2000, "cost_max": 15000, "cost_note": "TAFE农业学院实践型资质；适合偏实操方向的农业技术员", "sort_order": 1},
    {"stage": "无人机（UAV）操作执照（RPA）", "duration": "1~3天", "cost_min": 500, "cost_max": 2000, "cost_note": "CASA颁发；精准农业无人机施肥和监测的必要资质", "sort_order": 2},
    {"stage": "Vetassess 技能评估（移民）", "duration": "3~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民学历和经验评估机构", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Agricultural Science / Diploma", "issuer": "认可农业院校", "note": "农艺师和高级农业技术员的技术移民评估基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Certificate of Registration（农药使用）", "issuer": "各州农业部门", "note": "处理和施用农药的法律要求（大多数农业岗位必要）", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "无人机（UAV）Remote Pilot Licence（RPA）", "issuer": "CASA", "note": "商业精准农业无人机操作的必要资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "驾驶执照（含重型农机操作，MR+）", "issuer": "各州道路交通局", "note": "大型农场工作的实际操作要求", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 300, "count_max": 900, "note": "全国，含农业技术员/农艺师/农业顾问/种植技术员岗"},
    {"platform": "Indeed",   "count_min": 200, "count_max": 600, "note": "含农业公司、研究机构和大型农场"},
    {"platform": "LinkedIn", "count_min": 200, "count_max": 600, "note": "AgTech公司和农业咨询公司管理技术岗"},
]
SALARIES = [
    {"experience": "初级农业技术员（0~3年）", "salary_min": 58000, "salary_max": 75000, "salary_note": "大学毕业生起薪（农业科学/园艺）", "sort_order": 0},
    {"experience": "有经验农业技术员/农艺师（3~8年）", "salary_min": 78000, "salary_max": 100000, "salary_note": "SEEK农业技术员 $80k~$90k；农艺师 $75k~$95k（2026）", "sort_order": 1},
    {"experience": "高级农艺师/技术经理（6~12年）", "salary_min": 95000, "salary_max": 130000, "salary_note": "大型农业企业技术总监；精准农业技术专家，薪资溢价显著", "sort_order": 2},
    {"experience": "农业顾问/AgTech专家（8年+）", "salary_min": 110000, "salary_max": 160000, "salary_note": "农业咨询公司高级顾问；无人机+数字农业解决方案专家", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，MLTSSL在列；农业公司和AgTech公司担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列；Vetassess评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "农业州（WA/QLD/SA/NSW）积极提名", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远农业区技术员极度短缺，是最顺畅的PR路径之一", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "农学理论+实操技术+现代数字工具综合能力；户外实践经验很重要"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "大学学位3~4年；农艺师积累实战经验需要5~8年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Vetassess评估路径清晰；证书类培训获取相对简单"},
    {"dimension": "job_demand",               "label_zh": "较高", "stars": 4, "note": "MLTSSL短缺职业；精准农业技术革命推动技术人才需求；偏远地区极度短缺"},
    {"dimension": "competition",              "label_zh": "低", "stars": 2, "note": "农业技术人才供不应求；有UAV/GIS/AgTech技能者竞争力极强"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 3, "note": "季节性高强度（作物种植/收获季）；户外工作；偏远地区生活条件"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "有经验技术员 $78k~$100k；精准农业专家 $110k~$160k；整体中等"},
    {"dimension": "future_prospect",          "label_zh": "较好", "stars": 4, "note": "AgTech革命和可持续农业需求推动长期增长；数字农业是高增长方向"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI辅助作物监测和产量预测；但实地操作、技术解决方案设计不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列；491偏远路径顺畅；农业大州积极提名"},
    {"dimension": "pr_difficulty",            "label_zh": "很低", "stars": 1, "note": "偏远农业区491是澳洲PR最顺畅的路径之一；短缺明显"},
]
SUITABILITY_FIT = ["持有农业科学/农艺/园艺相关学位或Diploma，有3年以上农业技术工作经验", "具备精准农业技术技能（无人机/GPS/GIS/土壤传感器）或强烈意愿学习AgTech", "愿意在偏远农业区（WA内陆/NSW农业区/QLD农业区）工作（491路径最顺畅）", "有农药使用资质或驾驶经验（重型农机），英语达到基本工作标准", "有在澳洲农业企业、研究机构或AgTech公司长期发展的职业规划"]
SUITABILITY_UNFIT = ["完全不愿意在农村/偏远地区生活工作（大多数农业技术岗位在城区外）", "仅有城市园艺或家庭园艺经验，无正式农业培训或商业农业实践", "期望快速获得高薪（入门薪资偏低，需要积累3~5年才能达到较好薪资水平）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "农业技术员 $80k~$90k；农艺师 $75k~$95k（2026）", "url": "https://au.seek.com/career-advice/role/agricultural-technician/salary"},
    {"source_name": "Indeed AU", "content": "农场工人均值 $73,995（2026）", "url": "https://au.indeed.com/career/farm-worker/salaries"},
    {"source_name": "SEEK AU", "content": "农艺师薪资 $75k~$95k（2026）", "url": "https://au.seek.com/career-advice/role/agronomist/salary"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲农业技术员/农艺师工资多少？", "answer": "初级约 $58k~$75k；有经验农业技术员约 $78k~$100k（SEEK $80k~$90k）；农艺师约 $75k~$95k（SEEK）；高级精准农业专家约 $110k~$160k。偏远地区通常有生活津贴。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲农业技术员容易找工作吗？", "answer": "容易，特别是有精准农业技术的专业人员。MLTSSL短缺职业，偏远农业区技术人员极度缺乏。SEEK 300~900个职位，有UAV/GIS/AgTech技能者竞争力极强。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国农业专业经验澳洲认可吗？", "answer": "通过Vetassess技能评估，中国农业科研机构、农业企业和农技推广工作经验可以认可。需要提供英文版工作证明。中国在精准农业技术方面的先进经验（无人机植保）在澳洲很有价值。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "农业技术员会被AI替代吗？", "answer": "中等风险。AI辅助的作物监测、产量预测和精准施肥正在改变农业工作方式，但实地技术解决方案制定、农机操作和农场管理决策需要人类专业判断。向AgTech专家和农业数据分析师方向发展，成为技术革命的推动者而非被替代者。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲农业技术员有年龄限制吗？", "answer": "无。有丰富农业技术经验（特别是特定作物专长，如棉花/甘蔗/葡萄）的资深农业技术专家（40~55岁）非常受欢迎。户外体能要求因职位不同而异，管理和顾问类岗位对体能要求较低。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲农业技术员需要什么学历？", "answer": "农艺师和高级技术员位通常要求农业科学或相关学位；Certificate III/IV可满足实操技术员岗位要求。最重要的是实际农业技术技能和工作经验。有无人机（UAV）执照和GIS技能是当前最受欢迎的额外资质。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲农业技术员认证（移民）难吗？", "answer": "难度低。农业技术员在MLTSSL，偏远491路径是最顺畅的PR通道之一。WA、QLD和SA等农业大州积极提名190；雇主担保482也活跃。主要挑战是偏远地区生活适应和Vetassess评估时间（3~6个月）。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "农业技术员和林业工人哪个澳洲发展更好？", "answer": "农业技术员就业市场更大（18,000人 vs 林业5,000人）、薪资更高（$78k~$100k vs $65k~$85k），AgTech技术革命带来更多高薪晋升机会；林业工人（特别是树艺师）在城市绿化和环境管理方向有稳定需求。两者都在MLTSSL，PR路径相近。有技术/数据背景者选农业技术；喜欢树木和城市环境工作者选树艺师方向。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 农业技术员/农艺师数据入库完成")

if __name__ == "__main__":
    run()
