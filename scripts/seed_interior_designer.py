"""澳洲室内设计师（232511）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "232511", "anzsco_title": "Interior Designer",
    "category": "创意/媒体", "workforce_size": 20000, "shortage_listed": 0,
    "growth_areas": json.dumps(["住宅室内设计（建筑市场高峰后的翻新潮）","商业室内设计（后疫情办公空间重设计）","酒店和零售空间设计","可持续室内设计（绿色建筑）","虚拟室内设计咨询（远程服务）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "室内设计师",
    "summary": "室内设计师为住宅、商业和酒店空间规划功能布局和美学设计，协调建材、家具和照明采购与施工监管。澳洲建筑与装修市场持续活跃（大量新楼盘+老房翻新潮）推动对室内设计师的稳定需求。有3D可视化技能（SketchUp/Revit/3ds Max）和工程图纸能力的设计师竞争力更强。",
    "forecast_note": "JSA预测室内设计师就业至2030年基本稳定。商业空间重设计（COVID后办公室重整）和可持续绿色室内设计方向增长最快；建材和工程成本上涨影响新建项目数量。",
    "trend_summary": "澳洲住宅翻新市场（Renovation Market）持续火热，HomeBuilder补贴政策推高需求高峰后市场趋于正常化。商业室内设计（WeWork模式崩溃后企业自建高质量办公室）有新需求。虚拟室内设计咨询（Zoom/3D软件）让设计师服务范围超越本地市场。",
}
I18N_EN = {
    "locale": "en", "name": "Interior Designer",
    "summary": "Interior designers plan functional layouts and aesthetic design for residential, commercial and hospitality spaces, coordinating materials, furniture and lighting procurement and construction supervision. Australia's active construction and renovation market (high-volume new developments + old home renovation surge) drives stable demand for interior designers. Designers with 3D visualisation skills (SketchUp/Revit/3ds Max) and engineering drawing capability have stronger competitiveness.",
    "forecast_note": "JSA projects broadly stable interior designer employment through 2030. Commercial space redesign (post-COVID office reconfiguration) and sustainable green interior design are growing fastest; rising materials and construction costs are affecting new project volumes.",
    "trend_summary": "Australia's residential renovation market remains active following the HomeBuilder subsidy-driven peak, normalising gradually. Commercial interior design (businesses building high-quality offices after WeWork model collapse) is seeing new demand. Virtual interior design consulting (Zoom/3D software) is allowing designers to serve beyond local markets.",
}
EDUCATION = [
    {"stage": "Bachelor of Interior Design / Interior Architecture（3年）", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 110000, "cost_note": "澳洲主流资质路径；国际生约 $25,000~$35,000/年", "sort_order": 0},
    {"stage": "Diploma of Interior Design and Decoration（TAFE，1~2年）", "duration": "1~2年", "cost_min": 5000, "cost_max": 25000, "cost_note": "住宅装饰设计文凭，注重实操和材料知识", "sort_order": 1},
    {"stage": "3D设计软件技能（SketchUp/AutoCAD/Revit/3ds Max）", "duration": "3~12个月", "cost_min": 300, "cost_max": 3000, "cost_note": "商业室内设计公司的实际技能要求", "sort_order": 2},
    {"stage": "Decorex / Design Institute of Australia（DIA）认证", "duration": "申请制", "cost_min": 500, "cost_max": 2000, "cost_note": "澳洲室内设计师协会认证，提升专业信誉", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Design Institute of Australia (DIA) 会员", "issuer": "Design Institute of Australia", "note": "澳洲室内设计专业协会会员，提升专业信誉", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Interior Decoration Certificate（DIA认证）", "issuer": "DIA", "note": "住宅室内装饰设计的专业认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "建筑绘图技能（AutoCAD/Revit）", "issuer": "行业技能要求", "note": "商业室内设计项目的实际技能要求", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 300, "count_max": 800, "note": "全国，含室内设计师/家居设计顾问/空间设计师岗"},
    {"platform": "Indeed",   "count_min": 200, "count_max": 600, "note": "含设计公司、建材零售和家具品牌岗"},
    {"platform": "LinkedIn", "count_min": 300, "count_max": 800, "note": "商业室内设计公司和建筑事务所直招"},
]
SALARIES = [
    {"experience": "初级室内设计师（0~2年）", "salary_min": 52000, "salary_max": 68000, "salary_note": "毕业设计师助理起薪", "sort_order": 0},
    {"experience": "中级室内设计师（2~8年）", "salary_min": 72000, "salary_max": 97000, "salary_note": "SEEK 区间 $80k~$95k；Indeed 均值 $93,437；Glassdoor 均值 $73,488（2026）", "sort_order": 1},
    {"experience": "高级室内设计师（8~15年）", "salary_min": 95000, "salary_max": 130000, "salary_note": "SalaryExpert 资深室内设计师均值 $99,299；悉尼资深设计师约 $95,000", "sort_order": 2},
    {"experience": "室内设计总监 / 独立工作室（12年+）", "salary_min": 120000, "salary_max": 250000, "salary_note": "独立设计工作室或大型商业项目设计总监，含项目提成", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，建筑设计公司和室内设计公司可担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要VETASSESS技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要空间感知力+材料知识+设计软件+项目管理综合能力"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "本科3年；TAFE文凭1~2年；积累商业项目经验约2~3年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "VETASSESS评估；项目作品集（含空间方案和施工图）是关键"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "建筑市场周期性影响需求；商业重设计方向需求稳定"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级职位竞争较激烈；有商业项目经验的资深设计师供需平衡"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "多项目并行、施工监管期压力大；客户沟通和协调要求高"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级 $72k~$97k；独立工作室收入上限高，但初期收入不稳定"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "建筑市场与经济周期相关；可持续设计和商业空间方向有增长"},
    {"dimension": "ai_risk",                  "label_zh": "中低", "stars": 2, "note": "AI效果图工具改变视觉化流程，但空间规划判断和客户沟通不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL，雇主担保482可行；建筑/设计公司有担保能力"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "非短缺职业，189邀请分数要求高；雇主担保是更可行路径"},
]
SUITABILITY_FIT = ["持有室内设计/室内建筑学位，有商业或住宅设计项目作品集", "掌握3D设计软件（SketchUp/AutoCAD/Revit）和效果图制作", "有施工图绘制能力和建材/家具知识", "英语沟通能力强（与客户、建筑师、承包商的协调是核心工作）", "有意向在建筑事务所或室内设计公司（或独立开设工作室）发展"]
SUITABILITY_UNFIT = ["仅有家居装饰（软装）经验，无施工图和空间规划能力", "不擅长客户沟通和项目协调（室内设计50%是设计，50%是项目管理）", "期望通过室内设计快速获得技术移民（非短缺职业，移民难度较高）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "室内设计师薪资 $80k~$95k（2026）", "url": "https://au.seek.com/career-advice/role/interior-designer/salary"},
    {"source_name": "Indeed AU", "content": "室内设计师平均薪资 $93,437（2026）", "url": "https://au.indeed.com/career/interior-designer/salaries"},
    {"source_name": "Glassdoor AU", "content": "室内设计师平均薪资 $73,488（2026）", "url": "https://www.glassdoor.com.au/Salaries/interior-designer-salary-SRCH_KO0,17.htm"},
    {"source_name": "SalaryExpert AU", "content": "室内设计师平均薪资 $99,299（2026）", "url": "https://www.salaryexpert.com/salary/job/interior-designer/australia"},
    {"source_name": "Bespoke Careers Sydney", "content": "悉尼室内设计师均值 $95,000（2026）", "url": "https://www.bespokecareers.com/salary-guide/sydney/"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲室内设计师工资多少？", "answer": "中级室内设计师约 $72,000~$97,000（SEEK $80k~$95k；Indeed $93,437；Glassdoor $73,488；SalaryExpert $99,299）；高级设计师约 $95k~$130k；设计总监/独立工作室约 $120k~$250k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲室内设计师容易找工作吗？", "answer": "中等难度。建筑装修市场活跃时需求旺盛，SEEK 挂牌约300~800个职位。有商业项目经验（办公室/零售/酒店）的资深设计师需求稳定，初级职位竞争较激烈。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国室内设计经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国室内设计本科学历和工作经验可以认可。需要提供商业项目作品集（方案设计+施工图+实景照片）。澳洲市场更注重空间功能性和可持续性，建议补充澳洲本地建材市场和建筑法规知识。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "室内设计师会被AI替代吗？", "answer": "AI效果图工具（Midjourney、Adobe Firefly）正在改变设计可视化流程，但空间规划决策、建材选型、施工协调和客户关系管理仍需专业设计师。向高端住宅设计和商业空间策略方向发展可有效保持竞争优势。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲室内设计师有年龄限制吗？", "answer": "无。有丰富高端住宅或商业项目经验和客户网络的资深设计师（40~55岁）在市场上非常有竞争力。室内设计是高度依赖口碑和客户关系的职业，资历越深越有价值。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲室内设计师需要什么学历？", "answer": "大型商业设计公司通常要求室内设计/室内建筑本科学历；住宅装饰设计市场可以凭TAFE文凭+强作品集入行。DIA会员资格（设计澳洲协会）提升专业信誉。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲室内设计师认证（移民）难吗？", "answer": "不在MLTSSL，移民难度中等偏高。雇主担保482是可行路径，建筑/室内设计公司有担保能力。建议先通过学生签证就读室内设计或建筑相关课程，积累澳洲本地项目经验后申请担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "室内设计师和建筑师哪个澳洲发展更好？", "answer": "建筑师薪资更高（$90k~$150k+），但注册要求严格（ARB注册，需要5~7年专业培训）；室内设计师入行门槛相对较低，市场更灵活（可以独立开工作室）。有建筑学背景者强烈推荐获得ARB注册成为建筑师；有设计天赋但不想长期读书者选室内设计。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 室内设计师数据入库完成")

if __name__ == "__main__":
    run()
