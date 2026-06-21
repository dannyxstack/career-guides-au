"""ERP顾问 (261111) ERP Consultant — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "261111", "anzsco_title": "ERP Consultant",
    "category": "IT", "workforce_size": 8000, "shortage_listed": 1,
    "growth_areas": json.dumps(["SAP S/4HANA Migrations","Oracle Cloud ERP","Microsoft Dynamics 365","Government ERP Transformation"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "ERP顾问",
    "summary": "ERP顾问负责企业资源规划系统的实施、配置、培训和优化，是企业数字化转型的关键专业人员。澳洲大型企业和政府机构持续推进SAP、Oracle和Microsoft ERP系统升级，具备行业知识的认证ERP顾问长期供不应求。",
    "forecast_note": "澳洲SAP S/4HANA迁移浪潮2025-2028年进入高峰期，政府数字化转型项目大量采购ERP系统。具备制造业、零售或政府行业背景的ERP顾问日合费率可达$1,200~$2,000。",
    "trend_summary": "云ERP（SaaS模式）加速取代传统本地部署，顾问须同时掌握业务流程和云技术。AI驱动的流程自动化（SAP AI/Oracle Fusion AI）成新技能要求，提高了入门门槛但也扩大了高端市场需求。"}
I18N_EN = {"locale": "en", "name": "ERP Consultant",
    "summary": "ERP consultants implement, configure, train and optimise enterprise resource planning systems, playing a key role in business digital transformation. Australian large enterprises and government agencies are continuously upgrading SAP, Oracle and Microsoft ERP systems, keeping certified ERP consultants in persistent short supply.",
    "forecast_note": "Australia's SAP S/4HANA migration wave peaks 2025-2028; government digital transformation projects are procuring ERP systems heavily. Consultants with manufacturing, retail or government sector backgrounds command daily rates of $1,200-$2,000.",
    "trend_summary": "Cloud ERP (SaaS) is rapidly replacing on-premise deployments; consultants must master both business processes and cloud technology. AI-driven process automation (SAP AI, Oracle Fusion AI) is a new skills requirement, raising the entry bar while expanding the high-end market."}
EDUCATION = [
    {"stage": "Bachelor of IT / Business / Accounting", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "SAP Certified Associate / Oracle Cloud Certification", "duration": "3~6个月备考", "cost_min": 800, "cost_max": 4000, "cost_note": "核心认证", "sort_order": 1},
    {"stage": "Industry Functional Training (Finance/Supply Chain)", "duration": "持续进修", "cost_min": 500, "cost_max": 3000, "cost_note": "行业模块专精", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of IT / Business / Accounting", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "SAP Certified Application Associate", "issuer": "SAP", "note": "主流ERP认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Oracle Cloud ERP Implementation Specialist", "issuer": "Oracle", "note": "Oracle路线认证", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 120, "count_max": 220, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 70, "count_max": 140, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 180, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 75000, "salary_max": 100000, "salary_note": "Junior ERP Consultant", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 105000, "salary_max": 155000, "salary_note": "ERP Consultant", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 160000, "salary_max": 250000, "salary_note": "Senior/Principal Consultant", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，IT顾问紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较难", "stars": 4, "note": "需业务流程+技术双栈能力"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学位+认证+行业经验积累"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "SAP/Oracle认证需系统学习"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 5, "note": "迁移项目高峰期"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "高端顾问供不应求"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 4, "note": "项目期出差和加班常见"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "AUD 10.5万~25万+合同费率"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "云ERP持续扩张"},
    {"dimension": "ai_risk",                  "label_zh": "低", "stars": 2, "note": "业务判断和变革管理难替代"},
    {"dimension": "pr_friendliness",          "label_zh": "高", "stars": 4, "note": "IT类移民友好"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需认证和项目经验"},
]
SUITABILITY_FIT = ["有IT或会计/财务背景并希望进入顾问行业者", "具备业务分析和系统配置能力者", "能接受频繁出差和项目驻场者"]
SUITABILITY_UNFIT = ["不愿出差的纯技术开发偏好者", "不喜欢与业务部门沟通协调者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 261111 ERP顾问数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/erp-consultant-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "ERP顾问在澳洲薪资怎么样？", "answer": "初级约AUD 7.5万~10万，中级10.5万~15.5万，高级顾问16万~25万，合同制顾问日费率可达$1,200~$2,000+。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲ERP顾问需求旺盛吗？", "answer": "SAP S/4HANA迁移高峰期和政府数字化项目使ERP顾问处于极度紧缺状态，Seek常年有120~220个活跃职位，实际需求通过猎头和合同渠道更大。"},
]
MARKDOWN = """# ERP顾问（ERP Consultant）职业分析 · 澳大利亚

**职业代码：261111 – ERP Consultant。**

ERP顾问是澳洲企业数字化转型核心专业，SAP/Oracle迁移高峰期叠加云化需求，使该职业成为IT行业薪资最高的细分方向之一。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $75,000~$100,000 |
| 中级（3-8年） | $105,000~$155,000 |
| 高级（8年+） | $160,000~$250,000 |

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
    print("[OK] ERP顾问入库完成")
if __name__ == "__main__": run()
