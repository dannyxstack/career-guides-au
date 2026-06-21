"""Mining Machine Operator (811611) 采矿机械操作工 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "811611", "anzsco_title": "Mining Machine Operator",
    "category": "采矿", "workforce_size": 28000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Autonomous Haul Trucks (AHS)","Surface Open Cut Mining","Coal & Iron Ore Operations","Critical Minerals Open Cut"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "采矿机械操作工",
    "summary": "采矿机械操作工（Mining Machine Operator）操作露天或地下采矿设备，包括挖掘机、推土机、矿用卡车和铲运机。澳洲铁矿石（WA Pilbara）和煤矿（QLD/NSW）是全球最大出口来源，对机械操作工需求庞大。无人驾驶矿车（AHS）在兴起，但过渡期仍需大量操作员。",
    "forecast_note": "Pilbara铁矿石和QLD煤矿仍是核心需求。自动驾驶矿车（AHS）快速扩展，同时催生新的AHS监控员岗位。关键矿产新矿山开发持续创造露天矿操作工需求。",
    "trend_summary": "自主矿车技术改变部分驾驶岗，但现场维护、监控和非标设备操作仍需人力。FIFO年薪在澳洲蓝领中名列前茅。"}
I18N_EN = {"locale": "en", "name": "Mining Machine Operator",
    "summary": "Mining machine operators operate open-cut and underground mining equipment including excavators, bulldozers, haul trucks and loaders. Australia's iron ore (WA Pilbara) and coal mining (QLD/NSW) are among the world's largest export operations, requiring a large workforce. Autonomous haulage systems (AHS) are growing but transition period still needs large numbers of operators.",
    "forecast_note": "Pilbara iron ore and QLD coal remain core demand drivers. Autonomous haulage systems (AHS) rapidly expanding, creating AHS controller roles alongside traditional ones. New critical minerals open-cut mines continuing to create operator demand.",
    "trend_summary": "Autonomous truck technology changing some driving roles but on-site maintenance, monitoring and non-standard equipment operation still require human workers. FIFO annual pay among the highest blue-collar earnings in Australia."}
EDUCATION = [
    {"stage": "Certificate II in Surface Extraction Operations", "duration": "3~6个月", "cost_min": 1000, "cost_max": 3000, "cost_note": "入行最快路径", "sort_order": 0},
    {"stage": "Certificate III in Mining Operations", "duration": "12~18个月（在职）", "cost_min": 2000, "cost_max": 4000, "cost_note": "雇主通常提供", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate II/III in Surface Extraction/Mining Ops", "issuer": "RTO", "note": "核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "HR/HC Truck Licence", "issuer": "各州交通厅", "note": "矿用卡车操作必备", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "必备安全证", "is_mandatory": 1, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 600, "count_max": 1500, "note": "全国，WA/QLD/NSW集中"},
    {"platform": "Indeed", "count_min": 300, "count_max": 700, "note": "露天矿操作工"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 300, "note": "大型矿业公司（BHP/Rio/Glencore）"},
]
SALARIES = [
    {"experience": "初级操作工（0~2年）", "salary_min": 80000, "salary_max": 105000, "salary_note": "Mining Industry Award", "sort_order": 0},
    {"experience": "中级（2~6年）FIFO", "salary_min": 105000, "salary_max": 145000, "salary_note": "WA Pilbara均值", "sort_order": 1},
    {"experience": "高级/AHS监控员（6年+）", "salary_min": 140000, "salary_max": 190000, "salary_note": "自动化矿车监控溢价", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "矿业雇主担保", "sort_order": 0},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 1},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "重型设备驾驶，规程为主"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Cert II可3~6个月入行"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Cert II+驾照"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "全澳最大量技工需求之一"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "BHP/Rio/Glencore持续批量招聘"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "12hr班，FIFO，高温高粉尘"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级FIFO $105k~$145k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "AHS监控新岗位+关键矿产扩张"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AHS将减少部分驾驶岗，但监控/维护不受影响"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，偏远491加分"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "门槛低，入行快，积分容易"},
]
SUITABILITY_FIT = [
    "接受FIFO模式，追求矿业最快速高薪路径",
    "有重型机械或卡车驾驶背景",
]
SUITABILITY_UNFIT = [
    "不接受FIFO和偏远矿区12hr班制",
    "期望城市工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 811611 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Mining Machine Operator 薪资及岗位量", "url": "https://www.seek.com.au/mining-machine-operator-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲采矿机械操作工工资多少？", "answer": "中级FIFO采矿机械操作工年薪约 $105,000~$145,000（WA Pilbara均值）。高级/AHS监控员可达 $190,000+。"},
    {"faq_type": "demand", "sort_order": 1, "question": "没有采矿经验可以直接申请吗？", "answer": "可以。Certificate II（3~6个月）即可入行，BHP/Rio/Glencore有专门的新手培训项目，HR/HC卡车驾照是加分。"},
]
MARKDOWN = """# 采矿机械操作工（Mining Machine Operator）职业分析 · 澳大利亚

**职业代码：811611 – Mining Machine Operator。**

采矿机械操作工驾驶露天矿挖掘机和矿用卡车，是澳洲矿业需求量最大的岗位之一。BHP/Rio/Glencore持续批量招聘，FIFO收入极高，入行门槛低。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0~2年） | $80,000~$105,000 |
| 中级 FIFO（2~6年） | $105,000~$145,000 |
| 高级/AHS监控 | $140,000~$190,000+ |

---

*数据来源：JSA、Seek AU（2025-2026）*
"""
def run():
    with get_cursor() as cur:
        cur.execute("INSERT INTO occupations (anzsco_code,occ_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE occ_code=VALUES(occ_code),anzsco_title=VALUES(anzsco_title),category=VALUES(category),workforce_size=VALUES(workforce_size),shortage_listed=VALUES(shortage_listed),growth_areas=VALUES(growth_areas)",
            (OCCUPATION["anzsco_code"],OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],OCCUPATION["category"],OCCUPATION["workforce_size"],OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"]))
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s AND country_code='AU'", (OCCUPATION["anzsco_code"],))
        occ_id = cur.fetchone()["id"]; print(f"[occupations] id={occ_id}")
        for i18n in [I18N_ZH, I18N_EN]:
            cur.execute("INSERT INTO occupations_i18n (occupation_id,locale,name,summary,forecast_note,trend_summary) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name),summary=VALUES(summary),forecast_note=VALUES(forecast_note),trend_summary=VALUES(trend_summary)",
                (occ_id,i18n["locale"],i18n["name"],i18n["summary"],i18n["forecast_note"],i18n["trend_summary"]))
        cur.execute("DELETE FROM occupation_ratings WHERE occupation_id=%s",(occ_id,))
        for r in RATINGS: cur.execute("INSERT INTO occupation_ratings (occupation_id,dimension,label_zh,stars,note) VALUES (%s,%s,%s,%s,%s)",(occ_id,r["dimension"],r["label_zh"],r["stars"],r.get("note")))
        cur.execute("DELETE FROM occupation_education WHERE occupation_id=%s",(occ_id,))
        for e in EDUCATION: cur.execute("INSERT INTO occupation_education (occupation_id,stage,duration,cost_min,cost_max,cost_note,sort_order) VALUES (%s,%s,%s,%s,%s,%s,%s)",(occ_id,e["stage"],e["duration"],e["cost_min"],e["cost_max"],e["cost_note"],e["sort_order"]))
        cur.execute("DELETE FROM occupation_qualifications WHERE occupation_id=%s",(occ_id,))
        for q in QUALIFICATIONS: cur.execute("INSERT INTO occupation_qualifications (occupation_id,qual_name,issuer,note,is_mandatory,sort_order) VALUES (%s,%s,%s,%s,%s,%s)",(occ_id,q["qual_name"],q.get("issuer"),q.get("note"),q["is_mandatory"],q["sort_order"]))
        cur.execute("DELETE FROM occupation_job_listings WHERE occupation_id=%s",(occ_id,))
        for jl in JOB_LISTINGS: cur.execute("INSERT INTO occupation_job_listings (occupation_id,platform,count_min,count_max,note,snapshot_date) VALUES (%s,%s,%s,%s,%s,%s)",(occ_id,jl["platform"],jl["count_min"],jl["count_max"],jl["note"],TODAY))
        cur.execute("DELETE FROM occupation_salaries WHERE occupation_id=%s",(occ_id,))
        for s in SALARIES: cur.execute("INSERT INTO occupation_salaries (occupation_id,experience,salary_min,salary_max,salary_note,sort_order) VALUES (%s,%s,%s,%s,%s,%s)",(occ_id,s["experience"],s["salary_min"],s["salary_max"],s["salary_note"],s["sort_order"]))
        cur.execute("DELETE FROM occupation_visa_pathways WHERE occupation_id=%s",(occ_id,))
        for v in VISA_PATHWAYS: cur.execute("INSERT INTO occupation_visa_pathways (occupation_id,visa_subclass,visa_name,description,sort_order) VALUES (%s,%s,%s,%s,%s)",(occ_id,v["visa_subclass"],v["visa_name"],v["description"],v["sort_order"]))
        cur.execute("DELETE FROM occupation_suitability WHERE occupation_id=%s",(occ_id,))
        for i,item in enumerate(SUITABILITY_FIT): cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'fit',%s,%s)",(occ_id,item,i))
        for i,item in enumerate(SUITABILITY_UNFIT): cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'unfit',%s,%s)",(occ_id,item,i))
        cur.execute("DELETE FROM occupation_sources WHERE occupation_id=%s",(occ_id,))
        for s in SOURCES: cur.execute("INSERT INTO occupation_sources (occupation_id,source_name,content,url) VALUES (%s,%s,%s,%s)",(occ_id,s["source_name"],s.get("content"),s.get("url")))
        cur.execute("DELETE FROM occupation_faqs WHERE occupation_id=%s",(occ_id,))
        for faq in FAQS:
            cur.execute("INSERT INTO occupation_faqs (occupation_id,faq_type,sort_order) VALUES(%s,%s,%s)",(occ_id,faq["faq_type"],faq["sort_order"]))
            faq_id = cur.lastrowid
            cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'zh-CN',%s,%s) ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",(faq_id,faq["question"],faq["answer"]))
        print("[all tables] done")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "career-contents", "au")
    os.makedirs(out_dir, exist_ok=True)
    slug = re.sub(r'-+',' ',re.sub(r'[^a-z0-9 ]','',re.sub(r'[/()\[\]]',' ',I18N_EN["name"].lower()))).strip().replace(' ','-')
    with open(os.path.join(out_dir, f"{slug}.md"), "w", encoding="utf-8") as f: f.write(MARKDOWN.strip()+"\n")
    print(f"[markdown] {slug}.md")
    print("[OK] 采矿机械操作工入库完成")
if __name__ == "__main__": run()
