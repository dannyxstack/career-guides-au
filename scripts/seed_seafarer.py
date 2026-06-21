"""澳洲船员/航海官（231212）数据入库。数据来源：JSA、SEEK、SalaryExpert（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "231212", "anzsco_title": "Marine Transport Professional",
    "category": "其他", "workforce_size": 5000, "shortage_listed": 1,
    "growth_areas": json.dumps(["液化天然气（LNG）船员（澳洲LNG出口全球第一）","海洋工程和近海石油平台支援","港口引航员（Harbour Pilot）","游轮运营（旅游复苏推动）","海洋可再生能源（海上风电）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "船员/航海官",
    "summary": "船员和航海官负责商船、油轮、LNG船和渡轮等海洋运输工具的航行操控、安全管理和货物运输。澳洲是全球最大的LNG出口国（每年约8,000万吨），海洋运输行业对持证航海官（STCW认证）需求持续旺盛，并在MLTSSL短缺职业名单上。",
    "forecast_note": "JSA预测船员就业至2030年增长约6%。澳洲LNG和铁矿石出口规模的持续扩大推动对海洋运输专业人员的需求。港湾引航员因退休潮面临严重短缺，是薪资最高的细分方向。",
    "trend_summary": "澳洲海运业受LNG和铁矿石出口驱动持续扩张，兼具稳定性和高薪。STCW（海员培训/发证/值班国际公约）证书是全球标准，中国认可的STCW证书通过AMSA可转换为澳洲证书。澳洲本地航海院校毕业生供给不足，对具有STCW资质的海外船员需求旺盛。",
}
I18N_EN = {
    "locale": "en", "name": "Seafarer / Marine Officer",
    "summary": "Seafarers and marine officers operate cargo ships, oil tankers, LNG vessels and ferries — managing navigation, safety and cargo transportation. Australia is the world's largest LNG exporter (~80 million tonnes/year), driving sustained demand for certified marine officers (STCW-certified) who appear on the MLTSSL shortage list.",
    "forecast_note": "JSA projects ~6% seafarer employment growth by 2030. Australia's continued expansion of LNG and iron ore exports drives demand for marine transport professionals. Harbour pilots face acute shortages due to retirement wave — the highest-paid sub-sector.",
    "trend_summary": "Australian maritime industry is driven by LNG and iron ore export growth, offering stability and high salaries. STCW (Standards of Training, Certification and Watchkeeping) certificates are the global standard — Chinese STCW certificates can be converted to Australian certificates through AMSA. Local maritime college graduates are insufficient to meet demand, creating strong need for overseas-trained officers with STCW qualifications.",
}
EDUCATION = [
    {"stage": "Bachelor of Maritime Operations（3年）", "duration": "3年", "cost_min": 30000, "cost_max": 100000, "cost_note": "澳洲海事学院（AMSA认可）；澳大利亚海洋学院（IMAS）是主要院校", "sort_order": 0},
    {"stage": "Certificate IV/Diploma of Maritime Operations", "duration": "12~24个月", "cost_min": 8000, "cost_max": 30000, "cost_note": "TAFE或私立海事学院；适合从低级船员晋升路径", "sort_order": 1},
    {"stage": "STCW 基础安全培训（Basic Safety Training）", "duration": "5~10天", "cost_min": 500, "cost_max": 2000, "cost_note": "所有船员的国际法定要求；包含消防/急救/溺水救生/海上求生", "sort_order": 2},
    {"stage": "AMSA 证书转换（海外持证人员）", "duration": "3~6个月", "cost_min": 500, "cost_max": 3000, "cost_note": "中国交通部认可STCW证书可通过AMSA程序转换", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "STCW Officer of the Watch（III/1 or II/1）", "issuer": "AMSA（澳洲海事安全局）", "note": "商业船舶副驾驶（大副/三副）的法定核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Master Class 5/4/2/1", "issuer": "AMSA", "note": "船长资质，按船舶吨位分级；Class 2适用于无限航区大型商船", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "STCW Basic Safety Training（BST）", "issuer": "AMSA认可培训机构", "note": "所有船员的国际法定要求", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "医疗适航证书（ENG1/Medical Fitness）", "issuer": "认可海事医疗机构", "note": "所有商业船员的健康准入要求", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 100, "count_max": 350, "note": "全国，含船长/大副/三副/轮机长岗及近海平台岗"},
    {"platform": "Indeed",   "count_min": 80, "count_max": 250, "note": "含LNG船公司、矿业海运和渡轮运营商"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 300, "note": "大型海运公司（Teekay/Woodside/BHP Marine）直招"},
]
SALARIES = [
    {"experience": "初级航海官/三副（0~3年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "商船三副或初级轮机员年薪", "sort_order": 0},
    {"experience": "大副/轮机长（3~10年）", "salary_min": 105000, "salary_max": 135000, "salary_note": "SEEK 航海工程师 $105k~$125k（2026）；Merchant Marine均值 $63,960（低端）~$120k（LNG高端）", "sort_order": 1},
    {"experience": "船长/轮机总管（8~18年）", "salary_min": 130000, "salary_max": 200000, "salary_note": "LNG/油轮船长年薪 $150k~$200k+，含海上作业津贴", "sort_order": 2},
    {"experience": "港湾引航员（Harbour Pilot）", "salary_min": 200000, "salary_max": 350000, "salary_note": "各州港湾局引航员年薪约 $200k~$350k（短缺严重，薪资最高）", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保；LNG运营商（Woodside/Shell）和大型海运公司担保活跃", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列；STCW持证人优先", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，WA（矿业海运）和QLD（LNG）积极提名", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较高", "stars": 4, "note": "航海技术、导航系统、货物管理和应急处置综合技能要求高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学位3年+海上服务时数积累约3~5年方可晋升大副/船长"},
    {"dimension": "certification_difficulty", "label_zh": "较高", "stars": 4, "note": "STCW和AMSA资质体系严格；中国证书转换有明确路径但需时间"},
    {"dimension": "job_demand",               "label_zh": "较高", "stars": 4, "note": "MLTSSL短缺职业；LNG出口和港湾引航员退休潮推动旺盛需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "澳洲本地海事毕业生不足；STCW持证海外人员竞争力强"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 4, "note": "轮班制（4小时当班/8小时休息）；长期海上作业远离家庭"},
    {"dimension": "income_level",             "label_zh": "较高", "stars": 4, "note": "大副/轮机长 $105k~$135k；船长 $130k~$200k；港湾引航员最高 $350k"},
    {"dimension": "future_prospect",          "label_zh": "较好", "stars": 4, "note": "LNG出口和海上可再生能源提供长期稳定需求；港湾引航员极度短缺"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "自动导航系统辅助但不替代；碰撞规避和应急决策需要人类判断"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列；WA和QLD积极提名；海运公司担保活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "MLTSSL短缺职业；STCW资质转换后PR路径相对顺畅"},
]
SUITABILITY_FIT = ["已持有STCW Officer of the Watch（III/1或II/1）及以上资质，有商船或油轮工作经验", "英语达到ICAO/STCW要求（IELTS 5.5+或等同水平）", "愿意长期海上作业（每次合同3~6个月），能接受与家人分离的工作方式", "有LNG船、VLCC或矿石船操作经验者优先（高薪LNG方向）", "有意向在澳洲西部（LNG中心）或主要港口城市（悉尼/墨尔本/布里斯班）附近定居"]
SUITABILITY_UNFIT = ["不能接受长期海上作业（数月不回家）和轮班制工作方式", "仅有内河或近海小船经验，无商业海洋等级STCW资质", "身体健康状况不符合海事医疗适航要求"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "航海工程师薪资 $105k~$125k（2026）", "url": "https://au.seek.com/career-advice/role/maritime-engineer/salary"},
    {"source_name": "SalaryExpert AU", "content": "澳洲商船船员薪资数据（2026）", "url": "https://www.salaryexpert.com/salary/job/merchant-marine/australia"},
    {"source_name": "AMSA", "content": "澳洲海事安全局海员证书信息", "url": "https://www.amsa.gov.au/vessels-operators/seafarers"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲船员/航海官工资多少？", "answer": "初级三副约 $75k~$95k；大副/轮机长约 $105k~$135k（SEEK $105k~$125k）；LNG/油轮船长约 $150k~$200k；港湾引航员（Harbour Pilot）约 $200k~$350k（极度短缺）。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲船员容易找工作吗？", "answer": "容易。MLTSSL短缺职业，澳洲LNG出口（全球最大）和铁矿石出口持续推动海运需求。STCW持证航海官供不应求，大型LNG运营商（Woodside/Shell）常年招募。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国船员证书澳洲认可吗？", "answer": "中国交通部颁发的STCW证书可通过AMSA（澳洲海事安全局）的证书认可程序转换为澳洲证书，通常需要3~6个月。英语能力和医疗体检是主要要求。建议提前联系AMSA或IMAS（澳洲海事学院）了解具体流程。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "船员会被AI替代吗？", "answer": "短期内不会。自动驾驶和避碰系统是辅助工具，但SOLAS和国际海事法规要求持证船员值守；港口进出、恶劣天气导航和应急处置需要人类判断力。澳洲和国际海事法规在可预见未来不会允许无人商船运营。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲船员有年龄限制吗？", "answer": "无明确年龄上限，但需定期通过医疗适航体检。有丰富LNG或油轮经验的资深船长（45~58岁）非常受欢迎。港湾引航员通常要求有20年以上海上经验，40~55岁是典型就职年龄段。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲船员需要什么资质？", "answer": "STCW证书是核心，具体等级取决于职务（三副需III/1，船长需Master Class 2）。学历可通过认可海事院校（IMAS/TAFE）获取；中国STCW证书通过AMSA认可程序可直接转换。STCW Basic Safety Training（BST）是所有船员的基础要求。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲船员认证（移民）难吗？", "answer": "难度较低。航海官员在MLTSSL，PR路径顺畅。雇主担保482非常活跃（LNG运营商和大型海运公司）；WA和QLD州提名190也可行。主要挑战是STCW证书转换时间（约3~6个月）和英语要求。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "船员和飞行员哪个澳洲发展更好？", "answer": "飞行员起步薪资（$70k~$90k）低于船员（$75k~$95k），但机长薪资（$160k~$250k）高于船长（$130k~$200k）；港湾引航员（$200k~$350k）是海运最高薪。飞行员培训成本（$100k~$150k）远高于海事培训（$40k~$80k）；两者都是MLTSSL短缺职业，PR难度相当。喜欢海洋选船员；喜欢飞行且有培训资金选飞行员。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 船员/航海官数据入库完成")

if __name__ == "__main__":
    run()
