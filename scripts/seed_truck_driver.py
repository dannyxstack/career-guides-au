"""澳洲卡车司机（733111）数据入库。数据来源：JSA、SEEK、Indeed、ERI、ATA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "733111", "anzsco_title": "Truck Driver (General)",
    "category": "技工", "workforce_size": 200000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Long-Haul Freight & Road Trains","Mining & Resources FIFO Haulage","E-commerce Last-Mile Delivery","Refrigerated & Dangerous Goods","Infrastructure Construction Haulage"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "卡车司机",
    "summary": "卡车司机驾驶重型货运卡车（HR/HC/MC）运输货物，覆盖城市配送、长途公路运输和矿业重型物料运输。澳大利亚物流行业庞大，卡车司机长期短缺，是技术移民中较受欢迎的运输类职业。",
    "forecast_note": "Jobs and Skills Australia 预测运输和物流行业至2030年缺口持续扩大。电商最后一公里配送和矿业运输是两大持续增量方向。",
    "trend_summary": "电商配送、矿业重型运输和基建项目驱动需求。自动驾驶卡车处于测试阶段，短期内无法在复杂公路条件下商业化替代人工驾驶。",
}
I18N_EN = {
    "locale": "en", "name": "Truck Driver",
    "summary": "Truck drivers operate heavy vehicles (HR/HC/MC licence) to transport freight across urban delivery, long-haul and mining haulage routes. Australia's logistics sector sustains persistent shortages.",
    "forecast_note": "JSA projects widening supply gaps in transport and logistics through 2030. E-commerce last-mile delivery and mining haulage are the primary growth segments.",
    "trend_summary": "E-commerce delivery, mining haulage and infrastructure projects drive demand. Autonomous trucks are in testing phases but will not commercially replace human drivers in complex conditions in the near term.",
}
EDUCATION = [
    {"stage": "重型车驾驶执照培训（HR / HC / MC Licence）", "duration": "1~4周（视执照类型）", "cost_min": 1500, "cost_max": 5000, "cost_note": "HR 约 $1,500~$2,500；HC 约 $2,500~$4,000；MC（Road Train）约 $4,000~$5,000+", "sort_order": 0},
    {"stage": "危险品运输资质（ADG / DG Licence）", "duration": "1~2天", "cost_min": 300, "cost_max": 600, "cost_note": "运输危险品的额外资质，薪资溢价", "sort_order": 1},
    {"stage": "Certificate III in Driving Operations（可选）", "duration": "3~6个月", "cost_min": 0, "cost_max": 800, "cost_note": "各州补贴，提升就业竞争力", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Heavy Rigid Licence (HR)", "issuer": "各州交通局 / TMC", "note": "驾驶刚性重型卡车的标准执照", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Heavy Combination Licence (HC)", "issuer": "各州交通局 / TMC", "note": "驾驶半挂卡车/拖挂车的执照，薪资提升显著", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Multi-Combination Licence (MC)", "issuer": "各州交通局 / TMC", "note": "驾驶Road Train（公路列车），WA长途运输必须", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Dangerous Goods Certificate (ADG)", "issuer": "认可RTO", "note": "运输危险品额外资质，薪资溢价10~15%", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 5000, "count_max": 9000, "note": "全国，含城市配送、长途和矿业运输，是挂牌量最多的职业之一"},
    {"platform": "Indeed",   "count_min": 3000, "count_max": 5000, "note": "含兼职、合同工和过夜长途"},
    {"platform": "LinkedIn", "count_min": 500,  "count_max": 1200, "note": "偏物流企业直招和车队管理岗"},
]
SALARIES = [
    {"experience": "新手 HR 司机（0~2年）", "salary_min": 55000, "salary_max": 70000, "salary_note": "城市配送，Road Transport Award 最低工资", "sort_order": 0},
    {"experience": "HC 司机（2~5年）", "salary_min": 70000, "salary_max": 88000, "salary_note": "半挂拖运，含夜班/长途溢价", "sort_order": 1},
    {"experience": "HC/MC 长途司机（5年+）", "salary_min": 88000, "salary_max": 110000, "salary_note": "Indeed 全国平均约 $37.63/hr（约 $78k~$85k）；HC+加班约 $95k", "sort_order": 2},
    {"experience": "Road Train MC 司机（WA）", "salary_min": 100000, "salary_max": 130000, "salary_note": "WA 公路列车（Road Train）MC执照司机薪资最高", "sort_order": 3},
    {"experience": "矿业 FIFO 重型运输司机（WA/QLD）", "salary_min": 120000, "salary_max": 170000, "salary_note": "矿区重型车辆运输，轮班津贴+FIFO补贴", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，需CSOL在列，部分卡车司机职类已纳入", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，需较长在澳工作经验", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "部分州提名，WA对重型驾驶员有较大需求", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名，矿业和农业物流运输地区机会较多", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "取证相对简单，主要是驾驶技能和法规知识"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "HR 1周可取证；MC 约4周；远快于学徒制"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "驾驶考试通过率较高，有国内重型驾驶经验者容易通过"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "全国从业20万人仍供不应求，Seek 挂牌量最多之一"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持HC/MC证的长途司机极度短缺，矿业FIFO供需缺口尤大"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "长途过夜驾驶、夜班和疲劳驾驶是主要风险"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 3, "note": "HC长途 $88k~$110k；矿业FIFO可达 $120k~$170k"},
    {"dimension": "future_prospect",          "label_zh": "较佳", "stars": 4, "note": "电商和矿业短期需求旺盛；自动驾驶是中长期风险"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "自动驾驶卡车处于测试阶段，2030前商业化替代有限，矿区封闭路面风险更高"},
    {"dimension": "pr_friendliness",          "label_zh": "较高", "stars": 3, "note": "482/190/491路径存在，但比技工类略窄"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "PR路径相对有限，建议优先申请雇主担保或州提名"},
]
SUITABILITY_FIT = ["有重型车驾驶经验，希望快速来澳就业", "接受长途过夜驾驶或FIFO矿业运输模式", "目标是矿业高薪（$120k~$170k）或长途Road Train路线", "作为技能移民的过渡职业，取证快、就业快"]
SUITABILITY_UNFIT = ["有明显晕动症或不适合长时间驾驶", "担忧自动驾驶替代（长期看此风险真实存在）", "无法接受长途过夜或FIFO远离家庭的工作模式"]
SOURCES = [
    {"source_name": "Indeed AU", "content": "卡车司机平均时薪 $37.63（2026）", "url": "https://www.inedjobs.com/2026/05/truck-driver-salary-australia-2026.html"},
    {"source_name": "SEEK AU", "content": "卡车司机薪资及职位需求数据（2026）", "url": "https://www.seek.com.au/truck-driver-jobs"},
    {"source_name": "Australian Trucking Association", "content": "行业短缺报告和薪资标准", "url": "https://www.truck.net.au/"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲卡车司机工资多少？", "answer": "HC长途司机年薪约 $88,000~$110,000；矿业FIFO重型运输可达 $120k~$170k；Road Train MC司机在WA可达 $100k~$130k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲卡车司机容易找工作吗？", "answer": "极容易。Seek 常年挂牌 5,000~9,000 个职位，是所有职业中挂牌量最多之一，HC/MC长途司机极度短缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国重型驾照澳洲认可吗？", "answer": "不直接认可。需在澳考取对应类别（HR/HC/MC）的重型车执照，有国内重型驾驶经验者通常可较快通过考试。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "卡车司机会被自动驾驶替代吗？", "answer": "中等风险，但短期有限。自动驾驶卡车（如Rio Tinto AHS矿用卡车）已在封闭矿区运营，但公路长途运输的商业化自动驾驶2030前难以大规模普及。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲卡车司机有年龄限制吗？", "answer": "法律上无上限，但重型长途驾驶建议55岁以下。驾照无年龄限制，移民打分45岁以上无加分。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲卡车司机需要大学学历吗？", "answer": "完全不需要。持有对应类别重型车执照即可，是准入门槛最低的高薪类职业之一。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲卡车司机难学吗？", "answer": "取证难度较低。主要是驾驶技能和澳洲道路法规考试，有国内重型驾驶经验者通常 1~4周即可取证。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "卡车司机和叉车操作员哪个更适合移民澳洲？", "answer": "卡车司机薪资更高（HC ~$90k+ vs 叉车 ~$75k），PR路径更清晰，矿业FIFO高薪机会更多。叉车入门更快（1~3天取证），适合快速就业的过渡选择。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 卡车司机数据入库完成")

if __name__ == "__main__":
    run()
