"""Mine Surveyor (232612) 矿山测量师 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "232612", "anzsco_title": "Mine Surveyor",
    "category": "采矿", "workforce_size": 3500, "shortage_listed": 1,
    "growth_areas": json.dumps(["WA Gold & Nickel Mines","Critical Minerals New Projects","Underground 3D Mapping","Digital Twin Mine Modelling"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "矿山测量师",
    "summary": "矿山测量师（Mine Surveyor）提供矿山地表和地下精密测量服务，包括爆破标定、进度测量和矿体建模。这是采矿行业中的专业技术岗位，通常需要测量学学位或工程学位，加上矿山测量从业执照。持续短缺，薪资远高于普通测量师。",
    "forecast_note": "WA关键矿产项目激增，矿山测量师需求2025-2026年显著增加。无人机+LiDAR+数字孪生技术改变传统工作流，懂新技术的测量师高度抢手。",
    "trend_summary": "无人机航测（UAV）和3D激光扫描快速替代传统全站仪，但矿山测量的专业判断仍需持证人员。矿山测量师是采矿业最难招募的专业之一。"}
I18N_EN = {"locale": "en", "name": "Mine Surveyor",
    "summary": "Mine surveyors provide precision surface and underground survey services including blast pegging, progress measurement and orebody modelling. A specialist technical role requiring a surveying or engineering degree plus mine surveying practising certificate. Persistently scarce with pay well above general surveyors.",
    "forecast_note": "WA critical minerals project boom significantly increasing mine surveyor demand in 2025-2026. UAV + LiDAR + digital twin technology transforming traditional workflows; surveyors skilled in new tech highly sought after.",
    "trend_summary": "Drone photogrammetry (UAV) and 3D laser scanning rapidly supplementing traditional total station methods, but specialist judgment still requires licensed personnel. Mine surveyors are among the hardest mining professionals to recruit."}
EDUCATION = [
    {"stage": "Bachelor of Surveying or Mining Engineering", "duration": "3~4年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际留学生更高", "sort_order": 0},
    {"stage": "Mine Surveyor Practising Certificate", "duration": "经验积累后申请", "cost_min": 500, "cost_max": 2000, "cost_note": "各州矿监局颁发", "sort_order": 1},
    {"stage": "海外学历技能评估（Engineers Australia / AIES）", "duration": "6~12个月", "cost_min": 1000, "cost_max": 3000, "cost_note": "移民路径", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Surveying or Mining Engineering", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Mine Surveyor Practising Certificate", "issuer": "各州矿监局", "note": "独立执业必备", "is_mandatory": 1, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 60, "count_max": 150, "note": "全国，WA/QLD集中"},
    {"platform": "Indeed", "count_min": 30, "count_max": 80, "note": "矿山测量专职"},
    {"platform": "LinkedIn", "count_min": 20, "count_max": 60, "note": "大型矿业公司和测量咨询"},
]
SALARIES = [
    {"experience": "初级矿山测量师（0~3年）", "salary_min": 90000, "salary_max": 115000, "salary_note": "采矿行业基础", "sort_order": 0},
    {"experience": "中级（3~8年）FIFO", "salary_min": 120000, "salary_max": 170000, "salary_note": "WA矿山均值", "sort_order": 1},
    {"experience": "高级/首席测量师（8年+）", "salary_min": 170000, "salary_max": 230000, "salary_note": "大型矿山或咨询公司", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "矿业雇主担保", "sort_order": 0},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "独立技术移民，积分制", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "WA/QLD优先", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "高",   "stars": 4, "note": "测量学+矿山地质+3D建模"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学士3~4年+实习经验"},
    {"dimension": "certification_difficulty", "label_zh": "高",   "stars": 4, "note": "学位+州级执照"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "矿业极度短缺专业"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "矿山测量师是最难招的岗位之一"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "FIFO但属专业技术工种"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级FIFO $120k~$170k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "新矿山+无人机测量新技能双重需求"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助数据处理，但专业判断不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，189/190均可申请"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "Engineers Australia评估+英语"},
]
SUITABILITY_FIT = [
    "有测量或采矿工程学位，目标矿业高薪FIFO职业",
    "擅长空间数据和3D技术，有无人机或LiDAR经验加分",
]
SUITABILITY_UNFIT = [
    "无测量或工程学历背景",
    "不接受FIFO矿区环境",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 232612 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Mine Surveyor 薪资及岗位量", "url": "https://www.seek.com.au/mine-surveyor-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲矿山测量师工资多少？", "answer": "中级FIFO矿山测量师年薪约 $120,000~$170,000。高级/首席可达 $230,000+，是矿业专业人才中收入最高的之一。"},
    {"faq_type": "recognition", "sort_order": 1, "question": "中国测量学历澳洲认可吗？", "answer": "需通过Engineers Australia或AIES学历评估，再结合工作经验申请州级矿山测量执照（各州要求不同）。"},
]
MARKDOWN = """# 矿山测量师（Mine Surveyor）职业分析 · 澳大利亚

**职业代码：232612 – Mine Surveyor。**

矿山测量师为矿山提供精密测量和建模服务，是矿业中薪资最高、最难招募的专业之一。关键矿产新矿山开发持续推动需求，无人机和LiDAR新技能进一步提升薪资溢价。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0~3年） | $90,000~$115,000 |
| 中级 FIFO（3~8年） | $120,000~$170,000 |
| 高级/首席 | $170,000~$230,000+ |

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
    print("[OK] 矿山测量师入库完成")
if __name__ == "__main__": run()
