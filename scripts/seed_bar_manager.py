"""澳洲调酒师/酒吧经理（431111）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "431111", "anzsco_title": "Bar Attendant",
    "category": "餐饮/酒店/旅游", "workforce_size": 70000, "shortage_listed": 0,
    "growth_areas": json.dumps(["精调鸡尾酒吧（Cocktail Bar/Speakeasy）","葡萄酒侍酒师（Sommelier）","精酿啤酒吧（Craft Beer）","无酒精饮品吧（Zero Alcohol/Mocktail）","酒吧经理和酒店F&B经理"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "调酒师/酒吧经理",
    "summary": "调酒师为顾客调制和提供酒精及非酒精饮品，在酒吧、餐厅、酒店和活动现场工作；酒吧经理负责酒吧运营、库存管理和人员督导。澳洲酒水服务行业（$200亿+/年）持续活跃，精品鸡尾酒吧和葡萄酒吧市场快速增长，有调酒技艺和侍酒师知识的从业者薪资溢价显著。酒吧经理是MLTSSL在列的短缺职业，移民路径相对清晰。",
    "forecast_note": "JSA预测酒水服务行业就业至2030年基本稳定。精品鸡尾酒吧和高端酒吧方向增长，低酒精/无酒精饮品市场快速增长（健康生活趋势），标准酒吧岗位数量平稳。",
    "trend_summary": "澳洲精品鸡尾酒文化持续高端化，悉尼和墨尔本进入全球50佳酒吧排名的数量持续增加。无酒精精调饮品（Mocktail）成为主流菜单选项。葡萄酒教育（WSET/侍酒师认证）需求大幅增长。有侍酒师资格的调酒师薪资比普通调酒师高约20~30%。",
}
I18N_EN = {
    "locale": "en", "name": "Bartender / Bar Manager",
    "summary": "Bartenders mix and serve alcoholic and non-alcoholic beverages for patrons in bars, restaurants, hotels and event venues; bar managers oversee bar operations, inventory management and staff supervision. Australia's beverage service industry ($20B+/year) remains active, with the premium cocktail bar and wine bar market growing rapidly. Practitioners with bartending skills and sommelier knowledge command significant salary premiums. Bar Manager is MLTSSL-listed (short supply), providing a relatively clear migration pathway.",
    "forecast_note": "JSA projects broadly stable beverage service industry employment through 2030. Premium cocktail bars and high-end venues are growing, the low-alcohol/non-alcoholic beverage market is rapidly growing (health lifestyle trend), while standard bar positions remain flat.",
    "trend_summary": "Australia's premium cocktail culture continues premiumising, with Sydney and Melbourne increasingly represented in the World's 50 Best Bars. Non-alcoholic craft beverages (mocktails) have become mainstream menu items. Wine education (WSET/sommelier certification) demand is growing significantly. Bartenders with sommelier qualifications earn approximately 20-30% more than standard bartenders.",
}
EDUCATION = [
    {"stage": "Certificate II/III in Hospitality（含RSA和调酒单元）", "duration": "6~12个月", "cost_min": 2000, "cost_max": 10000, "cost_note": "TAFE或私立酒店学校；是调酒师的入门资质路径", "sort_order": 0},
    {"stage": "WSET（葡萄酒及烈酒教育基金会）Level 2/3 认证", "duration": "2~6个月", "cost_min": 500, "cost_max": 3000, "cost_note": "全球最权威的葡萄酒和烈酒教育认证；Level 2约 $500，Level 3约 $1,500", "sort_order": 1},
    {"stage": "Australian Bartenders Guild 调酒认证", "duration": "各级别1~3天", "cost_min": 300, "cost_max": 2000, "cost_note": "澳洲调酒师协会提供的专业调酒技能认证", "sort_order": 2},
    {"stage": "Food Safety Supervisor + RSA 证书", "duration": "1~2天", "cost_min": 150, "cost_max": 500, "cost_note": "澳洲所有酒水服务从业者的法律必须资质", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "RSA（Responsible Service of Alcohol）", "issuer": "各州认可机构", "note": "澳洲所有接触酒精服务的从业者的法律要求，费用约 $50~$150", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "WSET Level 2/3（葡萄酒及烈酒）", "issuer": "Wine & Spirit Education Trust", "note": "侍酒师和高端酒吧调酒师的专业进阶认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Food Safety Supervisor Certificate", "issuer": "各州认可机构", "note": "酒吧经理的法律要求", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "Vetassess 技能评估（酒吧经理 431111）", "issuer": "Vetassess", "note": "酒吧经理技术移民（ANZSCO 431111）必须的评估", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1500, "count_max": 4000, "note": "全国，含调酒师/酒吧经理/侍酒师/饮品主管岗"},
    {"platform": "Indeed",   "count_min": 1000, "count_max": 3000, "note": "含酒店F&B部门、餐厅酒水岗和夜场酒吧岗"},
    {"platform": "LinkedIn", "count_min": 500, "count_max": 1500, "note": "酒店集团和高端餐饮直招"},
]
SALARIES = [
    {"experience": "初级调酒师（0~2年）", "salary_min": 52000, "salary_max": 66000, "salary_note": "全职调酒师基础薪资；酒吧行业普遍含小费", "sort_order": 0},
    {"experience": "有经验调酒师（2~6年）", "salary_min": 64000, "salary_max": 80000, "salary_note": "SEEK 调酒师均值 $65k~$75k；Indeed 均值约 $70,803（$34.04/hr × 2080h）", "sort_order": 1},
    {"experience": "酒吧经理（3~8年）", "salary_min": 75000, "salary_max": 92000, "salary_note": "SEEK 酒吧经理均值 $80k~$85k；高端酒店酒吧经理可达 $85k~$95k", "sort_order": 2},
    {"experience": "侍酒师 / 高级饮品总监（5年+）", "salary_min": 85000, "salary_max": 130000, "salary_note": "持有侍酒师资格（Court of Master Sommeliers）的顶级从业者", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，酒店和高端餐厅最常见路径（以酒吧经理岗担保）", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，需满足2年担保期", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "酒吧经理（431111）有时被纳入提名清单，需确认各州具体情况", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，部分州将酒吧经理纳入提名", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区酒吧和酒店缺人，加15分可行", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中低", "stars": 2, "note": "基础调酒技能门槛不高；精品鸡尾酒和侍酒师方向有较高知识要求"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "初级调酒师可快速上岗；WSET认证约2~6个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Vetassess以酒吧经理评估难度中等；需RSA+管理经验证明"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "餐饮行业持续活跃；精品酒吧市场旺盛；夜间经济政策推动高需求"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级调酒师竞争一般；有侍酒师资格和精品鸡尾酒技能者供不应求"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "夜间和周末工作；高峰时段极快节奏；体力消耗较大"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "调酒师 $64k~$80k；酒吧经理 $75k~$92k；含小费实际收入较高"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "精品酒吧持续增长；无酒精饮品新市场；但整体行业受夜经济政策影响"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "调酒技艺和顾客互动高度抗AI；自动化饮品机仅影响标准连锁市场"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "以酒吧经理（非调酒师）身份申请更有优势；MLTSSL含部分酒店服务管理职位"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "初级调酒师移民难度高；以酒吧经理身份申请需管理经验证明"},
]
SUITABILITY_FIT = ["有3年以上调酒工作经验+1年以上酒吧管理经验，有意以酒吧经理身份申请技术移民", "持有WSET Level 2/3或侍酒师认证，有精品鸡尾酒吧或高端酒店F&B工作背景", "持有RSA和Food Safety Supervisor证书（法律要求，必须具备）", "英语沟通能力良好（顾客服务和供应商沟通）", "愿意在餐饮活跃城市（悉尼/墨尔本/布里斯班）的高端酒店或餐厅工作"]
SUITABILITY_UNFIT = ["仅有中国国内酒吧或KTV服务经验，无西式酒吧调酒技艺（烈酒/鸡尾酒）", "无RSA（澳洲酒精服务法律必须资质）", "期望通过初级调酒师岗位快速获得技术移民（需要以管理岗身份申请）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "调酒师薪资 $65k~$75k；酒吧经理 $80k~$85k（2026）", "url": "https://au.seek.com/career-advice/role/bar-manager/salary"},
    {"source_name": "Indeed AU", "content": "调酒师平均时薪 $34.04（约 $70,803/年，2026）", "url": "https://au.indeed.com/career/bartender/salaries"},
    {"source_name": "PayScale AU", "content": "酒吧经理时薪数据（2026）", "url": "https://www.payscale.com/research/AU/Job=Bar_Manager/Salary"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲调酒师/酒吧经理工资多少？", "answer": "有经验调酒师约 $64,000~$80,000（SEEK $65k~$75k；Indeed约 $70,803）；酒吧经理约 $75,000~$92,000（SEEK $80k~$85k）；侍酒师/高端饮品总监约 $85k~$130k。含小费实际收入高于基本薪资。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲调酒师容易找工作吗？", "answer": "容易。餐饮行业持续活跃，SEEK 挂牌约 1,500~4,000 个职位。精品鸡尾酒吧和高端酒店F&B部门对有WSET认证的调酒师供不应求。夜间经济政策（悉尼深夜经济解禁）推动酒吧就业增加。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国调酒经验澳洲认可吗？", "answer": "通过Vetassess以酒吧经理（431111）身份评估，中国酒吧和餐饮调酒经验可以认可。关键是：①必须持有澳洲RSA（或等同资质）；②最好有管理经验（以经理而非调酒师身份申请）；③WSET认证大幅提升评估竞争力。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "调酒师会被AI/自动化替代吗？", "answer": "风险较低。自动化调酒机（Bartesian等）影响标准连锁酒吧低端饮品出品；但精品手工鸡尾酒调制、顾客互动和酒吧表演技艺是不可替代的核心价值。高端酒吧消费者特别重视调酒师的技艺展示和社交互动体验。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲调酒师有年龄限制吗？", "answer": "无。有丰富酒水知识和顾客关系积累的资深调酒师（35~50岁）在精品鸡尾酒吧和高端侍酒师岗位非常有竞争力。顾客往往更信任有经验的老调酒师。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲调酒师需要什么资质？", "answer": "RSA（Responsible Service of Alcohol）是澳洲所有酒水服务从业者的法律硬性要求（约$50~$150，1天课程），无RSA不可合法上岗。技术移民路径（酒吧经理431111）需要Certificate III Hospitality+RSA+管理经验+Vetassess评估。WSET Level 2/3是精品酒吧的竞争优势证书。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲调酒师认证（移民）难吗？", "answer": "以初级调酒师身份移民难度高；以酒吧经理（431111）身份申请难度中等。需RSA+Certificate III+管理经验+Vetassess评估。建议先通过打工度假（417）积累本地经验，晋升为管理岗后申请雇主担保482。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "调酒师和咖啡师哪个澳洲发展更好？", "answer": "两者薪资相近（酒吧经理 $75k~$92k vs 咖啡馆经理 $68k~$85k）；调酒师含小费实际收入更高，夜间工作时段灵活；咖啡师工作时间更规律（早班）、健康生活方式更好。两者都以经理身份申请MLTSSL，路径相似。有精调鸡尾酒热情者选调酒师；有精品咖啡热情者选咖啡师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 调酒师/酒吧经理数据入库完成")

if __name__ == "__main__":
    run()
