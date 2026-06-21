"""澳洲新闻记者（212111）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "212111", "anzsco_title": "Journalist",
    "category": "创意/媒体", "workforce_size": 12000, "shortage_listed": 0,
    "growth_areas": json.dumps(["数字媒体内容记者","播客与音频新闻","数据新闻（Data Journalism）","视频新闻（Video Journalism/VJ）","自媒体与企业媒体（内容营销记者）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "新闻记者",
    "summary": "新闻记者为媒体机构采写报道、制作内容，覆盖时事、商业、体育、文化等领域。澳洲传统媒体（Nine/News Corp/ABC等）面临数字化转型压力，记者岗位从纸质媒体向数字媒体、播客和视频新闻转移。有多媒体技能（文字+视频+社交媒体）的记者竞争力最强；自媒体和企业内容方向提供额外机会。",
    "forecast_note": "JSA预测记者就业至2030年整体下降约5%。传统印刷媒体岗位继续收缩，但数字新闻、播客和企业内容方向提供新增就业。独立记者和自媒体创作者数量增加。",
    "trend_summary": "澳洲媒体行业持续重组（大型集团缩减编辑部规模），但数字新闻订阅模式（如The Australian Digital、AFR付费墙）稳定了部分岗位。企业内容营销对具备新闻写作能力的内容创作者需求旺盛。AI写作工具影响结构化新闻（财经数据、体育简报），但深度报道和调查性新闻不可替代。",
}
I18N_EN = {
    "locale": "en", "name": "Journalist",
    "summary": "Journalists write reports and create content for media organisations covering news, business, sport, culture and more. Australian traditional media (Nine/News Corp/ABC etc.) face digital transformation pressure, with journalist roles shifting from print to digital media, podcasts and video journalism. Journalists with multimedia skills (text + video + social media) are most competitive; independent media and corporate content directions provide additional opportunities.",
    "forecast_note": "JSA projects ~5% overall decline in journalist employment by 2030. Traditional print media positions continue to shrink, but digital news, podcasts and corporate content directions are creating new employment. The number of independent journalists and personal media creators is increasing.",
    "trend_summary": "Australia's media industry continues restructuring (major groups reducing editorial headcount), but digital news subscription models (e.g., The Australian Digital, AFR paywall) have stabilised some roles. Corporate content marketing has strong demand for content creators with journalism writing skills. AI writing tools are affecting structured journalism (financial data, sports briefs) but in-depth reporting and investigative journalism remain irreplaceable.",
}
EDUCATION = [
    {"stage": "Bachelor of Journalism / Media and Communications（3年）", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 110000, "cost_note": "UTS、莫纳什、昆士兰大学等澳洲顶尖新闻院校；国际生约 $25,000~$35,000/年", "sort_order": 0},
    {"stage": "Graduate Diploma of Journalism（1年，已有本科学位者）", "duration": "1年（研究生文凭）", "cost_min": 15000, "cost_max": 35000, "cost_note": "快速转换入行路径", "sort_order": 1},
    {"stage": "实习经历和作品集（Clips）建设", "duration": "持续", "cost_min": 0, "cost_max": 2000, "cost_note": "发表的新闻报道（Clips）是求职的核心证明材料", "sort_order": 2},
    {"stage": "多媒体技能（视频采制/播客制作/数据可视化）", "duration": "自主学习", "cost_min": 0, "cost_max": 3000, "cost_note": "现代新闻记者的必备拓展技能", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Media Entertainment and Arts Alliance (MEAA) 会员", "issuer": "MEAA", "note": "澳洲新闻记者行业工会会员资格，大型媒体机构任职的实际惯例", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "驾驶执照（Car Licence）", "issuer": "各州交通部门", "note": "外勤记者的实际工作要求", "is_mandatory": 0, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 200, "count_max": 600, "note": "全国，传统媒体岗位减少，数字媒体岗持续"},
    {"platform": "Indeed",   "count_min": 150, "count_max": 500, "note": "含媒体机构、政府公关岗和企业内容岗"},
    {"platform": "LinkedIn", "count_min": 300, "count_max": 800, "note": "数字媒体和企业内容营销记者岗活跃"},
]
SALARIES = [
    {"experience": "初级记者 / 记者助理（0~3年）", "salary_min": 55000, "salary_max": 70000, "salary_note": "毕业记者起薪；区域媒体起薪约 $55k~$60k，都市媒体略高", "sort_order": 0},
    {"experience": "有经验记者（3~10年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "SEEK 区间 $70k~$85k；Indeed 均值 $70,542（2026）", "sort_order": 1},
    {"experience": "高级记者 / 专线记者（8~15年）", "salary_min": 85000, "salary_max": 120000, "salary_note": "SEEK 记者薪资最高端 $85k~$90k；ABC/Nine资深记者可超 $100k", "sort_order": 2},
    {"experience": "编辑 / 新闻主任（12年+）", "salary_min": 110000, "salary_max": 180000, "salary_note": "大型媒体机构编辑和新闻主任薪资区间", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，大型媒体集团可担保记者岗位（较少见）", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要VETASSESS技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要写作技能+信息核实能力+多媒体技能+快速学习能力"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "本科3年；GDip 1年；实习经验积累约1~2年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "VETASSESS评估；发表的Clips（报道作品）是核心评判标准"},
    {"dimension": "job_demand",               "label_zh": "较低", "stars": 2, "note": "传统媒体岗位持续收缩；数字媒体和企业内容方向保持需求"},
    {"dimension": "competition",              "label_zh": "较高", "stars": 4, "note": "主流媒体岗位竞争激烈；区域媒体和企业内容方向相对容易"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "新闻周期紧、突发事件频繁；情绪性报道（灾难/犯罪）有心理压力"},
    {"dimension": "income_level",             "label_zh": "中低", "stars": 2, "note": "有经验记者 $70k~$90k；整体薪资低于大多数专业职业"},
    {"dimension": "future_prospect",          "label_zh": "中低", "stars": 2, "note": "传统媒体持续收缩；AI写作工具替代部分结构化报道任务"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI已影响财经数据和体育简报等结构化内容；调查性新闻和深度报道不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "较低", "stars": 2, "note": "不在MLTSSL，就业岗位数量有限，移民难度高"},
    {"dimension": "pr_difficulty",            "label_zh": "较高", "stars": 4, "note": "非短缺职业，媒体行业担保意愿低；技术移民邀请分数要求高"},
]
SUITABILITY_FIT = ["持有新闻/传媒学位，有发表的新闻报道作品集（Clips），英语写作能力极强", "有多媒体技能（视频采制/社交媒体运营）", "已在澳洲建立本地媒体人脉（大学实习/区域媒体工作经验）", "有专业领域专长（科技/金融/商业），可以向企业内容和专业媒体方向发展", "考虑以企业内容营销记者（Content Marketer）作为新闻职业在澳洲的替代路径"]
SUITABILITY_UNFIT = ["期望通过新闻记者路径获得技术移民（岗位数量有限，非短缺职业）", "英语写作能力不足以达到澳洲主流媒体出版标准", "不适应紧张的新闻截止压力和不规律工作时间"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "记者薪资 $70k~$85k（2026）", "url": "https://au.seek.com/career-advice/role/journalist/salary"},
    {"source_name": "Indeed AU", "content": "记者平均薪资 $70,542（2026）", "url": "https://au.indeed.com/career/journalist/salaries"},
    {"source_name": "SEEK AU", "content": "记者（Reporter）薪资 $85k~$90k（2026）", "url": "https://au.seek.com/career-advice/role/reporter/salary"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲新闻记者工资多少？", "answer": "有经验记者约 $70,000~$90,000（SEEK $70k~$85k；Indeed $70,542）；高级记者约 $85k~$120k；编辑/新闻主任约 $110k~$180k。整体薪资低于大多数专业职业，但ABC/Nine等大型媒体资深记者可达 $100k+。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲新闻记者容易找工作吗？", "answer": "有一定难度。传统媒体岗位持续减少（SEEK 约200~600个），竞争激烈。有多媒体技能（视频/社交媒体）的数字记者需求相对稳定；企业内容营销和品牌新闻方向为记者提供额外就业机会。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国新闻经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国新闻工作经历可以认可。关键挑战是：①中国媒体的运作模式与澳洲独立媒体有较大差异；②英语新闻写作能力是主要门槛。建议以企业内容营销或数字媒体（科技/商业方向）作为在澳洲起步的首选方向。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "新闻记者会被AI替代吗？", "answer": "部分风险较高。AI已能处理财经数据新闻、体育比分简报等结构化内容；但调查性报道、深度专访、现场新闻采集和媒体信任度仍需人类记者。向调查报道、播客和专业领域分析方向发展可有效规避AI风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲新闻记者有年龄限制吗？", "answer": "无。有深厚行业积累和信源网络的资深记者（45~60岁）在深度报道和专业媒体领域非常有竞争力。新闻行业以经验和信誉为核心，资历越深越有价值。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲记者需要什么学历？", "answer": "大型媒体机构（ABC/Nine/AFR）通常要求新闻或传媒相关学历；但区域媒体和数字媒体更注重实际发表作品（Clips）和多媒体技能。英语写作能力是硬性要求。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲记者认证（移民）难吗？", "answer": "难度较高。不在MLTSSL，媒体行业担保意愿低。建议将记者技能转化至企业内容营销（Content Marketing）或公关（PR）方向，这两个方向的就业机会和移民路径更宽广。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "新闻记者和公关专员哪个澳洲发展更好？", "answer": "公关专员（PR Specialist）就业机会更多（任何企业都需要公关）、薪资更高（$75k~$120k vs 记者 $70k~$90k），移民路径更好；新闻记者工作满足感更强（公共信息服务），但行业整体收缩。有新闻写作技能者强烈推荐向公关/企业传播方向拓展。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 新闻记者数据入库完成")

if __name__ == "__main__":
    run()
