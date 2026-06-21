"""澳洲屋顶工/屋顶水管工（334113）数据入库。数据来源：JSA、Indeed、SEEK、ERI、TRA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "334113", "anzsco_title": "Roof Plumber", "category": "技工",
    "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Construction & Renovation","Solar Panel Roof Integration","Commercial Roofing & Waterproofing","Storm Damage Repair","Green Roof & Rainwater Harvesting"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "屋顶工",
    "summary": "屋顶工（Roof Plumber）负责安装和维护金属屋顶、排水天沟、落水管和防水系统，广泛服务于住宅、商业建筑。在澳大利亚，屋顶工需持 Certificate III 执业，列入技术短缺清单，住宅建设和太阳能屋顶集成驱动持续需求。",
    "forecast_note": "JSA 预测建筑类技工至2035年新增约195,800个岗位（+9.8%）。住宅建设热潮和太阳能屋顶安装激增推高屋顶工招聘量。",
    "trend_summary": "太阳能屋顶整合、绿色建筑防水系统和老旧屋顶翻新是三大增长方向。AI替代风险极低，屋顶高空作业高度依赖人工。",
}
I18N_EN = {
    "locale": "en", "name": "Roof Plumber",
    "summary": "Roof plumbers install and maintain metal roofing, gutters, downpipes and stormwater systems on residential and commercial buildings. Certification is mandatory across all states.",
    "forecast_note": "JSA projects ~195,800 new trades jobs by 2035 (+9.8%). Solar roof integration and housing construction sustain strong demand.",
    "trend_summary": "Solar panel roofing integration, waterproofing systems, and roof renovation are key growth areas. AI replacement risk is very low.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（含 CPC32720 Certificate III in Roof Plumbing）", "duration": "42~48个月", "cost_min": 0, "cost_max": 1200, "cost_note": "各州补贴，NSW 大部分免费，WA 上限 $1,200", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "含TRA评估费及实习期费用", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Roof Plumbing (CPC32720)", "issuer": "TAFE / RTO", "note": "全国统一课程，执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Roof Plumber Licence（各州）", "issuer": "各州 Fair Trading / Building Commission", "note": "合法施工强制持牌", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Working at Heights Certificate", "issuer": "各州SafeWork认可RTO", "note": "屋顶高空作业强制安全资质", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "Trades Recognition Australia", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 500,  "count_max": 1000, "note": "全国，含住宅、商业和太阳能屋顶岗"},
    {"platform": "Indeed",   "count_min": 300,  "count_max": 600,  "note": "含学徒岗"},
    {"platform": "LinkedIn", "count_min": 100,  "count_max": 300,  "note": "偏项目管理岗"},
]
SALARIES = [
    {"experience": "学徒 1年级", "salary_min": 21000, "salary_max": 28000, "salary_note": "Fair Work Award 最低工资", "sort_order": 0},
    {"experience": "学徒 2~4年级", "salary_min": 28000, "salary_max": 46000, "salary_note": "约 $23~$30/hr", "sort_order": 1},
    {"experience": "初级屋顶工（持牌后 1~3年）", "salary_min": 70000, "salary_max": 86000, "salary_note": "Indeed 25th percentile", "sort_order": 2},
    {"experience": "中级屋顶工（3~8年）", "salary_min": 86000, "salary_max": 108000, "salary_note": "SEEK 区间 $95k~$115k；ERI 平均 $83,977；Indeed $43.89/hr", "sort_order": 3},
    {"experience": "资深屋顶工 / 承包商（8年+）", "salary_min": 108000, "salary_max": 135000, "salary_note": "含承包商利润和商业屋顶项目", "sort_order": 4},
    {"experience": "矿业 / 大型工业屋顶 FIFO", "salary_min": 120000, "salary_max": 160000, "salary_note": "高空危险津贴 + 轮班补贴", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，永居", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "金属加工和防水系统有一定难度，高空安全规范须严格遵守"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒约4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "各州持牌独立；高空作业额外资质"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，太阳能屋顶安装激增推高需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "屋顶工从业人数少（约18,000），供不应求"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 5, "note": "高温高空作业，夏季极端气候下工作强度大"},
    {"dimension": "income_level",             "label_zh": "较高", "stars": 4, "note": "中位数约 $86k~$108k，高于一般建筑技工"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "太阳能屋顶、绿色建筑和住宅建设热潮三重驱动"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "高空作业和复杂屋顶结构无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，189/190/491均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估周期长，从业人数少导致评估案例较少"},
]
SUITABILITY_FIT = [
    "有建筑/金属加工/屋顶施工背景，希望技能移民来澳",
    "接受高空作业和极端气候（夏季高温屋顶），体力好",
    "目标是自建屋顶承包公司或太阳能屋顶集成方向",
    "年龄25~40岁，有体力优势应对高强度高空作业",
]
SUITABILITY_UNFIT = [
    "有恐高症或平衡问题",
    "对极端气候（夏季高温屋顶）有明显生理抵触",
    "期望低强度室内工作环境",
]
SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 334113 职业档案与短缺清单", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "SEEK AU", "content": "屋顶工薪资区间 $95k~$115k（2026）", "url": "https://www.seek.com.au/career-advice/role/roofer/salary"},
    {"source_name": "ERI SalaryExpert", "content": "屋顶工平均年薪 $83,977（2026）", "url": "https://www.salaryexpert.com/salary/job/roofer/australia"},
    {"source_name": "Indeed AU", "content": "屋顶工平均时薪 $43.89（2026）", "url": "https://au.indeed.com/career/roofer/salaries"},
    {"source_name": "TRA", "content": "海外屋顶工技能评估", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲屋顶工工资多少？", "answer": "中级屋顶工年薪约 $86,000~$108,000，SEEK 区间 $95k~$115k（2026）。承包商和矿业高空岗可达 $120k~$160k，学徒约 $21k~$46k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲屋顶工容易找工作吗？", "answer": "容易。从业人数少（约18,000人），供不应求，Seek 挂牌 500~1,000 个职位，太阳能屋顶安装激增额外推高需求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国建筑经验澳洲认可吗？", "answer": "不直接认可，需通过 TRA Job Ready Program 评估，周期约12~18个月。有金属板金或建筑背景有助于缩短评估时间。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "屋顶工会被机器人替代吗？", "answer": "替代风险极低。高空复杂屋顶施工和防水系统安装无法自动化，且每个屋顶结构各不相同，需人工判断。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲屋顶工有年龄限制吗？", "answer": "无法律上限，但高空重体力性质建议40岁以下。35岁以上可走TRA互认路径，转向监理或质检岗位发展。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲屋顶工需要大学学历吗？", "answer": "不需要。完成 Certificate III（CPC32720）即可执业，高中毕业可直接申请学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲屋顶工难学吗？", "answer": "难度中等。金属加工和防水系统有一定理论，高空安全规范须严格遵守，有建筑基础者3~6个月可入门。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "屋顶工和水管工哪个更适合移民澳洲？", "answer": "水管工从业人数更多（~85,000 vs 18,000），就业机会更广；屋顶工供需缺口更尖锐，薪资竞争力相当。两者PR路径相同。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 屋顶工数据入库完成")

if __name__ == "__main__":
    run()
