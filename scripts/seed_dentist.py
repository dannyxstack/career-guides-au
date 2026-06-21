"""澳洲牙医（252111）数据入库。数据来源：JSA、AHPRA、ADC、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "252111", "anzsco_title": "Dentist",
    "category": "医疗健康", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Cosmetic & Aesthetic Dentistry","Orthodontics & Implants","Rural & Remote Dental Services","Aged Care Dental","Telehealth Dental Triage"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "牙医",
    "summary": "牙医负责诊断和治疗口腔疾病，提供洗牙、补牙、拔牙、正畸和种植牙等服务。澳大利亚牙医严重短缺，尤其在农村和公共牙科诊所，是高薪且PR友好的医疗职业之一。",
    "forecast_note": "澳洲牙医供给长期无法满足需求，农村和偏远地区严重短缺。政府公立牙科诊所等候时间超4年，私立市场需求极旺盛。",
    "trend_summary": "美容牙科（漂白、贴瓷/种植）和正畸市场快速增长，私立诊所盈利能力强。农村DWS区域享有额外政府补贴和PR快速通道。",
}
I18N_EN = {
    "locale": "en", "name": "Dentist",
    "summary": "Dentists diagnose and treat oral health conditions including preventive care, restorations, extractions, orthodontics and implants. Australia faces chronic shortages, particularly in rural areas and public dental.",
    "forecast_note": "Australia's dental supply cannot meet demand. Public dental waiting times exceed 4 years. The private market remains extremely strong.",
    "trend_summary": "Cosmetic dentistry (whitening, veneers, implants) and orthodontics are fast-growing segments. Rural DWS areas offer government incentives and PR fast-tracking.",
}
EDUCATION = [
    {"stage": "牙医学学位（Bachelor of Dental Science/Surgery）", "duration": "5年（澳洲）", "cost_min": 40000, "cost_max": 350000, "cost_note": "澳洲国际生学费约 $65,000~$75,000/年（5年约 $325,000~$375,000）；国内牙医学位申请ADC评估", "sort_order": 0},
    {"stage": "ADC 考试（澳洲牙科委员会评估）", "duration": "6~18个月", "cost_min": 5000, "cost_max": 12000, "cost_note": "含笔试（$3,150）和临床技能考试（$7,000+），总约 $10,000~$12,000", "sort_order": 1},
    {"stage": "AHPRA 牙医注册", "duration": "1~3个月", "cost_min": 500, "cost_max": 1000, "cost_note": "完成ADC评估后申请", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Dental Science / Surgery", "issuer": "认可大学", "note": "AHPRA注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "ADC Certificate（澳洲牙科委员会资质证书）", "issuer": "Australian Dental Council", "note": "海外牙医在澳执业的强制评估", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "AHPRA Dental Registration", "issuer": "AHPRA", "note": "全国统一牙医注册，无此注册不得执业", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "专科资质（正畸/口腔外科等）", "issuer": "各专科学会/AHPRA", "note": "晋升专科牙医额外 3~4 年培训，薪资翻倍", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600,  "count_max": 1200, "note": "全国，含私立诊所、公立和农村牙科岗"},
    {"platform": "Indeed",   "count_min": 400,  "count_max": 800,  "note": "含兼职和合同工"},
    {"platform": "LinkedIn", "count_min": 200,  "count_max": 500,  "note": "偏诊所合伙人和牙科连锁管理岗"},
]
SALARIES = [
    {"experience": "新注册牙医（0~2年）", "salary_min": 90000, "salary_max": 130000, "salary_note": "诊所受雇，含基本薪+佣金（按诊疗量计）", "sort_order": 0},
    {"experience": "中级牙医（2~8年）", "salary_min": 130000, "salary_max": 220000, "salary_note": "私立诊所佣金制约 $150k~$220k；Indeed/Glassdoor区间 $110k~$200k", "sort_order": 1},
    {"experience": "资深牙医 / 诊所主任（8年+）", "salary_min": 200000, "salary_max": 350000, "salary_note": "持股诊所收益叠加，高产牙医年收入 $300k~$400k+", "sort_order": 2},
    {"experience": "专科牙医（正畸/口腔外科）", "salary_min": 300000, "salary_max": 600000, "salary_note": "专科培训后薪资翻倍，正畸医生年收入普遍超 $400k", "sort_order": 3},
    {"experience": "农村/DWS区域牙医", "salary_min": 180000, "salary_max": 350000, "salary_note": "政府补贴 $50,000~$100,000+/年，实际收入显著高于城市", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，牙医为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，农村牙医享优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，政府补贴叠加", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "医学+精细手工操作双重高要求，ADC临床考试难度大"},
    {"dimension": "learning_duration",        "label_zh": "极长", "stars": 5, "note": "牙医学位5年+ADC评估约1年，总约6~7年"},
    {"dimension": "certification_difficulty", "label_zh": "极高", "stars": 5, "note": "ADC临床技能考试是公认最难的医疗类考试之一"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "公立候诊超4年，私立需求旺盛，农村极度短缺"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "ADC通过后诊所主动招募，城市农村均供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "长时间弯腰操作对颈椎和腰椎有职业损耗"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级牙医 $130k~$220k；资深 $300k~$400k+；正畸专科 $400k~$600k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "美容牙科市场快速增长，供需缺口持续扩大"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助诊断（X光分析）已应用，但手工操作和患者沟通无法替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，农村牙医PR快速通道和高额补贴"},
    {"dimension": "pr_difficulty",            "label_zh": "较高", "stars": 4, "note": "ADC临床考试是最大门槛，通过率约50%~60%，需充分备考"},
]
SUITABILITY_FIT = ["已持有国内牙医执照（5年制口腔医学本科以上）", "英语能力优秀（ADC考试全英语，OET A级或IELTS 7.5+）", "手工精细操作能力强，有耐心和亲和力", "接受农村就业以快速获取PR和额外补贴", "目标是高薪私立诊所或专科培训（正畸/种植）"]
SUITABILITY_UNFIT = ["英语能力较弱，ADC临床考试困难", "有颈椎或腰椎问题（长期弯腰操作职业损耗大）", "无法接受高考试成本（ADC约 $10,000~$12,000）"]
SOURCES = [
    {"source_name": "Australian Dental Council (ADC)", "content": "海外牙医评估和ADC考试流程", "url": "https://www.adc.org.au/"},
    {"source_name": "AHPRA", "content": "牙医注册要求", "url": "https://www.ahpra.gov.au/"},
    {"source_name": "Indeed AU", "content": "牙医薪资区间 $110k~$200k（2026）", "url": "https://au.indeed.com/career/dentist/salaries"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲牙医工资多少？", "answer": "中级牙医年收入约 $130,000~$220,000；资深牙医 $300,000~$400,000+；正畸专科医生可达 $400,000~$600,000。农村DWS区域额外补贴 $50,000~$100,000+。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲牙医容易找工作吗？", "answer": "极容易。公立牙科候诊超4年，私立需求旺盛，ADC通过后诊所主动招募，农村地区几乎可立即入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国牙医执照澳洲认可吗？", "answer": "通过 ADC（澳洲牙科委员会）笔试+临床技能考试，总费用约 $10,000~$12,000。ADC临床考试是公认最难的医疗类考试之一，建议充分备考（通过率约50%~60%）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "牙医会被AI替代吗？", "answer": "短期内风险较低。AI在X光诊断和治疗方案辅助上快速发展，但实际牙科手术操作和患者沟通仍无法替代。美容牙科和正畸市场的增长超过AI渗透速度。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲牙医有年龄限制吗？", "answer": "无执业年龄上限，但移民打分45岁以上无加分。建议35~45岁牙医尽快启动ADC申请，通过后仍有15~20年高薪执业年限。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲牙医需要什么学历？", "answer": "需要牙医学学位（Bachelor of Dental Science 或同等，通常5年制）。国内口腔医学（5年制）毕业可申请ADC评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲牙医认证难吗？", "answer": "ADC临床技能考试是公认最难的医疗类考试之一，通过率约50%~60%。需要在澳参加标准化模型实操，与实际临床操作有所不同，建议提前参加培训课程。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "牙医和全科医生哪个更适合移民澳洲？", "answer": "两者均是极佳移民职业。全科医生薪资区间更宽（$250k~$500k+），PR路径相近；牙医ADC考试难度比AMC略高，但私立市场收入稳定性更强，自主开诊所的灵活性更高。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 牙医数据入库完成")

if __name__ == "__main__":
    run()
