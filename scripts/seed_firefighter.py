"""澳洲消防员（441211）数据入库。数据来源：JSA、SEEK、Indeed（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "441211", "anzsco_title": "Firefighter",
    "category": "其他", "workforce_size": 15000, "shortage_listed": 0,
    "growth_areas": json.dumps(["城市消防（都市扩张）","林区消防（灌木火灾季节性需求）","机场消防（航空业复苏）","危险品处置专家（HAZMAT）","消防检查员和防火安全顾问"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "消防员",
    "summary": "消防员负责灭火、紧急救援、医疗急救响应和防火安全教育，是社区安全的核心力量。澳洲各州消防和紧急服务局（Fire and Rescue NSW、MFB/FRV、QFES等）定期招募全职消防员，竞争激烈但工作稳定、福利完善、晋升路径清晰。气候变化导致的灌木火灾频发增加了消防行业的社会重要性和人员需求。",
    "forecast_note": "JSA预测消防员就业至2030年稳定增长约5%。都市扩张和高密度城市开发推动城市消防需求；气候变化导致的极端天气事件（灌木火/洪水）推动紧急服务需求。消防检查员和防火安全顾问是增速最快的细分方向。",
    "trend_summary": "澳洲消防服务面临城市化和气候变化双重挑战：城市高层建筑火灾风险增加；灌木火季节延长。各州消防局持续增加编制，并向消防员提供全面培训（包括医疗急救、水上救援和HAZMAT）。消防员职业非常稳定，工会保障完善，是公务员性质的高福利岗位。",
}
I18N_EN = {
    "locale": "en", "name": "Firefighter",
    "summary": "Firefighters handle fire suppression, emergency rescue, medical emergency response and fire safety education — a core community safety role. NSW Fire and Rescue, MFB/FRV, QFES and other state services regularly recruit full-time firefighters. Competition is intense but employment is stable with good benefits and clear promotion pathways. Climate change-driven bushfires increase both the social importance and workforce needs of the fire services.",
    "forecast_note": "JSA projects ~5% stable firefighter employment growth by 2030. Urban expansion and high-density development drive city fire demand; climate change-driven extreme weather events (bushfires/floods) drive emergency services needs. Fire safety inspectors and consultants are the fastest-growing sub-sector.",
    "trend_summary": "Australian fire services face dual challenges of urbanisation and climate change: increased high-rise fire risk and extended bushfire seasons. State fire services continue to expand headcount and provide comprehensive training (medical first response, water rescue, HAZMAT). Firefighting is a very stable career with strong union protection and comprehensive public service benefits.",
}
EDUCATION = [
    {"stage": "高中或以上学历（必须）", "duration": "—", "cost_min": 0, "cost_max": 0, "cost_note": "各州消防局要求Year 12以上；数理化基础有助于通过招募考试", "sort_order": 0},
    {"stage": "Certificate III in Public Safety (Firefighting)", "duration": "由消防局招募后提供", "cost_min": 0, "cost_max": 0, "cost_note": "各州消防局的标准培训，录取后免费参加约6个月的学员培训", "sort_order": 1},
    {"stage": "急救证书（Certificate III/IV in First Aid）", "duration": "2~5天", "cost_min": 200, "cost_max": 500, "cost_note": "申请前取得可提升竞争力（现代消防员是多功能紧急救援人员）", "sort_order": 2},
    {"stage": "体能训练和准备（PAT测试）", "duration": "持续训练", "cost_min": 0, "cost_max": 500, "cost_note": "Physical Aptitude Test是消防员招募的核心门槛，需长期体能训练", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Public Safety (Firefighting and Emergency Operations)", "issuer": "各州消防局/TAFE", "note": "消防员岗位任职的法定职业资质（录用后提供）", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Driver's Licence（Heavy Vehicle/MR+）", "issuer": "各州道路交通局", "note": "消防车驾驶资质（录用后由消防局安排培训）", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "急救证书（First Aid）", "issuer": "St John Ambulance等认可机构", "note": "申请消防员岗位的加分资质", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "无犯罪记录证明（National Police Check）", "issuer": "澳联邦警察或州警察局", "note": "所有公共安全类岗位的硬性要求", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "各州消防局官网", "count_min": 50, "count_max": 300, "note": "NSW FRNSW/VIC FRV/QLD QFES/WA DFES等按轮次招募"},
    {"platform": "Seek",     "count_min": 100, "count_max": 400, "note": "含消防检查员/防火安全顾问/消防设备技术员岗"},
    {"platform": "Indeed",   "count_min": 80, "count_max": 300, "note": "含私人消防安全公司和工业消防岗"},
]
SALARIES = [
    {"experience": "消防员学员（培训期）", "salary_min": 60000, "salary_max": 70000, "salary_note": "各州消防局学员培训期薪资（约6个月）", "sort_order": 0},
    {"experience": "初级/正式消防员（1~5年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "SEEK区间 $70k~$90k；Indeed均值 $89,193（2026）", "sort_order": 1},
    {"experience": "高级消防员/Leading Firefighter（5~12年）", "salary_min": 88000, "salary_max": 115000, "salary_note": "包含轮班津贴和加班后年薪约 $90k~$115k", "sort_order": 2},
    {"experience": "消防队长/主管级（10年+）", "salary_min": 110000, "salary_max": 160000, "salary_note": "Station Officer及以上管理岗，含所有津贴补贴", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "公民/PR限制", "visa_name": "政府服务限制", "description": "各州消防局正式编制通常要求澳洲公民或永居PR身份", "sort_order": 0},
    {"visa_subclass": "482", "visa_name": "TSS（工业消防）", "description": "私人工业消防公司或矿区消防可能担保482", "sort_order": 1},
    {"visa_subclass": "189/190", "visa_name": "技术移民后申请", "description": "建议先获得PR再申请政府消防局岗位", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "技术综合：灭火技术、医疗急救、化学品处置，体能要求高"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "消防局学员培训约6个月；持续在职培训贯穿整个职业生涯"},
    {"dimension": "certification_difficulty", "label_zh": "较高", "stars": 4, "note": "体能测试（PAT）是主要门槛；招募竞争激烈（录取率约5~10%）"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "政府编制有限，招募机会不常见；工业消防和防火安全顾问需求较大"},
    {"dimension": "competition",              "label_zh": "很高", "stars": 5, "note": "政府消防局招募竞争极激烈；每个名额有数十甚至上百人竞争"},
    {"dimension": "work_intensity",           "label_zh": "很高", "stars": 4, "note": "24/48小时轮班；应急任务随时待命；高强度体力工作和心理压力"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "初级 $70k~$90k；含津贴高级消防员 $90k~$115k；整体薪资中等"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "稳定公务员性质工作；气候变化推动需求但编制扩张有限"},
    {"dimension": "ai_risk",                  "label_zh": "很低", "stars": 1, "note": "灭火操作、生命救援和现场判断无法自动化；AI辅助预测火情"},
    {"dimension": "pr_friendliness",          "label_zh": "中低", "stars": 2, "note": "政府消防局编制通常要求公民/PR；建议先获PR再申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "消防员不在MLTSSL；需先通过其他途径获得PR再进入政府消防局"},
]
SUITABILITY_FIT = ["澳洲公民或永久居民（PR），身体健康，体能出色，能通过PAT体能测试", "有急救证书（First Aid/CPR）或医疗/护理背景，有志于公共安全服务事业", "有重型车驾照（MR或以上）或职业驾驶经验，英语沟通流利", "有在特定消防局所在州定居的明确计划（各州消防局独立招募）", "心理素质良好，能承受高压和应急情境下的快速决策"]
SUITABILITY_UNFIT = ["尚未获得澳洲公民或PR身份（政府消防局编制的硬性要求）", "体能水平未达到消防PAT测试标准（需提前至少6~12个月进行专项体能训练）", "期望通过消防员职业直接移民（非MLTSSL，不适合作为移民路径的首选）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "消防员薪资 $70k~$90k（2026）", "url": "https://au.seek.com/career-advice/role/firefighter/salary"},
    {"source_name": "Indeed AU", "content": "消防员均值 $89,193（2026）", "url": "https://au.indeed.com/career/firefighter/salaries"},
    {"source_name": "Fire and Rescue NSW", "content": "FRNSW消防员招募信息（2026）", "url": "https://www.fire.nsw.gov.au/page.php?id=200"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲消防员工资多少？", "answer": "初级消防员约 $70,000~$90,000（SEEK $70k~$90k；Indeed $89,193）；含轮班和加班津贴高级消防员约 $90k~$115k；消防队长级别含所有津贴可达 $110k~$160k。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲消防员容易找工作吗？", "answer": "政府消防局名额竞争极激烈（录取率5~10%）。消防检查员、工业消防和防火安全顾问岗位竞争相对低。SEEK挂牌约100~400个消防相关职位。需要澳洲公民或PR才能申请政府消防局。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国消防员经验澳洲认可吗？", "answer": "可以作为参考但需重新培训。澳洲各州消防局有独立的培训和认证体系，所有新进消防员（包括有经验者）都需要完成约6个月的学员培训。中国消防经验可以提升申请竞争力，但不能豁免培训要求。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "消防员会被AI替代吗？", "answer": "风险极低。灭火操作、生命救援和现场环境判断是需要实体行动的工作，AI无法执行。人工智能辅助预测火情风险和优化调度，但实际消防任务需要有血有肉的消防员。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲消防员有年龄限制吗？", "answer": "大多数州消防局要求18~35岁（部分州放宽至40岁）申请初级消防员岗位。已在职消防员无强制退休年龄限制（按体能和健康状况评估）。消防检查员和防火安全顾问岗位无年龄限制。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲消防员需要什么学历？", "answer": "高中毕业（Year 12）是基本要求；大学学历不是必须的但有助于晋升管理岗。最重要的是体能（通过PAT测试）、急救资质和英语沟通能力。有驾照（MR级以上）有加分。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "消防员移民/入职难吗？", "answer": "政府消防局需要公民或PR资格，不能作为首选移民路径。建议先通过其他途径（如技术移民或配偶签证）获得PR，再申请各州消防局。竞争激烈，需提前1~2年进行体能训练和准备。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "消防员和警察哪个澳洲发展更好？", "answer": "薪资相近（消防 $70k~$90k vs 警察 $55k~$75k初级，含津贴后相当）；警察晋升通道更宽广；消防员工作内容更多元（医疗急救/HAZMAT/救援）。两者都要求公民或PR；警察招募更频繁（全年），消防局招募机会相对少。有医疗急救热情选消防；有执法和侦查兴趣选警察。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 消防员数据入库完成")

if __name__ == "__main__":
    run()
