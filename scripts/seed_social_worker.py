"""澳洲社会工作者（272511）数据入库。数据来源：JSA、SEEK、Indeed、AASW（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "272511", "anzsco_title": "Social Worker",
    "category": "教育/社会服务", "workforce_size": 65000, "shortage_listed": 1,
    "growth_areas": json.dumps(["NDIS（残疾支持计划）社会工作","儿童保护与家庭支持","老年护理社会工作","心理健康社会工作","偏远地区和土著社区社会工作"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "社会工作者",
    "summary": "社会工作者为个人、家庭和社区提供福利评估、危机干预、案例管理和倡导服务，覆盖儿童保护、老年护理、心理健康、残疾和移民服务等领域。澳洲NDIS（国家残疾保险计划）的持续扩张和老龄化社会推动对社会工作者的旺盛需求，是工作意义感最强的社会服务职业之一。",
    "forecast_note": "JSA预测社会工作者至2035年就业增长约14%。NDIS社会工作（残疾评估与计划制定）和儿童保护是需求增长最快的两个方向。偏远和土著社区社会工作者缺口极大。",
    "trend_summary": "NDIS持续扩张（2026年覆盖人数超60万）是澳洲社会工作就业增长的最大驱动力，NDIS协调员（Support Coordinator）和计划管理社会工作者需求急增。老龄化政策（Royal Commission后的改革）推动老年护理社会工作者需求大幅增加。",
}
I18N_EN = {
    "locale": "en", "name": "Social Worker",
    "summary": "Social workers provide welfare assessment, crisis intervention, case management and advocacy for individuals, families and communities across child protection, aged care, mental health, disability and migration services. Australia's expanding NDIS and ageing society drive strong sustained demand — one of the most purposeful social service professions.",
    "forecast_note": "JSA projects ~14% employment growth for social workers by 2035. NDIS social work (disability assessment and plan development) and child protection are the fastest-growing directions. Remote and Indigenous community social workers face acute shortages.",
    "trend_summary": "NDIS expansion (600,000+ participants by 2026) is the biggest employment growth driver for Australian social workers. NDIS support coordination and plan management social workers are in acute demand. Aged care social workers are surging following Royal Commission reforms.",
}
EDUCATION = [
    {"stage": "Bachelor of Social Work（BSW，4年，AASW认可）", "duration": "4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "AASW认可的社会工作学位是注册社会工作者的基本要求；国际生约 $28,000~$38,000/年", "sort_order": 0},
    {"stage": "Master of Social Work（MSW，2年，已有相关学士学位者）", "duration": "2年（全日制）", "cost_min": 30000, "cost_max": 80000, "cost_note": "持有相关学科本科者可通过MSW快速获取社会工作资格", "sort_order": 1},
    {"stage": "AASW 海外社会工作资格认证", "duration": "3~6个月", "cost_min": 500, "cost_max": 2000, "cost_note": "澳洲社会工作者协会（AASW）对海外社会工作学历的评估，约 $480 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "AASW会员资格（Member of AASW）", "issuer": "Australian Association of Social Workers（AASW）", "note": "澳洲社会工作者专业会员资格，是政府和大型机构就业的实际要求", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "AASW海外资格认证", "issuer": "AASW", "note": "189/190签证技术移民和海外社工必须，约 $480 申请费", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Working With Children Check", "issuer": "各州政府", "note": "涉及儿童和青少年服务的社会工作者法律必须", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "NDIS Worker Screening Check", "issuer": "各州NDIS机构", "note": "NDIS服务提供者雇佣时法律必须的背景审查", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2500, "count_max": 6000, "note": "全国，含儿童保护/NDIS/老年护理/心理健康/移民服务社工岗"},
    {"platform": "Indeed",   "count_min": 2000, "count_max": 5000, "note": "含政府机构和非政府组织（NGO）社工岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 5000, "note": "大型NGO和政府社会服务部门直招"},
]
SALARIES = [
    {"experience": "初级社会工作者（0~2年）", "salary_min": 65000, "salary_max": 80000, "salary_note": "毕业社工起薪；NGO和政府机构略有差异", "sort_order": 0},
    {"experience": "有经验社会工作者（2~8年）", "salary_min": 85000, "salary_max": 108000, "salary_note": "SEEK 区间 $95k~$110k；Indeed 均值 $98,403（2026）", "sort_order": 1},
    {"experience": "高级/专精社会工作者（8~15年）", "salary_min": 105000, "salary_max": 135000, "salary_note": "NDIS专业社工、儿童保护高级案例工作者；堪培拉ACT均值 $100k~$120k", "sort_order": 2},
    {"experience": "社工主任 / 团队负责人（15年+）", "salary_min": 130000, "salary_max": 180000, "salary_note": "政府部门社工主任或大型NGO项目总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，NGO和政府机构常直接担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，AASW评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，各州均有通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区社工极度紧缺，加15分，多州积极提名", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要心理学+社会学+法律知识综合，实习期（约1000小时）挑战较大"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "BSW 4年或MSW 2年（需先有本科）；AASW评估约3~6个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "AASW评估难度中等；需要英语能力和实习经验证明"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL短缺职业，NDIS扩张和人口老龄化推动持续旺盛需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "NDIS和偏远地区社工供不应求；城市区域竞争相对较高"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "儿童保护和危机干预岗情感压力大；工作量大，需要强大的心理韧性"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "有经验社工 $85k~$108k；专精NDIS/儿童保护 $105k~$135k；整体低于商业类"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "NDIS扩张+人口老龄化+心理健康需求增加是社会工作20年以上的增长引擎"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "社会工作中人际关系建立、危机判断和倡导工作是AI无法替代的核心价值"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，AASW评估路径成熟，偏远地区491路径大幅降低移民门槛"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "AASW评估路径清晰；需要英语能力证明和实习经验；偏远491最容易"},
]
SUITABILITY_FIT = ["持有社会工作或相关学科（心理学/社会学/公共卫生）学位，有社工相关工作经验", "英语沟通能力强（IELTS 7.0+，客户服务和报告撰写要求）", "有NDIS、儿童保护、老年护理或心理健康相关工作经验（需求最旺盛方向）", "有耐心、同理心和心理韧性（社会工作的核心职业素质）", "愿意接受偏远地区或土著社区任职（缺口极大，491签证加分明显）"]
SUITABILITY_UNFIT = ["心理承受能力较弱，无法应对高情感强度的危机干预工作", "英语沟通能力不足，无法进行专业客户访谈和报告撰写", "期望高薪（$120k+）快速回报的求职者（社工薪资整体低于商业类）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "社会工作者薪资 $95k~$110k（2026）", "url": "https://au.seek.com/career-advice/role/social-worker/salary"},
    {"source_name": "Indeed AU", "content": "社会工作者平均薪资 $98,403（2026）", "url": "https://au.indeed.com/career/social-worker/salaries"},
    {"source_name": "AASW", "content": "澳洲社会工作者协会资格认证", "url": "https://www.aasw.asn.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲社会工作者工资多少？", "answer": "有经验社工约 $85,000~$108,000（Indeed均值 $98,403；SEEK $95k~$110k）；NDIS/儿童保护专精高级社工约 $105k~$135k；ACT社工均值 $100k~$120k；主任级社工约 $130k~$180k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲社会工作者容易找工作吗？", "answer": "容易。NDIS扩张（超60万参与者）和人口老龄化推动极强需求，Seek 挂牌约 2,500~6,000 个职位。偏远地区和NDIS专精社工供不应求，政府主动吸引海外社工。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国社会工作经验澳洲认可吗？", "answer": "通过AASW海外资格评估（约 $480），中国社会工作学历和工作经验可以认可。需要提供实习时间证明（实际服务时间）和英语能力（IELTS 7.0+）。中国民政系统和NGO的社工经验通常可以认可。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "社会工作者会被AI替代吗？", "answer": "不会。社会工作中危机评估、信任建立、倡导和个案判断需要人际关系和情感智慧，是AI无法替代的核心价值。AI辅助文书记录和资源匹配，但实际服务工作完全依赖人类社工。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲社会工作者有年龄限制吗？", "answer": "无。有生活经验和人生阅历的中年社工（35~55岁）在处理复杂家庭和危机案例时具有独特优势，特别是在老年护理和家庭支持领域。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲社会工作者需要什么学历？", "answer": "AASW认可的社会工作学位（BSW或MSW）是成为注册社工和大多数政府机构职位的基本要求。相关学科（心理学/社会学）本科+两年MSW是国际学生的主流快速路径。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲社工认证（移民）难吗？", "answer": "难度中等偏低。AASW评估路径清晰（$480），英语达标（IELTS 7.0+）后流程顺畅。偏远地区491路径大幅降低移民门槛，多州积极通过491提名缺口严重地区的社工。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "社会工作者和护士哪个更适合移民澳洲？", "answer": "两者都是MLTSSL短缺职业；护士薪资略高（$95k~$120k vs 社工 $85k~$108k），工作更规律；社工工作意义感更强，NDIS方向增长空间更大。有医疗护理背景者选护士，有心理学/社会科学背景者选社工。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 社会工作者数据入库完成")

if __name__ == "__main__":
    run()
