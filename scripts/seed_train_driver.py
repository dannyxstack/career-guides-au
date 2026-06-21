"""澳洲火车驾驶员（731111）数据入库。数据来源：JSA、SEEK、Indeed、ONRSR、ARTC（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "731111", "anzsco_title": "Train and Tram Driver",
    "category": "技工", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Heavy Haul Mining Railway (WA/QLD)","Passenger Metro & Suburban Rail","Light Rail & Tram Expansion","Freight Rail Logistics","Cross-Country Rail Network"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "火车驾驶员",
    "summary": "火车驾驶员操作货运和客运铁路机车，覆盖矿业重载铁路（WA/QLD）、城市地铁/郊区铁路和州际货运线路。澳大利亚矿业铁路对火车驾驶员的需求极为旺盛，薪资是运输类最高之一。",
    "forecast_note": "澳洲矿业铁路扩建（WA皮尔巴拉地区）和城市轻轨扩展持续推高驾驶员需求。从业人数少（约12,000人），供需缺口持续。",
    "trend_summary": "矿业重载铁路（力拓、BHP、FMG等）是最高薪资方向，年薪可达 $150k~$200k+。城市客运铁路则为稳定政府就业路径。",
}
I18N_EN = {
    "locale": "en", "name": "Train Driver",
    "summary": "Train and tram drivers operate freight and passenger rail vehicles across mining heavy-haul networks, metropolitan rail and interstate freight. Mining railway roles in WA/QLD offer the highest salaries in the transport sector.",
    "forecast_note": "WA mining railway expansion and urban light rail projects sustain persistent demand. With only ~12,000 practitioners, the supply gap is significant.",
    "trend_summary": "Heavy-haul mining railways (Rio Tinto, BHP, FMG) offer the highest salaries ($150k~$200k+). Urban passenger rail provides stable government employment.",
}
EDUCATION = [
    {"stage": "铁路运营培训（雇主内部带薪培训）", "duration": "6~12个月", "cost_min": 0, "cost_max": 0, "cost_note": "大多数铁路公司提供全薪内部培训，无需自费；矿业公司（力拓/BHP）有专项学员计划", "sort_order": 0},
    {"stage": "Certificate III in Rail Operations (TLI32416)（可选）", "duration": "6~18个月", "cost_min": 0, "cost_max": 2000, "cost_note": "部分州补贴，雇主通常承担培训费", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Train Driver Competency Certificate（各运营商颁发）", "issuer": "各铁路运营商 / ONRSR认可机构", "note": "ONRSR框架下，各运营商独立颁发，不通用", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Safeworking Competency Certificate", "issuer": "各铁路运营商", "note": "铁路安全工作规程资质，强制要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Medical Fitness Certificate（Category 1）", "issuer": "铁路医疗认可机构", "note": "视力、色觉、听力和药物测试均需达标", "is_mandatory": 1, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 200,  "count_max": 500,  "note": "全国，含矿业重载、客运地铁和货运线路岗"},
    {"platform": "Indeed",   "count_min": 100,  "count_max": 300,  "note": "含学员和正驾驶岗"},
    {"platform": "LinkedIn", "count_min": 50,   "count_max": 150,  "note": "偏矿业公司直招岗"},
]
SALARIES = [
    {"experience": "学员驾驶员（培训期）", "salary_min": 55000, "salary_max": 72000, "salary_note": "带薪内部培训，部分运营商支付全额正式工资", "sort_order": 0},
    {"experience": "初级驾驶员（取证后 1~3年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "客运城市铁路，政府雇主薪资较稳定", "sort_order": 1},
    {"experience": "中级驾驶员（3~8年）", "salary_min": 95000, "salary_max": 125000, "salary_note": "SEEK 区间约 $100k~$120k；含班次补贴和加班", "sort_order": 2},
    {"experience": "资深驾驶员（8年+）", "salary_min": 125000, "salary_max": 150000, "salary_note": "含全夜班津贴、资历加薪和工龄奖金", "sort_order": 3},
    {"experience": "矿业重载火车驾驶员（WA/QLD）", "salary_min": 140000, "salary_max": 210000, "salary_note": "力拓/BHP/FMG矿业铁路FIFO，是运输类薪资最高职业", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，矿业铁路公司常走此路径招募海外驾驶员", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，TRT流需持482满2年", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "部分州提名，WA矿业州需求较大", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿业铁路地区，提名加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "铁路规程和信号系统理论有一定难度，实操培训较系统"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "带薪培训6~12个月，快于传统学徒制"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "医疗体检严格（色觉/视力），安全规程考核要求高"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "从业人数少（约12,000），矿业铁路持续缺人"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "矿业铁路驾驶员极度稀缺，有经验者竞争极低"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "久坐驾驶，夜班轮班常见；矿业FIFO生活节奏独特"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "矿业重载铁路 $140k~$210k，是运输类薪资最高职业"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "矿业铁路扩建和城市轻轨扩展双轮驱动"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "矿业无人驾驶列车（力拓AutoHaul）已商业运营，城市客运铁路自动化较慢"},
    {"dimension": "pr_friendliness",          "label_zh": "较高", "stars": 3, "note": "482/190/491路径可用，但比传统技工类略窄"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "资质体系雇主专属，跨雇主跨州就业需重新培训"},
]
SUITABILITY_FIT = ["有铁路/重型运输驾驶经验，希望进入矿业高薪岗位", "接受FIFO轮班（矿业铁路）或夜班（客运铁路）", "体检达标（色觉/视力/听力均无问题）", "目标是矿业重载铁路（$140k~$210k）"]
SUITABILITY_UNFIT = ["色觉或视力无法达到铁路医疗 Category 1 标准", "无法接受FIFO或夜班", "担忧矿业无人驾驶替代趋势（力拓AutoHaul等已商业运营）"]
SOURCES = [
    {"source_name": "ONRSR", "content": "澳洲国家铁路安全监管机构，驾照资质框架", "url": "https://www.onrsr.com.au/"},
    {"source_name": "SEEK AU", "content": "火车驾驶员薪资及职位需求数据（2026）", "url": "https://www.seek.com.au/"},
    {"source_name": "Rio Tinto AutoHaul", "content": "矿业无人驾驶列车商业运营情况", "url": "https://www.riotinto.com/en/operations/australia/pilbara"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲火车驾驶员工资多少？", "answer": "矿业重载火车驾驶员年薪约 $140,000~$210,000+（力拓/BHP/FMG，FIFO）；城市客运铁路约 $95,000~$125,000。是运输类薪资最高的职业。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲火车驾驶员容易找工作吗？", "answer": "矿业铁路极容易。WA矿业铁路驾驶员长期短缺，从业人数约12,000人，矿业铁路公司常赴海外招募。城市客运铁路竞争稍高。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国火车驾驶证澳洲认可吗？", "answer": "不直接认可。澳洲铁路资质体系为雇主专属，需通过各铁路公司的内部培训取证。有铁路驾驶经验者通常可获优先培训机会。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "火车驾驶员会被自动驾驶替代吗？", "answer": "矿业重载铁路风险较高（力拓AutoHaul已全面运营无人驾驶列车）；城市客运铁路受安全法规保护，全自动运营推进较慢，短期内人工驾驶仍是主流。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲火车驾驶员有年龄限制吗？", "answer": "无法律上限，但需定期通过医疗体检（含视力/色觉）。矿业公司通常要求40岁以下以满足FIFO体能要求。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲火车驾驶员需要大学学历吗？", "answer": "不需要。铁路公司内部培训即可，多数接受高中毕业加培训。部分雇主要求 Certificate III in Rail Operations。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲火车驾驶员难学吗？", "answer": "难度中等。铁路信号规程和紧急处置程序需要系统学习，但实操技能上手较快，雇主提供全薪培训，压力远低于考取独立技工资质。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "火车驾驶员和卡车司机哪个更适合移民澳洲？", "answer": "矿业铁路驾驶员薪资显著高于卡车司机（$140k~$210k vs $78k~$170k）；但铁路取证依赖雇主，自主性低于卡车。卡车可自主接单，铁路就业更稳定。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 火车驾驶员数据入库完成")

if __name__ == "__main__":
    run()
