"""数据库管理员 (262113) Database Administrator — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "262113", "anzsco_title": "Database Administrator",
    "category": "IT", "workforce_size": 14000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Cloud Database Migration","Data Governance & Compliance","Real-Time Analytics Platforms","Healthcare & Government Data"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "数据库管理员",
    "summary": "数据库管理员（DBA）负责设计、维护和优化企业数据库系统，确保数据安全性、可用性和性能。澳洲数字化转型和云迁移持续推动对具备云数据库（AWS RDS、Azure SQL）技能DBA的需求，是IT领域稳定高薪职业。",
    "forecast_note": "澳洲医疗、政府和金融机构的数据治理合规要求持续提升，2025-2030年云DBA和数据平台工程师需求强劲增长。传统DBA向云架构师和数据工程师转型是主流路径。",
    "trend_summary": "PostgreSQL、MySQL和SQL Server仍是主流，NoSQL（MongoDB、Cassandra）和云原生数据库快速增长。自动化管理工具减少了部分日常运维工作，但数据架构设计和性能调优技能仍不可替代。"}
I18N_EN = {"locale": "en", "name": "Database Administrator",
    "summary": "Database administrators design, maintain and optimise enterprise database systems, ensuring data security, availability and performance. Australia's digital transformation and cloud migration are driving strong demand for cloud-database-skilled DBAs (AWS RDS, Azure SQL), making this a stable, well-paid IT career.",
    "forecast_note": "Rising data governance compliance requirements across Australian healthcare, government and finance sectors will drive strong cloud DBA and data platform engineer demand 2025-2030. Traditional DBAs are increasingly transitioning to cloud architect and data engineer roles.",
    "trend_summary": "PostgreSQL, MySQL and SQL Server remain dominant; NoSQL (MongoDB, Cassandra) and cloud-native databases are growing fast. Automation tools have reduced routine ops workloads, but database architecture design and performance tuning remain irreplaceable skills."}
EDUCATION = [
    {"stage": "Bachelor of IT / Computer Science", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "Oracle / Microsoft SQL Server / PostgreSQL Cert", "duration": "1~6个月", "cost_min": 300, "cost_max": 2000, "cost_note": "在职可考", "sort_order": 1},
    {"stage": "AWS Database Specialty / Azure Data Fundamentals", "duration": "1~3个月", "cost_min": 300, "cost_max": 1500, "cost_note": "云DBA加分项", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of IT / Computer Science", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Oracle DBA / Microsoft SQL Server Certification", "issuer": "Oracle/Microsoft", "note": "核心认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "AWS Database Specialty", "issuer": "AWS", "note": "云DBA认证", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 150, "count_max": 280, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 90, "count_max": 180, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 120, "count_max": 220, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 68000, "salary_max": 88000, "salary_note": "Junior DBA", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 92000, "salary_max": 130000, "salary_note": "Database Administrator", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 133000, "salary_max": 175000, "salary_note": "Senior DBA / Data Architect", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，IT紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需SQL和数据库理论基础"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位+认证约3~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "多种认证路径可选"},
    {"dimension": "job_demand",               "label_zh": "稳定", "stars": 4, "note": "企业数据需求持续增长"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "云DBA竞争相对激烈"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "含on-call值班"},
    {"dimension": "income_level",             "label_zh": "高", "stars": 4, "note": "AUD 9.2万~17.5万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 4, "note": "向数据工程师和架构师方向发展"},
    {"dimension": "ai_risk",                  "label_zh": "中低", "stars": 2, "note": "自动化影响部分运维，设计难替代"},
    {"dimension": "pr_friendliness",          "label_zh": "高", "stars": 4, "note": "IT类移民通道顺畅"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需经验和认证"},
]
SUITABILITY_FIT = ["喜欢数据管理和系统优化工作者", "有SQL基础并希望深耕数据领域者", "愿意转向云数据库架构的传统DBA"]
SUITABILITY_UNFIT = ["偏好前端或移动开发者", "不耐受on-call和系统突发故障响应者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 262113 数据库管理员数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/database-administrator-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "数据库管理员在澳洲薪资如何？", "answer": "初级约AUD 6.8万~8.8万，中级9.2万~13万，高级DBA/数据架构师13.3万~17.5万，云数据库专家额外溢价。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲DBA职位好找吗？", "answer": "需求稳定旺盛，Seek常年有150~280个活跃职位，政府、金融和医疗行业是最大雇主，云数据库技能是最热门方向。"},
]
MARKDOWN = """# 数据库管理员（Database Administrator）职业分析 · 澳大利亚

**职业代码：262113 – Database Administrator。**

数据库管理员维护企业核心数据资产，随云迁移和数据治理需求增长，该职业向云DBA和数据架构师方向加速演进。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $68,000~$88,000 |
| 中级（3-8年） | $92,000~$130,000 |
| 高级（8年+） | $133,000~$175,000 |

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
    print("[OK] 数据库管理员入库完成")
if __name__ == "__main__": run()
