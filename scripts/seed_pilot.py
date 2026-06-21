"""澳洲飞行员（231111）数据入库。数据来源：JSA、SEEK、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "231111", "anzsco_title": "Airline Pilot",
    "category": "其他", "workforce_size": 6000, "shortage_listed": 1,
    "growth_areas": json.dumps(["商业航空飞行员（干线/支线）","货机飞行员（电商航空货运增长）","直升机飞行员（矿业/医疗/海上作业）","无人机（UAV）飞行操控与监管","飞行训练教官（飞行学院）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "飞行员",
    "summary": "飞行员负责驾驶商业、货运或私人航空器执行飞行任务，是高技术高准入门槛的专业职业。澳洲飞行员长期短缺，亚太地区航空市场快速扩张（波音预测2043年前需新增28万名飞行员）推动全球和澳洲本地飞行员需求持续旺盛。机长（Captain）薪资超过 $200,000 是常见水平。",
    "forecast_note": "JSA预测澳洲飞行员就业至2030年增长约10%。Qantas、Virgin Australia、Regional Express等持续补充飞行员缺口。亚太地区（中国/印度/东南亚）航空扩张进一步扩大全球澳籍飞行员需求。",
    "trend_summary": "全球飞行员短缺是结构性问题（COVID期间大量飞行员提前退休），澳洲尤为突出。商业飞行员培训成本高（约 $100k~$150k）制约供给，推动薪资持续增长。货机飞行员需求因电商快递航空增长而大幅提升。ATPL（航线飞行员执照）持有者在澳洲就业率接近100%。",
}
I18N_EN = {
    "locale": "en", "name": "Airline / Commercial Pilot",
    "summary": "Pilots fly commercial, cargo or private aircraft — a high-skill, high-barrier professional career. Australian pilots face long-term structural shortage, with Asia-Pacific aviation market expansion (Boeing projects 280,000 new pilots needed by 2043) driving sustained demand globally and locally. Captain salaries exceeding $200,000 are common.",
    "forecast_note": "JSA projects ~10% pilot employment growth in Australia by 2030. Qantas, Virgin Australia, Regional Express and others continue to fill pilot gaps. Asia-Pacific (China/India/Southeast Asia) aviation expansion further increases demand for Australian-trained pilots.",
    "trend_summary": "Global pilot shortage is structural (large numbers retired early during COVID), with Australia particularly affected. High commercial pilot training costs (~$100k–$150k) constrain supply and push salaries higher. Cargo pilot demand has surged with e-commerce aviation freight growth. ATPL (Airline Transport Pilot Licence) holders in Australia have near-100% employment rates.",
}
EDUCATION = [
    {"stage": "Integrated ATPL（Airline Transport Pilot Licence）培训", "duration": "18~36个月", "cost_min": 80000, "cost_max": 150000, "cost_note": "商业飞行员培训总费用（含CPL/IR/MCC/ATPL理论）；澳洲飞行学院约 $90k~$150k", "sort_order": 0},
    {"stage": "商用飞行员执照（CPL）+仪表等级（IR）", "duration": "12~24个月", "cost_min": 60000, "cost_max": 100000, "cost_note": "核心执照；需积累200小时+飞行时数", "sort_order": 1},
    {"stage": "多机组配合（MCC/JOC）课程", "duration": "2~4周", "cost_min": 5000, "cost_max": 15000, "cost_note": "商业航空公司招募飞行员的实际前提条件", "sort_order": 2},
    {"stage": "飞行时数积累（1500小时+）", "duration": "3~5年", "cost_min": 0, "cost_max": 0, "cost_note": "ATPL申请需1500小时总飞行时数；通常通过飞行教官或支线飞行积累", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "ATPL（Airline Transport Pilot Licence）", "issuer": "民用航空安全局（CASA）", "note": "担任机长的法定资质要求，也是技术移民评估的核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "CPL（Commercial Pilot Licence）", "issuer": "CASA", "note": "副驾驶或担保飞行员资质（200小时+）", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Class 1 Aviation Medical Certificate", "issuer": "CASA 认可航空医疗体检官", "note": "所有商业飞行员的硬性健康要求（每年或两年更新）", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "型别等级（Type Rating）", "issuer": "航空公司/CASA认可模拟机", "note": "特定机型（B737/A320等）驾驶资质，由航空公司提供培训", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 100, "count_max": 400, "note": "全国，含干线/支线/货机/直升机飞行员岗"},
    {"platform": "Indeed",   "count_min": 80, "count_max": 300, "note": "含航空公司、包机公司和直升机运营商"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 350, "note": "Qantas/Virgin Australia/FlyPelican等航空公司直招"},
]
SALARIES = [
    {"experience": "初级副驾驶/支线飞行员（0~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "支线航空（Regional Express/QantasLink）起步薪资", "sort_order": 0},
    {"experience": "干线副驾驶/有经验飞行员（3~8年）", "salary_min": 110000, "salary_max": 140000, "salary_note": "SEEK 干线飞行员 $110k~$130k（2026）；Glassdoor 均值 $153,500", "sort_order": 1},
    {"experience": "机长（Captain，8~15年）", "salary_min": 160000, "salary_max": 250000, "salary_note": "Qantas/Virgin Australia机长薪资 $160k~$238k+（2026）", "sort_order": 2},
    {"experience": "资深/宽体机机长（15年+）", "salary_min": 220000, "salary_max": 350000, "salary_note": "Qantas A380/B787长途机长可达 $238k~$300k+", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，MLTSSL在列；Qantas/Virgin等大型航空公司担保活跃", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，满3年后申请", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列；ATPL持有者邀请分数优先", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道（QLD/NT/WA等偏远航空需求州）", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "高度精密技术职业；飞行训练强度极大，安全要求极严格"},
    {"dimension": "learning_duration",        "label_zh": "很长", "stars": 5, "note": "ATPL培训18~36个月+时数积累3~5年；总准备期约5~8年"},
    {"dimension": "certification_difficulty", "label_zh": "极高", "stars": 5, "note": "CASA执照体系严格；技能评估和医疗体检是持续门槛"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "全球结构性飞行员短缺；ATPL持有者就业率接近100%；MLTSSL在列"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "飞行员供不应求；Qantas等主动全球招募；ATPL持有者几乎全员就业"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "跨时区飞行、不规律作息；高度责任感和持续注意力是职业必要素质"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "机长 $160k~$250k；资深宽体机机长 $220k~$350k；澳洲顶尖薪资职业之一"},
    {"dimension": "future_prospect",          "label_zh": "极好", "stars": 5, "note": "全球飞行员短缺预计持续至2040年+；亚太航空扩张提供大量机会"},
    {"dimension": "ai_risk",                  "label_zh": "很低", "stars": 1, "note": "自动驾驶技术辅助飞行员，但CASA法规要求双人制驾驶；飞行员不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列；雇主担保活跃；飞行员技术移民是澳洲最受欢迎的专业类别之一"},
    {"dimension": "pr_difficulty",            "label_zh": "很低", "stars": 1, "note": "MLTSSL短缺职业，PR通道畅通；雇主担保和独立技术移民两条路均顺畅"},
]
SUITABILITY_FIT = ["已持有或正在考取ATPL/CPL及仪表等级（IR），有500小时以上总飞行时数", "身体健康，通过CASA Class 1航空体检；英语能力达到ICAO Level 4以上", "有在澳洲或海外商业航空公司飞行经验（B737/A320等常见机型型别等级优先）", "愿意从支线航空积累时数，长期发展干线机长职业路径", "愿意在偏远地区（NT/QLD/WA）或货运航空工作以快速积累时数"]
SUITABILITY_UNFIT = ["仅有私人执照（PPL）而无商用执照（CPL）或ATPL", "不满足CASA Class 1医疗体检的健康条件", "不能接受不规律作息、长途飞行和持续高强度注意力要求"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "飞行员薪资 $110k~$130k（2026）", "url": "https://au.seek.com/career-advice/role/pilot/salary"},
    {"source_name": "Glassdoor AU", "content": "飞行员均值 $153,500（2026）", "url": "https://www.glassdoor.com.au/Salaries/pilot-salary-SRCH_KO0,5.htm"},
    {"source_name": "Qantas Careers", "content": "Qantas机长薪资信息（2026）", "url": "https://www.qantasgroup.com/careers"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲飞行员工资多少？", "answer": "副驾驶约 $70k~$90k（支线起步）；干线副驾驶约 $110k~$140k；机长约 $160k~$250k；资深宽体机机长约 $220k~$350k。Glassdoor均值 $153,500，SEEK区间 $110k~$130k（2026）。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲飞行员容易找工作吗？", "answer": "极易。全球结构性飞行员短缺，ATPL持有者就业率接近100%。Qantas和Virgin Australia主动全球招募，支线航空（Regional Express/QantasLink）门槛较低。澳洲飞行员薪资在全球范围内竞争力强。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国飞行员执照澳洲认可吗？", "answer": "中国ATPL可通过CASA的overseas licence validation路径转换为澳洲执照，但需要通过CASA英语测试（ICAO Level 4）和部分飞行技术考核。强烈建议在申请前联系CASA确认具体要求。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "飞行员会被AI替代吗？", "answer": "短中期内不会。CASA和国际民航组织（ICAO）法规要求商业航班双人驾驶制；自动驾驶是辅助工具而非替代品。紧急情况处置、天气决策和乘客安全管理需要人类飞行员判断力。预计2040年后部分货机可能采用单人制，但客机飞行员至少还有20年以上的稳定需求期。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲飞行员有年龄限制吗？", "answer": "ICAO规定定期航班机长退休年龄上限65岁，副驾驶无明确年龄上限。考虑培训时间（5~8年）和职业发展，建议35岁前完成ATPL获取以保证足够的职业生涯长度。45岁以后开始飞行培训经济回报率较低。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲飞行员需要什么学历？", "answer": "无严格大学学历要求，ATPL执照是核心资质。部分航空公司（特别是Qantas）有大学学历偏好，但有丰富飞行时数的CPL/ATPL持有者学历要求相对宽松。最重要的是ATPL执照、类型等级和飞行经验。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲飞行员认证（移民）难吗？", "answer": "难度较低。飞行员在MLTSSL，是澳洲技术移民中最受欢迎的职业之一。雇主担保482路径非常活跃（Qantas/Virgin等大型航空公司）；189/190独立技术移民路径也顺畅。主要挑战是ATPL转换和英语ICAO Level 4+要求。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "飞行员和工程师哪个澳洲发展更好？", "answer": "飞行员薪资（机长 $160k~$250k）显著高于多数工程师职业（$90k~$150k），就业率更高（几乎零失业），PR难度更低。但培训成本极高（$100k~$150k）且职业门槛极高；工程师入行成本低、职业路径更多元。有清晰飞行热情和培训资金的人选飞行员；偏好技术多元化的选工程师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 飞行员数据入库完成")

if __name__ == "__main__":
    run()
