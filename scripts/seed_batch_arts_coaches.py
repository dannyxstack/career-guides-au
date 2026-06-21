# -*- coding: utf-8 -*-
"""新增 11 个艺术/教练/营养类职业（AU）。数据为综合公开来源（JSA / SEEK / Indeed 2025-2026）的估算。
评分为 10 分制；is_migration 枚举 0/1/2（按官方 CSOL/MLTSSL 核对）。
幂等：seed_occupation_v2 按 (country_code, occ_code) 定位。
运行：python -m scripts.seed_batch_arts_coaches
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation_v2

CREATIVE = "Creative, Media & Personal Services"
HEALTH = "Healthcare & Care"
DIMS = ["learning_difficulty", "learning_duration", "certification_difficulty", "job_demand",
        "competition", "work_intensity", "income_level", "future_prospect", "ai_risk",
        "pr_friendliness", "pr_difficulty"]


def ratings(rows):
    """rows: 11 个 (label_zh, stars(10分制), note)，顺序同 DIMS。"""
    return [{"dimension": d, "label_zh": r[0], "stars": r[1], "note": r[2]} for d, r in zip(DIMS, rows)]


def jl(seek=(100, 400)):
    return [{"platform": "Seek", "count_min": seek[0], "count_max": seek[1], "note": "全国岗位区间（含兼职/合同）"},
            {"platform": "Indeed", "count_min": int(seek[0] * 0.7), "count_max": int(seek[1] * 0.8), "note": "含俱乐部、工作室、自由职业"}]


NONMIG_VISA = []  # is_migration=0：不列签证（页面显示非技术移民说明）
RESTRICTED_VISA = [
    {"visa_subclass": "482", "visa_name": "Skills in Demand", "description": "雇主担保；该职业在 CSOL 上，可由符合条件的雇主提名", "sort_order": 0},
    {"visa_subclass": "494", "visa_name": "Skilled Employer Sponsored Regional", "description": "偏远地区雇主担保（临时转永居）", "sort_order": 1},
    {"visa_subclass": "DAMA", "visa_name": "Designated Area Migration Agreement", "description": "部分偏远地区指定协议可纳入资格清单", "sort_order": 2},
]
GSM_VISA = [
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "邀请制；需相关学位与技能评估（VETASSESS）", "sort_order": 0},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州/领地提名", "sort_order": 1},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名（临时转永居）", "sort_order": 2},
    {"visa_subclass": "482", "visa_name": "Skills in Demand", "description": "雇主担保（注意：该职业在 GSM 清单，但不在 482 的 CSOL，482 仅限劳务协议）", "sort_order": 3},
]

OCCS = []

# 1. Painter (Visual Arts) 211411 —— 非移民
OCCS.append(dict(
    occ_code="211411", anzsco_code="211411", anzsco_title="Painter (Visual Arts)", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["数字艺术与插画", "公共艺术/壁画委约", "艺术教育与工作坊", "画廊代理与线上销售（Etsy/Saatchi）"],
    name_zh="画家（视觉艺术）", name_en="Painter (Visual Arts)",
    summary_zh="视觉艺术画家用绘画、素描等媒介进行原创艺术创作，作品通过画廊、委约、比赛和线上平台销售。多数为自由职业或兼职，收入波动大、与声誉和作品销售强相关；常以艺术教学、插画或设计等相关工作补充收入。",
    summary_en="Visual arts painters create original artworks in paint and other media, selling through galleries, commissions, prizes and online platforms. Most work freelance or part-time with highly variable income tied to reputation and sales, often supplementing earnings through teaching, illustration or design.",
    forecast_zh="艺术类职业整体增长平缓，岗位高度自雇化；数字艺术、插画和公共艺术委约是相对活跃的细分。AI 生成图像带来风格与版权冲击，但原创性、实体作品与艺术家品牌仍具不可替代价值。",
    trend_zh="艺术市场两极分化：少数知名艺术家高溢价，多数靠教学/委约/线上销售维持。线上平台降低了销售门槛；AI 绘图工具既是竞争也是创作辅助。",
    edu=[{"stage": "Bachelor of Fine Arts / Visual Arts（视觉艺术学士，可选）", "duration": "3年", "cost_min": 30000, "cost_max": 90000, "cost_note": "并非强制；许多画家自学或经美术学院短训成才", "sort_order": 0},
         {"stage": "美术学院短期课程 / 工作坊", "duration": "数周~1年", "cost_min": 500, "cost_max": 8000, "cost_note": "技法提升与作品集积累", "sort_order": 1}],
    quals=[{"qual_name": "作品集（Portfolio）", "issuer": "—", "note": "声誉与销售的核心；学历非必需", "is_mandatory": 0, "sort_order": 0}],
    sal=[{"experience": "新晋/兼职画家", "salary_min": 25000, "salary_max": 45000, "salary_note": "多为兼职；收入随作品销售波动", "sort_order": 0},
         {"experience": "全职职业画家", "salary_min": 45000, "salary_max": 75000, "salary_note": "含教学/委约/线上销售综合收入", "sort_order": 1},
         {"experience": "知名艺术家", "salary_min": 80000, "salary_max": 250000, "salary_note": "画廊代理+高价委约，头部溢价显著", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("中低", 4.0, "技法可自学；达到可售水平需长期练习"),
        ("中等", 5.0, "成才周期长，但无固定学制门槛"),
        ("低", 2.0, "无强制执照；凭作品集"),
        ("低", 3.0, "全职岗位少，高度自雇"),
        ("很高", 9.0, "供给远大于稳定需求，竞争激烈"),
        ("中等", 5.0, "创作自由但收入与交付压力并存"),
        ("低", 3.0, "多数收入偏低且不稳定"),
        ("中等", 5.0, "线上销售与委约带来新机会"),
        ("中高", 6.0, "AI 生成图像冲击商业插画，但原创实体艺术与品牌护城河仍在"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["有强烈创作热情并能长期坚持作品集积累", "愿意结合教学、委约、线上销售多元化收入", "能接受收入波动与自雇不确定性"],
    unfit=["追求稳定月薪与清晰晋升路径", "以移民为主要目标（本职业无技术移民通道）", "不愿做自我营销与作品销售"],
    sources=[{"source_name": "Jobs and Skills Australia", "content": "艺术职业就业与收入概况", "url": "https://www.jobsandskills.gov.au/"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲画家收入多少？", "answer": "差异极大：兼职新晋约 $25k~$45k；全职职业画家约 $45k~$75k（含教学/委约/线上销售）；知名艺术家可达 $80k~$250k+。多数画家以多元收入维持。"},
          {"faq_type": "difficulty", "sort_order": 1, "question": "画家能技术移民澳洲吗？", "answer": "基本不能。Painter (Visual Arts, 211411) 不在 CSOL 或 GSM 技术移民清单上，没有独立技术或雇主担保提名通道。少数顶尖艺术家可考虑全球人才（GTI）或杰出人才（858）等特殊通道。"},
          {"faq_type": "ai_risk", "sort_order": 2, "question": "画家会被 AI 替代吗？", "answer": "商业插画/图库类受 AI 生成图像冲击较大，但原创实体艺术、艺术家品牌、现场创作与展览体验难以被替代。把 AI 作为创作与构图辅助、强化个人风格与线下展售，是更稳的路径。"}],
))

# 2. Musician (Instrumental) 211213 —— 非移民
OCCS.append(dict(
    occ_code="211213", anzsco_code="211213", anzsco_title="Musician (Instrumental)", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["现场演出与巡演", "录音与配乐（影视/广告/游戏）", "音乐教学", "流媒体与自媒体（YouTube/Spotify）"],
    name_zh="音乐家（器乐）", name_en="Musician (Instrumental)",
    summary_zh="器乐音乐家演奏一种或多种乐器，从事现场演出、录音、配乐与教学。多为自由职业，收入由演出、版税、教学和资助等多元构成，波动较大，顶尖演奏者与乐团首席收入较高。",
    summary_en="Instrumental musicians perform on one or more instruments across live shows, recording, scoring and teaching. Most work freelance with variable income from gigs, royalties, teaching and grants; principals and top performers earn considerably more.",
    forecast_zh="现场演出市场回暖，但全职乐团席位有限；影视/游戏配乐、教学和流媒体是增量方向。AI 生成音乐冲击背景/库存音乐，但现场演奏、原创性与表演者魅力难以替代。",
    trend_zh="收入高度多元化：演出+教学+录音+流媒体。自媒体降低了触达门槛；版权与流媒体分成是关注重点。",
    edu=[{"stage": "Bachelor of Music（音乐学士，可选）", "duration": "3~4年", "cost_min": 30000, "cost_max": 100000, "cost_note": "古典/乐团方向常见；流行/自学路径亦可", "sort_order": 0},
         {"stage": "私人器乐训练 / 考级", "duration": "多年持续", "cost_min": 2000, "cost_max": 30000, "cost_note": "长期技艺积累；AMEB 考级", "sort_order": 1}],
    quals=[{"qual_name": "演奏水平与作品/演出记录", "issuer": "—", "note": "试奏（audition）决定乐团/演出机会", "is_mandatory": 0, "sort_order": 0}],
    sal=[{"experience": "兼职/自由演奏者", "salary_min": 30000, "salary_max": 55000, "salary_note": "按场次计酬，波动大", "sort_order": 0},
         {"experience": "全职音乐家", "salary_min": 55000, "salary_max": 85000, "salary_note": "演出+教学+录音综合", "sort_order": 1},
         {"experience": "乐团首席/知名演奏家", "salary_min": 90000, "salary_max": 160000, "salary_note": "主要交响乐团席位与高端演出", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("高", 7.0, "高水平器乐需多年训练"),
        ("高", 8.0, "技艺成熟周期很长"),
        ("低", 2.0, "无强制执照；靠试奏"),
        ("低", 3.0, "全职乐团席位稀缺"),
        ("很高", 9.0, "竞争极其激烈"),
        ("中高", 6.0, "排练演出强度高，作息不规律"),
        ("中等", 5.0, "顶尖高收入，多数中等且不稳"),
        ("中等", 5.0, "配乐/教学/流媒体带来增量"),
        ("中等", 5.0, "AI 冲击库存/背景音乐，现场演奏与原创难替代"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["有扎实器乐功底并持续精进", "愿意多元化收入（演出/教学/录音/流媒体）", "能适应不规律作息与收入波动"],
    unfit=["追求稳定坐班与固定薪资", "以移民为主要目标", "不愿长期投入技艺训练"],
    sources=[{"source_name": "Jobs and Skills Australia", "content": "音乐/表演艺术职业概况", "url": "https://www.jobsandskills.gov.au/"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲音乐家收入多少？", "answer": "兼职/自由演奏者约 $30k~$55k（按场计酬）；全职音乐家约 $55k~$85k（演出+教学+录音）；乐团首席/知名演奏家可达 $90k~$160k。多数靠多元收入。"},
          {"faq_type": "difficulty", "sort_order": 1, "question": "音乐家能技术移民澳洲吗？", "answer": "基本不能。Musician (211213) 不在 CSOL 或 GSM 技术移民清单上。顶尖音乐家可探索全球人才（GTI）或杰出人才（858）等特殊通道。"},
          {"faq_type": "ai_risk", "sort_order": 2, "question": "音乐家会被 AI 替代吗？", "answer": "AI 生成音乐冲击背景/库存音乐与简单编曲，但现场演奏、即兴、舞台魅力与原创艺术性难以替代。把 AI 用于编曲/制作辅助，强化现场与个人风格更稳。"}],
))

# 3. Singer 211214 —— 非移民
OCCS.append(dict(
    occ_code="211214", anzsco_code="211214", anzsco_title="Singer", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["现场与活动演出", "录音/翻唱与流媒体", "声乐教学", "音乐剧/合唱团"],
    name_zh="歌手", name_en="Singer",
    summary_zh="歌手以歌唱进行表演，涵盖现场演出、录音、音乐剧、合唱团与活动演唱。多为自由职业，收入由演出、版税、教学和活动构成，波动大；成名与稳定收入高度依赖作品、曝光与个人品牌。",
    summary_en="Singers perform vocally across live shows, recording, musical theatre, choirs and events. Most work freelance with variable income from performances, royalties, teaching and functions; stable income depends heavily on material, exposure and personal brand.",
    forecast_zh="活动与现场演出需求稳定，音乐剧与合唱是相对稳定的就业方向；流媒体与短视频改变了成名与变现路径。AI 合成人声冲击配音/库存演唱，但现场感染力与原创表达难以替代。",
    trend_zh="自媒体与短视频成为重要曝光与变现渠道；活动演唱（婚礼/企业）是稳定的现金流来源。",
    edu=[{"stage": "声乐训练 / 音乐学位（可选）", "duration": "数年持续", "cost_min": 2000, "cost_max": 60000, "cost_note": "私人声乐课或音乐学院；非强制", "sort_order": 0}],
    quals=[{"qual_name": "演出记录与作品（Demo/曲目）", "issuer": "—", "note": "试唱与曝光决定机会", "is_mandatory": 0, "sort_order": 0}],
    sal=[{"experience": "兼职/活动歌手", "salary_min": 28000, "salary_max": 52000, "salary_note": "按场次计酬，波动大", "sort_order": 0},
         {"experience": "全职歌手", "salary_min": 52000, "salary_max": 80000, "salary_note": "演出+教学+活动综合", "sort_order": 1},
         {"experience": "知名歌手/音乐剧主演", "salary_min": 85000, "salary_max": 200000, "salary_note": "头部演出与版税溢价显著", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("中高", 6.0, "声乐技巧与舞台表现需长期打磨"),
        ("高", 7.0, "成熟周期长"),
        ("低", 2.0, "无强制执照"),
        ("低", 3.0, "全职稳定岗位少"),
        ("很高", 9.0, "竞争极其激烈"),
        ("中高", 6.0, "演出作息不规律，需保护嗓音"),
        ("中等", 5.0, "头部高收入，多数中等不稳"),
        ("中等", 5.0, "流媒体与活动带来增量"),
        ("中等", 5.0, "AI 合成人声冲击配唱，现场与原创难替代"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["有声乐天赋并持续训练", "擅长自我营销与舞台表现", "能接受收入波动并多元化变现"],
    unfit=["追求稳定坐班与固定薪资", "以移民为主要目标", "不愿做曝光与个人品牌经营"],
    sources=[{"source_name": "Jobs and Skills Australia", "content": "表演艺术职业概况", "url": "https://www.jobsandskills.gov.au/"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲歌手收入多少？", "answer": "兼职/活动歌手约 $28k~$52k；全职歌手约 $52k~$80k；知名歌手/音乐剧主演可达 $85k~$200k+。多数靠演出+教学+活动多元收入。"},
          {"faq_type": "difficulty", "sort_order": 1, "question": "歌手能技术移民澳洲吗？", "answer": "基本不能。Singer (211214) 不在技术移民清单上。极少数顶尖表演者可考虑全球人才/杰出人才等特殊通道。"},
          {"faq_type": "ai_risk", "sort_order": 2, "question": "歌手会被 AI 替代吗？", "answer": "AI 合成人声与翻唱冲击配唱/库存演唱，但现场演出、情感表达、舞台魅力与个人品牌难以替代。强化现场与原创、用 AI 辅助制作更稳。"}],
))

# 4. Dance Teacher 249212 —— 非移民
OCCS.append(dict(
    occ_code="249212", anzsco_code="249212", anzsco_title="Dance Teacher (Private Tuition)", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["少儿舞蹈培训", "成人兴趣班（拉丁/街舞/芭蕾）", "考级与比赛培训", "线上课程"],
    name_zh="舞蹈教练", name_en="Dance Teacher (Private Tuition)",
    summary_zh="舞蹈教练在舞蹈工作室或私人培训机构教授芭蕾、现代舞、拉丁、街舞等，面向少儿与成人。多为按课时计酬或自营工作室，收入与学生规模、口碑和经营能力相关。",
    summary_en="Dance teachers instruct ballet, contemporary, Latin, hip-hop and other styles to children and adults in studios or private settings. Many are paid per class or run their own studio, with income tied to student numbers, reputation and business skills.",
    forecast_zh="少儿艺术教育需求稳定，舞蹈培训是稳定的本地服务行业；自营工作室是常见创业路径。线上课程拓展了触达，但核心教学依赖现场指导与互动。",
    trend_zh="少儿培训为主力市场；成人兴趣与健身舞蹈（如尊巴）增长。自营工作室与连锁加盟并存。",
    edu=[{"stage": "舞蹈专业训练 / 教学资质（如 RAD/CSTD 考级体系）", "duration": "多年持续", "cost_min": 2000, "cost_max": 30000, "cost_note": "教学体系认证提升竞争力；非强制", "sort_order": 0},
         {"stage": "Working with Children Check（与儿童工作许可）", "duration": "申请即得", "cost_min": 0, "cost_max": 130, "cost_note": "教授未成年人的法定要求（各州）", "sort_order": 1}],
    quals=[{"qual_name": "Working with Children Check（WWCC）", "issuer": "各州主管机构", "note": "教未成年人的法定要求", "is_mandatory": 1, "sort_order": 0},
           {"qual_name": "舞蹈教学考级资质（RAD/CSTD 等）", "issuer": "相关考级机构", "note": "提升专业认可度", "is_mandatory": 0, "sort_order": 1}],
    sal=[{"experience": "兼职舞蹈教练", "salary_min": 35000, "salary_max": 55000, "salary_note": "按课时计酬", "sort_order": 0},
         {"experience": "全职舞蹈教练", "salary_min": 55000, "salary_max": 75000, "salary_note": "稳定课表+少量私教", "sort_order": 1},
         {"experience": "工作室经营者", "salary_min": 70000, "salary_max": 150000, "salary_note": "自营工作室净利润（视规模）", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("中等", 5.0, "需扎实舞蹈功底+教学能力"),
        ("中高", 6.0, "技艺与教学经验积累周期长"),
        ("低", 3.0, "无统一执照，需 WWCC"),
        ("中等", 5.0, "本地培训需求稳定"),
        ("中高", 6.0, "热门城市工作室竞争较强"),
        ("中高", 6.0, "晚间/周末课多，体力要求高"),
        ("中等", 5.0, "按课时为主；自营可提升收入"),
        ("中等", 6.0, "少儿培训刚需稳定"),
        ("很低", 2.0, "高度依赖现场示范与互动，AI 难替代"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["有舞蹈功底并热爱教学", "擅长与儿童/学员互动", "有意自营工作室创业"],
    unfit=["不喜欢晚间周末工作", "以移民为主要目标", "不愿持续训练与考取教学资质"],
    sources=[{"source_name": "Jobs and Skills Australia", "content": "私人教学职业概况", "url": "https://www.jobsandskills.gov.au/"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲舞蹈教练收入多少？", "answer": "兼职约 $35k~$55k（按课时）；全职约 $55k~$75k；自营工作室经营者约 $70k~$150k（视规模）。"},
          {"faq_type": "difficulty", "sort_order": 1, "question": "舞蹈教练能技术移民吗？", "answer": "不能直接技术移民。Dance Teacher (Private Tuition, 249212) 不在 CSOL 或 GSM 独立技术移民清单上。"},
          {"faq_type": "education_limit", "sort_order": 2, "question": "当舞蹈教练需要什么资质？", "answer": "无强制学历，但教未成年人必须持 Working with Children Check（WWCC）。RAD/CSTD 等舞蹈考级教学资质能显著提升专业认可与收费能力。"}],
))

# 5. Fitness Instructor 452111 —— 非移民
OCCS.append(dict(
    occ_code="452111", anzsco_code="452111", anzsco_title="Fitness Instructor", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["私人教练（PT）", "团课教练（HIIT/动感单车）", "线上健身课程", "专项人群（产后/银发/康复）"],
    name_zh="健身教练", name_en="Fitness Instructor",
    summary_zh="健身教练（含私人教练）指导个人或团体进行体能训练与健康管理，工作于健身房、工作室或上门/线上。多为按课时或自雇，收入与客户量、留存和口碑强相关，资深 PT 与自营者收入可观。",
    summary_en="Fitness instructors (including personal trainers) guide individuals or groups in physical training and wellbeing, working in gyms, studios, mobile or online. Many are paid per session or self-employed, with income tied to client base, retention and reputation; senior PTs and owners can earn well.",
    forecast_zh="健康意识提升推动健身行业稳定增长；私人教练、线上课程和专项人群（产后/银发/康复）是增量方向。岗位多为兼职/自雇，需自我营销与客户经营。",
    trend_zh="线上+线下混合训练成为常态；专项化（功能性/康复/营养结合）提升单价与留存。",
    edu=[{"stage": "Certificate III in Fitness（SIS30321）", "duration": "3~6个月", "cost_min": 1500, "cost_max": 6000, "cost_note": "团课/助理教练入门资质", "sort_order": 0},
         {"stage": "Certificate IV in Fitness（私人教练 PT）", "duration": "6~12个月", "cost_min": 2500, "cost_max": 9000, "cost_note": "独立带私教的行业标准资质", "sort_order": 1}],
    quals=[{"qual_name": "Certificate IV in Fitness（SIS40221）", "issuer": "认可 RTO", "note": "独立从事私人教练的行业标准", "is_mandatory": 1, "sort_order": 0},
           {"qual_name": "急救与 CPR 证书 + 行业注册（AusREP/Fitness Australia）", "issuer": "Fitness Australia 等", "note": "执业与保险常见要求", "is_mandatory": 1, "sort_order": 1}],
    sal=[{"experience": "初级/团课教练", "salary_min": 45000, "salary_max": 60000, "salary_note": "按课时/兼职常见", "sort_order": 0},
         {"experience": "私人教练（PT）", "salary_min": 55000, "salary_max": 80000, "salary_note": "客户量决定收入", "sort_order": 1},
         {"experience": "资深 PT/自营工作室", "salary_min": 80000, "salary_max": 150000, "salary_note": "高留存客群+团课+线上", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("中低", 4.0, "Cert III/IV 入门门槛不高"),
        ("低", 3.0, "数月可取证"),
        ("中低", 4.0, "需行业注册+急救证"),
        ("中高", 6.0, "健身需求增长，岗位多但多兼职"),
        ("中高", 6.0, "PT 市场竞争较强，靠留存"),
        ("中高", 6.0, "早晚高峰+体力示范"),
        ("中等", 5.0, "按客户量；自营可观"),
        ("中高", 6.0, "健康意识推动稳定增长"),
        ("中低", 4.0, "线上课/AI 计划冲击标准化训练，但现场指导与激励难替代"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["热爱运动并善于激励他人", "愿意经营客户与个人品牌", "可接受早晚高峰与兼职起步"],
    unfit=["追求固定坐班与稳定月薪", "以移民为主要目标", "不愿做客户开发与留存"],
    sources=[{"source_name": "SEEK AU", "content": "Fitness Instructor / PT 薪资区间", "url": "https://au.seek.com/career-advice"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲健身教练收入多少？", "answer": "初级/团课约 $45k~$60k；私人教练约 $55k~$80k（客户量决定）；资深 PT/自营工作室约 $80k~$150k。多为按课时或自雇。"},
          {"faq_type": "difficulty", "sort_order": 1, "question": "健身教练能技术移民吗？", "answer": "不能直接技术移民。Fitness Instructor (452111) 不在 CSOL 或 GSM 技术移民清单上。"},
          {"faq_type": "education_limit", "sort_order": 2, "question": "当健身教练需要什么资质？", "answer": "团课入门需 Certificate III in Fitness；独立带私教需 Certificate IV in Fitness，并通常需急救/CPR 证书与行业注册（如 AusREP）。无需大学学历。"}],
))

# 6. Yoga Instructor （占位 occ_code，anzsco 452111）—— 非移民
OCCS.append(dict(
    occ_code="452111Y", anzsco_code="452111", anzsco_title="Yoga Instructor", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["工作室团课", "私教/企业瑜伽", "线上课程与会员", "孕产/理疗瑜伽细分"],
    name_zh="瑜伽教练", name_en="Yoga Instructor",
    summary_zh="瑜伽教练带领团体或私人瑜伽课程，涵盖哈他、流瑜伽、阴瑜伽及孕产/理疗等方向（ANZSCO 归入 452111 Fitness Instructor）。多为按课时或自营，收入与排课量、私教和线上会员相关。",
    summary_en="Yoga instructors lead group or private yoga classes across hatha, vinyasa, yin and prenatal/therapeutic styles (classified under ANZSCO 452111 Fitness Instructor). Most are paid per class or self-employed, with income tied to class volume, private clients and online memberships.",
    forecast_zh="身心健康与减压需求推动瑜伽稳定增长；企业瑜伽、孕产与理疗方向单价较高。岗位以兼职/自雇为主，个人品牌与社群经营是关键。",
    trend_zh="线上会员制与录播课成为重要收入来源；理疗/孕产等专项方向提升专业溢价。",
    edu=[{"stage": "瑜伽教师培训（200/500 小时 RYT）", "duration": "1~6个月", "cost_min": 2000, "cost_max": 8000, "cost_note": "国际通行的 Yoga Alliance RYT 认证", "sort_order": 0},
         {"stage": "急救与 CPR 证书", "duration": "1天", "cost_min": 100, "cost_max": 250, "cost_note": "执业与保险常见要求", "sort_order": 1}],
    quals=[{"qual_name": "Registered Yoga Teacher（RYT-200/500）", "issuer": "Yoga Alliance / 认可培训机构", "note": "行业通行资质", "is_mandatory": 0, "sort_order": 0},
           {"qual_name": "急救/CPR + 职业责任保险", "issuer": "—", "note": "工作室授课与自营常见要求", "is_mandatory": 1, "sort_order": 1}],
    sal=[{"experience": "兼职瑜伽教练", "salary_min": 40000, "salary_max": 58000, "salary_note": "按课时，$50~$90/节常见", "sort_order": 0},
         {"experience": "全职瑜伽教练", "salary_min": 55000, "salary_max": 78000, "salary_note": "稳定排课+私教", "sort_order": 1},
         {"experience": "资深/自营工作室", "salary_min": 78000, "salary_max": 140000, "salary_note": "团课+私教+线上会员", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("中低", 4.0, "RYT 培训门槛适中"),
        ("低", 3.0, "数月可取证"),
        ("中低", 4.0, "RYT 非强制，但需急救/保险"),
        ("中等", 5.0, "需求稳定增长，多兼职"),
        ("中高", 6.0, "热门城市竞争较强"),
        ("中等", 5.0, "早晚课为主，体力适中"),
        ("中等", 5.0, "按课时；专项与自营更高"),
        ("中高", 6.0, "身心健康需求推动增长"),
        ("很低", 3.0, "现场指导与体式纠正难被 AI 替代"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["热爱瑜伽并持续精进", "善于社群与个人品牌经营", "对孕产/理疗等专项有兴趣"],
    unfit=["追求固定坐班与稳定月薪", "以移民为主要目标", "不愿经营客户与线上内容"],
    sources=[{"source_name": "SEEK AU", "content": "Yoga / Fitness Instructor 薪资区间", "url": "https://au.seek.com/career-advice"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲瑜伽教练收入多少？", "answer": "兼职约 $40k~$58k（$50~$90/节）；全职约 $55k~$78k；资深/自营工作室约 $78k~$140k（含线上会员）。"},
          {"faq_type": "difficulty", "sort_order": 1, "question": "瑜伽教练能技术移民吗？", "answer": "不能直接技术移民。瑜伽教练在 ANZSCO 归入 Fitness Instructor (452111)，不在 CSOL 或 GSM 技术移民清单上。"},
          {"faq_type": "education_limit", "sort_order": 2, "question": "当瑜伽教练需要什么资质？", "answer": "行业通行的是 200/500 小时 RYT（Yoga Alliance）认证；工作室授课与自营通常需急救/CPR 证书与职业责任保险。无需大学学历。"}],
))

# 7. Swimming Coach or Instructor 452316 —— 非移民
OCCS.append(dict(
    occ_code="452316", anzsco_code="452316", anzsco_title="Swimming Coach or Instructor", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["少儿游泳培训（Learn to Swim）", "竞技游泳教练", "水中康复/水疗", "救生与水安全培训"],
    name_zh="游泳教练", name_en="Swimming Coach or Instructor",
    summary_zh="游泳教练教授游泳技能与水安全，涵盖少儿启蒙、成人培训与竞技训练，工作于泳池、游泳学校或俱乐部。需持教练与救生资质，岗位以兼职/季节性为主，资深竞技教练收入较高。",
    summary_en="Swimming coaches teach swimming and water safety from learn-to-swim through to competitive squads, working at pools, swim schools and clubs. Coaching and lifesaving qualifications are required; roles are often part-time/seasonal, with senior competitive coaches earning more.",
    forecast_zh="澳洲水上文化与强制水安全教育支撑稳定需求；少儿游泳培训长期刚需，行业普遍缺合格教练。竞技与康复方向提供进阶空间。",
    trend_zh="Learn to Swim 少儿培训是主力刚需市场；合格教练短缺使排课充足。",
    edu=[{"stage": "AUSTSWIM / Swim Australia 教练资格", "duration": "数天~数周", "cost_min": 300, "cost_max": 1200, "cost_note": "教授游泳的行业资格", "sort_order": 0},
         {"stage": "救生与 CPR 资质 + WWCC", "duration": "数天", "cost_min": 200, "cost_max": 600, "cost_note": "水安全与教未成年人的法定要求", "sort_order": 1}],
    quals=[{"qual_name": "AUSTSWIM Teacher of Swimming and Water Safety", "issuer": "AUSTSWIM", "note": "行业标准教学资格", "is_mandatory": 1, "sort_order": 0},
           {"qual_name": "Working with Children Check + 急救/CPR", "issuer": "各州 / 认可机构", "note": "教未成年人与水安全要求", "is_mandatory": 1, "sort_order": 1}],
    sal=[{"experience": "兼职/初级游泳教练", "salary_min": 35000, "salary_max": 55000, "salary_note": "$28~$45/时，季节性", "sort_order": 0},
         {"experience": "全职游泳教练", "salary_min": 55000, "salary_max": 72000, "salary_note": "稳定排课+squad", "sort_order": 1},
         {"experience": "竞技/高级教练", "salary_min": 72000, "salary_max": 110000, "salary_note": "俱乐部竞技队/高水平训练", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("中低", 4.0, "教练资格培训门槛适中"),
        ("低", 3.0, "数周可取证"),
        ("中低", 4.0, "需 AUSTSWIM+救生+WWCC"),
        ("中高", 7.0, "合格教练短缺，排课充足"),
        ("中低", 4.0, "需求大于供给，竞争不强"),
        ("中高", 6.0, "早晚课+下水，体力要求高"),
        ("中等", 5.0, "竞技/全职更高"),
        ("中高", 6.0, "少儿培训刚需稳定"),
        ("很低", 2.0, "现场水中教学与安全难被替代"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["擅长游泳并喜欢与儿童/学员互动", "愿意早晚与周末排课", "可考取 AUSTSWIM+救生资质"],
    unfit=["不愿下水或长时间在泳池环境", "以移民为主要目标", "追求固定白领坐班"],
    sources=[{"source_name": "AUSTSWIM", "content": "游泳教学资格与行业信息", "url": "https://austswim.com.au/"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲游泳教练收入多少？", "answer": "兼职/初级约 $35k~$55k（$28~$45/时，季节性）；全职约 $55k~$72k；竞技/高级教练约 $72k~$110k。"},
          {"faq_type": "demand", "sort_order": 1, "question": "澳洲游泳教练好找工作吗？", "answer": "较好。强制水安全教育与水上文化支撑稳定刚需，少儿 Learn to Swim 市场长期缺合格教练，排课通常充足。"},
          {"faq_type": "difficulty", "sort_order": 2, "question": "游泳教练能技术移民吗？", "answer": "不能直接技术移民。Swimming Coach or Instructor (452316) 不在 CSOL 或 GSM 技术移民清单上（注意：通用的 Sports Coach 452317 在 CSOL 上，可雇主担保）。"}],
))

# 8. Sports Coach or Instructor 452317 —— 受限移民(2, CSOL)
OCCS.append(dict(
    occ_code="452317", anzsco_code="452317", anzsco_title="Sports Coach or Instructor", category=CREATIVE, is_migration=2,
    workforce_size=None, shortage=0,
    growth=["职业/半职业球队教练", "青少年体育学院", "专项技术教练", "体能与运动表现"],
    name_zh="体育教练", name_en="Sports Coach or Instructor",
    summary_zh="体育教练训练并指导运动员或队伍提升竞技水平，涵盖各类球类与运动项目，工作于俱乐部、学校、学院与职业队。该职业在澳洲 CSOL 清单上，可走雇主担保移民；薪资随级别差异大，职业队与高水平教练收入较高。",
    summary_en="Sports coaches train and develop athletes and teams across many sports, working in clubs, schools, academies and professional teams. The occupation is on Australia's CSOL, enabling employer-sponsored migration; pay varies widely, with professional and high-performance coaches earning more.",
    forecast_zh="体育产业与青少年体育培训稳定增长；高水平与专项教练需求较好。该职业在 CSOL 上，符合条件的俱乐部/学院可通过 482 担保海外教练。",
    trend_zh="数据与运动科学（GPS/表现分析）日益融入训练；专项化与持证化提升议价能力。",
    edu=[{"stage": "专项教练认证（各运动协会 Level 1/2/3）", "duration": "数周~数年（逐级）", "cost_min": 200, "cost_max": 5000, "cost_note": "各运动项目国家协会的教练认证体系", "sort_order": 0},
         {"stage": "运动科学/体育相关学位（高水平方向，可选）", "duration": "3年", "cost_min": 30000, "cost_max": 90000, "cost_note": "职业队/学院高级岗位常见", "sort_order": 1},
         {"stage": "急救/CPR + WWCC", "duration": "数天", "cost_min": 200, "cost_max": 600, "cost_note": "执业与教未成年人的常见要求", "sort_order": 2}],
    quals=[{"qual_name": "国家运动协会教练认证（NCAS 等）", "issuer": "各运动项目协会", "note": "执教资质；级别决定可执教层次", "is_mandatory": 1, "sort_order": 0},
           {"qual_name": "VETASSESS 技能评估（雇主担保）", "issuer": "VETASSESS", "note": "482 等提名常需职业技能评估", "is_mandatory": 0, "sort_order": 1}],
    sal=[{"experience": "初级/社区教练", "salary_min": 50000, "salary_max": 65000, "salary_note": "兼职常见", "sort_order": 0},
         {"experience": "全职专项教练", "salary_min": 65000, "salary_max": 95000, "salary_note": "俱乐部/学院", "sort_order": 1},
         {"experience": "高水平/职业队教练", "salary_min": 95000, "salary_max": 200000, "salary_note": "职业与精英方向溢价显著", "sort_order": 2}],
    visa=RESTRICTED_VISA,
    ratings=ratings([
        ("中等", 5.0, "需专项技术+逐级教练认证"),
        ("中等", 6.0, "高水平资历积累周期长"),
        ("中等", 5.0, "需协会认证+WWCC"),
        ("中等", 6.0, "高水平/专项需求较好"),
        ("中高", 6.0, "高端岗位竞争激烈"),
        ("中高", 6.0, "训练+赛事，作息不规律"),
        ("中高", 6.0, "职业队/精英方向高收入"),
        ("中高", 6.0, "体育产业稳定增长"),
        ("低", 3.0, "数据分析辅助训练，但现场指导难替代"),
        ("中等", 5.0, "在 CSOL，可雇主担保（非独立技术移民）"),
        ("中高", 7.0, "无 189/190 直通；仅 482/494/DAMA"),
    ]),
    fit=["有专项运动背景并取得教练认证", "愿意走雇主担保（俱乐部/学院 482）路径", "能适应赛事与不规律作息"],
    unfit=["期望独立技术移民（本职业仅雇主担保/DAMA）", "不愿逐级考取教练认证", "追求固定坐班白领节奏"],
    sources=[{"source_name": "Department of Home Affairs", "content": "Core Skills Occupation List（含 452317）", "url": "https://immi.homeaffairs.gov.au/Documents/core-sol.pdf"},
             {"source_name": "Jobs and Skills Australia", "content": "体育教练职业概况", "url": "https://www.jobsandskills.gov.au/"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲体育教练收入多少？", "answer": "初级/社区约 $50k~$65k；全职专项约 $65k~$95k；高水平/职业队教练约 $95k~$200k+。差异主要由级别与项目决定。"},
          {"faq_type": "difficulty", "sort_order": 1, "question": "体育教练能移民澳洲吗？", "answer": "可以，但受限。Sports Coach or Instructor (452317) 在 CSOL 上，可通过雇主担保（482 Skills in Demand、494 偏远地区）或 DAMA 移民；不在独立技术移民（189/190）清单上，无法直接积分移民。"},
          {"faq_type": "ai_risk", "sort_order": 2, "question": "体育教练会被 AI 替代吗？", "answer": "风险低。数据分析、运动科学与可穿戴设备会增强训练，但临场指导、战术判断、激励与人际信任难以被替代。会用数据工具的教练更具竞争力。"}],
))

# 9. Driving Instructor 451511 —— 非移民
OCCS.append(dict(
    occ_code="451511", anzsco_code="451511", anzsco_title="Driving Instructor", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["普通汽车（C 类）教练", "重型车（HR/HC/MC）驾照教练", "考前路考辅导", "自营驾校"],
    name_zh="驾驶教练", name_en="Driving Instructor",
    summary_zh="驾驶教练教授学员驾驶技能并辅导路考，涵盖普通汽车（C 类）与重型货车（HR/HC/MC，即卡车驾照）培训。需持各州驾驶教练执照，多为自雇/自营，收入与课时量和驾校经营相关，重型车教练单价更高。",
    summary_en="Driving instructors teach learners to drive and prepare them for licence tests, covering standard cars (Class C) and heavy vehicles (HR/HC/MC, i.e. truck licences). A state driving-instructor licence is required; most are self-employed, with income tied to lesson volume and (for heavy-vehicle training) higher rates.",
    forecast_zh="人口增长与持续的考照需求支撑稳定市场；重型车（卡车）驾照培训因物流业司机短缺需求旺盛、单价高。岗位以自雇/自营为主。",
    trend_zh="重型车驾照（HR/HC/MC）培训需求随物流业司机短缺上升；自营驾校与挂靠并存。",
    edu=[{"stage": "各州驾驶教练执照（Driving Instructor Authority）", "duration": "数周~数月", "cost_min": 2000, "cost_max": 6000, "cost_note": "含 Certificate IV in Driving Instruction 等要求，按州不同", "sort_order": 0},
         {"stage": "重型车驾照与重型车教练资质（可选，单价更高）", "duration": "数周", "cost_min": 1500, "cost_max": 6000, "cost_note": "教授 HR/HC/MC 需相应等级驾照与认证", "sort_order": 1}],
    quals=[{"qual_name": "驾驶教练执照（各州主管交通部门）", "issuer": "各州交通主管部门", "note": "合法教学的法定资质；含背景审查", "is_mandatory": 1, "sort_order": 0},
           {"qual_name": "Certificate IV in Driving Instruction（TLI41222 等）", "issuer": "认可 RTO", "note": "多数州的执照前置要求", "is_mandatory": 1, "sort_order": 1}],
    sal=[{"experience": "兼职/初级教练", "salary_min": 50000, "salary_max": 65000, "salary_note": "按课时；自雇起步", "sort_order": 0},
         {"experience": "全职驾驶教练", "salary_min": 65000, "salary_max": 85000, "salary_note": "稳定课表/自营", "sort_order": 1},
         {"experience": "重型车教练/驾校经营", "salary_min": 85000, "salary_max": 130000, "salary_note": "卡车驾照培训单价高+经营收入", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("中低", 4.0, "Cert IV+执照，门槛适中"),
        ("低", 3.0, "数周~数月取证"),
        ("中等", 5.0, "需执照+背景审查"),
        ("中高", 6.0, "考照刚需；卡车教练需求旺"),
        ("中低", 4.0, "本地化经营，竞争中等"),
        ("中等", 5.0, "户外驾车，作息较灵活"),
        ("中等", 5.0, "自营/重型车更高"),
        ("中高", 6.0, "刚需稳定；卡车方向增长"),
        ("很低", 2.0, "陪驾路考辅导难被自动化替代"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["有耐心、善于教学且驾驶经验丰富", "愿意自雇/自营经营", "可考取重型车驾照拓展卡车培训业务"],
    unfit=["不喜欢长时间在车内陪驾", "以移民为主要目标", "不愿做自营客户经营"],
    sources=[{"source_name": "各州交通主管部门", "content": "驾驶教练执照要求", "url": "https://www.service.nsw.gov.au/"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲驾驶教练收入多少？", "answer": "兼职/初级约 $50k~$65k；全职约 $65k~$85k；重型车（卡车驾照）教练或驾校经营者约 $85k~$130k（卡车培训单价更高）。"},
          {"faq_type": "education_limit", "sort_order": 1, "question": "当驾驶教练需要什么资质？", "answer": "需取得所在州的驾驶教练执照（通常以 Certificate IV in Driving Instruction 为前置），并通过背景审查。教授重型车（HR/HC/MC）需相应等级驾照与认证。"},
          {"faq_type": "difficulty", "sort_order": 2, "question": "驾驶教练能技术移民吗？", "answer": "不能直接技术移民。Driving Instructor (451511) 不在 CSOL 或 GSM 技术移民清单上。"}],
))

# 10. Outdoor Adventure Instructor 452413 —— 非移民
OCCS.append(dict(
    occ_code="452413", anzsco_code="452413", anzsco_title="Outdoor Adventure Instructor", category=CREATIVE, is_migration=0,
    workforce_size=None, shortage=0,
    growth=["滑翔伞/跳伞", "攀岩/绳索", "皮划艇/漂流", "丛林徒步与营地教育"],
    name_zh="户外探险教练", name_en="Outdoor Adventure Instructor",
    summary_zh="户外探险教练带领并指导滑翔伞、攀岩、皮划艇、漂流、丛林徒步等户外活动，负责技能教学与安全管理。需持专项资质与急救证书，岗位多为季节性/合同制，与旅游和户外教育市场强相关。",
    summary_en="Outdoor adventure instructors lead and instruct activities such as paragliding, climbing, kayaking, rafting and bushwalking, handling skills instruction and safety. Specialist qualifications and first aid are required; roles are often seasonal/contract and tied to tourism and outdoor education.",
    forecast_zh="户外旅游与体验式教育需求增长，专项（滑翔伞/攀岩/水上）合格教练较稀缺；多为季节性与合同岗位，安全责任要求高。",
    trend_zh="体验式与冒险旅游增长；专项资质与安全记录是核心竞争力。",
    edu=[{"stage": "专项户外资质（如 APA 滑翔伞、攀岩/绳索、皮划艇等）", "duration": "数周~数年（逐项）", "cost_min": 1000, "cost_max": 10000, "cost_note": "各专项协会的教练/向导认证", "sort_order": 0},
         {"stage": "野外急救（Wilderness First Aid）+ WWCC", "duration": "数天", "cost_min": 300, "cost_max": 1000, "cost_note": "户外安全与带未成年人的法定要求", "sort_order": 1}],
    quals=[{"qual_name": "专项户外教练/向导认证", "issuer": "各专项协会（如 APA、PADI 等）", "note": "合法带队与保险要求", "is_mandatory": 1, "sort_order": 0},
           {"qual_name": "野外急救 + WWCC", "issuer": "认可机构 / 各州", "note": "安全与带未成年人的法定要求", "is_mandatory": 1, "sort_order": 1}],
    sal=[{"experience": "季节性/初级教练", "salary_min": 45000, "salary_max": 58000, "salary_note": "季节性，按项目计酬", "sort_order": 0},
         {"experience": "全职户外教练", "salary_min": 55000, "salary_max": 72000, "salary_note": "稳定带队+多专项", "sort_order": 1},
         {"experience": "资深/自营运营者", "salary_min": 72000, "salary_max": 120000, "salary_note": "自营探险旅游/培训公司", "sort_order": 2}],
    visa=NONMIG_VISA,
    ratings=ratings([
        ("中等", 5.0, "需专项技能+安全管理能力"),
        ("中等", 6.0, "多专项资质逐项积累"),
        ("中等", 5.0, "需专项认证+野外急救"),
        ("中等", 5.0, "旅游/户外教育需求增长，季节性"),
        ("中低", 4.0, "合格专项教练较稀缺"),
        ("高", 7.0, "户外体力强度高，有安全责任"),
        ("中等", 5.0, "自营/资深更高"),
        ("中高", 6.0, "体验式旅游增长"),
        ("很低", 2.0, "现场带队与安全判断难被替代"),
        ("很低", 2.0, "不在技术移民清单上"),
        ("很高", 9.0, "几乎无独立技术移民通道"),
    ]),
    fit=["热爱户外并具备专项技能与安全意识", "可接受季节性/合同制与户外作息", "愿意考取多项专项与急救资质"],
    unfit=["偏好室内稳定坐班", "以移民为主要目标", "难以承担户外安全责任与体力强度"],
    sources=[{"source_name": "Jobs and Skills Australia", "content": "户外/旅游教练职业概况", "url": "https://www.jobsandskills.gov.au/"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（本职业未列入）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲户外探险教练收入多少？", "answer": "季节性/初级约 $45k~$58k；全职约 $55k~$72k；资深/自营探险运营者约 $72k~$120k。"},
          {"faq_type": "education_limit", "sort_order": 1, "question": "当户外探险教练需要什么资质？", "answer": "需取得相应专项（滑翔伞、攀岩、皮划艇等）的协会教练/向导认证，并持野外急救证书；带未成年人需 WWCC。安全记录与保险是执业关键。"},
          {"faq_type": "difficulty", "sort_order": 2, "question": "户外探险教练能技术移民吗？", "answer": "不能直接技术移民。Outdoor Adventure Instructor (452413) 不在 CSOL 或 GSM 技术移民清单上。"}],
))

# 11. Nutritionist 251112 —— 可直接技术移民(1, GSM/MLTSSL)
OCCS.append(dict(
    occ_code="251112", anzsco_code="251112", anzsco_title="Nutritionist", category=HEALTH, is_migration=1,
    workforce_size=None, shortage=0,
    growth=["公共卫生与社区营养", "食品行业（研发/标签合规）", "私人执业与企业健康", "运动营养"],
    name_zh="营养师", name_en="Nutritionist",
    summary_zh="营养师运用营养科学改善个人与人群的饮食与健康，工作于公共卫生、社区、食品企业与私人执业等领域（需本科及以上）。与营养治疗师（Dietitian）不同，营养师一般不提供临床医学营养治疗。营养师在 GSM 技术移民清单上，可走 189/190/491；但不在 482 的 CSOL 上。",
    summary_en="Nutritionists apply nutrition science to improve diet and health for individuals and populations, working in public health, community, food industry and private practice (bachelor degree or above). Unlike Dietitians, nutritionists generally do not provide clinical medical nutrition therapy. The occupation is on the GSM skilled lists (189/190/491) though not on the 482 CSOL.",
    forecast_zh="健康与预防医学意识提升推动营养相关岗位增长；公共卫生、食品行业合规与运动营养是活跃方向。营养师为技能等级 1 的专业职业，是较友好的技术移民职业之一（VETASSESS 评估）。",
    trend_zh="预防健康、食品标签合规与个性化营养（含数据/可穿戴）兴起；与 Dietitian 的执业边界需注意区分。",
    edu=[{"stage": "Bachelor of Nutrition / Nutrition Science（营养学学士）", "duration": "3年", "cost_min": 30000, "cost_max": 90000, "cost_note": "技术移民与执业的基础学历", "sort_order": 0},
         {"stage": "硕士（公共卫生营养/运动营养，可选）", "duration": "1.5~2年", "cost_min": 35000, "cost_max": 80000, "cost_note": "提升专业方向与就业竞争力", "sort_order": 1}],
    quals=[{"qual_name": "营养学本科及以上学历", "issuer": "认可大学", "note": "执业与技能评估的基础", "is_mandatory": 1, "sort_order": 0},
           {"qual_name": "VETASSESS 技能评估（移民）", "issuer": "VETASSESS", "note": "189/190/491 技术移民评估机构", "is_mandatory": 0, "sort_order": 1},
           {"qual_name": "Nutrition Society of Australia 注册（RNutr，可选）", "issuer": "NSA", "note": "提升专业认可度", "is_mandatory": 0, "sort_order": 2}],
    sal=[{"experience": "初级营养师（0~2年）", "salary_min": 60000, "salary_max": 72000, "salary_note": "社区/公共卫生起薪", "sort_order": 0},
         {"experience": "有经验营养师（2~8年）", "salary_min": 72000, "salary_max": 95000, "salary_note": "食品行业/私人执业更高", "sort_order": 1},
         {"experience": "资深/管理或私人执业", "salary_min": 95000, "salary_max": 130000, "salary_note": "管理岗/自营/企业健康", "sort_order": 2}],
    visa=GSM_VISA,
    ratings=ratings([
        ("中高", 6.0, "需营养学本科及以上"),
        ("高", 7.0, "学位+评估周期较长"),
        ("中等", 5.0, "需学历评估；注意与 Dietitian 区分"),
        ("中等", 6.0, "公共卫生与食品行业需求稳定"),
        ("中高", 6.0, "与 Dietitian/教练有交叉竞争"),
        ("中等", 5.0, "多为常规工作时间"),
        ("中高", 6.0, "专业岗位收入中上"),
        ("中高", 7.0, "预防健康趋势利好"),
        ("中低", 4.0, "AI 辅助饮食建议，但个体评估与行为干预仍需专业人"),
        ("中高", 7.0, "在 GSM 清单（189/190/491）"),
        ("中等", 5.0, "可积分移民，但需评估与较高英语/分数"),
    ]),
    fit=["有营养学本科及以上学历", "希望走技术移民（189/190/491）路径", "对公共卫生/食品行业/运动营养有兴趣"],
    unfit=["无相关学位且不愿进修", "想做临床医学营养治疗（那是 Dietitian 的范畴）", "期望短期低门槛快速入行"],
    sources=[{"source_name": "VETASSESS", "content": "Nutritionist (251112) 技能评估信息", "url": "https://www.vetassess.com.au/check-my-occupation/professional-occupations/nutritionist"},
             {"source_name": "Department of Home Affairs", "content": "技术职业清单（GSM）", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
             {"source_name": "Jobs and Skills Australia", "content": "营养专业职业概况（2511）", "url": "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/2511-nutrition-professionals"}],
    faqs=[{"faq_type": "salary", "sort_order": 0, "question": "澳洲营养师收入多少？", "answer": "初级约 $60k~$72k；有经验约 $72k~$95k（食品行业/私人执业更高）；资深/管理或私人执业约 $95k~$130k。"},
          {"faq_type": "difficulty", "sort_order": 1, "question": "营养师能技术移民澳洲吗？", "answer": "可以。Nutritionist (251112) 在 GSM 技术移民清单上，可走 189/190/491（需 VETASSESS 评估与较好英语/分数）；但不在 482 的 CSOL 上，雇主担保 482 仅限劳务协议。"},
          {"faq_type": "comparison", "sort_order": 2, "question": "营养师和营养治疗师（Dietitian）有什么区别？", "answer": "Dietitian（251111）受更严格的临床注册管理，可在医院提供医学营养治疗（MNT），且在多数移民与医保体系中认可度更高；Nutritionist（251112）侧重公共卫生、社区、食品行业与一般营养指导，通常不做临床治疗。两者都在技术移民清单上。"}],
))


def run():
    with get_cursor() as cur:
        for o in OCCS:
            OCC = {"country_code": "AU", "occ_code": o["occ_code"], "occ_code_type": "ANZSCO",
                   "anzsco_code": o["anzsco_code"], "anzsco_title": o["anzsco_title"],
                   "category": o["category"], "currency": "AUD", "workforce_size": o["workforce_size"],
                   "shortage_listed": o["shortage"], "is_migration": o["is_migration"], "is_public_servant": 0,
                   "growth_areas": json.dumps(o["growth"], ensure_ascii=False)}
            I18N_ZH = {"locale": "zh-CN", "name": o["name_zh"], "summary": o["summary_zh"],
                       "forecast_note": o["forecast_zh"], "trend_summary": o["trend_zh"]}
            I18N_EN = {"locale": "en", "name": o["name_en"], "summary": o["summary_en"],
                       "forecast_note": "", "trend_summary": ""}
            seed_occupation_v2(cur, OCC, I18N_ZH, I18N_EN, o["edu"], o["quals"], jl(), o["sal"],
                               o["visa"], o["ratings"], o["fit"], o["unfit"], o["sources"], o["faqs"])
    print(f"\n[OK] 新增/更新 {len(OCCS)} 个职业完成")


if __name__ == "__main__":
    run()
