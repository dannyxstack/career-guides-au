"""澳洲产权转让师/房产律师（271299）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "271299", "anzsco_title": "Legal Professionals nec",
    "category": "商业/金融/法律", "workforce_size": 12000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Off-the-Plan & Development Conveyancing","Foreign Investment Review Board (FIRB) Conveyancing","Digital/e-Conveyancing (PEXA)","Commercial Property Conveyancing","Strata & Community Title"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "产权转让师（房产产权律师）",
    "summary": "产权转让师（Conveyancer）处理房产买卖、产权转让、土地登记和相关法律文件，确保房产交易合法合规顺利完成。澳洲房产市场的持续活跃（悉尼/墨尔本房价高位）推动对产权转让专业人士的稳定需求，是门槛较低、自雇路径成熟的法律类专业职业。",
    "forecast_note": "澳洲数字化产权转让系统（PEXA平台）已覆盖绝大多数州，推动产权转让效率提升同时对传统产权转让师提出技术升级要求。2026年降息周期推动房产交易量回升，产权转让业务量明显增加。",
    "trend_summary": "PEXA数字化产权转让（e-Conveyancing）是行业强制趋势，NSW/VIC已强制使用。海外买家（FIRB）和楼花（Off-the-Plan）产权转让是华人专业Conveyancer的高价值专精方向。",
}
I18N_EN = {
    "locale": "en", "name": "Conveyancer / Property Settlement Lawyer",
    "summary": "Conveyancers handle property purchases, sales, title transfers, land registration and related legal documentation to ensure compliant property transactions. Australia's persistently active property market (Sydney/Melbourne at elevated price levels) supports steady demand for settlement professionals — a lower-barrier, self-employment-mature legal specialisation.",
    "forecast_note": "Australia's digital conveyancing system (PEXA) now covers most states, raising efficiency while requiring technical upskilling from traditional conveyancers. The 2026 rate-cutting cycle is driving a property transaction volume recovery, boosting conveyancing workloads.",
    "trend_summary": "PEXA e-conveyancing is a mandatory industry trend (already mandatory in NSW/VIC). FIRB foreign buyer and off-the-plan conveyancing are high-value specialisations for Chinese-speaking conveyancers.",
}
EDUCATION = [
    {"stage": "Certificate IV / Diploma of Conveyancing（各州要求不同）", "duration": "6个月~2年（视州要求）", "cost_min": 5000, "cost_max": 20000, "cost_note": "NSW：Diploma of Conveyancing（TAFE，约 $8,000~$15,000）；VIC/QLD：类似资格要求；是成为持牌产权转让师的学历基础", "sort_order": 0},
    {"stage": "州产权转让师执照注册", "duration": "1~6个月申请", "cost_min": 500, "cost_max": 2000, "cost_note": "NSW：NSW Fair Trading执照注册；VIC：Business Licensing Authority注册；各州要求略有不同", "sort_order": 1},
    {"stage": "PEXA平台认证培训", "duration": "1~4周", "cost_min": 200, "cost_max": 1000, "cost_note": "澳洲数字化产权转让平台PEXA是行业强制平台，必须完成平台培训", "sort_order": 2},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须，约 $650 申请费", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Licensed Conveyancer（持牌产权转让师）", "issuer": "NSW Fair Trading / VIC BLA / 各州监管机构", "note": "各州产权转让师执照，是合法独立执业的法律要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AICSA会员（Australian Institute of Conveyancers SA）", "issuer": "澳洲各州产权转让师协会", "note": "行业协会会员资格，提升执业信誉", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "PEXA平台认证", "issuer": "PEXA Group", "note": "澳洲数字化产权转让平台认证，NSW/VIC强制使用", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 400, "count_max": 1200, "note": "全国，含产权转让师、产权结算专员和房产律师助理岗"},
    {"platform": "Indeed",   "count_min": 300, "count_max": 900, "note": "含产权转让公司和律所房产部门岗"},
    {"platform": "LinkedIn", "count_min": 500, "count_max": 1500, "note": "大型产权转让公司和房产律所直招"},
]
SALARIES = [
    {"experience": "产权转让助理 / 结算协调员（0~3年）", "salary_min": 55000, "salary_max": 75000, "salary_note": "受聘于产权转让公司初期起薪", "sort_order": 0},
    {"experience": "持牌产权转让师（3~8年）", "salary_min": 80000, "salary_max": 110000, "salary_note": "SEEK 区间 $85k~$100k；受聘模式；旺季可有提成", "sort_order": 1},
    {"experience": "高级产权转让师 / 自雇（5年+）", "salary_min": 100000, "salary_max": 160000, "salary_note": "自有客户基础，悉尼/墨尔本高端房产市场，含重复客户转介", "sort_order": 2},
    {"experience": "房产律师（持有LLB，专精产权）", "salary_min": 120000, "salary_max": 220000, "salary_note": "同时持有律师和产权转让师执照的复合型专业人士，高端商业房产", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，产权转让公司可担保有经验的专业人士", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，VETASSESS评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "NSW/VIC/QLD州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要房产法律知识+产权搜索技能+客户沟通能力，无顶级学术门槛"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Diploma约6个月~2年，是法律类入门最快的执照职业之一"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "州执照考试难度中等；PEXA平台技术要求需要持续更新"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "房产市场驱动；市场旺季需求高，利率上升期需求减少"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "市场规模较小（约12,000从业者），初级岗竞争一般；自雇模式取决于客户网络"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "房产交割截止期有压力，但总体工作节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "持牌产权转让师 $80k~$110k；自雇高端市场 $100k~$160k"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "PEXA数字化提升效率的同时保持对人工专业判断的需求；房产市场长期稳健"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "标准产权搜索和文件生成部分自动化，但产权风险判断和客户关系不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL核心短缺列表；VETASSESS评估可行，但职位总量较小"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "雇主担保482是最快路径；州执照是额外要求"},
]
SUITABILITY_FIT = ["持有法律/商科/房产相关学位或Diploma（产权转让相关），有房产结算工作经验", "熟悉澳洲房产买卖流程和产权登记系统", "英语能力达到 IELTS 7.0+（法律文件和客户沟通要求）", "有华人社区人脉（海外买家产权转让是高价值专精）", "目标是悉尼/墨尔本高端房产市场或自雇产权转让公司"]
SUITABILITY_UNFIT = ["英语法律写作能力不足，无法处理英语产权文件", "无意愿学习澳洲各州产权转让法律框架和PEXA平台", "无法承受自雇模式初期建立客户基础的低收入期"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "产权转让师薪资 $85k~$100k（2026）", "url": "https://au.seek.com/career-advice/role/conveyancer/salary"},
    {"source_name": "Indeed AU", "content": "产权转让师平均薪资 $81,813（2026）", "url": "https://au.indeed.com/career/conveyancer/salaries"},
    {"source_name": "NSW Fair Trading", "content": "NSW产权转让师执照要求", "url": "https://www.fairtrading.nsw.gov.au/trades-and-businesses/licensing/property-and-conveyancing"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲产权转让师工资多少？", "answer": "持牌产权转让师约 $80,000~$110,000（SEEK $85k~$100k；Indeed均值 $81,813）；自雇高端市场 $100k~$160k；持双执照的房产律师约 $120k~$220k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲产权转让师容易找工作吗？", "answer": "中等难度。Seek 挂牌约 400~1,200 个职位；2026年降息周期带动房产交易量回升，市场需求增加。FIRB海外买家产权转让专精的华人Conveyancer有明显的市场机会。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国房产法律经验澳洲认可吗？", "answer": "中国房产法律背景有帮助，但必须完成澳洲Diploma of Conveyancing课程+各州执照注册。约6个月~2年可完成资格转换。澳洲产权转让（Torrens系统）与中国房产法律体系完全不同，必须重新学习。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "产权转让师会被AI替代吗？", "answer": "部分替代。标准产权搜索和合同条款检查受AI工具影响，PEXA数字化提升了处理效率；但产权风险判断、复杂结构性问题（楼花/海外买家FIRB合规）和客户关系不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲产权转让师有年龄限制吗？", "answer": "无。资深产权转让师（40~55岁）凭借丰富的本地市场经验和客户信任网络，特别是在高端住宅和商业房产领域，收入通常高于年轻同行。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲产权转让师需要什么学历？", "answer": "Diploma of Conveyancing（或各州相当学历）+州执照注册是法律要求。无需大学本科学历即可入行，是法律类门槛最低的执照职业之一。持法律本科者可通过律师执照+产权专精路径获得更高薪资。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲产权转让师认证（移民）难吗？", "answer": "难度中等偏低。Diploma约6个月~2年可完成，州执照注册相对清晰。主要挑战是澳洲产权法律体系学习和PEXA平台技术操作。雇主担保482是快速路径。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "产权转让师和移民代理哪个更适合华人移民？", "answer": "两者都有华人社区市场机会；产权转让师门槛略低（Diploma vs Graduate Certificate），与房产行业协同效应强；移民代理服务中国移民客户群体更直接，自雇潜力更大。有房产行业背景者选产权转让师，有移民咨询背景者选RMA。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 产权转让师数据入库完成")

if __name__ == "__main__":
    run()
