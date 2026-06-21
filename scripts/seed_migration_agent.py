"""澳洲移民中介（224913）数据入库。数据来源：JSA、SEEK、Indeed、OMARA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "224913", "anzsco_title": "Migration Agent",
    "category": "商业/金融/法律", "workforce_size": 6000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Employer-Sponsored Visa (482/186)","Student & Graduate Visa","Skilled Independent Visa (189/190/491)","Family Visa & Partner Visa","Refugee & Humanitarian Visa"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "移民中介（注册移民代理）",
    "summary": "注册移民代理（Registered Migration Agent/RMA）代表客户向澳洲移民局提交签证申请，提供签证策略咨询、申请准备和合规服务。澳洲持续的高移民配额（2024-2025年度移民目标约185,000人）和多元签证类别推动对注册移民代理的稳定需求，是华人社区就业密度最高的商业类执照职业。",
    "forecast_note": "JSA预测移民代理至2035年就业稳定增长约5%。技能移民（482/189/190）需求持续旺盛，家庭签证积压延误推动对专业处理复杂申请的RMA需求增加。",
    "trend_summary": "技能移民（Skills in Demand签证482/186体系2024年大幅改革）是2025年业务量最大的签证类别。RMA通过AI辅助申请文件生成可显著提升效率，但签证策略判断和复杂案例处理不可替代。",
}
I18N_EN = {
    "locale": "en", "name": "Registered Migration Agent (RMA)",
    "summary": "Registered Migration Agents (RMAs) represent clients in visa applications to the Australian Department of Home Affairs, providing visa strategy advisory, application preparation and compliance services. Australia's high sustained migration intake (~185,000/year) and diverse visa categories support steady demand for RMAs, particularly concentrated in the Chinese-speaking community.",
    "forecast_note": "JSA projects ~5% stable employment growth for migration agents by 2035. Skilled migration (482/189/190) demand remains strong, with processing backlogs in family visas driving demand for specialist complex-case RMAs.",
    "trend_summary": "Skilled migration (Skills in Demand visa 482/186 major reforms in 2024) is the highest-volume visa category in 2025. AI-assisted application document generation can significantly lift RMA efficiency, but visa strategy judgement and complex case handling remain irreplaceable.",
}
EDUCATION = [
    {"stage": "Graduate Certificate in Australian Migration Law & Practice（6~12个月）", "duration": "6~12个月（OMARA认可课程）", "cost_min": 5000, "cost_max": 20000, "cost_note": "是成为注册移民代理的法律学历要求；澳洲多所大学提供，约 $5,000~$15,000", "sort_order": 0},
    {"stage": "OMARA 注册申请（Registered Migration Agent）", "duration": "1~3个月申请流程", "cost_min": 1000, "cost_max": 3000, "cost_note": "OMARA注册费约 $1,200~$1,500/年；是合法执业移民代理的法律要求", "sort_order": 1},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须，约 $650 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "OMARA注册（Registered Migration Agent）", "issuer": "OMARA（Office of the Migration Agents Registration Authority）", "note": "澳洲合法执业移民代理的法律要求，缺少此注册不可执业", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Graduate Certificate in Australian Migration Law & Practice", "issuer": "澳洲认可大学（如UNSW/ANU/Murdoch）", "note": "OMARA注册的学历要求，6~12个月完成", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "MARA Member Status", "issuer": "Migration Institute of Australia（MIA）", "note": "行业协会会员资格，提升执业信誉和转介网络", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 300, "count_max": 800, "note": "全国，含注册移民代理、移民律师助理和签证顾问岗"},
    {"platform": "Indeed",   "count_min": 200, "count_max": 600, "note": "含移民公司和律所移民部门岗"},
    {"platform": "LinkedIn", "count_min": 400, "count_max": 1000, "note": "移民公司直招和自雇RMA广告"},
]
SALARIES = [
    {"experience": "初级移民代理 / 签证顾问（0~3年）", "salary_min": 60000, "salary_max": 80000, "salary_note": "受聘于移民公司初期起薪", "sort_order": 0},
    {"experience": "执业移民代理（3~8年）", "salary_min": 75000, "salary_max": 110000, "salary_note": "SEEK 区间 $85k~$100k；Indeed 均值 $77,754（2026）", "sort_order": 1},
    {"experience": "资深/自雇移民代理（8年+，自有客户基础）", "salary_min": 100000, "salary_max": 200000, "salary_note": "自雇RMA，每案佣金制；活跃华人社区RMA收入可显著超 $150k", "sort_order": 2},
    {"experience": "移民律师 / 合伙人", "salary_min": 150000, "salary_max": 350000, "salary_note": "同时持有律师执照的移民律师，高端商业移民客户，收入远高于普通RMA", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，移民公司可担保有经验的RMA", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，VETASSESS评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "Graduate Certificate课程难度中等；核心是熟记复杂的澳洲移民法律体系"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Graduate Certificate约6~12个月；是商业类入门最快的执照职业之一"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "OMARA注册考试（法律知识测试）难度中等；CPD学习要求持续"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "华人社区市场有较大机会，但受移民政策变化影响较大"},
    {"dimension": "competition",              "label_zh": "中高", "stars": 4, "note": "华人RMA市场竞争激烈，特别是在悉尼/墨尔本中文移民咨询服务密集区域"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "案件截止期有压力，政策变化要求持续学习更新"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "受聘RMA $75k~$110k；活跃自雇RMA收入 $100k~$200k+"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "移民政策变化是主要风险；持续高移民配额支撑长期需求"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI辅助标准申请文件生成，但签证策略、复杂案例和客户关系不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL核心短缺列表；VETASSESS评估可行，但竞争分数需要达到要求"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "雇主担保482是最快路径；自雇移民代理需要通过189/190评估"},
]
SUITABILITY_FIT = ["英语能力极强（IELTS 7.0+），熟悉澳洲移民法律体系或有意深入学习", "有华人社区人脉或多元文化社区背景（华人移民市场机会大）", "持有或有意完成Graduate Certificate课程+OMARA注册（6~12个月入门）", "有法律/商科相关学历（Graduate Certificate申请优势）", "目标是自雇模式（个人品牌建立后收入增长空间大）"]
SUITABILITY_UNFIT = ["英语能力较弱，无法处理英语移民法律文件和与移民局沟通", "不适应移民政策频繁变化带来的持续学习压力", "期望稳定收入但不愿承担自雇模式的客户开发压力"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "移民代理薪资 $85k~$100k（2026）", "url": "https://au.seek.com/career-advice/role/migration-agent/salary"},
    {"source_name": "Indeed AU", "content": "移民代理平均薪资 $77,754（2026）", "url": "https://au.indeed.com/career/migration-agent/salaries"},
    {"source_name": "OMARA", "content": "注册移民代理资格和注册信息", "url": "https://www.omara.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲移民代理工资多少？", "answer": "受聘移民代理约 $75,000~$110,000（SEEK $85k~$100k；Indeed均值 $77,754）；活跃自雇RMA收入约 $100k~$200k+（取决于案件量和收费标准）；移民律师约 $150k~$350k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲移民代理容易找工作吗？", "answer": "中等难度。Seek 挂牌约 300~800 个职位；华人社区市场有大量自雇机会。技能移民（482/189/190）需求旺盛，但华人RMA市场竞争激烈。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国移民咨询经验澳洲认可吗？", "answer": "中国移民咨询背景有帮助，但必须完成澳洲Graduate Certificate课程+OMARA注册方可合法执业。约6~12个月可完成资格转换。澳洲移民法律体系与中国完全不同，必须从头学习。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "移民代理会被AI替代吗？", "answer": "部分替代。AI工具可辅助标准申请表填写和文件核查，但签证策略规划、复杂案例处理（拒签/上诉）和客户关系管理不可替代。高质量的RMA服务价值反而更凸显。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲移民代理有年龄限制吗？", "answer": "无。资深RMA（40~55岁）凭借深厚的行业经验和客户网络，是市场上最被信任的执业者，特别是在高净值商业移民领域。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲移民代理需要什么学历？", "answer": "Graduate Certificate in Australian Migration Law & Practice是OMARA注册的学历要求，约6~12个月完成。有法律/商科本科学历者申请Graduate Certificate有优势，但非必须。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲移民代理认证（移民）难吗？", "answer": "难度中等。Graduate Certificate约6~12个月，OMARA注册相对清晰。主要挑战是澳洲移民法律体系的记忆和理解，以及持续的CPD要求。移民政策频繁变化需要持续学习。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "移民代理和律师哪个更适合移民澳洲？", "answer": "移民代理入门门槛大幅低于律师（Graduate Certificate 6~12个月 vs LLB/JD 4~5年），收入中等；律师薪资天花板更高（合伙人 $200k~$600k），但移民路径更复杂。有法律背景且英语极强者选律师；有移民背景且华人网络丰富者选RMA自雇路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 移民代理数据入库完成")

if __name__ == "__main__":
    run()
