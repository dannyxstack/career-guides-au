"""过程/控制工程师 (233912) Process Engineer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "233912", "anzsco_title": "Process Engineer",
    "category": "工程", "workforce_size": 9000, "shortage_listed": 1,
    "growth_areas": json.dumps(["LNG & Gas Processing","Mining Mineral Processing","Battery & Critical Minerals","Water Treatment Plants"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "过程工程师",
    "summary": "过程工程师设计和优化工业生产流程，广泛服务于油气、矿业、化工和食品加工行业。澳洲LNG出口、关键矿物加工和新能源产业链持续扩张，为过程工程师提供丰富机会，薪资水平极具吸引力。",
    "forecast_note": "澳洲锂矿、镍矿等关键矿物加工产业链本地化趋势2025-2030年持续推进，LNG出口设施维护升级也产生大量需求。能源转型新装置建设将为过程工程师带来充足就业机会。",
    "trend_summary": "数字孪生技术和流程模拟软件（Aspen、HYSYS）广泛应用，AI辅助工艺优化成新趋势。油气行业经验可横向迁移至矿业和新能源领域，拓宽了职业发展路径。"}
I18N_EN = {"locale": "en", "name": "Process Engineer",
    "summary": "Process engineers design and optimise industrial production processes across oil and gas, mining, chemicals and food processing. Australia's expanding LNG exports, critical mineral processing and new energy supply chains provide strong demand for process engineers at very competitive salaries.",
    "forecast_note": "Australia's domestic critical mineral processing (lithium, nickel) is expanding 2025-2030, alongside LNG facility maintenance and upgrade cycles. Energy transition new-build projects will sustain strong employment for process engineers.",
    "trend_summary": "Digital twin technology and process simulation software (Aspen, HYSYS) are standard. AI-assisted process optimisation is emerging. Oil and gas experience is highly transferable to mining and new energy sectors."}
EDUCATION = [
    {"stage": "Bachelor of Chemical/Process Engineering", "duration": "4年", "cost_min": 32000, "cost_max": 56000, "cost_note": "国际生约$160k~$210k总费", "sort_order": 0},
    {"stage": "Engineers Australia Competency Assessment", "duration": "2~5年经验积累", "cost_min": 500, "cost_max": 2000, "cost_note": "CPEng申请", "sort_order": 1},
    {"stage": "Oil & Gas / Mining Sector On-the-Job Training", "duration": "持续进修", "cost_min": 0, "cost_max": 5000, "cost_note": "行业特定培训", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Chemical/Process Engineering", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "MIEAust / CPEng", "issuer": "Engineers Australia", "note": "专业执照", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Functional Safety Engineer (FSE)", "issuer": "TÜV/exida", "note": "油气行业加分项", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 350, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 120, "count_max": 200, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 150, "count_max": 260, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 80000, "salary_max": 100000, "salary_note": "Graduate Process Engineer", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 105000, "salary_max": 150000, "salary_note": "Process Engineer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 155000, "salary_max": 220000, "salary_note": "Senior/Principal Engineer", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，工程紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，WA/QLD开放", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较难", "stars": 4, "note": "需化工/流体力学基础"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "本科4年+行业经验"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CPEng可逐步考取"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 5, "note": "油气矿业持续招聘"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "含倒班和远矿工作"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "AUD 10.5万~22万"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "新能源转型带来新机遇"},
    {"dimension": "ai_risk",                  "label_zh": "低", "stars": 1, "note": "工艺判断与安全签章难以替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "多州紧缺清单在列"},
    {"dimension": "pr_difficulty",            "label_zh": "较易", "stars": 2, "note": "技术移民优先通道"},
]
SUITABILITY_FIT = ["有化工/化学工程背景者", "能接受FIFO（fly-in fly-out）工作模式者", "喜欢工艺优化与数据分析结合工作者"]
SUITABILITY_UNFIT = ["不接受轮班或远程驻场者", "偏好纯办公室环境者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 233912 过程工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/process-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "过程工程师在澳洲薪资怎么样？", "answer": "初级约AUD 8万~10万，中级10.5万~15万，高级/主任工程师15.5万~22万，矿业FIFO有额外津贴。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲过程工程师市场如何？", "answer": "WA和QLD矿业及油气行业需求最旺，全澳Seek常年有200~350个活跃职位，关键矿物加工产业快速扩张。"},
]
MARKDOWN = """# 过程工程师（Process Engineer）职业分析 · 澳大利亚

**职业代码：233912 – Process Engineer。**

过程工程师设计并优化工业生产流程，在澳洲油气、矿业和关键矿物加工行业中发挥核心作用，薪资极具竞争力。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $80,000~$100,000 |
| 中级（3-8年） | $105,000~$150,000 |
| 高级（8年+） | $155,000~$220,000 |

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
    print("[OK] 过程工程师入库完成")
if __name__ == "__main__": run()
