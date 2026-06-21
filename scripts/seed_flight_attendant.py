"""澳洲航空乘务员（451711）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "451711", "anzsco_title": "Flight Attendant",
    "category": "其他", "workforce_size": 15000, "shortage_listed": 0,
    "growth_areas": json.dumps(["国际航线乘务员（亚太航线复苏）","商务舱/头等舱高端服务","私人包机乘务员（商务航空）","航空安全培训师","华语乘务员（亚太航线需求旺盛）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "航空乘务员",
    "summary": "航空乘务员负责航班客舱安全管理、旅客服务和应急响应，是民用航空运营的关键角色。澳洲航空业（Qantas/Virgin Australia/Jetstar等）全面复苏，亚太国际航线旅客量持续增长，具备普通话/粤语服务能力的华语乘务员在亚太航线上需求特别旺盛。",
    "forecast_note": "JSA预测航空乘务员就业至2030年增长约8%。澳洲-中国直航复苏和东南亚航线扩张是最大需求驱动力，Qantas旗舰远程航线（Project Sunrise悉尼-伦敦直飞）将创造更多高端乘务员需求。",
    "trend_summary": "澳洲国际航空市场COVID后强劲复苏，2026年旅客量超越2019年历史高点。Qantas、Virgin Australia持续扩大舰队规模，高峰期招募需求旺盛。亚太航线（日本/韩国/中国/东南亚）华语服务能力成为加分项，商务航空（私人包机）乘务员薪资显著高于商业航空。",
}
I18N_EN = {
    "locale": "en", "name": "Flight Attendant",
    "summary": "Flight attendants manage cabin safety, passenger service and emergency response — a critical role in civil aviation. Australia's aviation industry (Qantas/Virgin Australia/Jetstar etc.) has fully recovered, with Asia-Pacific international passenger volumes continuing to grow. Mandarin/Cantonese-speaking flight attendants are in particular demand on Asia-Pacific routes.",
    "forecast_note": "JSA projects ~8% flight attendant employment growth by 2030. The recovery of Australia-China direct flights and expansion of Southeast Asian routes are the biggest demand drivers. Qantas's long-haul Project Sunrise routes (Sydney-London direct) will create additional demand for premium cabin crew.",
    "trend_summary": "Australia's international aviation market has strongly recovered post-COVID, with 2026 passenger volumes surpassing 2019 historic highs. Qantas and Virgin Australia continue fleet expansion with peak recruitment demand. Mandarin/Cantonese language skills are an advantage on Asia-Pacific routes. Business aviation (private charter) crew earn significantly more than commercial airline crew.",
}
EDUCATION = [
    {"stage": "高中或以上学历（必须）", "duration": "—", "cost_min": 0, "cost_max": 0, "cost_note": "各大航空公司要求高中毕业（Year 12）以上", "sort_order": 0},
    {"stage": "航空公司内部乘务员培训（约6~8周）", "duration": "6~8周", "cost_min": 0, "cost_max": 0, "cost_note": "通过航空公司招募后由公司提供，无需自费", "sort_order": 1},
    {"stage": "Certificate III in Aviation（Cabin Crew，可选）", "duration": "6~12个月", "cost_min": 3000, "cost_max": 10000, "cost_note": "部分私立航空学院提供，可提升求职竞争力，但非硬性要求", "sort_order": 2},
    {"stage": "急救证书（First Aid/CPR）", "duration": "1~2天", "cost_min": 100, "cost_max": 300, "cost_note": "航空公司招募的实际前提条件", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "CASA 认可的乘务员资格（Cabin Crew Attestation）", "issuer": "民用航空安全局（CASA）", "note": "澳洲乘务员上岗前必须持有CASA颁发的资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "急救证书（First Aid / CPR）", "issuer": "St John Ambulance等认可机构", "note": "所有航空公司的硬性要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "有效护照（国际航线）", "issuer": "—", "note": "国际航线乘务员的硬性要求", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "背景调查无犯罪记录（ASIC航空安全证件）", "issuer": "Department of Home Affairs", "note": "澳洲所有机场工作人员的硬性安全要求", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 200, "count_max": 600, "note": "全国，Qantas/Virgin/Jetstar/Regional Express等航空公司"},
    {"platform": "Indeed",   "count_min": 150, "count_max": 400, "note": "含航空公司官网直招和乘务员代理公司"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 300, "note": "国际航空公司和商务航空公司招募"},
]
SALARIES = [
    {"experience": "初级乘务员（0~2年）", "salary_min": 58000, "salary_max": 68000, "salary_note": "SEEK 起薪约 $60k~$70k；Indeed 全国均值 $63,669（2026）", "sort_order": 0},
    {"experience": "有经验乘务员（2~8年）", "salary_min": 65000, "salary_max": 82000, "salary_note": "含飞行津贴和过夜补贴；Qantas中级乘务员年薪约 $75k~$85k", "sort_order": 1},
    {"experience": "高级/乘务长（Purser，8年+）", "salary_min": 80000, "salary_max": 110000, "salary_note": "Qantas乘务长（Senior Cabin Crew）年薪约 $85k~$105k", "sort_order": 2},
    {"experience": "商务航空/私人包机乘务员", "salary_min": 90000, "salary_max": 140000, "salary_note": "商务包机乘务员薪资显著高于商业航空，含高端服务奖金", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，航空公司可担保；华语乘务员最常见路径", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，在澳洲工作满3年后可申请", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要Vetassess技能评估，邀请分数要求高", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道，昆士兰等州有提名", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中低", "stars": 2, "note": "技术门槛不高，但需要出色的应急处置、服务意识和人际沟通能力"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "航空公司培训约6~8周；实践积累比学历更重要"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CASA资质和航空公司安全审核是门槛；身高/体重和健康要求需满足"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "航空业复苏推动需求，但岗位总量有限；华语乘务员需求相对旺盛"},
    {"dimension": "competition",              "label_zh": "较高", "stars": 4, "note": "热门职业，竞争激烈；Qantas一次招募往往有数千人申请"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "倒时差、不规律作息、长途飞行体力消耗大；应急处置责任重"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "初级 $58k~$68k；乘务长 $80k~$110k；收入含多种津贴补贴"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "航空业扩张提供增长；亚太航线和商务航空方向前景较好"},
    {"dimension": "ai_risk",                  "label_zh": "很低", "stars": 1, "note": "安全管理、应急响应和人性化客舱服务是AI无法替代的核心价值"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL；雇主担保482可行；华语乘务员被担保机会更高"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "非短缺职业，技术移民难度中等；雇主担保是主要路径"},
]
SUITABILITY_FIT = ["英语沟通流利，有服务业或酒店业工作经验，形象气质良好", "普通话/粤语流利，有意向在亚太航线（中国/东南亚方向）任职", "身体健康，满足航空公司身高/体重要求，能适应不规律作息和长途飞行", "具备急救资质（First Aid/CPR）或愿意在就职前取得", "有在澳洲合法工作的签证状态（公民/PR/雇主担保类签证）"]
SUITABILITY_UNFIT = ["不能适应高频倒时差、长途夜间飞行和周末节假日不规律工作安排", "期望通过乘务员职业快速获得技术移民（非MLTSSL，移民难度中等）", "身体或健康状况不符合CASA和航空公司的医疗适航要求"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "乘务员薪资 $60k~$70k（2026）", "url": "https://au.seek.com/career-advice/role/flight-attendant/salary"},
    {"source_name": "Indeed AU", "content": "乘务员均值 $63,669（2026）", "url": "https://au.indeed.com/career/flight-attendant/salaries"},
    {"source_name": "Qantas Careers", "content": "Qantas乘务员招募信息和薪资（2026）", "url": "https://www.qantasgroup.com/careers"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲航空乘务员工资多少？", "answer": "初级乘务员约 $58,000~$68,000（SEEK $60k~$70k；Indeed $63,669）；有经验乘务员约 $65k~$82k；Qantas乘务长约 $85k~$105k；商务包机乘务员 $90k~$140k。薪资含飞行津贴和过夜补贴。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲航空乘务员容易找工作吗？", "answer": "竞争激烈。航空业复苏推动招募需求，但每次招募吸引大量申请者。华语（普通话/粤语）乘务员在亚太航线上相对容易获得机会，特别是中国大陆直航复苏后需求增加。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国航空乘务经验澳洲认可吗？", "answer": "国内经验对求职有帮助（大型航空公司服务标准相通），但需要满足澳洲CASA资质要求并通过航空公司的本地培训。英语沟通能力是主要评估维度，中文能力是亚太航线的额外优势。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "航空乘务员会被AI替代吗？", "answer": "风险极低。客舱安全管理、应急疏散、医疗急救处置和人性化乘客服务是AI无法替代的。自动化主要影响机场地面服务（值机/行李托运），不影响客舱乘务岗位。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲航空乘务员有年龄限制吗？", "answer": "Qantas等主要航空公司无明确年龄上限，但18岁以上方可申请。商务航空（私人包机）有时偏好有经验的成熟乘务员。体能要求（搬运应急设备）在任何年龄段都需满足。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲航空乘务员需要什么学历？", "answer": "主要航空公司要求高中毕业（Year 12），无需大学学历。最重要的要求是CASA资质、流利英语、服务意识和健康状况。Certificate III in Aviation（Cabin Crew）可提升竞争力但非硬性要求。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲航空乘务员移民难吗？", "answer": "乘务员不在MLTSSL，技术移民难度中等。雇主担保482是最可行路径，华语乘务员被担保机会相对更高。建议先以其他合法签证入境澳洲，直接向航空公司申请，获得录用后由公司担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "航空乘务员和酒店服务业哪个澳洲发展更好？", "answer": "薪资相近（乘务员 $65k~$82k vs 酒店前台经理 $65k~$82k），但乘务员含飞行津贴实际收入通常更高。生活方式差异大：乘务员经常出行旅行但作息不规律；酒店服务相对稳定。有旅行爱好和语言优势的人选乘务员；偏好稳定工作的选酒店管理路径。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 航空乘务员数据入库完成")

if __name__ == "__main__":
    run()
