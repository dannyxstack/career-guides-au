"""澳洲起重机操作员（721111）数据入库。数据来源：JSA、SEEK、Indeed、ERI、SafeWork（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "721111", "anzsco_title": "Crane, Hoist and Lift Operator", "category": "技工",
    "workforce_size": 15000, "shortage_listed": 1,
    "growth_areas": json.dumps(["High-Rise Construction","Mining & Resources","Wind Turbine Installation","Infrastructure & Civil Works","Port & Logistics Operations"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "起重机操作员",
    "summary": "起重机操作员负责操作各类起重设备（塔吊、流动式起重机、门式起重机），用于建筑、矿业、港口和基础设施工程。澳大利亚高楼建设热潮和矿业扩张驱动持续旺盛的需求，薪资是技工类最高之一。",
    "forecast_note": "JSA 预测至2035年建筑和矿业基础设施岗位持续增长。高层建设项目和风电设施安装激增推高起重机操作员招聘量。",
    "trend_summary": "风力发电机安装、高层住宅建设和矿业扩建是三大需求驱动力。操作员须持多类证照，进入门槛高，供给持续短缺。",
}
I18N_EN = {
    "locale": "en", "name": "Crane Operator",
    "summary": "Crane operators operate tower cranes, mobile cranes and gantry cranes for construction, mining, ports and infrastructure. High-rise construction and mining expansion sustain very high and persistent demand.",
    "forecast_note": "JSA projects sustained growth in construction and mining infrastructure jobs through 2035. Wind turbine installation further accelerates demand.",
    "trend_summary": "Wind energy installation, high-rise construction, and mining expansion are the key demand drivers. High licensing barriers keep supply chronically short.",
}
EDUCATION = [
    {"stage": "Certificate III in Crane Operations（含各类起重机执照培训）", "duration": "6~18个月（视机型而定）", "cost_min": 3000, "cost_max": 12000, "cost_note": "培训费因机型（塔吊/流动式）差异大；部分雇主提供带薪培训", "sort_order": 0},
    {"stage": "各州/联邦高风险工作执照（High Risk Work Licence, HRWL）", "duration": "1~4周（考证培训）", "cost_min": 1000, "cost_max": 3000, "cost_note": "全国统一，按起重机类型（CT/C2/C6等）分别考取", "sort_order": 1},
    {"stage": "海外资质评估（VETASSESS / SafeWork Recognition）", "duration": "3~12个月", "cost_min": 1500, "cost_max": 4000, "cost_note": "海外操作经验可申请互认，但通常需本地实操考核", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "High Risk Work Licence – Tower Crane (CT)", "issuer": "各州 SafeWork / WorkSafe", "note": "全国统一许可证，操作塔吊的强制执照", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "High Risk Work Licence – Mobile Crane (C2/C6)", "issuer": "各州 SafeWork / WorkSafe", "note": "流动式起重机执照，按吨位分级", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Dogman Licence (DG)", "issuer": "各州 SafeWork / WorkSafe", "note": "配合起重作业的引导员资质，常作为入门路径", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Working at Heights Certificate", "issuer": "认可RTO", "note": "高空作业强制安全资质", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 400,  "count_max": 900,  "note": "全国，含塔吊、流动吊和矿业起重机岗"},
    {"platform": "Indeed",   "count_min": 200,  "count_max": 500,  "note": "含合同工和 FIFO 岗"},
    {"platform": "LinkedIn", "count_min": 100,  "count_max": 300,  "note": "偏大型建设和矿业公司直招"},
]
SALARIES = [
    {"experience": "Dogman / 入门（0~2年）", "salary_min": 55000, "salary_max": 72000, "salary_note": "引导员起步，积累经验取得起重机执照", "sort_order": 0},
    {"experience": "初级操作员（持CT/C2照后 1~3年）", "salary_min": 80000, "salary_max": 100000, "salary_note": "Indeed 25th percentile", "sort_order": 1},
    {"experience": "中级操作员（3~8年）", "salary_min": 100000, "salary_max": 130000, "salary_note": "SEEK 区间 $125k~$145k（May 2026）；Indeed $44.64/hr", "sort_order": 2},
    {"experience": "资深操作员（8年+，大型塔吊）", "salary_min": 130000, "salary_max": 160000, "salary_note": "高层建设大型塔吊操作员薪资最高", "sort_order": 3},
    {"experience": "矿业 FIFO 起重机操作员（WA/QLD）", "salary_min": 140000, "salary_max": 200000, "salary_note": "矿业高空重型起重岗，轮班津贴+FIFO补贴", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分，永居", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，5年转PR", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "操作技能要求高精度；塔吊盲区作业需丰富经验"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "取证培训6~18个月，远快于传统学徒制"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "HRWL 实操考核难度较高，各类机型须分别考取"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "高层建设和矿业扩张双轮驱动，极度供不应求"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "持证操作员极度稀缺，薪资溢价显著"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "久坐驾驶室为主，但精神高度集中，高空心理压力大"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中位数约 $100k~$145k，是机械操作类薪资最高职业之一"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "风电安装激增、高层建设和矿业扩建三重驱动"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "远程遥控和半自动化在试点应用，但大型工地仍需持证人工操作"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "189/190/491/482均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "海外资质互认有一定难度，需本地实操考核"},
]
SUITABILITY_FIT = ["有起重机或重型设备操作经验，希望技能移民来澳", "接受高空作业和精神高度集中工作，不恐高", "目标是矿业FIFO高薪（$140k~$200k）或大型建设项目", "年龄25~45岁，能适应长时间驾驶室作业"]
SUITABILITY_UNFIT = ["有恐高症或空间感知问题", "无法承受高度精神集中和长时间工作", "期望通过传统学徒路径入职（起重机取证不需要学徒制）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "起重机操作员薪资区间 $125k~$145k（May 2026）", "url": "https://au.seek.com/career-advice/role/crane-operator/salary"},
    {"source_name": "Indeed AU", "content": "起重机操作员平均时薪 $44.64（2026）", "url": "https://au.indeed.com/career/crane-operator/salaries"},
    {"source_name": "SafeWork Australia", "content": "High Risk Work Licence 要求和考证流程", "url": "https://www.safeworkaustralia.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲起重机操作员工资多少？", "answer": "中级操作员年薪约 $100,000~$130,000，SEEK 区间 $125k~$145k（2026）。矿业FIFO可达 $140k~$200k，是机械操作类薪资最高职业之一。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲起重机操作员容易找工作吗？", "answer": "极容易。持证操作员极度稀缺，Seek 挂牌 400~900 个职位，高层建设和风电安装额外推高需求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国起重机证澳洲认可吗？", "answer": "不直接认可，需申请各州 SafeWork High Risk Work Licence 实操考核。有丰富操作经验者考试通过率较高。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "起重机操作员会被自动化替代吗？", "answer": "短期内风险较低。远程遥控和半自动化已在港口和部分矿场试点，但高层建设的复杂环境仍需持证人工操作，且安全法规要求持证人员在场。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲起重机操作员有年龄限制吗？", "answer": "无法律上限。取证培训不需要学徒制，成年人可直接参加培训考证，35~50岁转行者均有成功案例。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "起重机操作员需要大学学历吗？", "answer": "不需要。持有 High Risk Work Licence（HRWL）即可执业，无学历要求，培训周期远短于传统技工学徒。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "起重机操作员难学吗？", "answer": "操作技能有一定难度，塔吊盲区吊装需要丰富的空间感和经验积累。通常从 Dogman（引导员）做起，2~3年后考取操作员执照。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "起重机操作员和叉车操作员哪个更适合移民澳洲？", "answer": "起重机操作员薪资显著更高（$100k~$200k vs 叉车 $65k~$80k），但取证难度和准入门槛更高。叉车操作员入门更简单，适合快速就业。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 起重机操作员数据入库完成")

if __name__ == "__main__":
    run()
