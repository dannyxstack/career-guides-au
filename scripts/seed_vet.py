"""澳洲兽医（234711）数据入库。数据来源：JSA、AVA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "234711", "anzsco_title": "Veterinarian",
    "category": "医疗健康", "workforce_size": 14000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Small Animal/Pet Clinic","Emergency & Specialist Vet","Rural & Large Animal Vet","Livestock Export & Biosecurity","Aquaculture & Wildlife Vet"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "兽医",
    "summary": "兽医负责宠物、农场牲畜和野生动物的医疗诊断、治疗和预防保健。澳大利亚宠物经济快速增长和农村大型动物兽医严重短缺推动需求持续上升，是MLTSSL在列的紧缺职业。",
    "forecast_note": "JSA 预测兽医至2035年就业增长约20%。宠物人文化趋势（COVID后宠物拥有量增加25%）和农村大型动物兽医严重短缺是主要驱动力。",
    "trend_summary": "宠物主人越来越愿意为宠物支付专科治疗费用（肿瘤、骨科、心脏病），推高专科兽医薪资。农村大型动物兽医极度短缺，享PR快速通道。",
}
I18N_EN = {
    "locale": "en", "name": "Veterinarian",
    "summary": "Veterinarians diagnose and treat animals including pets, livestock and wildlife. Australia's booming pet economy and critical rural/large-animal vet shortage sustain strong demand. Listed on MLTSSL.",
    "forecast_note": "JSA projects ~20% employment growth for vets by 2035. Post-COVID pet ownership surge (+25%) and acute rural large-animal vet shortage are the primary drivers.",
    "trend_summary": "Pet humanisation drives specialist veterinary growth (oncology, orthopaedics, cardiology). Rural large-animal vets face critical shortages and have fast-tracked PR pathways.",
}
EDUCATION = [
    {"stage": "Doctor of Veterinary Medicine / BVSc（5~6年）", "duration": "5~6年（全日制）", "cost_min": 30000, "cost_max": 300000, "cost_note": "澳洲国际生约 $50,000~$60,000/年；政府补贴名额学费约 $9,000/年", "sort_order": 0},
    {"stage": "海外资历评估（AVBC + AHPRA注册）", "duration": "6~18个月", "cost_min": 2000, "cost_max": 8000, "cost_note": "含 Australasian Veterinary Boards Council 评估费和AHPRA注册费", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "BVSc / Doctor of Veterinary Medicine", "issuer": "认可大学", "note": "AHPRA/AVBC注册基础学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Veterinarian Registration", "issuer": "AHPRA / 各州兽医委员会", "note": "全国统一注册，部分州由专属机构管理", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "AVBC（Australasian Veterinary Boards Council）评估", "issuer": "AVBC", "note": "海外兽医学历评估，确认是否达到澳洲标准", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "专科兽医资质（肿瘤/眼科/骨科等）", "issuer": "各专科学会", "note": "额外3~5年培训，薪资大幅提升", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 800,  "count_max": 1600, "note": "全国，含宠物诊所、大型动物、农村和急诊兽医岗"},
    {"platform": "Indeed",   "count_min": 500,  "count_max": 1000, "note": "含兼职和合同工"},
    {"platform": "LinkedIn", "count_min": 200,  "count_max": 500,  "note": "偏专科和科研岗"},
]
SALARIES = [
    {"experience": "新注册兽医（0~2年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "宠物诊所入门，含基本薪", "sort_order": 0},
    {"experience": "中级兽医（2~8年）", "salary_min": 90000, "salary_max": 130000, "salary_note": "Indeed 平均 $119,124；SEEK 区间 $90k~$130k（2026）", "sort_order": 1},
    {"experience": "资深兽医 / 诊所主任（8年+）", "salary_min": 130000, "salary_max": 200000, "salary_note": "持股诊所收益叠加，资深宠物兽医 $140k~$200k", "sort_order": 2},
    {"experience": "专科兽医（肿瘤/骨科/眼科）", "salary_min": 180000, "salary_max": 300000, "salary_note": "专科资质后薪资显著高于全科兽医", "sort_order": 3},
    {"experience": "农村/大型动物兽医", "salary_min": 100000, "salary_max": 160000, "salary_note": "农村短缺溢价明显，含住房/车辆补贴，实际待遇优于城市", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，兽医为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，农村大型动物兽医享优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区兽医服务，提名加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "兽医学位涵盖多种动物的医学知识，与人类医学难度相当"},
    {"dimension": "learning_duration",        "label_zh": "极长", "stars": 5, "note": "学位5~6年+AVBC评估约6~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "较高", "stars": 4, "note": "AVBC评估+AHPRA注册，海外兽医评估周期较长"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "宠物经济+农村大型动物双重短缺，MLTSSL在列"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "全国兽医极度短缺，注册后立即入职"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "急诊和农村兽医工作强度大，体力要求较高"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位数约 $90k~$130k；专科兽医 $180k~$300k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "宠物人文化+农村医疗需求，至少20年持续增长"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "动物医疗高度依赖体检、操作和主人沟通，AI替代率极低"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，农村大型动物兽医189/190/491均可快速通道"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "AVBC评估周期较长，海外兽医学历差异较大"},
]
SUITABILITY_FIT = ["已持有国内兽医学位（5~6年制），希望来澳执业", "英语能力达到 OET B / IELTS 7.0+", "喜欢动物，有耐心和爱心", "接受农村大型动物兽医（PR最快通道）", "目标是宠物诊所合伙人或专科兽医培训"]
SUITABILITY_UNFIT = ["对动物不感兴趣或有动物过敏", "英语能力较弱，难以通过AVBC评估", "无法接受农村或急诊兽医的高强度工作"]
SOURCES = [
    {"source_name": "AHPRA / Vet Boards", "content": "兽医注册要求", "url": "https://www.ahpra.gov.au/"},
    {"source_name": "AVBC", "content": "海外兽医学历评估", "url": "https://www.avbc.asn.au/"},
    {"source_name": "Indeed AU", "content": "兽医平均薪资 $119,124（2026）", "url": "https://au.indeed.com/career/veterinarian/salaries"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲兽医工资多少？", "answer": "中级兽医年薪约 $90,000~$130,000（Indeed平均$119,124）；农村大型动物兽医约 $100k~$160k（含补贴）；专科兽医（肿瘤/骨科）可达 $180k~$300k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲兽医容易找工作吗？", "answer": "极容易。宠物诊所和农村大型动物兽医均极度短缺，注册后几乎立即入职，农村兽医甚至提供住房和车辆补贴吸引人才。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国兽医学位澳洲认可吗？", "answer": "通过 AVBC（澳洲亚太兽医委员会）评估，确认学历标准后申请各州兽医委员会注册。周期约6~18个月，部分学校毕业生可直接注册。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "兽医会被AI替代吗？", "answer": "替代风险极低。动物无法表达症状，医生高度依赖体检和主人沟通。手术操作和情感支持是AI无法替代的核心服务。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲兽医有年龄限制吗？", "answer": "无执业年龄上限。农村大型动物兽医有一定体力要求，但城市宠物诊所对年龄无明显限制。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲兽医需要什么学历？", "answer": "需要兽医学位（BVSc或Doctor of Veterinary Medicine，通常5~6年制）。国内兽医学（5年制，双语）可申请AVBC评估。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲兽医认证难吗？", "answer": "难度中高。AVBC评估主要是学历审核（非高难度考试），但周期较长。英语要求（OET B/IELTS 7.0+）是最常见障碍。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "兽医和全科医生哪个更适合移民澳洲？", "answer": "全科医生薪资远高于兽医（$250k~$500k+ vs $90k~$160k），但认证更复杂（AMC vs AVBC）。有兽医学位者走兽医路径效率更高；有人类医学背景者走全科医生路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 兽医数据入库完成")

if __name__ == "__main__":
    run()
