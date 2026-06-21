"""项目工程师 (233999) Project Engineer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "233999", "anzsco_title": "Project Engineer",
    "category": "工程", "workforce_size": 25000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Infrastructure Megaprojects","Renewable Energy Construction","Defence Projects","Mining Capital Works"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "项目工程师",
    "summary": "项目工程师负责工程项目的技术协调、进度管理和质量控制，是连接设计团队与施工现场的核心角色。澳洲基础设施大投入和能源转型项目持续产生大量需求，具备工程学位和项目管理能力的人才处于供不应求状态。",
    "forecast_note": "2025-2030年澳洲基础设施投资超$3,000亿，铁路、公路、医院和国防项目均需大量项目工程师。可再生能源建设热潮也为电气和机械项目工程师提供了新的增长方向。",
    "trend_summary": "BIM平台、项目管理软件（Procore/Aconex）和数字工地技术改变传统项目执行方式。PMP或CPM认证结合工程学位成为晋升为项目经理的标准路径。"}
I18N_EN = {"locale": "en", "name": "Project Engineer",
    "summary": "Project engineers coordinate technical delivery, schedule management and quality control on engineering projects, bridging design teams and construction sites. Australia's $300B+ infrastructure pipeline and energy transition generate persistent demand for engineers with project management capability.",
    "forecast_note": "Australia's 2025-2030 infrastructure investment pipeline across rail, roads, hospitals and defence will drive continued strong demand for project engineers. Renewable energy construction also provides growth for electrical and mechanical project engineers.",
    "trend_summary": "BIM platforms, project management software (Procore/Aconex) and digital site tools are transforming project delivery. PMP or CPM certification combined with an engineering degree is the standard path to project manager roles."}
EDUCATION = [
    {"stage": "Bachelor of Engineering (Civil/Mechanical/Electrical)", "duration": "4年", "cost_min": 32000, "cost_max": 55000, "cost_note": "国际生约$160k总费", "sort_order": 0},
    {"stage": "PMP / CPM Project Management Certification", "duration": "3~6个月备考", "cost_min": 1000, "cost_max": 5000, "cost_note": "在职可考", "sort_order": 1},
    {"stage": "Engineers Australia Competency Assessment", "duration": "2~5年工作经验", "cost_min": 500, "cost_max": 2000, "cost_note": "CPEng申请", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Engineering", "issuer": "认可大学", "note": "入行必备", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "PMP / CAPM", "issuer": "PMI", "note": "项目管理认证加分", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "MIEAust / CPEng", "issuer": "Engineers Australia", "note": "专业执照", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 400, "count_max": 700, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 250, "count_max": 450, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 350, "count_max": 600, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 75000, "salary_max": 98000, "salary_note": "Graduate Project Engineer", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 100000, "salary_max": 145000, "salary_note": "Project Engineer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 148000, "salary_max": 200000, "salary_note": "Senior/Principal Engineer", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，工程紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，多州开放", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "技术+管理双能力"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "本科4年+项目经验"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "PMP可短期备考"},
    {"dimension": "job_demand",               "label_zh": "极旺", "stars": 5, "note": "全澳岗位最多的工程类职位之一"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "需求大但申请者也多"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 4, "note": "现场与办公室结合"},
    {"dimension": "income_level",             "label_zh": "高", "stars": 4, "note": "AUD 10万~20万"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "晋升项目经理路径清晰"},
    {"dimension": "ai_risk",                  "label_zh": "低", "stars": 2, "note": "协调与现场判断难以替代"},
    {"dimension": "pr_friendliness",          "label_zh": "高", "stars": 4, "note": "工程类移民友好"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "竞争较多需积累经验"},
]
SUITABILITY_FIT = ["有工程学位并希望进入项目管理方向者", "能接受现场出差和项目驻场工作者", "具备跨团队沟通协调能力者"]
SUITABILITY_UNFIT = ["不喜欢现场环境者", "只希望从事纯设计工作者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 233999 项目工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/project-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "项目工程师在澳洲薪资怎么样？", "answer": "初级约AUD 7.5万~9.8万，中级10万~14.5万，高级/主任工程师14.8万~20万，大型基础设施项目有额外津贴。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲项目工程师好找工作吗？", "answer": "是全澳岗位量最大的工程类职位之一，Seek常年有400~700个活跃职位，基础设施、矿业和可再生能源行业均有强劲需求。"},
]
MARKDOWN = """# 项目工程师（Project Engineer）职业分析 · 澳大利亚

**职业代码：233999 – Project Engineer。**

项目工程师是澳洲基础设施建设和工程行业的核心执行岗位，负责技术协调、进度和质量管理，晋升路径清晰，薪资具竞争力。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $75,000~$98,000 |
| 中级（3-8年） | $100,000~$145,000 |
| 高级（8年+） | $148,000~$200,000 |

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
    print("[OK] 项目工程师入库完成")
if __name__ == "__main__": run()
