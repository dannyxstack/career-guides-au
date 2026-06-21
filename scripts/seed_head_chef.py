"""澳洲厨师/主厨（351311）数据入库。数据来源：JSA、SEEK、Indeed、Barcats（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "351311", "anzsco_title": "Chef",
    "category": "餐饮/酒店/旅游", "workforce_size": 120000, "shortage_listed": 1,
    "growth_areas": json.dumps(["高端餐厅主厨（Fine Dining）","植物性/素食料理专精","亚洲菜系厨师（中/日/泰/印）","酒店宴会和活动餐饮","偏远地区和矿山营地厨师（FIFO）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "厨师/主厨",
    "summary": "厨师和主厨在餐厅、酒店、机构和活动餐饮中负责菜单研发、食材管理、团队督导和出品质量控制。澳洲餐饮业是最大的雇主行业之一，厨师长期处于全国短缺名单，是技术移民中路径最清晰的体力技能类职业之一。高端餐厅、酒店和矿山营地（FIFO）厨师薪资显著高于平均水平。",
    "forecast_note": "JSA预测厨师就业至2030年净增约15,000人。餐饮业复苏（COVID后）和旅游业反弹推动强劲需求，偏远地区和矿山营地厨师（FIFO）薪资溢价显著。",
    "trend_summary": "澳洲餐饮业COVID后全面复苏，但厨师短缺状况未有缓解——全国各地餐厅面临严重用工荒。持有证书级资格（Certificate III Hospitality/Commercial Cookery）的厨师在职业移民市场有清晰路径。矿山FIFO厨师（两周工作一周休假模式）薪资可达 $100,000~$130,000，吸引力极强。",
}
I18N_EN = {
    "locale": "en", "name": "Chef / Head Chef",
    "summary": "Chefs and head chefs are responsible for menu development, ingredient management, team supervision and output quality control in restaurants, hotels, institutions and event catering. The Australian hospitality industry is one of the largest employer sectors; chefs have been on the national shortage list long-term, making this one of the clearest skilled migration pathways among trade skill occupations. Fine dining, hotel and mine-site (FIFO) chefs earn significantly above average.",
    "forecast_note": "JSA projects net new demand for ~15,000 chefs by 2030. Post-COVID hospitality recovery and tourism rebound drive strong demand, with remote area and mine-site FIFO chefs commanding significant salary premiums.",
    "trend_summary": "Australia's hospitality industry has fully recovered post-COVID, but chef shortages have not eased — restaurants nationwide face severe staffing shortages. Chefs with certificate-level qualifications (Certificate III Hospitality/Commercial Cookery) have a clear pathway in the skilled migration market. Mine-site FIFO chefs (2 weeks on/1 week off roster) can earn $100,000–$130,000, making this extremely attractive.",
}
EDUCATION = [
    {"stage": "Certificate III in Commercial Cookery（SIT30821，约12~18个月）", "duration": "12~18个月（全日制含实习）", "cost_min": 3000, "cost_max": 20000, "cost_note": "TAFE或私立烹饪学院；国际生约 $8,000~$18,000；是澳洲厨师最主流的资质路径", "sort_order": 0},
    {"stage": "Certificate IV in Kitchen Management", "duration": "6~12个月（在Certificate III基础上）", "cost_min": 2000, "cost_max": 10000, "cost_note": "主厨/厨房管理层的进阶证书", "sort_order": 1},
    {"stage": "海外厨师技能评估（TRA/Vetassess）", "duration": "3~6个月", "cost_min": 300, "cost_max": 1000, "cost_note": "技术移民需要TRA（Trade Recognition Australia）技能评估；约 $300~$500 申请费", "sort_order": 2},
    {"stage": "食品安全监督员证书（Food Safety Supervisor）", "duration": "1天课程+考核", "cost_min": 100, "cost_max": 300, "cost_note": "澳洲所有餐饮从业者的法律必须资质（各州要求）", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Commercial Cookery（SIT30821）", "issuer": "TAFE / 认可的私立烹饪学院", "note": "澳洲厨师技术移民和正式就业的核心资质；TRA技能评估的基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "TRA 技能评估（Trade Recognition Australia）", "issuer": "TRA / 澳洲工业部", "note": "厨师技术移民（189/190/491/482）的必要步骤", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Food Safety Supervisor Certificate", "issuer": "各州认可培训机构", "note": "餐饮场所法律必须，费用约 $100~$300", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "RSA（Responsible Service of Alcohol）", "issuer": "各州认可机构", "note": "接触酒水的餐饮从业者大多数州法律要求", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 5000, "count_max": 12000, "note": "全国，含厨师长/副厨/糕点厨师/学徒厨师各级岗"},
    {"platform": "Indeed",   "count_min": 3000, "count_max": 8000, "note": "含高端餐厅、酒店、机构和FIFO营地厨师岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 6000, "note": "酒店集团和大型餐饮企业直招"},
]
SALARIES = [
    {"experience": "厨师学徒 / 初级厨师（0~2年）", "salary_min": 55000, "salary_max": 70000, "salary_note": "学徒厨师按级别支付；完成学徒后约 $60k~$70k", "sort_order": 0},
    {"experience": "厨师（Commis/Chef de Partie，2~6年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "中级厨师全国均值区间；高端餐厅分部主厨可达 $85k+", "sort_order": 1},
    {"experience": "主厨（Head Chef，5~12年）", "salary_min": 85000, "salary_max": 110000, "salary_note": "SEEK 主厨均值 $85k~$100k；Indeed 均值 $84,589；悉尼主厨均值 $91,890（2026）", "sort_order": 2},
    {"experience": "行政总厨 / FIFO营地主厨（10年+）", "salary_min": 105000, "salary_max": 160000, "salary_note": "五星酒店行政总厨或矿山FIFO主厨约 $100k~$130k；悉尼/布里斯班顶级主厨约 $92k~$126k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，餐厅和酒店直接担保最常见路径", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，需满足2年担保期", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，TRA评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，各州均有通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区厨师极度紧缺，加15分，多州积极提名", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要烹饪技术+食材知识+厨房管理综合能力；体力要求高"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "Certificate III约12~18个月；成为主厨需要5~8年实践经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中低", "stars": 2, "note": "TRA技能评估路径清晰；海外厨师资历认可度高（实操技能可验证）"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL长期在列，全国持续严重短缺，是餐饮行业中移民路径最清晰的职业"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "各级别厨师全国供不应求，雇主主动争抢并提供签证担保"},
    {"dimension": "work_intensity",           "label_zh": "极高", "stars": 5, "note": "高峰时段极高强度（站立8~12小时）、高温和快节奏；行业离职率高"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "主厨 $85k~$110k；FIFO厨师 $100k~$130k；整体薪资合理但体力消耗大"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "旅游业持续增长；餐饮业持续扩张；植物性食品和亚洲菜系专精有溢价"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "烹饪是AI替代风险最低的职业之一，人工烹饪技艺和创意不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL长期在列，是餐饮类职业中移民友好度最高的，各州积极提名"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "TRA评估路径清晰；雇主担保482非常活跃；偏远地区491更容易"},
]
SUITABILITY_FIT = ["持有商业烹饪证书（Certificate III Commercial Cookery或等同资历），有2年以上厨师工作经验", "已通过或有意向申请TRA（Trade Recognition Australia）技能评估", "有亚洲菜系专精（特别是中餐/日餐/泰餐）——澳洲对亚洲菜系主厨需求极旺盛", "愿意接受偏远地区或矿山FIFO工作安排（薪资更高，签证更容易）", "英语基础可以进行基本厨房沟通（IELTS要求相对较低）"]
SUITABILITY_UNFIT = ["无正规商业烹饪资质（家庭烹饪经验不被TRA认可）", "体力状况不适合长时间站立和高强度厨房环境", "期望在悉尼/墨尔本顶级餐厅直接担任主厨（竞争激烈；建议先积累1~2年经验）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "主厨薪资 $85k~$100k（2026）", "url": "https://au.seek.com/career-advice/role/head-chef/salary"},
    {"source_name": "Indeed AU", "content": "主厨平均薪资 $84,589；悉尼 $91,890（2026）", "url": "https://au.indeed.com/career/head-chef/salaries"},
    {"source_name": "Barcats AU", "content": "澳洲主厨真实薪资报告2026", "url": "https://www.barcats.com.au/news/what-australian-head-chefs-are-really-earning-in-2026"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲厨师/主厨工资多少？", "answer": "主厨约 $85,000~$110,000（SEEK $85k~$100k；Indeed $84,589；悉尼均值 $91,890）；行政总厨约 $105k~$160k；矿山FIFO主厨约 $100k~$130k。中级厨师约 $70k~$90k，学徒厨师约 $55k~$70k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲厨师容易找工作吗？", "answer": "极容易。厨师是澳洲长期短缺职业，全国各级别厨师供不应求。SEEK 挂牌约 5,000~12,000 个职位。偏远地区、矿山营地和FIFO岗位尤其紧缺，雇主主动提供签证担保。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国厨师资历澳洲认可吗？", "answer": "通过TRA（Trade Recognition Australia）技能评估，中国厨师工作经验可以认可。需要提供雇主证明信（英文）、工作照片和食材/菜单记录。中餐厨师在澳洲需求极旺盛（中餐馆是最多的亚洲餐厅类别），雇主担保482是最常见的路径。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "厨师会被AI替代吗？", "answer": "不会。烹饪是AI替代风险最低的职业之一。人工烹饪技艺、感官判断（味道/香气/质地）和创意菜单研发是AI无法复制的。自动化设备仅影响标准化快餐生产线，不影响正式餐厅厨师。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲厨师有年龄限制吗？", "answer": "实际上，年龄较大的厨师（40~55岁）在高端餐厅和酒店中非常受欢迎，丰富的菜系经验和稳定性是优势。但厨房工作体力要求高，建议关注管理层（主厨/行政总厨）发展路径以减少纯体力负担。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲厨师需要什么资质？", "answer": "Certificate III in Commercial Cookery（SIT30821）是澳洲技术移民和雇主担保的核心资质。海外厨师需要通过TRA技能评估（约 $300~$500），提供至少3年烹饪工作证明。食品安全监督员证书（Food Safety Supervisor）是所有餐饮从业者的法律要求。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲厨师认证（移民）难吗？", "answer": "难度较低（相对于其他技术职业）。TRA评估路径清晰，雇主担保482非常活跃。MLTSSL在列，各州积极提名厨师。偏远地区491路径最容易，加15分且担保时间短。建议先获取雇主担保offer，再推进签证申请。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "厨师和护士哪个更适合移民澳洲？", "answer": "两者都是MLTSSL短缺职业；护士薪资更高（$95k~$120k vs 厨师 $85k~$110k），英语要求更高（IELTS 7.0+）；厨师英语要求较低（IELTS基础级），技能评估路径更简单，雇主担保更快。英语一般的职业移民首选厨师路径，英语强的建议结合护士或其他医疗路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 厨师/主厨数据入库完成")

if __name__ == "__main__":
    run()
