"""测量/质量工程师 (233917) Quality Engineer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "233917", "anzsco_title": "Quality Engineer",
    "category": "工程", "workforce_size": 12000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Construction Quality Assurance","Manufacturing Quality Systems","Defence & Aerospace QA","Pharmaceutical & Food Safety"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "质量工程师",
    "summary": "质量工程师负责建立和维护质量管理体系，确保工程项目、制造产品和服务符合标准规范。澳洲建筑行业、国防制造和食品医疗等行业均有持续需求，ISO认证和AS/NZS标准知识是核心竞争力。",
    "forecast_note": "澳洲国防制造本地化战略（AUKUS）和大型基础设施项目对质量保证专业人员需求2025-2030年稳步增长。食品安全法规收紧和医疗器械质量监管升级也推动相关行业质量工程师需求上升。",
    "trend_summary": "ISO 9001质量管理体系和Six Sigma方法论在澳洲制造和工程行业广泛应用，数字化质量平台提升检测效率。具备行业特定认证（AS9100航空/ISO 13485医疗）的质量工程师薪资溢价明显。"}
I18N_EN = {"locale": "en", "name": "Quality Engineer",
    "summary": "Quality engineers establish and maintain quality management systems, ensuring engineering projects, manufactured products and services meet standards. Sustained demand from construction, defence manufacturing, food and medical sectors. ISO certification and AS/NZS standards knowledge are core competencies.",
    "forecast_note": "Australia's defence manufacturing localisation strategy (AUKUS) and major infrastructure projects are driving steady growth in quality assurance roles 2025-2030. Tightening food safety regulations and medical device quality oversight are further growth drivers.",
    "trend_summary": "ISO 9001 and Six Sigma are widely applied in Australian manufacturing and engineering. Digital quality platforms are improving inspection efficiency. Engineers with sector-specific certifications (AS9100 for aerospace, ISO 13485 for medical devices) command salary premiums."}
EDUCATION = [
    {"stage": "Bachelor of Engineering (Mech/Civil/Industrial)", "duration": "4年", "cost_min": 30000, "cost_max": 55000, "cost_note": "国际生约$150k总费", "sort_order": 0},
    {"stage": "ISO 9001 Lead Auditor / Six Sigma Certification", "duration": "1~3个月", "cost_min": 1000, "cost_max": 4000, "cost_note": "在职可完成", "sort_order": 1},
    {"stage": "Sector-Specific QA Training (AS9100/ISO 13485)", "duration": "数周至数月", "cost_min": 500, "cost_max": 3000, "cost_note": "行业加分项", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Engineering", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "ISO 9001 Lead Auditor", "issuer": "BSI / SAI Global", "note": "质量管理核心认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Six Sigma Green/Black Belt", "issuer": "ASQ / IASSC", "note": "流程改善加分", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 180, "count_max": 320, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 100, "count_max": 200, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 130, "count_max": 250, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "Quality Officer/Graduate", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 92000, "salary_max": 125000, "salary_note": "Quality Engineer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 128000, "salary_max": 170000, "salary_note": "Senior QA/Quality Manager", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需工程+标准法规知识"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 3, "note": "本科4年+认证积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "ISO/Six Sigma可短期备考"},
    {"dimension": "job_demand",               "label_zh": "稳定", "stars": 3, "note": "各行业均有需求"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "需求稳定，竞争适中"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "以办公室审查为主"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 3, "note": "AUD 9.2万~17万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 3, "note": "国防和医疗行业前景好"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "部分检测可自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "工程类职业移民友好"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需积累行业经验"},
]
SUITABILITY_FIT = ["注重流程和规范、对细节要求高者", "希望在多行业横向发展者", "有工程背景但偏好系统管理工作者"]
SUITABILITY_UNFIT = ["偏好纯设计或现场施工者", "不耐繁琐文档和审查工作者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 233917 质量工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/quality-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "质量工程师在澳洲薪资如何？", "answer": "初级约AUD 7万~9万，中级9.2万~12.5万，高级/质量经理12.8万~17万，国防和医疗器械行业有溢价。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲质量工程师好找工作吗？", "answer": "需求稳定，各行业均有需求，国防制造、建筑和食品医疗是最主要的就业方向，Seek常年有180~320个活跃职位。"},
]
MARKDOWN = """# 质量工程师（Quality Engineer）职业分析 · 澳大利亚

**职业代码：233917 – Quality Engineer。**

质量工程师建立和维护质量管理体系，确保工程项目和产品符合澳洲标准，在国防、建筑和医疗行业需求稳定。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $70,000~$90,000 |
| 中级（3-8年） | $92,000~$125,000 |
| 高级（8年+） | $128,000~$170,000 |

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
    print("[OK] 质量工程师入库完成")
if __name__ == "__main__": run()
