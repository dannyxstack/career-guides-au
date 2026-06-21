"""CNC Machinist (323214) 数控机床操作工 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "323214", "anzsco_title": "Precision Metal Trades Worker",
    "category": "技工", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Defence Manufacturing","Aerospace Machining","Medical Device Precision Parts","Mining Equipment Repair"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "数控机床操作工",
    "summary": "数控机床操作工（CNC Machinist）操作和编程CNC车床、铣床等精密机床，生产金属零部件，是制造业核心技工。澳洲持证CNC操作工持续短缺，尤其集中在国防、航空和矿业设备维修领域。",
    "forecast_note": "AUKUS国防制造和航空维修MRO业务扩展将提升CNC需求。矿业设备大修期间对高级CNC操作工需求激增。",
    "trend_summary": "CNC技术持续升级（5轴加工中心），会CAD/CAM编程的操作工薪资溢价明显。自动化装卸辅助提升效率，但编程判断仍需人工。"}
I18N_EN = {"locale": "en", "name": "CNC Machinist",
    "summary": "CNC machinists operate and program CNC lathes, milling machines and machining centres to produce precision metal components. Persistent shortage under ANZSCO 323214, concentrated in defence, aerospace and mining equipment repair.",
    "forecast_note": "AUKUS defence manufacturing and aviation MRO expansion will increase CNC demand. Mining equipment overhaul periods create surge demand for experienced CNC operators.",
    "trend_summary": "CNC technology advances (5-axis machining centres) with premium pay for CAD/CAM programmers. Automation assists loading/unloading, but programming judgment remains human-dependent."}
EDUCATION = [
    {"stage": "Certificate III in Engineering (Machining Trade)", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州TAFE", "sort_order": 0},
    {"stage": "Certificate IV in Engineering (Advanced)", "duration": "12个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "CAD/CAM编程进阶", "sort_order": 1},
    {"stage": "海外资质TRA互认", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Engineering (Machining Trade)", "issuer": "TAFE/RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 500, "note": "全国，VIC/NSW/WA集中"},
    {"platform": "Indeed", "count_min": 100, "count_max": 280, "note": "含矿业和航空方向"},
    {"platform": "LinkedIn", "count_min": 50, "count_max": 130, "note": "国防/航空方向"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 30000, "salary_max": 60000, "salary_note": "Metal Industry Award", "sort_order": 0},
    {"experience": "初级CNC操作工（1~3年）", "salary_min": 70000, "salary_max": 88000, "salary_note": "制造业基础", "sort_order": 1},
    {"experience": "中级（3~8年）", "salary_min": 88000, "salary_max": 115000, "salary_note": "含CAD/CAM编程能力", "sort_order": 2},
    {"experience": "高级/编程工程师（8年+）", "salary_min": 110000, "salary_max": 140000, "salary_note": "5轴+国防合同工", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "VIC/SA制造业州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "CNC编程+精密公差"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "制造业核心技工，持续短缺"},
    {"dimension": "competition",              "label_zh": "低",   "stars": 2, "note": "持证CNC操作工稀缺"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "车间工作，精神专注度高"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中级 $88k~$115k"},
    {"dimension": "future_prospect",          "label_zh": "较好", "stars": 4, "note": "AUKUS+航空MRO拉动"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "自动化装卸发展，但编程判断难以替代"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有CNC操作或编程经验，希望移民VIC/NSW/SA",
    "精密加工背景，愿意在国防或航空制造发展",
]
SUITABILITY_UNFIT = [
    "无机械加工背景",
    "不接受车间精密工作环境",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 323214 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "CNC Machinist 薪资及岗位量", "url": "https://www.seek.com.au/cnc-machinist-jobs"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲CNC操作工工资多少？", "answer": "中级CNC操作工年薪约 $88,000~$115,000。有CAD/CAM编程能力者或国防合同工可达 $140,000+。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲CNC操作工容易找工作吗？", "answer": "容易。持证CNC操作工全国短缺，Seek挂牌200~500个职位，VIC/NSW/WA最多。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国CNC经验澳洲认可吗？", "answer": "需TRA技能评估（12~18个月），提交机床操作记录和图纸样本，通过率较高。"},
]
MARKDOWN = """# 数控机床操作工（CNC Machinist）职业分析 · 澳大利亚

**职业代码：323214 – Precision Metal Trades Worker（CNC Machinist）。**

数控机床操作工操作CNC车铣床生产精密金属零部件，是澳洲制造业短缺核心技工。AUKUS国防制造和航空MRO扩展将持续拉动需求。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 学徒（0~4年） | $30,000~$60,000 |
| 初级（1~3年） | $70,000~$88,000 |
| 中级（3~8年） | $88,000~$115,000 |
| 高级/编程工程师 | $110,000~$140,000+ |

---

*数据来源：JSA、Seek AU、TRA（2025-2026）*
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
    print("[OK] 数控机床操作工（CNC Machinist）入库+Markdown完成")
if __name__ == "__main__": run()
