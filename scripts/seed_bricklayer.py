"""澳洲瓦工/砖工（331111）数据入库。数据来源：JSA、Indeed、SEEK、ERI、TRA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "331111", "anzsco_title": "Bricklayer", "category": "技工",
    "workforce_size": 35000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Construction","Commercial & Industrial Buildings","Infrastructure & Civil Works","Heritage Restoration","Landscaping & Retaining Walls"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "瓦工",
    "summary": "瓦工（砖工/砌砖工）负责砌筑砖块、混凝土砌块、石材和瓷砖，用于住宅、商业建筑的墙体、地基和装饰结构。澳大利亚住宅建设热潮驱动持续旺盛的需求，瓦工长期列入技术短缺清单。",
    "forecast_note": "JSA 预测建筑类技工至2035年新增约195,800个岗位（+9.8%）。住宅建设扩张是瓦工需求的核心驱动力。",
    "trend_summary": "澳洲住宅短缺问题使建筑活动持续高位，瓦工供需缺口扩大。AI替代风险极低，砌砖和石工均高度依赖人工技能。",
}
I18N_EN = {
    "locale": "en", "name": "Bricklayer",
    "summary": "Bricklayers construct walls, partitions, arches and other structures using bricks, stone and other materials. Australia's housing construction boom sustains strong and sustained demand.",
    "forecast_note": "JSA projects ~195,800 new trades jobs by 2035 (+9.8%). Residential construction expansion is the primary demand driver for bricklayers.",
    "trend_summary": "Australia's housing shortage keeps construction activity elevated. AI replacement risk is very low; bricklaying requires skilled manual work.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（含 CPC33020 Certificate III in Bricklaying/Blocklaying）", "duration": "42~48个月", "cost_min": 0, "cost_max": 1200, "cost_note": "各州补贴，WA 上限 $1,200，NSW 大部分免费", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "含TRA评估费及实习期费用", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Bricklaying/Blocklaying (CPC33020)", "issuer": "TAFE / RTO", "note": "全国统一课程，执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card (CPCCWHS1001)", "issuer": "认可RTO", "note": "建筑工地安全强制持卡", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "Trades Recognition Australia", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600,  "count_max": 1200, "note": "全国，含住宅和商业砌砖岗"},
    {"platform": "Indeed",   "count_min": 400,  "count_max": 800,  "note": "含学徒岗"},
    {"platform": "LinkedIn", "count_min": 150,  "count_max": 400,  "note": "偏工程管理岗"},
]
SALARIES = [
    {"experience": "学徒 1年级", "salary_min": 21000, "salary_max": 28000, "salary_note": "Fair Work Award 最低工资", "sort_order": 0},
    {"experience": "学徒 2~4年级", "salary_min": 28000, "salary_max": 46000, "salary_note": "约 $23~$30/hr", "sort_order": 1},
    {"experience": "初级瓦工（持证后 1~3年）", "salary_min": 62000, "salary_max": 78000, "salary_note": "Indeed 25th percentile", "sort_order": 2},
    {"experience": "中级瓦工（3~8年）", "salary_min": 78000, "salary_max": 95000, "salary_note": "SEEK 区间 $80k~$90k；Indeed $31.36~$43.36/hr", "sort_order": 3},
    {"experience": "资深瓦工 / 承包商（8年+）", "salary_min": 95000, "salary_max": 120000, "salary_note": "含承包商利润和工地管理职责", "sort_order": 4},
    {"experience": "矿业 / 大型基建 FIFO", "salary_min": 110000, "salary_max": 150000, "salary_note": "轮班津贴 + FIFO 补贴", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，永居", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "基础砌砖上手较快，石工和装饰砌筑难度更高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒约4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Certificate III 考核相对straightforward"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，住宅建设热潮持续推高需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，持证后通常可快速入职"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 5, "note": "重体力劳动，背部和膝盖伤害风险较高"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位数约 $78k~$90k，低于电工和水管工"},
    {"dimension": "future_prospect",          "label_zh": "较佳", "stars": 4, "note": "住宅建设热潮驱动，但受地产周期影响较大"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "砌砖机器人尚处实验阶段，短期内无法取代人工"},
    {"dimension": "pr_friendliness",          "label_zh": "较高", "stars": 4, "note": "MLTSSL在列，189/190/491均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估周期长"},
]
SUITABILITY_FIT = [
    "有建筑/砌砖/泥瓦背景，希望技能移民来澳",
    "接受重体力劳动，不抵触户外施工和粉尘环境",
    "目标是积累经验后自建建筑承包公司",
    "年龄25~38岁，有体力优势完成学徒期或TRA评估",
]
SUITABILITY_UNFIT = [
    "有背部或膝盖健康问题，不适合长期重体力砌砖",
    "期望高薪快速入职（瓦工起薪低于电工和水管工）",
    "完全无建筑或砌砖基础",
]
SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 331111 职业档案与短缺清单", "url": "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/331111-bricklayers"},
    {"source_name": "SEEK AU", "content": "瓦工薪资区间 $80k~$90k（2026）", "url": "https://www.seek.com.au/career-advice/role/bricklayer/salary"},
    {"source_name": "Indeed AU", "content": "瓦工薪资 $22.52~$43.36/hr（2026）", "url": "https://au.indeed.com/career-advice/pay-salary/how-much-do-bricklayers-make"},
    {"source_name": "TRA", "content": "海外瓦工技能评估", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲瓦工工资多少？", "answer": "中级瓦工年薪约 $78,000~$95,000，SEEK 区间 $80k~$90k（2026）。承包商可达 $95k~$120k，学徒约 $21k~$46k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲瓦工容易找工作吗？", "answer": "较容易。MLTSSL在列，住宅建设热潮驱动Seek挂牌 600~1,200 个职位，持证后通常可快速入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国砌砖经验澳洲认可吗？", "answer": "不直接认可，需通过 TRA Job Ready Program 评估，周期约12~18个月。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "瓦工会被机器人替代吗？", "answer": "短期内风险极低。自动砌砖机器人（如 SAM100）已在部分工地测试，但成本高、适用范围窄，2030前人工瓦工仍是主力。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲瓦工有年龄限制吗？", "answer": "无法律上限，但重体力性质建议35岁以下从事。35岁以上可走TRA互认路径，偏向工头或质检岗位发展。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲瓦工需要大学学历吗？", "answer": "不需要。完成 Certificate III（CPC33020）即可执业，高中毕业可直接申请学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲瓦工难学吗？", "answer": "难度中等。基础砌砖上手较快，石工和装饰砌筑需要更多训练，有国内建筑基础者适应较快。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "瓦工和木工哪个更适合移民澳洲？", "answer": "两者均在MLTSSL。木工就业量更大，薪资略高；瓦工体力要求更高，但竞争度相当，PR路径相同。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 瓦工数据入库完成")

if __name__ == "__main__":
    run()
