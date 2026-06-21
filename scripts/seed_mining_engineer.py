"""澳洲采矿工程师（233611）数据入库。数据来源：JSA、SEEK、Indeed、MCA（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "233611", "anzsco_title": "Mining Engineer",
    "category": "IT/工程", "workforce_size": 16000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Critical Minerals Mining (Lithium/Cobalt/Rare Earths)","Autonomous Mining Systems","Underground Mining Technology","Mine Rehabilitation & Sustainability","Hydrogen & Renewable Energy Mining"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "采矿工程师",
    "summary": "采矿工程师规划、设计和监督矿山开采作业，包括露天矿和地下矿开采、选矿和矿山安全管理。澳洲是全球最大的铁矿石、锂、铜和黄金生产国，关键矿产（锂/钴/稀土）的全球需求激增推动澳洲采矿行业空前扩张，是IT/工程类薪资最高的职业之一。",
    "forecast_note": "JSA 预测采矿工程师至2035年就业增长约10%。全球电动车产业对锂/钴/镍等关键矿产的需求使澳洲采矿项目大幅扩张，FIFO工程师薪资持续上涨。",
    "trend_summary": "自动驾驶矿山设备（力拓/必和必拓自动化系统）对采矿+IT复合型工程师的需求急剧增加。关键矿产（Critical Minerals）方向是2025-2035年薪资增速最快的采矿子领域。",
}
I18N_EN = {
    "locale": "en", "name": "Mining Engineer",
    "summary": "Mining engineers plan, design and supervise mine operations including open cut and underground mining, mineral processing and mine safety management. Australia is the world's largest producer of iron ore, lithium, copper and gold. Critical minerals demand is driving unprecedented expansion.",
    "forecast_note": "JSA projects ~10% employment growth for mining engineers by 2035. Global EV demand for lithium/cobalt/nickel is massively expanding Australian mining projects, driving sustained FIFO salary growth.",
    "trend_summary": "Autonomous mining systems (Rio Tinto/BHP automation) are driving acute demand for mining+IT hybrid engineers. Critical minerals is the fastest-growing and highest-premium mining sub-discipline in 2025-2035.",
}
EDUCATION = [
    {"stage": "Bachelor of Mining Engineering（荣誉，4年）", "duration": "4年（全日制）", "cost_min": 32000, "cost_max": 200000, "cost_note": "澳洲采矿工程师资质要求4年荣誉学位；Western Australian School of Mines (WASM) 是业内最受认可的院校", "sort_order": 0},
    {"stage": "Engineers Australia（EA）技能评估", "duration": "3~12个月", "cost_min": 770, "cost_max": 3000, "cost_note": "189/190签证必须，约 $770 申请费", "sort_order": 1},
    {"stage": "CPEng（Chartered Professional Engineer）", "duration": "4~7年工作经验后申请", "cost_min": 1500, "cost_max": 5000, "cost_note": "专业注册工程师认证，大型矿山项目管理的重要资质", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Mining Engineering (Honours)", "issuer": "认可大学（EA认证）", "note": "WASM（科廷大学）、UQ和UNSW是最受矿业公司认可的院校", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Engineers Australia（EA）技能评估", "issuer": "Engineers Australia", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPEng（Chartered Professional Engineer）", "issuer": "Engineers Australia", "note": "大型矿山项目管理和独立签名的重要资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Underground/Explosives Certification", "issuer": "各州矿山安全机构", "note": "地下采矿和爆破作业的现场安全资质", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 500,  "count_max": 1500, "note": "全国，含采矿工程师、选矿工程师、矿山地质和FIFO岗"},
    {"platform": "Indeed",   "count_min": 300,  "count_max": 900,  "note": "含关键矿产项目和铁矿石岗"},
    {"platform": "LinkedIn", "count_min": 600,  "count_max": 1500, "note": "大型矿业公司直招（力拓/必和必拓/Fortescue）"},
]
SALARIES = [
    {"experience": "毕业生采矿工程师（0~2年）", "salary_min": 85000, "salary_max": 105000, "salary_note": "应届生FIFO起薪含轮岗补贴，高于大多数工程类毕业生", "sort_order": 0},
    {"experience": "中级采矿工程师（2~7年，FIFO）", "salary_min": 130000, "salary_max": 175000, "salary_note": "SEEK 区间 $145k~$165k；Indeed 平均 $150,725（2026）；含远程轮岗补贴", "sort_order": 1},
    {"experience": "高级采矿工程师（7~15年，CPEng）", "salary_min": 175000, "salary_max": 250000, "salary_note": "矿山总工程师和高级项目工程师，含年终奖", "sort_order": 2},
    {"experience": "矿业总监 / 技术总监（15年+）", "salary_min": 250000, "salary_max": 450000, "salary_note": "大型矿业公司（力拓/必和必拓）总监级别，含股权奖励", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，采矿工程师为核心短缺职业，矿业公司直接担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，矿业公司直接支持", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，WA（全国矿业中心）优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区矿业岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "采矿工程需要岩石力学、爆破工程和选矿等专业知识"},
    {"dimension": "learning_duration",        "label_zh": "中高", "stars": 4, "note": "4年本科+EA评估+CPEng累计约8~10年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "EA评估是学历审核，爆破/地下作业资质需要现场培训"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "关键矿产需求激增，FIFO工程师持续短缺"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "采矿工程师严重短缺，矿业公司主动担保移民"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "FIFO轮岗（2:1或3:1）强度高，远程现场环境艰苦"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级FIFO约 $145k~$175k，是所有工程职业薪资最高"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "全球EV+新能源对锂/钴/稀土需求推动澳洲采矿扩张20年"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助矿山优化，但现场工程判断和安全管理不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，矿业公司常主动担保FIFO工程师移民"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "EA评估对采矿工程学历要求严格，但矿业公司担保482是最快路径"},
]
SUITABILITY_FIT = ["持有采矿工程/矿山地质/选矿工程学位（4年荣誉）", "有实际矿山工作经验（地下矿或露天矿），愿意接受FIFO生活方式", "英语能力达到 IELTS 6.0+（EA评估要求）", "有关键矿产（锂/铜/镍）项目背景（市场溢价最高）", "能接受西澳/昆士兰偏远地区轮岗工作（FIFO薪资最高）"]
SUITABILITY_UNFIT = ["不接受FIFO生活方式（大多数高薪采矿岗位均为FIFO）", "非工程学位，无法通过EA评估", "有严重健康问题（采矿现场对体能有基本要求）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "采矿工程师薪资 $145k~$165k（2026）", "url": "https://au.seek.com/career-advice/role/mining-engineer/salary"},
    {"source_name": "Indeed AU", "content": "采矿工程师平均薪资 $150,725（2026）", "url": "https://au.indeed.com/career/mining-engineer/salaries"},
    {"source_name": "Minerals Council of Australia", "content": "采矿业就业数据和关键矿产战略", "url": "https://www.minerals.org.au/"},
    {"source_name": "Engineers Australia", "content": "EA技能评估和CPEng认证", "url": "https://www.engineersaustralia.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲采矿工程师工资多少？", "answer": "中级FIFO采矿工程师约 $130,000~$175,000（Indeed均值 $150,725）；高级工程师约 $175k~$250k；总监级可超 $300k。是所有工程职业中薪资最高的类别。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲采矿工程师容易找工作吗？", "answer": "极容易。关键矿产（锂/钴/镍）需求激增推动西澳和昆士兰新矿项目大量开工，矿业公司（力拓/必和必拓/Fortescue）常主动担保签证。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国采矿工程学位澳洲认可吗？", "answer": "通过 Engineers Australia（EA）技能评估。中国矿业大学、北京科技大学等矿业专业院校的学历通常能通过EA评估，但课程匹配度需要验证。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "采矿工程师会被AI替代吗？", "answer": "风险较低。AI辅助矿山优化和自动驾驶设备，但反而增加了对能管理AI采矿系统的采矿+IT复合型工程师的需求。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲采矿工程师有年龄限制吗？", "answer": "无。资深工程师（40~55岁）凭借丰富的大型矿山项目经验在市场上具有高溢价。FIFO生活方式确实对体能有一定要求，但并无年龄上限。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲采矿工程师需要什么学历？", "answer": "必须持有4年荣誉采矿工程/地质工程/矿山工程学位，这是EA评估的基本要求。部分地质工程背景者也可通过EA评估进入采矿工程师岗位。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲采矿工程师认证（移民）难吗？", "answer": "难度中低（最容易的工程类移民之一）。矿业公司主动担保482签证，EA评估周期3~12个月；189/190 EOI分数对有5年经验者友好。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "采矿工程师和土木工程师哪个更适合移民澳洲？", "answer": "采矿工程师薪资高得多（$145k~$175k vs $95k~$115k），移民难度更低（矿业公司主动担保）；但FIFO生活方式不适合所有人。愿意接受FIFO者应优先选择采矿工程师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 采矿工程师数据入库完成")

if __name__ == "__main__":
    run()
