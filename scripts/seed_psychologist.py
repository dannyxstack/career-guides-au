"""澳洲心理学家（272311）数据入库。数据来源：JSA、SEEK、Indeed、APS（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "272311", "anzsco_title": "Clinical Psychologist",
    "category": "教育/社会服务", "workforce_size": 40000, "shortage_listed": 1,
    "growth_areas": json.dumps(["临床心理学（Medicare Better Access项目）","儿童与青少年心理学","NDIS心理支持服务","网络/远程心理咨询","神经心理学与认知康复"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "心理学家（临床心理学家）",
    "summary": "心理学家（特别是临床心理学家）为个人提供心理评估、诊断和循证治疗，覆盖焦虑、抑郁、创伤、儿童发展和神经心理等领域。澳洲心理健康危机（COVID后激增）和Medicare Better Access计划（每人每年最多20次心理咨询补贴）推动对心理学家的强劲需求，是医疗健康领域薪资最高的非医生职业之一。",
    "forecast_note": "JSA预测心理学家至2035年就业增长约19%，是增速最快的医疗类职业之一。青少年心理健康危机、NDIS心理服务扩张和老年人认知健康需求是三大增长驱动力。",
    "trend_summary": "澳洲心理健康需求持续爆发（等待就诊时间从2周延长至6个月以上），临床心理学家全国严重短缺。远程心理咨询（Telehealth）在COVID后成为主流服务模式，大幅扩大了心理学家的服务覆盖范围。",
}
I18N_EN = {
    "locale": "en", "name": "Psychologist (Clinical)",
    "summary": "Psychologists (particularly clinical psychologists) provide psychological assessment, diagnosis and evidence-based treatment for anxiety, depression, trauma, child development and neuropsychology. Australia's mental health crisis (post-COVID surge) and Medicare Better Access (up to 20 subsidised sessions/person/year) drive strong demand — one of the highest-paid non-physician health professions.",
    "forecast_note": "JSA projects ~19% employment growth for psychologists by 2035 — among the fastest-growing health occupations. Youth mental health crisis, NDIS psychology service expansion and elderly cognitive health needs are the three major growth drivers.",
    "trend_summary": "Australia's mental health demand continues to surge (wait times extending from 2 weeks to 6+ months). Clinical psychologists are in severe nationwide shortage. Telehealth has become a mainstream service model post-COVID, significantly expanding psychologists' service reach.",
}
EDUCATION = [
    {"stage": "Bachelor of Psychology（荣誉学位/4年）+ 研究生资格（必须）", "duration": "本科4年（Honours）或 3年+1年honours", "cost_min": 25000, "cost_max": 160000, "cost_note": "澳洲注册心理学家必须持有APAC认可的4年（含Honours）心理学学位", "sort_order": 0},
    {"stage": "临床心理学硕士（Masters in Clinical Psychology，2年）", "duration": "2年（全日制研究生）", "cost_min": 25000, "cost_max": 80000, "cost_note": "临床心理学家资格要求；入学极具竞争性（通常需要GPA 6.5+/7.0）", "sort_order": 1},
    {"stage": "心理学委员会注册（AHPRA Registration）+ 2年受监督实习", "duration": "2年受监督实习（通配注册心理学家路径）", "cost_min": 500, "cost_max": 2000, "cost_note": "AHPRA注册约 $450/年；完成4年本科+2年受监督实习可成为注册心理学家", "sort_order": 2},
    {"stage": "AHPRA 海外资格认证", "duration": "3~9个月", "cost_min": 500, "cost_max": 3000, "cost_note": "海外心理学资格通过AHPRA评估，约 $500~$1,000 申请费", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "AHPRA注册（心理学家）", "issuer": "AHPRA（澳洲健康从业者监管局）", "note": "澳洲合法执业心理学家的法律要求，缺少此注册不可执业", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "临床心理学家认可（Clinical Psychologist Endorsement）", "issuer": "AHPRA / Psychology Board of Australia", "note": "提供Medicare Better Access全额补贴服务的必要资格；薪资显著高于普通注册心理学家", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "APS会员（Australian Psychological Society）", "issuer": "APS", "note": "行业协会会员资格，提升执业信誉", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Medicare Provider Number", "issuer": "Services Australia", "note": "独立执业心理学家提供Medicare补贴咨询服务的必要注册", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 4000, "note": "全国，含临床/学校/NDIS/组织/神经心理学家岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 3000, "note": "含Medicare私人执业、医院、学校和NDIS服务机构岗"},
    {"platform": "LinkedIn", "count_min": 1500, "count_max": 4000, "note": "私人诊所和医疗健康机构直招"},
]
SALARIES = [
    {"experience": "注册心理学家（0~3年实习后）", "salary_min": 85000, "salary_max": 110000, "salary_note": "通配注册（General Registration）心理学家，受监督实习完成后的起薪", "sort_order": 0},
    {"experience": "临床心理学家（3~8年，有Endorsement）", "salary_min": 110000, "salary_max": 135000, "salary_note": "SEEK 临床心理学家区间 $120k~$125k；Indeed 均值 $120,616（2026）", "sort_order": 1},
    {"experience": "资深临床心理学家（8~15年）", "salary_min": 130000, "salary_max": 180000, "salary_note": "私人执业资深临床心理学家，含Medicare补贴业务；PayScale 普通心理学家 $87,746（2026）", "sort_order": 2},
    {"experience": "独立私人执业（10年+）", "salary_min": 150000, "salary_max": 350000, "salary_note": "独立私人诊所，Medicare补贴+私费咨询，收入上限极高", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，医疗机构和NDIS服务商常担保心理学家", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，AHPRA评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，心理健康短缺各州均积极提名", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区心理学家极度紧缺，加15分，多州积极提名", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "需要顶尖学业成绩（临床硕士入学GPA要求高）+2年受监督实习，总周期极长"},
    {"dimension": "learning_duration",        "label_zh": "极长", "stars": 5, "note": "4年本科honours+2年临床硕士+2年受监督实习=总周期8~10年"},
    {"dimension": "certification_difficulty", "label_zh": "极高", "stars": 5, "note": "临床心理学硕士入学极具竞争性；AHPRA海外资格认证有一定复杂性"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL短缺职业，全国心理健康危机推动极度紧缺状态"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "临床心理学家全国严重短缺，被机构和私人诊所主动争抢"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "私人执业节奏相对自主；情感共情型工作有情绪消耗，但强度低于急诊医疗"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "临床心理学家 $110k~$135k；私人执业 $150k~$350k，是非医生医疗职业中收入上限最高的"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "澳洲心理健康危机预计持续20年以上；Medicare补贴政策确保稳定需求"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "心理治疗核心在于人际关系和情感共情，是AI替代风险最低的职业之一"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，AHPRA评估路径清晰，是医疗类移民最便利的职业之一"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "AHPRA海外资格评估有一定复杂性，受监督实习期要求需要在澳完成或互认"},
]
SUITABILITY_FIT = ["持有心理学学位（APAC/APS认可），有心理咨询或临床实习经验", "英语能力强（IELTS 7.5+，临床访谈和报告撰写要求高）", "有儿童/青少年心理学、NDIS心理支持或神经心理学专长（需求最旺盛）", "有意通过AHPRA海外资格评估+澳洲受监督实习完成本地资格认证", "愿意接受偏远地区任职（等待时间短、扶持政策多，签证更容易）"]
SUITABILITY_UNFIT = ["英语能力不足（临床访谈和专业报告撰写要求IELTS 7.5+）", "仅持有心理学本科（无Honours/Masters），无法通过AHPRA认证为临床心理学家", "不愿意承担8~10年的漫长资格路径（建议通过澳洲本地研究生路径加速）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "临床心理学家薪资 $120k~$125k（2026）", "url": "https://au.seek.com/career-advice/role/clinical-psychologist/salary"},
    {"source_name": "Indeed AU", "content": "临床心理学家平均薪资 $120,616（2026）", "url": "https://au.indeed.com/career/clinical-psychologist/salaries"},
    {"source_name": "PayScale AU", "content": "心理学家平均薪资 $87,746（2026）", "url": "https://www.payscale.com/research/AU/Job=Psychologist/Salary"},
    {"source_name": "AHPRA", "content": "澳洲心理学家注册和海外资格认证", "url": "https://www.ahpra.gov.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲心理学家工资多少？", "answer": "临床心理学家约 $110,000~$135,000（SEEK $120k~$125k；Indeed $120,616）；资深临床心理学家约 $130k~$180k；独立私人执业约 $150k~$350k（含Medicare补贴业务）。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲心理学家容易找工作吗？", "answer": "极容易（有资格者）。临床心理学家全国严重短缺，Seek 挂牌约 1,500~4,000 个职位，NDIS心理服务和远程心理咨询岗需求急增。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国心理学资历澳洲认可吗？", "answer": "通过AHPRA海外资格评估，中国心理学学历可以评估。主要挑战是：①中国临床心理学培训体系与澳洲差异较大；②可能需要在澳洲完成额外的受监督实习期。建议通过在澳大学攻读Master of Clinical Psychology（2年）作为最直接的本地资格路径。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "心理学家会被AI替代吗？", "answer": "不会。心理治疗的核心是人际关系建立（治疗同盟）、情感共情和个体化干预，是AI无法提供的。AI辅助心理健康APP（Woebot等）是低强度补充工具，不替代专业心理学家。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲心理学家有年龄限制吗？", "answer": "无。有人生经验和临床积累的中年心理学家（40~60岁）在处理复杂创伤、人生转折和关系问题时具有独特优势，特别是在私人执业市场中更受信任。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲心理学家需要什么学历？", "answer": "APAC认可的4年心理学学位（含Honours）是基础要求。临床心理学家还需要2年临床硕士（竞争极激烈）或2年受监督实习（通配路径）。总资格路径约8~10年。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲心理学家认证（移民）难吗？", "answer": "AHPRA评估路径可行，但总资格路径长（8~10年）。建议有海外心理学资历者通过AHPRA评估+在澳完成剩余实习期，或通过在澳大学就读Master of Clinical Psychology（2年）直接获取本地资格。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "心理学家和社会工作者哪个更适合移民澳洲？", "answer": "两者均为MLTSSL短缺职业；心理学家薪资更高（$110k~$350k vs 社工 $85k~$135k），但资格路径更长（8~10年 vs 4年）；社工就业多样性更广。有心理学硕士学位者选心理学家，有社会科学本科背景者选社会工作（MSW 2年即可）。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 心理学家数据入库完成")

if __name__ == "__main__":
    run()
