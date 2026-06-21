"""澳洲摄影师（211212）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "211212", "anzsco_title": "Photographer",
    "category": "创意/媒体", "workforce_size": 18000, "shortage_listed": 0,
    "growth_areas": json.dumps(["商业产品摄影（电商平台）","企业品牌与活动摄影","地产摄影（空中无人机摄影）","视频拍摄与剪辑（摄影+视频融合）","户外/旅游商业摄影"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "摄影师",
    "summary": "摄影师为企业、媒体和个人客户提供商业、新闻、婚庆和艺术摄影服务。澳洲电商爆发（产品摄影需求暴增）和企业品牌建设推动对商业摄影师的持续需求。自由职业摄影师（Freelance）比例极高，多数通过多平台接单（Airtasker/Instagram/商业直客）经营个人工作室。",
    "forecast_note": "JSA预测摄影师就业至2030年基本稳定，自由职业比例高达60%以上。商业/电商摄影方向增长，传统新闻摄影岗位因媒体行业收缩而减少。无人机摄影（地产和旅游）是增速最快的细分方向。",
    "trend_summary": "澳洲电商市场（2026年超 $650亿）持续推动电商产品摄影需求。智能手机摄影提升了消费级摄影质量，压缩了低端市场；但专业商业摄影（品牌大片、活动摄影、建筑/地产航拍）仍需专业摄影师。AI图片生成工具对部分库存图片市场有冲击。",
}
I18N_EN = {
    "locale": "en", "name": "Photographer",
    "summary": "Photographers provide commercial, news, wedding and artistic photography services for businesses, media and individuals. The Australian e-commerce boom (surging product photography demand) and corporate branding drive sustained demand for commercial photographers. The freelance proportion is very high — most photographers run personal studios through multi-platform client acquisition (Airtasker/Instagram/direct commercial).",
    "forecast_note": "JSA projects broadly stable photographer employment through 2030 with over 60% freelance. Commercial/e-commerce photography is growing while traditional news photography positions decline with media industry contraction. Drone photography (real estate and tourism) is the fastest-growing niche.",
    "trend_summary": "Australia's e-commerce market (over $65B by 2026) continues to drive e-commerce product photography demand. Smartphone photography has raised consumer-grade quality and compressed the low-end market, but professional commercial photography (brand campaigns, events, architectural/real estate aerial) still requires specialists. AI image generation tools are impacting some stock photo markets.",
}
EDUCATION = [
    {"stage": "Bachelor of Photography / Fine Arts Photography（3年）", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 100000, "cost_note": "大学摄影学位；国际生约 $25,000~$35,000/年", "sort_order": 0},
    {"stage": "Diploma of Photography（TAFE/私立学院，1~2年）", "duration": "1~2年", "cost_min": 5000, "cost_max": 25000, "cost_note": "实践型摄影技术文凭，是许多商业摄影师的入门路径", "sort_order": 1},
    {"stage": "无人机驾驶执照（RePL，远程飞行员执照）", "duration": "1~3天考试+理论学习", "cost_min": 1500, "cost_max": 4000, "cost_note": "商业无人机航拍摄影的法律要求（CASA监管）", "sort_order": 2},
    {"stage": "摄影软件技能（Adobe Lightroom/Photoshop）", "duration": "自主学习", "cost_min": 0, "cost_max": 2000, "cost_note": "后期处理是商业摄影师核心技能", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "远程飞行员执照（RePL）", "issuer": "CASA（澳洲民用航空安全局）", "note": "商业无人机航拍的法律要求，地产和旅游摄影高附加值技能", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Australian Institute of Professional Photography (AIPP) 会员", "issuer": "AIPP", "note": "澳洲专业摄影师协会会员资格，提升商业信誉", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "公共责任保险（Public Liability Insurance）", "issuer": "保险公司", "note": "商业摄影接单的实际必要条件，通常约 $600~$1,200/年", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 300, "count_max": 800, "note": "全国，全职摄影师岗较少，多为合同/自由职业"},
    {"platform": "Indeed",   "count_min": 200, "count_max": 600, "note": "含企业摄影师和媒体摄影岗"},
    {"platform": "LinkedIn", "count_min": 300, "count_max": 800, "note": "企业内部摄影师和媒体机构岗"},
]
SALARIES = [
    {"experience": "助理摄影师 / 初级（0~2年）", "salary_min": 50000, "salary_max": 65000, "salary_note": "助理摄影师或摄影工作室助理的全职薪资", "sort_order": 0},
    {"experience": "有经验摄影师（2~8年，含自由职业）", "salary_min": 65000, "salary_max": 90000, "salary_note": "SEEK 区间 $70k~$80k；Indeed 均值约 $93,800（$45.14/hr × 2080h，2026）", "sort_order": 1},
    {"experience": "商业/品牌摄影师（5~12年）", "salary_min": 85000, "salary_max": 130000, "salary_note": "企业品牌摄影、地产航拍摄影收入区间；自由职业高峰年收入可超 $130k", "sort_order": 2},
    {"experience": "知名商业/广告摄影师（10年+）", "salary_min": 120000, "salary_max": 300000, "salary_note": "广告大片摄影师按项目计费，年均收入差异极大", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，媒体机构和大型广告公司可担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要VETASSESS技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "技术技能（摄影参数/灯光/后期）+商业经营能力同等重要"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3年；文凭1~2年；自主学习+实践经验约2~3年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "VETASSESS评估；作品集质量是核心评判标准"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "商业和电商方向稳定需求；传统新闻摄影岗减少"},
    {"dimension": "competition",              "label_zh": "较高", "stars": 4, "note": "自由职业市场竞争激烈；专业商业摄影师供需相对平衡"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "婚庆和活动摄影周末高强度；商业摄影项目节奏相对可控"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "全职摄影师薪资 $65k~$90k；自由职业收入差异极大"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "AI图片生成冲击库存摄影，但现场商业摄影需求稳定"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI影响库存摄影和部分插图需求；现场活动/商业/建筑摄影不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "较低", "stars": 2, "note": "不在MLTSSL，移民路径难度高；全职受雇摄影师更容易获得担保"},
    {"dimension": "pr_difficulty",            "label_zh": "较高", "stars": 4, "note": "非短缺职业，189邀请分数要求高；雇主担保482是更可行路径"},
]
SUITABILITY_FIT = ["有系统摄影学习背景（学位/文凭），有高质量商业作品集", "商业摄影技能完整（布光、后期、与客户沟通）", "持有无人机执照（RePL）——地产/旅游摄影高附加值技能", "有在澳洲已有商业客户基础或媒体机构担保意向", "愿意以自由职业模式在澳洲经营个人摄影业务"]
SUITABILITY_UNFIT = ["仅有婚庆/人像摄影经验，无商业品牌或产品摄影项目经验", "期望通过摄影职业快速获得技术移民（非短缺职业，移民难度大）", "缺乏商业经营能力（摄影师的成功50%靠技术，50%靠营销和客户管理）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "摄影师薪资 $70k~$80k（2026）", "url": "https://au.seek.com/career-advice/role/photographer/salary"},
    {"source_name": "Indeed AU", "content": "摄影师平均时薪 $45.14（约 $93,800/年，2026）", "url": "https://au.indeed.com/career/photographer/salaries"},
    {"source_name": "CASA", "content": "无人机商业飞行执照要求", "url": "https://www.casa.gov.au/drones/fly-drone-commercially/commercial-operations"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲摄影师工资多少？", "answer": "有经验摄影师约 $65,000~$90,000（SEEK $70k~$80k）；Indeed 均值约 $93,800；商业/品牌摄影师约 $85k~$130k；知名广告摄影师年收入可超 $200k。自由职业收入差异极大，取决于客户资源和专长方向。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲摄影师容易找工作吗？", "answer": "全职岗位有限（SEEK 约300~800个）；自由职业市场更大但竞争激烈。商业/电商产品摄影和企业品牌摄影方向需求稳定；建议以自由职业+兼职全职结合的方式进入市场。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国摄影经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，有商业摄影作品集的摄影师可以申请评估。关键是高质量的商业项目作品集（品牌摄影/产品摄影/活动摄影），而非个人创作。澳洲商业摄影客户更看重专业经验和服务可靠性。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "摄影师会被AI替代吗？", "answer": "AI图片生成工具（Midjourney等）对库存摄影和部分插图市场有冲击；但现场活动摄影、商业产品摄影、建筑/地产摄影、人物摄影仍需专业摄影师。向商业/品牌/无人机摄影方向发展可有效规避AI风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲摄影师有年龄限制吗？", "answer": "无。有丰富商业客户关系的资深摄影师（40~55岁）在行业中非常有竞争力。澳洲商业摄影客户更看重专业信誉和作品质量，不受年龄影响。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲摄影师需要什么学历？", "answer": "学历在摄影行业不是硬性要求；作品集质量远比学历重要。但大型媒体机构和广告公司的全职摄影师岗位通常偏好有设计类本科学历者。TAFE文凭+专业作品集可以进入大多数商业摄影市场。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲摄影师认证（移民）难吗？", "answer": "难度较高（相对于医疗/教育类）。摄影不在MLTSSL短缺职业清单，雇主担保482是最可行的路径。建议先通过学生签证在澳就读，积累本地商业客户，再申请雇主担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "摄影师和视频制作人哪个澳洲发展更好？", "answer": "两者市场相近；视频制作需求增速略快于平面摄影（短视频营销爆发）。建议同时掌握摄影和视频拍摄/剪辑技能（摄影+视频二合一），大幅提升市场竞争力和收入上限。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 摄影师数据入库完成")

if __name__ == "__main__":
    run()
