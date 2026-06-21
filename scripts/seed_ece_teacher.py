"""澳洲幼儿教育工作者（241111）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor、Department of Education（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "241111", "anzsco_title": "Early Childhood (Pre-primary School) Teacher",
    "category": "教育/社会服务", "workforce_size": 85000, "shortage_listed": 1,
    "growth_areas": json.dumps(["0~2岁婴幼儿教育（未纳入ECEC资助的增长空间）","STEM早期启蒙课程（Coding/Robotics for under-5s）","特殊需求幼儿融合教育","双语/多语幼儿教育","室外自然教育（Forest School/Nature Play）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "幼儿教育工作者（幼儿教师）",
    "summary": "幼儿教师（Early Childhood Teacher）持有大学教育学位，在幼儿园/学前班（0~5岁/Kindy）主导教育课程设计和实施，是澳洲幼儿教育与护理（ECEC）行业的专业核心岗位。政府推行《幼儿教育改革》（每间服务设施必须配备持证ECT）和普惠性幼儿教育政策推动对幼儿教师的持续旺盛需求。",
    "forecast_note": "JSA预测幼儿教师至2035年需求增长约15%。澳洲政府2023年起推行幼儿教育设施必须配备合格ECT的强制要求，大幅推动对幼儿教师的结构性需求。",
    "trend_summary": "澳洲政府2022-2030幼儿教育战略投资推动幼儿园入学率大幅提升，每周15小时普惠性幼儿教育政策（3岁和4岁儿童）进一步增加对幼儿教师的需求。薪资改革（多州提升幼教薪资）正在改善行业吸引力。",
}
I18N_EN = {
    "locale": "en", "name": "Early Childhood Teacher (ECT)",
    "summary": "Early Childhood Teachers hold university education degrees and lead curriculum design and delivery in childcare centres and kindergartens (0-5 year olds). They are the professional core of Australia's ECEC sector. Government reforms (mandatory qualified ECT per service) and universal early childhood education policy drive sustained strong demand.",
    "forecast_note": "JSA projects ~15% employment growth for early childhood teachers by 2035. The 2023+ government mandate requiring qualified ECTs in all childcare facilities creates structural demand growth.",
    "trend_summary": "Australian government 2022-2030 early childhood education strategy investment drives significant increases in kindergarten participation rates. Universal access (15hrs/week for 3 and 4 year olds) further increases ECT demand. Salary reforms across multiple states are improving sector attractiveness.",
}
EDUCATION = [
    {"stage": "Bachelor of Education（Early Childhood，4年）", "duration": "4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "或 Early Childhood + Primary双资质学位；国际生约 $28,000~$38,000/年", "sort_order": 0},
    {"stage": "Graduate Diploma of Education（Early Childhood）", "duration": "1~2年（研究生文凭，已有相关学位者）", "cost_min": 15000, "cost_max": 50000, "cost_note": "持有相关本科学位者可通过GDE快速获取ECT资质", "sort_order": 1},
    {"stage": "AITSL 海外幼儿教师资格认证 + 州注册", "duration": "3~6个月", "cost_min": 500, "cost_max": 2000, "cost_note": "AITSL评估+各州教师注册机构（如NSW NESA）注册；英语要求 IELTS 7.5+", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "澳洲州教师注册（Early Childhood）", "issuer": "各州注册机构（NESA/VIT/QCT等）", "note": "在幼儿园/学前班作为ECT任职的法律要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AITSL海外教师资格认证", "issuer": "AITSL", "note": "海外幼儿教师资格评估，189/190签证必须", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Working With Children Check", "issuer": "各州政府", "note": "所有幼教从业者法律必须，费用约免费~$110", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "First Aid Certificate（婴儿/儿童心肺复苏）", "issuer": "St John Ambulance / Red Cross等认可机构", "note": "幼儿教育从业者必须持有的急救认证", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 5000, "note": "全国，幼儿教师（ECT）职位数量庞大，各州均有明显缺口"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 4000, "note": "含幼儿园中心、学前班和家庭日托岗"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 3000, "note": "大型幼教连锁机构直招"},
]
SALARIES = [
    {"experience": "初级幼儿教师（0~2年）", "salary_min": 68000, "salary_max": 82000, "salary_note": "ECEC行业整体薪资低于中小学，但ECT层级高于普通幼教工作者", "sort_order": 0},
    {"experience": "幼儿教师（2~7年，ECT）", "salary_min": 80000, "salary_max": 105000, "salary_note": "SEEK ECT区间约 $85k~$105k；Indeed均值约 $84,400（$40.58/hr × 2080h）", "sort_order": 1},
    {"experience": "主任幼儿教师 / 教育主任（5年+）", "salary_min": 95000, "salary_max": 125000, "salary_note": "担任中心教育主任（Educational Leader）或主任教师（Lead Teacher）", "sort_order": 2},
    {"experience": "幼教中心园长 / 教育主任（10年+）", "salary_min": 110000, "salary_max": 150000, "salary_note": "大型幼教连锁机构园长或区域教育主任", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，幼教机构可担保ECT", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，AITSL评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，各州幼教严重短缺", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区幼教更紧缺，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要儿童发展理论+课程设计+儿童保护知识，实习强度较高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "B.Ed Early Childhood 4年；GDE路径2+1年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "AITSL评估难度中等；英语要求（IELTS 7.5+）是主要门槛"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL短缺职业，政府强制配置ECT推动结构性需求增长"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "持证ECT极度短缺，各机构主动争抢合格幼儿教师"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "照顾0~5岁儿童，体力和情感投入较高；文件记录要求多"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "ECT $80k~$105k；整体低于中小学教师；政府持续推动薪资改善"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "政府幼教战略投资+普惠性幼儿教育政策是20年以上的需求保障"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "幼儿教育中人际关系、情感安全感和发展性互动是AI无法替代的核心价值"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，各州主动招募海外幼儿教师，是最移民友好的教育职业"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "AITSL评估路径清晰；英语达标后门槛较低，偏远地区491更容易"},
]
SUITABILITY_FIT = ["持有幼儿教育/学前教育学位（师范学院学前教育专业），有幼教工作经验", "英语能力达到 IELTS 7.5 各单项（是注册硬性要求）", "有儿童保护培训和急救认证（或愿意在澳洲完成）", "热爱儿童并具有耐心和观察力（幼儿教育核心素质）", "愿意接受偏远地区任职（新州/昆州农村地区ECT极度紧缺）"]
SUITABILITY_UNFIT = ["英语能力不足 IELTS 7.5 各单项（是绝对门槛）", "仅持有幼儿园保育员资格（Certificate III/Diploma），未达到ECT大学学历要求", "不适应体力需求较高和文件记录密集的幼教工作"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "幼儿教师薪资 $85k~$105k（2026）", "url": "https://au.seek.com/career-advice/role/early-childhood-teacher/salary"},
    {"source_name": "Indeed AU", "content": "幼儿教师平均时薪 $40.58（约 $84,400/年，2026）", "url": "https://au.indeed.com/career/early-childhood-teacher/salaries"},
    {"source_name": "Australian Government", "content": "幼儿教育薪资和政策信息", "url": "https://www.education.gov.au/early-childhood/providers/workforce/wages"},
    {"source_name": "AITSL", "content": "海外幼儿教师资格认证", "url": "https://www.aitsl.edu.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲幼儿教师工资多少？", "answer": "幼儿教师（ECT）约 $80,000~$105,000（SEEK $85k~$105k；Indeed均值约 $84,400）；主任幼儿教师约 $95k~$125k；园长约 $110k~$150k。整体低于中小学教师，但政府持续推动薪资改革。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲幼儿教师容易找工作吗？", "answer": "极容易。持证ECT（Early Childhood Teacher）在全澳极度短缺，各机构主动争抢。政府强制要求每家幼教机构配置合格ECT创造了结构性需求缺口。SEEK 挂牌约 2,000~5,000 个职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国学前教育学历澳洲认可吗？", "answer": "通过AITSL海外教师资格评估，中国师范院校学前教育专业（4年本科）通常可以通过评估。主要挑战是英语能力（IELTS 7.5 各单项），以及澳洲儿童保护法规和文化理解的补充学习。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "幼儿教师会被AI替代吗？", "answer": "不会。幼儿教育中儿童情感安全感建立、发展性互动和游戏式学习的引导是AI无法替代的核心价值。0~5岁儿童需要人际关系和情感依附，这是任何技术工具都无法提供的。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲幼儿教师有年龄限制吗？", "answer": "无。有丰富幼教经验的中年教师（35~50岁）在担任教育主任（Educational Leader）和园长职位上具有显著优势。经验和成熟度在幼教领域比年龄更重要。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲幼儿教师需要什么学历？", "answer": "必须持有大学本科教育学位（Early Childhood方向），或相关学位+Graduate Diploma。仅持有Certificate III/Diploma的幼教工作者不具备ECT资质，需要进一步升学才能担任ECT职位。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲幼儿教师认证（移民）难吗？", "answer": "难度较低（主要门槛是英语）。AITSL评估路径清晰，英语达到IELTS 7.5后流程顺畅。各州教育主管部门对海外幼儿教师非常欢迎，偏远地区491路径更容易。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "幼儿教师和中小学教师哪个更适合移民澳洲？", "answer": "两者都是MLTSSL短缺职业，移民路径相同。中小学教师薪资略高（$95k~$115k vs ECT $80k~$105k）；幼儿教师职位数量更多，门槛相对略低。有幼教背景者选ECT，有中学学科背景（特别是数学/科学）者强烈推荐中学教师路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 幼儿教育工作者数据入库完成")

if __name__ == "__main__":
    run()
