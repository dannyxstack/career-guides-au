"""澳洲建筑工程师/工地经理（133111）数据入库。数据来源：JSA、SEEK、Indeed、PayScale（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "133111", "anzsco_title": "Construction Project Manager",
    "category": "其他", "workforce_size": 45000, "shortage_listed": 1,
    "growth_areas": json.dumps(["基础设施超级项目（铁路/公路/隧道）","住房供应加速（各州政府增加住房建设计划）","可持续建筑和绿色认证项目","BIM数字建造和智能工地管理","商业地产翻修和改建（城市更新）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "建筑工程师/工地经理",
    "summary": "建筑工程师和工地经理负责建设项目全周期管理——从预算制定、进度控制、分包协调到安全合规和竣工交付。澳洲建设行业规模庞大（每年约 $2,800亿产值），基础设施超级项目（地铁/公路/公共住房）和住房供应计划驱动对有经验建设管理人才的强劲需求。建设项目经理是澳洲薪资最高的管理类职业之一（机长级别薪资）。",
    "forecast_note": "JSA预测建筑工程师/项目经理就业至2030年增长约10%。各州政府基础设施投资（NSW铁路/VIC西关隧道/QLD奥运基础设施/WA METRONET）持续推动需求。住房危机使各州政府加大住宅建设计划，推动额外需求。",
    "trend_summary": "澳洲建设行业面临历史性劳动力短缺——每年需要数万名建设管理和工程人才。BIM数字建造和绿色建筑（NABERS/Green Star认证）成为大型项目的标配要求，掌握这些技能的项目经理竞争优势显著。FIFO（飞进飞出）矿业建设和偏远基础设施项目提供额外高薪机会（日薪 $800~$1,500）。",
}
I18N_EN = {
    "locale": "en", "name": "Construction Manager / Site Manager",
    "summary": "Construction managers and site managers oversee the full construction project lifecycle — from budgeting, schedule control and subcontractor coordination to safety compliance and project handover. Australia's construction industry is massive (~$280B annual output) with infrastructure mega-projects (metro/roads/social housing) and housing supply plans driving strong demand for experienced construction management talent. Construction project managers are among Australia's highest-paid management careers.",
    "forecast_note": "JSA projects ~10% construction manager employment growth by 2030. State government infrastructure investments (NSW Rail/VIC West Gate Tunnel/QLD Olympics/WA METRONET) continue to drive demand. The housing crisis is prompting states to accelerate residential building programmes, creating additional demand.",
    "trend_summary": "Australia's construction industry faces historic labour shortages — tens of thousands of construction management and engineering professionals needed annually. BIM digital construction and green building (NABERS/Green Star certification) are becoming standard for major projects, giving project managers with these skills significant competitive advantages. FIFO mining construction and remote infrastructure projects offer additional high-pay opportunities ($800–$1,500 day rates).",
}
EDUCATION = [
    {"stage": "Bachelor of Construction Management / Civil Engineering（4年）", "duration": "4年", "cost_min": 30000, "cost_max": 150000, "cost_note": "主要澳洲大学提供（UNSW/Deakin/QUT/Curtin）；国际生约 $35,000~$45,000/年", "sort_order": 0},
    {"stage": "Diploma of Building and Construction（Management）", "duration": "2年", "cost_min": 8000, "cost_max": 30000, "cost_note": "TAFE或私立建筑学院；实践型建设管理文凭路径", "sort_order": 1},
    {"stage": "PMP / Prince2 项目管理认证（加分）", "duration": "1~3个月", "cost_min": 1000, "cost_max": 5000, "cost_note": "建设项目管理能力的国际认可证书，提升竞争力", "sort_order": 2},
    {"stage": "White Card（建设工地安全证）", "duration": "半天~1天", "cost_min": 50, "cost_max": 200, "cost_note": "进入建设工地的法定安全培训证书（所有工地人员必须）", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "White Card（建设工地安全证）", "issuer": "TAFE / 认可RTO", "note": "所有建设工地工作人员的法定要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Builder's Licence（建筑师执照）", "issuer": "各州建筑监管局", "note": "独立承包建设项目（合同额超过 $20k）的法定要求", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Vetassess / AIPM 技能评估", "issuer": "Vetassess / 澳洲项目管理研究院", "note": "技术移民的学历和经验评估", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "PMP（Project Management Professional）", "issuer": "Project Management Institute", "note": "大型基础设施项目经理的国际认可资质", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 800, "count_max": 3000, "note": "全国，含建设项目经理/工地经理/工地主管各类岗"},
    {"platform": "Indeed",   "count_min": 600, "count_max": 2500, "note": "含大型承建商（Lendlease/CIMIC/John Holland）和政府项目"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 4000, "note": "基础设施和商业建设承建商直招管理岗"},
]
SALARIES = [
    {"experience": "初级工地主管/见习项目经理（0~3年）", "salary_min": 85000, "salary_max": 110000, "salary_note": "建设现场主管起薪；PayScale 工地主管均值 $106,438（2026）", "sort_order": 0},
    {"experience": "项目经理（3~10年）", "salary_min": 120000, "salary_max": 165000, "salary_note": "SEEK 建设经理 $160k~$180k；PayScale $122,452；Indeed工地主管 $106,231（2026）", "sort_order": 1},
    {"experience": "高级项目经理/项目总监（8~15年）", "salary_min": 160000, "salary_max": 220000, "salary_note": "大型基础设施项目总监，悉尼/墨尔本高端市场", "sort_order": 2},
    {"experience": "建设总监/运营总监（15年+）", "salary_min": 200000, "salary_max": 350000, "salary_note": "Tier 1承建商（Lendlease/John Holland）高管级别薪资", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，MLTSSL在列；大型承建商担保活跃", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，满3年后申请", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列；建设项目经理邀请分数优先", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "各州基础设施重点项目积极提名（NSW/QLD/WA/VIC）", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远基础设施和矿业建设项目管理极度短缺", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较高", "stars": 4, "note": "工程技术+项目管理+法律合规+财务控制综合能力要求高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学位4年；晋升高级项目经理需8~12年大型项目经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Vetassess评估明确；White Card简单；Builder执照需工作经验"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL短缺职业；基础设施超级周期创造历史性需求；SEEK 800~3000+职位"},
    {"dimension": "competition",              "label_zh": "低", "stars": 2, "note": "供不应求；有Tier 1大型项目经验的项目经理几乎全员就业"},
    {"dimension": "work_intensity",           "label_zh": "极高", "stars": 5, "note": "工地管理压力极大；24/7待命；安全事故责任重；多方协调繁重"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "项目经理 $120k~$165k；总监 $160k~$220k；高管 $200k~$350k"},
    {"dimension": "future_prospect",          "label_zh": "极好", "stars": 5, "note": "基础设施超级周期预计持续至2030年代；住房供应危机提供额外推动力"},
    {"dimension": "ai_risk",                  "label_zh": "中低", "stars": 2, "note": "AI辅助BIM分析和进度预测；但现场协调、安全决策和利益方管理不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列；各州基础设施项目积极提名；大型承建商担保非常活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "很低", "stars": 1, "note": "短缺职业PR路径顺畅；有Tier 1大项目经验者几乎可立即获得担保"},
]
SUITABILITY_FIT = ["持有建设管理/土木工程学位，有3年以上建设项目现场管理经验（含分包协调和进度管理）", "持有White Card和驾驶执照，熟悉Procore/Aconex等工地管理软件", "有大型基础设施项目（轨道交通/商业建筑/公共住房）或Tier 1承建商工作经历", "有PMP认证或等同的项目管理能力证明（大型项目投标要求）", "愿意在基础设施重点城市（悉尼/墨尔本/布里斯班/珀斯）或接受FIFO矿区建设岗"]
SUITABILITY_UNFIT = ["仅有设计/结构工程背景而无实际建设现场管理经验（设计和施工管理是不同方向）", "不能承受极高压力、多方冲突管理和随时待命的工地管理工作强度", "期望通过建设管理快速进阶到办公室轻松工作（工地管理本质是户外高强度管理职业）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "建设经理薪资 $160k~$180k（2026）", "url": "https://au.seek.com/career-advice/role/construction-manager/salary"},
    {"source_name": "PayScale AU", "content": "建设经理均值 $122,452；工地主管均值 $106,438（2026）", "url": "https://www.payscale.com/research/AU/Job=Construction_Manager/Salary"},
    {"source_name": "Indeed AU", "content": "工地主管均值 $106,231（2026）", "url": "https://au.indeed.com/career/construction-foreman/salaries"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲建筑工程师/工地经理工资多少？", "answer": "初级工地主管约 $85k~$110k（PayScale $106,438）；项目经理约 $120k~$165k（SEEK $160k~$180k）；高级项目总监约 $160k~$220k；建设高管约 $200k~$350k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲建设项目经理容易找工作吗？", "answer": "非常容易。MLTSSL短缺职业，基础设施超级周期历史性推动需求，SEEK常年在线800~3000+职位。有Tier 1大型项目经验的项目经理几乎全员就业，是澳洲劳动力市场最紧缺的职业之一。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国建设管理经验澳洲认可吗？", "answer": "通过Vetassess技能评估，中国大型建设项目（高铁/地铁/大楼）管理经验可以认可。需要提供英文项目经历证明（项目规模/预算/人员管理）。中国Tier 1承建商（中建/中铁/中交）经验在澳洲很受认可。White Card是唯一额外要求（半天培训）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "建设项目经理会被AI替代吗？", "answer": "风险较低。AI辅助BIM 4D进度分析、安全风险预测和资源优化，但工地现场协调、分包谈判、安全事故处置和业主关系管理是AI无法替代的核心管理职责。向高级项目总监和建设运营总监方向发展AI风险几乎为零。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲建设项目经理有年龄限制吗？", "answer": "无。有丰富大型项目经验的中高年龄项目总监（45~60岁）在澳洲极为抢手，特别是有Tier 1承建商或重大基础设施项目管理经历者。建设行业高度依赖经验积累，越有经验越有价值。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲建设项目经理需要什么学历？", "answer": "Bachelor of Construction Management或相关工程学位是标准要求；有大型项目经验者学历要求相对宽松（经验评估路径）。Tier 1大型承建商（Lendlease/CIMIC）通常要求本科学历；中小承建商更注重实际项目经验。White Card是所有工地人员的法定要求（半天课程）。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲建设项目经理认证（移民）难吗？", "answer": "难度较低。建设项目经理在MLTSSL，PR路径顺畅。Vetassess评估路径清晰；各州基础设施项目积极提名190；大型承建商雇主担保482非常活跃。有大型项目经验者几乎可直接获得担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "建设项目经理和土木工程师哪个澳洲发展更好？", "answer": "建设项目经理薪资（$120k~$165k）高于多数土木工程师（$90k~$130k），晋升天花板更高（总监/高管 $200k+）；土木工程师职业更多元（设计/咨询/政府），工作相对稳定，压力略低。有大型项目管理热情和高压承受能力选建设项目经理；偏好技术分析和设计工作选土木工程师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 建筑工程师/工地经理数据入库完成")

if __name__ == "__main__":
    run()
