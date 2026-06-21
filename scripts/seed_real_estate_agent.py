"""澳洲房地产经纪/物业管理（612112/612113）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "612112", "anzsco_title": "Real Estate Agent / Property Manager",
    "category": "其他", "workforce_size": 85000, "shortage_listed": 0,
    "growth_areas": json.dumps(["华裔社区房产经纪（中文服务需求旺盛）","商业地产（写字楼/零售/工业厂房）经纪","物业管理经理（公寓/商业综合体）","Strata Manager（层权管理/物业委员会）","澳洲海外华人投资物业顾问"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "房地产经纪/物业管理",
    "summary": "房地产经纪负责住宅和商业物业的买卖中介、市场推广和客户谈判；物业管理人员负责出租物业的租务管理、租客关系和维护协调；Strata Manager管理层权公寓（Strata Title）的物业委员会事务。澳洲华裔买家（新移民/投资者）占悉尼和墨尔本部分区域房产交易的重要比例，华语能力是显著竞争优势。",
    "forecast_note": "JSA预测房地产从业人员就业至2030年稳定增长约7%。澳洲房价高企（悉尼/墨尔本中位价超 $100万）使房产交易佣金收入可观。住房短缺危机持续推动租务市场旺盛，物业管理岗位需求稳定。",
    "trend_summary": "澳洲房产市场2026年保持活跃（悉尼中位价约 $150万）。华裔投资者和新移民买家在Burwood/Chatswood/Box Hill/Glen Waverley等华人聚集区占主导，华语房产经纪在这些区域极受欢迎且佣金收入丰厚。PropTech（房产科技平台Domain/REA Group）改变行业但未替代经纪核心价值。",
}
I18N_EN = {
    "locale": "en", "name": "Real Estate Agent / Property Manager",
    "summary": "Real estate agents handle residential and commercial property sales, marketing and client negotiation; property managers oversee rental property tenancy management, tenant relations and maintenance coordination; strata managers administer strata-titled apartment buildings' body corporate affairs. Chinese-Australian buyers (new migrants/investors) form a significant proportion of property transactions in parts of Sydney and Melbourne — Mandarin/Cantonese skills are a major competitive advantage.",
    "forecast_note": "JSA projects ~7% stable property industry employment growth by 2030. High Australian property prices (Sydney/Melbourne median >$1M) make commission income substantial. The housing shortage crisis maintains strong rental market activity, with stable property management demand.",
    "trend_summary": "Australia's property market remains active in 2026 (Sydney median ~$1.5M). Chinese investors and new migrant buyers dominate in Chinese-community areas (Burwood/Chatswood/Box Hill/Glen Waverley) — Mandarin-speaking agents in these areas are highly sought-after with lucrative commission income. PropTech (Domain/REA Group) is transforming the industry but has not replaced the core value of agents.",
}
EDUCATION = [
    {"stage": "Certificate IV in Property Services (Real Estate, CPP41419)", "duration": "3~6个月", "cost_min": 1500, "cost_max": 5000, "cost_note": "获取房产经纪执照的法定培训；TAFE或认可RTO提供", "sort_order": 0},
    {"stage": "房产经纪执照（Real Estate Agent Licence）", "duration": "2~4周审核", "cost_min": 300, "cost_max": 800, "cost_note": "各州Fair Trading/Consumer Affairs颁发；年费约 $200~$400", "sort_order": 1},
    {"stage": "Strata Management 证书（物业委员会管理）", "duration": "3~6个月", "cost_min": 1500, "cost_max": 5000, "cost_note": "Strata Manager（层权管理）的专业资质，NSW/VIC等州要求", "sort_order": 2},
    {"stage": "普通话/粤语能力（华语经纪核心竞争力）", "duration": "—", "cost_min": 0, "cost_max": 0, "cost_note": "在华裔聚集区的核心竞争优势；直接影响佣金收入", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Real Estate Agent Licence", "issuer": "各州 Fair Trading / Consumer Affairs", "note": "在澳洲从事房产经纪业务的法定持牌要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Certificate IV in Property Services", "issuer": "TAFE / 认可RTO", "note": "执照申请的前提培训资质", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Strata Manager Licence（NSW/VIC等）", "issuer": "各州相应监管局", "note": "Strata Manager在NSW等州需要专门执照", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "REINSW/REIV 会员资格", "issuer": "各州房地产协会", "note": "行业协会会员资格，提升专业信誉和市场网络", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 800, "count_max": 3000, "note": "全国，含房产经纪/物业管理/Strata Manager/商业地产岗"},
    {"platform": "Indeed",   "count_min": 600, "count_max": 2000, "note": "含大型中介公司（Ray White/Barry Plant/McGrath）岗"},
    {"platform": "LinkedIn", "count_min": 500, "count_max": 1500, "note": "商业地产和大型物业管理公司管理岗"},
]
SALARIES = [
    {"experience": "助理经纪/物管助理（0~2年）", "salary_min": 55000, "salary_max": 72000, "salary_note": "基本薪+佣金起步；华裔聚集区华语助理经纪起薪更高", "sort_order": 0},
    {"experience": "房地产经纪（2~7年）", "salary_min": 85000, "salary_max": 125000, "salary_note": "SEEK $90k~$110k；Indeed $91,615（含佣金，2026）", "sort_order": 1},
    {"experience": "物业管理经理（3~8年）", "salary_min": 75000, "salary_max": 100000, "salary_note": "SEEK 物业经理 $75k~$90k；Indeed $84,679（2026）", "sort_order": 2},
    {"experience": "Strata Manager（3~8年）", "salary_min": 90000, "salary_max": 120000, "salary_note": "SEEK Strata Manager $90k~$110k；Glassdoor $100,000（2026）", "sort_order": 3},
    {"experience": "明星经纪/团队领袖（8年+）", "salary_min": 150000, "salary_max": 500000, "salary_note": "悉尼/墨尔本华裔聚集区顶级经纪年收入 $200k~$500k+（含高额佣金）", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保；大型房产中介和物业管理公司担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要Vetassess技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中低", "stars": 2, "note": "入门门槛低（Certificate IV约3~6个月）；顶级经纪需要出色的人际和谈判能力"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "执照培训3~6个月；从助理到独立经纪约2~3年"},
    {"dimension": "certification_difficulty", "label_zh": "低", "stars": 1, "note": "执照获取相对容易；主要门槛是背景调查和完成培训课程"},
    {"dimension": "job_demand",               "label_zh": "较高", "stars": 4, "note": "房产市场活跃；SEEK 800~3000+职位；华语经纪在聚集区极度紧缺"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "普通英语经纪竞争一般；华语（普通话/粤语）经纪在华裔区极有竞争优势"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 3, "note": "周末必须工作（开放日/拍卖）；客户服务全天候；业绩压力大"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "经纪 $90k~$125k（含佣金）；顶级华语经纪 $200k~$500k+；波动性高"},
    {"dimension": "future_prospect",          "label_zh": "较好", "stars": 3, "note": "房产市场长期活跃；住房危机推动租市旺盛；华语市场长期增长"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI辅助市场分析和自动化文档；但客户谈判和情感信任建立是AI无法替代的"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL；雇主担保可行；Strata Manager级别更容易"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "非短缺职业，技术移民难度中等；需要雇主担保或晋升至经理级别"},
]
SUITABILITY_FIT = ["普通话/粤语流利，有意向在华裔聚集区（Chatswood/Burwood/Box Hill等）从事华语房产经纪", "已持有或愿意在3~6个月内取得澳洲房产经纪执照（Certificate IV + State Licence）", "有销售背景、金融/投资知识或澳洲房产市场了解，英语沟通流利", "有意向从物业管理入手，逐步发展成房产经纪（稳定底薪+成长型佣金路径）", "有意向考取Strata Manager资质（公寓经济繁荣，Strata Manager需求强且稳定）"]
SUITABILITY_UNFIT = ["不喜欢销售工作和以业绩为导向的收入结构（经纪薪资高度依赖佣金）", "不愿意周末工作（周六开放日/拍卖日是房产经纪的核心工作时间）", "英语和普通话表达能力不足以进行客户谈判和呈现（沟通是核心技能）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "房产经纪 $90k~$110k；物业管理 $75k~$90k；Strata Manager $90k~$110k（2026）", "url": "https://au.seek.com/career-advice/role/real-estate-agent/salary"},
    {"source_name": "Indeed AU", "content": "房产经纪均值 $91,615；物业管理均值 $84,679（2026）", "url": "https://au.indeed.com/career/real-estate-agent/salaries"},
    {"source_name": "Glassdoor AU", "content": "Strata Manager均值 $100,000（2026）", "url": "https://www.glassdoor.com.au/Salaries/strata-manager-salary-SRCH_KO0,14.htm"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲房产经纪/物业管理工资多少？", "answer": "助理经纪/物管助理约 $55k~$72k（底薪）；经纪约 $85k~$125k（SEEK $90k~$110k；Indeed $91,615含佣金）；物业经理约 $75k~$100k（Indeed $84,679）；Strata Manager约 $90k~$120k；悉尼华裔聚集区顶级华语经纪年收入 $200k~$500k+。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲房产经纪容易找工作吗？", "answer": "容易。SEEK 800~3000+职位，房产市场活跃。华语（普通话/粤语）经纪在华裔聚集区（Chatswood/Box Hill）极度紧缺，往往被直接猎头。物业管理岗位因租市旺盛需求稳定。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国房产从业经验澳洲认可吗？", "answer": "中国房产销售和物业管理经验对求职有帮助，但必须取得澳洲本地执照（Certificate IV + State Licence，约3~6个月）。华语能力和中国投资客户网络是直接竞争优势，许多大型中介公司（Ray White/Barry Plant）主动招募华语经纪。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "房产经纪会被AI替代吗？", "answer": "部分替代。AI自动化房产搜索匹配、估价分析和文档生成；但买卖双方的情感决策（最大的人生财务决定之一）、谈判策略和客户信任建立是AI无法完成的。华语服务和高端定制服务的经纪AI替代风险最低。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲房产经纪有年龄限制吗？", "answer": "无。有丰富人际网络和客户信任基础的中高年龄经纪（45~60岁）在高端物业市场非常受欢迎。房产是人脉驱动的行业，经验和客户积累随时间增值。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲房产经纪需要什么资质？", "answer": "Certificate IV in Property Services（3~6个月）+各州房产经纪执照是必须的法定要求；无需大学学历。大学学历（商科/法律/金融）有助于商业地产方向。最重要的是执照+沟通能力+市场知识+客户网络。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲房产经纪能移民吗？", "answer": "不在MLTSSL，技术移民难度中等。雇主担保482可行；建议先以学生签证/配偶签证等入境，取得执照后开始从业，积累2~3年经验后通过雇主担保推进PR。Strata Manager级别通过190州提名的机会更高。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "房产经纪和物业管理哪个澳洲发展更好？", "answer": "经纪收入弹性大（顶级经纪 $200k~$500k+）但收入不稳定（佣金制）；物业管理收入稳定（底薪 $75k~$100k）但上限较低。华语经纪在华裔聚集区收入潜力极高；物业管理和Strata Manager适合偏好稳定底薪者。有销售能力和客户网络选经纪；偏好稳定和管理选物业管理/Strata。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 房地产经纪/物业管理数据入库完成")

if __name__ == "__main__":
    run()
