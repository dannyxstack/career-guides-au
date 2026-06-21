"""澳洲软件工程师（261312）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor、ACS（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "261312", "anzsco_title": "Software Engineer",
    "category": "IT/工程", "workforce_size": 160000, "shortage_listed": 1,
    "growth_areas": json.dumps(["AI/ML Application Development","Cloud-Native & Microservices","Cybersecurity Software","Fintech & Digital Banking","Defence & Government Digital Transformation"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "软件工程师",
    "summary": "软件工程师设计、开发和维护软件系统，覆盖Web、移动、云原生、AI/ML和企业级应用。澳大利亚IT行业持续扩张，联邦政府数字化转型和AUKUS国防科技投入驱动需求长期旺盛，是技术移民最受欢迎的职业之一。",
    "forecast_note": "JSA 预测软件工程师至2035年就业增长约25%。AI工具辅助开发提高生产率的同时，也推高了对高级工程师（系统架构、AI集成、安全）的需求。",
    "trend_summary": "AI辅助编程（GitHub Copilot/Cursor）正在重塑初级开发工作，但系统设计、代码审查和跨功能协作的需求持续增加。澳洲本地大科技公司（Atlassian、Canva、WiseTech）薪资与硅谷差距缩小。",
}
I18N_EN = {
    "locale": "en", "name": "Software Engineer",
    "summary": "Software engineers design, develop and maintain software systems across web, mobile, cloud-native, AI/ML and enterprise applications. Strong sustained demand driven by federal digital transformation and AUKUS defence technology investment.",
    "forecast_note": "JSA projects ~25% employment growth for software engineers by 2035. AI-assisted coding raises productivity while increasing demand for senior engineers in system design, AI integration and security.",
    "trend_summary": "AI coding tools (GitHub Copilot, Cursor) are reshaping junior development roles while amplifying demand for system design and architectural skills. Salaries at Atlassian, Canva and WiseTech are approaching Silicon Valley levels.",
}
EDUCATION = [
    {"stage": "Bachelor of Computer Science / Software Engineering（3~4年）", "duration": "3~4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "澳洲国际生约 $35,000~$45,000/年；政府补贴名额约 $8,000~$10,000/年", "sort_order": 0},
    {"stage": "编程训练营 / 自学路径（可选替代）", "duration": "3~12个月", "cost_min": 2000, "cost_max": 20000, "cost_note": "非传统路径，适合有作品集的转行者；澳洲雇主对GitHub Portfolio认可度高", "sort_order": 1},
    {"stage": "技能移民评估（ACS，澳洲计算机学会）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "海外IT学历的正式评估机构，约 $500 申请费，是189/190签证的必要评估", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Computer Science / Software Engineering", "issuer": "认可大学", "note": "行业通用基础学历，大多数雇主认可", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "ACS（Australian Computer Society）技能评估", "issuer": "Australian Computer Society", "note": "189/190/491签证技术移民必须，学历互认的官方机构", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "AWS/Azure/GCP Cloud Certification", "issuer": "Amazon/Microsoft/Google", "note": "云认证显著提升薪资竞争力（$10k~$20k溢价）", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "TOGAF / Software Architecture Certifications", "issuer": "The Open Group", "note": "高级架构师晋升路径，提升薪资天花板", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 6000,  "count_max": 12000, "note": "全国，含前端/后端/全栈/移动/嵌入式岗，是IT类挂牌量最大职业"},
    {"platform": "Indeed",   "count_min": 4000,  "count_max": 8000,  "note": "含合同工、FIFO和远程岗"},
    {"platform": "LinkedIn", "count_min": 5000,  "count_max": 10000, "note": "科技公司直招和猎头岗比例高"},
]
SALARIES = [
    {"experience": "毕业生 / 初级工程师（0~2年）", "salary_min": 72000, "salary_max": 88000, "salary_note": "应届毕业生起薪，悉尼/墨尔本通常高于平均", "sort_order": 0},
    {"experience": "中级工程师（2~5年）", "salary_min": 95000, "salary_max": 125000, "salary_note": "SEEK 区间 $105k~$125k；Indeed 平均 $109,692（2026）", "sort_order": 1},
    {"experience": "高级工程师（5~10年）", "salary_min": 130000, "salary_max": 170000, "salary_note": "Indeed Senior 平均 $152,409；悉尼/墨尔本顶层约 $190k", "sort_order": 2},
    {"experience": "首席/Principal工程师（10年+）", "salary_min": 170000, "salary_max": 250000, "salary_note": "Atlassian/Canva/WiseTech 等顶尖公司高端岗位薪资", "sort_order": 3},
    {"experience": "合同工（Daily Rate）", "salary_min": 120000, "salary_max": 220000, "salary_note": "合同工日薪 $600~$1,200（年化约 $120k~$240k）", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，IT为核心紧缺类别，处理速度快", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，ACS评估+EOI", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，ACT/NSW/VIC科技移民通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区IT岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "数据结构、算法和系统设计需要系统学习，自学路径可行"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "CS学位3~4年；训练营+自学约6~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "ACS评估主要是学历审核，无高难度考试"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "联邦数字化转型和AI浪潮持续推高需求，是澳洲需求量最大的IT职业"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级岗位竞争较激烈，但高级工程师极度供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "项目冲刺期强度高，日常工作节奏相对灵活"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "中级约 $95k~$125k；高级 $130k~$170k；顶级 $170k~$250k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "AI工具推高对高级工程师需求；澳洲科技产业持续扩张"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "初级编码任务受AI Copilot冲击，系统架构和复杂工程能力更有价值"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，189/190/482多路径，ACS评估相对简单"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "ACS评估和EOI分数竞争是主要门槛，高技能者分数通常足够"},
]
SUITABILITY_FIT = ["已有软件开发经验（2年以上），希望通过技术移民来澳", "英语能力达到 IELTS 6.0+ / PTE 50+（ACS评估和工作环境均需英语）", "有扎实的编程基础（Python/Java/TypeScript/Go等主流语言）", "有云平台（AWS/Azure/GCP）或AI/ML开发经验（薪资溢价高）", "目标是悉尼/墨尔本科技公司或远程工作（灵活度高）"]
SUITABILITY_UNFIT = ["英语能力极弱，无法胜任英语工作环境", "仅有初级编程经验（无实际项目经验）", "不适应持续学习和快速技术迭代的工作节奏"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "软件工程师薪资区间 $105k~$125k（2026）", "url": "https://au.seek.com/career-advice/role/software-engineer/salary"},
    {"source_name": "Indeed AU", "content": "软件工程师平均薪资 $109,692（2026）", "url": "https://au.indeed.com/career/software-engineer/salaries"},
    {"source_name": "Australian Computer Society (ACS)", "content": "技能评估机构，189/190签证必须", "url": "https://www.acs.org.au/"},
    {"source_name": "Jobs and Skills Australia", "content": "ICT职业短缺清单和就业预测", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲软件工程师工资多少？", "answer": "中级工程师年薪约 $95,000~$125,000（Indeed平均$109,692）；高级工程师约 $130,000~$170,000；Atlassian/Canva等顶级公司 $170,000~$250,000+。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲软件工程师容易找工作吗？", "answer": "高级工程师极容易；初级竞争较激烈。Seek 挂牌约 6,000~12,000 个职位，联邦数字化转型和AI产业扩张持续推高需求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国CS/计算机学位澳洲认可吗？", "answer": "通过 ACS（澳洲计算机学会）技能评估，约 $500 申请费，周期 2~6 个月。是189/190签证的必要步骤，通过率较高。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "软件工程师会被AI替代吗？", "answer": "初级编码（CRUD、重复模板）受AI Copilot冲击；但系统架构、复杂业务逻辑设计、代码审查和跨团队协调的需求反而增加。AI工具提高了工程师的整体产出。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲软件工程师有年龄限制吗？", "answer": "无法律限制。移民打分45岁以上无加分，建议35~42岁尽快申请。澳洲IT行业对年龄偏见少于美国科技公司。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲软件工程师需要大学学历吗？", "answer": "技术移民ACS评估通常需要相关本科学历，但有丰富项目经验+强作品集的自学者也有机会通过雇主担保（482签证）入职。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲软件工程师认证/移民难吗？", "answer": "相对其他技术类职业较简单。ACS评估主要是学历审核，无高难度考试；189/190签证主要看EOI分数，高技能者通常可在1~2年内获邀。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "软件工程师和网络安全工程师哪个更适合移民澳洲？", "answer": "两者均是极佳移民职业。软件工程师就业量更大（Seek ~10000+），薪资略低；网络安全工程师薪资更高（$127k~$148k vs $105k~$125k），但职位数量更少。有安全背景者选网络安全，有开发背景者选软件工程师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 软件工程师数据入库完成")

if __name__ == "__main__":
    run()
