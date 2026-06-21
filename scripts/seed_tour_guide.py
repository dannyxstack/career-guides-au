"""澳洲旅游导游/旅游顾问（451411）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "451411", "anzsco_title": "Tour Guide",
    "category": "餐饮/酒店/旅游", "workforce_size": 20000, "shortage_listed": 0,
    "growth_areas": json.dumps(["生态旅游导游（大堡礁/雨林/红土中心）","华语导游（中国入境游复苏）","探险和户外旅游导游","自驾游顾问（Campervan/4WD）","旅游规划师（定制化高端旅游）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "旅游导游/旅游顾问",
    "summary": "旅游导游为游客提供向导解说、行程组织和安全管理服务，覆盖城市观光、自然生态、文化遗产和冒险旅游等类型；旅游顾问为客户规划和预订旅游产品。澳洲旅游业全面复苏（国际游客人数超越COVID前水平），华语导游因中国入境游复苏而需求大幅增加，是华人求职者的独特优势方向。",
    "forecast_note": "JSA预测旅游导游就业至2030年增长约12%。中国游客回流（每年超过100万人次）和生态旅游需求增长是最大驱动力。偏远地区生态旅游（NT/QLD/WA）导游极度短缺。",
    "trend_summary": "澳洲入境旅游全面恢复，中国是最大单一来源市场之一（超100万/年）。华语导游（普通话/粤语）在大堡礁、悉尼、墨尔本和黄金海岸需求极旺盛，薪资优于普通导游。生态旅游（大堡礁潜水/雨林徒步/红土中心自驾）成为最高价值的导游方向。",
}
I18N_EN = {
    "locale": "en", "name": "Tour Guide / Travel Consultant",
    "summary": "Tour guides provide guiding commentary, itinerary organisation and safety management for tourists across city sightseeing, nature ecology, cultural heritage and adventure tourism; travel consultants plan and book travel products for clients. Australia's tourism industry has fully recovered (international visitor numbers exceeding pre-COVID levels), with Mandarin/Cantonese-speaking guides in high demand due to Chinese inbound tourism recovery — a distinct competitive advantage for Chinese-speaking jobseekers.",
    "forecast_note": "JSA projects ~12% tour guide employment growth by 2030. The return of Chinese visitors (over 1 million annually) and growing ecotourism demand are the biggest drivers. Remote area ecotourism guides (NT/QLD/WA) face acute shortages.",
    "trend_summary": "Australian inbound tourism has fully recovered, with China as one of the largest single source markets (1M+ per year). Mandarin/Cantonese-speaking guides at the Great Barrier Reef, Sydney, Melbourne and Gold Coast are in very high demand at salaries above average tour guides. Ecotourism (Great Barrier Reef diving/rainforest trekking/Red Centre road trips) has become the highest-value guiding direction.",
}
EDUCATION = [
    {"stage": "Certificate III or IV in Tourism（SIT30216/SIT40116）", "duration": "6~12个月", "cost_min": 2000, "cost_max": 12000, "cost_note": "TAFE或旅游学院；是澳洲导游资质的主流路径", "sort_order": 0},
    {"stage": "澳洲导游注册（各州/领地导游执照）", "duration": "课程+考核", "cost_min": 300, "cost_max": 2000, "cost_note": "部分景区（大堡礁/卡卡杜）要求特定导游执照；年费约 $200~$500", "sort_order": 1},
    {"stage": "急救和水上安全认证", "duration": "2~3天课程", "cost_min": 200, "cost_max": 500, "cost_note": "户外和水上导游的实际必要资质", "sort_order": 2},
    {"stage": "驾驶执照（小型巴士/4WD）", "duration": "视具体需要", "cost_min": 100, "cost_max": 500, "cost_note": "自驾旅游导游的实际要求", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III/IV in Tourism", "issuer": "TAFE / 旅游学院", "note": "澳洲导游技术评估的基础学历", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "大堡礁海洋公园导游执照", "issuer": "Great Barrier Reef Marine Park Authority", "note": "大堡礁潜水和游船导游的法律要求", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CPR/急救证书（First Aid）", "issuer": "St John Ambulance等认可机构", "note": "所有户外旅游导游的实际必要资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "土著文化意识培训（Indigenous Cultural Awareness）", "issuer": "各认可机构", "note": "涉及土著文化旅游的导游的额外要求", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 300, "count_max": 800, "note": "全国，含旅游导游/旅游顾问/旅游协调员岗"},
    {"platform": "Indeed",   "count_min": 200, "count_max": 600, "note": "含旅游公司、旅行社和景区直招岗"},
    {"platform": "LinkedIn", "count_min": 200, "count_max": 600, "note": "大型旅游集团和旅行社管理岗"},
]
SALARIES = [
    {"experience": "初级旅游导游（0~2年）", "salary_min": 52000, "salary_max": 65000, "salary_note": "全职起薪；含小费后实际收入更高", "sort_order": 0},
    {"experience": "有经验导游（2~8年）", "salary_min": 62000, "salary_max": 85000, "salary_note": "SEEK 导游均值 $60k~$75k；Indeed 均值约 $82,763（$39.79/hr × 2080h）；悉尼均值 $88,000", "sort_order": 1},
    {"experience": "旅游顾问 / 专线导游（3~8年）", "salary_min": 68000, "salary_max": 90000, "salary_note": "SEEK 旅游顾问均值 $70k~$80k；Indeed 旅游顾问均值 $75,239（2026）", "sort_order": 2},
    {"experience": "旅游产品经理 / 导游主管（8年+）", "salary_min": 85000, "salary_max": 130000, "salary_note": "旅游公司产品经理或大型旅游集团导游主管", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，旅游公司可担保（华语导游需求旺盛）", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要Vetassess技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，昆士兰/NT/WA旅游重点州有提名通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远旅游区（NT/QLD偏远）导游极度短缺", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中低", "stars": 2, "note": "技术门槛不高，但需要丰富知识储备（历史/地理/文化）和出色的人际沟通能力"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Certificate III约6~12个月；实践经验比课程更重要"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Vetassess评估需要工作经验证明；特定景区执照有额外要求"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "旅游业全面复苏；华语导游需求量大且持续增长"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "普通英语导游竞争一般；华语（普通话/粤语）导游供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "户外工作体力消耗中等；旅游旺季压力大；服务质量要求高"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "导游 $62k~$85k；小费收入可观；整体薪资中等偏低"},
    {"dimension": "future_prospect",          "label_zh": "中高", "stars": 4, "note": "旅游业持续增长；生态旅游和华语旅游市场是长期增长方向"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "现场导览、安全管理和人际互动是AI无法替代的；AI语音导览只影响低端自助游市场"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "旅游导游不在MLTSSL，但偏远旅游区491路径可行；华语导游雇主担保更容易"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "非MLTSSL短缺职业，技术移民邀请分数要求较高；雇主担保是更可行路径"},
]
SUITABILITY_FIT = ["流利普通话或粤语（华语导游是最大优势方向）+英语沟通能力", "对澳洲历史、地理、生态和文化有深厚了解或强烈学习兴趣", "有旅游行业工作经验（旅行社/景区/导游），持有澳洲旅游类证书", "有意向在旅游重点城市（悉尼/墨尔本/凯恩斯/北领地）长期发展", "有急救资质，驾驶经验良好（特别是自驾旅游方向）"]
SUITABILITY_UNFIT = ["期望通过旅游导游职业快速获得技术移民（非MLTSSL短缺职业，移民难度中等）", "不喜欢户外工作或长时间与陌生人互动", "英语和普通话表达能力不足（导游核心技能）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "旅游导游薪资 $60k~$75k；旅游顾问 $70k~$80k（2026）", "url": "https://au.seek.com/career-advice/role/tour-guide/salary"},
    {"source_name": "Indeed AU", "content": "旅游导游平均时薪 $39.79（约 $82,763/年）；旅游顾问 $75,239（2026）", "url": "https://au.indeed.com/career/tour-guide/salaries"},
    {"source_name": "SalaryExpert AU", "content": "澳洲旅游导游薪资数据（2026）", "url": "https://www.salaryexpert.com/salary/job/tour-guide/australia"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲旅游导游工资多少？", "answer": "有经验导游约 $62,000~$85,000（SEEK $60k~$75k；Indeed约 $82,763；悉尼均值 $88,000）；旅游顾问约 $68k~$90k（Indeed $75,239）；小费（Tipping）可额外增加 $5,000~$15,000/年。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲旅游导游容易找工作吗？", "answer": "普通英语导游竞争中等；华语（普通话/粤语）导游需求量大且供不应求。旅游业全面复苏，大堡礁、凯恩斯、悉尼和黄金海岸华语导游岗位常年空缺。SEEK 挂牌约300~800个职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国旅游从业经验澳洲认可吗？", "answer": "通过Vetassess技能评估，中国旅行社和景区工作经验可以认可。华语导游最大优势是语言能力——流利普通话/粤语是竞争优势，建议补充澳洲旅游类Certificate III课程（约6~12个月）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "旅游导游会被AI替代吗？", "answer": "风险较低。AI语音导览（类似故宫语音导览）影响低端自助游市场；但现场导游的安全管理、临场应变、文化连接和真实人际互动是AI无法提供的。华语服务和高端定制旅游方向抗AI性更强。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲旅游导游有年龄限制吗？", "answer": "无。有丰富澳洲知识积累和文化理解的中年导游（40~55岁）在高端定制旅游市场非常受欢迎。体力要求因导游类型不同而异，文化/历史类导游体力要求较低。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲旅游导游需要什么资质？", "answer": "Certificate III in Tourism是推荐资质；部分景区（大堡礁/卡卡杜）要求特定执照。急救证书（CPR/First Aid）是户外旅游导游的实际必要资质。最重要的是实际知识积累和语言表达能力。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲旅游导游认证（移民）难吗？", "answer": "旅游导游不在MLTSSL，技术移民有一定难度。华语导游通过旅游公司雇主担保482是最可行路径；偏远旅游区（NT/昆州偏远）491路径可行。建议先以打工度假签证（417）或学生签证进入澳洲积累经验，获取雇主担保后再推进长期签证。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "旅游导游和旅游顾问哪个澳洲发展更好？", "answer": "旅游顾问（旅行社销售）薪资略高（$68k~$90k vs 导游 $62k~$85k），工作环境室内为主；旅游导游自由度更高、小费收入可观，华语导游竞争优势更明显。有销售和客户服务背景者选旅游顾问；有语言优势（华语）和户外爱好者选旅游导游。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 旅游导游/旅游顾问数据入库完成")

if __name__ == "__main__":
    run()
