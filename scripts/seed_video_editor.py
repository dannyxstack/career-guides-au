"""澳洲视频制作/剪辑师（212314）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "212314", "anzsco_title": "Video Producer",
    "category": "创意/媒体", "workforce_size": 22000, "shortage_listed": 0,
    "growth_areas": json.dumps(["短视频内容（TikTok/Instagram Reels/YouTube Shorts）","企业品牌视频和培训视频","流媒体原创内容（Netflix/Stan澳洲本地制作）","直播技术与活动直播制作","AI辅助视频剪辑（CapCut AI/Adobe Premiere AI）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "视频制作人/剪辑师",
    "summary": "视频制作人和剪辑师为企业、媒体机构、广告公司和内容平台制作短视频、品牌宣传片、纪录片和社交媒体内容。澳洲数字营销对视频内容的需求爆发——90%的营销内容预算已转向视频——推动对视频内容制作者的持续强劲需求。掌握拍摄+剪辑+动态图形全栈技能的制作人竞争力最强。",
    "forecast_note": "JSA预测视频制作就业至2030年增长约8%。短视频营销（TikTok/Instagram/YouTube）是增速最快的方向，企业培训视频和流媒体本地内容制作保持稳定增长。",
    "trend_summary": "澳洲企业视频内容预算快速增长，尤其是中小企业通过短视频进行品牌营销。AI视频剪辑工具（Adobe Premiere AI、CapCut AI）提升了生产效率，但创意策划、客户沟通和最终品质把控仍需专业制作人。流媒体服务（Netflix在澳洲本地内容投资大幅增加）推动高端制作岗位增长。",
}
I18N_EN = {
    "locale": "en", "name": "Video Producer / Editor",
    "summary": "Video producers and editors create short videos, brand promotional films, documentaries and social media content for businesses, media organisations, ad agencies and content platforms. The explosion of Australian digital marketing demand for video content — with 90% of marketing budgets shifting to video — drives sustained strong demand for video content creators. Producers with full-stack skills (shooting + editing + motion graphics) have the strongest market competitiveness.",
    "forecast_note": "JSA projects ~8% growth in video production employment by 2030. Short-form video marketing (TikTok/Instagram/YouTube) is the fastest-growing direction, with corporate training videos and streaming local content production maintaining stable growth.",
    "trend_summary": "Australian corporate video content budgets are growing rapidly, especially SMEs using short video for brand marketing. AI editing tools (Adobe Premiere AI, CapCut AI) have increased production efficiency, but creative strategy, client communication and final quality control still require professional producers. Streaming services (Netflix significantly increasing Australian local content investment) are driving growth in premium production roles.",
}
EDUCATION = [
    {"stage": "Bachelor of Film & Television / Media Production（3年）", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 110000, "cost_note": "澳洲多所大学提供影视制作专业；国际生约 $25,000~$36,000/年", "sort_order": 0},
    {"stage": "Diploma of Screen and Media（TAFE，1~2年）", "duration": "1~2年", "cost_min": 5000, "cost_max": 25000, "cost_note": "TAFE影视技术文凭，注重实践技能训练", "sort_order": 1},
    {"stage": "Adobe Premiere Pro / DaVinci Resolve / After Effects 专项技能", "duration": "3~12个月自主学习", "cost_min": 0, "cost_max": 3000, "cost_note": "剪辑软件熟练度是入门硬性要求", "sort_order": 2},
    {"stage": "作品集（Demo Reel）建设", "duration": "持续", "cost_min": 0, "cost_max": 5000, "cost_note": "Demo Reel是视频制作人求职的核心展示材料", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Adobe Certified Professional - Premiere Pro", "issuer": "Adobe", "note": "视频剪辑官方认证", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "DaVinci Resolve Certified User", "issuer": "Blackmagic Design", "note": "调色和专业剪辑认证，高端制作公司重视", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "远程飞行员执照（RePL）", "issuer": "CASA", "note": "无人机航拍视频制作的商业法律要求", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600, "count_max": 2000, "note": "全国，含视频剪辑师/内容制作人/制作总监岗"},
    {"platform": "Indeed",   "count_min": 500, "count_max": 1500, "note": "含企业内容团队和制作公司岗"},
    {"platform": "LinkedIn", "count_min": 800, "count_max": 2500, "note": "企业数字营销团队和制作公司直招"},
]
SALARIES = [
    {"experience": "初级视频剪辑师（0~2年）", "salary_min": 52000, "salary_max": 68000, "salary_note": "助理剪辑或初级内容制作人的全职薪资", "sort_order": 0},
    {"experience": "中级视频制作人/剪辑师（2~7年）", "salary_min": 68000, "salary_max": 90000, "salary_note": "SEEK 区间 $75k~$85k；Indeed 均值 $72,347；SEEK制作人 $85k~$105k（2026）", "sort_order": 1},
    {"experience": "高级视频制作人（5~12年）", "salary_min": 90000, "salary_max": 125000, "salary_note": "有完整项目管理能力的资深制作人；悉尼/墨尔本广告公司资深岗", "sort_order": 2},
    {"experience": "制作总监 / 执行制片（10年+）", "salary_min": 120000, "salary_max": 200000, "salary_note": "电视台、流媒体和大型广告公司的制作总监级岗位", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，媒体公司和制作公司可担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要VETASSESS技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要技术技能+创意眼光+项目管理能力的综合素质"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3年；文凭1~2年；系统自学+实践约1~3年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "VETASSESS评估；Demo Reel作品集是关键评判标准"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "数字营销视频需求爆发，企业内容团队快速扩张"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "全栈技能（拍摄+剪辑+动效）的制作人供不应求；单一剪辑竞争较激烈"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "项目截止期前强度高；直播制作强度极大；广告公司加班文化浓"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级 $68k~$90k；资深制作人可达 $90k~$125k；制作总监 $120k+"},
    {"dimension": "future_prospect",          "label_zh": "中高", "stars": 4, "note": "视频内容需求持续增长，是创意类职业中增长最稳定的方向"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI剪辑工具影响初级任务效率，但创意制作和品牌策略不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "不在MLTSSL，但雇主担保路径相对可行（媒体/广告行业担保活跃）"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "非短缺职业，189邀请分数要求高；雇主担保482是更可行路径"},
]
SUITABILITY_FIT = ["有完整的视频制作作品集（Demo Reel），涵盖不同类型项目", "全栈技能：拍摄（摄影机操作/灯光）+ 剪辑（Premiere/DaVinci）+ 动态图形（After Effects）", "有企业品牌视频或社交媒体内容制作经验（需求量最大方向）", "有意向在澳洲媒体/广告/企业内容团队就职", "英语沟通流利（客户汇报和创意方向确认）"]
SUITABILITY_UNFIT = ["仅有个人YouTube/TikTok内容创作经验，无商业项目经验", "技能单一（仅剪辑，无拍摄或动效能力）", "期望通过视频制作快速获得技术移民（非短缺职业，需要雇主担保）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "视频剪辑师薪资 $75k~$85k；制作人 $85k~$105k（2026）", "url": "https://au.seek.com/career-advice/role/video-editor/salary"},
    {"source_name": "Indeed AU", "content": "视频剪辑师平均薪资 $72,347（2026）", "url": "https://au.indeed.com/career/video-editor/salaries"},
    {"source_name": "PayScale AU", "content": "视频剪辑师平均时薪 $29.45（2026）", "url": "https://www.payscale.com/research/AU/Job=Film_%2F_Video_Editor/Salary"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲视频剪辑师工资多少？", "answer": "中级视频制作人/剪辑师约 $68,000~$90,000（SEEK $75k~$85k；Indeed $72,347）；高级制作人约 $90k~$125k；制作总监约 $120k~$200k。自由职业收入差异大，按项目计费。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲视频制作/剪辑师容易找工作吗？", "answer": "有一定需求，全栈技能（拍摄+剪辑+动效）的制作人供不应求。SEEK 挂牌约600~2,000个职位，企业数字营销团队对内容制作人的需求持续增长。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国影视制作经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，有商业视频制作项目经验者可以认可。关键是制作一份高质量的英语Demo Reel（包含商业/品牌视频作品），展示技术技能和创意能力。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "视频剪辑师会被AI替代吗？", "answer": "AI工具（Adobe Premiere AI、CapCut AI、Runway）正在自动化粗剪、字幕生成等初级任务，但创意制作决策、品牌故事构建和客户沟通不可替代。向内容策略、品牌制作人和高端制作总监方向发展可有效规避AI风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲视频制作人有年龄限制吗？", "answer": "无。有丰富商业制作经验和客户资源的资深制作人（40~55岁）在广告公司和企业内容团队非常有竞争力。创意行业更看重作品质量和客户关系管理能力。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲视频制作人需要什么学历？", "answer": "大型制作公司和广告公司偏好影视/媒体制作本科学历；企业内容团队和中小型制作公司更注重Demo Reel和实际技能。TAFE文凭+专业作品集可以进入大多数市场。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲视频制作人认证（移民）难吗？", "answer": "不在MLTSSL，移民难度相对较高。雇主担保482是最可行路径，媒体公司和大型广告公司有担保能力。建议先通过学生签证就读媒体制作相关课程，积累澳洲商业项目经验后申请担保。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "视频制作人和平面设计师哪个澳洲发展更好？", "answer": "视频制作人需求增速更快（数字营销视频预算增长20%/年）；薪资略高且移民路径相近。两者都不在MLTSSL短缺清单，均需要雇主担保或高分技术移民。有视频技能者选视频方向；有平面设计基础者可以在视频动效方向发展，差异化竞争。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 视频制作人/剪辑师数据入库完成")

if __name__ == "__main__":
    run()
