"""澳洲工业设计师（232312）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "232312", "anzsco_title": "Industrial Designer",
    "category": "IT/工程", "workforce_size": 8500, "shortage_listed": 0,
    "growth_areas": json.dumps(["Product Design for Medical Devices","Defence Equipment Design (AUKUS)","Sustainable & Circular Product Design","Consumer Electronics & IoT Hardware","Automotive & EV Component Design"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "工业设计师",
    "summary": "工业设计师设计工业产品、消费品、医疗设备和交通工具的外观和功能，覆盖从概念草图到3D原型的全流程。AUKUS国防制造和医疗器械设计是澳洲工业设计师最有薪资潜力的专业方向。",
    "forecast_note": "JSA 预测工业设计师至2035年就业增长约5%。医疗设备设计（澳洲医疗科技产业）和国防装备设计（AUKUS）是主要驱动力。",
    "trend_summary": "可持续设计（Circular Economy Design）和生命周期评估（LCA）是2025-2026年受大型制造企业最重视的设计技能。AI辅助设计（Generative Design in Fusion 360/Grasshopper）正在改变工业设计工作流。",
}
I18N_EN = {
    "locale": "en", "name": "Industrial Designer",
    "summary": "Industrial designers design the appearance and functionality of industrial products, consumer goods, medical devices and vehicles from concept sketches to 3D prototypes. AUKUS defence manufacturing and medical device design offer the highest salary potential.",
    "forecast_note": "JSA projects ~5% employment growth for industrial designers by 2035. Medical device design (Australian medtech industry) and defence equipment design (AUKUS) are the primary demand drivers.",
    "trend_summary": "Sustainable design (Circular Economy Design) and Life Cycle Assessment (LCA) are the most valued design skills at large manufacturers in 2025-2026. AI-assisted design (Generative Design in Fusion 360) is transforming workflows.",
}
EDUCATION = [
    {"stage": "Bachelor of Industrial Design（荣誉，4年）", "duration": "4年（全日制）", "cost_min": 28000, "cost_max": 170000, "cost_note": "或 Bachelor of Design（产品设计方向）；作品集是就业的核心竞争力", "sort_order": 0},
    {"stage": "Autodesk / SolidWorks 专业认证", "duration": "1~3个月", "cost_min": 200, "cost_max": 1500, "cost_note": "CAD软件专业认证，提升技术技能竞争力", "sort_order": 1},
    {"stage": "ACS / AACA 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "视具体设计方向，工业设计师可能通过ACS（若偏IT/交互）或AACA（若偏建筑空间）评估，需要咨询确认评估机构", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Industrial Design (Honours)", "issuer": "认可大学", "note": "行业基础学历，作品集权重高于学位", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Autodesk Certified Professional (Fusion 360 / Inventor)", "issuer": "Autodesk", "note": "CAD/CAM行业认证，提升工程设计能力", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "SolidWorks Certified Professional (CSWP)", "issuer": "Dassault Systèmes", "note": "制造业设计岗广泛要求的3D建模认证", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Lean Product Development / DfM 认证", "issuer": "各认证机构", "note": "面向制造的设计能力认证，制造业工业设计岗的加分项", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 300,  "count_max": 800,  "note": "全国，含工业设计师、产品设计师和CAD工程师岗"},
    {"platform": "Indeed",   "count_min": 200,  "count_max": 600,  "note": "含医疗设备、消费品和国防设计岗"},
    {"platform": "LinkedIn", "count_min": 400,  "count_max": 1000, "note": "制造业企业和设计顾问公司直招"},
]
SALARIES = [
    {"experience": "初级工业设计师（0~3年）", "salary_min": 60000, "salary_max": 78000, "salary_note": "入门级，作品集质量决定初始薪资", "sort_order": 0},
    {"experience": "中级工业设计师（3~7年）", "salary_min": 78000, "salary_max": 105000, "salary_note": "SEEK 区间 $80k~$100k；Indeed 平均 $84,417（2026）", "sort_order": 1},
    {"experience": "高级/医疗设备设计师（7年+）", "salary_min": 105000, "salary_max": 140000, "salary_note": "医疗器械和国防设备设计专精，薪资溢价显著", "sort_order": 2},
    {"experience": "设计总监 / 创意总监（15年+）", "salary_min": 140000, "salary_max": 200000, "salary_note": "大型制造企业或国防公司创意总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，工业设计师为专业技能岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要技能评估+EOI", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，VIC/NSW制造业设计岗", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "设计思维+CAD工具+材料工学的综合能力，作品集质量最重要"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "4年学位；作品集积累需要贯穿整个学习过程"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "CAD认证难度中低；技能评估机构选择需要确认"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "职位总量较小，但医疗设备和国防方向需求增加"},
    {"dimension": "competition",              "label_zh": "中高", "stars": 4, "note": "职位少，初级岗竞争激烈；高级专精岗供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "项目原型期强度较高，日常设计工作节奏相对规律"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "均值约 $80k~$100k；医疗/国防专精高级岗可达 $130k~$140k"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "AUKUS国防制造和可持续设计提供增长动力"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "生成式设计（Generative Design）影响初步方案生成，但材料/制造约束判断和用户体验设计不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "STOL列表，但职位数量少，建议优先考虑雇主担保482路径"},
    {"dimension": "pr_difficulty",            "label_zh": "较高", "stars": 4, "note": "技能评估机构选择需要确认（非纯IT类）；职位少导致EOI等待期较长"},
]
SUITABILITY_FIT = ["有工业产品/消费品/医疗器械设计实际经验（2年以上）", "有强设计作品集（Portfolio），能展示从概念到原型的完整流程", "熟悉SolidWorks/Fusion 360/Rhino等3D设计软件", "英语能力达到 IELTS 6.5+（设计汇报和客户沟通要求）", "对医疗设备或国防装备设计有专业兴趣（薪资潜力最高）"]
SUITABILITY_UNFIT = ["没有实物产品设计作品集，无法展示3D设计能力", "仅有平面设计或视觉传达背景，无产品设计经验", "不接受作品集展示英语要求（澳洲雇主必须能看懂设计说明）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "工业设计师薪资 $80k~$100k（2026）", "url": "https://au.seek.com/career-advice/role/industrial-designer/salary"},
    {"source_name": "Indeed AU", "content": "工业设计师平均薪资 $84,417（2026）", "url": "https://au.indeed.com/career/industrial-designer/salaries"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲工业设计师工资多少？", "answer": "中级工业设计师约 $78,000~$105,000（Indeed均值 $84,417）；医疗设备/国防设计专精约 $105k~$140k；创意总监约 $140k~$200k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲工业设计师容易找工作吗？", "answer": "有一定难度。Seek 挂牌约 300~800 个职位，总量较少，初级岗竞争激烈。有医疗器械或CAD工程设计专精且作品集突出的设计师更容易找到工作。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国工业设计学历澳洲认可吗？", "answer": "工业设计的技能评估机构需要视具体情况而定（ACS或AACA），建议提前咨询。作品集是最重要的申请材料，需要包含英文设计过程说明。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "工业设计师会被AI替代吗？", "answer": "生成式设计工具（Fusion 360/Grasshopper Generative Design）加速了初步方案生成，但材料/制造约束判断、用户测试解读和创意决策不可替代。AI是辅助工具而非替代品。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲工业设计师有年龄限制吗？", "answer": "无。有丰富医疗器械或国防设备设计经验的资深设计师在市场上仍具高竞争力。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲工业设计师需要什么学历？", "answer": "工业设计/产品设计/机械工程相关学位是主流，但强作品集（含3D产品原型案例）在某些情况下可以弥补学历不足。雇主担保482签证对有经验者友好。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲工业设计师认证（移民）难吗？", "answer": "难度较高。技能评估机构选择需要确认，职位数量少导致EOI等待期较长。建议优先通过雇主担保482签证入境，再在澳洲内部转其他签证。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "工业设计师和UX设计师哪个更适合移民澳洲？", "answer": "UX设计师就业量更大（Seek ~1000 vs 工业设计 ~400），薪资相当，技能评估路径更清晰（ACS评估）。工业设计师在医疗器械和国防方向薪资潜力更高。有产品实物设计背景者选工业设计师，有数字产品设计背景者选UX设计师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 工业设计师数据入库完成")

if __name__ == "__main__":
    run()
