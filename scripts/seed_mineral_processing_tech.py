"""Mineral Processing Technician (311411) 选矿/湿法冶金技术员 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "311411", "anzsco_title": "Mineral Processing Technician",
    "category": "采矿", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Lithium Processing Plants","Nickel Hydrometallurgy","Rare Earth Processing","Gold & Copper Flotation"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "选矿技术员",
    "summary": "选矿技术员（Mineral Processing Technician）在矿物加工厂监控和优化选矿流程，包括浮选、浸出、过滤和冶金作业。澳洲关键矿产加工（锂/镍/稀土）快速扩张，选矿技术员严重短缺，FIFO薪资极具吸引力。",
    "forecast_note": "澳洲锂电池原料加工（皮尔斯巴拉锂矿/卡尔古利选矿厂）扩产，镍湿法冶金项目激增，对有加工工艺背景的技术员需求大增。",
    "trend_summary": "过程控制自动化提升效率，但工艺优化和故障排查仍需专业人员。化工/冶金+矿产背景组合是最高竞争力。"}
I18N_EN = {"locale": "en", "name": "Mineral Processing Technician",
    "summary": "Mineral processing technicians monitor and optimise mineral processing plant operations including flotation, leaching, filtration and metallurgical processes. Critical minerals processing (lithium/nickel/rare earth) rapidly expanding in Australia, creating severe shortages with attractive FIFO pay.",
    "forecast_note": "Australian lithium battery material processing (Pilbara lithium/Kalgoorlie processing plants) expanding production. Nickel hydrometallurgy projects surging. Large increase in demand for technicians with processing knowledge.",
    "trend_summary": "Process control automation improving efficiency but process optimisation and troubleshooting still requires specialists. Chemical/metallurgical + mineral processing background combination is most competitive."}
EDUCATION = [
    {"stage": "Certificate IV in Process Plant Technology", "duration": "12~18个月", "cost_min": 3000, "cost_max": 8000, "cost_note": "RTO，矿业公司常赞助", "sort_order": 0},
    {"stage": "Diploma in Metallurgy or Mineral Processing", "duration": "18~24个月", "cost_min": 8000, "cost_max": 20000, "cost_note": "进阶路径", "sort_order": 1},
    {"stage": "海外化工/冶金学历评估", "duration": "6~12个月", "cost_min": 1000, "cost_max": 3000, "cost_note": "Engineers Australia评估", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate IV in Process Plant Technology", "issuer": "RTO", "note": "核心入行资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card + Site Safety Induction", "issuer": "矿山", "note": "现场必备", "is_mandatory": 1, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 150, "count_max": 400, "note": "WA/QLD矿山加工厂集中"},
    {"platform": "Indeed", "count_min": 80, "count_max": 200, "note": "选矿和冶金方向"},
    {"platform": "LinkedIn", "count_min": 40, "count_max": 100, "note": "大型矿业集团"},
]
SALARIES = [
    {"experience": "初级技术员（0~3年）", "salary_min": 80000, "salary_max": 105000, "salary_note": "Mining Industry Award", "sort_order": 0},
    {"experience": "中级（3~8年）FIFO", "salary_min": 105000, "salary_max": 145000, "salary_note": "工艺专科溢价", "sort_order": 1},
    {"experience": "高级工艺工程师（8年+）", "salary_min": 140000, "salary_max": 190000, "salary_note": "锂/镍加工专家", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "矿业雇主担保", "sort_order": 0},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "积分制，CSOL在列", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "化工工艺+仪表控制+矿物冶金"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "Cert IV 12~18个月可入行"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Cert IV +现场经验"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "锂/镍/稀土加工扩张，严重短缺"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "有矿物加工背景极度稀缺"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "FIFO，24小时连续生产"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级FIFO $105k~$145k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "关键矿产加工是澳洲战略重点"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "自动化辅助，工艺判断仍需专业人员"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，偏远491"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "化工/冶金评估+英语"},
]
SUITABILITY_FIT = [
    "有化工、冶金或矿物加工工艺背景，目标澳洲关键矿产加工业",
    "接受FIFO连续生产环境，追求矿业高薪",
]
SUITABILITY_UNFIT = [
    "无任何化工或工艺背景",
    "不接受FIFO和24小时连续生产班制",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 311411 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Mineral Processing Technician 薪资及岗位量", "url": "https://www.seek.com.au/mineral-processing-technician-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲选矿技术员工资多少？", "answer": "中级FIFO选矿技术员年薪约 $105,000~$145,000。锂/镍加工专家可达 $140,000~$190,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "为什么选矿技术员这么短缺？", "answer": "澳洲锂/镍关键矿产加工厂快速扩张，但有矿物加工工艺背景的人才极少，供需严重失衡。"},
]
MARKDOWN = """# 选矿技术员（Mineral Processing Technician）职业分析 · 澳大利亚

**职业代码：311411 – Mineral Processing Technician。**

选矿技术员监控矿物加工厂的浮选、浸出等工艺流程，是澳洲关键矿产（锂/镍/稀土）加工业的紧缺专才。锂电池产业链快速扩张使这一职业需求激增。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0~3年） | $80,000~$105,000 |
| 中级 FIFO（3~8年） | $105,000~$145,000 |
| 高级/工艺专家 | $140,000~$190,000+ |

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
    print("[OK] 选矿技术员入库完成")
if __name__ == "__main__": run()
