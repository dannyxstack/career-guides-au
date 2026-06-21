"""澳洲动画师/游戏设计师（212411）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "212411", "anzsco_title": "Animator",
    "category": "创意/媒体", "workforce_size": 15000, "shortage_listed": 0,
    "growth_areas": json.dumps(["3D动画与视觉特效（VFX）","游戏开发（独立游戏+AAA工作室）","AR/VR沉浸式体验动画","企业动态图形与营销动画","AI辅助动画制作（Adobe Firefly/Runway Gen-2）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "动画师/游戏设计师",
    "summary": "动画师为影视、游戏、广告和数字媒体创作2D/3D动画内容；游戏设计师负责游戏关卡、系统和玩法机制的设计。澳洲VFX行业（电影后期制作）和独立游戏开发圈在全球具有一定影响力，设计师需要掌握专业动画软件（Maya/Blender/Unreal Engine）和扎实的艺术基础。",
    "forecast_note": "JSA预测动画和游戏设计就业至2030年保持稳定至略微增长。流媒体平台（Netflix在澳洲动画内容投资增加）和游戏产业扩张是主要增长驱动力；AI动画工具改变部分基础工作流程。",
    "trend_summary": "澳洲Screen Australia持续资助本地动画和VFX制作，维持稳定的产业就业。澳洲独立游戏（Indie Game）开发圈活跃（如House House、League of Geeks等悉尼/墨尔本工作室）。AI动画工具（Runway Gen-2、Adobe Firefly）正在改变内容创作流程，但人工动画师在创意质量控制上仍不可替代。",
}
I18N_EN = {
    "locale": "en", "name": "Animator / Game Designer",
    "summary": "Animators create 2D/3D animated content for film, games, advertising and digital media; game designers design game levels, systems and gameplay mechanics. Australia's VFX industry (film post-production) and indie game development community have global influence. Designers need professional animation software (Maya/Blender/Unreal Engine) and strong artistic foundations.",
    "forecast_note": "JSA projects stable to slightly growing animation and game design employment through 2030. Streaming platforms (Netflix increasing Australian animation content investment) and gaming industry expansion are the main growth drivers; AI animation tools are changing some basic workflows.",
    "trend_summary": "Screen Australia continues funding local animation and VFX production, maintaining stable industry employment. Australia's indie game development scene is active (e.g., House House, League of Geeks in Sydney/Melbourne). AI animation tools (Runway Gen-2, Adobe Firefly) are transforming content creation workflows, but human animators remain irreplaceable for creative quality control.",
}
EDUCATION = [
    {"stage": "Bachelor of Animation / Game Design（3年）", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 110000, "cost_note": "RMIT、Swinburne、AIE等顶尖动画/游戏设计院校；国际生约 $25,000~$38,000/年", "sort_order": 0},
    {"stage": "Diploma of Screen and Media（Animation）（TAFE，1~2年）", "duration": "1~2年", "cost_min": 5000, "cost_max": 25000, "cost_note": "实践型动画技术文凭", "sort_order": 1},
    {"stage": "Academy of Interactive Entertainment（AIE）专项课程", "duration": "1~2年", "cost_min": 15000, "cost_max": 40000, "cost_note": "澳洲最具影响力的游戏和VFX专业培训机构，行业对接活跃", "sort_order": 2},
    {"stage": "专业软件技能（Maya/Blender/Unity/Unreal Engine/After Effects）", "duration": "自主学习+课程", "cost_min": 0, "cost_max": 3000, "cost_note": "Unreal Engine 5是游戏/VFX行业的新一代标准工具", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Autodesk Maya Certified User", "issuer": "Autodesk", "note": "3D动画行业标准软件认证", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Unreal Engine Certification", "issuer": "Epic Games", "note": "游戏开发和实时渲染行业标准工具认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Adobe After Effects 认证", "issuer": "Adobe", "note": "动态图形和合成特效的行业标准工具认证", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 200, "count_max": 600, "note": "全国，含2D/3D动画师、VFX艺术家、游戏设计师岗"},
    {"platform": "Indeed",   "count_min": 150, "count_max": 500, "note": "含独立游戏工作室、VFX公司和广告动画岗"},
    {"platform": "LinkedIn", "count_min": 300, "count_max": 800, "note": "游戏工作室和VFX公司直招活跃"},
]
SALARIES = [
    {"experience": "初级动画师 / 游戏设计师（0~2年）", "salary_min": 52000, "salary_max": 68000, "salary_note": "入门级VFX艺术家或初级游戏设计师", "sort_order": 0},
    {"experience": "动画师（2~7年）", "salary_min": 72000, "salary_max": 92000, "salary_note": "SEEK 动画师区间 $80k~$90k；PayScale 均值 $60,594（2026）", "sort_order": 1},
    {"experience": "游戏设计师（2~8年）", "salary_min": 85000, "salary_max": 118000, "salary_note": "SEEK 游戏设计师 $100k~$115k；Indeed 均值 $95,251（2026）", "sort_order": 2},
    {"experience": "高级VFX/动画总监（8年+）", "salary_min": 115000, "salary_max": 200000, "salary_note": "大型VFX公司（Animal Logic等）或AAA游戏工作室高级岗", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，VFX公司和游戏工作室可担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要VETASSESS技能评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道（NSW/VIC有科技创意产业提名）", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "需要强大的艺术基础+专业3D软件技能+技术理解（游戏设计需要编程基础）"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位3年；专项课程1~2年；工业级作品集建设约2~3年"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "VETASSESS评估；Demo Reel/作品集是关键评判标准，要求很高"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "全职岗位数量有限，自由职业比例高；游戏设计需求略强于动画"},
    {"dimension": "competition",              "label_zh": "较高", "stars": 4, "note": "VFX和游戏行业全球竞争激烈，顶尖人才从全球招募"},
    {"dimension": "work_intensity",           "label_zh": "高", "stars": 5, "note": "游戏发布前的Crunch Time（高强度冲刺期）是行业普遍现象"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "动画师 $72k~$92k；游戏设计师 $85k~$118k；VFX总监 $115k+"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "流媒体动画需求增长；AI动画工具影响基础工作；VR/AR是新增长点"},
    {"dimension": "ai_risk",                  "label_zh": "中高", "stars": 4, "note": "AI动画工具（Runway/Adobe Firefly）影响初级动画任务；创意总监和角色设计抗AI性更强"},
    {"dimension": "pr_friendliness",          "label_zh": "中低", "stars": 2, "note": "不在MLTSSL，全职岗位数量有限，移民难度较高"},
    {"dimension": "pr_difficulty",            "label_zh": "较高", "stars": 4, "note": "非短缺职业，VFX/游戏公司担保意愿因公司规模而异；建议先建立澳洲本地人脉"},
]
SUITABILITY_FIT = ["持有动画/游戏设计学位，有工业级作品集（Demo Reel/游戏Demo）", "掌握专业3D软件（Maya/Blender/Unreal Engine 5），技能水平可对标国际标准", "有VFX公司或游戏工作室工作经验，可以提供雇主担保参考", "有独立游戏发布或参与商业VFX项目的实际经验", "愿意先以自由职业或合同制方式进入澳洲市场，积累本地项目经验"]
SUITABILITY_UNFIT = ["仅有业余/个人创作动画经验，无商业项目或工作室实习经历", "期望通过动画/游戏设计职业快速获得技术移民（岗位数量有限，非短缺职业）", "不能接受游戏发布前极高强度的Crunch Time工作文化"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "动画师薪资 $80k~$90k；游戏设计师 $100k~$115k（2026）", "url": "https://au.seek.com/career-advice/role/animator/salary"},
    {"source_name": "Indeed AU", "content": "视频游戏设计师平均薪资 $95,251（2026）", "url": "https://au.indeed.com/career/video-game-designer/salaries"},
    {"source_name": "PayScale AU", "content": "动画师平均薪资 $60,594（2026）", "url": "https://www.payscale.com/research/AU/Job=Animator/Salary"},
    {"source_name": "Screen Australia", "content": "澳洲动画和VFX产业就业数据", "url": "https://www.screenaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲动画师/游戏设计师工资多少？", "answer": "动画师约 $72,000~$92,000（SEEK $80k~$90k）；游戏设计师约 $85,000~$118,000（SEEK $100k~$115k；Indeed $95,251）；高级VFX/动画总监约 $115k~$200k。PayScale动画师均值 $60,594，反映了大量自由职业兼职收入。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲动画师/游戏设计师容易找工作吗？", "answer": "全职岗位数量有限（SEEK约200~600个），竞争激烈。Animal Logic、Framestore、Rising Sun Pictures等VFX工作室和墨尔本/悉尼游戏工作室有固定招聘需求，但对技能水平要求很高。自由职业（广告动画、企业动态图形）提供额外收入来源。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国动画/游戏经验澳洲认可吗？", "answer": "通过VETASSESS技能评估，中国动画和游戏工作室工作经验可以认可。关键是制作一份英语Demo Reel（动画）或游戏Demo（游戏设计），技能水平必须达到国际标准。中国主要VFX/游戏公司（网易/米哈游/腾讯等）的工作经验在澳洲有一定认可度。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "动画师/游戏设计师会被AI替代吗？", "answer": "中高风险。AI工具（Runway Gen-2、Adobe Firefly动画）正在自动化部分基础动画任务（背景动画、中间帧）；但角色动画、情感表达和创意方向决策不可替代。游戏设计中玩法创新和关卡设计也难以被AI替代。向技术总监、VFX总监和游戏主策划方向发展可提升AI抗性。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲动画师有年龄限制吗？", "answer": "无。有丰富工作室经验和项目管理能力的资深动画总监（40~55岁）在大型VFX项目中非常有价值。游戏设计行业也欢迎有丰富设计积累的资深设计师。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲动画师/游戏设计师需要什么学历？", "answer": "大型VFX公司（Animal Logic等）通常要求相关本科学历；游戏工作室和中小型制作公司更注重Demo Reel和技能水平。AIE（Academy of Interactive Entertainment）等专业培训机构的文凭被行业广泛认可。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲动画师认证（移民）难吗？", "answer": "难度较高。不在MLTSSL，全职岗位有限。建议先通过学生签证就读AIE或RMIT等院校，积累澳洲本地工作室实习经验，通过VFX/游戏公司雇主担保482是最可行路径。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "动画师和游戏设计师哪个澳洲发展更好？", "answer": "游戏设计师薪资略高（$85k~$118k vs 动画师 $72k~$92k），游戏产业增长更快（全球游戏市场持续扩张）；动画师在VFX/广告/企业动画等多领域有就业机会，更灵活。有编程/技术背景者选游戏设计；有艺术/手绘基础者选动画。两者都可以在同一路径上发展（许多工作室需要动画+游戏双技能）。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 动画师/游戏设计师数据入库完成")

if __name__ == "__main__":
    run()
