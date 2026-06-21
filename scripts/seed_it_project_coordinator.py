"""IT项目协调员 (224211) IT Project Coordinator — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "224211", "anzsco_title": "IT Project Coordinator",
    "category": "IT", "workforce_size": 18000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Digital Transformation Programs","Cloud Migration Coordination","Agile Programme Office","Government ICT Projects"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "IT项目协调员",
    "summary": "IT项目协调员负责协调信息技术项目的进度、资源和沟通，是项目团队与各部门之间的关键联络人。澳洲大规模数字化转型项目持续推进，对具备IT背景和项目管理技能的协调人才需求旺盛，是从IT技术支持晋升的热门路径。",
    "forecast_note": "澳洲政府和企业数字化转型项目规模持续扩大，2025-2030年IT项目协调和PMO（项目管理办公室）职位需求稳步增长。PMP或PRINCE2认证结合IT背景是晋升为项目经理的标准路径。",
    "trend_summary": "Agile（Scrum/Kanban）项目管理方法已成为IT行业主流，项目协调员须熟悉敏捷工具（Jira、Confluence）。混合项目管理模式（Agile+Waterfall）在大型政府项目中广泛应用，PMP认证仍是重要加分项。"}
I18N_EN = {"locale": "en", "name": "IT Project Coordinator",
    "summary": "IT project coordinators coordinate the progress, resources and communications of information technology projects, serving as the key liaison between project teams and departments. Australia's large-scale digital transformation projects are driving sustained demand for IT-background project management talent; this is a popular advancement path from IT support roles.",
    "forecast_note": "Australian government and enterprise digital transformation project scale continues to grow; IT project coordination and PMO roles will see steady demand growth 2025-2030. PMP or PRINCE2 certification combined with IT experience is the standard path to project manager.",
    "trend_summary": "Agile (Scrum/Kanban) project management has become the IT industry mainstream; project coordinators must be familiar with agile tools (Jira, Confluence). Hybrid project management (Agile+Waterfall) is widely used in large government projects; PMP certification remains an important differentiator."}
EDUCATION = [
    {"stage": "Bachelor of IT / Business / Management", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "CAPM / PMP Project Management Certification", "duration": "3~6个月备考", "cost_min": 600, "cost_max": 2500, "cost_note": "项目管理核心认证", "sort_order": 1},
    {"stage": "Scrum Master / Agile Practitioner Certification", "duration": "1~2个月", "cost_min": 400, "cost_max": 1500, "cost_note": "敏捷加分项", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of IT / Business", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "PMP / CAPM", "issuer": "PMI", "note": "项目管理核心认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Certified Scrum Master (CSM)", "issuer": "Scrum Alliance", "note": "敏捷方法论认证", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 250, "count_max": 450, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 160, "count_max": 300, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 200, "count_max": 380, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 62000, "salary_max": 82000, "salary_note": "Junior IT Coordinator", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 85000, "salary_max": 118000, "salary_note": "IT Project Coordinator", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 120000, "salary_max": 160000, "salary_note": "Senior Coordinator / PM", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，IT管理类", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "沟通管理为主，技术要求中等"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位+认证约3~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "PMP需准备时间"},
    {"dimension": "job_demand",               "label_zh": "稳定", "stars": 3, "note": "数字化项目持续增长"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "申请者较多"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "项目关键节点压力集中"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "AUD 8.5万~16万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 4, "note": "晋升IT项目经理路径清晰"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "协调沟通难以自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "IT管理类移民可行"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需PMP认证和经验"},
]
SUITABILITY_FIT = ["有IT背景并希望转向项目管理的技术人员", "具备强沟通协调能力的IT从业者", "希望进入大型数字化转型项目工作者"]
SUITABILITY_UNFIT = ["纯技术开发偏好者", "不擅长跨部门沟通和项目协调者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 224211 IT项目协调员数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/it-project-coordinator-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "IT项目协调员在澳洲薪资如何？", "answer": "初级约AUD 6.2万~8.2万，中级8.5万~11.8万，高级协调员/初级项目经理12万~16万，政府项目稳定且薪资有竞争力。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲IT项目协调员好找工作吗？", "answer": "需求稳定旺盛，Seek常年有250~450个活跃职位，政府和大型企业IT部门是主要雇主，PMP认证明显提升竞争力。"},
]
MARKDOWN = """# IT项目协调员（IT Project Coordinator）职业分析 · 澳大利亚

**职业代码：224211 – IT Project Coordinator。**

IT项目协调员是数字化转型项目的关键联络人，是技术人员转型项目管理方向的重要跳板，晋升IT项目经理路径清晰。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $62,000~$82,000 |
| 中级（3-8年） | $85,000~$118,000 |
| 高级（8年+） | $120,000~$160,000 |

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
    print("[OK] IT项目协调员入库完成")
if __name__ == "__main__": run()
