"""澳洲钣金工（322211）数据入库。数据来源：JSA、ERI、Indeed、SEEK、TRA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "322211", "anzsco_title": "Sheetmetal Trades Worker", "category": "技工",
    "workforce_size": 28000, "shortage_listed": 1,
    "growth_areas": json.dumps(["HVAC Ductwork Fabrication","Mining & Industrial Equipment","Defence Shipbuilding","Renewable Energy Structures","Architectural Metalwork"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "钣金工",
    "summary": "钣金工负责切割、成型、连接和安装金属薄板制品，用于通风管道、矿业设备、建筑装饰和工业容器。澳大利亚国防造船、矿业和HVAC行业对钣金工的需求持续旺盛。",
    "forecast_note": "JSA 预测技工类至2035年新增约195,800个岗位。AUKUS国防项目和可再生能源结构件制造带动钣金工需求增长。",
    "trend_summary": "国防造船（AUKUS）、HVAC管道制造和可再生能源钢结构是三大增长方向。AI和自动化在重复性钣金加工中有一定渗透，复杂定制件仍依赖人工。",
}
I18N_EN = {
    "locale": "en", "name": "Sheetmetal Trades Worker",
    "summary": "Sheetmetal trades workers cut, shape, join and install sheet metal products for HVAC ducting, mining equipment, building and industrial applications. Defence and energy sectors sustain strong demand.",
    "forecast_note": "JSA projects ~195,800 new trades jobs by 2035. AUKUS defence projects and renewable energy fabrication drive sheetmetal demand growth.",
    "trend_summary": "Defence shipbuilding, HVAC ducting, and renewable energy structures are key growth areas. Automation affects repetitive work but complex custom fabrication remains manual.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（含 MEM30219 Certificate III in Engineering – Sheet Metal Trade）", "duration": "42~48个月", "cost_min": 0, "cost_max": 1200, "cost_note": "各州补贴，WA Lower Fees 计划上限 $1,200", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "含TRA评估费及实习期费用", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Engineering – Sheet Metal Trade (MEM30219)", "issuer": "TAFE / RTO", "note": "全国统一课程，执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Working at Heights / Confined Space Certificates", "issuer": "各州SafeWork认可RTO", "note": "施工和矿业现场作业强制安全资质", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "Trades Recognition Australia", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600,  "count_max": 1200, "note": "全国，含HVAC管道、矿业和国防岗"},
    {"platform": "Indeed",   "count_min": 400,  "count_max": 800,  "note": "含学徒岗和合同工"},
    {"platform": "LinkedIn", "count_min": 200,  "count_max": 500,  "note": "偏国防/工业企业直招岗"},
]
SALARIES = [
    {"experience": "学徒 1年级", "salary_min": 21000, "salary_max": 28000, "salary_note": "Fair Work Award 最低工资", "sort_order": 0},
    {"experience": "学徒 2~4年级", "salary_min": 28000, "salary_max": 46000, "salary_note": "约 $23~$30/hr", "sort_order": 1},
    {"experience": "初级钣金工（持证后 1~3年）", "salary_min": 65000, "salary_max": 80000, "salary_note": "ERI 初级估算", "sort_order": 2},
    {"experience": "中级钣金工（3~8年）", "salary_min": 80000, "salary_max": 105000, "salary_note": "ERI SalaryExpert 悉尼平均 $104,949；全国平均约 $85k", "sort_order": 3},
    {"experience": "资深钣金工 / 工头（8年+）", "salary_min": 105000, "salary_max": 130000, "salary_note": "含国防/精密制造溢价", "sort_order": 4},
    {"experience": "矿业 / 国防造船 FIFO", "salary_min": 120000, "salary_max": 160000, "salary_note": "国防造船（BAE Systems/ASC）和矿业岗薪资较高", "sort_order": 5},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，永居", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "基础钣金加工上手较快，精密件和复杂结构难度更高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒约4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III 考核可备考通过"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，国防和HVAC行业持续需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，精密钣金和国防资质者尤其稀缺"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "噪音、金属碎屑和高温环境常见，体力劳动"},
    {"dimension": "income_level",             "label_zh": "较高", "stars": 4, "note": "中位数约 $80k~$105k；国防造船和矿业溢价明显"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "AUKUS国防扩张、HVAC增长和可再生能源三重驱动"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "自动折弯/激光切割已应用，但复杂定制件仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，189/190/491均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估周期长"},
]
SUITABILITY_FIT = ["有金属加工/钣金/机械制造背景，希望技能移民来澳", "接受噪音和金属加工工作环境", "目标是国防造船（BAE Systems/ASC）或矿业高薪岗", "年龄28~42岁，有时间完成TRA评估"]
SUITABILITY_UNFIT = ["对金属噪音和碎屑有明显生理抵触", "期望1~2年内快速取得资质", "完全无金属加工基础"]
SOURCES = [
    {"source_name": "ERI SalaryExpert", "content": "钣金工悉尼平均年薪 $104,949（2026）", "url": "https://www.erieri.com/salary/job/sheet-metal-worker/australia/sydney"},
    {"source_name": "TRA", "content": "海外钣金工技能评估", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲钣金工工资多少？", "answer": "中级钣金工年薪约 $80,000~$105,000，ERI 悉尼平均 $104,949（2026）。国防造船和矿业高薪岗可达 $120k~$160k，学徒约 $21k~$46k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲钣金工容易找工作吗？", "answer": "容易。MLTSSL在列，AUKUS国防项目和HVAC行业持续需求，Seek 挂牌 600~1,200 个职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国钣金工经验澳洲认可吗？", "answer": "不直接认可，需通过 TRA Job Ready Program 评估，周期约12~18个月。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "钣金工会被机器人替代吗？", "answer": "部分替代，但整体风险偏低。自动折弯和激光切割已在标准件生产中广泛应用，但复杂定制件和现场安装仍需人工。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲钣金工有年龄限制吗？", "answer": "无法律上限。35岁以上可走TRA互认路径，移民打分45岁以上无加分。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲钣金工需要大学学历吗？", "answer": "不需要。完成 Certificate III 即可执业，高中毕业可直接申请学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲钣金工难学吗？", "answer": "难度中等。基础折弯和切割上手较快，精密件和复杂结构需要更多训练，有国内金属加工基础者适应较快。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "钣金工和焊工哪个更适合移民澳洲？", "answer": "两者均在MLTSSL，薪资和路径相近。焊工就业量更大（Seek ~2,500 vs 钣金工 ~1,000）；钣金工在国防造船和HVAC领域有独特优势。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 钣金工数据入库完成")

if __name__ == "__main__":
    run()
