"""澳洲网页设计师（232413）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "232413", "anzsco_title": "Web Designer",
    "category": "创意/媒体", "workforce_size": 28000, "shortage_listed": 0,
    "growth_areas": json.dumps(["UI/UX设计（移动应用和网页产品）","电商网站设计（Shopify/WooCommerce）","无障碍网页设计（WCAG合规）","网页动效与交互设计","设计系统（Design System）构建"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "网页设计师",
    "summary": "网页设计师专注于网站和数字产品的视觉设计、用户体验和交互原型，是数字产品团队的核心成员之一。电商爆发（澳洲$650亿+电商市场）和企业数字化推动对网页设计师的持续需求。掌握Figma+基础前端（HTML/CSS）+UX研究技能的全栈设计师竞争力最强，薪资可对标UI/UX设计师。",
    "forecast_note": "JSA预测网页设计师就业至2030年保持稳定至略微增长。向UI/UX设计方向深耕（产品设计师）的从业者需求增长最快，纯视觉网页设计方向有一定AI冲击。",
    "trend_summary": "澳洲企业网站和电商平台持续升级，推动对网页设计师的稳定需求。Figma成为网页和产品设计的绝对行业标准。AI设计工具（Wix ADI/Framer AI）影响低端网站模板设计，但定制化品牌网站和复杂UX项目仍需专业设计师。无障碍设计（WCAG 2.1合规）成为政府和大型企业的强制要求。",
}
I18N_EN = {
    "locale": "en", "name": "Web Designer",
    "summary": "Web designers focus on the visual design, user experience and interactive prototypes of websites and digital products, serving as core members of digital product teams. The e-commerce boom (Australia's $65B+ e-commerce market) and corporate digitalisation drive sustained demand for web designers. Full-stack designers with Figma + basic front-end (HTML/CSS) + UX research skills have the strongest competitiveness, with salaries matching UI/UX designers.",
    "forecast_note": "JSA projects stable to slightly growing web designer employment through 2030. Practitioners deepening into UI/UX design (product designers) have the fastest-growing demand, while pure visual web design faces some AI disruption.",
    "trend_summary": "Australian corporate websites and e-commerce platforms continue upgrading, driving stable demand for web designers. Figma has become the absolute industry standard for web and product design. AI design tools (Wix ADI/Framer AI) are affecting low-end website template design, but customised brand websites and complex UX projects still require professional designers. Accessible design (WCAG 2.1 compliance) has become mandatory for government and large enterprises.",
}
EDUCATION = [
    {"stage": "Bachelor of Design（Web/Interactive）或 IT/Computing（3年）", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 110000, "cost_note": "国际生约 $25,000~$35,000/年", "sort_order": 0},
    {"stage": "Diploma of Web Design / UX Design（TAFE/私立，1~2年）", "duration": "1~2年", "cost_min": 5000, "cost_max": 25000, "cost_note": "实践型文凭，专注Figma/Adobe XD和前端基础技能", "sort_order": 1},
    {"stage": "Figma Professional 技能认证 + UX Design专项课程", "duration": "3~9个月", "cost_min": 300, "cost_max": 3000, "cost_note": "Google UX Design Certificate（Coursera，约$300）是热门认证", "sort_order": 2},
    {"stage": "基础前端技能（HTML/CSS/JavaScript基础）", "duration": "3~6个月自主学习", "cost_min": 0, "cost_max": 1000, "cost_note": "设计师有前端基础是强竞争优势", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Google UX Design Certificate", "issuer": "Google / Coursera", "note": "谷歌官方UX设计认证，全球认可，入门友好", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Figma 熟练掌握", "issuer": "行业事实标准", "note": "2025年网页/产品设计行业的绝对工具标准", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "WCAG 2.1 无障碍设计认证", "issuer": "IAAP", "note": "政府和大型企业项目的强制要求，溢价技能", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 500, "count_max": 1500, "note": "全国，含网页设计/数字设计/UI设计岗"},
    {"platform": "Indeed",   "count_min": 400, "count_max": 1200, "note": "含电商设计师和数字代理公司岗"},
    {"platform": "LinkedIn", "count_min": 800, "count_max": 2500, "note": "企业数字产品团队和代理公司设计师岗活跃"},
]
SALARIES = [
    {"experience": "初级网页设计师（0~2年）", "salary_min": 52000, "salary_max": 68000, "salary_note": "毕业设计师起薪", "sort_order": 0},
    {"experience": "中级网页设计师（2~6年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "SEEK 区间 $80k~$85k；Indeed 均值 $79,491；数字设计师 SEEK $90k~$110k（2026）", "sort_order": 1},
    {"experience": "高级网页/UI/UX设计师（6~12年）", "salary_min": 90000, "salary_max": 125000, "salary_note": "Indeed 数字设计师均值 $88,417；资深UX设计师可达 $110k~$125k", "sort_order": 2},
    {"experience": "设计主管 / 产品设计总监（12年+）", "salary_min": 125000, "salary_max": 200000, "salary_note": "科技公司设计总监或大型电商平台设计主管", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，科技公司和数字代理公司可担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要VETASSESS技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "设计美学+UX方法论+Figma工具+基础前端的综合技能要求"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3年；文凭/专项课程1~2年；自学路径约1~2年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "VETASSESS评估；作品集（Portfolio）质量是关键"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "电商和企业数字化推动稳定需求；向UI/UX转型者供不应求"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "纯网页设计竞争激烈；有UX研究和前端基础的设计师需求旺盛"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "项目截止期前强度高；数字代理公司多项目并行"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级 $70k~$90k；向UI/UX深耕后 $90k~$125k；设计总监 $125k+"},
    {"dimension": "future_prospect",          "label_zh": "中高", "stars": 4, "note": "电商和产品数字化持续增长，向产品设计师转型前景明朗"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI工具影响低端模板网站设计，但定制品牌网站和复杂UX不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL，雇主担保482可行（科技公司担保活跃）"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "非短缺职业，189邀请分数要求高；雇主担保是更可行路径"},
]
SUITABILITY_FIT = ["持有设计类学历，有高质量网页/UI/UX设计作品集", "熟练掌握Figma（行业标准工具），有UX研究方法基础", "有电商平台（Shopify/Magento）或SaaS产品设计经验", "有基础前端技能（HTML/CSS），可以与开发团队高效协作", "有意向在科技公司或数字代理公司的产品设计团队发展"]
SUITABILITY_UNFIT = ["仅掌握Photoshop/Illustrator，未学习Figma（行业已转移）", "没有UX研究基础（用户访谈/可用性测试），仅注重视觉美学", "期望纯靠网页设计技能快速获得技术移民（非短缺职业，需要雇主担保）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "网页设计师薪资 $80k~$85k；数字设计师 $90k~$110k（2026）", "url": "https://au.seek.com/career-advice/role/webdesigner/salary"},
    {"source_name": "Indeed AU", "content": "网页设计师平均薪资 $79,491；数字设计师 $88,417（2026）", "url": "https://au.indeed.com/career/web-designer/salaries"},
    {"source_name": "PayScale AU", "content": "网页设计师时薪（2026）", "url": "https://www.payscale.com/research/AU/Job=Web_Designer/Salary"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲网页设计师工资多少？", "answer": "中级网页设计师约 $70,000~$90,000（SEEK $80k~$85k；Indeed $79,491）；数字设计师 SEEK $90k~$110k（Indeed $88,417）；高级UX/产品设计师约 $90k~$125k；设计总监约 $125k~$200k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲网页设计师容易找工作吗？", "answer": "有一定需求，SEEK 挂牌约500~1,500个职位。纯网页设计竞争较激烈；有UI/UX融合技能的数字设计师需求稳定旺盛。建议向产品设计师（Product Designer）方向发展，大幅提升竞争力和薪资。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国网页设计经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，有商业网页设计项目经验者可以认可。关键是准备高质量的英语作品集，展示用户体验设计过程（用户研究→原型设计→最终交付），而不只是视觉截图。Figma原型是最被认可的展示格式。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "网页设计师会被AI替代吗？", "answer": "AI工具（Wix ADI、Framer AI）已能自动生成低端模板网站；但定制品牌网站设计、复杂UX流程优化和电商转化率设计仍需专业设计师。向产品设计、UX研究和设计系统方向深耕可有效规避AI风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲网页设计师有年龄限制吗？", "answer": "无。有丰富商业项目经验和客户资源的资深设计师（40~55岁）在设计顾问和设计主管岗位具有优势。关键是保持工具技能更新（跟上Figma、AI设计工具的发展）。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲网页设计师需要什么学历？", "answer": "大型科技公司和代理机构偏好设计类本科学历；中小型企业更注重作品集和Figma技能。Google UX Design Certificate（Coursera）是被广泛认可的补充证书。TAFE文凭+强作品集可以进入大多数中小型公司。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲网页设计师认证（移民）难吗？", "answer": "不在MLTSSL，移民难度中等偏高。雇主担保482是可行路径，科技公司和数字代理公司有担保能力。建议向UI/UX/产品设计方向发展，部分州将产品设计师纳入科技人才需求范围。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "网页设计师和前端开发者哪个澳洲发展更好？", "answer": "前端开发者薪资更高（$95k~$130k vs 网页设计师 $70k~$90k），移民路径更清晰（IT类职业，MLTSSL部分在列）；网页设计师技能转换门槛更低（不需要编程）。有编程基础者强烈推荐往全栈开发方向发展；纯设计背景者建议向UI/UX产品设计师转型，不必强求前端开发。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 网页设计师数据入库完成")

if __name__ == "__main__":
    run()
