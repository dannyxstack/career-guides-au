"""澳洲机器学习工程师（262114）数据入库。数据来源：JSA、SEEK、Indeed、Glassdoor、Talenza（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "262114", "anzsco_title": "Machine Learning Engineer",
    "category": "IT/工程", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["LLM & Generative AI Engineering","MLOps & AI Infrastructure","Computer Vision & NLP","AI for Healthcare & Mining","Responsible AI & Governance"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "机器学习工程师",
    "summary": "机器学习工程师构建、训练、部署和维护ML/AI模型，覆盖NLP、计算机视觉、推荐系统和生成式AI。澳洲联邦AI战略（AU$1.2亿投入）和大型企业AI应用爆发推动对ML工程师的需求急剧上升，是IT类薪资最高且增速最快的职业。",
    "forecast_note": "Talenza 2026 AI薪资报告：ML工程师年薪中位数 $165,000，同比增长约18%。全国从业人数约18,000，供需缺口持续扩大。",
    "trend_summary": "生成式AI（LLM/RAG/Fine-tuning）工程师是2025-2026年薪资溢价最高的专业方向，年薪可超 $200,000。MLOps工程师（模型运维自动化）需求显著增加。",
}
I18N_EN = {
    "locale": "en", "name": "Machine Learning Engineer",
    "summary": "ML engineers build, train, deploy and maintain ML/AI models across NLP, computer vision, recommendation systems and generative AI. Federal AI strategy investment ($1.2B) and enterprise AI adoption are driving acute demand.",
    "forecast_note": "Talenza 2026 AI salary report: ML engineer median salary $165,000, ~18% YoY growth. National workforce ~18,000 with a widening supply gap.",
    "trend_summary": "Generative AI (LLM/RAG/Fine-tuning) engineering commands the highest salary premiums in 2025-2026, with top earners exceeding $200,000. MLOps demand is rising sharply.",
}
EDUCATION = [
    {"stage": "Bachelor/Master of Computer Science（AI/ML专业方向）", "duration": "3~5年（全日制）", "cost_min": 25000, "cost_max": 180000, "cost_note": "ML岗位通常偏好硕士学历（Master提供更深的数学/统计基础）", "sort_order": 0},
    {"stage": "在线专项课程（Coursera/DeepLearning.AI/Fast.ai）", "duration": "3~12个月自学", "cost_min": 500, "cost_max": 3000, "cost_note": "作为转行路径，配合强实战项目（Kaggle/GitHub）在澳洲有一定认可度", "sort_order": 1},
    {"stage": "ACS 技能评估（189/190签证）", "duration": "2~6个月", "cost_min": 500, "cost_max": 1500, "cost_note": "技术移民必须，ML工程师通常以CS/Software Engineering类别评估", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Master/PhD of Computer Science (AI/ML方向)", "issuer": "认可大学", "note": "ML工程师岗位中约60%要求硕士及以上", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "TensorFlow Developer Certificate / AWS ML Specialty", "issuer": "Google/AWS", "note": "行业认证，补充学历的实践能力证明", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Kaggle Master/Grandmaster 排名", "issuer": "Kaggle", "note": "业界认可的技术能力证明，替代部分学历要求", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "ACS 技能评估", "issuer": "Australian Computer Society", "note": "189/190签证技术移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 600,  "count_max": 1500, "note": "全国，含ML工程师、Data Scientist、AI工程师和研究员岗"},
    {"platform": "Indeed",   "count_min": 400,  "count_max": 1000, "note": "含合同工和研究岗"},
    {"platform": "LinkedIn", "count_min": 1000, "count_max": 2500, "note": "科技公司直招和猎头，高端岗比例高"},
]
SALARIES = [
    {"experience": "初级ML工程师（0~3年）", "salary_min": 90000, "salary_max": 120000, "salary_note": "通常需要硕士学历，含实习转正", "sort_order": 0},
    {"experience": "中级ML工程师（3~6年）", "salary_min": 120000, "salary_max": 160000, "salary_note": "Indeed 平均 $131,670；Glassdoor 平均 $137,500（2026）", "sort_order": 1},
    {"experience": "高级ML工程师 / LLM专家（6~10年）", "salary_min": 160000, "salary_max": 210000, "salary_note": "Talenza 报告中位数 $165k；生成式AI专家可达 $200k+", "sort_order": 2},
    {"experience": "ML架构师 / AI负责人（10年+）", "salary_min": 200000, "salary_max": 320000, "salary_note": "Atlassian/Canva/顶尖科技公司AI研究总监级别", "sort_order": 3},
    {"experience": "合同/顾问ML工程师", "salary_min": 150000, "salary_max": 280000, "salary_note": "日薪 $800~$1,500（年化约 $160k~$300k）", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，ML工程师为核心短缺岗位", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "SkillSelect Independent", "description": "无需雇主，邀请制，MLTSSL在列", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，NSW/VIC AI产业通道", "sort_order": 3},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区IT，加15分", "sort_order": 4},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极高", "stars": 5, "note": "需要线性代数、概率统计、深度学习和工程化落地的综合能力"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "通常需要CS硕士或5年以上自学+实战积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "ACS评估不难；ML专项认证实操重于考试"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "生成式AI浪潮推动需求急剧增加，供需缺口最大的IT职业之一"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "高技能ML工程师极度短缺，优秀候选者通常有多个offer"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "实验周期长、模型迭代压力大，但工作灵活度较高"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "是IT类薪资最高的职业之一，中位数 $165k，生成式AI专家 $200k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "生成式AI和自主智能体是澳洲科技产业最大投资方向"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "AI是ML工程师的工作工具和工作领域，不存在被AI替代的问题"},
    {"dimension": "pr_friendliness",          "label_zh": "很高", "stars": 4, "note": "MLTSSL在列，但ML工程师职位数较少，雇主担保482是最快路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "ACS评估和EOI分数是门槛，硕士学历优势明显"},
]
SUITABILITY_FIT = ["有ML/深度学习从业经验（2年以上），有真实项目部署经验", "熟悉 PyTorch/TensorFlow，有LLM/NLP或计算机视觉专攻", "CS硕士或以上学历，或有强竞赛/开源贡献记录", "英语能力达到 IELTS 6.5+", "目标是大型科技公司（Atlassian/Canva）或AI独角兽企业"]
SUITABILITY_UNFIT = ["无真实ML项目部署经验（仅完成在线课程）", "数学基础薄弱（线性代数/概率论），无法理解模型原理", "不适应高度不确定性和实验失败率高的工作环境"]
SOURCES = [
    {"source_name": "Indeed AU", "content": "ML工程师平均薪资 $131,670（2026）", "url": "https://au.indeed.com/career/machine-learning-engineer/salaries"},
    {"source_name": "Glassdoor AU", "content": "ML工程师平均薪资 $137,500（2026）", "url": "https://www.glassdoor.com.au/Salaries/machine-learning-engineer-salary-SRCH_KO0,25.htm"},
    {"source_name": "Talenza 2026 AI Salary Guide", "content": "ML工程师中位数 $165,000，同比增长18%", "url": "https://talenza.com.au/employers/2026-ai-salary-guide/"},
    {"source_name": "ACS", "content": "技能评估机构", "url": "https://www.acs.org.au/"},
    {"source_name": "Department of Home Affairs", "content": "MLTSSL / 签证条件", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲机器学习工程师工资多少？", "answer": "中级ML工程师约 $120,000~$160,000（Indeed均值 $131,670，Glassdoor $137,500）；高级工程师约 $160k~$210k；生成式AI专家可超 $200k。Talenza报告中位数 $165,000（2026）。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲ML工程师容易找工作吗？", "answer": "容易（高技能者）。生成式AI浪潮推动需求急剧增加，优秀ML工程师通常同时收到多个offer，但入门门槛较高（通常需要硕士+实战项目）。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国AI/ML经验澳洲认可吗？", "answer": "国际学术论文（如顶会ICML/NeurIPS）和开源贡献（GitHub/Hugging Face）在澳洲完全认可。ACS技能评估对CS/ML相关学历的认可度高，通过率较好。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "ML工程师会被AI替代吗？", "answer": "不会。AI是ML工程师的工作工具和研究对象，而非替代品。反而是AI浪潮推高了对ML工程师的需求——更多AI应用需要更多工程师来构建和维护。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲ML工程师有年龄限制吗？", "answer": "无。深度学习领域的资深工程师（40岁以上）在架构设计和项目落地方面具有明显优势，市场需求旺盛。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲ML工程师需要什么学历？", "answer": "约60%的岗位要求硕士学历（CS/统计/数学相关）。但有强竞赛记录（Kaggle Master）或顶级开源贡献者也可通过作品集竞争本科学历岗位。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲ML工程师认证（移民）难吗？", "answer": "技术要求高（需要真实项目经验），但移民流程本身不复杂。ACS评估和EOI分数是门槛，持CS硕士+工作经验者通常可获邀。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "ML工程师和数据分析师哪个更适合移民澳洲？", "answer": "ML工程师薪资更高（$131k~$165k vs $95k~$115k），门槛也更高（通常需要硕士）；数据分析师就业量更大（Seek ~3000 vs ML ~1000），入门门槛更低。有编程和ML深度背景者选ML工程师，有商业分析+SQL背景者选数据分析师。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 机器学习工程师数据入库完成")

if __name__ == "__main__":
    run()
