"""零售销售员 (621111) Sales Assistant (General) — AU 2025-2026
非技术移民职业（is_migration=0），ANZSCO 分类码 621111 用于职业分类，不在技术移民清单。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from db.connection import get_cursor
from _seed_helper import seed_occupation_v2
from pipeline.generators.md_generator import generate_md

OCC = {
    "occ_code": "621111", "anzsco_code": "621111", "anzsco_title": "Sales Assistant (General)",
    "category": "Hospitality, Retail & Tourism", "workforce_size": 680000,
    "shortage_listed": 0, "is_migration": 0,
    "growth_areas": json.dumps(["Omnichannel & Click-and-Collect Retail", "Customer Experience Specialist",
                                "Visual Merchandising", "Retail Tech / POS & Self-checkout"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "零售销售员",
    "summary": "零售销售员在商店、超市和专卖店为顾客提供商品介绍、销售和结账服务，是澳洲就业人数最多的职业之一。门槛低、入职快，多为时薪制，适合学生、新移民和兼职人群作为过渡或长期工作。",
    "forecast_note": "澳洲零售业整体就业稳定但增长平缓，电商和自助结账对基础岗位有一定挤压；同时全渠道零售、客户体验和视觉营销方向出现更高附加值的岗位。",
    "trend_summary": "时薪受 Retail Award 与最低工资保护，周末和公共假期有加班费（penalty rates）。晋升路径为资深销售→主管→店长。具备客户服务、库存和 POS 系统经验者更易转向零售管理。"}
I18N_EN = {"locale": "en", "name": "Sales Assistant (General)",
    "summary": "Sales assistants serve customers in shops, supermarkets and specialty stores, advising on products, processing sales and handling point-of-sale. It is one of Australia's largest occupations by headcount, with low barriers to entry and mostly hourly, award-covered pay.",
    "forecast_note": "Australian retail employment is stable but slow-growing; e-commerce and self-checkout pressure entry-level roles, while omnichannel retail, customer experience and visual merchandising create higher-value positions.",
    "trend_summary": "Hourly pay is protected by the Retail Award and minimum wage, with weekend and public-holiday penalty rates. Progression runs from senior sales to supervisor to store manager."}
EDUCATION = [
    {"stage": "无强制学历（在职培训）", "duration": "即时~数周", "cost_min": 0, "cost_max": 0, "cost_note": "雇主提供在岗培训", "sort_order": 0},
    {"stage": "Certificate II/III in Retail Services（可选）", "duration": "3~12个月", "cost_min": 0, "cost_max": 3000, "cost_note": "TAFE，部分州补贴", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Retail (SIR30216)", "issuer": "TAFE / RTO", "note": "非强制，利于晋升", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "RSA（售酒场所需要）", "issuer": "各州主管部门", "note": "在售酒零售点为强制", "is_mandatory": 0, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 8000, "count_max": 14000, "note": "全国，含兼职/casual"},
    {"platform": "Indeed", "count_min": 6000, "count_max": 11000, "note": "全国"},
]
SALARIES = [
    {"experience": "入门（casual/兼职）", "salary_min": 45000, "salary_max": 55000, "salary_note": "时薪约$25~$30含casual补贴", "sort_order": 0},
    {"experience": "全职（1~3年）", "salary_min": 55000, "salary_max": 62000, "salary_note": "Retail Award 全职", "sort_order": 1},
    {"experience": "资深 / 专卖店", "salary_min": 62000, "salary_max": 72000, "salary_note": "资深或高价值品类销售", "sort_order": 2},
]
VISA_PATHWAYS = []
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "很低", "stars": 1, "note": "在岗即可上手"},
    {"dimension": "learning_duration",        "label_zh": "很短", "stars": 1, "note": "数天到数周"},
    {"dimension": "certification_difficulty", "label_zh": "很低", "stars": 1, "note": "无强制证书"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "全国岗位量最大职业之一"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "应聘者多但岗位也多"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "久站、周末班"},
    {"dimension": "income_level",             "label_zh": "较低", "stars": 2, "note": "AUD 4.5万~7.2万"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "可晋升零售管理"},
    {"dimension": "ai_risk",                  "label_zh": "中高", "stars": 4, "note": "自助结账/电商挤压基础岗"},
    {"dimension": "pr_friendliness",          "label_zh": "很低", "stars": 1, "note": "非技术移民职业"},
    {"dimension": "pr_difficulty",            "label_zh": "极高", "stars": 5, "note": "不在技术移民清单"},
]
SUITABILITY_FIT = ["喜欢与人打交道、服务意识强的人", "学生、兼职及希望灵活排班者", "想进入零售管理路径的入门者"]
SUITABILITY_UNFIT = ["以技术移民为主要目标者", "不愿久站或不适应周末轮班者", "追求高起薪的求职者"]
SOURCES = [
    {"source_name": "JSA / JobOutlook", "content": "ANZSCO 6211 销售员就业与人数", "url": "https://joboutlook.gov.au/occupations/occupation?occupationCode=6211"},
    {"source_name": "Seek AU", "content": "薪资与岗位量", "url": "https://www.seek.com.au/career-advice/role/sales-assistant/salary"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲零售销售员工资多少？", "answer": "casual时薪约AUD $25~$30（含补贴），全职年薪约$5.5万~$6.2万，资深或专卖店可达$7万+。周末和公共假期有penalty rates。"},
    {"faq_type": "migration", "sort_order": 1, "question": "零售销售员能技术移民吗？", "answer": "不能。零售销售员不在澳洲技术移民职业清单上，属于非技术移民职业；如以移民为目标，建议考虑清单上的相关职业。"},
    {"faq_type": "demand", "sort_order": 2, "question": "澳洲零售销售员好找工作吗？", "answer": "非常好找，是全国岗位量最大的职业之一，Seek常年有上万个职位，casual和兼职机会尤其多。"},
]
def run():
    with get_cursor() as cur:
        seed_occupation_v2(cur, OCC, I18N_ZH, I18N_EN, EDUCATION, QUALIFICATIONS,
                           JOB_LISTINGS, SALARIES, VISA_PATHWAYS, RATINGS,
                           SUITABILITY_FIT, SUITABILITY_UNFIT, SOURCES, FAQS)
    path = generate_md(OCC["anzsco_code"])
    print(f"[markdown] {path}")
    print("[OK] 零售销售员入库完成")
if __name__ == "__main__":
    run()
