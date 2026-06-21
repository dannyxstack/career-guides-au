"""澳洲叉车操作员（721311）数据入库。数据来源：JSA、SEEK、Indeed、ERI、SafeWork（2025-2026）。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper import seed_occupation

OCCUPATION = {
    "anzsco_code": "721311", "anzsco_title": "Forklift Driver", "category": "技工",
    "workforce_size": 120000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Warehouse & Logistics","Manufacturing & Distribution","Construction Materials Handling","Cold Storage & Food Processing","E-commerce Fulfilment Centres"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "叉车操作员",
    "summary": "叉车操作员在仓库、配送中心、工厂和建筑工地操作叉车移运货物。澳大利亚电商物流爆发带动叉车操作员需求持续增长，是入门门槛最低的技工类职业之一。",
    "forecast_note": "电商物流、冷链配送和自动化仓储的扩张持续推高叉车操作员需求。叉车自动化（AGV）在高度标准化仓库中逐步渗透，但中小型仓库仍大量需要人工操作。",
    "trend_summary": "电商物流爆发是最大需求驱动力。部分大型仓库已引入自动导引叉车（AGV），叉车操作员需向维护和监控方向转型以应对自动化冲击。",
}
I18N_EN = {
    "locale": "en", "name": "Forklift Driver",
    "summary": "Forklift drivers operate forklifts to move goods in warehouses, distribution centres, factories and construction sites. E-commerce logistics expansion is the primary demand driver.",
    "forecast_note": "E-commerce, cold chain logistics, and warehouse automation expansion sustain strong demand. AGV adoption in standardised warehouses is a medium-term risk.",
    "trend_summary": "E-commerce fulfilment boom is the key demand driver. Operators who can also maintain or supervise automated equipment will have better long-term prospects.",
}
EDUCATION = [
    {"stage": "叉车执照培训（High Risk Work Licence – LF）", "duration": "1~3天", "cost_min": 300, "cost_max": 600, "cost_note": "全国统一 HRWL LF 证书，是入门门槛最低的机械操作资质", "sort_order": 0},
]
QUALIFICATIONS = [
    {"qual_name": "High Risk Work Licence – Forklift (LF)", "issuer": "各州 SafeWork / WorkSafe", "note": "全国统一，操作叉车的法定强制执照", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Elevated Work Platform Licence (WP)", "issuer": "各州 SafeWork / WorkSafe", "note": "高空作业平台操作资质（可选，扩展就业范围）", "is_mandatory": 0, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 3000, "count_max": 5000, "note": "全国，含仓库、物流、制造和建筑物料岗"},
    {"platform": "Indeed",   "count_min": 2000, "count_max": 3500, "note": "含兼职、夜班和合同工"},
    {"platform": "LinkedIn", "count_min": 300,  "count_max": 700,  "note": "偏仓储管理和物流主管岗"},
]
SALARIES = [
    {"experience": "初级操作员（持证后 0~2年）", "salary_min": 55000, "salary_max": 68000, "salary_note": "全国最低工资附近，不同班次差异较大", "sort_order": 0},
    {"experience": "中级操作员（2~5年）", "salary_min": 68000, "salary_max": 80000, "salary_note": "SEEK 区间 $65k~$75k（Jun 2026）；Indeed $35.26/hr", "sort_order": 1},
    {"experience": "资深操作员 / 班长（5年+）", "salary_min": 80000, "salary_max": 95000, "salary_note": "含班长责任津贴；夜班溢价约15~20%", "sort_order": 2},
    {"experience": "矿业 / 港口叉车操作员（WA/QLD）", "salary_min": 90000, "salary_max": 120000, "salary_note": "矿业和港口岗位轮班津贴+FIFO补贴显著提升薪资", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，叉车操作员需CSOL在列方可申请482", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居（需较长工作经验）", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "部分州提名叉车操作员（需查询最新州提名清单）", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名，适合偏远物流仓储岗位", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "极低", "stars": 1, "note": "1~3天即可取证，是所有技工类中上手最快的职业"},
    {"dimension": "learning_duration",        "label_zh": "极短", "stars": 1, "note": "取证仅需1~3天，无需学徒制"},
    {"dimension": "certification_difficulty", "label_zh": "极低", "stars": 1, "note": "HRWL LF 考试简单，通过率极高"},
    {"dimension": "job_demand",               "label_zh": "很高", "stars": 4, "note": "电商物流爆发，挂牌量是技工类最多之一"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "入门门槛低导致竞争者多，但工作量大可快速入职"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "久坐驾驶室，夜班和连续班次比较常见"},
    {"dimension": "income_level",             "label_zh": "较低", "stars": 2, "note": "中位数约 $68k~$80k，是技工类薪资最低之一"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "电商短期需求旺盛，但AGV自动化是中长期风险"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AGV已在大型标准化仓库广泛应用，叉车操作员面临中期替代风险"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "叉车操作员PR路径比技工类略窄，需查询最新清单"},
    {"dimension": "pr_difficulty",            "label_zh": "较高", "stars": 4, "note": "叉车可能未列MLTSSL，PR路径相对有限"},
]
SUITABILITY_FIT = ["希望快速入职（1~3天取证），不在意薪资较低", "接受仓库、物流和夜班工作环境", "作为来澳后快速就业的过渡职业，积累工作经验", "有重型叉车或矿业设备操作经验，目标矿业高薪岗位"]
SUITABILITY_UNFIT = ["目标是高薪技工职业，建议转学电工、柴油机技工或起重机", "担心自动化替代（AGV已开始渗透大型仓库）", "完全无法接受夜班或轮班工作"]
SOURCES = [
    {"source_name": "SEEK AU", "content": "叉车操作员薪资区间 $65k~$75k（Jun 2026）", "url": "https://au.seek.com/career-advice/role/forklift-driver/salary"},
    {"source_name": "Indeed AU", "content": "叉车操作员平均时薪 $35.26（2026）", "url": "https://au.indeed.com/career/forklift-operator/salaries"},
    {"source_name": "ERI SalaryExpert", "content": "叉车操作员平均年薪数据（2026）", "url": "https://www.salaryexpert.com/salary/job/forklift-operator/australia"},
    {"source_name": "SafeWork Australia", "content": "High Risk Work Licence LF 要求", "url": "https://www.safeworkaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲叉车操作员工资多少？", "answer": "中级叉车操作员年薪约 $68,000~$80,000，SEEK 区间 $65k~$75k（2026）。矿业和港口岗可达 $90k~$120k，夜班溢价约 15~20%。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲叉车操作员容易找工作吗？", "answer": "非常容易。Seek 常年挂牌 3,000~5,000 个职位，电商物流爆发使需求旺盛，1~3天取证后即可应聘。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国叉车证澳洲认可吗？", "answer": "不直接认可，但考取澳洲 HRWL LF 证书仅需 1~3天，考试简单，有操作经验者几乎都能通过。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "叉车操作员会被机器人替代吗？", "answer": "中等风险。自动导引叉车（AGV）已在亚马逊、科尔斯等大型仓库广泛应用，标准化环境中替代趋势明显。建议学习AGV维护或转向矿业/港口岗位以规避风险。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲叉车操作员有年龄限制吗？", "answer": "无法律上限，18岁以上即可考取执照。是所有技工类中对年龄和学历要求最低的职业。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "澳洲叉车操作员需要大学学历吗？", "answer": "完全不需要。持有 HRWL LF 证书即可执业，是技工类准入门槛最低的职业之一。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "澳洲叉车操作员难学吗？", "answer": "极易上手。1~3天培训考证，有驾驶经验者几乎可以直接通过。是所有持证技工职业中学习周期最短的。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "叉车操作员和卡车司机哪个更适合移民澳洲？", "answer": "卡车司机薪资更高（$78k~$120k+ vs 叉车 $68k~$80k），PR路径更清晰；叉车入门更快，适合刚来澳快速就业。"},
]

def run():
    with get_cursor() as cur:
        seed_occupation(cur, OCCUPATION, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS, JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS, SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    print("\n[OK] 叉车操作员数据入库完成")

if __name__ == "__main__":
    run()
