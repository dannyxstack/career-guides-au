"""网页开发 (261212) Web Developer — AU 2025-2026
技术移民职业（is_migration=1），ANZSCO 261212。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from db.connection import get_cursor
from _seed_helper import seed_occupation_v2
from pipeline.generators.md_generator import generate_md

OCC = {
    "occ_code": "261212", "anzsco_code": "261212", "anzsco_title": "Web Developer",
    "category": "IT & Digital", "workforce_size": 28000,
    "shortage_listed": 1, "is_migration": 1,
    "growth_areas": json.dumps(["React / Next.js Front-end", "Headless CMS & JAMstack",
                                "E-commerce (Shopify/Magento)", "Web Performance & Accessibility",
                                "Full-stack / Node.js"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "网页开发",
    "summary": "网页开发负责设计、构建和维护网站与 Web 应用，涵盖前端界面、后端逻辑与性能优化。澳洲各行业数字化对 Web 技能需求稳定，且属于 IT 技术移民职业，是较友好的入行与移民方向之一。",
    "forecast_note": "澳洲企业持续投入数字渠道，前端框架（React/Vue）、全栈和电商方向需求旺盛；初级岗位竞争加剧，具备全栈、云部署和无障碍/性能经验者更抢手。",
    "trend_summary": "React/Next.js 是主流前端栈，Node.js 全栈与 headless CMS 增长明显。职业路径可向全栈工程师、前端架构师或软件工程师延伸。技术移民需通过 ACS 技能评估。"}
I18N_EN = {"locale": "en", "name": "Web Developer",
    "summary": "Web developers design, build and maintain websites and web applications, spanning front-end UI, back-end logic and performance. Demand across Australian industries is steady, and the role is on skilled migration pathways, making it an accessible entry and migration option.",
    "forecast_note": "Australian firms keep investing in digital channels; front-end frameworks, full-stack and e-commerce skills are in demand. Entry-level competition is rising, while full-stack, cloud and accessibility/performance experience stands out.",
    "trend_summary": "React/Next.js dominate the front-end; Node.js full-stack and headless CMS are growing. Career paths extend to full-stack engineer, front-end architect or software engineer. Skilled migration requires ACS assessment."}
EDUCATION = [
    {"stage": "Bachelor of IT / Computer Science", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "Diploma of IT / Web Development", "duration": "1~2年", "cost_min": 8000, "cost_max": 20000, "cost_note": "TAFE 路径", "sort_order": 1},
    {"stage": "Coding Bootcamp / 自学作品集", "duration": "3~9个月", "cost_min": 0, "cost_max": 15000, "cost_note": "需作品集支撑", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of IT / Computer Science", "issuer": "认可大学", "note": "技术移民 ACS 评估首选", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "ACS Skills Assessment", "issuer": "Australian Computer Society", "note": "技术移民必备", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "AWS / Azure 云认证（可选）", "issuer": "Amazon / Microsoft", "note": "全栈/部署加分", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 1200, "count_max": 2200, "note": "全国，含全栈/前端"},
    {"platform": "Indeed", "count_min": 900, "count_max": 1600, "note": "全国"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 1800, "note": "偏企业直招"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 65000, "salary_max": 82000, "salary_note": "Junior/Front-end Dev", "sort_order": 0},
    {"experience": "中级（3-7年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "Mid / Full-stack", "sort_order": 1},
    {"experience": "高级（7年+）", "salary_min": 115000, "salary_max": 145000, "salary_note": "Senior / Lead", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "Skills in Demand", "description": "雇主担保（旧称TSS），按职责匹配ANZSCO", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，需ACS评估", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，按各州清单", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "前端易入门，全栈较深"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位或作品集约1~3年"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "靠作品集而非考证"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 4, "note": "全行业数字化需求"},
    {"dimension": "competition",              "label_zh": "中高", "stars": 4, "note": "初级岗位竞争激烈"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "项目期偏忙"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 3, "note": "AUD 8.5万~14.5万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 4, "note": "可转全栈/软件工程"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI辅助编码但需架构判断"},
    {"dimension": "pr_friendliness",          "label_zh": "高", "stars": 4, "note": "IT技术移民通道顺畅"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需ACS评估+邀请分"},
]
SUITABILITY_FIT = ["喜欢做产品界面与交互的人", "自学能力强、能积累作品集者", "希望走IT技术移民通道的转行者"]
SUITABILITY_UNFIT = ["不愿持续学习新框架者", "偏好稳定流程化工作的人", "排斥与设计/产品频繁沟通者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 261212 Web Developers 数据", "url": "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/261212-web-developers"},
    {"source_name": "Seek AU", "content": "薪资与岗位量", "url": "https://www.seek.com.au/web-developer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲网页开发工资多少？", "answer": "初级约AUD $6.5万~$8.2万，中级全栈$8.5万~$11.5万，高级$11.5万~$14.5万，云和全栈技能有溢价。"},
    {"faq_type": "migration", "sort_order": 1, "question": "网页开发能技术移民吗？", "answer": "可以。Web Developer（261212）是IT技术移民职业，可走482 Skills in Demand雇主担保、186永居、190州提名，需通过ACS技能评估，并按具体职责匹配ANZSCO。"},
    {"faq_type": "demand", "sort_order": 2, "question": "澳洲网页开发好找工作吗？", "answer": "需求稳定，Seek常年有1200~2200个职位，但初级竞争激烈，有作品集和全栈经验更易就业。"},
]
def run():
    with get_cursor() as cur:
        seed_occupation_v2(cur, OCC, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS,
                           JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS,
                           SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    path = generate_md(OCC["anzsco_code"])
    print(f"[markdown] {path}")
    print("[OK] 网页开发入库完成")
if __name__ == "__main__":
    run()
