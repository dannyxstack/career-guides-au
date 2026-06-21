"""澳洲酒店经理（141311）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "141311", "anzsco_title": "Hotel or Motel Manager",
    "category": "餐饮/酒店/旅游", "workforce_size": 35000, "shortage_listed": 1,
    "growth_areas": json.dumps(["精品酒店和生态度假村管理","高端旅游目的地酒店","商务会议酒店（MICE市场）","数字化酒店运营（PMS/OTA管理）","可持续酒店管理（绿色认证）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "酒店经理",
    "summary": "酒店经理负责酒店/汽车旅馆的整体运营管理，包括前台、客房、餐饮、销售、人员和财务管理。澳洲旅游业强劲复苏（入境和国内旅游创历史新高）推动酒店行业持续扩张，有酒店管理经验的专业人员长期短缺。五星酒店、精品度假村和大型会议酒店的酒店经理薪资溢价显著。",
    "forecast_note": "JSA预测酒店经理就业至2030年增长约8%。澳洲入境旅游恢复、国内旅游旺盛和亚太地区商务旅游增长是主要驱动力。精品酒店和可持续度假村方向是增速最快的细分市场。",
    "trend_summary": "澳洲旅游业（2026年产值约 $770亿）全面复苏，国际游客人数超越COVID前水平。酒店数字化转型（OTA管理/PMS系统/动态定价）成为行业标配，有酒店科技运营能力的经理人需求特别旺盛。高端住宿市场（精品酒店/豪华度假村）增速超过标准商务酒店。",
}
I18N_EN = {
    "locale": "en", "name": "Hotel / Motel Manager",
    "summary": "Hotel managers oversee the overall operations of hotels/motels, including front desk, housekeeping, F&B, sales, staffing and financial management. Australia's strong tourism recovery (inbound and domestic tourism at historic highs) drives continued hospitality sector expansion, with experienced hotel management professionals in long-term shortage. Five-star hotel, boutique resort and large conference hotel managers command significant salary premiums.",
    "forecast_note": "JSA projects ~8% hotel manager employment growth by 2030. Australian inbound tourism recovery, strong domestic tourism and Asia-Pacific business travel growth are the main drivers. Boutique hotels and sustainable resorts are the fastest-growing market segments.",
    "trend_summary": "Australia's tourism industry (valued at ~$77B in 2026) has fully recovered, with international visitor numbers surpassing pre-COVID levels. Hotel digital transformation (OTA management/PMS systems/dynamic pricing) has become industry standard, with strong demand for managers with hospitality tech operation skills. The luxury accommodation market (boutique hotels/luxury resorts) is growing faster than standard business hotels.",
}
EDUCATION = [
    {"stage": "Bachelor of Hotel Management / Hospitality Management（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 130000, "cost_note": "William Angliss、Blue Mountains International Hotel Management School等；国际生约 $28,000~$40,000/年", "sort_order": 0},
    {"stage": "Diploma of Hospitality Management（SIT50422，1.5~2年）", "duration": "18~24个月", "cost_min": 5000, "cost_max": 30000, "cost_note": "TAFE或私立学院酒店管理文凭，是多数酒店经理的实际资质路径", "sort_order": 1},
    {"stage": "酒店管理实习经验（Internship/Industry Placement）", "duration": "6~12个月实习", "cost_min": 0, "cost_max": 0, "cost_note": "大型酒店集团（Accor/Marriott/IHG）的管理培训项目是晋升快速通道", "sort_order": 2},
    {"stage": "Vetassess 技能评估", "duration": "3~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民路径必须的技能评估机构", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Diploma/Bachelor of Hospitality Management", "issuer": "认可的酒店管理院校", "note": "技术移民评估的基础学历要求", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Food Safety Supervisor Certificate", "issuer": "各州认可机构", "note": "酒店餐饮运营的法律要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "RSA（Responsible Service of Alcohol）", "issuer": "各州认可机构", "note": "酒店提供酒精服务的法律要求", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "Vetassess 技能评估（ANZSCO 141311）", "issuer": "Vetassess", "note": "189/190/491技术移民必须的评估", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 800, "count_max": 2500, "note": "全国，含酒店总经理/副总经理/客房经理/前台经理岗"},
    {"platform": "Indeed",   "count_min": 600, "count_max": 2000, "note": "含国际酒店集团和独立酒店管理岗"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 3000, "note": "Accor/Marriott/IHG等国际酒店集团直招"},
]
SALARIES = [
    {"experience": "助理酒店经理（0~3年）", "salary_min": 65000, "salary_max": 82000, "salary_note": "前台经理或部门主管起薪", "sort_order": 0},
    {"experience": "酒店经理（3~10年）", "salary_min": 80000, "salary_max": 105000, "salary_note": "SEEK 区间 $80k~$100k；Indeed 均值 $88,343；Glassdoor 均值 $95,800（2026）", "sort_order": 1},
    {"experience": "资深酒店总经理（10~18年）", "salary_min": 105000, "salary_max": 160000, "salary_note": "四/五星级酒店总经理；住宿经理均值 $84,195（Indeed 2026）", "sort_order": 2},
    {"experience": "区域总监 / 集团高管（15年+）", "salary_min": 150000, "salary_max": 350000, "salary_note": "Accor/Marriott/Hilton区域总监或集团高管薪资区间", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，大型酒店集团和度假村最常见路径", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，国际酒店集团担保路径成熟", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，Vetassess评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，旅游重点州（QLD/SA/TAS/NT）积极提名", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远度假村和旅游区酒店极度紧缺，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要运营+财务+人力+销售+客户服务的全面酒店管理综合能力"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3年或文凭1.5~2年；晋升总经理需要8~12年实践经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Vetassess评估难度中等；酒店管理工作经验和学历证明是关键"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，澳洲旅游复苏推动旺盛需求；偏远旅游区极度短缺"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "有资质的酒店经理供不应求，国际酒店集团主动全球招聘"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "酒店运营7天24小时，总经理责任重大，高峰期压力极大"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "酒店经理 $80k~$105k；五星酒店总经理 $105k~$160k；集团高管 $150k+"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "旅游业扩张和亚太商务旅游增长推动稳定需求；精品酒店方向增速最快"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI优化动态定价和预订管理，但客户服务、危机处理和团队领导不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，旅游重点州积极提名；国际酒店集团担保活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "Vetassess评估清晰；雇主担保482路径成熟；偏远旅游区491最容易"},
]
SUITABILITY_FIT = ["持有酒店/hospitality管理学位或文凭，有3年以上酒店管理工作经验", "有国际酒店集团（Accor/Marriott/IHG/Hilton等）工作背景，英语沟通能力强", "熟悉PMS酒店管理系统（Opera/RMS/Maestro等）和OTA渠道管理", "有在旅游重点目的地（昆士兰/NT/SA/TAS）任职意愿", "已有澳洲酒店集团的担保意向或在同一集团内的内部调动机会"]
SUITABILITY_UNFIT = ["无正规酒店管理学历或文凭（仅有服务员/前台工作经验）", "英语沟通能力不足以担任管理者和处理高端客户需求", "不接受包含周末和节假日的不规律管理工作"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "酒店经理薪资 $80k~$100k（2026）", "url": "https://au.seek.com/career-advice/role/hotel-manager/salary"},
    {"source_name": "Indeed AU", "content": "酒店经理平均薪资 $88,343（2026）", "url": "https://au.indeed.com/career/hotel-manager/salaries"},
    {"source_name": "Glassdoor AU", "content": "酒店经理平均薪资 $95,800（2026）", "url": "https://www.glassdoor.com.au/Salaries/hotel-manager-salary-SRCH_KO0,13.htm"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲酒店经理工资多少？", "answer": "酒店经理约 $80,000~$105,000（SEEK $80k~$100k；Indeed $88,343；Glassdoor $95,800）；资深四/五星酒店总经理约 $105k~$160k；区域总监/集团高管约 $150k~$350k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲酒店经理容易找工作吗？", "answer": "容易。MLTSSL短缺职业，旅游业全面复苏推动旺盛需求，SEEK 挂牌约 800~2,500 个职位。有国际酒店集团经验的经理人竞争力极强，偏远旅游目的地（凯恩斯/北领地/塔斯马尼亚）酒店经理极度紧缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国酒店管理经验澳洲认可吗？", "answer": "通过Vetassess技能评估，中国国际酒店集团（锦江/华住/洲际等）工作经验可以认可。有同一国际集团（如Accor/Marriott）内部调动机会最为顺畅。英语能力是主要挑战（IELTS 6.0+），PMS系统操作经验（Opera等）有加分。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "酒店经理会被AI替代吗？", "answer": "不会。AI优化动态定价、预订管理和能源效率，但酒店危机管理（客户投诉/设施故障）、团队领导和高端客户关系管理是AI无法替代的核心管理职责。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲酒店经理有年龄限制吗？", "answer": "无。有丰富国际酒店管理经验的中高年龄经理人（40~55岁）在澳洲非常受欢迎，特别是有五星酒店总经理经验者。成熟稳重是高端酒店管理岗位的优势。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲酒店经理需要什么学历？", "answer": "大型国际酒店集团通常要求酒店管理本科或文凭；但有10年以上总经理经验的候选人即使学历偏低也可以通过经验评估（Recognition of Prior Learning）。William Angliss和Blue Mountains酒店管理学院毕业证书在澳洲行业内认知度高。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲酒店经理认证（移民）难吗？", "answer": "难度较低。MLTSSL在列，Vetassess评估路径清晰，雇主担保482非常活跃（特别是国际酒店集团）。昆士兰、北领地和塔斯马尼亚等旅游重点州积极提名酒店管理人员。偏远旅游度假区491路径最容易。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "酒店经理和餐厅经理哪个澳洲发展更好？", "answer": "酒店经理薪资更高（$80k~$105k vs 餐厅经理 $72k~$92k），职业发展路径更宽广（区域总监/集团高管）；餐厅经理岗位数量更多（全澳餐厅数量远多于酒店），雇主担保更容易获得。有国际酒店集团背景者选酒店经理；有餐饮运营背景者选餐厅经理。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 酒店经理数据入库完成")

if __name__ == "__main__":
    run()
