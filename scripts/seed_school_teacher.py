"""澳洲中小学教师（241411/241213）数据入库。数据来源：JSA、SEEK、各州教育部（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "241411", "anzsco_title": "Secondary School Teacher",
    "category": "教育/社会服务", "workforce_size": 290000, "shortage_listed": 1,
    "growth_areas": json.dumps(["STEM教师（数学/科学/信息技术）","英语作为第二语言教师（ESL/EAL）","特殊教育需求教师（SEN）","职业教育与培训（VET in Schools）","偏远地区/农村学校教师"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "中小学教师",
    "summary": "中小学教师（Primary/Secondary School Teacher）在澳洲公立和私立学校教授学生，是澳洲就业量最大的职业之一。全国性教师短缺（特别是STEM和偏远地区）使教师成为最稳定的移民友好职业，政府积极吸引海外教师填补空缺，是技术移民门槛最清晰的教育类职业。",
    "forecast_note": "JSA预测中小学教师至2035年需求净增约25,000人。STEM教师（数学/物理/信息技术）是最紧缺的细分方向，全澳各州均有明显缺口；偏远地区教师短缺更为严重，491签证加分明显。",
    "trend_summary": "澳洲正经历1970年代以来最严重的教师短缺，各州政府大幅提升教师薪资（NSW 2024年涨幅约4%）并积极开展海外教师招募。数字化教学工具和AI辅助教学成为课堂标配，但教师核心工作不可替代。",
}
I18N_EN = {
    "locale": "en", "name": "School Teacher (Primary/Secondary)",
    "summary": "School teachers teach students in Australian public and private schools — one of Australia's largest occupations. A nationwide teacher shortage (especially STEM and remote areas) makes teaching one of the most migration-friendly stable professions. Government actively recruits overseas teachers to fill gaps, providing one of the clearest skilled migration pathways in education.",
    "forecast_note": "JSA projects net new demand for ~25,000 school teachers by 2035. STEM teachers (maths/physics/ICT) are the most urgently needed specialisation nationwide. Remote area teacher shortages are even more acute, with 491 visa score bonuses.",
    "trend_summary": "Australia is experiencing its worst teacher shortage since the 1970s. State governments have significantly raised teacher salaries (NSW ~4% raise in 2024) and are actively recruiting overseas. Digital teaching tools and AI-assisted learning are becoming classroom standards, but core teaching work remains irreplaceable.",
}
EDUCATION = [
    {"stage": "Bachelor of Education（B.Ed，4年）或相关学位+研究生教育文凭（Grad Dip Ed，1年）", "duration": "4年（B.Ed）或 3年学位+1年GDE", "cost_min": 25000, "cost_max": 180000, "cost_note": "国际生费用约 $28,000~$38,000/年；GDE约 $20,000~$35,000/年", "sort_order": 0},
    {"stage": "NESA/VIT/QCT 等州教师注册（Teacher Registration）", "duration": "1~3个月申请", "cost_min": 100, "cost_max": 500, "cost_note": "各州教师注册机构注册费约 $100~$500；是合法在州内任教的法律要求", "sort_order": 1},
    {"stage": "AITSL 海外教师资格认证（OTES 评估）", "duration": "3~6个月", "cost_min": 500, "cost_max": 2000, "cost_note": "澳洲教师教育学会（AITSL）对海外教师资格的专项评估，约 $500~$800 申请费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "澳洲州教师注册（Teacher Registration）", "issuer": "各州注册机构（NESA/VIT/QCT/TRB等）", "note": "在澳洲合法任教的法律要求，每州注册机构不同", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AITSL海外教师资格认证（OTES）", "issuer": "AITSL（澳洲教师教育学会）", "note": "海外教师资格评估，是189/190签证和雇主担保的必要步骤", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "英语水平要求（IELTS 7.5+ 或 OET）", "issuer": "各州教师注册机构", "note": "非英语国家背景的教师需要提供英语能力证明，通常 IELTS 7.5/8.0 各单项", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "工作背景调查（Working With Children Check）", "issuer": "各州政府", "note": "所有在职任教者法律必须，费用约免费~$110", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 5000, "count_max": 12000, "note": "全国，含小学/中学/特殊教育/ESL教师岗，公立/私立均有"},
    {"platform": "Indeed",   "count_min": 3000, "count_max": 8000, "note": "含各州教育部直聘和私立学校岗"},
    {"platform": "LinkedIn", "count_min": 2000, "count_max": 6000, "note": "私立学校直招比例较高"},
]
SALARIES = [
    {"experience": "毕业教师（0~2年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "各州毕业教师薪酬有差异；NSW约 $84,724，NT最高约 $96,180（2026）", "sort_order": 0},
    {"experience": "有经验教师（3~10年）", "salary_min": 95000, "salary_max": 115000, "salary_note": "SEEK 区间 $100k~$105k；大多数州有固定薪资阶梯", "sort_order": 1},
    {"experience": "资深教师 / 主任教师（10年+）", "salary_min": 115000, "salary_max": 140000, "salary_note": "NT顶端课堂教师 $136,997（2026）；NSW主任教师 $113,497~$120,000", "sort_order": 2},
    {"experience": "校长 / 副校长", "salary_min": 140000, "salary_max": 230000, "salary_note": "大型公立学校校长薪酬含绩效奖金", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，各州教育部和私立学校常直接担保海外教师", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "邀请制，MLTSSL在列，AITSL评估", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，各州均有通道，STEM教师优先", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区学校极度短缺，加15分，多州积极提名", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需要学科知识+教学法+课堂管理能力，实习期挑战较大"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "B.Ed 4年或相关学位3年+GDE 1年；总周期约4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "AITSL海外资格评估难度中等；英语要求（IELTS 7.5+）是主要门槛"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "全国最严重的职业短缺之一，STEM教师和偏远地区教师极度紧缺"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "STEM/ESL/特殊教育教师供不应求，甚至主动为海外教师提供安置支持"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "课堂教学+备课+学生评估+家长沟通，总实际工作时间远超合同课时"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "有经验教师 $95k~$115k；薪资增长稳定但天花板相对较低（除校长路径）"},
    {"dimension": "future_prospect",          "label_zh": "很好", "stars": 4, "note": "人口增长推动持续需求；AI辅助教学不替代教师，但要求数字化技能提升"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "教学是澳洲AI替代风险最低的职业之一，学生关系、情感支持和课堂管理不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "MLTSSL在列，各州政府主动招募海外教师并提供安置支持，是最移民友好的职业之一"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "AITSL评估路径清晰，英语要求可达，偏远地区491路径更容易"},
]
SUITABILITY_FIT = ["持有教育学/学科相关学位+教育资格（如中国师范学院毕业），有任教经验", "英语能力强（IELTS 7.5 各单项，是澳洲教师注册的硬性要求）", "STEM学科背景（数学/物理/信息技术/化学）——全澳最紧缺的方向", "有特殊教育需求（SEN）或ESL教学经验（溢价最高）", "愿意接受偏远地区任教（薪资更高+491签证加分+安置补贴）"]
SUITABILITY_UNFIT = ["英语能力不足 IELTS 7.5 各单项（是硬性门槛，无例外）", "无正规教育学历和教学法培训，无法通过AITSL评估", "仅愿意在悉尼/墨尔本市区任教（竞争最激烈，491加分也无效）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "中学教师薪资 $100k~$105k（2026）", "url": "https://au.seek.com/career-advice/role/secondary-teacher/salary"},
    {"source_name": "NSW Department of Education", "content": "NSW教师薪资阶梯（2026）", "url": "https://education.nsw.gov.au/teach-nsw/explore-teaching/salary-of-a-teacher"},
    {"source_name": "AITSL", "content": "海外教师资格认证（OTES）", "url": "https://www.aitsl.edu.au/"},
    {"source_name": "TeachBuySell", "content": "澳洲各州教师薪资2026对比", "url": "https://teachbuysell.com.au/teacher-guides/teacher-salary-australia-2026"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲中小学教师工资多少？", "answer": "有经验教师约 $95,000~$115,000（SEEK $100k~$105k）；毕业教师约 $75,000~$95,000（NT最高约 $96,180）；资深/主任教师约 $115k~$140k；校长可超 $140k~$230k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲中小学教师容易找工作吗？", "answer": "极容易。澳洲正经历严重教师短缺，STEM教师（数学/物理/信息技术）全国各州极度紧缺。SEEK 挂牌约 5,000~12,000 个职位，各州教育部甚至主动为海外教师提供安置支持和搬家补贴。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国教师资格/经验澳洲认可吗？", "answer": "通过 AITSL（澳洲教师教育学会）海外教师资格评估（OTES），中国师范学历和教学经验可以认可。主要挑战是英语能力（IELTS 7.5 各单项），而非学历认可。通过评估后需要向各州注册机构（如NSW的NESA）申请教师注册。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "教师会被AI替代吗？", "answer": "不会。教学是AI替代风险最低的职业之一。AI辅助备课和差异化教学内容生成，但课堂管理、学生情感支持、差异化教学判断和家长沟通完全不可替代。澳洲课程标准明确要求人类教师。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲教师有年龄限制吗？", "answer": "无。澳洲非常欢迎有经验的中年教师（35~55岁），特别是STEM学科和特殊教育方向。学校更重视教学经验而非年龄，资深教师更受学校欢迎。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲教师需要什么学历？", "answer": "需要AITSL认可的教育资格（等同于澳洲B.Ed 4年或相关学科学位+研究生教育文凭）。中国师范院校本科+教师资格证通常可以通过AITSL评估（具体取决于学科和课程内容）。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲教师认证（移民）难吗？", "answer": "难度较低（与其他专业相比）。主要门槛是英语能力（IELTS 7.5 各单项）。AITSL评估路径清晰，各州教育部对海外教师非常欢迎，491偏远地区路径大幅降低移民门槛。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "教师和护士哪个更适合移民澳洲？", "answer": "两者都是MLTSSL短缺职业，移民路径成熟。教师英语要求更高（IELTS 7.5 vs 护士 7.0），但收入更稳定、工作节奏更规律。STEM教师短缺程度可能超过一般护士。有教学背景者强烈推荐教师路径，特别是数学/科学教师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 中小学教师数据入库完成")

if __name__ == "__main__":
    run()
