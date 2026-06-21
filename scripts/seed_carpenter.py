"""澳洲木工（331212）数据入库。数据来源：JSA、Indeed、SEEK、ERI、TRA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "331212", "anzsco_title": "Carpenter and Joiner", "category": "技工",
    "workforce_size": 90000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Construction Boom","Commercial Fit-out & Refurbishment","Prefab & Modular Housing","Heritage & Restoration","Infrastructure & Civil Works"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "木工",
    "summary": "木工负责安装、修缮木结构框架、门窗、地板、橱柜和室内装修，广泛服务于住宅建设、商业装修和基础设施领域。在澳大利亚，木工持 Certificate III 执业，长期列入技术短缺清单。",
    "forecast_note": "JSA 预测建筑行业木工至2035年新增约195,800个技工类岗位（+9.8%）。住宅建设热潮和老旧建筑翻新需求持续推高招聘量。",
    "trend_summary": "预制模块化住宅、可持续建材应用和旧建筑翻新是三大增长方向。AI替代风险极低，现场施工高度依赖人工判断。",
}
I18N_EN = {
    "locale": "en", "name": "Carpenter",
    "summary": "Carpenters construct and install timber frameworks, doors, windows, floors and fittings across residential, commercial and civil sectors. Certificate III is the standard entry qualification.",
    "forecast_note": "JSA projects ~195,800 new trades jobs by 2035 (+9.8%). The housing construction boom and renovation demand sustain strong recruitment volumes.",
    "trend_summary": "Prefab/modular housing, sustainable materials, and heritage restoration are growth areas. AI replacement risk is very low.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（含 CPC30220 Certificate III in Carpentry）", "duration": "42~48个月", "cost_min": 0, "cost_max": 1500, "cost_note": "各州补贴差异，NSW/QLD 大部分学费补贴；WA 上限 $1,200", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "含TRA评估费及实习期费用", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Carpentry (CPC30220)", "issuer": "TAFE / RTO", "note": "全国统一课程，执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card (CPCCWHS1001)", "issuer": "认可RTO", "note": "建筑工地安全强制持卡", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "Trades Recognition Australia", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 3500, "note": "全国，含学徒岗、住宅框架和商业装修岗"},
    {"platform": "Indeed",   "count_min": 1200, "count_max": 2000, "note": "含兼职、合同工"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 900,  "note": "偏企业直招及项目管理岗"},
]
SALARIES = [
    {"experience": "学徒 1年级", "salary_min": 22000, "salary_max": 29000, "salary_note": "Fair Work Award 最低工资", "sort_order": 0},
    {"experience": "学徒 2~4年级", "salary_min": 29000, "salary_max": 48000, "salary_note": "约 $24~$31/hr", "sort_order": 1},
    {"experience": "初级木工（持证后 1~3年）", "salary_min": 68000, "salary_max": 82000, "salary_note": "SEEK/Indeed 25th percentile", "sort_order": 2},
    {"experience": "中级木工（3~8年）", "salary_min": 82000, "salary_max": 105000, "salary_note": "Indeed 平均 $47.85/hr（约 $99k/yr）", "sort_order": 3},
    {"experience": "资深木工 / 工头（8年+）", "salary_min": 105000, "salary_max": 130000, "salary_note": "含工地管理职责及承包利润", "sort_order": 4},
    {"experience": "矿业 FIFO 木工（WA/QLD）", "salary_min": 120000, "salary_max": 160000, "salary_note": "轮班津贴 + FIFO 补贴", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，TRT流需持482满2年", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，永居，首选路线", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "基础木工上手较快，精细装修和特种木工难度更高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒约4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III 考核可备考通过；White Card 简单"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，住宅建设热潮持续推高需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，持证后通常数周内可找到工作"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "体力劳动，高空、粉尘和噪音环境常见"},
    {"dimension": "income_level",             "label_zh": "较高", "stars": 4, "note": "中位数约 $85k~$100k；矿业FIFO可达 $160k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "住宅建设、翻新市场和基础设施项目持续驱动"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场施工和精细装修高度依赖人工判断"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，多路径均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估周期长；各州持牌要求有差异"},
]
SUITABILITY_FIT = [
    "有建筑/木工/家具制造背景，希望技能移民来澳",
    "接受体力劳动，不抵触户外施工和粉尘环境",
    "目标是矿业高薪或自建建筑承包公司",
    "年龄30~42岁，有时间完成TRA评估",
]
SUITABILITY_UNFIT = [
    "对粉尘、高空或噪音环境有明显生理抵触",
    "期望1~2年内快速取得资质",
    "完全无木工或建筑基础",
]
SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 331212 职业档案与短缺清单", "url": "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/331212-carpenters-and-joiners"},
    {"source_name": "training.gov.au", "content": "CPC30220 Certificate III in Carpentry", "url": "https://training.gov.au/Training/Details/CPC30220"},
    {"source_name": "Indeed AU", "content": "木工平均时薪 $47.85（2026）", "url": "https://au.indeed.com/career/carpenter/salaries"},
    {"source_name": "TRA", "content": "海外木工技能评估", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲木工工资多少？", "answer": "中级木工年薪约 $82,000~$105,000，Indeed 平均 $47.85/hr（约 $99k）。矿业FIFO可达 $120k~$160k，学徒约 $22k~$48k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲木工容易找工作吗？", "answer": "容易。MLTSSL在列，Seek 常年挂牌 2,000~3,500 个职位，住宅建设热潮使需求持续旺盛。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国木工证澳洲认可吗？", "answer": "不直接认可，需通过 TRA Job Ready Program 评估，周期约12~18个月。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "木工会被AI替代吗？", "answer": "替代风险极低。现场施工和精细装修高度依赖人工，无成熟自动化方案可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲木工有年龄限制吗？", "answer": "无法律上限。35岁以上可走TRA互认路径跳过学徒期，移民打分45岁以上无加分。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲木工需要大学学历吗？", "answer": "不需要。完成 Certificate III（CPC30220）即可执业，高中毕业可直接申请学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲木工难学吗？", "answer": "难度中等。基础框架结构上手较快，精细装修和木工设计需要更多训练，有国内建筑基础者适应较快。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "木工和水管工哪个更适合移民澳洲？", "answer": "两者均在MLTSSL，路径相近。水管工薪资略高（中位~$95k vs 木工~$90k）；木工就业量更大，竞争度相当。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 木工数据入库完成")

if __name__ == "__main__":
    run()
