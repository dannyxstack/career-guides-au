"""澳洲精算师（224111）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor、IAA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "224111", "anzsco_title": "Actuary",
    "category": "商业/金融/法律", "workforce_size": 6500, "shortage_listed": 1,
    "growth_areas": json.dumps(["Climate Risk & Catastrophe Modelling","Health Insurance & Government NDIS Modelling","Cyber Risk Quantification","AI Risk & Model Validation","Superannuation & Retirement Modelling"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "保险精算师",
    "summary": "精算师运用数学、统计和金融方法评估保险、退休金、医疗和气候风险，是金融业薪资最高的职业之一。澳洲精算师市场规模虽小（约6,500人），但供需缺口显著，资深精算师薪资可超 $200,000，且是189/190技术移民的优先考量职业。",
    "forecast_note": "JSA 预测精算师至2035年就业增长约10%。气候风险量化（保险公司应对极端天气索赔激增）和网络安全风险精算是2025-2030年增长最快的新兴方向。",
    "trend_summary": "气候精算（Catastrophe Modelling/CAT modelling）是2025年保险行业最紧缺的精算方向，澳洲极端天气事件频发推动对相关专家的需求急剧增加。AI模型验证精算师也是新兴高薪方向。",
}
I18N_EN = {
    "locale": "en", "name": "Actuary",
    "summary": "Actuaries apply mathematics, statistics and financial modelling to quantify insurance, superannuation, healthcare and climate risk — one of the highest-paid professions in the financial sector. Despite a relatively small market (~6,500 practitioners), the supply-demand gap is significant with senior actuaries earning $200,000+.",
    "forecast_note": "JSA projects ~10% employment growth for actuaries by 2035. Climate risk quantification (insurers responding to surging extreme weather claims) and cyber risk actuarial modelling are the fastest-growing emerging directions.",
    "trend_summary": "Climate actuarial modelling (CAT modelling) is the most urgently needed actuarial specialisation in 2025, driven by Australia's frequent extreme weather events. AI model validation actuaries are a new high-premium direction.",
}
EDUCATION = [
    {"stage": "Bachelor of Actuarial Studies（3年）+ 精算师考试", "duration": "3年学位 + 精算师资格通常7~10年", "cost_min": 30000, "cost_max": 160000, "cost_note": "或数学/统计/精算相关学位；精算师资格考试费约 $500~$1,000/门", "sort_order": 0},
    {"stage": "精算师资格路径（FIAA / AIAA）", "duration": "Part I~III考试，通常7~12年", "cost_min": 5000, "cost_max": 20000, "cost_note": "澳洲精算学会（Actuaries Institute）的正式会员资格，含Associate（AIAA）和Fellow（FIAA）级别", "sort_order": 1},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须，约 $650 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "FIAA（Fellow of the Institute of Actuaries of Australia）", "issuer": "Actuaries Institute of Australia", "note": "澳洲精算师最高级别资格，需要通过全部Part I~III考试+实践经验", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "AIAA（Associate of the Institute of Actuaries of Australia）", "issuer": "Actuaries Institute of Australia", "note": "精算师助理级别资格，是晋升FIAA的阶段性认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "FSA（Fellow of the Society of Actuaries）/ FIA", "issuer": "SOA（美国）/ IFoA（英国）", "note": "国际精算师资格，在澳洲通过互认协议部分认可", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 200, "count_max": 600, "note": "全国，含精算师、精算分析师和风险量化分析师岗"},
    {"platform": "Indeed",   "count_min": 100, "count_max": 400, "note": "含保险、超级年金和咨询公司岗"},
    {"platform": "LinkedIn", "count_min": 300, "count_max": 800, "note": "保险公司和精算顾问公司直招，猎头活跃"},
]
SALARIES = [
    {"experience": "精算分析师（0~4年）", "salary_min": 75000, "salary_max": 100000, "salary_note": "精算学位毕业生起薪", "sort_order": 0},
    {"experience": "精算师 / Associate（4~8年）", "salary_min": 100000, "salary_max": 155000, "salary_note": "SEEK 区间 $135k~$155k；Glassdoor 均值 $145k；Indeed 均值 $112,874（2026）", "sort_order": 1},
    {"experience": "资深/Fellow精算师（FIAA，8~15年）", "salary_min": 155000, "salary_max": 250000, "salary_note": "持FIAA资格，大型保险公司和咨询公司高级精算师", "sort_order": 2},
    {"experience": "首席精算师 / 合伙人（15年+）", "salary_min": 250000, "salary_max": 450000, "salary_note": "澳洲大型保险公司首席精算师或精算咨询合伙人", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，精算师为核心短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NSW/VIC保险业集中", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "精算学是最难的商业类专业，需要顶尖数学/统计基础+多年考试"},
    {"dimension": "learning_duration",        "label_zh": "极长", "stars": 5, "note": "学位3年+FIAA资格通常7~12年=总周期可达10~15年"},
    {"dimension": "certification_difficulty", "label_zh": "极高", "stars": 5, "note": "精算师资格考试通过率低，Part III级别难度极高，是澳洲最难获取的专业资格之一"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "职位总量小但供需缺口大，气候精算和网络安全精算需求急增"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "FIAA持有者极度稀缺，高级精算师被猎头主动争抢"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "工作节奏相对合理，模型开发和报告期强度较高"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "是商业类薪资最高的职业，FIAA持有者 $155k~$250k，首席精算师 $250k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "气候风险+网络安全风险+AI风险是精算业未来20年的三大增长引擎"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "精算师是AI风险的量化者，AI反而增加了对精算师（验证AI模型风险）的需求"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，供需缺口大，雇主担保482很容易获得"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "VETASSESS评估和EOI分数是门槛，精算学历通过率较高"},
]
SUITABILITY_FIT = ["持有精算/数学/统计相关学位（数学基础非常扎实）", "已通过部分精算师考试（Part I或以上）", "有保险、超级年金或风险咨询工作经验", "英语能力达到 IELTS 6.5+", "有气候风险建模、网络安全精算或健康保险精算专长（溢价最高方向）"]
SUITABILITY_UNFIT = ["数学基础薄弱，无法应对精算考试的高强度数量训练", "不愿意投入7~12年持续备考的漫长精算师资格路径", "薪资期望在短期（5年内）超过 $150k（精算师需要时间积累资格和经验）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "精算师薪资区间 $135k~$155k（2026）", "url": "https://au.seek.com/career-advice/role/actuary/salary"},
    {"source_name": "Indeed AU", "content": "精算师平均薪资 $112,874（2026）", "url": "https://au.indeed.com/career/actuary/salaries"},
    {"source_name": "Glassdoor AU", "content": "精算师平均薪资 $145,000（2026）", "url": "https://www.glassdoor.com.au/Salaries/actuary-salary-SRCH_KO0,7.htm"},
    {"source_name": "Actuaries Institute of Australia", "content": "精算师资格和行业信息", "url": "https://www.actuaries.asn.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲精算师工资多少？", "answer": "精算分析师约 $75,000~$100,000；持资格精算师（AIAA）约 $100k~$155k（SEEK均值 $135k~$155k；Glassdoor $145k）；资深FIAA精算师约 $155k~$250k；首席精算师可超 $250k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲精算师容易找工作吗？", "answer": "容易（有资格者）。FIAA持有者极度短缺，被猎头主动争抢。气候风险和网络安全精算方向需求急剧增加，即使是Associate级别的精算师也供不应求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国精算经验澳洲认可吗？", "answer": "中国精算师协会（FCAS/FCAA）资格与澳洲精算学会有部分互认协议。通过VETASSESS技能评估，精算学历认可度较高。建议尽快加入澳洲精算学会参加考试。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "精算师会被AI替代吗？", "answer": "不会。精算师是量化AI风险的专家，AI反而增加了对精算师（验证AI模型风险）的需求。气候AI和自主驾驶技术都需要精算师来建立风险定价模型。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲精算师有年龄限制吗？", "answer": "无。资深FIAA精算师（40~55岁）是最被重视的，特别是在气候精算和超级年金领域有深厚经验者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲精算师需要什么学历？", "answer": "精算/数学/统计相关学位是基础；实际上，持有精算师资格（AIAA/FIAA）比学历更重要。通过澳洲精算学会考试路径可以不局限于精算本科学历。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲精算师认证（移民）难吗？", "answer": "移民流程不难，但精算师资格本身是澳洲最难获取的专业资格之一（需要7~12年持续备考）。持部分精算考试通过记录的候选人也可通过雇主担保482快速入境。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "精算师和金融分析师哪个更适合移民澳洲？", "answer": "精算师薪资更高（$135k~$250k vs $100k~$200k），缺口更大（FIAA供不应求），移民便利性更好；但精算师资格路径极长（7~12年）。有数学/精算背景者选精算师，有金融投资背景者选金融分析师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 保险精算师数据入库完成")

if __name__ == "__main__":
    run()
