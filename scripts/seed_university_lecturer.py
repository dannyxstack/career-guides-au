"""澳洲大学讲师（242111）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor、AcademicJobs（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "242111", "anzsco_title": "University Lecturer",
    "category": "教育/社会服务", "workforce_size": 55000, "shortage_listed": 0,
    "growth_areas": json.dumps(["AI & Data Science学术研究","在线教育与EdTech","国际学生教育（亚洲市场）","工程与技术学科","医疗健康研究"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "大学讲师（高校教师）",
    "summary": "大学讲师负责本科和研究生课程的教学、科研和学术服务，是澳洲高等教育体系的核心专业人员。澳洲37所大学提供稳定的学术就业市场，但竞争激烈，通常需要博士学位和发表记录。是学术背景人士的主流就业方向之一。",
    "forecast_note": "JSA预测大学讲师至2035年就业稳定增长约5%。AI与数据科学、网络安全和医疗健康相关学科的讲师需求增长最快，国际学生市场的持续活跃也支撑整体教学岗位数量。",
    "trend_summary": "澳洲高校正面临合同制教职（Casual/Sessional）比例过高的结构性问题，全职讲席（Continuing/Ongoing）竞争激烈。AI辅助教学和在线课程扩展对传统教学模式有影响，但科研产出和研究型讲师职位持续增长。",
}
I18N_EN = {
    "locale": "en", "name": "University Lecturer / Academic",
    "summary": "University lecturers teach undergraduate and postgraduate courses, conduct research and provide academic service — the core professionals of Australia's higher education system. Australia's 37 universities provide a stable academic employment market, though competition is intense and a doctoral degree with publication record is typically required.",
    "forecast_note": "JSA projects ~5% stable employment growth for university lecturers by 2035. AI and data science, cybersecurity and health-related disciplines have the fastest-growing lecturer demand. The active international student market also supports overall teaching position numbers.",
    "trend_summary": "Australian universities face structural issues with high proportions of casual/sessional contracts. Full continuing positions are highly competitive. AI-assisted teaching and online course expansion affect traditional delivery but research-focused positions continue to grow.",
}
EDUCATION = [
    {"stage": "博士学位（PhD，3~5年）", "duration": "3~5年（全日制）", "cost_min": 0, "cost_max": 150000, "cost_note": "博士学位是大学讲师职位的基本要求；澳洲公民/PR读博通常免学费；国际生约 $30,000~$42,000/年", "sort_order": 0},
    {"stage": "博士后研究（Postdoctoral Research，可选但竞争性强）", "duration": "1~3年", "cost_min": 0, "cost_max": 0, "cost_note": "博士后通常获得薪酬（HEW Level 6-7，约 $90,000~$100,000）；是竞争全职讲席前的主流学术路径", "sort_order": 1},
    {"stage": "学术英语和科研写作能力", "duration": "持续提升", "cost_min": 0, "cost_max": 5000, "cost_note": "期刊发表记录（Publication Record）和科研经费申请（Grant Application）能力是竞争讲席的关键", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "博士学位（PhD）", "issuer": "澳洲或国际认可大学", "note": "绝大多数大学讲师职位的硬性学历要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "高校教学资格认证（GCHE/教学法证书）", "issuer": "各大学教学与学习中心", "note": "部分大学要求，提升教学法能力和晋升竞争力", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "期刊发表记录（Publication Record）", "issuer": "学术期刊（Q1/ABDC A/A*）", "note": "不是正式证书，但是竞争全职讲席职位的实际必要条件", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "科研经费记录（ARC/NHMRC等）", "issuer": "澳洲科研委员会（ARC）等资助机构", "note": "是晋升副教授和教授的关键绩效指标", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 800, "count_max": 2500, "note": "全国，含讲师/高级讲师/副教授/教授和博士后岗"},
    {"platform": "Indeed",   "count_min": 600, "count_max": 2000, "note": "含37所大学的学术岗和研究员岗"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 3000, "note": "大学直招，学术猎头活跃"},
]
SALARIES = [
    {"experience": "博士后研究员（0~3年，HEW 6-7级）", "salary_min": 88000, "salary_max": 104000, "salary_note": "博士后典型薪资区间（全澳大学HEW薪资表）", "sort_order": 0},
    {"experience": "讲师 / Lecturer A/B（3~8年，HEW 8-9级）", "salary_min": 105000, "salary_max": 135000, "salary_note": "SEEK 区间 $125k~$130k；Indeed 均值 $124,444；Glassdoor 均值 $112,596（2026）", "sort_order": 1},
    {"experience": "高级讲师 / Senior Lecturer（8~15年）", "salary_min": 130000, "salary_max": 175000, "salary_note": "HEW 10级高级讲师，含科研绩效奖金", "sort_order": 2},
    {"experience": "副教授 / 教授（15年+）", "salary_min": 170000, "salary_max": 280000, "salary_note": "副教授约 $160k~$195k；教授约 $185k~$280k（含大学津贴和科研经费）", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，大学可直接担保学术岗位候选人", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居，大学担保路径成熟", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，需要技能评估+EOI，博士学位加分", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区大学（Armidale/Wagga Wagga等），加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "博士学位是最高学历，科研独立性和期刊发表能力要求极高"},
    {"dimension": "learning_duration",        "label_zh": "极长", "stars": 5, "note": "本科4年+硕士2年+博士3~5年+博士后2~3年=总周期可达12~15年"},
    {"dimension": "certification_difficulty", "label_zh": "极高", "stars": 5, "note": "博士毕业和科研发表记录是实际门槛；全职讲席竞争极激烈"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "全职continuing讲席稀少，合同制和临时岗位比例高；AI和数据科学学科供不应求"},
    {"dimension": "competition",              "label_zh": "很高", "stars": 4, "note": "全职讲席职位竞争极激烈，常有100+申请者；合同制博士后岗相对容易"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "教学+科研+行政三重任务；科研截止期和教学高峰期压力大"},
    {"dimension": "income_level",             "label_zh": "很高", "stars": 4, "note": "讲师 $105k~$135k；副教授/教授 $170k~$280k；整体薪资稳定且透明（HEW薪资表）"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "AI和EdTech对传统教学模式有挑战；科研型学者路径有持续增长"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "在线教学内容部分受AI影响，但原创科研、学术判断和学生指导不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "大学担保482路径活跃；博士学位加分（10分）有移民优势"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "大学雇主担保是主流路径；189/190评估需要技能评估机构和EOI"},
]
SUITABILITY_FIT = ["持有博士学位（相关学科），有科研发表记录（期刊/会议论文）", "有教学经验（本科/研究生课程辅导），英语学术写作能力极强", "AI/数据科学/网络安全/医疗健康等高需求学科背景（竞争优势最大）", "已获得澳洲大学博士后职位（是进入全职讲席的主流通道）", "接受合同制/临时岗位作为全职讲席的过渡期"]
SUITABILITY_UNFIT = ["仅持有硕士学位，无博士学位（绝大多数讲师职位的硬性要求）", "期望快速（5年内）获得全职稳定讲席（竞争极激烈，通常需要10年+积累）", "学术英语写作能力不足以发表国际期刊论文"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "大学讲师薪资 $125k~$130k（2026）", "url": "https://au.seek.com/career-advice/role/lecturer/salary"},
    {"source_name": "Indeed AU", "content": "大学讲师平均薪资 $124,444（2026）", "url": "https://au.indeed.com/career/lecturer/salaries"},
    {"source_name": "Glassdoor AU", "content": "讲师平均薪资 $112,596（2026）", "url": "https://www.glassdoor.com.au/Salaries/lecturer-salary-SRCH_KO0,8.htm"},
    {"source_name": "AcademicJobs.com", "content": "澳洲大学教授薪资指南2026", "url": "https://www.academicjobs.com/higher-education-news/professor-salary-australia-2026-or-university-pay-guide-12537"},
    {"source_name": "Department of Home Affairs", "content": "签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲大学讲师工资多少？", "answer": "讲师（Lecturer A/B）约 $105,000~$135,000（SEEK $125k~$130k；Indeed $124,444；Glassdoor $112,596）；高级讲师约 $130k~$175k；副教授约 $170k~$195k；教授约 $185k~$280k。薪资透明（HEW薪资表）且稳定增长。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲大学讲师容易找工作吗？", "answer": "全职讲席竞争激烈（难），但博士后和合同制教学岗相对容易。AI/数据科学/网络安全学科的讲师供不应求。Seek 挂牌约 800~2,500 个学术岗（含全职/合同制/博士后）。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国大学教师经验澳洲认可吗？", "answer": "中国985/211高校博士学位通常被澳洲大学认可。中国大学发表记录（SSCI/SCI/EI期刊）在澳洲学术市场有一定认可度。主要挑战是英语学术写作能力和在澳洲本地建立学术网络。通过大学担保482签证是最直接路径。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "大学讲师会被AI替代吗？", "answer": "部分影响。在线教学内容和标准化课程评估受AI工具影响；但原创科研、研究指导（博士/硕士生）、学术判断和科研合作关系不可替代。AI实际上增加了对AI学科讲师（研究AI的人）的需求。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲大学讲师有年龄限制吗？", "answer": "无。学术界特别尊重经验积累，资深教授（55~70岁）通常是薪资最高和最受尊重的学术人员。中年博士毕业生（40+岁）在澳洲学术市场也有很好的机会，特别是有行业经验背景者。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲大学讲师需要什么学历？", "answer": "博士学位（PhD）是绝大多数讲师职位的硬性要求。部分实践类学科（商科/设计）可能接受硕士+丰富行业经验；但学术型大学（G8集团）几乎100%要求博士。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲大学讲师认证（移民）难吗？", "answer": "移民路径本身不难（大学担保482清晰），但获得讲师职位本身极具竞争性。建议通过在澳洲大学完成博士+博士后的路径，自然过渡到全职讲席申请。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "大学讲师和中小学教师哪个更适合移民澳洲？", "answer": "中小学教师移民路径更确定（MLTSSL+AITSL评估），就业保障更强（短缺职业）；大学讲师薪资更高（$105k~$280k vs 教师 $95k~$140k），但竞争极激烈，需要博士学位和发表记录。有博士学位和学术背景者选大学讲师，有教学经验（特别是STEM）者选中小学教师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 大学讲师数据入库完成")

if __name__ == "__main__":
    run()
