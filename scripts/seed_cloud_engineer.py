"""澳洲云计算工程师（263111）数据入库。数据来源：JSA、SEEK、Indeed、AWS/Azure（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "263111", "anzsco_title": "Computer Network and Systems Engineer",
    "category": "IT/工程", "workforce_size": 55000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Multi-Cloud Architecture (AWS/Azure/GCP)","Cloud Security & Compliance","Platform Engineering & Kubernetes","Government Cloud Migration","FinOps & Cloud Cost Optimisation"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "云计算工程师",
    "summary": "云计算工程师设计、部署和管理基于AWS、Azure、GCP的云基础设施，覆盖云架构、DevOps、容器化、网络和安全。澳洲联邦政府「云优先」政策和企业大规模数据中心上云推动需求持续旺盛，是IT类薪资最高的专业之一。",
    "forecast_note": "JSA 预测云和系统工程师至2035年就业增长约22%。政府云迁移（ASD Cloud Security Guidelines）和企业AI基础设施建设是主要驱动力。",
    "trend_summary": "平台工程（Platform Engineering）和FinOps（云成本优化）是2025-2026年增长最快的子领域。多云架构（同时管理AWS+Azure+GCP）的工程师薪资溢价 $15k~$30k。",
}
I18N_EN = {
    "locale": "en", "name": "Cloud Engineer",
    "summary": "Cloud engineers design, deploy and manage AWS, Azure and GCP cloud infrastructure covering architecture, DevOps, containerisation, networking and security. Federal cloud-first policy and enterprise cloud migration drive sustained high demand.",
    "forecast_note": "JSA projects ~22% employment growth for cloud/systems engineers by 2035. Government cloud migration and enterprise AI infrastructure build-out are the primary demand drivers.",
    "trend_summary": "Platform Engineering and FinOps are the fastest-growing sub-disciplines. Multi-cloud engineers (AWS+Azure+GCP) command $15k~$30k salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of Computer Science / IT / Engineering（3~4年）", "duration": "3~4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "基础学历，实际工作中认证权重不低于学位", "sort_order": 0},
    {"stage": "云平台认证（AWS/Azure/GCP Professional Level）", "duration": "2~6个月备考", "cost_min": 1500, "cost_max": 5000, "cost_note": "AWS Solutions Architect Professional 约 $300 考试费；是澳洲云工程师岗位强烈推荐的认证", "sort_order": 1},
    {"stage": "ACS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民必须的学历认证机构", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "AWS Certified Solutions Architect – Professional", "issuer": "Amazon Web Services", "note": "澳洲市场最认可的云认证，持有者薪资溢价显著", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Microsoft Azure Solutions Architect Expert", "issuer": "Microsoft", "note": "政府/金融机构Azure岗位的强烈推荐认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Certified Kubernetes Administrator (CKA)", "issuer": "CNCF", "note": "容器化和平台工程方向的重要技术认证", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "ACS 技能评估", "issuer": "Australian Computer Society", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 4000, "note": "全国，含云架构师、DevOps工程师、平台工程师和云安全岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 3000, "note": "含合同和远程岗"},
    {"platform": "LinkedIn", "count_min": 3000, "count_max": 6000, "note": "企业和政府直招，猎头活跃"},
]
SALARIES = [
    {"experience": "初级云工程师（0~3年）", "salary_min": 80000, "salary_max": 110000, "salary_note": "持Associate级认证，含基础云运维岗", "sort_order": 0},
    {"experience": "中级云工程师（3~6年）", "salary_min": 110000, "salary_max": 150000, "salary_note": "SEEK 区间 $125k~$145k；Indeed 平均 $126,688（2026）", "sort_order": 1},
    {"experience": "高级/云架构师（6~10年）", "salary_min": 150000, "salary_max": 200000, "salary_note": "Professional级认证+多云架构经验", "sort_order": 2},
    {"experience": "首席云架构师 / CTO路径（10年+）", "salary_min": 200000, "salary_max": 300000, "salary_note": "大型金融/政府机构云转型领头人", "sort_order": 3},
    {"experience": "合同工（Daily Rate）", "salary_min": 130000, "salary_max": 250000, "salary_note": "合同云工程师日薪 $700~$1,300（年化约 $140k~$260k）", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，云工程师为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，ACT/NSW/VIC科技移民通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区IT岗，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "需要系统理解网络、存储、计算和安全的整合，认证路径结构清晰"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3~4年；单平台认证路径自学可在6~12个月达到Associate级"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "AWS Professional级考试难度较高；多平台认证积累需要时间"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "政府云迁移+企业AI基础设施+多云普及，是增速最快的IT岗位之一"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持Professional级认证工程师极度供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "随叫随到的生产环境支持有压力，但总体工作节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中位数约 $125k~$150k，是所有IT职业中薪资最高的类别之一"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "云是数字化基础设施的核心，AI工作负载驱动云支出持续增长"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI基础设施本身需要云工程师来部署和管理，AI增加了云工程需求"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，Professional级认证大幅提升189/190邀请分"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "ACS评估和EOI分数是门槛，Professional认证有效提升竞争力"},
]
SUITABILITY_FIT = ["有云平台工作经验（AWS/Azure/GCP，2年以上）", "持有云认证（至少Associate级），或正在备考Professional", "有DevOps/Kubernetes/Terraform等基础设施自动化经验", "英语能力达到 IELTS 6.5+", "目标是联邦政府云迁移岗位（稳定）或顶级科技公司（高薪）"]
SUITABILITY_UNFIT = ["无云平台实际工作经验（仅理论学习）", "不愿意持续学习新服务（云平台每年推出数百个新功能）", "英语能力极弱，无法在团队中有效沟通"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "云工程师薪资 $125k~$145k（2026）", "url": "https://au.seek.com/career-advice/role/cloud-engineer/salary"},
    {"source_name": "Indeed AU", "content": "云工程师平均薪资 $126,688（2026）", "url": "https://au.indeed.com/career/cloud-engineer/salaries"},
    {"source_name": "ACS", "content": "技能评估机构，189/190签证必须", "url": "https://www.acs.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲云计算工程师工资多少？", "answer": "中级云工程师约 $110,000~$150,000（Indeed均值 $126,688）；云架构师约 $150k~$200k；首席架构师可超 $250k。合同工日薪 $700~$1,300。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲云计算工程师容易找工作吗？", "answer": "极容易。Seek 挂牌约 2000~4000 个职位，政府云迁移和企业AI基础设施建设驱动需求，持Professional认证者主动被猎头联系。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国云工程师经验澳洲认可吗？", "answer": "通过 ACS 技能评估即可（学历审核），云平台认证（AWS/Azure/GCP）是国际通用认证，在澳洲完全认可。实际工作经验+认证组合是最强的竞争力。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "云工程师会被AI替代吗？", "answer": "风险极低。AI大模型本身需要大量云基础设施来运行，云工程需求反而因AI浪潮急剧增加。AI工具辅助配置生成，但架构决策和复杂排障仍需人工。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲云工程师有年龄限制吗？", "answer": "无。IT行业对年龄偏见少，丰富的企业架构经验在市场上具有高溢价。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲云工程师需要什么学历？", "answer": "CS/IT相关学位是主流，但持有 AWS/Azure Professional 级认证+5年以上经验的非CS学历者同样竞争力强。ACS技能评估对相关学科的认可范围较广。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲云工程师认证（移民）难吗？", "answer": "难度中等。ACS评估不难，Professional级云认证需要深入实战经验，189/190邀请分对持高端认证的工程师友好。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "云工程师和DevOps工程师哪个更适合移民澳洲？", "answer": "云工程师薪资略高（$125k~$145k vs $120k~$140k），两者技能高度重叠。云工程师更偏基础设施架构；DevOps更偏CI/CD流水线和自动化。有架构经验者选云工程师，有pipeline经验者选DevOps。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 云计算工程师数据入库完成")

if __name__ == "__main__":
    run()
