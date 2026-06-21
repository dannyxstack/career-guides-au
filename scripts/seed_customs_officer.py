"""澳洲海关官员/边境力量官（441312）数据入库。数据来源：JSA、SEEK、ABF（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "441312", "anzsco_title": "Customs Officer",
    "category": "其他", "workforce_size": 8000, "shortage_listed": 0,
    "growth_areas": json.dumps(["澳大利亚边境力量（ABF）专业官员","海关查验与风险评估专家","生物安全检查（DAFF生物安全）","国际邮件和电商货物查验","华语口岸联络官（中文贸易背景）"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "海关官员/边境力量官",
    "summary": "海关官员（澳大利亚边境力量ABF成员）负责在口岸（机场/港口/邮件中心）查验货物和旅客，执行澳洲海关、生物安全和移民法规，保护澳洲边境安全。ABF是联邦政府机构，提供公务员薪资、完善福利和清晰的职业晋升路径，是华裔申请者的有竞争力方向（贸易和双语能力是显著加分项）。",
    "forecast_note": "JSA预测边境力量官员就业至2030年稳定增长约4%。澳洲电商进口激增（跨境包裹数量快速增长）和生物安全威胁推动ABF持续扩大检查人员编制。华裔官员在中澳贸易查验和华语社区服务中具有独特价值。",
    "trend_summary": "澳洲每年处理超过2亿个入境包裹（电商进口激增），ABF扩大邮件中心和口岸查验编制。生物安全（防止害虫和疾病进入）是ABF最高优先级任务之一。DAFF（农业渔业林业部）生物安全官员与ABF密切协作。具备普通话/粤语的官员在华裔入境旅客服务和中澳贸易查验中具有独特价值。",
}
I18N_EN = {
    "locale": "en", "name": "Customs Officer / Border Force Officer",
    "summary": "Customs officers (Australian Border Force members) inspect goods and passengers at ports of entry (airports/seaports/mail centres), enforcing Australian customs, biosecurity and immigration regulations to protect Australia's border. ABF is a federal agency offering public service salaries, comprehensive benefits and clear career progression — a competitive direction for Chinese-Australian applicants where trade knowledge and bilingual skills are significant advantages.",
    "forecast_note": "JSA projects ~4% stable border force officer employment growth by 2030. Australia's surging e-commerce imports (rapidly growing cross-border parcel volumes) and biosecurity threats drive ABF's continued expansion of inspection headcount. Chinese-Australian officers have unique value in Australia-China trade inspection and Chinese-community services.",
    "trend_summary": "Australia processes over 200 million inbound parcels annually (e-commerce import surge), with ABF expanding mail centre and port inspection staffing. Biosecurity (preventing pests and disease entry) is one of ABF's highest-priority missions. DAFF (Department of Agriculture, Fisheries and Forestry) biosecurity officers work closely with ABF. Officers with Mandarin/Cantonese skills have unique value in Chinese inbound traveller services and Australia-China trade inspection.",
}
EDUCATION = [
    {"stage": "高中或以上学历（必须）", "duration": "—", "cost_min": 0, "cost_max": 0, "cost_note": "ABF要求Year 12以上；大学学历有助于快速晋升至高级岗位", "sort_order": 0},
    {"stage": "ABF边境力量官员新兵培训计划（Recruit Training Program）", "duration": "12个月（含实习）", "cost_min": 0, "cost_max": 0, "cost_note": "录取后由ABF提供全免费培训，同期领取APS3学员薪资 $66,839", "sort_order": 1},
    {"stage": "大学学历（关税/法律/国际贸易/移民法）", "duration": "3年", "cost_min": 20000, "cost_max": 50000, "cost_note": "非硬性要求但有助于晋升高级关税官或管理岗", "sort_order": 2},
    {"stage": "普通话/粤语能力（语言优势）", "duration": "—", "cost_min": 0, "cost_max": 0, "cost_note": "华语能力是ABF中澳贸易和华裔旅客服务岗位的显著竞争优势", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "ABF边境力量官员资质（Border Force Officer Accreditation）", "issuer": "澳大利亚边境力量（ABF）", "note": "通过培训计划后获得，是正式上岗的法定要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "航空安全证件（ASIC）", "issuer": "Department of Home Affairs", "note": "在机场工作的所有ABF人员的硬性安全要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "无犯罪记录及完整背景安全审查（Security Clearance）", "issuer": "AGSVA（澳洲政府安全审查局）", "note": "联邦政府岗位的必要条件", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "澳洲公民身份（公民要求）", "issuer": "—", "note": "ABF联邦政府岗位的硬性要求（PR通常不够）", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "ABF官方招募", "count_min": 50, "count_max": 300, "note": "ABF通过 abf.gov.au 发布定期批次招募"},
    {"platform": "APS Jobs", "count_min": 50, "count_max": 200, "note": "澳洲公务员招募平台（jobs.gov.au）"},
    {"platform": "Seek",     "count_min": 100, "count_max": 400, "note": "含DAFF生物安全/关税顾问/口岸检查岗"},
]
SALARIES = [
    {"experience": "ABF学员（培训期12个月）", "salary_min": 64000, "salary_max": 70000, "salary_note": "APS3学员薪资 $66,839（含15.4%超级年金，2026）", "sort_order": 0},
    {"experience": "初级边境力量官员（APS3~4，1~5年）", "salary_min": 68000, "salary_max": 85000, "salary_note": "APS3 $57,497~$60,946；APS4约 $68k~$75k；SEEK均值 $70k~$80k（2026）", "sort_order": 1},
    {"experience": "高级官员/主管（APS5~6，5~12年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "APS6 $99,734~$111,701；Glassdoor ABF均值约 $95k（2026）", "sort_order": 2},
    {"experience": "管理级（EL1/EL2，10年+）", "salary_min": 115000, "salary_max": 175000, "salary_note": "EL1/EL2管理级联邦公务员薪资区间", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "公民要求", "visa_name": "联邦政府岗位要求", "description": "ABF联邦岗位要求澳洲公民（入籍）；PR通常不满足安全审查要求", "sort_order": 0},
    {"visa_subclass": "189/190", "visa_name": "技术移民后入籍申请", "description": "建议先通过其他途径获得PR，在澳居住满4年后入籍再申请ABF", "sort_order": 1},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "关税法/移民法/生物安全规定复杂；需要决策判断力和法律知识"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "ABF培训12个月；晋升高级官员需5~8年工作经验"},
    {"dimension": "certification_difficulty", "label_zh": "较高", "stars": 4, "note": "需要公民资格+安全审查+背景调查；申请门槛严格"},
    {"dimension": "job_demand",               "label_zh": "中等", "stars": 3, "note": "政府编制有限但稳定增长；电商包裹激增推动检查人员需求"},
    {"dimension": "competition",              "label_zh": "较高", "stars": 4, "note": "受欢迎的公务员岗位；竞争激烈但华语双语申请者具有优势"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 3, "note": "轮班工作（机场24/7运营）；需要高度注意力和规范化执法"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "APS3~6薪资 $70k~$115k；管理级 $115k+；稳定且含丰厚退休金"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "稳定公务员；电商和生物安全需求推动编制扩大；晋升通道清晰"},
    {"dimension": "ai_risk",                  "label_zh": "低", "stars": 2, "note": "AI辅助包裹扫描分析；但最终查扣决定和执法权力需要人类官员"},
    {"dimension": "pr_friendliness",          "label_zh": "低", "stars": 1, "note": "ABF需要澳洲公民；只能在入籍后申请，不适合作为移民路径"},
    {"dimension": "pr_difficulty",            "label_zh": "极高", "stars": 5, "note": "不是移民路径，而是入籍后的职业选择；需先完成移民再入籍"},
]
SUITABILITY_FIT = ["已入籍或即将入籍的澳洲公民，背景清白，通过严格政府安全审查", "普通话/粤语流利，有中澳国际贸易或海关物流行业背景", "有大学学历（法律/贸易/公共政策）或相关工作经验，英语沟通流利", "愿意在机场、港口或邮件中心轮班工作，有志于联邦公务员职业发展", "有在大城市（悉尼/墨尔本/布里斯班机场）长期定居计划"]
SUITABILITY_UNFIT = ["非澳洲公民（ABF联邦岗位硬性要求；PR通常不够）", "有犯罪记录或重大信用问题（联邦安全审查硬性排除条件）", "期望通过海关官员职业移民澳洲（需先移民/入籍再申请ABF）"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "边境力量官薪资 $70k~$80k（2026）", "url": "https://au.seek.com/career-advice/role/border-force-officer/salary"},
    {"source_name": "Australian Border Force", "content": "ABF学员薪资 $66,839（APS3，2026）；APS6 $99,734~$111,701", "url": "https://www.abf.gov.au/about-us/careers"},
    {"source_name": "Glassdoor AU", "content": "ABF薪资均值约 $57,000~$75,000（2026）", "url": "https://www.glassdoor.com.au/Salary/Australian-Border-Force-Salaries-E703202.htm"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲海关官员/边境力量官工资多少？", "answer": "ABF学员期 $66,839（APS3）；初级官员（APS3~4）约 $68k~$85k；高级官员（APS5~6）约 $85k~$115k（APS6 $99,734~$111,701）；管理级（EL1/EL2）约 $115k~$175k。另含15.4%超级年金。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲海关官员容易找工作吗？", "answer": "政府编制有限但持续增长（电商包裹激增推动）。ABF批次招募竞争较激烈，但双语（普通话/粤语）申请者在华裔旅客和中澳贸易查验岗位具有显著优势。需要澳洲公民资格是主要门槛。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国海关经验澳洲认可吗？", "answer": "中国海关工作经验（特别是商品查验和贸易合规）对ABF申请非常有价值，可以提升竞争力。但需要澳洲公民资格（非公民无法申请ABF），且需通过ABF的12个月培训计划。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "海关官员会被AI替代吗？", "answer": "部分会。AI辅助X光扫描分析和包裹风险评分正在替代部分重复性筛查工作；但最终查扣决定、旅客查询和执法权力只能由ABF官员行使。向高级分析岗（风险情报）发展可规避AI影响。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲海关官员有年龄限制吗？", "answer": "无明确年龄上限，但ABF新兵培训有体能要求。有中澳贸易经验的中高年龄申请者（35~50岁）在专业化高级岗位竞争力强。公务员体系无强制退休年龄（按公务员法规定）。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲海关官员需要什么学历？", "answer": "Year 12是基本要求；大学学历（关税法/国际贸易/法律）有助于快速晋升。最重要的是澳洲公民资格、安全审查通过和通过ABF选拔（笔试/面试/体能）。双语能力（普通话/粤语）是显著加分项。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲海关官员入职难吗？", "answer": "难度较高，主要因为需要澳洲公民资格。建议先通过技术移民获得PR，在澳居住满4年后申请入籍，入籍后再申请ABF新兵培训计划。海关官员不是移民路径，而是入籍后的职业选择。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "海关官员和警察哪个澳洲发展更好？", "answer": "薪资相近（均含津贴在 $85k~$130k范围）；海关官员职业更专业化（贸易/边境安全方向），工作强度相对较低（无高危执法任务）；警察晋升通道更宽广，社区存在感更强。有国际贸易/物流背景者选海关；有执法/犯罪调查志趣者选警察。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 海关官员/边境力量官数据入库完成")

if __name__ == "__main__":
    run()
