"""澳洲急救人员（411711）数据入库。数据来源：JSA、Paramedics Australasia、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "411711", "anzsco_title": "Ambulance Officer and Paramedic",
    "category": "医疗健康", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Advanced Care Paramedic (ACP)","Community Paramedicine","Industrial & Mining Paramedic (FIFO)","Rural & Remote Paramedic","Critical Care Transfer Paramedic"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "急救人员/急诊医务辅助",
    "summary": "急救人员（Paramedic）在紧急医疗现场提供高级生命支持、药物给予和患者转运服务，服务于澳洲国家救护车系统、矿业工业现场急救和社区急救服务。MLTSSL在列，是紧缺医疗辅助职业。",
    "forecast_note": "JSA 预测急救人员至2035年就业增长约15%。人口老龄化（急救呼叫量增加）、偏远和矿业工业急救扩张是主要驱动力。",
    "trend_summary": "社区急救医疗（Community Paramedicine）是最新成长方向，减少急诊室压力。矿业FIFO急救（工业急救员）是薪资最高的方向。",
}
I18N_EN = {
    "locale": "en", "name": "Paramedic",
    "summary": "Paramedics provide advanced life support, medication administration and patient transport at emergency scenes through state ambulance services, mining/industrial sites and community paramedicine programs.",
    "forecast_note": "JSA projects ~15% employment growth for paramedics by 2035. Ageing population (increased emergency call volume) and mining/remote emergency services expansion are key drivers.",
    "trend_summary": "Community paramedicine (reducing ED pressure) is the newest growth area. Mining/industrial FIFO paramedics command the highest salaries in the sector.",
}
EDUCATION = [
    {"stage": "Bachelor of Paramedicine（3年）", "duration": "3年（全日制）", "cost_min": 22000, "cost_max": 120000, "cost_note": "澳洲国际生约 $35,000~$40,000/年；政府补贴名额约 $6,000~$8,000/年", "sort_order": 0},
    {"stage": "海外资历评估（PA + AHPRA注册）", "duration": "6~18个月", "cost_min": 1500, "cost_max": 5000, "cost_note": "含 Paramedicine Board of Australia 评估和AHPRA注册费", "sort_order": 1},
    {"stage": "州/领地救护车服务培训（Graduate Paramedic）", "duration": "1~2年（有薪）", "cost_min": 0, "cost_max": 0, "cost_note": "通过AHPRA注册后，各州救护车服务提供带薪临床培训期", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Paramedicine", "issuer": "认可大学", "note": "AHPRA注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Paramedic Registration", "issuer": "AHPRA / Paramedicine Board of Australia", "note": "2018年起全国统一注册，强制要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Advanced Care Paramedic (ACP) 资质", "issuer": "各州救护车服务", "note": "晋升高级急救的进阶资质，薪资显著提升", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Industrial/Mining Paramedic 资质", "issuer": "ITLS / AHA / 各认可机构", "note": "进入矿业FIFO急救领域的专科资质", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 400,  "count_max": 900,  "note": "全国，含州救护车服务、矿业FIFO急救和社区急救岗"},
    {"platform": "Indeed",   "count_min": 250,  "count_max": 600,  "note": "含兼职和合同工"},
    {"platform": "LinkedIn", "count_min": 100,  "count_max": 300,  "note": "偏高级急救和工业急救岗"},
]
SALARIES = [
    {"experience": "新注册急救人员（Graduate Paramedic）", "salary_min": 65000, "salary_max": 80000, "salary_note": "州救护车服务起薪，含轮班津贴", "sort_order": 0},
    {"experience": "中级急救人员（2~8年）", "salary_min": 80000, "salary_max": 110000, "salary_note": "SEEK 区间 $105k~$125k（含津贴）；基本薪约 $80k~$100k", "sort_order": 1},
    {"experience": "高级急救人员（ACP/MICA，8年+）", "salary_min": 110000, "salary_max": 140000, "salary_note": "高级急救资质后薪资显著提升", "sort_order": 2},
    {"experience": "矿业/工业FIFO急救员", "salary_min": 120000, "salary_max": 200000, "salary_note": "矿业FIFO急救是急救类薪资最高方向，含夜班和远程津贴", "sort_order": 3},
    {"experience": "农村/偏远地区急救人员", "salary_min": 88000, "salary_max": 125000, "salary_note": "偏远地区津贴和住房补贴，实际待遇好于城市", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，急救人员为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，农村急救服务优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区急救，提名加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "急救医学、药理学和高压临床操作综合要求高"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3年+培训期1~2年，比医学学位短很多"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "AHPRA注册+州救护车服务培训，2018年后全国统一标准"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "老龄化+矿业FIFO+偏远急救三重需求，MLTSSL在列"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "AHPRA注册后就业相对容易，矿业FIFO急救尤其短缺"},
    {"dimension": "work_intensity",           "label_zh": "极高", "stars": 5, "note": "24小时轮班、高压紧急现场和情绪劳动，职业倦怠风险高"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "基本薪 $80k~$110k；矿业FIFO急救 $120k~$200k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 4, "note": "老龄化+社区急救改革+矿业扩张三重驱动"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "紧急现场判断、体力操作和患者稳定是AI无法替代的核心"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，189/190/491/482多路径，农村急救优先"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "AHPRA注册+州培训期约1~3年，海外急救资质互认流程较复杂"},
]
SUITABILITY_FIT = ["已持有国内急救/急诊医疗技术学位（3年制以上）", "英语能力达到 OET B / IELTS 7.0", "体力好、心理承受能力强，适应高压紧急环境", "接受轮班和农村/矿业FIFO就业", "目标是矿业工业急救（$120k~$200k高薪路径）"]
SUITABILITY_UNFIT = ["心理承受能力弱，无法应对高压紧急场景和死亡事件", "英语能力较弱，AHPRA注册困难", "体力条件不达标（急救现场需要体力搬运患者）"]
SOURCES = [
    {"source_name": "AHPRA / Paramedicine Board", "content": "急救人员注册要求（2018年起全国统一）", "url": "https://www.paramedicineboard.gov.au/"},
    {"source_name": "Paramedics Australasia", "content": "急救行业协会和职业信息", "url": "https://www.paramedics.org/"},
    {"source_name": "SEEK AU", "content": "急救人员薪资区间 $105k~$125k（2026，含津贴）", "url": "https://www.seek.com.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲急救人员工资多少？", "answer": "中级急救人员（含轮班津贴）约 $80,000~$110,000；高级急救 $110k~$140k；矿业FIFO工业急救员约 $120,000~$200,000（是急救类薪资最高方向）。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲急救人员容易找工作吗？", "answer": "容易。AHPRA注册后各州救护车服务和矿业公司主动招募，农村和矿业地区尤为短缺。矿业FIFO急救员通常可立即入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国急救资质澳洲认可吗？", "answer": "不直接认可。需申请AHPRA Paramedicine Board评估，2018年后澳洲建立全国统一注册制度。海外急救资质互认流程较复杂，建议提前联系评估机构。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "急救人员会被AI替代吗？", "answer": "替代风险极低。紧急现场的即时判断、体力急救操作（CPR/气管插管）和患者心理安抚是AI无法替代的核心职能。AI主要用于调度优化和数据记录。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲急救人员有年龄限制吗？", "answer": "无法律上限，但体力要求较高，定期体能测试是部分雇主要求。矿业FIFO通常偏好40岁以下，州救护车服务对年龄无明显限制。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲急救人员需要什么学历？", "answer": "需要急救医学学位（Bachelor of Paramedicine，3年制）。2018年后AHPRA全国统一注册，本科学位是强制要求。国内急救医疗技术本科（3年制）可申请评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲急救人员认证难吗？", "answer": "难度中高。AHPRA注册+州救护车服务培训期约1~3年。主要难点是高压临床环境适应、英语能力（OET B）和体能测试。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "急救人员和注册护士哪个更适合技术移民澳洲？", "answer": "护士就业量更大（Seek ~10,000+ vs 急救 ~700），薪资相近。急救人员矿业FIFO路径薪资最高可达 $200k，但工作压力和情绪劳动远高于护士。体力好且不怕高压环境者选急救，否则选护士。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 急救人员数据入库完成")

if __name__ == "__main__":
    run()
