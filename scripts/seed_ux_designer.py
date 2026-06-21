"""澳洲UI/UX设计师（232412）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "232412", "anzsco_title": "Web Designer",
    "category": "IT/工程", "workforce_size": 48000, "shortage_listed": 0,
    "growth_areas": json.dumps(["AI-Augmented UX Design","Product Design for SaaS & Fintech","Accessibility & Inclusive Design","Design Systems & Tokens","UX Research & Behavioural Analytics"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "UI/UX设计师",
    "summary": "UI/UX设计师创造用户界面和交互体验，覆盖Web、移动App、SaaS产品和政府数字服务。澳洲科技产业（Atlassian/Canva/WiseTech）对产品设计师的需求持续旺盛，Canva等公司将设计驱动的产品理念推向全球，是最适合创意型技术人才的职业之一。",
    "forecast_note": "JSA 预测网页和数字设计师至2035年就业增长约15%。AI设计工具（Figma AI/Adobe Firefly）提高生产率，但策略性设计思维和用户研究的价值反而提升。",
    "trend_summary": "Figma已成为澳洲UI/UX设计工具的绝对标准。Design Tokens和设计系统（Design System）管理是2025-2026年薪资溢价最高的细分技能。AI生成式设计加速了产品迭代，但提升了对高级设计师的需求。",
}
I18N_EN = {
    "locale": "en", "name": "UI/UX Designer",
    "summary": "UI/UX designers create user interfaces and interaction experiences for web, mobile, SaaS products and government digital services. Strong demand from Australia's tech sector (Atlassian/Canva/WiseTech). Canva has elevated design-driven product thinking globally.",
    "forecast_note": "JSA projects ~15% employment growth for web and digital designers by 2035. AI design tools (Figma AI/Adobe Firefly) raise productivity while increasing demand for senior designers with strategic thinking.",
    "trend_summary": "Figma is the absolute standard in Australian UI/UX tooling. Design Systems management is the highest-premium niche skill in 2025-2026. Generative AI accelerates prototyping but increases demand for senior designers.",
}
EDUCATION = [
    {"stage": "Bachelor of Design (Interaction/UX) / Computer Science（3~4年）", "duration": "3~4年（全日制）", "cost_min": 25000, "cost_max": 160000, "cost_note": "或相关学位+自学UX设计课程；作品集（Portfolio）的权重高于学位", "sort_order": 0},
    {"stage": "Google UX Design Certificate / Nielsen Norman UX Certification", "duration": "3~12个月", "cost_min": 500, "cost_max": 3000, "cost_note": "Google UX Certificate（Coursera，约 $50/月）是转行路径的入门认证", "sort_order": 1},
    {"stage": "ACS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民必须，232412按Web Designer类别评估", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Design (Interaction/Digital)", "issuer": "认可大学", "note": "UX岗位最直接相关的学历，ACS评估认可", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Google UX Design Certificate", "issuer": "Google / Coursera", "note": "广泛认可的UX入门认证，适合转行者", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Nielsen Norman Group UX Certification", "issuer": "Nielsen Norman Group", "note": "业界最权威的UX研究和设计认证，高级岗位的强烈推荐", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "ACS 技能评估", "issuer": "Australian Computer Society", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 800,  "count_max": 2000, "note": "全国，含UX设计师、产品设计师、UI工程师和设计研究员岗"},
    {"platform": "Indeed",   "count_min": 600,  "count_max": 1500, "note": "含合同工和远程设计岗"},
    {"platform": "LinkedIn", "count_min": 1200, "count_max": 3000, "note": "科技公司直招，产品设计岗比例高"},
]
SALARIES = [
    {"experience": "初级UX/UI设计师（0~2年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "含毕业生和转行者，悉尼/墨尔本科技公司高于均值", "sort_order": 0},
    {"experience": "中级UX/UI设计师（2~5年）", "salary_min": 85000, "salary_max": 120000, "salary_note": "SEEK UX区间 $100k~$120k；Indeed 平均 $103,812（2026）", "sort_order": 1},
    {"experience": "高级/产品设计师（5~10年）", "salary_min": 120000, "salary_max": 160000, "salary_note": "含设计系统负责人和设计Lead", "sort_order": 2},
    {"experience": "设计总监 / Head of Design（10年+）", "salary_min": 160000, "salary_max": 250000, "salary_note": "Canva/Atlassian等顶尖公司设计总监薪资可超 $200k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，科技公司UX岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，ACS技能评估+EOI", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NSW/VIC科技通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要设计思维和用户研究方法，Figma等工具相对易学"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3~4年；作品集路径自学6~18个月可入职初级岗"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "UX认证难度低，作品集质量远比认证重要"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "科技行业高需求，但职位总量少于开发岗位"},
    {"dimension": "competition",              "label_zh": "中高", "stars": 4, "note": "初级岗竞争激烈，顶级产品设计师极度稀缺"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "产品发布前强度高，日常工作节奏相对灵活"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位数约 $100k~$120k，顶级科技公司设计总监可超 $200k"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "AI工具加速设计，但策略性设计思维和用户研究价值反而提升"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "UI资产生成部分受AI冲击，但UX研究、设计策略和设计系统管理不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "STOL列表，189/190可申请，但职位数少于开发岗位"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "ACS评估对设计类学历认可较窄，建议用CS/IT相关学历评估"},
]
SUITABILITY_FIT = ["有Figma/Sketch/Adobe XD实际项目经验（2年以上）", "有强设计作品集（Portfolio），能展示设计思维和用户研究过程", "有用户研究（User Research）和可用性测试经验", "英语能力达到 IELTS 6.5+（设计汇报和跨团队沟通要求）", "目标是悉尼/墨尔本科技公司（Atlassian/Canva生态）"]
SUITABILITY_UNFIT = ["没有设计作品集（Portfolio），无法展示实际设计项目", "英语沟通能力较弱，无法进行设计评审和用户访谈", "对用户体验研究不感兴趣，仅关注视觉美观"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "UX设计师薪资 $100k~$120k（2026）", "url": "https://au.seek.com/career-advice/role/ux-designer/salary"},
    {"source_name": "Indeed AU", "content": "UI/UX设计师平均薪资 $103,812（2026）", "url": "https://au.indeed.com/career/ux-designer/salaries"},
    {"source_name": "ACS", "content": "技能评估机构", "url": "https://www.acs.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲UI/UX设计师工资多少？", "answer": "中级UX设计师约 $85,000~$120,000（Indeed均值 $103,812）；高级产品设计师约 $120k~$160k；Canva/Atlassian设计总监可超 $200k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲UX设计师容易找工作吗？", "answer": "中等难度。Seek 挂牌约 800~2000 个职位，初级岗竞争较激烈，需要强作品集；有设计系统经验的高级产品设计师极为稀缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国UX设计经验澳洲认可吗？", "answer": "通过 ACS 技能评估（建议用CS/数字设计相关学历评估），设计作品集（Portfolio）是最重要的能力证明。重要的是作品集中需包含英文的设计思维过程说明。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "UX设计师会被AI替代吗？", "answer": "UI资产生成（图标/配色/基础布局）受AI工具冲击，但用户研究、设计策略、设计系统架构和与PM/工程师的协作不可替代。AI反而让设计师能做更多战略性工作。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲UX设计师有年龄限制吗？", "answer": "无。具有深厚行业领域知识的设计师（如医疗UX、金融UX）在40岁以上仍然极具价值。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲UX设计师需要什么学历？", "answer": "设计/CS相关学位是主流，但强作品集+Google UX Certificate的转行者也有入职机会。ACS技能评估对设计学历的认可范围相对较窄，建议咨询ACS具体情况。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲UX设计师认证（移民）难吗？", "answer": "难度中等。ACS评估对非IT学历设计师较严格；作品集质量是关键；职位数量少于开发岗位，雇主担保482可能更快。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "UX设计师和软件工程师哪个更适合移民澳洲？", "answer": "软件工程师移民路径更清晰（职位数多约5~10倍，ACS评估更简单）；UX设计师竞争压力较小（供需比更好），但职位总量少。有设计背景者选UX，有技术背景者选软件工程师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] UI/UX设计师数据入库完成")

if __name__ == "__main__":
    run()
