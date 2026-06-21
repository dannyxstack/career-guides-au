"""澳洲营销经理（131112）数据入库。数据来源：JSA、SEEK、Indeed、Robert Half（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "131112", "anzsco_title": "Marketing Manager",
    "category": "创意/媒体", "workforce_size": 75000, "shortage_listed": 0,
    "growth_areas": json.dumps(["数字营销（SEO/SEM/社交媒体营销）","内容营销与品牌故事","数据驱动营销（Marketing Analytics）","电商营销（D2C品牌）","AI营销工具应用与自动化"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "营销经理",
    "summary": "营销经理负责制定和执行品牌营销策略，管理营销团队，协调广告、公关、数字营销和内容创作活动，推动业务增长。澳洲数字营销市场（$130亿+）的持续扩张和企业品牌竞争加剧推动对营销管理人才的旺盛需求。有数字营销数据分析能力的营销经理薪资溢价显著。",
    "forecast_note": "JSA预测营销经理就业至2030年增长约8%。数字营销和数据驱动营销方向增长最快，传统媒体广告管理方向市场收缩。有AI营销工具和分析平台操作能力的营销经理需求量大。",
    "trend_summary": "澳洲企业数字化转型推动营销预算大幅向数字渠道倾斜。数据驱动营销（Google Analytics/HubSpot/Salesforce Marketing Cloud）成为行业标配。AI营销工具（ChatGPT内容生成、自动化广告优化）正在重塑营销团队工作方式，但营销策略制定和品牌创意仍需人类营销经理。",
}
I18N_EN = {
    "locale": "en", "name": "Marketing Manager",
    "summary": "Marketing managers develop and execute brand marketing strategies, manage marketing teams and coordinate advertising, PR, digital marketing and content creation activities to drive business growth. The sustained expansion of Australia's digital marketing market ($13B+) and intensifying corporate brand competition drive strong demand for marketing talent. Marketing managers with digital marketing and data analytics skills command significant salary premiums.",
    "forecast_note": "JSA projects ~8% marketing manager employment growth by 2030. Digital and data-driven marketing are growing fastest while traditional media advertising management is contracting. Marketing managers with AI marketing tools and analytics platform skills are in high demand.",
    "trend_summary": "Australian corporate digital transformation is driving major marketing budget shifts towards digital channels. Data-driven marketing (Google Analytics/HubSpot/Salesforce Marketing Cloud) has become the industry standard. AI marketing tools (ChatGPT content generation, automated ad optimisation) are reshaping marketing team workflows, but marketing strategy formulation and brand creativity still require human marketing managers.",
}
EDUCATION = [
    {"stage": "Bachelor of Marketing / Business（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 130000, "cost_note": "或 MBA（已有工作经验者）；国际生约 $28,000~$38,000/年", "sort_order": 0},
    {"stage": "Master of Marketing / MBA", "duration": "1~2年", "cost_min": 30000, "cost_max": 80000, "cost_note": "提升至管理层的进阶路径", "sort_order": 1},
    {"stage": "数字营销认证（Google Analytics/HubSpot/Meta）", "duration": "1~6个月", "cost_min": 0, "cost_max": 2000, "cost_note": "Google Analytics（免费认证）、HubSpot Marketing Certification（免费）、Meta Blueprint等", "sort_order": 2},
    {"stage": "营销协会认证（AMI Certified Practicing Marketer）", "duration": "申请制", "cost_min": 500, "cost_max": 2000, "cost_note": "澳洲营销协会（AMI）CPM认证，提升职业信誉", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Google Analytics Certification", "issuer": "Google", "note": "数字营销经理的事实上必备技能认证", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "HubSpot Marketing Certification", "issuer": "HubSpot", "note": "入境营销（Inbound Marketing）行业标准认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "AMI Certified Practising Marketer (CPM)", "issuer": "Australian Marketing Institute", "note": "澳洲营销专业人员最高认证，提升管理层竞争力", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 2000, "count_max": 5000, "note": "全国，含数字营销经理/品牌经理/市场营销总监岗"},
    {"platform": "Indeed",   "count_min": 1500, "count_max": 4000, "note": "含企业内部营销团队和营销代理机构岗"},
    {"platform": "LinkedIn", "count_min": 3000, "count_max": 8000, "note": "企业营销总监和数字营销经理招聘活跃"},
]
SALARIES = [
    {"experience": "营销专员/协调员（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "数字营销专员起薪；Indeed 均值约 $82,989（2026）", "sort_order": 0},
    {"experience": "营销经理（3~8年）", "salary_min": 95000, "salary_max": 125000, "salary_note": "SEEK 区间 $105k~$125k；Indeed 均值 $101,395（2026）", "sort_order": 1},
    {"experience": "高级营销经理 / 品牌经理（8~15年）", "salary_min": 120000, "salary_max": 160000, "salary_note": "Robert Half 2026报告：资深营销经理约 $120k~$150k", "sort_order": 2},
    {"experience": "营销总监 / CMO（15年+）", "salary_min": 155000, "salary_max": 300000, "salary_note": "SEEK 营销总监均值 $170k~$190k；大型企业CMO薪资超 $250k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，企业和营销公司可担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要VETASSESS技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要商业策略+数字营销技能+数据分析+创意思维的综合能力"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "本科3年；进入管理层需要5~8年工作经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "VETASSESS评估；需要工作经验证明；数字营销认证加分"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "数字营销爆发推动稳定需求；数据驱动营销经理供不应求"},
    {"dimension": "competition",              "label_zh": "中高", "stars": 4, "note": "管理层职位竞争激烈；有数字营销数据技能者竞争优势明显"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "多项目并行、KPI压力；营销代理公司节奏快、加班较多"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "营销经理 $95k~$125k；总监 $155k~$300k；整体薪资高于大多数创意类职业"},
    {"dimension": "future_prospect",          "label_zh": "中高", "stars": 4, "note": "数字营销持续增长，有数据分析和AI营销工具能力的营销经理前景明朗"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI自动化内容生成和广告优化影响部分基础工作，但品牌策略制定不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL，但大量企业有担保能力；雇主担保482是主流路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "非短缺职业，189邀请分数要求高；雇主担保是更可行的路径"},
]
SUITABILITY_FIT = ["持有商业/营销学位，有5年以上营销管理工作经验", "掌握数字营销工具（Google Analytics/HubSpot/Salesforce/Meta Ads）", "有品牌策略和营销活动全案管理经验（从策划到执行到效果评估）", "英语书面和口头表达能力强（创意简报、高管汇报、代理公司协作）", "对澳洲市场有了解，或有意在澳洲企业/营销代理机构发展"]
SUITABILITY_UNFIT = ["仅有中国市场营销经验，对澳洲消费者行为和本地营销渠道不熟悉", "无数字营销技能（仅传统媒体广告经验）", "期望直接以营销经理职位入职（通常需要先从专员岗积累本地经验）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "营销经理薪资 $105k~$125k；营销总监 $170k~$190k（2026）", "url": "https://au.seek.com/career-advice/role/marketing-manager/salary"},
    {"source_name": "Indeed AU", "content": "营销经理平均薪资 $101,395（2026）", "url": "https://au.indeed.com/career/marketing-manager/salaries"},
    {"source_name": "Robert Half AU", "content": "澳洲营销薪资指南2026", "url": "https://www.roberthalf.com/au/en/insights/salary-guide/marketing"},
    {"source_name": "SEEK AU", "content": "广告经理薪资 $85k~$105k（2026）", "url": "https://au.seek.com/career-advice/role/advertising-manager/salary"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲营销经理工资多少？", "answer": "营销经理约 $95,000~$125,000（SEEK $105k~$125k；Indeed $101,395）；高级营销经理约 $120k~$160k；营销总监约 $155k~$300k（SEEK均值 $170k~$190k）。数字营销和数据分析技能可带来明显薪资溢价。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲营销经理容易找工作吗？", "answer": "有一定难度，管理层职位竞争较激烈。但有数字营销技能（SEO/SEM/社交媒体）的营销经理需求持续旺盛，SEEK 挂牌约 2,000~5,000 个职位。建议先在澳洲积累1~2年本地市场经验再竞争管理岗。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国营销经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国营销经验可以认可。关键挑战是澳洲市场和中国市场在渠道（微信/微博 vs LinkedIn/Instagram）和消费者行为上有较大差异，建议快速补充本地数字营销平台操作经验（Google Analytics、Meta Ads、LinkedIn Ads）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "营销经理会被AI替代吗？", "answer": "AI工具正在自动化内容生成、广告优化和营销数据分析等基础任务，但品牌战略制定、客户关系管理和创意策划仍需要人类营销经理。向营销策略、品牌管理和数据驱动营销方向深耕可有效规避AI风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲营销经理有年龄限制吗？", "answer": "无。有丰富品牌管理经验和行业人脉的资深营销总监（45~60岁）在大型企业非常有竞争力。营销是高度依赖经验和客户关系的职业，资历越深越有价值。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲营销经理需要什么学历？", "answer": "通常需要商业/营销相关本科学历。管理层和总监级岗位倾向于MBA或相关研究生学位持有者。但数字营销领域中，有Google/HubSpot/Meta认证+实际成绩证明有时比学历更重要。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲营销经理认证（移民）难吗？", "answer": "不在MLTSSL，移民难度中等偏高。雇主担保482是主流路径，大型企业有担保能力。建议先通过学生签证在澳就读商科/营销研究生课程，积累本地市场经验后申请雇主担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "营销经理和商业分析师哪个澳洲发展更好？", "answer": "商业分析师薪资略高（$110k~$130k vs 营销经理 $95k~$125k），技术门槛更高（SQL/BI工具）；营销经理就业范围更广（任何行业都需要营销），创意空间更大。有数据分析背景者选商业分析师；有创意和品牌管理倾向者选营销经理。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 营销经理数据入库完成")

if __name__ == "__main__":
    run()
