"""水资源工程师 (233911) Water Resources Engineer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "233911", "anzsco_title": "Water Resources Engineer",
    "category": "工程", "workforce_size": 6000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Desalination & Water Treatment","Flood Mitigation Infrastructure","Irrigation & Agricultural Water","Climate Adaptation Projects"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "水资源工程师",
    "summary": "水资源工程师负责规划、设计和管理供水、排水、防洪及灌溉系统，是应对澳洲干旱与洪涝双重挑战的关键专业。随气候变化加剧，水利基础设施投资持续增加，该职业长期供不应求。",
    "forecast_note": "联邦及各州政府2025-2030年投入超$200亿用于水利基础设施更新与气候适应项目，水资源工程师需求将保持强劲。城市水网老化更新和沿海海水淡化项目是主要增长点。",
    "trend_summary": "水文模型软件（TUFLOW、MIKE）和GIS应用广泛，数字孪生水利系统成新趋势。气候风险评估能力成为差异化竞争优势，CPEng持证工程师优先获得大型项目机会。"}
I18N_EN = {"locale": "en", "name": "Water Resources Engineer",
    "summary": "Water resources engineers plan, design and manage water supply, drainage, flood mitigation and irrigation systems. They are critical for addressing Australia's dual challenges of drought and flooding. Climate change is intensifying infrastructure investment, keeping this role in persistent shortage.",
    "forecast_note": "Federal and state governments are investing $20B+ in water infrastructure and climate adaptation 2025-2030. Urban network renewal and coastal desalination projects are key growth areas for water resources engineers.",
    "trend_summary": "Hydrological modelling software (TUFLOW, MIKE) and GIS are standard tools; digital twin water systems are an emerging trend. Climate risk assessment capability is a key differentiator; CPEng registration is preferred for major projects."}
EDUCATION = [
    {"stage": "Bachelor of Civil/Environmental Engineering", "duration": "4年", "cost_min": 32000, "cost_max": 55000, "cost_note": "国际生约$160k总费", "sort_order": 0},
    {"stage": "Engineers Australia Competency Assessment", "duration": "2~5年工作经验", "cost_min": 500, "cost_max": 2000, "cost_note": "MIEAust/CPEng申请", "sort_order": 1},
    {"stage": "Postgraduate in Water Engineering (可选)", "duration": "1~2年", "cost_min": 30000, "cost_max": 50000, "cost_note": "专攻水文水利", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Civil/Environmental Engineering", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "MIEAust / CPEng", "issuer": "Engineers Australia", "note": "专业执照", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "RPEQ / State Registration", "issuer": "各州工程师委员会", "note": "独立签章", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 100, "count_max": 180, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 60, "count_max": 110, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 80, "count_max": 140, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 72000, "salary_max": 92000, "salary_note": "Graduate Engineer", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 95000, "salary_max": 135000, "salary_note": "Project Engineer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 140000, "salary_max": 190000, "salary_note": "Principal Engineer", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，工程紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较难", "stars": 4, "note": "需水文、流体力学基础"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "本科4年+经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CPEng逐步考取"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 5, "note": "气候变化推动需求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "含现场勘察"},
    {"dimension": "income_level",             "label_zh": "高", "stars": 4, "note": "AUD 9.5万~19万"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "气候投资持续增加"},
    {"dimension": "ai_risk",                  "label_zh": "低", "stars": 1, "note": "需现场判断与工程签章"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "紧缺清单常客"},
    {"dimension": "pr_difficulty",            "label_zh": "较易", "stars": 2, "note": "技术移民优先"},
]
SUITABILITY_FIT = ["有土木/环境工程背景者", "关注气候变化与可持续发展者", "喜欢户外现场与建模结合工作者"]
SUITABILITY_UNFIT = ["不耐受出差与野外作业者", "偏好纯室内工作者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 233911 水资源工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/water-resources-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "水资源工程师澳洲薪资如何？", "answer": "初级约AUD 7.2万~9.2万，中级9.5万~13.5万，高级14万~19万，矿业及大型基础设施项目有额外津贴。"},
    {"faq_type": "demand", "sort_order": 1, "question": "水资源工程师在澳洲好找工作吗？", "answer": "需求持续旺盛，各州政府水利更新项目及私营矿业公司均有大量需求，是长期紧缺职业之一。"},
]
MARKDOWN = """# 水资源工程师（Water Resources Engineer）职业分析 · 澳大利亚

**职业代码：233911 – Water Resources Engineer。**

水资源工程师规划和设计供水、防洪及灌溉系统，是澳洲气候适应基础设施建设中的核心工程职业。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $72,000~$92,000 |
| 中级（3-8年） | $95,000~$135,000 |
| 高级（8年+） | $140,000~$190,000 |

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
    print("[OK] 水资源工程师入库完成")
if __name__ == "__main__": run()
