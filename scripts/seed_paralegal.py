"""澳洲法务助理/法律秘书（599411）数据入库。数据来源：JSA、SEEK、Indeed、PayScale（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "599411", "anzsco_title": "Legal Secretary",
    "category": "商业/金融/法律", "workforce_size": 28000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Litigation Support & E-Discovery","Compliance & Legal Operations","Contract Management Technology","Immigration Law Support","In-house Legal Operations"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "法务助理 / 法律秘书",
    "summary": "法务助理（Paralegal）和法律秘书协助律师处理法律文件、案件管理、法庭准备和法律研究，是法律团队的重要支撑角色。澳洲法律市场的活跃和对法律运营效率的重视使法务助理成为法律行业的稳定就业岗位，也是希望进入法律行业但暂未持有执照的法律专业学生的主流入门路径。",
    "forecast_note": "JSA预测法律秘书/法务助理至2035年就业稳定增长约4%。Legal Tech工具（合同管理系统/e-Discovery软件）的普及对传统法律文书工作有一定替代影响，但增加了对懂Tech的法务助理的需求。",
    "trend_summary": "Legal Operations（法律运营）是2025年法律行业增长最快的新兴方向，懂合同管理技术和e-Discovery软件的法务助理薪资显著高于传统法律文书。In-house Legal Team的法务助理岗位薪资通常高于律所岗位。",
}
I18N_EN = {
    "locale": "en", "name": "Legal Secretary / Paralegal",
    "summary": "Legal secretaries and paralegals support solicitors with legal documentation, case management, court preparation and legal research — a key support role in legal teams. Australia's active legal market supports steady employment as a mainstream entry pathway for legal graduates who haven't yet obtained their practising certificate.",
    "forecast_note": "JSA projects ~4% stable employment growth for legal secretaries by 2035. Legal tech tools (contract management systems/e-Discovery software) partially substitute traditional legal document work but create new demand for tech-savvy paralegals.",
    "trend_summary": "Legal Operations is the fastest-growing direction in the Australian legal sector in 2025. Paralegals with contract management technology and e-Discovery software expertise command significantly higher salaries. In-house legal team paralegal positions typically pay more than law firm positions.",
}
EDUCATION = [
    {"stage": "Associate Degree / Diploma of Paralegal Studies（1~2年）", "duration": "1~2年", "cost_min": 5000, "cost_max": 30000, "cost_note": "法务助理专业课程；TAFE/职业院校费用约 $5,000~$15,000", "sort_order": 0},
    {"stage": "Bachelor of Laws（LLB）在读/毕业未注册", "duration": "3~5年本科", "cost_min": 30000, "cost_max": 200000, "cost_note": "法律系在读学生常担任法务助理积累经验；毕业未完成PLT者也以法务助理身份工作", "sort_order": 1},
    {"stage": "Certificate III / IV in Legal Services", "duration": "3~12个月", "cost_min": 2000, "cost_max": 8000, "cost_note": "法律事务支持基础课程，是法律秘书入门的快捷路径", "sort_order": 2},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须，约 $650 申请费", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III/IV in Legal Services", "issuer": "ASQA认可RTO / TAFE", "note": "法律秘书基础资格，是快捷入门的职业证书路径", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Diploma of Paralegal Studies", "issuer": "ASQA认可RTO / TAFE", "note": "法务助理专业文凭，薪资高于纯法律秘书岗", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "eDiscovery软件认证（Relativity/Nuix）", "issuer": "Relativity / Nuix", "note": "诉讼支持和法律科技高溢价认证，持有者薪资显著高于普通法务助理", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1000, "count_max": 3000, "note": "全国，含法务助理、法律秘书、合规支持和法律运营专员岗"},
    {"platform": "Indeed",   "count_min": 700, "count_max": 2000, "note": "含律所、企业法律部门和政府法律团队岗"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 2500, "note": "大型律所和In-house法律团队直招"},
]
SALARIES = [
    {"experience": "初级法律秘书（0~2年）", "salary_min": 55000, "salary_max": 72000, "salary_note": "法律行政入门起薪", "sort_order": 0},
    {"experience": "法务助理 / 高级法律秘书（2~7年）", "salary_min": 68000, "salary_max": 95000, "salary_note": "SEEK 区间 $75k~$90k；PayScale 均值 $64,772（all experience）；Indeed均值含高级岗约 $75k", "sort_order": 1},
    {"experience": "高级法务助理 / Legal Ops Specialist（5~10年）", "salary_min": 90000, "salary_max": 130000, "salary_note": "懂法律科技（e-Discovery/合同管理）的法务助理，In-house团队薪资更高", "sort_order": 2},
    {"experience": "法律运营经理 / 合规经理（10年+）", "salary_min": 120000, "salary_max": 180000, "salary_note": "从法务助理晋升为法律运营管理的职业路径", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，部分律所对有经验的法务助理提供担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，VETASSESS评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "法律文书和案件管理技能难度适中，主要是规程和流程学习"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Cert III/IV约3~12个月；Diploma约1~2年；入门最快的法律类职业"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "法律秘书课程难度较低；e-Discovery认证有一定技术门槛"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "就业稳定，但Legal Tech工具对部分初级文书工作有替代影响"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级法律秘书竞争一般；懂法律科技的高级法务助理供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "法庭截止期和案件密集期有压力，总体工作节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "较低", "stars": 2, "note": "法务助理薪资偏低（$68k~$95k），但懂法律科技者可达 $90k~$130k"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "Legal Operations是增长方向；传统法律文书部分受AI替代压力"},
    {"dimension": "ai_risk",                  "label_zh": "中高", "stars": 4, "note": "标准法律文件起草和法律研究受AI（Harvey AI/ChatGPT）显著影响"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL核心短缺列表；雇主担保482是主要路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "VETASSESS评估路径可行，但职位总量较小，竞争激烈"},
]
SUITABILITY_FIT = ["持有法律/法务助理相关学历，有法律文书工作经验（2年以上）", "英语书面能力强（IELTS 7.0+，法律文件撰写要求精准）", "有e-Discovery软件（Relativity/Nuix）或合同管理系统操作经验（溢价最高）", "目标是In-house法律团队或大型律所（薪资高于中小律所）", "将法务助理作为法律职业跳板，同时备考PLT+律师注册"]
SUITABILITY_UNFIT = ["英语法律写作能力较弱，无法精准处理英语法律文件", "目标直接是律师职位（法务助理薪资相对低，应直接走LLB/JD+PLT路径）", "AI风险意识强，担忧传统法律文书工作被替代（建议向Legal Ops方向转型）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "法务助理/法律秘书薪资 $75k~$90k（2026）", "url": "https://au.seek.com/career-advice/role/legal-secretary/salary"},
    {"source_name": "PayScale AU", "content": "法律秘书平均薪资 $64,772（2026）", "url": "https://www.payscale.com/research/AU/Job=Legal_Secretary/Salary"},
    {"source_name": "Indeed AU", "content": "法务助理薪资约 $75k（2026）", "url": "https://au.indeed.com/career/paralegal/salaries"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲法务助理工资多少？", "answer": "法务助理/高级法律秘书约 $68,000~$95,000（SEEK $75k~$90k；PayScale均值约 $65k）；懂法律科技的高级法务助理约 $90k~$130k；法律运营经理约 $120k~$180k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲法务助理容易找工作吗？", "answer": "容易（有经验者）。Seek 挂牌约 1,000~3,000 个职位，就业稳定性较高。懂e-Discovery软件和合同管理技术的法务助理供不应求。In-house法律团队需求持续增加。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国法律工作经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国法律事务支持经验可以认可。英语法律写作能力是关键门槛。建议完成澳洲本地的Certificate IV或Diploma of Paralegal Studies来补充本地法律框架知识。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "法务助理会被AI替代吗？", "answer": "风险较高（与其他法律职业相比）。AI工具（Harvey AI/ChatGPT法律版）能够自动生成标准法律文件、进行案例研究和合同条款审查，对初级法律文书工作冲击较大。建议向懂法律科技的Legal Operations方向转型。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲法务助理有年龄限制吗？", "answer": "无。资深Legal Operations专员（35~50岁）在大型企业法律团队中具有稳定就业，特别是有特定行业（金融/医疗/能源）法律运营经验者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲法务助理需要什么学历？", "answer": "Diploma of Paralegal Studies或Certificate IV in Legal Services是主流学历路径（1~2年）；法律本科在读/毕业者也大量担任法务助理。无需全法律学位，是进入法律行业门槛最低的路径。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲法务助理认证（移民）难吗？", "answer": "难度较低。Diploma约1~2年可完成，VETASSESS评估路径可行。主要挑战是英语法律写作能力（IELTS 7.0+）。雇主担保482是快速路径，大型律所有时对有经验的海外法务助理提供担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "法务助理和产权转让师哪个更适合移民澳洲？", "answer": "两者均为中等移民难度；产权转让师薪资略高（$80k~$110k vs 法务助理 $68k~$95k），自雇路径更成熟；法务助理就业多样性更强，可在律所/企业/政府工作。有房产行业背景者选产权转让师，有法律行政背景者选法务助理。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 法务助理/法律秘书数据入库完成")

if __name__ == "__main__":
    run()
