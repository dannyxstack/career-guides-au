"""澳洲供应链经理（133611）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "133611", "anzsco_title": "Supply and Distribution Manager",
    "category": "商业/金融/法律", "workforce_size": 48000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Supply Chain Technology & Digital Twin","ESG & Sustainable Supply Chain","Cold Chain & Pharmaceutical Logistics","E-commerce Fulfilment Optimisation","Critical Minerals & Defence Supply Chain"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "供应链经理",
    "summary": "供应链经理统筹采购、仓储、物流和配送网络，确保产品从生产端高效流通至终端客户。后疫情时代澳洲供应链韧性建设需求和电商物流爆发推动对供应链专业人才的持续需求，是理工科背景跨入商业管理领域的高薪通道。",
    "forecast_note": "JSA预测供应链经理至2035年就业增长约11%。关键矿产战略储备、国防供应链本地化和ESG供应链合规是2025-2030年增长最快的政策驱动方向。",
    "trend_summary": "供应链数字化（Digital Supply Chain）是2025年行业核心转型，SAP S/4HANA和Oracle Supply Chain Management的专精人才需求急增。ESG供应链（可持续采购+碳足迹追踪）是上市公司供应链合规的强制方向。",
}
I18N_EN = {
    "locale": "en", "name": "Supply Chain Manager",
    "summary": "Supply chain managers coordinate procurement, warehousing, logistics and distribution networks to ensure efficient product flow from production to end customers. Post-pandemic supply chain resilience demands and e-commerce logistics growth drive sustained demand, providing a premium pathway for technical graduates transitioning into commercial management.",
    "forecast_note": "JSA projects ~11% employment growth for supply chain managers by 2035. Critical minerals strategic reserves, defence supply chain localisation and ESG supply chain compliance are the fastest-growing policy-driven directions.",
    "trend_summary": "Supply chain digitalisation is the core industry transformation in 2025. SAP S/4HANA and Oracle Supply Chain Management specialists are in acute demand. ESG supply chain (sustainable sourcing + carbon footprint tracking) is a mandatory compliance direction for listed companies.",
}
EDUCATION = [
    {"stage": "Bachelor of Supply Chain / Logistics / Business（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "或工程/商科相关学位；供应链是跨学科领域", "sort_order": 0},
    {"stage": "APICS CSCP / CPIM 认证", "duration": "3~12个月备考", "cost_min": 1500, "cost_max": 5000, "cost_note": "CSCP（供应链专业认证）考试费约 $700~$1,000；是全球最认可的供应链认证", "sort_order": 1},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须，约 $650 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "CSCP（Certified Supply Chain Professional）", "issuer": "APICS（美国生产和库存管理协会）", "note": "全球最认可的供应链专业认证，持有者薪资溢价显著", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "CPIM（Certified in Planning and Inventory Management）", "issuer": "APICS", "note": "库存和生产计划专精认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CLTD（Certified in Logistics Transportation and Distribution）", "issuer": "APICS", "note": "物流和配送专精认证", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 4000, "note": "全国，含供应链经理、物流经理、S&OP经理和采购运营经理岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 3000, "note": "含零售、制造、医疗和政府供应链岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 5000, "note": "大型零售商（Woolworths/Coles）和制造企业直招"},
]
SALARIES = [
    {"experience": "供应链分析师 / 协调员（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "供应链入门岗位起薪", "sort_order": 0},
    {"experience": "供应链经理（3~8年）", "salary_min": 100000, "salary_max": 140000, "salary_note": "SEEK 区间 $125k~$145k；Indeed 均值 $106,104（2026）", "sort_order": 1},
    {"experience": "高级供应链经理 / S&OP总监（8~15年）", "salary_min": 140000, "salary_max": 200000, "salary_note": "大型零售/制造企业供应链总监，含奖金", "sort_order": 2},
    {"experience": "VP Supply Chain / Chief Supply Chain Officer（15年+）", "salary_min": 200000, "salary_max": 400000, "salary_note": "上市公司首席供应链官，含奖金和股权激励", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，供应链经理为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，VETASSESS评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区制造/物流中心，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要跨领域知识（采购+物流+数据分析），CSCP备考有难度"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "3年学位+CSCP认证约6~12个月；总周期约3~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CSCP考试难度中等，通过率约70%；需要系统学习供应链知识体系"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL短缺职业，后疫情供应链重建和电商爆发推动持续需求"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级岗竞争一般，持CSCP+SAP/Oracle Tech的高级经理供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "供应链危机和旺季（圣诞/黑色星期五）期间强度高"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "供应链经理 $100k~$140k；S&OP总监 $140k~$200k，是商业类薪资较高的管理职业"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "供应链数字化+关键矿产+ESG合规是未来10年的三大增长引擎"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI优化路线规划和库存预测，但供应链战略、风险管理和供应商关系不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，VETASSESS评估路径清晰，雇主担保482活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "VETASSESS评估对工程/商科学历友好；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["持有供应链/物流/工程/商科相关学位，有3年以上供应链工作经验", "熟悉ERP系统（SAP/Oracle）和供应链分析工具", "英语能力达到 IELTS 6.5+", "持有或正在备考CSCP/CPIM认证", "有ESG供应链、数字化转型或关键矿产/国防供应链经验（溢价最高方向）"]
SUITABILITY_UNFIT = ["无供应链/物流/运营相关工作经验，仅有纯财务背景", "不熟悉ERP系统，无意愿学习供应链技术工具", "不适应跨部门协调和供应商关系管理的高压环境"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "供应链经理薪资 $125k~$145k（2026）", "url": "https://au.seek.com/career-advice/role/supply-chain-manager/salary"},
    {"source_name": "Indeed AU", "content": "供应链经理平均薪资 $106,104（2026）", "url": "https://au.indeed.com/career/supply-chain-manager/salaries"},
    {"source_name": "APICS", "content": "CSCP和CPIM认证信息", "url": "https://www.ascm.org/learning-development/certifications-credentials/cscp/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲供应链经理工资多少？", "answer": "供应链经理约 $100,000~$140,000（SEEK均值 $125k~$145k；Indeed $106,104）；高级S&OP总监约 $140k~$200k；首席供应链官（CSCO）约 $200k~$400k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲供应链经理容易找工作吗？", "answer": "容易。Seek 挂牌约 1,500~4,000 个职位，MLTSSL短缺职业。持CSCP+SAP/Oracle Tech的高级供应链经理供不应求，关键矿产和国防供应链方向更是新兴高需求领域。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国供应链经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国制造业或大型零售商供应链经验可以认可。CSCP是国际通用认证，在澳洲完全认可。建议强调可量化的供应链改进成果（如库存周转率、物流成本降低比例等）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "供应链经理会被AI替代吗？", "answer": "风险较低。AI优化路线规划、需求预测和库存管理，但供应链战略设计、供应商风险管理、危机应对和可持续供应链规划需要深度判断和关系能力，不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲供应链经理有年龄限制吗？", "answer": "无。资深供应链总监（40~55岁）在大型零售/制造企业中备受重视，特别是有全球供应链整合和危机管理经验者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲供应链经理需要什么学历？", "answer": "供应链/物流/工程/商科相关本科学历是VETASSESS评估基础。CSCP认证可弥补学历差异。SAP供应链模块认证对技术类供应链岗位有额外价值。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲供应链经理认证（移民）难吗？", "answer": "难度中等。VETASSESS评估路径清晰；CSCP考试难度中等，通过率约70%。雇主担保482是快速路径，大型零售商（Woolworths/Coles）和制造企业常对供应链专家提供担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "供应链经理和采购经理哪个更适合移民澳洲？", "answer": "两者均为MLTSSL短缺职业；供应链经理薪资均值略低（$106k vs 采购经理 $115k），但职位总量更大、行业覆盖更广；采购经理薪资更高、专精化更强。有全链条运营经验者选供应链经理，有强专项采购经验者选采购经理。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 供应链经理数据入库完成")

if __name__ == "__main__":
    run()
