"""岩土工程师 (233215) Geotechnical Engineer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "233215", "anzsco_title": "Geotechnical Engineer",
    "category": "工程", "workforce_size": 8000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Mining Infrastructure","Tunnelling & Underground Works","Coastal & Flood Management","Renewable Energy Foundations"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "岩土工程师",
    "summary": "岩土工程师专注于土壤、岩石及地下工程分析，为建筑物基础、隧道、矿山边坡和海岸防护提供专业设计。澳洲矿业、基础设施建设及采矿业的持续投入使该职业长期处于紧缺状态，持证工程师（CPEng/RPEQ）薪资极具竞争力。",
    "forecast_note": "澳洲地下基础设施项目（轨道交通、水坝、矿山）2025-2030年投资超$500亿，岩土工程师需求持续高涨。气候变化引发的滑坡与海岸侵蚀风险管理也推动专业需求增长。",
    "trend_summary": "GIS技术与三维地质建模普及，自动化监测设备减少现场工作量，但工程判断与签章责任仍需持证岩土工程师。地下工程与矿业岩土细分方向薪资溢价明显。"}
I18N_EN = {"locale": "en", "name": "Geotechnical Engineer",
    "summary": "Geotechnical engineers analyse soil, rock and underground conditions to design foundations, tunnels, mine slopes and coastal defences. Australia's mining, infrastructure and construction sectors maintain strong demand, with licensed engineers (CPEng/RPEQ) commanding top salaries.",
    "forecast_note": "Over $50B in underground infrastructure projects (rail, dams, mines) planned 2025-2030, sustaining high geotechnical demand. Climate-driven slope instability and coastal erosion risk management also driving specialist roles.",
    "trend_summary": "GIS and 3D geological modelling are now standard tools; automated monitoring reduces fieldwork, but engineering judgement and sign-off still requires licensed geotechnical engineers. Mining geotechnics commands a salary premium."}
EDUCATION = [
    {"stage": "Bachelor of Civil/Geotechnical Engineering", "duration": "4年", "cost_min": 32000, "cost_max": 55000, "cost_note": "国际生约$160k~$200k总费", "sort_order": 0},
    {"stage": "Engineers Australia Competency Assessment", "duration": "2~5年工作经验", "cost_min": 500, "cost_max": 2000, "cost_note": "MIEAust/CPEng申请", "sort_order": 1},
    {"stage": "RPEQ / State Engineer Registration", "duration": "视州而定", "cost_min": 500, "cost_max": 2000, "cost_note": "独立签章必备", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Civil/Geotechnical Engineering", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "MIEAust / CPEng", "issuer": "Engineers Australia", "note": "专业会员/执业工程师", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "RPEQ (QLD) / REC", "issuer": "各州工程师委员会", "note": "独立签章执业", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 150, "count_max": 250, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 80, "count_max": 140, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 180, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "Graduate Engineer", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 100000, "salary_max": 140000, "salary_note": "Project Engineer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 145000, "salary_max": 200000, "salary_note": "Principal/CPEng", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，工程紧缺职业", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居，工程紧缺", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，多州开放", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较难", "stars": 4, "note": "需扎实地质/力学基础"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "本科4年+工作经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CPEng/RPEQ可逐步考取"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 5, "note": "长期紧缺职业"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 3, "note": "含现场勘察与出差"},
    {"dimension": "income_level",             "label_zh": "高", "stars": 5, "note": "AUD 10万~20万区间"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "基建与矿业持续投入"},
    {"dimension": "ai_risk",                  "label_zh": "低", "stars": 1, "note": "需现场判断，AI难替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "多州紧缺清单在列"},
    {"dimension": "pr_difficulty",            "label_zh": "较易", "stars": 2, "note": "技术移民优先通道"},
]
SUITABILITY_FIT = ["有岩土/土木工程背景者", "喜欢户外现场勘察与实验室结合工作者", "对矿业或基础设施建设感兴趣者"]
SUITABILITY_UNFIT = ["不耐受出差和野外作业者", "纯粹偏好办公室工作者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 233215 岩土工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/geotechnical-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "岩土工程师在澳洲薪资怎么样？", "answer": "初级约AUD 7.5万~9.5万，中级10万~14万，持证高级工程师可达14.5万~20万。矿业项目薪资溢价明显。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲岩土工程师好找工作吗？", "answer": "是长期紧缺职业，Seek常年有150~250个活跃职位，WA、QLD矿业地区和NSW/VIC基础设施项目需求最旺。"},
]
MARKDOWN = """# 岩土工程师（Geotechnical Engineer）职业分析 · 澳大利亚

**职业代码：233215 – Geotechnical Engineer。**

岩土工程师专注土壤、岩石与地下工程，服务矿业、基础设施、隧道与海岸防护领域，是澳洲长期紧缺的核心工程职业。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $75,000~$95,000 |
| 中级（3-8年） | $100,000~$140,000 |
| 高级（8年+） | $145,000~$200,000 |

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
    print("[OK] 岩土工程师入库完成")
if __name__ == "__main__": run()
