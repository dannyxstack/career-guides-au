"""澳洲DevOps工程师（261399）数据入库。数据来源：JSA、SEEK、Indeed、PayScale（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "261399", "anzsco_title": "ICT Developers and Programmers nec",
    "category": "IT/工程", "workforce_size": 45000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Platform Engineering & Internal Developer Platforms","GitOps & Infrastructure as Code","SRE & Reliability Engineering","DevSecOps (Security in CI/CD)","AI/ML Pipeline Automation"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "DevOps工程师",
    "summary": "DevOps工程师构建和维护CI/CD流水线、基础设施自动化和云原生部署平台，通过Kubernetes、Terraform、GitHub Actions等工具加速软件交付。澳洲企业大规模迁移云端推动DevOps需求持续增长，是IT类薪资最高的职业之一。",
    "forecast_note": "JSA 预测DevOps/平台工程师至2035年就业增长约20%。平台工程（Platform Engineering）是2025-2026年演进方向，提升内部开发者体验（IDP）。",
    "trend_summary": "平台工程正在取代传统DevOps模式，专注于构建内部开发者平台（IDP）。DevSecOps（安全集成CI/CD）是最紧缺的子领域，薪资溢价 $15k~$25k。",
}
I18N_EN = {
    "locale": "en", "name": "DevOps Engineer",
    "summary": "DevOps engineers build and maintain CI/CD pipelines, infrastructure automation and cloud-native deployment platforms using Kubernetes, Terraform and GitHub Actions. Enterprise cloud adoption is driving sustained high demand.",
    "forecast_note": "JSA projects ~20% employment growth for DevOps/platform engineers by 2035. Platform Engineering (IDP focus) is the 2025-2026 evolution direction.",
    "trend_summary": "Platform Engineering is superseding traditional DevOps, focusing on Internal Developer Platforms (IDP). DevSecOps commands the highest salary premiums ($15k~$25k above standard DevOps).",
}
EDUCATION = [
    {"stage": "Bachelor of Computer Science / Software Engineering（3~4年）", "duration": "3~4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "基础学历，实际工作中认证+工具熟练度权重高于学位", "sort_order": 0},
    {"stage": "DevOps认证（CKA / Terraform Associate / AWS DevOps Professional）", "duration": "2~6个月备考", "cost_min": 1000, "cost_max": 4000, "cost_note": "CKA（$395）、Terraform Associate（$70）是市场最认可的DevOps认证", "sort_order": 1},
    {"stage": "ACS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民必须", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certified Kubernetes Administrator (CKA)", "issuer": "CNCF", "note": "DevOps/平台工程最重要的认证，持有者薪资溢价明显", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "HashiCorp Terraform Associate / Professional", "issuer": "HashiCorp", "note": "IaC（基础设施即代码）领域最广泛使用的认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "AWS DevOps Engineer Professional", "issuer": "Amazon Web Services", "note": "AWS生态DevOps方向的高级认证", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "ACS 技能评估", "issuer": "Australian Computer Society", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 3000, "note": "全国，含DevOps工程师、平台工程师、SRE和CI/CD工程师岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 2000, "note": "含合同工和远程岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 4000, "note": "企业直招和猎头"},
]
SALARIES = [
    {"experience": "初级DevOps工程师（0~3年）", "salary_min": 80000, "salary_max": 105000, "salary_note": "含基础CI/CD和云运维经验", "sort_order": 0},
    {"experience": "中级DevOps工程师（3~6年）", "salary_min": 110000, "salary_max": 140000, "salary_note": "SEEK 平均 $120k~$140k；Indeed 平均 $123,052（2026）", "sort_order": 1},
    {"experience": "高级/平台工程师（6~10年）", "salary_min": 140000, "salary_max": 185000, "salary_note": "平台工程负责人和SRE高级岗，含Kubernetes架构经验", "sort_order": 2},
    {"experience": "DevSecOps / 安全专精（5年+）", "salary_min": 145000, "salary_max": 195000, "salary_note": "安全集成CI/CD是薪资溢价最高的DevOps子领域", "sort_order": 3},
    {"experience": "合同工（Daily Rate）", "salary_min": 120000, "salary_max": 220000, "salary_note": "日薪 $650~$1,150（年化约 $130k~$230k）", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，DevOps为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，ACT/NSW/VIC科技移民通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区IT岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "需要系统理解Linux、网络、容器、CI/CD和云平台的综合技术栈"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "从0到胜任中级岗位约2~3年（含学位或自学+认证路径）"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CKA是实操考试，有难度但有系统学习方法；Terraform Associate相对容易"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "企业云化和CI/CD成熟化驱动持续高需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持CKA+Terraform等认证工程师供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "生产环境on-call压力较大，事故响应需要深夜处理"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "中位数约 $120k~$140k；高级工程师可达 $185k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "平台工程和AI流水线自动化是DevOps的持续演进方向"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助脚本生成，但系统架构决策和故障诊断仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，189/190/482多路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "ACS评估和EOI分数是门槛，认证有效提升竞争力"},
]
SUITABILITY_FIT = ["有Linux/Docker/Kubernetes实际工作经验（2年以上）", "熟悉CI/CD工具（GitHub Actions/Jenkins/ArgoCD），有云平台经验", "英语能力达到 IELTS 6.5+", "有CKA或Terraform认证，或正在备考", "目标是大型企业平台工程团队或DevSecOps方向"]
SUITABILITY_UNFIT = ["无Linux/Shell脚本基础，无法处理生产环境故障", "不适应on-call值班和深夜故障响应", "仅有开发经验，对基础设施和网络知识空白"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "DevOps工程师薪资 $120k~$140k（2026）", "url": "https://au.seek.com/career-advice/role/devops-engineer/salary"},
    {"source_name": "Indeed AU", "content": "DevOps工程师平均薪资 $123,052（2026）", "url": "https://au.indeed.com/career/devops-engineer/salaries"},
    {"source_name": "ACS", "content": "技能评估机构", "url": "https://www.acs.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲DevOps工程师工资多少？", "answer": "中级DevOps工程师约 $110,000~$140,000（Indeed均值 $123,052）；高级工程师约 $140k~$185k；DevSecOps专精约 $145k~$195k。合同工日薪 $650~$1,150。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲DevOps工程师容易找工作吗？", "answer": "容易。Seek 挂牌约 1500~3000 个职位，企业云化持续推高需求，持CKA+Terraform认证者主动被猎头联系。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国DevOps经验澳洲认可吗？", "answer": "通过 ACS 技能评估（学历审核），CKA/Terraform/AWS等认证是国际通用的，在澳洲完全认可。GitHub上的开源贡献也是有效的能力证明。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "DevOps工程师会被AI替代吗？", "answer": "风险较低。AI工具辅助脚本生成和配置，但生产环境架构决策、故障根因分析和跨团队协调仍需人工。AI反而增加了对平台工程师（管理AI工作负载基础设施）的需求。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲DevOps工程师有年龄限制吗？", "answer": "无。系统可靠性工程（SRE）领域特别重视有大规模生产环境经验的资深工程师，40岁以上有经验者在市场上具有竞争力。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲DevOps工程师需要什么学历？", "answer": "CS/IT相关学位是主流，但具有丰富实战经验+CKA/Terraform/AWS认证的工程师可通过雇主担保（482签证）绕过学历门槛。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲DevOps工程师认证（移民）难吗？", "answer": "难度中等。ACS评估不难；CKA是有难度的实操考试，建议充分实战练习；189/190 EOI分数对高技能者友好。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "DevOps工程师和云工程师哪个更适合移民澳洲？", "answer": "云工程师薪资略高（$125k~$145k vs $120k~$140k），两者技能高度重叠。DevOps更偏流水线和自动化；云工程师更偏基础设施架构。两者均可PR，建议结合自身技能方向选择。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] DevOps工程师数据入库完成")

if __name__ == "__main__":
    run()
