"""澳洲IT项目经理（135111）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor、AIPM（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "135111", "anzsco_title": "ICT Managers",
    "category": "IT/工程", "workforce_size": 75000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Digital Transformation Program Delivery","Agile & SAFe at Enterprise Scale","Cloud Migration Project Management","Cybersecurity Program Management","Government ICT Projects (Defence/Health/Tax)"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "IT项目经理",
    "summary": "IT项目经理领导技术项目的规划、执行和交付，覆盖软件开发、云迁移、数字化转型和政府IT系统。澳洲联邦数字化政府计划（Digital Government Strategy）和AUKUS国防IT项目推动持续高需求，是IT类职场晋升路径最宽广的岗位之一。",
    "forecast_note": "JSA 预测ICT经理至2035年就业增长约18%。大型云迁移项目和联邦政府数字服务转型是主要驱动力，PMP/PRINCE2持有者供不应求。",
    "trend_summary": "Agile/SAFe框架已成为澳洲IT项目标配。Product Owner和Scrum Master角色与IT PM高度融合，混合型IT PM（技术背景+Agile认证）薪资溢价 $15k~$25k。",
}
I18N_EN = {
    "locale": "en", "name": "IT Project Manager",
    "summary": "IT project managers lead the planning, execution and delivery of technology projects including software development, cloud migration, digital transformation and government IT systems. Federal Digital Government Strategy and AUKUS defence IT programs drive sustained high demand.",
    "forecast_note": "JSA projects ~18% employment growth for ICT managers by 2035. Large-scale cloud migration and federal government digital service transformation are the primary drivers.",
    "trend_summary": "Agile/SAFe has become standard practice in Australian IT projects. Hybrid IT PMs (technical background + Agile certification) command $15k~$25k salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of IT / Computer Science / Business（3~4年）", "duration": "3~4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "IT背景学历是首选，MBA有助于晋升程序级PM", "sort_order": 0},
    {"stage": "PMP（Project Management Professional）认证", "duration": "3~6个月备考（需35小时培训+经验）", "cost_min": 800, "cost_max": 3000, "cost_note": "PMP考试费 $405（PMI会员）/ $555（非会员）；是IT PM的黄金认证", "sort_order": 1},
    {"stage": "ACS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民必须，以ICT Manager类别评估", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "PMP（Project Management Professional）", "issuer": "Project Management Institute (PMI)", "note": "全球最广泛认可的PM认证，澳洲IT PM岗位中约70%优先要求", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "PRINCE2 Practitioner", "issuer": "AXELOS/PeopleCert", "note": "政府IT项目广泛使用的项目管理框架认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Certified SAFe Agilist / SAFe Program Consultant", "issuer": "Scaled Agile Inc.", "note": "大型企业Agile转型的核心认证，溢价明显", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "ACS 技能评估", "issuer": "Australian Computer Society", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 4500, "note": "全国，含IT PM、技术项目经理、Scrum Master和产品负责人岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 3000, "note": "含政府、银行和大型企业IT项目岗"},
    {"platform": "LinkedIn", "count_min": 3000, "count_max": 6000, "note": "企业直招和猎头，合同岗比例高"},
]
SALARIES = [
    {"experience": "初级IT PM / Scrum Master（0~3年）", "salary_min": 85000, "salary_max": 105000, "salary_note": "含初级产品负责人和数字项目协调员", "sort_order": 0},
    {"experience": "中级IT PM（3~8年，PMP持有）", "salary_min": 110000, "salary_max": 145000, "salary_note": "SEEK 区间 $120k~$140k；Indeed 平均 $128,069（2026）", "sort_order": 1},
    {"experience": "高级IT PM / 项目总监（8~15年）", "salary_min": 145000, "salary_max": 190000, "salary_note": "大型程序交付和多项目组合管理，Glassdoor均值 $134,500", "sort_order": 2},
    {"experience": "程序总监 / CIO路径（15年+）", "salary_min": 190000, "salary_max": 300000, "salary_note": "国防/联邦政府/大型银行CIO和程序总监级别", "sort_order": 3},
    {"experience": "合同IT PM（Day Rate）", "salary_min": 130000, "salary_max": 260000, "salary_note": "合同IT PM日薪 $700~$1,100（年化约 $140k~$220k）", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，IT PM/ICT Manager为短缺类别", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，ACT政府IT项目多", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区IT PM岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "技术+管理综合能力，PMP考试需要系统学习但非技术性考试"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "IT PM通常从开发/分析岗晋升，需要3~5年IT经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "PMP通过率约60~70%，需要35小时培训+经验记录；难度中等"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "联邦数字化项目和企业AI转型推动PM需求稳定增长"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "持PMP+Agile认证的工程师背景PM较供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "项目截止期压力大，多stakeholder管理和会议密集"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "中级约 $110k~$145k；高级可达 $190k+；合同工年化 $140k~$220k"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "数字化转型持续推进，AI/云项目PM是长期紧缺方向"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "stakeholder管理、风险决策和政治协调是AI无法替代的核心能力"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，雇主担保机会多，合同市场活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "ACS评估要求管理类经验，EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["有IT项目管理经验（3年以上），熟悉Agile/Scrum方法论", "持有PMP或PRINCE2认证，或正在备考", "英语沟通能力强（IELTS 7.0+ / PTE 65+，管理岗对英语要求高）", "有跨职能团队管理和stakeholder沟通经验", "目标是政府IT项目（稳定）或银行/金融数字化转型岗（高薪）"]
SUITABILITY_UNFIT = ["无实际IT项目交付经验（仅有开发背景，无管理经验）", "英语沟通能力较弱，无法主持会议和汇报", "不适应高压截止期和多方利益冲突的工作环境"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "IT项目经理薪资 $120k~$140k（2026）", "url": "https://au.seek.com/career-advice/role/project-manager-it/salary"},
    {"source_name": "Indeed AU", "content": "IT项目经理平均薪资 $128,069（2026）", "url": "https://au.indeed.com/career/it-project-manager/salaries"},
    {"source_name": "Glassdoor AU", "content": "IT项目经理平均薪资 $134,500（2026）", "url": "https://www.glassdoor.com.au/Salaries/it-project-manager-salary-SRCH_KO0,18.htm"},
    {"source_name": "ACS", "content": "技能评估机构", "url": "https://www.acs.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲IT项目经理工资多少？", "answer": "中级IT PM约 $110,000~$145,000（Indeed均值 $128,069；Glassdoor均值 $134,500）；高级项目总监约 $145k~$190k；合同PM日薪 $700~$1,100，年化约 $140k~$220k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲IT项目经理容易找工作吗？", "answer": "容易（有PMP+Agile认证者）。Seek 挂牌约 2000~4500 个职位，联邦数字化政府计划和企业云迁移项目持续推高需求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国IT项目管理经验澳洲认可吗？", "answer": "通过 ACS 技能评估（管理类）+ PMP/PRINCE2国际认证，在澳洲完全认可。重要的是要能证明有实际项目交付经验（用STAR方法描述项目规模、预算和成果）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "IT项目经理会被AI替代吗？", "answer": "风险较低。AI工具辅助项目计划生成和风险识别，但stakeholder关系管理、政治决策和跨文化团队协调是AI无法胜任的核心价值。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲IT项目经理有年龄限制吗？", "answer": "无。丰富的大型项目交付经验（10年以上）在市场上具有高溢价，40~55岁的资深PM受政府和大企业青睐。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲IT项目经理需要什么学历？", "answer": "IT/CS/商科相关本科学历是主流，PMP认证对IT PM岗位权重非常高。ACS技能评估要求有管理类相关学历或经验。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲IT项目经理认证（移民）难吗？", "answer": "难度中等。PMP考试需要备考约3个月；ACS评估对管理类经验有要求；189/190 EOI分数对有经验者友好。建议先获取PMP再申请移民。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "IT项目经理和软件工程师哪个更适合移民澳洲？", "answer": "IT PM薪资略高（$128k vs $110k均值），英语要求更高；软件工程师就业量更大（职位数多约2~3倍），技术背景移民路径更清晰。有管理经验+IT背景者选IT PM，纯技术背景者先选软件工程师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] IT项目经理数据入库完成")

if __name__ == "__main__":
    run()
