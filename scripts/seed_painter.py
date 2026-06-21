"""澳洲油漆工（332211）数据入库。数据来源：JSA、Indeed、Glassdoor、SEEK、ERI、TRA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "332211", "anzsco_title": "Painter and Decorator", "category": "技工",
    "workforce_size": 40000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential New Build & Renovation","Commercial & Industrial Painting","Protective Coating & Corrosion Control","Aged Care & Social Housing","Infrastructure Maintenance"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "油漆工",
    "summary": "油漆工负责内外墙面、天花、木材和金属表面的涂装与装饰，广泛服务于住宅、商业建筑和基础设施领域。在澳大利亚，油漆工需持 Certificate III 执业，列入技术短缺清单，住宅翻新和新建市场需求旺盛。",
    "forecast_note": "JSA 预测建筑类技工至2035年新增约195,800个岗位（+9.8%）。住宅翻新热潮和老旧建筑维护持续驱动油漆工需求。",
    "trend_summary": "住宅建设热潮、商业翻新和政府基础设施维护是三大需求来源。工业防腐涂层（矿业/桥梁/管道）是高薪增长方向。",
}
I18N_EN = {
    "locale": "en", "name": "Painter and Decorator",
    "summary": "Painters and decorators apply paint, varnish and other finishes to interior and exterior surfaces of buildings and structures. Certificate III is the standard entry qualification.",
    "forecast_note": "JSA projects ~195,800 new trades jobs by 2035 (+9.8%). Residential renovation and new builds sustain steady recruitment demand.",
    "trend_summary": "Residential renovation, commercial refurbishment and industrial protective coatings are the key demand drivers.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（含 CPC30620 Certificate III in Painting and Decorating）", "duration": "42~48个月", "cost_min": 0, "cost_max": 1200, "cost_note": "各州补贴，NSW 大部分免费，WA 上限 $1,200", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "含TRA评估费及实习期费用", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Painting and Decorating (CPC30620)", "issuer": "TAFE / RTO", "note": "全国统一课程，执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card (CPCCWHS1001)", "issuer": "认可RTO", "note": "建筑工地安全强制持卡", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Working at Heights Certificate", "issuer": "各州SafeWork认可RTO", "note": "高空作业强制安全资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "Trades Recognition Australia", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 800,  "count_max": 1500, "note": "全国，含住宅、商业和工业防腐岗"},
    {"platform": "Indeed",   "count_min": 500,  "count_max": 900,  "note": "含学徒岗和兼职"},
    {"platform": "LinkedIn", "count_min": 200,  "count_max": 500,  "note": "偏工业防腐和项目管理岗"},
]
SALARIES = [
    {"experience": "学徒 1年级", "salary_min": 20000, "salary_max": 27000, "salary_note": "Fair Work Award 最低工资", "sort_order": 0},
    {"experience": "学徒 2~4年级", "salary_min": 27000, "salary_max": 44000, "salary_note": "约 $22~$28/hr", "sort_order": 1},
    {"experience": "初级油漆工（持证后 1~3年）", "salary_min": 60000, "salary_max": 74000, "salary_note": "Indeed 25th percentile", "sort_order": 2},
    {"experience": "中级油漆工（3~8年）", "salary_min": 74000, "salary_max": 90000, "salary_note": "Indeed 平均 $77,858；$34.39/hr", "sort_order": 3},
    {"experience": "资深油漆工 / 承包商（8年+）", "salary_min": 90000, "salary_max": 115000, "salary_note": "含承包商利润；工业防腐涂层薪资溢价明显", "sort_order": 4},
    {"experience": "工业防腐 / 矿业 FIFO", "salary_min": 110000, "salary_max": 150000, "salary_note": "矿业高空防腐岗薪资显著高于住宅油漆", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，永居", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "基础住宅油漆上手最快；工业防腐难度更高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒约4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Certificate III 考核相对简单"},
    {"dimension": "job_demand",               "label_zh": "较高", "stars": 4, "note": "MLTSSL在列，住宅翻新和新建市场需求持续"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "供需相对平衡，竞争低于电工但高于焊工"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "体力劳动，溶剂气味和高空作业是主要风险"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位数约 $74k~$85k，低于电工和水管工"},
    {"dimension": "future_prospect",          "label_zh": "较佳", "stars": 4, "note": "住宅建设、翻新和工业防腐均有增长，受周期影响较小"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场喷涂和精细装饰高度依赖人工技巧"},
    {"dimension": "pr_friendliness",          "label_zh": "较高", "stars": 4, "note": "MLTSSL在列，189/190/491均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估周期长，竞争度中等"},
]
SUITABILITY_FIT = [
    "有建筑装修/涂装背景，希望技能移民来澳",
    "不排斥溶剂气味和高空作业，能接受住宅/商业涂装环境",
    "目标是自建涂装承包公司或转向工业防腐高薪方向",
    "年龄28~42岁，有时间完成TRA评估",
]
SUITABILITY_UNFIT = [
    "对溶剂或油漆气味有化学过敏或呼吸系统问题",
    "期望高薪快速入职（油漆工起薪是技工类最低之一）",
    "完全无涂装或装修基础",
]
SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 332211 职业档案与短缺清单", "url": "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/332211-painters-and-decorators"},
    {"source_name": "Indeed AU", "content": "油漆工平均年薪 $77,858；$34.39/hr（2026）", "url": "https://au.indeed.com/career/painter/salaries"},
    {"source_name": "TRA", "content": "海外油漆工技能评估", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲油漆工工资多少？", "answer": "中级油漆工年薪约 $74,000~$90,000，Indeed 平均 $77,858（2026）。工业防腐方向可达 $110k~$150k，学徒约 $20k~$44k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲油漆工容易找工作吗？", "answer": "较容易。MLTSSL在列，Seek 常年挂牌 800~1,500 个职位，住宅翻新和新建市场持续活跃。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国涂装经验澳洲认可吗？", "answer": "不直接认可，需通过 TRA Job Ready Program 评估，周期约12~18个月。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "油漆工会被机器人替代吗？", "answer": "替代风险极低。自动喷涂机器人在标准化大型工业场所有一定应用，但住宅精细涂装和不规则表面仍高度依赖人工。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲油漆工有年龄限制吗？", "answer": "无法律上限。35岁以上可走TRA互认路径跳过学徒期，移民打分45岁以上无加分。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲油漆工需要大学学历吗？", "answer": "不需要。完成 Certificate III（CPC30620）即可执业，高中毕业可直接申请学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲油漆工难学吗？", "answer": "难度较低。基础住宅油漆是技工类中上手最快的职业之一，有国内装修涂装经验者1~3个月可入门。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "油漆工和木工哪个更适合移民澳洲？", "answer": "木工就业量更大（Seek ~3,000个 vs 油漆工 ~1,200个），薪资略高。油漆工学习难度更低，适合无技术背景但有装修涂装经验者。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 油漆工数据入库完成")

if __name__ == "__main__":
    run()
