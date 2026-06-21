"""澳洲网络安全工程师（262112）数据入库。数据来源：JSA、SEEK、ACSC、ACS（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "262112", "anzsco_title": "ICT Security Specialist",
    "category": "IT/工程", "workforce_size": 70900, "shortage_listed": 1,
    "growth_areas": json.dumps(["Cloud Security & Zero Trust","Government & Defence Cyber","Penetration Testing & Red Team","SOC Analyst & Incident Response","AI/ML Security & Prompt Injection Defence"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "网络安全工程师",
    "summary": "网络安全工程师保护政府、企业和关键基础设施免受网络攻击，负责渗透测试、安全架构、事件响应和合规管理。AUKUS国防协议和澳洲关键基础设施保护法（SOCI）大幅推高需求，是IT类薪资增速最快的职业。",
    "forecast_note": "ABS 数据显示网络安全从业人数同比增长 4.8%（年增3,300人），至2025年已达70,900人，增速是全行业平均的两倍。2030年预测缺口达17,000人。",
    "trend_summary": "AUKUS国防协议（AU$368亿核潜艇计划）对安全认证人才需求急剧增加。AI安全（防御LLM攻击/提示注入）是2025-2030年薪资溢价最高的新兴方向。",
}
I18N_EN = {
    "locale": "en", "name": "Cybersecurity Engineer / ICT Security Specialist",
    "summary": "Cybersecurity engineers protect government, enterprise and critical infrastructure from cyberattacks through penetration testing, security architecture, incident response and compliance management. AUKUS and SOCI legislation are driving unprecedented demand.",
    "forecast_note": "ABS data shows 4.8% YoY growth in cybersecurity employment, reaching 70,900 nationally by 2025 — double the national average. The 2030 projected gap is 17,000 professionals.",
    "trend_summary": "AUKUS defence commitments ($368B nuclear submarine program) are driving acute demand for security-cleared professionals. AI security (LLM attack defence, prompt injection) commands the highest salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of Cybersecurity / IT Security（3~4年）", "duration": "3~4年（全日制）", "cost_min": 28000, "cost_max": 160000, "cost_note": "或 Bachelor of Computer Science + 安全专业方向", "sort_order": 0},
    {"stage": "安全认证（CISSP / CISM / CEH / OSCP）", "duration": "3~12个月备考", "cost_min": 2000, "cost_max": 8000, "cost_note": "CISSP 约 $699 考试费；OSCP 约 $1,499；是高级岗位的重要敲门砖", "sort_order": 1},
    {"stage": "政府安全许可（Security Clearance NV1/NV2）", "duration": "3~18个月申请", "cost_min": 0, "cost_max": 0, "cost_note": "雇主承担费用；持有安全许可薪资溢价 $20k~$40k+", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Cybersecurity / Computer Science", "issuer": "认可大学", "note": "行业通用基础学历", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "CISSP（Certified Information Systems Security Professional）", "issuer": "ISC²", "note": "行业最高认可认证，要求5年从业经验，持有者薪资溢价显著", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "OSCP（Offensive Security Certified Professional）", "issuer": "Offensive Security", "note": "渗透测试黄金标准认证，是红队/渗透岗的强烈推荐", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "ACS 技能评估", "issuer": "Australian Computer Society", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
    {"qual_name": "Australian Government Security Clearance（NV1/NV2）", "issuer": "AGSVA", "note": "政府和国防网络安全岗必须，持有者供不应求", "is_mandatory": 0, "sort_order": 4},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1800, "count_max": 3500, "note": "全国，含SOC分析师、渗透测试、安全架构和政府岗"},
    {"platform": "Indeed",   "count_min": 1200, "count_max": 2500, "note": "含合同工和安全顾问"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 4000, "note": "企业和政府直招，猎头活跃度极高"},
]
SALARIES = [
    {"experience": "初级安全分析师（0~3年）", "salary_min": 80000, "salary_max": 100000, "salary_note": "SOC Tier 1/2，SIEM操作，ABS数据约 $119k年化（含各级别）", "sort_order": 0},
    {"experience": "中级网络安全工程师（3~8年）", "salary_min": 110000, "salary_max": 145000, "salary_note": "SEEK 平均 $120k；行业市场 $127k~$148k（Terratern 2026）", "sort_order": 1},
    {"experience": "高级/渗透测试工程师（OSCP+）", "salary_min": 145000, "salary_max": 195000, "salary_note": "红队/渗透测试专家，ERI 平均 $176,485（顶端）", "sort_order": 2},
    {"experience": "安全架构师 / CISO（10年+）", "salary_min": 190000, "salary_max": 300000, "salary_note": "企业级CISO和政府安全架构薪资可超 $250k", "sort_order": 3},
    {"experience": "政府/国防（持安全许可）", "salary_min": 140000, "salary_max": 250000, "salary_note": "NV1/NV2安全许可溢价 $20k~$40k，Canberra岗位密集", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，网络安全为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，ACT（堪培拉政府岗密集）优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区IT，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "很高", "stars": 4, "note": "安全知识广度要求高（网络/系统/密码学），持续更新学习必须"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3~4年；认证路径自学可加速，CISSP通常需要5年经验"},
    {"dimension": "certification_difficulty", "label_zh": "较高", "stars": 4, "note": "OSCP是实操考试难度高；CISSP需要5年经验+广泛知识域"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "2030年缺口17,000人，AUKUS国防需求急剧增加"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "持证工程师极度供不应求，猎头主动联系"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "事件响应和安全事故处理需要随叫随到，心理压力较大"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "行业均薪 $127k~$148k，是IT类薪资最高职业之一"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "AUKUS+SOCI立法+AI安全三重驱动，20年以上持续增长"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI安全工具辅助防御，但攻防对抗和创意渗透测试无法被AI替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，政府岗可快速获得雇主担保"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "ACS评估和EOI积分是主要门槛，安全认证加分竞争力强"},
]
SUITABILITY_FIT = ["有网络安全/IT安全工作经验（2年以上）", "有CISSP/CEH/OSCP等安全认证，或正在备考", "英语能力达到 IELTS 6.5+（政府安全岗有沟通要求）", "愿意在堪培拉或其他政府机构所在地工作（国防岗）", "目标是政府安全许可岗（薪资溢价最高路径）"]
SUITABILITY_UNFIT = ["无任何安全从业背景，仅有普通IT经验", "英语能力极弱，无法通过政府背景调查", "无法适应随叫随到的事件响应工作节奏"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "网络安全工程师薪资 $100k~$120k（2026）", "url": "https://au.seek.com/career-advice/role/cyber-security-analyst/salary"},
    {"source_name": "Australian Cyber Security Centre (ACSC)", "content": "澳洲网络安全战略和需求", "url": "https://www.cyber.gov.au/"},
    {"source_name": "ABS 劳动力数据", "content": "网络安全从业人数70,900（2025），增速是全行业均值两倍", "url": "https://www.abs.gov.au/"},
    {"source_name": "Terratern 2026", "content": "网络安全薪资市场 $127k~$148k（2026）", "url": "https://terratern.com/blog/cyber-security-salary-australia/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲网络安全工程师工资多少？", "answer": "市场均薪 $127,000~$148,000；中级工程师约 $110k~$145k；持OSCP的渗透测试工程师约 $145k~$195k；CISO可超 $250k。政府/国防安全许可岗溢价 $20k~$40k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲网络安全工程师容易找工作吗？", "answer": "极容易。2030年预测缺口17,000人，持证工程师主动被猎头联系，AUKUS国防岗大量招募安全人才。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国网络安全经验澳洲认可吗？", "answer": "通过 ACS 技能评估（学历审核），国际通用认证（CISSP/CEH/OSCP）在澳洲完全认可。政府安全岗需要澳洲公民身份申请安全许可，非公民只能在部分私企岗就职。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "网络安全工程师会被AI替代吗？", "answer": "风险较低。AI安全工具辅助威胁检测，但攻防对抗创造性（红队）、复杂事件响应决策和安全架构设计是AI无法替代的核心价值。AI反而增加了安全需求（AI系统本身需要防护）。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲网络安全工程师有年龄限制吗？", "answer": "无。经验丰富的40~50岁安全专家在市场上备受青睐，特别是有政府/金融从业背景的资深专家。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲网络安全工程师需要什么学历？", "answer": "本科学历（CS/网络安全相关）是主流，但持有 CISSP+OSCP 等高端认证且有丰富经验的非CS学历者也受欢迎。ACS技能评估对部分相关学科的学历认可范围较广。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲网络安全工程师认证难吗？", "answer": "OSCP 是实操渗透考试，难度较高但被业界认可；CISSP 需要5年经验+广泛知识域，通过率约75%。ACS技术评估本身不难。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "网络安全和软件工程师哪个更适合移民澳洲？", "answer": "网络安全薪资更高（$127k~$148k vs $105k~$125k），缺口更大（2030年缺17000人）；软件工程师就业量更大（职位数多约3~4倍）。有安全背景者选网络安全，有开发背景者选软件工程师，两者均PR友好。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 网络安全工程师数据入库完成")

if __name__ == "__main__":
    run()
