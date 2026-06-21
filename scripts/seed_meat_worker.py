"""澳洲屠宰工/肉类加工工人（362111）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "362111", "anzsco_title": "Meat Process Worker",
    "category": "其他", "workforce_size": 40000, "shortage_listed": 1,
    "growth_areas": json.dumps(["肉类加工技术工（高薪熟练骨手/修整工）","肉类出口质检官（DAFF认可）","肉类加工主管/班组长","澳洲肉类出口中文贸易联络","有机/优质肉类品质管理"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "屠宰工/肉类加工工人",
    "summary": "屠宰工和肉类加工工人在屠宰场（abattoir）和肉类加工厂从事牲畜屠宰、分割、剔骨、修整和包装工作。澳洲是全球最大的牛肉出口国之一，肉类加工行业规模庞大（年产值约 $250亿），常年需要大量技术工人（特别是剔骨工Boner），是澳洲MLTSSL短缺职业，也是新移民获得PR的重要途径之一。",
    "forecast_note": "JSA预测肉类加工工人就业至2030年稳定增长约3%。澳洲牛羊肉出口（特别是对亚洲市场）推动持续需求；技术工人（剔骨工/修整工）短缺严重，企业主动提供签证担保。偏远屠宰场（QLD/WA/NT）技术工人极度短缺，491路径顺畅。",
    "trend_summary": "澳洲肉类加工行业长期依赖技术移民填补劳动力缺口（特别是技术要求高的剔骨工）。技术工（Boner/Slicer）薪资在 $80k~$100k，有企业直接提供签证担保和住宿安排吸引技术移民。中国是澳洲最大的牛肉出口市场，具备中文能力的肉类质检官和贸易联络人员有独特价值。",
}
I18N_EN = {
    "locale": "en", "name": "Abattoir / Meat Process Worker",
    "summary": "Abattoir and meat processing workers handle livestock slaughter, cutting, boning, trimming and packaging in abattoirs and meat processing plants. Australia is one of the world's largest beef exporters with a large meat processing industry (annual output ~$25B), constantly requiring large numbers of skilled workers (particularly boners). It appears on the MLTSSL and is an important PR pathway for new migrants.",
    "forecast_note": "JSA projects ~3% stable meat processing worker employment growth by 2030. Australian beef and lamb exports (particularly to Asian markets) drive sustained demand; skilled worker (boner/trimmer) shortages are severe, with companies proactively providing visa sponsorship. Remote abattoirs (QLD/WA/NT) face acute skilled worker shortages with smooth 491 visa pathways.",
    "trend_summary": "Australia's meat processing industry relies on skilled migrants to fill workforce gaps (particularly high-skill boners). Skilled workers (boners/slicers) earn $80k–$100k, with companies directly offering visa sponsorship and accommodation to attract skilled migrants. China is Australia's largest beef export market — Mandarin-speaking meat quality inspectors and trade liaison staff have unique value.",
}
EDUCATION = [
    {"stage": "Certificate III in Meat Processing（AMP30615）", "duration": "12~18个月（在职培训）", "cost_min": 1000, "cost_max": 5000, "cost_note": "行业标准资质；大多数公司提供边工作边获取资质的在职培训", "sort_order": 0},
    {"stage": "Certificate II in Meat Processing（入门级）", "duration": "3~6个月", "cost_min": 500, "cost_max": 2000, "cost_note": "初级上岗的基础培训；快速入职路径", "sort_order": 1},
    {"stage": "食品安全证书（Food Safety）", "duration": "1~2天", "cost_min": 100, "cost_max": 300, "cost_note": "肉类加工企业的食品安全操作基础要求", "sort_order": 2},
    {"stage": "Vetassess 技能评估（移民）", "duration": "3~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民的学历和经验评估（有工作经验可认可）", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Meat Processing", "issuer": "TAFE / 认可RTO", "note": "技术工人（剔骨工/修整工）的行业标准资质；技术移民评估基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "DAFF 出口肉类认可（Export Meat Inspector）", "issuer": "澳联邦农业渔业林业部（DAFF）", "note": "出口肉类质检官的法定认可资质（薪资显著更高）", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Food Safety Supervisor Certificate", "issuer": "各州认可机构", "note": "肉类加工班组长和主管的实际必要资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "无犯罪记录（National Police Check）", "issuer": "澳联邦警察", "note": "大型肉类出口企业的背景要求", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 200, "count_max": 600, "note": "全国，含剔骨工/修整工/屠宰工/肉类质检岗"},
    {"platform": "Indeed",   "count_min": 150, "count_max": 500, "note": "含大型肉类加工公司（JBS/Teys/Australian Lamb）和出口企业"},
    {"platform": "LinkedIn", "count_min": 50, "count_max": 200, "note": "肉类行业管理岗和贸易联络岗"},
]
SALARIES = [
    {"experience": "初级肉类加工工人（0~2年）", "salary_min": 60000, "salary_max": 75000, "salary_note": "包装/清洁等入门级，约 $31.83/hr含部分加班", "sort_order": 0},
    {"experience": "技术工人/剔骨工（2~8年）", "salary_min": 78000, "salary_max": 100000, "salary_note": "SEEK屠宰工/精肉师 $80k~$90k；Indeed均值 $75,633（2026）", "sort_order": 1},
    {"experience": "班组长/质检员（4~10年）", "salary_min": 90000, "salary_max": 120000, "salary_note": "持Food Safety和DAFF资质的质检员薪资显著更高", "sort_order": 2},
    {"experience": "肉类加工主管/管理层（8年+）", "salary_min": 110000, "salary_max": 160000, "salary_note": "大型屠宰场生产主管或质量经理", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，MLTSSL在列；大型肉类公司（JBS/Teys）主动担保技术工人", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，满3年后申请", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列；Vetassess评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "QLD/WA/NT等肉类出口大州积极提名", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远屠宰场（QLD/WA内陆）最便捷PR路径，公司通常提供住宿", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中低", "stars": 2, "note": "技术工（剔骨/修整）有一定技术曲线；入门工种门槛低"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Certificate II约3~6个月可上岗；剔骨技术约1~2年达到熟练"},
    {"dimension": "certification_difficulty", "label_zh": "低", "stars": 1, "note": "Certificate III资质相对容易获得；Vetassess评估有工作经验路径"},
    {"dimension": "job_demand",               "label_zh": "较高", "stars": 4, "note": "MLTSSL短缺职业；牛肉出口推动持续需求；技术工人主动被担保"},
    {"dimension": "competition",              "label_zh": "低", "stars": 2, "note": "技术工（剔骨工）供不应求；偏远屠宰场有住宿+担保招募"},
    {"dimension": "work_intensity",           "label_zh": "极高", "stars": 5, "note": "体力极密集；寒冷湿滑环境；重复性动作导致职业伤害风险"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "技术工 $78k~$100k；班长/质检 $90k~$120k；劳动强度高但薪资尚可"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "稳定需求但增长有限；向管理和质检方向晋升是最佳路径"},
    {"dimension": "ai_risk",                  "label_zh": "中低", "stars": 2, "note": "自动化屠宰线正在发展，但剔骨和修整精细操作仍需熟练技工"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列；企业主动担保；偏远491路径极顺畅"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "企业主动担保技术工人；偏远491路径最快；PR难度较低"},
]
SUITABILITY_FIT = ["体能强健，能承受极高强度的寒冷工厂体力劳动（这是职业最重要的适合条件）", "愿意在偏远农业区（QLD/WA/NT内陆屠宰场）工作并接受公司提供的住宿安排", "持有Certificate II/III in Meat Processing（或愿意在职期间取得），有食品安全意识", "中文能力（普通话/粤语）对肉类出口贸易联络和中国客户沟通有独特价值", "以获取澳洲PR为主要目标，接受从技术工人开始积累经验和签证资历的路径"]
SUITABILITY_UNFIT = ["无法承受极高强度体力劳动、寒冷工厂环境和重复性动作导致的职业伤害风险", "期望从事轻松的室内白领工作（肉类加工是重体力工厂工作）", "有严格的宗教或文化禁忌不允许接触特定动物肉类（需提前了解具体工厂加工的动物种类）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "屠宰工/精肉师薪资 $80k~$90k（2026）", "url": "https://au.seek.com/career-advice/role/butcher/salary"},
    {"source_name": "Indeed AU", "content": "屠宰工均值 $75,633（2026）", "url": "https://au.indeed.com/career/butcher/salaries"},
    {"source_name": "Meat Industry Award 2020", "content": "澳洲肉类行业最低工资标准（Fair Work Commission）", "url": "https://calculate.fairwork.gov.au/payguides/fairwork/ma000059/docx"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲屠宰工/肉类加工工人工资多少？", "answer": "初级加工工人约 $60k~$75k；技术工（剔骨工/修整工）约 $78k~$100k（SEEK $80k~$90k；Indeed $75,633）；班组长/质检员约 $90k~$120k；生产主管约 $110k~$160k。偏远屠宰场通常含住宿补贴。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲屠宰工容易找工作吗？", "answer": "容易，特别是技术工（剔骨工）。MLTSSL短缺职业，大型肉类公司（JBS/Teys）主动担保技术工人。偏远屠宰场极度短缺，提供住宿和签证担保组合。SEEK 200~600个职位常年在线。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国肉类加工经验澳洲认可吗？", "answer": "通过Vetassess技能评估，中国肉类加工工厂工作经验（特别是剔骨/修整技术）可以认可（需3年以上）。澳洲Certificate II/III是补充资质，可以在职边工作边取得。食品安全意识是澳洲的额外要求。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "屠宰工会被AI替代吗？", "answer": "中低风险。自动化屠宰线（机械屠宰/分割）正在大型工厂推广，但精细剔骨（Boning）和肌肉修整需要人类的力道控制和判断，目前机器仍无法完全复制。向班组长、质检员和管理岗晋升可有效降低自动化替代风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲屠宰工有年龄限制吗？", "answer": "无明确年龄上限，但极高强度体力工作对体能有要求，通常适合18~45岁。质检员和班组长岗位对体能要求相对较低，适合年龄较大的从业者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲屠宰工需要什么学历？", "answer": "无学历要求。Certificate II/III in Meat Processing是标准资质（可边工作边取得）。最重要的是体能、技术熟练度（剔骨/修整）和食品安全意识。DAFF出口质检资质可显著提升薪资。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "屠宰工能移民澳洲吗？", "answer": "是的，这是澳洲PR途径之一。肉类加工工人在MLTSSL，大型肉类公司主动担保技术工人（482签证）。偏远屠宰场491路径最顺畅（加15分），通常附带住宿安排。建议通过正规肉类行业招聘机构联系澳洲屠宰场。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "屠宰工和其他澳洲技术移民路径哪个更好？", "answer": "优势：PR路径顺畅（MLTSSL+企业担保），入行门槛低（Certificate II约3~6个月），偏远491快速PR通道，薪资尚可（技术工 $78k~$100k）。劣势：体力极密集，工作环境恶劣，职业发展空间相对有限。适合以获取PR为首要目标且体能良好的申请者；不适合期望白领职业发展者。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 屠宰工/肉类加工工人数据入库完成")

if __name__ == "__main__":
    run()
