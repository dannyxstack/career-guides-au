"""澳洲平面设计师（232411）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "232411", "anzsco_title": "Graphic Designer",
    "category": "创意/媒体", "workforce_size": 55000, "shortage_listed": 0,
    "growth_areas": json.dumps(["UI/UX设计（数字产品设计）","品牌策略与视觉识别系统","内容营销视觉设计","运动图形与视频内容设计","AR/VR沉浸式体验设计"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "平面设计师",
    "summary": "平面设计师为企业、媒体和个人客户创作视觉传播材料，包括品牌标识、营销物料、数字内容和印刷品。数字营销爆发推动对多平台内容设计师（平面+数字）的持续需求。技能全面（Adobe CC + Figma + 视频基础）的设计师竞争力显著提升。",
    "forecast_note": "JSA预测平面设计师就业至2030年保持稳定，数字内容设计和UI/UX融合技能方向增长最快。纯印刷设计市场收缩，数字多媒体设计方向持续增长。",
    "trend_summary": "澳洲数字营销市场持续增长（2026年超过$130亿澳元），推动对视觉内容设计师的旺盛需求。AI设计工具（Midjourney/Adobe Firefly）改变初级设计任务，但品牌策略、创意概念和客户沟通不可替代。Figma成为UI/UX和平面设计的行业标准。",
}
I18N_EN = {
    "locale": "en", "name": "Graphic Designer",
    "summary": "Graphic designers create visual communication materials for businesses, media and individual clients, including brand identity, marketing collateral, digital content and print. The digital marketing boom drives sustained demand for multi-platform content designers (print + digital). Designers with broad skills (Adobe CC + Figma + video basics) have significantly stronger competitiveness.",
    "forecast_note": "JSA projects stable graphic designer employment through 2030, with digital content design and UI/UX hybrid skills growing fastest. Pure print design market is contracting while digital multimedia design continues to grow.",
    "trend_summary": "Australia's digital marketing market continues to expand (over $13B AUD by 2026), driving strong demand for visual content designers. AI design tools (Midjourney/Adobe Firefly) are changing junior design tasks, but brand strategy, creative concepts and client communication remain irreplaceable. Figma has become the industry standard for UI/UX and graphic design.",
}
EDUCATION = [
    {"stage": "Bachelor of Design / Visual Communication（3年）", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 120000, "cost_note": "国际生约 $28,000~$36,000/年；部分私立艺术学院课程2~3年", "sort_order": 0},
    {"stage": "Diploma of Graphic Design（TAFE，1~2年）", "duration": "1~2年", "cost_min": 5000, "cost_max": 30000, "cost_note": "TAFE文凭是入门路径；技能型岗位雇主接受文凭+作品集", "sort_order": 1},
    {"stage": "作品集（Portfolio）建设", "duration": "持续", "cost_min": 0, "cost_max": 5000, "cost_note": "作品集质量比学历更重要；Behance/个人网站是标配展示平台", "sort_order": 2},
    {"stage": "Adobe CC / Figma / After Effects 技能认证", "duration": "自主学习，3~12个月", "cost_min": 0, "cost_max": 3000, "cost_note": "Adobe Certified Professional认证提升竞争力", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Design / Graphic Design", "issuer": "澳洲高校或等同国际学历", "note": "大型广告公司和品牌设计机构的基本学历要求", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Adobe Certified Professional（ACP）", "issuer": "Adobe", "note": "Adobe官方认证，提升简历竞争力", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Figma / UI Design 技能证明", "issuer": "Figma / Coursera / LinkedIn Learning", "note": "数字设计岗位事实上的技能要求", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 1000, "count_max": 3000, "note": "全国，含品牌设计/数字内容/UI设计师岗"},
    {"platform": "Indeed",   "count_min": 800, "count_max": 2500, "note": "含广告公司、品牌设计机构和内部设计岗"},
    {"platform": "LinkedIn", "count_min": 1500, "count_max": 4000, "note": "企业内部设计师和数字营销设计岗招聘活跃"},
]
SALARIES = [
    {"experience": "初级平面设计师（0~2年）", "salary_min": 52000, "salary_max": 68000, "salary_note": "毕业生起薪；悉尼/墨尔本较偏远地区略高", "sort_order": 0},
    {"experience": "中级平面设计师（2~6年）", "salary_min": 70000, "salary_max": 88000, "salary_note": "SEEK 区间 $75k~$85k；Indeed 均值 $78,126；Glassdoor 均值 $77,250（2026）", "sort_order": 1},
    {"experience": "高级平面设计师（6~12年）", "salary_min": 88000, "salary_max": 110000, "salary_note": "高级设计师均值 $90,929；品牌策略专精可超 $100k", "sort_order": 2},
    {"experience": "创意总监 / 设计总监（12年+）", "salary_min": 110000, "salary_max": 180000, "salary_note": "大型广告公司或品牌创意总监；悉尼创意总监均值 $120k~$150k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，广告公司和设计机构可担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要技能评估（VETASSESS）", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要美学基础+软件技能+商业思维，作品集建设是核心挑战"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "B.Design 3年；Diploma 1~2年；技能型自学路径约1~2年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "VETASSESS评估难度中等；作品集质量是关键"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "数字营销方向需求稳定；纯印刷设计方向市场收缩"},
    {"dimension": "competition",              "label_zh": "较高", "stars": 4, "note": "初级设计师竞争激烈；有UI/UX融合技能者竞争优势显著"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "项目截止期前强度高；广告公司加班文化较浓"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "中级 $70k~$88k；整体薪资低于IT/工程类；创意总监例外"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "AI影响初级任务，但品牌策略和创意方向有稳定需求"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI工具已影响初级图片生成和模板设计，但品牌策略和创意判断抗AI"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL，雇主担保482和189技能移民均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "不在短缺职业清单，邀请分数要求较高；雇主担保是更可行路径"},
]
SUITABILITY_FIT = ["持有设计类学历，有专业作品集（品牌/数字媒体/UI设计方向）", "熟练掌握Adobe Creative Suite（Ps/Ai/Id/Ae）和Figma", "有商业品牌或数字营销项目经验（不只是艺术创作）", "英语沟通和汇报能力强（客户简报和创意方向确认）", "有UI/UX基础或愿意向数字产品设计方向发展"]
SUITABILITY_UNFIT = ["仅有纯艺术/手工艺背景，无商业设计项目经验", "软件技能单一（仅掌握Photoshop），无Figma或动态设计能力", "期望快速获得 $90k+ 薪资（需要5年以上资深经验才能达到）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "平面设计师薪资 $75k~$85k（2026）", "url": "https://au.seek.com/career-advice/role/graphic-designer/salary"},
    {"source_name": "Indeed AU", "content": "平面设计师平均薪资 $78,126（2026）", "url": "https://au.indeed.com/career/graphic-designer/salaries"},
    {"source_name": "Glassdoor AU", "content": "平面设计师平均薪资 $77,250（2026）", "url": "https://www.glassdoor.com.au/Salaries/graphic-designer-salary-SRCH_KO0,16.htm"},
    {"source_name": "Academy Xi", "content": "澳洲平面设计师市场薪资2026", "url": "https://academyxi.com/blogs/market-update-how-much-do-graphic-designers-earn-in-australia-2026/"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲平面设计师工资多少？", "answer": "中级设计师约 $70,000~$88,000（SEEK $75k~$85k；Indeed $78,126；Glassdoor $77,250）；高级设计师约 $88k~$110k；创意总监约 $110k~$180k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲平面设计师容易找工作吗？", "answer": "有一定难度。初级设计师竞争激烈，但有数字营销和UI/UX融合技能的设计师供不应求。SEEK 挂牌约 1,000~3,000 个职位，数字内容和品牌设计方向需求持续稳定。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国设计学历澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国设计专业本科学历通常可以认可。关键是作品集质量：澳洲雇主更看重实际商业项目作品集而非纯艺术作品。建议准备5~10个商业品牌或数字营销项目案例。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "平面设计师会被AI替代吗？", "answer": "部分风险。AI工具（Midjourney、Adobe Firefly）已能处理初级图片生成和模板设计。但品牌策略制定、客户沟通和创意概念提案仍需要人类设计师。向品牌策略、UI/UX和内容策略方向发展可有效规避AI风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲平面设计师有年龄限制吗？", "answer": "无。有丰富品牌策略和商业设计经验的中高级设计师（35~50岁）在创意总监和品牌顾问岗位上有明显优势。创意行业更看重作品组合和客户资源。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲平面设计师需要什么学历？", "answer": "大企业和广告公司通常要求设计类本科学历；中小型设计机构和初创公司更注重作品集。TAFE文凭+强作品集可以进入中小公司，但大型品牌公司仍偏好本科及以上学历。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲平面设计师认证（移民）难吗？", "answer": "不在MLTSSL短缺职业清单，移民难度高于教育/医疗类。雇主担保482是最可行路径；189技术移民需要VETASSESS评估+足够邀请分数。建议先通过学生签证在澳就读并积累工作经验。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "平面设计师和UI/UX设计师哪个更好？", "answer": "UI/UX设计师薪资更高（$90k~$130k vs 平面 $70k~$88k），需求更强，移民路径更清晰（有时被归入IT类）；平面设计师就业范围更广（任何行业都需要），但薪资整体偏低。有技术倾向者转型UI/UX，有品牌和创意倾向者深耕平面/品牌策略。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 平面设计师数据入库完成")

if __name__ == "__main__":
    run()
