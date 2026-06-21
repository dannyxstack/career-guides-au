"""澳洲企业培训师/培训经理（223211）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "223211", "anzsco_title": "Training and Development Manager",
    "category": "商业/金融/法律", "workforce_size": 42000, "shortage_listed": 1,
    "growth_areas": json.dumps(["AI & Digital Skills Upskilling","Leadership Development & Coaching","Learning Experience Design (LXD)","Compliance & Regulatory Training","Onboarding & Retention Programs"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "企业培训师 / 培训经理",
    "summary": "企业培训师和培训经理设计、开发和实施员工学习发展项目，覆盖技能提升、领导力发展、合规培训和新员工入职。澳洲企业AI转型和数字技能短缺推动对企业培训专业人士的需求持续增加，是HR领域薪资较有竞争力的专精方向。",
    "forecast_note": "JSA预测培训与发展经理至2035年就业增长约10%。AI工具培训（Copilot/ChatGPT企业应用）和数字技能再培训是2025-2030年增长最快的企业培训方向。",
    "trend_summary": "AI技能提升培训（AI Upskilling）是2025年澳洲企业培训增长最快的方向，各大企业和政府机构需要专职培训师设计AI工具应用课程。学习体验设计（LXD）和数字化学习（e-learning/LMS）专精培训师薪资溢价显著。",
}
I18N_EN = {
    "locale": "en", "name": "Corporate Trainer / Training and Development Manager",
    "summary": "Corporate trainers and training managers design, develop and deliver employee learning and development programs covering skills upskilling, leadership development, compliance training and onboarding. Enterprise AI transformation and digital skills gaps drive growing demand for L&D professionals, making it a competitive specialisation within HR.",
    "forecast_note": "JSA projects ~10% employment growth for training and development managers by 2035. AI tool training (Copilot/ChatGPT enterprise applications) and digital skills reskilling are the fastest-growing corporate training directions in 2025-2030.",
    "trend_summary": "AI skills upskilling is the fastest-growing corporate training direction in Australia in 2025. L&D specialists in learning experience design (LXD) and digital learning (e-learning/LMS) command significant salary premiums.",
}
EDUCATION = [
    {"stage": "Bachelor of HR / Education / Business（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 155000, "cost_note": "HR/教育/商科相关学位均可；教学设计背景有优势", "sort_order": 0},
    {"stage": "Certificate IV in Training & Assessment（TAE40122）", "duration": "3~6个月", "cost_min": 1500, "cost_max": 4000, "cost_note": "澳洲企业培训师从业基础资格；是在RTO机构任教的法律要求", "sort_order": 1},
    {"stage": "VETASSESS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 600, "cost_max": 2000, "cost_note": "技术移民必须，约 $650 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate IV in Training & Assessment（TAE40122）", "issuer": "ASQA认可RTO", "note": "澳洲企业培训师基础资格，在RTO任教必须持有", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "AHRI CPHR（含L&D专业方向）", "issuer": "AHRI（Australian HR Institute）", "note": "涵盖L&D专业方向的HR综合认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPLP（Certified Professional in Learning and Performance）", "issuer": "ATD（美国培训与发展协会）", "note": "国际L&D专业认证，在澳洲有认可度", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "VETASSESS 技能评估", "issuer": "VETASSESS", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1000, "count_max": 3000, "note": "全国，含培训经理、L&D专员、教学设计师和RTO培训师岗"},
    {"platform": "Indeed",   "count_min": 800, "count_max": 2500, "note": "含政府、医疗、金融和大型企业L&D岗"},
    {"platform": "LinkedIn", "count_min": 1500, "count_max": 4000, "note": "企业L&D团队直招，咨询公司培训顾问岗"},
]
SALARIES = [
    {"experience": "培训专员 / 教学设计师（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "L&D入门岗，含培训协调员", "sort_order": 0},
    {"experience": "企业培训师 / L&D经理（3~8年）", "salary_min": 85000, "salary_max": 120000, "salary_note": "SEEK 区间 $100k~$120k；Indeed 企业培训师均值 $103,005（2026）", "sort_order": 1},
    {"experience": "高级L&D经理 / 培训总监（8~15年）", "salary_min": 120000, "salary_max": 180000, "salary_note": "大型企业L&D总监，含AI专项培训和领导力发展", "sort_order": 2},
    {"experience": "CLO（Chief Learning Officer，15年+）", "salary_min": 180000, "salary_max": 350000, "salary_note": "大型企业首席学习官，含股权激励", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，培训经理为短缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，VETASSESS评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，各州均有通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要成人学习理论+教学设计能力+促动技巧，综合素质要求高"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "3年学位+TAE Cert IV约3~6个月；总周期约3~4年"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "TAE Cert IV难度较低；CPLP国际认证需要系统备考"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "MLTSSL短缺职业，AI工具培训和数字技能再培训推动持续需求"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级L&D岗竞争较激烈，具备AI培训设计和LXD能力的高级培训师供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "总体工作节奏合理，项目交付截止期有压力"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "企业培训师/L&D经理 $85k~$120k；培训总监 $120k~$180k"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "AI技能提升培训是10年以上的增长方向；企业数字化转型对L&D需求持续上升"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "标准课程内容被AI工具部分替代，但定制化培训设计和促动技能不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，VETASSESS评估路径清晰，雇主担保482活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "VETASSESS评估对HR/教育学历友好；EOI分数对有经验者友好"},
]
SUITABILITY_FIT = ["持有HR/教育/商科相关学位，有3年以上企业培训或L&D工作经验", "熟悉成人学习理论（ADDIE/Kirkpatrick）和LMS系统（Moodle/Cornerstone/SAP SuccessFactors Learning）", "英语能力达到 IELTS 7.0+（促动和演讲能力要求高）", "有AI技能培训设计、数字化学习（e-learning）或领导力发展项目经验（溢价最高）", "目标是大型企业或政府的L&D经理/培训总监岗位"]
SUITABILITY_UNFIT = ["英语口语能力较弱，无法主导课堂促动和演讲", "无成人学习理论基础，仅有课程内容专业知识", "不适应需要大量人际互动和演示展示的工作环境"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "培训经理薪资 $100k~$120k（2026）", "url": "https://au.seek.com/career-advice/role/training-manager/salary"},
    {"source_name": "Indeed AU", "content": "企业培训师平均薪资 $103,005（2026）", "url": "https://au.indeed.com/career/corporate-trainer/salaries"},
    {"source_name": "AHRI", "content": "L&D专业信息和CPHR认证", "url": "https://www.ahri.com.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲企业培训师工资多少？", "answer": "企业培训师/L&D经理约 $85,000~$120,000（Indeed均值 $103,005；SEEK $100k~$120k）；高级培训总监约 $120k~$180k；首席学习官（CLO）约 $180k~$350k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲企业培训师容易找工作吗？", "answer": "容易。Seek 挂牌约 1,000~3,000 个职位，MLTSSL短缺职业。AI技能培训设计和数字化学习专精的L&D经理目前供不应求，各大企业和政府机构积极招聘。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国企业培训经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国大型企业L&D/培训管理经验可以认可。建议强调可量化的培训成果（员工技能提升率、培训覆盖人数、ROI评估），以及对数字化培训工具的熟悉程度。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "企业培训师会被AI替代吗？", "answer": "部分替代。AI工具可以自动生成标准培训内容（微课/知识库），但个性化培训需求分析、促动技能、高级领导力发展和AI技能培训设计（讽刺性地成为最需要人工的方向）不可替代。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲企业培训师有年龄限制吗？", "answer": "无。资深L&D总监和首席学习官（40~55岁）在大型企业和政府中备受重视，特别是有组织变革管理和领导力培养经验者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲企业培训师需要什么学历？", "answer": "HR/教育/商科相关本科学历是VETASSESS评估基础。TAE Certificate IV是在RTO机构任教的法律要求（3~6个月即可完成）。CPLP国际认证可弥补学历差异。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲企业培训师认证（移民）难吗？", "answer": "难度中等偏低。TAE Cert IV难度较低（3~6个月），VETASSESS评估路径清晰。主要挑战是英语演讲能力（促动技能要求高）。雇主担保482是快速路径。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "企业培训师和人力资源经理哪个更适合移民澳洲？", "answer": "两者均为MLTSSL短缺职业；HR经理薪资略高（$102k~$135k vs L&D $85k~$120k），覆盖更广；L&D专精在AI技能培训方向有独特增长机会。有培训/教学设计背景者选L&D，有综合HR管理经验者选HR经理。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 企业培训师/培训经理数据入库完成")

if __name__ == "__main__":
    run()
