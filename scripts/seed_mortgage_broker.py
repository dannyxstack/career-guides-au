"""澳洲抵押贷款经纪（222311）数据入库。数据来源：MFAA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "222311", "anzsco_title": "Finance Broker",
    "category": "商业/金融/法律", "workforce_size": 27000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Commercial Property & Development Finance","SMSF & Investment Lending","Equipment & Asset Finance","Foreign Buyer & Expat Mortgage","Digital Mortgage & AI-Assisted Comparison"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "抵押贷款经纪（房贷经纪）",
    "summary": "抵押贷款经纪（Mortgage Broker）代表客户在多家贷款机构间比较和安排住房贷款、商业贷款和再融资。澳洲约70%的新房贷款通过经纪人办理，房产市场的强劲持续推动经纪人收入显著增长，是创业友好度最高的金融职业之一。",
    "forecast_note": "MFAA行业报告：经纪人市场占有率持续扩大（2024年创历史新高），行业总从业人数约27,000人。2026年随着降息周期开始，再融资业务量大幅增加，经纪人收入普遍上升。",
    "trend_summary": "AI贷款比较平台（Lendi/Joust）改变了部分初级经纪人的工作模式，但面对面关系型服务和复杂结构贷款（商业/SMSF/外籍买家）的经纪人价值反而提升。",
}
I18N_EN = {
    "locale": "en", "name": "Mortgage Broker / Finance Broker",
    "summary": "Mortgage brokers compare and arrange home loans, commercial loans and refinancing across multiple lenders on behalf of clients. About 70% of new Australian mortgages are now arranged through brokers. Strong property markets drive significant income growth, making this one of the most entrepreneurship-friendly financial careers.",
    "forecast_note": "MFAA industry report: Broker market share continues to expand (2024 historic high). The 2026 rate-cutting cycle has significantly boosted refinancing volume, lifting broker incomes broadly.",
    "trend_summary": "AI loan comparison platforms (Lendi/Joust) are changing some junior broker workflows, but relationship-driven service and complex structured lending (commercial/SMSF/expat buyers) increase the value of experienced brokers.",
}
EDUCATION = [
    {"stage": "Certificate IV in Finance and Mortgage Broking（FNS40821）", "duration": "3~6个月", "cost_min": 1500, "cost_max": 4000, "cost_note": "ASIC和MFAA要求的基础资格；是成为授权信用代表（ACR）的必要前提", "sort_order": 0},
    {"stage": "Diploma of Finance and Mortgage Broking Management（FNS50322）", "duration": "6~12个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "Diploma 是独立执照（Credit Licence）申请人的资格要求；建议提升为Diploma", "sort_order": 1},
    {"stage": "ASIC 信贷执照注册（Credit Licence or ACR）", "duration": "1~3个月申请", "cost_min": 1000, "cost_max": 5000, "cost_note": "独立执照约 $3,000~$5,000 ASIC申请费；受聘经纪人可作为授权代表（ACR）", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate IV in Finance and Mortgage Broking（FNS40821）", "issuer": "ASIC认可的RTO（注册培训机构）", "note": "澳洲抵押贷款经纪的基础从业资格，法律必须", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "MFAA会员（Member of MFAA）", "issuer": "Mortgage & Finance Association of Australia", "note": "行业协会会员资格，提升客户信任度和转介网络", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "FBAA会员（Finance Brokers Association of Australia）", "issuer": "FBAA", "note": "另一主要行业协会，与MFAA并列", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "ASIC Credit Representative（ACR）/ Credit Licence", "issuer": "ASIC", "note": "法律要求的信贷代表注册或信贷执照，缺少此证不可执业", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600, "count_max": 1500, "note": "全国，含受聘经纪人、业务发展经理和贷款助理岗"},
    {"platform": "Indeed",   "count_min": 400, "count_max": 1000, "note": "含大型聚合商（Aussie/Lendi/Mortgage Choice）下的加盟经纪人岗"},
    {"platform": "LinkedIn", "count_min": 800, "count_max": 2000, "note": "聚合商和银行直招"},
]
SALARIES = [
    {"experience": "新手经纪人（0~2年，受聘模式）", "salary_min": 55000, "salary_max": 80000, "salary_note": "受聘于聚合商，含基本薪资+提成；建立客户基础阶段收入较低", "sort_order": 0},
    {"experience": "成熟经纪人（2~5年，含提成）", "salary_min": 90000, "salary_max": 150000, "salary_note": "Indeed 均值 $95,070；Glassdoor 均值 $102,857（2026）", "sort_order": 1},
    {"experience": "独立经纪人（5年+，自有客户基础）", "salary_min": 130000, "salary_max": 250000, "salary_note": "MFAA 行业报告：经纪人总收入均值 $192,354（含前期+续期佣金）", "sort_order": 2},
    {"experience": "顶级经纪人 / 团队负责人", "salary_min": 250000, "salary_max": 500000, "salary_note": "高端房产市场或商业贷款专精经纪人，含续期佣金积累", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，大型抵押贷款机构可担保经验丰富的经纪人", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要技能评估+EOI", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NSW/VIC/QLD房产市场活跃州", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "Cert IV课程难度不高，核心在于销售能力和市场知识积累"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Cert IV约3~6个月；入职后边学边做，无需漫长资格路径"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Cert IV和ASIC注册难度较低，是商业类认证门槛最低的职业"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "房产市场驱动，市场旺季需求高；利率上升周期需求减少"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "行业门槛低导致新手竞争激烈，但建立稳定客源后竞争优势明显"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "高度依赖自我管理和销售驱动，特别是建立初期客源阶段压力大"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "成熟经纪人总收入 $130k~$250k+；顶级经纪人可达 $500k（含续期佣金）"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "AI贷款比较冲击初级业务，但关系型复杂贷款服务持续增值"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "简单再融资比较受AI工具冲击，但高端客户关系管理和复杂结构贷款不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "STOL列表，有移民路径，但不在MLTSSL核心短缺列表"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "技能评估和EOI分数是门槛；雇主担保482是最快路径"},
]
SUITABILITY_FIT = ["有金融/银行/销售工作经验，人脉资源较丰富", "英语沟通能力强（IELTS 7.0+），善于建立信任关系", "有华人社区人脉或高净值客户资源（华人房产经纪人有巨大市场潜力）", "愿意接受佣金制收入模式，能承受建立客户基础阶段的低收入期", "目标是长期自雇模式（积累续期佣金后收入持续增长）"]
SUITABILITY_UNFIT = ["英语沟通能力较弱，无法建立客户信任关系", "不接受销售驱动和高度不确定性的收入模式", "需要稳定月薪的求职者（经纪行业佣金制占主导）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "抵押贷款经纪薪资 $85k~$100k（2026）", "url": "https://au.seek.com/career-advice/role/mortgage-broker/salary"},
    {"source_name": "Indeed AU", "content": "抵押贷款经纪平均薪资 $95,070（2026）", "url": "https://au.indeed.com/career/mortgage-broker/salaries"},
    {"source_name": "MFAA行业报告", "content": "经纪人行业总收入均值 $192,354（2023）", "url": "https://www.mfaa.com.au/"},
    {"source_name": "Glassdoor AU", "content": "抵押贷款经纪平均薪资 $102,857（2026）", "url": "https://www.glassdoor.com.au/Salaries/mortgage-broker-salary-SRCH_KO0,15.htm"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲抵押贷款经纪工资多少？", "answer": "成熟经纪人约 $90,000~$150,000（Indeed均值 $95,070；Glassdoor $102,857）；MFAA报告经纪人总收入均值约 $192,354（含续期佣金）；顶级经纪人可超 $250k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲抵押贷款经纪容易找工作吗？", "answer": "入职容易（门槛低），但建立稳定客源需要2~3年。2026年降息周期带动再融资业务大幅增加，行业整体收入上升。华人市场有明显的结构性机会。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国金融/银行经验澳洲认可吗？", "answer": "金融/银行工作经验有帮助，但澳洲房贷经纪必须完成本地Cert IV课程+ASIC注册。约3~6个月即可完成；中国的金融背景和客户服务经验是有价值的加分项。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "房贷经纪会被AI替代吗？", "answer": "简单的标准化贷款比较和申请正在被AI平台（Lendi/Joust）部分替代，但高端客户关系管理、复杂商业贷款结构设计和华人社区信任建立是AI无法替代的核心价值。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲房贷经纪有年龄限制吗？", "answer": "无。资深经纪人（40~55岁）凭借丰富的客户网络和市场经验，收入通常高于年轻同行。这是一个经验越丰富、续期佣金积累越多的职业。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲房贷经纪需要大学学历吗？", "answer": "不需要大学学历！澳洲房贷经纪的最低要求是 Certificate IV（3~6个月课程）+ASIC注册。大学学历有帮助但非必须，是商业类门槛最低的职业之一。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲房贷经纪认证（移民）难吗？", "answer": "认证本身难度低（Cert IV）；移民路径需要技能评估和EOI，难度中等。雇主担保482是最快路径，部分大型聚合商（Aussie/Lendi）对有经验者提供担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "房贷经纪和会计师哪个更适合移民澳洲？", "answer": "会计师移民路径更成熟（MLTSSL+CPA评估），收入更稳定；房贷经纪门槛更低（Cert IV vs 会计学位），收入上限更高（成熟经纪人 $192k+），但收入波动大。有金融/银行背景且英语强者选房贷经纪；有会计背景者选会计师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 抵押贷款经纪数据入库完成")

if __name__ == "__main__":
    run()
