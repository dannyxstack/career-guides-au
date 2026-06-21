"""澳洲警察（441111）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "441111", "anzsco_title": "Police Officer",
    "category": "其他", "workforce_size": 65000, "shortage_listed": 0,
    "growth_areas": json.dumps(["网络犯罪侦查（Cyber Crime Unit）","金融犯罪调查（AFP经济犯罪）","社区联络警察（Community Liaison）","警察翻译/跨文化联络官（华语需求）","AFP（澳联邦警察）国际执法合作"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "警察",
    "summary": "警察维护社会秩序、预防和调查犯罪、应急响应和社区安全管理。澳洲警察体系包括各州/领地警察（NSW Police、Victoria Police等）和联邦警察（AFP），是公务员体系中最大的执法机构。华裔警察在社区联络、多文化警务和华语犯罪案件翻译/联络方面具有独特价值。",
    "forecast_note": "JSA预测警察就业至2030年稳定增长约4%。各州人口增长、城市扩张和网络犯罪率上升推动警察编制持续扩张。联邦警察（AFP）在跨国执法和网络犯罪调查方向招募需求显著增长。",
    "trend_summary": "澳洲各州警察局面临网络犯罪、家庭暴力和有组织犯罪的新挑战，持续扩大编制。华裔社区联络警察（CALD警务）在多元文化大城市（悉尼/墨尔本）需求旺盛。AFP（澳联邦警察）在国际执法合作（澳中边境犯罪/洗钱）方向华语能力是显著竞争优势。",
}
I18N_EN = {
    "locale": "en", "name": "Police Officer",
    "summary": "Police officers maintain social order, prevent and investigate crime, respond to emergencies and manage community safety. Australia's police system includes state/territory police (NSW Police, Victoria Police etc.) and the Australian Federal Police (AFP) — the largest law enforcement agency in the public service. Chinese-Australian police officers have unique value in community liaison, multicultural policing and Mandarin/Cantonese translation for Chinese-language criminal cases.",
    "forecast_note": "JSA projects ~4% stable police employment growth by 2030. Population growth, urban expansion and rising cybercrime rates drive continued expansion of police headcount. Australian Federal Police (AFP) has significantly increased recruitment in transnational law enforcement and cybercrime investigation.",
    "trend_summary": "Australian state police forces face new challenges from cybercrime, domestic violence and organised crime, continuing to expand headcount. CALD (Culturally and Linguistically Diverse) community liaison police are in strong demand in multicultural cities (Sydney/Melbourne). AFP has notable competitive advantage for Mandarin speakers in international law enforcement (Australia-China border crime/money laundering).",
}
EDUCATION = [
    {"stage": "高中毕业（Year 12，必须）", "duration": "—", "cost_min": 0, "cost_max": 0, "cost_note": "各州警察局基本学历要求；大学学历优先（部分州要求）", "sort_order": 0},
    {"stage": "警察学院（Police Academy）培训", "duration": "6~12个月（含实习）", "cost_min": 0, "cost_max": 0, "cost_note": "录取后由警察局提供全免费培训，期间领取学员薪资", "sort_order": 1},
    {"stage": "大学学历（Law/Criminology/Social Work，加分）", "duration": "3年", "cost_min": 20000, "cost_max": 50000, "cost_note": "非硬性要求但有助于加速晋升（侦探/管理岗）", "sort_order": 2},
    {"stage": "语言能力（普通话/粤语/其他）", "duration": "—", "cost_min": 0, "cost_max": 0, "cost_note": "多文化社区联络方向的竞争优势，部分岗位专招双语警察", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "警察学院培训证书（Police Recruit Training Program）", "issuer": "各州警察局", "note": "录取后由各州警察局或AFP提供，是正式上岗的法定资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "驾驶执照（C类或以上）", "issuer": "各州道路交通局", "note": "基本操作要求，申请前需持有效驾照", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "急救证书（First Aid）", "issuer": "St John Ambulance等认可机构", "note": "申请前取得可提升竞争力", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "无犯罪记录及完整背景调查", "issuer": "各州警察局", "note": "严格背景审查（含家庭关系/财务记录/社交媒体）", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "各州警察局官网", "count_min": 200, "count_max": 1000, "note": "NSW/VIC/QLD/WA/SA各州警察局定期开放招募批次"},
    {"platform": "Seek",     "count_min": 300, "count_max": 800, "note": "含警察学员/社区联络官/警察辅助人员岗"},
    {"platform": "AFP Careers", "count_min": 100, "count_max": 400, "note": "联邦警察（AFP）各类执法和分析岗"},
]
SALARIES = [
    {"experience": "警察学员（培训期）", "salary_min": 52000, "salary_max": 62000, "salary_note": "各州警察学院学员培训期薪资（含津贴）", "sort_order": 0},
    {"experience": "初级/正式警察（1~5年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "SEEK区间 $55k~$75k基本薪；含轮班加班津贴约 $70k~$90k", "sort_order": 1},
    {"experience": "资深警察/侦探（5~15年）", "salary_min": 90000, "salary_max": 130000, "salary_note": "Indeed均值 $94,327；Glassdoor均值 $110,000（含所有津贴，2026）", "sort_order": 2},
    {"experience": "警察中高级管理（15年+）", "salary_min": 120000, "salary_max": 200000, "salary_note": "Inspector及以上管理岗，AFP高级管理岗可超过 $150k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "公民/PR要求", "visa_name": "政府服务限制", "description": "各州警察局和AFP要求澳洲公民（部分岗位接受PR）", "sort_order": 0},
    {"visa_subclass": "189/190", "visa_name": "技术移民后申请", "description": "建议先获得澳洲公民/PR身份再申请警察岗位", "sort_order": 1},
    {"visa_subclass": "AFP国际招募", "visa_name": "特殊通道", "description": "AFP部分国际合作岗位可能对持特定签证的申请人开放", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "执法法律、危机处置、心理应对和社区沟通技能综合要求"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "警察学院培训约6~12个月；侦探晋升需5年以上经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "较高", "stars": 4, "note": "严格背景审查和体能测试；各州录取率约10~20%"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "政府编制稳定增长，但名额有限；网络犯罪和CALD方向需求旺盛"},
    {"dimension": "competition",              "label_zh": "较高", "stars": 4, "note": "受欢迎的公务员职业；双语（普通话/粤语）申请者竞争优势显著"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "轮班执勤；危险现场和心理创伤风险；职业伤亡率较高"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "初级 $70k~$90k；资深含津贴约 $90k~$130k；整体薪资中等"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "稳定公务员；网络犯罪侦查和华语社区联络方向增速较快"},
    {"dimension": "ai_risk",                  "label_zh": "很低", "stars": 1, "note": "执法权力、危机处置和社区信任建立是AI无法替代的；AI辅助犯罪分析"},
    {"dimension": "pr_friendliness",          "label_zh": "中低", "stars": 2, "note": "需公民/PR方可申请；建议先获PR再作职业规划"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "警察不在MLTSSL；需先通过其他途径获得PR，再进入警察体系"},
]
SUITABILITY_FIT = ["澳洲公民或永久居民（PR），英语沟通流利，无犯罪记录，背景清白", "普通话/粤语流利，有意向加入华语社区联络警务项目（CALD或双语警察计划）", "体能良好，心理素质稳定，能承受高压执法环境和偶发暴力风险", "有法律/犯罪学/社会工作学历背景，有助于加速晋升侦探或管理岗", "有在澳洲定居并从事长期职业发展的明确计划"]
SUITABILITY_UNFIT = ["尚未获得澳洲公民或PR身份（政府警察局的硬性要求）", "有犯罪记录或重大财务问题（严格背景审查无法通过）", "期望通过警察职业直接移民（非MLTSSL移民路径，需先获PR）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "警察薪资 $55k~$75k基本薪（2026）", "url": "https://au.seek.com/career-advice/role/police-officer/salary"},
    {"source_name": "Indeed AU", "content": "警察均值 $94,327（含津贴，2026）", "url": "https://au.indeed.com/career/police-officer/salaries"},
    {"source_name": "Glassdoor AU", "content": "警察均值 $110,000（含所有津贴，2026）", "url": "https://www.glassdoor.com.au/Salaries/police-officer-salary-SRCH_KO0,14.htm"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲警察工资多少？", "answer": "初级正式警察约 $70,000~$90,000（含轮班津贴）；资深警察/侦探约 $90k~$130k（Indeed $94,327；Glassdoor $110,000）；警察中高级管理约 $120k~$200k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲警察容易找工作吗？", "answer": "各州警察局定期开放招募批次，但竞争较激烈（录取率约10~20%）。双语（普通话/粤语）申请者在CALD社区联络岗位具有显著优势。需要澳洲公民或PR资格。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国警察经验澳洲认可吗？", "answer": "中国执法经验可作为背景参考，但澳洲警察局不会直接豁免培训。所有新进警察都需要完成警察学院培训（6~12个月）。中文普通话能力在多元文化警务岗位是实质性竞争优势。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "警察会被AI替代吗？", "answer": "风险极低。执法权力、现场危机处置、证人访谈和社区信任建立是需要人类判断的法律授权职责。AI辅助犯罪数据分析和监控，但实际执法权力只能由持牌警察行使。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲警察有年龄限制吗？", "answer": "各州警察局通常要求17~35岁（部分州放宽至45岁）申请初级警察岗位。有大学学历或特殊专业技能（IT/语言/财务）的申请者年龄限制相对宽松。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲警察需要什么学历？", "answer": "Year 12是基本要求，大学学历不是硬性要求但有助于晋升。有法律/犯罪学学历者在侦探岗位有竞争优势；有IT学历者在网络犯罪部门有优势。双语能力（普通话/粤语）是多文化警务岗位的重要资质。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "警察入职/移民难吗？", "answer": "政府警察局需要公民或PR，不能作为首选移民路径。建议先通过技术移民（189/190）或其他途径获得PR，再申请各州警察局。竞争激烈，需提前准备（体能/笔试/心理评估/背景调查）。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "警察和消防员哪个澳洲发展更好？", "answer": "薪资相近（含津贴后均在 $80k~$130k）；警察晋升通道更宽（侦探/管理/AFP联邦），职业多元性更高；消防员工作内容更多元（急救/救援/HAZMAT）。两者都需公民/PR，建议根据个人志趣选择——有执法和犯罪调查兴趣选警察；有应急救援和医疗急救热情选消防员。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 警察数据入库完成")

if __name__ == "__main__":
    run()
