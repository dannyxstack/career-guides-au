"""商业智能分析师 (262199) BI Analyst — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "262199", "anzsco_title": "BI Analyst",
    "category": "IT", "workforce_size": 16000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Power BI & Tableau Dashboards","Data Lakehouse & Azure Synapse","Retail & E-commerce Analytics","Government Open Data Platforms"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "商业智能分析师",
    "summary": "商业智能分析师通过数据可视化、报表设计和洞察挖掘，帮助企业做出数据驱动的业务决策。澳洲各行业数字化转型加速了对Power BI、Tableau和云数据仓库专业人才的需求，是数据职业中入行门槛最友好的方向之一。",
    "forecast_note": "澳洲企业2025-2030年持续加大数据基础设施投入，BI平台向云端迁移和自助分析民主化推动分析师需求持续增长。具备数据建模和云平台（Azure Synapse/Databricks）技能的BI工程师薪资明显高于纯报表分析师。",
    "trend_summary": "Power BI和Tableau是澳洲最主流的BI工具，Looker和Qlik在企业级市场占有一席之地。数据仓库建模（dbt）和Python分析技能成为高级BI工程师的标配，职业路径向数据工程师和数据分析师方向延伸。"}
I18N_EN = {"locale": "en", "name": "BI Analyst",
    "summary": "BI analysts use data visualisation, reporting and insight generation to support data-driven business decisions. Australia's accelerating digital transformation is driving demand for Power BI, Tableau and cloud data warehouse specialists; this is one of the more accessible entry points into data careers.",
    "forecast_note": "Australian enterprises will continue increasing data infrastructure investment 2025-2030; BI platform cloud migration and self-service analytics democratisation are driving analyst demand. BI engineers with data modelling and cloud platform skills (Azure Synapse/Databricks) earn noticeably more.",
    "trend_summary": "Power BI and Tableau are the dominant BI tools in Australia; Looker and Qlik maintain enterprise market positions. Data warehouse modelling (dbt) and Python analytical skills are becoming standard for senior BI engineers, with career paths extending to data engineering and analytics engineering."}
EDUCATION = [
    {"stage": "Bachelor of IT / Data Science / Statistics", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "Microsoft Power BI / Tableau Desktop Certification", "duration": "1~3个月", "cost_min": 200, "cost_max": 800, "cost_note": "核心工具认证", "sort_order": 1},
    {"stage": "Azure Data Engineer / AWS Data Analytics Cert", "duration": "2~4个月", "cost_min": 300, "cost_max": 1500, "cost_note": "云平台加分项", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of IT / Data Science", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Microsoft Power BI Data Analyst Certification", "issuer": "Microsoft", "note": "最常见BI认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Tableau Desktop Specialist / Certified Associate", "issuer": "Salesforce/Tableau", "note": "可视化认证", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 380, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 130, "count_max": 250, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 180, "count_max": 320, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 65000, "salary_max": 88000, "salary_note": "Junior BI Analyst", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 90000, "salary_max": 125000, "salary_note": "BI Analyst / Developer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 128000, "salary_max": 175000, "salary_note": "Senior BI Engineer / Manager", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，IT紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需SQL+可视化+业务理解"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位+工具认证约3~4年"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Power BI认证入门友好"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 4, "note": "各行业数据需求增长"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "初级岗位竞争较激烈"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "以办公室为主"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 3, "note": "AUD 9万~17.5万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 4, "note": "可发展为数据工程师/架构师"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI可辅助分析但解读仍需人"},
    {"dimension": "pr_friendliness",          "label_zh": "高", "stars": 4, "note": "IT数据类移民通道顺畅"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需要工具认证加持"},
]
SUITABILITY_FIT = ["有数据分析或统计背景者", "喜欢将数据转化为可视化洞察的人", "希望在商业和技术之间架桥的IT专业人士"]
SUITABILITY_UNFIT = ["偏好纯编程开发而非数据分析者", "不愿学习业务背景知识的纯技术人员"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 262199 BI分析师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/business-intelligence-analyst-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "商业智能分析师在澳洲薪资如何？", "answer": "初级约AUD 6.5万~8.8万，中级9万~12.5万，高级BI工程师/经理12.8万~17.5万，云数据平台技能有明显溢价。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲BI分析师好找工作吗？", "answer": "需求持续增长，Seek常年有200~380个活跃职位，金融、零售和政府行业是最大雇主，Power BI技能是最热门要求。"},
]
MARKDOWN = """# 商业智能分析师（BI Analyst）职业分析 · 澳大利亚

**职业代码：262199 – BI Analyst。**

商业智能分析师通过数据可视化和报表分析支持业务决策，是澳洲数据职业中入行门槛最友好且增长最快的方向之一。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $65,000~$88,000 |
| 中级（3-8年） | $90,000~$125,000 |
| 高级（8年+） | $128,000~$175,000 |

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
    print("[OK] 商业智能分析师入库完成")
if __name__ == "__main__": run()
