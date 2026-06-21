"""澳洲测量师/建筑测量师（232611/312512）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "232611", "anzsco_title": "Land Surveyor / Building Surveyor",
    "category": "其他", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["无人机测量（UAV Survey）和激光雷达（LiDAR）","BIM（建筑信息模型）与数字测量整合","矿区测量（WA/QLD矿业繁荣）","基础设施测量（铁路/公路大型项目）","建筑/工程量测量师（Quantity Surveyor）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "测量师/建筑测量师",
    "summary": "测量师（Land Surveyor）确定土地界限、坐标和地形特征，是建筑开发和基础设施工程的基础专业；建筑测量师（Building Surveyor）负责建筑审批、法规合规和竣工检查；工程量测量师（Quantity Surveyor）负责建设成本估算和合同管理。三类测量师均在澳洲技术短缺名单，就业市场强劲。",
    "forecast_note": "JSA预测测量师就业至2030年增长约12%。澳洲大规模基础设施投资（铁路/公路/住房供应计划）和矿业扩张持续推动需求。无人机和激光扫描技术正在提升测量效率并创造新专业方向。",
    "trend_summary": "澳洲各州政府大规模基础设施投资（NSW Suburban Rail Loop/QLD Olympics基础设施/WA METRONET）创造大量测量岗位。无人机测量（UAV）和BIM数字建模正在改变行业工作方式，掌握这些技术的测量师需求量大且薪资溢价显著。WA矿业繁荣推动矿区测量师（Mine Surveyor）薪资超过 $160k。",
}
I18N_EN = {
    "locale": "en", "name": "Land Surveyor / Building Surveyor",
    "summary": "Land surveyors determine land boundaries, coordinates and topographic features — a foundational profession for construction development and infrastructure. Building surveyors handle building approvals, regulatory compliance and completion inspections. Quantity surveyors manage construction cost estimation and contract management. All three surveyor types appear on Australian skill shortage lists with strong employment markets.",
    "forecast_note": "JSA projects ~12% surveyor employment growth by 2030. Australia's large-scale infrastructure investment (rail/roads/housing supply plans) and mining expansion continue to drive demand. Drone and laser scanning technology is improving survey efficiency and creating new specialist directions.",
    "trend_summary": "State government infrastructure investments (NSW Suburban Rail Loop/QLD Olympics infrastructure/WA METRONET) are creating large numbers of surveying roles. UAV drone surveying and BIM digital modelling are transforming industry workflows — surveyors with these skills see strong demand and significant salary premiums. WA mining boom drives mine surveyor salaries above $160k.",
}
EDUCATION = [
    {"stage": "Bachelor of Surveying / Geospatial Science（3~4年）", "duration": "3~4年", "cost_min": 30000, "cost_max": 130000, "cost_note": "主要澳洲大学提供测量学位；国际生约 $28,000~$40,000/年", "sort_order": 0},
    {"stage": "Registered Surveyor（注册测量师，职业执照）", "duration": "学位后2年专业经验", "cost_min": 500, "cost_max": 2000, "cost_note": "向各州测量师注册局申请；是独立执业的法律要求", "sort_order": 1},
    {"stage": "无人机（UAV）操作执照（RPA Operator Certificate）", "duration": "1~3天", "cost_min": 500, "cost_max": 2000, "cost_note": "CASA颁发；商业无人机测量的必要资质", "sort_order": 2},
    {"stage": "Vetassess/AIBS技能评估（移民）", "duration": "3~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民必须的学历和经验评估", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Registered Surveyor（注册测量师）", "issuer": "各州测量师注册局（如NSW BOSSI/VIC LMA）", "note": "独立执业的法律要求；是最高测量专业资质", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Bachelor of Surveying/Geospatial Science", "issuer": "BOSSI/AIBS认可大学", "note": "技术移民评估的基础学历要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "AIBS 会员资格（建筑测量师）", "issuer": "Australian Institute of Building Surveyors", "note": "建筑测量师专业资质；是建筑审批工作的行业标准", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "AIQS 会员资格（工程量测量师）", "issuer": "Australian Institute of Quantity Surveyors", "note": "QS专业认可资质；技术移民评估机构", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 400, "count_max": 1200, "note": "全国，含土地测量师/建筑测量师/工程量测量师各类岗"},
    {"platform": "Indeed",   "count_min": 300, "count_max": 900, "note": "含政府测量局、建筑公司和工程咨询公司岗"},
    {"platform": "LinkedIn", "count_min": 400, "count_max": 1200, "note": "大型工程测量公司（Aurecon/GHD/Jacobs）直招"},
]
SALARIES = [
    {"experience": "初级测量师（0~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "毕业生起薪；含Graduate Surveyor岗", "sort_order": 0},
    {"experience": "有经验测量师（3~8年）", "salary_min": 95000, "salary_max": 125000, "salary_note": "土地测量师 SEEK $100k~$120k；Indeed $114,081（2026）", "sort_order": 1},
    {"experience": "建筑测量师/工程量测量师（3~8年）", "salary_min": 105000, "salary_max": 135000, "salary_note": "建筑测量师 SEEK $110k~$130k；工程量测量师 SEEK $95k~$115k；Indeed $108,111（2026）", "sort_order": 2},
    {"experience": "注册测量师/高级（8年+）", "salary_min": 130000, "salary_max": 200000, "salary_note": "矿区测量师（WA）约 $150k~$200k；注册测量师高级岗 $130k+", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保；工程公司、矿业公司和政府测量机构担保活跃", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列（测量师类别）", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "各州基础设施重点项目积极提名（NSW/QLD/WA）", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区测量师极度短缺（WA内陆/QLD矿区）", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较高", "stars": 4, "note": "测量学/地理空间科学专业知识；法律/合规知识；数字技术工具"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学位3~4年；注册测量师需额外2年专业实践"},
    {"dimension": "certification_difficulty", "label_zh": "较高", "stars": 4, "note": "Vetassess/AIBS评估；注册执照要求工作经验证明"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "MLTSSL短缺职业；基础设施投资和矿业推动旺盛需求；SEEK 400~1200+职位"},
    {"dimension": "competition",              "label_zh": "低", "stars": 2, "note": "供不应求；有测量学位和GNSS/UAV技能者就业率接近100%"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "部分外业工作（户外测量）；矿区测量师FIFO（飞进飞出）作业"},
    {"dimension": "income_level",             "label_zh": "较高", "stars": 4, "note": "有经验测量师 $95k~$135k；矿区测量师 $150k~$200k；高薪技术职业"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "基础设施超级周期和矿业繁荣提供持续需求；UAV技术创造新机会"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI辅助数据处理和点云分析；但实地测量、法律合规决策不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列；各州积极提名；矿业公司担保活跃"},
    {"dimension": "pr_difficulty",            "label_zh": "很低", "stars": 1, "note": "短缺职业，PR路径顺畅；偏远矿区491路径最快"},
]
SUITABILITY_FIT = ["持有测量学/地理空间科学或相关工程学位，有3年以上测量工作经验", "熟悉GNSS/GPS测量技术、GIS软件（ArcGIS/MapInfo）和BIM平台", "持有或愿意申请CASA无人机操作执照（UAV Survey是当前最受欢迎技能）", "有意向在基础设施或矿业重点州（WA/QLD/NSW）工作", "愿意接受FIFO（飞进飞出）矿区工作安排（薪资显著更高）"]
SUITABILITY_UNFIT = ["持有土木工程或建筑设计学位但无专业测量学位（需要专门的测量学历）", "完全回避户外外业工作（测量工作有较多现场外业内容）", "期望快速注册成为独立执业测量师（注册需要学位+2年工作经验的积累）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "土地测量师 $100k~$120k；建筑测量师 $110k~$130k；QS $95k~$115k（2026）", "url": "https://au.seek.com/career-advice/role/land-surveyor/salary"},
    {"source_name": "Indeed AU", "content": "测量师均值 $114,081；QS均值 $108,111（2026）", "url": "https://au.indeed.com/career/land-surveyor/salaries"},
    {"source_name": "BOSSI NSW", "content": "NSW注册测量师信息", "url": "https://www.bossi.nsw.gov.au"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲测量师工资多少？", "answer": "初级测量师约 $70k~$90k；有经验土地测量师约 $95k~$125k（SEEK $100k~$120k；Indeed $114,081）；建筑测量师约 $105k~$135k（SEEK $110k~$130k）；工程量测量师约 $95k~$135k（Indeed $108,111）；矿区测量师约 $150k~$200k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲测量师容易找工作吗？", "answer": "非常容易。MLTSSL短缺职业，基础设施超级周期和矿业繁荣推动旺盛需求。SEEK常年在线400~1200+职位，有测量学位和UAV技能者就业率接近100%。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国测量经验澳洲认可吗？", "answer": "通过Vetassess（土地测量）或AIBS（建筑测量）/AIQS（工程量测量）技能评估，中国测量工作经验可以认可。需要提供英文项目经历证明。澳洲独立执业还需要注册测量师执照（学位+2年经验）。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "测量师会被AI替代吗？", "answer": "中等风险。AI辅助点云处理、地图生成和合规核查正在提升效率；但实地测量、法律边界裁定和建筑审批决策需要注册测量师的专业判断和法律责任承担。掌握UAV/BIM数字技术的测量师比纯传统外业测量师有更好的未来抗AI性。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲测量师有年龄限制吗？", "answer": "无。有丰富大型项目经验（基础设施/矿业）的资深注册测量师（40~55岁）在澳洲极为稀缺。外业体能要求较低（尤其建筑测量师和工程量测量师），是可持续发展至退休年龄的专业职业。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲测量师需要什么学历？", "answer": "Bachelor of Surveying / Geospatial Science是核心要求（3~4年）；建筑测量师可接受相关工程/建筑学位；工程量测量师可通过AIQS认可学位路径。持有中国测量相关学位者需通过技能评估机构（Vetassess/AIBS/AIQS）认可。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲测量师认证（移民）难吗？", "answer": "难度较低。测量师在MLTSSL，PR路径顺畅。Vetassess/AIBS评估路径清晰；各州基础设施项目积极提名190；矿业公司FIFO岗位雇主担保活跃。主要挑战是学历评估时间（3~6个月）和注册测量师执照的工作经验积累（2年）。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "土地测量师和工程量测量师哪个澳洲发展更好？", "answer": "土地测量师外业多、收入高（矿区 $150k~$200k），短缺更严重；工程量测量师（QS）以室内工作为主，就业市场更广（大量建设项目需要），薪资稳定（$95k~$135k）。喜欢户外测量技术和矿业机会选土地测量师；喜欢室内合同管理和成本控制选工程量测量师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 测量师/建筑测量师数据入库完成")

if __name__ == "__main__":
    run()
