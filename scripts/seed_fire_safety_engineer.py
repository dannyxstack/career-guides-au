"""消防安全工程师 (233916) Fire Safety Engineer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "233916", "anzsco_title": "Fire Safety Engineer",
    "category": "工程", "workforce_size": 3500, "shortage_listed": 1,
    "growth_areas": json.dumps(["High-Rise Residential Compliance","Data Centre Fire Safety","Tunnel & Underground Fire Engineering","Industrial Hazardous Materials"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "消防安全工程师",
    "summary": "消防安全工程师运用工程原理设计建筑物防火系统、制定疏散方案并进行火灾风险评估。澳洲建筑规范持续严格化，加之高密度住宅、数据中心和隧道项目增多，消防安全工程师需求持续走强，是极度紧缺的专业工程师之一。",
    "forecast_note": "澳洲各州强化《建筑规范》（NCC/BCA）合规审查，2025-2030年高层住宅和大型公共建筑消防性能化设计需求旺盛。新兴的储能系统（锂电池）消防安全标准推动专业需求进一步上升。",
    "trend_summary": "性能化消防设计（Performance-Based Fire Engineering）替代传统处方式方法成主流，FDS等火焰模拟软件是标配工具。SFPE认证和澳洲消防工程师协会（AFAC/AFSET）资质日益受重视。"}
I18N_EN = {"locale": "en", "name": "Fire Safety Engineer",
    "summary": "Fire safety engineers apply engineering principles to design fire protection systems, evacuation plans and fire risk assessments. Tightening Australian building codes plus growth in high-rise residential, data centres and tunnels keeps this specialty in persistent shortage.",
    "forecast_note": "Strengthened NCC/BCA compliance requirements 2025-2030 drive strong demand for performance-based fire design in high-rise and major public buildings. Emerging battery energy storage fire safety standards are a further growth driver.",
    "trend_summary": "Performance-based fire engineering is replacing prescriptive compliance as the mainstream approach; FDS simulation software is a standard tool. SFPE certification and AFAC/AFSET credentials are increasingly valued by employers."}
EDUCATION = [
    {"stage": "Bachelor of Fire Safety/Mechanical/Civil Engineering", "duration": "4年", "cost_min": 32000, "cost_max": 55000, "cost_note": "国际生约$160k总费", "sort_order": 0},
    {"stage": "Graduate Certificate in Fire Safety Engineering", "duration": "6~12个月", "cost_min": 15000, "cost_max": 30000, "cost_note": "可在职进修", "sort_order": 1},
    {"stage": "SFPE Membership / AFSET Registration", "duration": "视经验而定", "cost_min": 500, "cost_max": 3000, "cost_note": "专业执照", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Engineering (Fire/Civil/Mechanical)", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "MIEAust / CPEng", "issuer": "Engineers Australia", "note": "专业执照", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "SFPE Member / AFSET Registration", "issuer": "SFPE / 各州消防局", "note": "行业权威认证", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 60, "count_max": 120, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 30, "count_max": 70, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 50, "count_max": 100, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 78000, "salary_max": 100000, "salary_note": "Graduate Fire Engineer", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 105000, "salary_max": 145000, "salary_note": "Fire Safety Engineer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 150000, "salary_max": 210000, "salary_note": "Principal Fire Engineer", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，工程紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较难", "stars": 4, "note": "需工程+消防法规双重知识"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "本科4年+专业培训"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "SFPE/AFSET可逐步考取"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 5, "note": "极度紧缺职业"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "全澳从业者稀少"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "以办公室设计为主"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "AUD 10.5万~21万"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "建筑规范持续严格化"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "工程判断和法规责任难替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "工程类紧缺职业"},
    {"dimension": "pr_difficulty",            "label_zh": "较易", "stars": 2, "note": "技术移民优先"},
]
SUITABILITY_FIT = ["有机械/土木工程背景并对消防安全感兴趣者", "希望从事高价值专业咨询工作者", "喜欢结合法规与工程设计的工作者"]
SUITABILITY_UNFIT = ["不愿深入研究建筑规范者", "偏好大批量重复性工作者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 233916 消防安全工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/fire-safety-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "消防安全工程师澳洲薪资如何？", "answer": "初级约AUD 7.8万~10万，中级10.5万~14.5万，主任/高级工程师可达15万~21万，是工程行业薪资溢价最高的专业之一。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲消防安全工程师好找工作吗？", "answer": "全澳从业者极少，处于极度紧缺状态，大型建筑咨询公司和政府机构均有稳定招聘需求。"},
]
MARKDOWN = """# 消防安全工程师（Fire Safety Engineer）职业分析 · 澳大利亚

**职业代码：233916 – Fire Safety Engineer。**

消防安全工程师设计防火系统、制定疏散方案并进行性能化火灾风险评估，是澳洲建筑行业极度紧缺的高薪专业。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $78,000~$100,000 |
| 中级（3-8年） | $105,000~$145,000 |
| 高级（8年+） | $150,000~$210,000 |

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
    print("[OK] 消防安全工程师入库完成")
if __name__ == "__main__": run()
