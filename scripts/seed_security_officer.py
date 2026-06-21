"""澳洲安全官（442217）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "442217", "anzsco_title": "Security Officer",
    "category": "其他", "workforce_size": 120000, "shortage_listed": 0,
    "growth_areas": json.dumps(["企业安保经理（Corporate Security Manager）","活动和场馆安全（体育/音乐活动）","网络安全顾问（实体+数字融合安全）","私人调查员（Licensed Investigator）","夜间经济安保（酒吧/娱乐场所）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "安全官/保安",
    "summary": "安全官负责人员和财产保护、访客管理、应急响应和威胁预防，是澳洲规模最大的非公务员执法相关职业（约12万人）。从商场保安到企业安保经理，职业晋升路径清晰。澳洲安保行业受监管（每州要求持牌），提供相对稳定的就业环境，是新移民进入安保行业的常见入门职业。",
    "forecast_note": "JSA预测安保职业就业至2030年增长约8%。大型活动恢复（体育/音乐节）、高密度城市商业发展和企业安全意识提升推动需求增长。具备双语能力（普通话/粤语）的安保人员在华人聚集区商业地产有独特优势。",
    "trend_summary": "澳洲安保行业快速扩张（12万从业者，SEEK常年在线1,000+职位）。技术安全（CCTV监控/门禁系统）整合和安保人员的多技能要求（急救/消防监控）是行业趋势。企业安保经理（Corporate Security）是薪资最高的晋升方向，年薪可达 $100k~$150k。",
}
I18N_EN = {
    "locale": "en", "name": "Security Officer / Guard",
    "summary": "Security officers protect people and property, manage visitors, respond to emergencies and prevent threats — Australia's largest non-public service law enforcement-related profession (~120,000 workers). Career progression from shopping centre guard to corporate security manager is well-defined. The Australian security industry is regulated (licensed in each state), providing relatively stable employment — a common entry-point career for new migrants.",
    "forecast_note": "JSA projects ~8% security industry employment growth by 2030. Large events recovery (sports/music festivals), high-density urban commercial development and rising corporate security awareness drive demand. Bilingual (Mandarin/Cantonese) security personnel have unique advantages in Chinese-community commercial properties.",
    "trend_summary": "Australia's security industry is rapidly expanding (120,000 workers, 1,000+ jobs on SEEK at any time). Technology security integration (CCTV/access control) and multi-skill requirements (first aid/fire monitoring) are industry trends. Corporate Security Managers are the highest-paid career direction at $100k–$150k annually.",
}
EDUCATION = [
    {"stage": "Certificate II in Security Operations（必须）", "duration": "2~4周", "cost_min": 300, "cost_max": 1500, "cost_note": "获取安保执照（Security Licence）的法定培训要求", "sort_order": 0},
    {"stage": "安保执照（Security Licence）申请", "duration": "4~8周（审核期）", "cost_min": 200, "cost_max": 600, "cost_note": "各州安保监管局审核；包含背景调查", "sort_order": 1},
    {"stage": "急救证书（First Aid/CPR）", "duration": "1~2天", "cost_min": 100, "cost_max": 300, "cost_note": "大多数安保岗位的实际必要条件", "sort_order": 2},
    {"stage": "Certificate IV/Diploma in Security Operations（晋升）", "duration": "6~12个月", "cost_min": 2000, "cost_max": 8000, "cost_note": "晋升班长（Supervisor）或企业安保经理的进阶资质", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "安保执照（Security Licence）", "issuer": "各州安保监管局（NSW SLED/VIC LSCT等）", "note": "澳洲所有从事安保工作的法定持牌要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Certificate II in Security Operations", "issuer": "TAFE / 认可RTO", "note": "安保执照申请的前提培训资质", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "急救证书（First Aid/CPR）", "issuer": "St John Ambulance等认可机构", "note": "大多数安保公司的硬性要求", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "无犯罪记录（National Police Check）", "issuer": "澳联邦警察或州警察局", "note": "安保执照申请的背景审查要求", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1000, "count_max": 3000, "note": "澳洲最大安保职业市场，全年在线岗位数量最多"},
    {"platform": "Indeed",   "count_min": 800, "count_max": 2500, "note": "含商场/写字楼/工地/活动等各类安保岗"},
    {"platform": "LinkedIn", "count_min": 500, "count_max": 1500, "note": "企业安保经理和安全顾问管理岗"},
]
SALARIES = [
    {"experience": "初级保安（0~2年）", "salary_min": 55000, "salary_max": 72000, "salary_note": "基本时薪约 $25~$30/hr，夜班/周末有额外补贴", "sort_order": 0},
    {"experience": "有经验安保/班组长（2~6年）", "salary_min": 72000, "salary_max": 92000, "salary_note": "SEEK保安 $75k~$90k；Indeed均值 $36.94/hr（约 $76,835/年，2026）", "sort_order": 1},
    {"experience": "安保主管/督察（4~10年）", "salary_min": 85000, "salary_max": 110000, "salary_note": "安保督察/场地经理，含轮班津贴年薪约 $85k~$110k", "sort_order": 2},
    {"experience": "企业安保经理（8年+）", "salary_min": 100000, "salary_max": 150000, "salary_note": "Corporate Security Manager；大型企业安保总监可达 $130k~$150k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "大型安保公司（Securecorp/G4S/Wilson Security）雇主担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，企业安保经理级别可申请", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需技能评估，邀请分数要求较高", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "低", "stars": 1, "note": "入门门槛低；Certificate II培训约2~4周即可入职"},
    {"dimension": "learning_duration",        "label_zh": "很短", "stars": 1, "note": "安保执照培训2~4周；入职快速，是最快能合法就业的职业之一"},
    {"dimension": "certification_difficulty", "label_zh": "低", "stars": 1, "note": "安保执照获取较易；背景调查无犯罪记录即可通过"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "SEEK常年1,000+职位；澳洲12万从业者；是就业机会最多的职业之一"},
    {"dimension": "competition",              "label_zh": "很低", "stars": 1, "note": "入门级供不应求；有执照和急救资质者几乎立即可就业"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 3, "note": "夜班、站立工作、应对突发状况；精神高度集中"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "初级 $55k~$72k；企业安保经理 $100k~$150k；入门薪资偏低"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "行业持续增长；企业安保经理方向薪资可观；技术安全融合提供新机会"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "CCTV自动监控替代部分监控岗位；人工巡逻和应急处置需要人类"},
    {"dimension": "pr_friendliness",          "label_zh": "中低", "stars": 2, "note": "不在MLTSSL；雇主担保可行但需要上升到主管级别"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "入门保安不在短缺列表；企业安保经理级别PR更容易"},
]
SUITABILITY_FIT = ["持有或愿意立即申请澳洲安保执照（Security Licence），背景调查清白", "英语沟通能力基本达标，有急救证书（First Aid/CPR）", "有意向在商业地产密集区（悉尼/墨尔本CBD）或华人聚集区商场工作", "愿意接受轮班（夜班/周末），有能力应对偶发突发状况", "有长期职业发展计划（从保安→班长→督察→企业安保经理）"]
SUITABILITY_UNFIT = ["期望安保职业提供高起始薪资（初级保安薪资偏低）", "有犯罪记录（安保执照背景审查硬性排除条件）", "期望通过普通保安职业快速获得技术移民（非MLTSSL入门级，需晋升至主管级别）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "安保/保安薪资 $75k~$90k（2026）", "url": "https://au.seek.com/career-advice/role/security-guard/salary"},
    {"source_name": "Indeed AU", "content": "安保均值 $36.94/hr（约 $76,835/年，2026）", "url": "https://au.indeed.com/career/security-guard/salaries"},
    {"source_name": "Australian Security Industry Association Limited (ASIAL)", "content": "澳洲安保行业标准和执照要求", "url": "https://www.asial.com.au"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲安保/保安工资多少？", "answer": "初级保安约 $55,000~$72,000（时薪 $25~$30/hr，夜班额外补贴）；有经验安保/班长约 $72k~$92k（SEEK $75k~$90k；Indeed $76,835）；企业安保经理约 $100k~$150k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲保安容易找工作吗？", "answer": "非常容易。SEEK常年在线1,000~3,000个职位，是澳洲就业机会最多的职业之一。持有安保执照和急救资质者几乎立即可就业，是新移民进入澳洲劳动力市场的最快路径之一。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国安保经验澳洲认可吗？", "answer": "中国安保经验对求职有帮助，但澳洲要求持有本地安保执照（Security Licence）。培训约2~4周（Certificate II），加背景审查约6~10周可取得执照。英语沟通能力达到基本要求即可入门。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "保安会被AI替代吗？", "answer": "部分会，部分不会。AI监控（CCTV智能分析/人脸识别）正在替代部分固定监控岗位；但人工巡逻、访客管理、应急处置和现场执法是AI无法完成的。向企业安保经理或安全技术整合方向发展可有效规避AI替代风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲保安有年龄限制吗？", "answer": "无明确年龄上限。18岁以上可申请安保执照；有丰富安保经验的中高年龄者（40~55岁）在企业安保经理岗位非常受欢迎。体能要求因岗位不同而异，坐式（控制室）岗位对体能要求较低。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲保安需要什么学历？", "answer": "无学历要求，Certificate II in Security Operations（2~4周培训）即可入职。有大学学历（犯罪学/安全管理）有助于晋升企业安保经理。最关键是安保执照（State Security Licence）和急救证书。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲保安能移民吗？", "answer": "入门保安不在MLTSSL，普通移民难度较高。企业安保经理和安保督察（Security Supervisor）通过雇主担保482可行。建议把安保作为在澳工作积累经验的起点，晋升至督察/经理级别后再通过雇主担保推进PR。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "保安和消防员/警察哪个更容易进入澳洲就业市场？", "answer": "保安是三者中进入门槛最低的（2~4周培训），就业机会最多，不需要公民/PR资格（持工作签证可从事私人安保）。警察和消防员需要公民/PR，竞争更激烈。建议新移民以保安作为快速就业起点，同时规划长期职业（警察/消防）的PR路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 安全官/保安数据入库完成")

if __name__ == "__main__":
    run()
