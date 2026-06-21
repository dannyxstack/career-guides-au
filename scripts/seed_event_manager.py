"""澳洲活动策划师/活动经理（149211）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "149211", "anzsco_title": "Conference and Event Organiser",
    "category": "餐饮/酒店/旅游", "workforce_size": 28000, "shortage_listed": 0,
    "growth_areas": json.dumps(["企业会议和奖励旅游（MICE）","混合（线下+线上）活动策划","音乐节和大型体育赛事","婚礼策划和高端庆典","可持续绿色活动（Green Events）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "活动策划师/活动经理",
    "summary": "活动策划师和活动经理负责企业会议、展览、婚礼、音乐节和体育赛事的全流程策划、预算管理、供应商协调和现场执行。澳洲MICE（会议/奖励/会议/展览）市场（$360亿/年）全面复苏，推动对专业活动管理人才的旺盛需求。有大型活动经验和数字化活动技能（混合活动平台）的策划师竞争力最强。",
    "forecast_note": "JSA预测活动策划就业至2030年增长约10%。企业MICE活动是最大增长方向，音乐节和大型体育赛事（2032年布里斯班奥运会）提供额外就业机会。",
    "trend_summary": "澳洲MICE市场COVID后全面反弹，企业活动预算大幅增加。混合（线下+线上）活动已成为行业新标准，有虚拟活动平台（Hopin/Whova/Teams Live）操作经验的策划师需求旺盛。布里斯班2032奥运会将在未来6年内创造大量活动管理岗位。",
}
I18N_EN = {
    "locale": "en", "name": "Event Planner / Event Manager",
    "summary": "Event planners and managers oversee full-cycle planning, budget management, vendor coordination and on-site execution for corporate conferences, exhibitions, weddings, music festivals and sports events. Australia's MICE (Meetings/Incentives/Conferences/Exhibitions) market ($36B/year) has fully recovered, driving strong demand for professional event management talent. Planners with large-scale event experience and digital event skills (hybrid event platforms) are most competitive.",
    "forecast_note": "JSA projects ~10% event planning employment growth by 2030. Corporate MICE events are the largest growth direction, with music festivals and major sporting events (Brisbane 2032 Olympics) providing additional employment opportunities.",
    "trend_summary": "Australia's MICE market has fully rebounded post-COVID with significantly increased corporate event budgets. Hybrid (in-person + online) events have become the new industry standard, with strong demand for planners with virtual event platform (Hopin/Whova/Teams Live) experience. Brisbane's 2032 Olympics will create substantial event management roles over the next 6 years.",
}
EDUCATION = [
    {"stage": "Bachelor of Event Management / Hospitality（3年）", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 110000, "cost_note": "多所澳洲大学提供活动管理专业；国际生约 $25,000~$35,000/年", "sort_order": 0},
    {"stage": "Diploma of Event Management（TAFE/私立，1~2年）", "duration": "1~2年", "cost_min": 5000, "cost_max": 25000, "cost_note": "实践型活动管理文凭，许多活动经理的实际入门路径", "sort_order": 1},
    {"stage": "Project Management 认证（PMP/Prince2）", "duration": "1~3个月", "cost_min": 1000, "cost_max": 5000, "cost_note": "大型活动项目管理能力认证，提升竞争力和薪资", "sort_order": 2},
    {"stage": "数字活动平台技能（Hopin/Cvent/EventBrite）", "duration": "自主学习", "cost_min": 0, "cost_max": 1000, "cost_note": "混合活动时代的事实标准工具技能", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate IV/Diploma of Event Management", "issuer": "TAFE / 认可私立机构", "note": "技术移民评估的核心学历要求", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "PMP（Project Management Professional）", "issuer": "Project Management Institute", "note": "大型活动和会议项目管理的国际认可证书", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Meetings & Events Australia (MEA) 会员", "issuer": "Meetings & Events Australia", "note": "澳洲活动管理行业协会会员资格，提升专业信誉", "is_mandatory": 0, "sort_order": 2},
        {"qual_name": "RSA（Responsible Service of Alcohol）", "issuer": "各州认可机构", "note": "涉及酒精服务活动的法律要求", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600, "count_max": 2000, "note": "全国，含活动策划/活动经理/会议协调员岗"},
    {"platform": "Indeed",   "count_min": 500, "count_max": 1500, "note": "含企业活动部门、酒店宴会部和活动公司岗"},
    {"platform": "LinkedIn", "count_min": 800, "count_max": 2500, "note": "企业内部活动团队和MICE专业活动公司直招"},
]
SALARIES = [
    {"experience": "活动协调员（0~2年）", "salary_min": 58000, "salary_max": 72000, "salary_note": "活动助理或协调员起薪", "sort_order": 0},
    {"experience": "活动策划师（2~6年）", "salary_min": 70000, "salary_max": 85000, "salary_note": "SEEK 活动策划 $75k~$80k；Indeed 均值 $75,646（2026）", "sort_order": 1},
    {"experience": "活动经理（4~10年）", "salary_min": 83000, "salary_max": 108000, "salary_note": "SEEK 活动经理 $85k~$105k；Indeed 均值 $80,122（2026）", "sort_order": 2},
    {"experience": "活动总监 / MICE总监（10年+）", "salary_min": 110000, "salary_max": 180000, "salary_note": "大型活动公司总监或五星酒店宴会总监", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，大型活动公司和酒店宴会部可担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要Vetassess技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道（QLD奥运相关岗位可能有特别通道）", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要项目管理+供应商谈判+现场执行+预算控制综合能力"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3年；文凭1~2年；积累大型活动经验约3~5年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Vetassess评估需要活动管理工作经验证明"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "MICE市场全面复苏；布里斯班奥运相关岗位增加；企业活动预算增加"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "活动协调员竞争激烈；有大型MICE活动经验的经理供不应求"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "活动执行期极高强度（长时间工作、周末必上）；多项目并行压力大"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "活动经理 $83k~$108k；活动总监 $110k~$180k；整体薪资中等"},
    {"dimension": "future_prospect",          "label_zh": "中高", "stars": 4, "note": "MICE市场反弹+奥运相关活动推动中期增长；混合活动技能是竞争优势"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "活动现场执行和危机管理是AI无法替代的；AI优化预算和供应商匹配提升效率"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL，雇主担保482可行；酒店宴会部和活动公司有担保能力"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "非短缺职业，189邀请分数要求高；雇主担保是更可行路径"},
]
SUITABILITY_FIT = ["持有活动管理/酒店管理学历，有3年以上活动策划和执行工作经验", "有大型MICE活动（企业年会/展览/会议）或婚礼策划完整项目经验", "有混合活动平台（Hopin/Cvent/Teams Live/Zoom Webinars）操作经验", "英语沟通流利（与供应商、客户和场地的谈判是核心工作）", "有意向在布里斯班（奥运相关活动机会最多）或悉尼/墨尔本就业"]
SUITABILITY_UNFIT = ["仅有婚庆策划小型活动经验，无企业MICE或大型活动项目经验", "不耐高压和长时间工作（活动执行期极高强度）", "期望通过活动策划快速获得技术移民（非短缺职业，需要雇主担保）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "活动策划 $75k~$80k；活动经理 $85k~$105k（2026）", "url": "https://au.seek.com/career-advice/role/events-manager/salary"},
    {"source_name": "Indeed AU", "content": "活动策划均值 $75,646；活动经理均值 $80,122（2026）", "url": "https://au.indeed.com/career/event-manager/salaries"},
    {"source_name": "SEEK AU", "content": "活动协调员薪资（2026）", "url": "https://www.seek.com.au/career-advice/role/events-coordinator/salary"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲活动策划/活动经理工资多少？", "answer": "活动策划师约 $70,000~$85,000（SEEK $75k~$80k；Indeed $75,646）；活动经理约 $83,000~$108,000（SEEK $85k~$105k；Indeed $80,122）；活动总监约 $110k~$180k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲活动策划师容易找工作吗？", "answer": "中等难度。MICE市场全面复苏推动需求增长，SEEK 挂牌约600~2,000个职位。有大型企业活动和MICE经验的经理供不应求；布里斯班2032奥运相关岗位在未来6年内持续增加。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国活动策划经验澳洲认可吗？", "answer": "通过Vetassess技能评估，中国大型活动策划和MICE经验可以认可。需要提供英文项目经历证明（活动规模/预算/参与人数）。建议补充澳洲活动管理行业认可的证书（MEA会员或Diploma）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "活动策划师会被AI替代吗？", "answer": "风险较低。AI优化供应商匹配、预算管理和活动日程自动化；但现场协调、客户关系管理和突发危机处理是AI无法替代的核心价值。向大型活动总监和MICE专家方向发展可有效规避AI风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲活动策划师有年龄限制吗？", "answer": "无。有丰富行业供应商网络和大型活动经验的资深活动总监（40~55岁）非常有竞争力。活动行业高度依赖人脉和经验积累，资历越深越有价值。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲活动策划师需要什么学历？", "answer": "大型活动公司和酒店宴会部通常要求活动管理或酒店管理相关学历；中小型活动公司更注重项目经验和作品集（活动案例）。PMP认证在大型项目管理类活动岗位有显著加分。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲活动策划师认证（移民）难吗？", "answer": "不在MLTSSL，移民难度中等偏高。雇主担保482是最可行路径，大型活动公司和五星酒店宴会部有担保能力。建议先通过学生签证就读活动管理或酒店管理课程，积累本地供应商网络后申请担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "活动策划师和营销经理哪个澳洲发展更好？", "answer": "营销经理薪资略高（$95k~$125k vs 活动经理 $83k~$108k），就业市场更大；活动策划师工作内容更多元（每个活动都不同），有奥运相关额外机会。有品牌推广背景者选营销经理；有活动执行热情的选活动经理（两者技能高度互补）。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 活动策划师/活动经理数据入库完成")

if __name__ == "__main__":
    run()
