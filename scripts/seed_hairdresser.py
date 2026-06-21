"""澳洲理发师/美容师（391111/411611）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "391111", "anzsco_title": "Hairdresser / Beauty Therapist",
    "category": "其他", "workforce_size": 55000, "shortage_listed": 1,
    "growth_areas": json.dumps(["华裔美发美容中心（中文服务客群旺盛）","高端发廊造型师（Colourist/先进染发技术）","美容治疗师（Skin Therapist/Laser Aesthetician）","美甲美睫（Nail Technician/Lash Artist）","美容经营者/发廊老板（小企业创业路径）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "理发师/美容师",
    "summary": "理发师为客户提供剪发、染发、造型和护发服务；美容师提供皮肤护理、美甲、美睫和体毛处理等美容治疗。澳洲美发美容行业规模约 $50亿（2026），华裔移民集中区（悉尼/墨尔本/布里斯班）对华语美发美容服务需求旺盛，是华裔创业和就业的传统优势行业之一。理发师和美容师均在澳洲MLTSSL技术短缺名单。",
    "forecast_note": "JSA预测美发美容职业就业至2030年增长约7%。人口增长（移民净增加）推动服务需求；高端发廊和皮肤美容诊所（医美类）是增速最快的细分方向。华裔聚集区对华语美发美容师的需求持续旺盛，是华人创业开店的成熟路径。",
    "trend_summary": "澳洲美发美容行业近年向两极分化：大型连锁平价发廊（Supercuts/Just Cuts）和高端专业发廊（精品造型师/先进染发）。皮肤医美（Laser/IPL治疗）和抗衰美容治疗市场快速增长。华裔美发师在华裔聚集区拥有稳定客群，创业开店（小投资额约 $30k~$80k）是常见成功路径。",
}
I18N_EN = {
    "locale": "en", "name": "Hairdresser / Beauty Therapist",
    "summary": "Hairdressers provide haircuts, colouring, styling and hair treatment services; beauty therapists provide skincare, nail, lash and hair removal treatments. Australia's hair and beauty industry is valued at ~$5B (2026), with strong demand for Mandarin/Cantonese-speaking beauty services in Chinese-immigrant communities (Sydney/Melbourne/Brisbane) — a traditional competitive advantage industry for Chinese-Australian employment and entrepreneurship. Both hairdressers and beauty therapists appear on the MLTSSL skills shortage list.",
    "forecast_note": "JSA projects ~7% beauty industry employment growth by 2030. Population growth (high net migration) drives service demand; premium salons and skin aesthetics clinics (medical-grade beauty) are the fastest-growing sub-sectors. Demand for Mandarin/Cantonese-speaking beauty professionals in Chinese communities remains strong — a well-established pathway for Chinese-Australian business ownership.",
    "trend_summary": "Australia's hair and beauty industry has bifurcated: large budget chains (Supercuts/Just Cuts) and premium boutique specialists (colour specialists/advanced colouring). Medical aesthetics (laser/IPL treatments) and anti-ageing beauty treatments are fast-growing markets. Chinese-Australian hairdressers in Chinese communities have stable clientele, with beauty salon ownership (modest investment of $30k–$80k) as a common successful pathway.",
}
EDUCATION = [
    {"stage": "Certificate III in Hairdressing（CUA30920）", "duration": "3年（含学徒期）", "cost_min": 3000, "cost_max": 15000, "cost_note": "行业标准资质；学徒制（在职培训+TAFE课程）；学徒期间有收入", "sort_order": 0},
    {"stage": "Certificate III in Beauty Services（SHB30115）", "duration": "12~18个月", "cost_min": 3000, "cost_max": 15000, "cost_note": "美容师基础资质；TAFE或私立美容学院提供", "sort_order": 1},
    {"stage": "Certificate IV in Beauty Therapy（高级美容）", "duration": "6~12个月（在Certificate III基础上）", "cost_min": 2000, "cost_max": 8000, "cost_note": "皮肤治疗/激光美容/电疗等高级技术；薪资溢价显著", "sort_order": 2},
    {"stage": "澳洲理发/美容执照（各州注册）", "duration": "完成培训后申请", "cost_min": 200, "cost_max": 600, "cost_note": "部分州要求注册；经营美容诊所需要相应资质", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Hairdressing（CUA30920）", "issuer": "TAFE / 认可RTO", "note": "独立从事理发工作的法定资质；技术移民评估的基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Certificate III in Beauty Services（SHB30115）", "issuer": "TAFE / 私立美容学院", "note": "美容师基础资质；Habia或ABIC会员资格", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Vetassess 技能评估（移民）", "issuer": "Vetassess", "note": "189/190/491技术移民的学历和经验评估机构", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "激光美容/IPL操作资质（医美方向）", "issuer": "各州医疗委员会认可机构", "note": "在澳洲开展激光和IPL美容治疗的法律要求", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600, "count_max": 2000, "note": "全国，含理发师/美容师/美甲师/皮肤治疗师各类岗"},
    {"platform": "Indeed",   "count_min": 400, "count_max": 1500, "note": "含大型连锁发廊、精品发廊和美容诊所"},
    {"platform": "LinkedIn", "count_min": 200, "count_max": 600, "note": "高端美容诊所和医美机构管理岗"},
]
SALARIES = [
    {"experience": "初级理发师/美容师（0~2年）", "salary_min": 55000, "salary_max": 68000, "salary_note": "学徒毕业起薪；含小费实际收入稍高", "sort_order": 0},
    {"experience": "有经验理发师（2~8年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "SEEK理发师 $70k~$80k；Indeed发型师均值 $69,178（2026）", "sort_order": 1},
    {"experience": "有经验美容师（2~8年）", "salary_min": 68000, "salary_max": 90000, "salary_note": "SEEK美容师 $75k~$80k；Indeed美容师均值 $74,405（2026）", "sort_order": 2},
    {"experience": "高级造型师/皮肤治疗师（6年+）", "salary_min": 85000, "salary_max": 120000, "salary_note": "高端发廊Colourist/医美激光治疗师薪资，大城市溢价显著", "sort_order": 3},
    {"experience": "发廊/美容院老板（创业）", "salary_min": 80000, "salary_max": 300000, "salary_note": "华裔聚集区自营发廊/美容院净利润区间（视经营规模）", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，MLTSSL在列；发廊和美容院担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，满3年后申请", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列；Vetassess评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名（NSW/VIC/SA等积极提名）", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区理发师/美容师极度短缺", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中低", "stars": 2, "note": "实操技术学习曲线陡峭；学徒制3年培训塑造核心技能"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "理发师学徒制3年；美容师Certificate III约12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Vetassess评估需要工作经验证明；中国证书转换有明确路径"},
    {"dimension": "job_demand",               "label_zh": "较高", "stars": 4, "note": "MLTSSL短缺职业；SEEK 600~2000+职位；华语市场需求旺盛"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "普通英语市场竞争中等；华语（普通话/粤语）市场竞争优势显著"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 3, "note": "站立工作、体力消耗中等；周末是旺季；客户服务要求高"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "有经验 $65k~$90k；自营发廊利润高但风险也高"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "稳定需求；高端和医美方向增速快；创业路径成熟"},
    {"dimension": "ai_risk",                  "label_zh": "很低", "stars": 1, "note": "理发美容是强手工技能服务，无法自动化；人际互动是核心价值"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列；偏远地区491路径容易；雇主担保482活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "MLTSSL短缺职业；PR路径多且顺畅；偏远491最快"},
]
SUITABILITY_FIT = ["已持有Certificate III in Hairdressing或Beauty Services（或正在学徒），有2年以上工作经验", "普通话/粤语流利，有意向在华裔聚集区工作或创业开店", "有高端造型技术（Balayage/Korean Beauty/皮肤治疗）或意愿学习医美技术（激光/IPL）", "有创业意愿，考虑以发廊/美容院作为长期创业目标（低启动资金的小生意路径）", "愿意在偏远地区（城区外）工作以加速PR（491偏远美发师短缺严重）"]
SUITABILITY_UNFIT = ["不喜欢长时间站立工作和直接客户服务互动（美发美容的日常工作本质）", "期望通过美发美容快速进入高薪白领职业（入门薪资偏低，需时间积累技术和客群）", "没有任何美发或美容培训背景，且不愿意进行学徒制或院校培训"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "理发师 $70k~$80k；美容师 $75k~$80k（2026）", "url": "https://au.seek.com/career-advice/role/hairdresser/salary"},
    {"source_name": "Indeed AU", "content": "发型师均值 $69,178；美容师均值 $74,405（2026）", "url": "https://au.indeed.com/career/hairdresser/salaries"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL理发师/美容师技能短缺信息", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲理发师/美容师工资多少？", "answer": "初级理发师/美容师约 $55k~$68k；有经验理发师约 $65k~$85k（SEEK $70k~$80k；Indeed $69,178）；有经验美容师约 $68k~$90k（SEEK $75k~$80k；Indeed $74,405）；高端造型师/皮肤治疗师约 $85k~$120k；自营发廊/美容院净利润 $80k~$300k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲理发师/美容师容易找工作吗？", "answer": "容易。MLTSSL短缺职业，SEEK 600~2000+职位。华语（普通话/粤语）美发美容师在华裔聚集区（Chatswood/Box Hill/Burwood）供不应求，往往直接被猎头。偏远地区理发师极度短缺（491路径最便捷）。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国美发/美容经验澳洲认可吗？", "answer": "通过Vetassess技能评估，中国美发或美容工作经验可以认可（需3年以上）。Certificate III是理想的补充资质（如无国内同等学历认可）。中国的韩式美容技术（皮肤管理/美甲/美睫）在澳洲华裔聚集区非常受欢迎。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "理发师/美容师会被AI替代吗？", "answer": "风险极低。理发和美容是高度依赖手工技能和人际互动的服务，物理层面无法自动化。AI可能改善预约管理和个性化推荐，但核心服务本身不受AI威胁。美发美容是公认的AI抗性最强的职业之一。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲理发师/美容师有年龄限制吗？", "answer": "无。有丰富技术积累和稳定客群的中高年龄美发美容师（40~55岁）在高端发廊和私人客户市场非常受欢迎。开设自营发廊或美容院也无年龄限制，经验越丰富管理能力越强。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲理发师/美容师需要什么资质？", "answer": "Certificate III in Hairdressing（3年学徒制）是理发师的行业标准；Certificate III/IV in Beauty Services是美容师基础资质。无需大学学历。最重要的是资质证书+实操技术+客户服务能力。医美方向（激光/IPL）需要额外的专业培训资质。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲理发师/美容师认证（移民）难吗？", "answer": "难度较低。理发师和美容师在MLTSSL，PR路径相对顺畅。偏远地区491路径是最快捷通道（乡镇理发师极度短缺）；雇主担保482也很活跃（发廊普遍担保有技术的华语理发师）。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "理发师和美容师哪个澳洲发展更好？", "answer": "理发师（$65k~$85k）和美容师（$68k~$90k）薪资相近，但美容向医美（激光/皮肤治疗）方向发展薪资溢价显著（$85k~$120k）。理发师技术学习曲线陡（学徒3年）；美容师资质获取较快（12~18个月）。两者均在MLTSSL，都有良好PR路径。有医美发展意愿选美容；有造型热情选理发。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 理发师/美容师数据入库完成")

if __name__ == "__main__":
    run()
