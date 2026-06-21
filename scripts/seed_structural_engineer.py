"""Structural Engineer (233214) 结构工程师 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "233214", "anzsco_title": "Structural Engineer",
    "category": "工程", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Infrastructure Megaprojects","High-Rise Residential & Commercial","Defence Facilities","Renewable Energy Structures"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "结构工程师",
    "summary": "结构工程师（Structural Engineer）设计和分析建筑物、桥梁、基础设施的承重结构，是工程行业最核心的专业之一。澳洲基础设施大投入和住宅建设潮持续拉动需求，持证结构工程师（MIEAust / RPEQ）收入极高。",
    "forecast_note": "联邦和各州基础设施投资（轨道交通/医院/学校）总额超$2,000亿，结构工程师需求2025-2030年持续旺盛。全球气候适应性建筑（抗风/抗震/抗洪）新兴领域推动专业结构需求。",
    "trend_summary": "BIM（Revit/Tekla）普及和AI辅助结构分析提升效率，但工程判断和签章责任仍需持证工程师。RPEQ/CPEng是最重要的执业资质。"}
I18N_EN = {"locale": "en", "name": "Structural Engineer",
    "summary": "Structural engineers design and analyse load-bearing structures for buildings, bridges and infrastructure. One of the most core engineering specialisations. Australia's sustained infrastructure investment and residential construction demand persistently high. Licensed structural engineers (MIEAust/RPEQ) earn very high incomes.",
    "forecast_note": "Federal and state infrastructure investment ($200B+ in rail/hospitals/schools) sustaining strong structural engineer demand 2025-2030. Climate-adaptive building (wind/seismic/flood) emerging as new specialist area.",
    "trend_summary": "BIM (Revit/Tekla) adoption and AI-assisted structural analysis improving efficiency, but engineering judgement and certification responsibility still requires licensed engineers. RPEQ/CPEng are most important practising credentials."}
EDUCATION = [
    {"stage": "Bachelor of Civil / Structural Engineering", "duration": "4年", "cost_min": 30000, "cost_max": 55000, "cost_note": "国际留学生约$150k~$200k总费", "sort_order": 0},
    {"stage": "Engineers Australia Competency Assessment", "duration": "2~5年工作经验积累", "cost_min": 500, "cost_max": 2000, "cost_note": "MIEAust/CPEng申请", "sort_order": 1},
    {"stage": "RPEQ Registration (QLD) or equivalent", "duration": "根据州不同", "cost_min": 500, "cost_max": 2000, "cost_note": "独立签章必备", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Civil/Structural Engineering", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "MIEAust / CPEng", "issuer": "Engineers Australia", "note": "专业会员/执业工程师", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "RPEQ / REC (State Registration)", "issuer": "各州工程师委员会", "note": "独立签章执业", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 500, "count_max": 1200, "note": "全国，NSW/VIC/QLD集中"},
    {"platform": "Indeed", "count_min": 250, "count_max": 600, "note": "咨询公司和设计院"},
    {"platform": "LinkedIn", "count_min": 200, "count_max": 500, "note": "大型工程咨询（AECOM/WSP/Arup）"},
]
SALARIES = [
    {"experience": "初级结构工程师（0~3年）", "salary_min": 75000, "salary_max": 100000, "salary_note": "Graduate Engineer Award", "sort_order": 0},
    {"experience": "中级（3~8年）", "salary_min": 100000, "salary_max": 140000, "salary_note": "Seek均值约$50~$68/hr（2026）", "sort_order": 1},
    {"experience": "高级/Associate（8年+）", "salary_min": 140000, "salary_max": 200000, "salary_note": "大型咨询公司高级职级", "sort_order": 2},
    {"experience": "Principal/Director", "salary_min": 190000, "salary_max": 280000, "salary_note": "合伙人级别", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "积分制，Engineers Australia评估", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "高",   "stars": 4, "note": "结构分析+材料+规范+BIM"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学士4年+3~5年成为独立工程师"},
    {"dimension": "certification_difficulty", "label_zh": "高",   "stars": 4, "note": "CPEng/RPEQ需丰富项目经验"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "$2,000亿基础设施投资驱动"},
    {"dimension": "competition",              "label_zh": "低",   "stars": 2, "note": "持证结构工程师短缺"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "项目截止前高峰，整体可控"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级 $100k~$140k；高级$200k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "基础设施+气候适应双线驱动"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助分析，但签章责任不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，189/190均可"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "Engineers Australia评估+英语"},
]
SUITABILITY_FIT = [
    "有土木或结构工程学位，目标澳洲工程咨询或基础设施项目",
    "BIM技能（Revit/Tekla）+持续学习意愿",
]
SUITABILITY_UNFIT = [
    "无工程学历背景",
    "不喜欢计算和技术细节工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 233214 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Engineers Australia", "content": "CPEng/MIEAust资质", "url": "https://www.engineersaustralia.org.au/"},
    {"source_name": "Seek AU", "content": "Structural Engineer 薪资及岗位量", "url": "https://www.seek.com.au/structural-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲结构工程师工资多少？", "answer": "中级结构工程师年薪约 $100,000~$140,000。高级/Associate可达 $140,000~$200,000，Principal/Director $280,000+。"},
    {"faq_type": "recognition", "sort_order": 1, "question": "中国土木工程学历澳洲认可吗？", "answer": "需通过Engineers Australia学历评估（6~12个月）。评估通过后可积累工作经验申请MIEAust/CPEng资质。"},
    {"faq_type": "demand", "sort_order": 2, "question": "澳洲结构工程师好找工作吗？", "answer": "容易。$2,000亿基础设施投资使结构工程师持续短缺，AECOM/WSP/Arup等大公司常年招聘。"},
]
MARKDOWN = """# 结构工程师（Structural Engineer）职业分析 · 澳大利亚

**职业代码：233214 – Structural Engineer。**

结构工程师设计和分析建筑与基础设施的承重结构，是澳洲薪资最高的工程专业之一。$2,000亿基础设施投资使需求持续旺盛，RPEQ/CPEng持证工程师极度抢手。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0~3年） | $75,000~$100,000 |
| 中级（3~8年） | $100,000~$140,000 |
| 高级/Associate | $140,000~$200,000 |
| Principal/Director | $190,000~$280,000+ |

---

*数据来源：JSA、Engineers Australia、Seek AU（2025-2026）*
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
    print("[OK] 结构工程师入库完成")
if __name__ == "__main__": run()
