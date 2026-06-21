"""Underground Miner (811511) 地下矿工 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "811511", "anzsco_title": "Underground Miner",
    "category": "采矿", "workforce_size": 35000, "shortage_listed": 1,
    "growth_areas": json.dumps(["WA Gold & Nickel Mines","QLD Coal Underground","Critical Minerals (Lithium/Copper)","Autonomous Mining Transition"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "地下矿工",
    "summary": "地下矿工（Underground Miner）在地下采矿作业中操作钻机、装载机械和运输设备，执行爆破辅助和支护工作。澳洲WA黄金/镍矿和QLD煤矿持续旺盛，关键矿产（锂/铜）开发带来新增岗位。FIFO收入是全澳最高体力工种之一。",
    "forecast_note": "关键矿产战略（锂/钴/铜/镍）驱动新矿山开发，WA地下矿人力需求至2030年持续扩张。自动化（自动掘进机/遥控装载）同时催生机械操作和维护新需求。",
    "trend_summary": "自动驾驶地下设备快速普及，但仍需大量一线矿工操作和监督。关停期间（annual shutdown）收入极高。"}
I18N_EN = {"locale": "en", "name": "Underground Miner",
    "summary": "Underground miners operate drilling rigs, loaders and transport equipment in underground mining operations, assisting with blasting and ground support. WA gold/nickel and QLD coal mines persistently strong. Critical minerals development creates new roles. FIFO income among highest blue-collar jobs in Australia.",
    "forecast_note": "Critical minerals strategy (lithium/cobalt/copper/nickel) driving new mine development with WA underground workforce demand expanding to 2030. Automation (autonomous development machines/remote loaders) creating new mechanical operation and maintenance roles.",
    "trend_summary": "Autonomous underground equipment rapidly growing but still requires large front-line workforce for operation and supervision. Annual shutdown periods offer very high earnings."}
EDUCATION = [
    {"stage": "Certificate II in Surface Extraction Operations (entry)", "duration": "3~6个月", "cost_min": 1000, "cost_max": 3000, "cost_note": "入行最快路径", "sort_order": 0},
    {"stage": "Certificate III in Underground Metalliferous Mining", "duration": "12~24个月（在职）", "cost_min": 2000, "cost_max": 5000, "cost_note": "雇主通常赞助", "sort_order": 1},
    {"stage": "Shot Firer Licence（爆破执照）", "duration": "2~4周", "cost_min": 1000, "cost_max": 3000, "cost_note": "各州矿监局颁发", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Underground Metalliferous Mining", "issuer": "RTO/TAFE", "note": "核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "MR/HR Truck Licence", "issuer": "各州交通厅", "note": "驾驶矿山车辆", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "施工类必备", "is_mandatory": 1, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 500, "count_max": 1200, "note": "全国，WA/QLD集中"},
    {"platform": "Indeed", "count_min": 250, "count_max": 600, "note": "FIFO地下矿工"},
    {"platform": "LinkedIn", "count_min": 80, "count_max": 200, "note": "大型矿业集团"},
]
SALARIES = [
    {"experience": "初级矿工（0~2年）", "salary_min": 80000, "salary_max": 100000, "salary_note": "Mining Industry Award基础", "sort_order": 0},
    {"experience": "中级矿工（2~6年）", "salary_min": 100000, "salary_max": 140000, "salary_note": "WA FIFO年薪均值", "sort_order": 1},
    {"experience": "高级/领班（6年+）", "salary_min": 140000, "salary_max": 200000, "salary_note": "关停期额外收入", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "矿业雇主担保", "sort_order": 0},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 1},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "机械操作+安全规程"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Cert II可6个月入行"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Cert II/III+驾照"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "WA/QLD矿业长期强劲需求"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "岗位远多于求职者"},
    {"dimension": "work_intensity",           "label_zh": "极高", "stars": 5, "note": "FIFO+地下高危环境，12hr班"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级FIFO $100k~$140k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "关键矿产战略驱动长期需求"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "自动化提升效率，仍需大量一线人员"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，偏远区491"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "技能要求不高，积分相对容易"},
]
SUITABILITY_FIT = [
    "接受FIFO模式和地下高强度工作环境，追求矿业高薪",
    "有重型机械驾驶或采矿背景，快速进入WA/QLD矿业",
]
SUITABILITY_UNFIT = [
    "有幽闭恐惧或不接受地下作业",
    "不接受FIFO和高危工作环境",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 811511 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Underground Miner 薪资及岗位量", "url": "https://www.seek.com.au/underground-miner-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲地下矿工工资多少？", "answer": "中级FIFO地下矿工年薪约 $100,000~$140,000。高级/领班可达 $140,000~$200,000，关停期额外收入丰厚。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲矿工容易找工作吗？", "answer": "非常容易。WA/QLD矿业岗位长期大量空缺，Seek挂牌500~1200个，供不应求。"},
    {"faq_type": "education_limit", "sort_order": 2, "question": "没有采矿经验可以入行吗？", "answer": "可以。Certificate II（3~6个月）是最快入行路径，部分矿业公司直接提供在职培训。"},
]
MARKDOWN = """# 地下矿工（Underground Miner）职业分析 · 澳大利亚

**职业代码：811511 – Underground Miner。**

地下矿工在WA/QLD地下矿山操作钻机和装载机械，是澳洲FIFO收入最高的体力工种之一。关键矿产战略（锂/铜/镍）驱动新矿山开发，至2030年需求持续扩张。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级矿工（0~2年） | $80,000~$100,000 |
| 中级（2~6年）FIFO | $100,000~$140,000 |
| 高级/领班 | $140,000~$200,000 |

---

*数据来源：JSA、Seek AU、Department of Home Affairs（2025-2026）*
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
    print("[OK] 地下矿工入库完成")
if __name__ == "__main__": run()
