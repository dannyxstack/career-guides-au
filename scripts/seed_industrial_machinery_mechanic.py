"""Industrial Machinery Mechanic (323312) 工业设备维修工 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "323312", "anzsco_title": "Industrial Machinery Mechanic",
    "category": "技工", "workforce_size": 22000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Mining Plant Maintenance","Food Processing Equipment","Automated Manufacturing Lines","Wind Turbine Mechanical"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "工业机械维修工",
    "summary": "工业机械维修工（Industrial Machinery Mechanic）维护和修理工厂、矿山和工业设施中的机械设备，包括传动系统、液压设备和自动化生产线。在矿业、食品加工和制造业中需求旺盛，FIFO矿业职位收入极高。",
    "forecast_note": "矿业自动化（自动驾驶设备、遥控采矿）增加了对机械维修工的需求。风力发电机组机械维修新增需求。食品加工和冷链设施扩张带动维修岗位增长。",
    "trend_summary": "PLC/自动化系统技能成为增值加分项。FIFO矿业关停期间机械维修工薪资极高，是进入矿业最快速的技工通道之一。"}
I18N_EN = {"locale": "en", "name": "Industrial Machinery Mechanic",
    "summary": "Industrial machinery mechanics maintain and repair factory, mining and industrial machinery including drive systems, hydraulics and automated production lines. Strong demand in mining, food processing and manufacturing. FIFO mining roles offer very high income.",
    "forecast_note": "Mining automation (autonomous vehicles, remote-controlled mining) increases mechanical maintenance demand. Wind turbine mechanical servicing adds new demand. Food processing and cold chain facility expansion drives maintenance job growth.",
    "trend_summary": "PLC/automation system skills becoming a value-add differentiator. FIFO mining shutdown periods offer extremely high rates, making this one of the fastest pathways into mining from a trade background."}
EDUCATION = [
    {"stage": "Certificate III in Engineering (Mechanical Trade)", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州TAFE", "sort_order": 0},
    {"stage": "PLC/自动化系统进阶培训", "duration": "3~6个月", "cost_min": 1000, "cost_max": 3000, "cost_note": "Siemens/Allen Bradley认证", "sort_order": 1},
    {"stage": "海外资质TRA互认", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Engineering (Mechanical Trade)", "issuer": "TAFE/RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 700, "note": "全国，WA/QLD矿业集中"},
    {"platform": "Indeed", "count_min": 150, "count_max": 400, "note": "含矿业和食品加工"},
    {"platform": "LinkedIn", "count_min": 80, "count_max": 200, "note": "自动化和工业方向"},
]
SALARIES = [
    {"experience": "学徒/初级（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "Metal Industry Award", "sort_order": 0},
    {"experience": "中级机械工（3~8年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "约$41~$55/hr", "sort_order": 1},
    {"experience": "矿业FIFO / 自动化专家（8年+）", "salary_min": 115000, "salary_max": 180000, "salary_note": "WA/QLD FIFO+关停津贴", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "机械原理+液压+PLC"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "矿业+食品加工+自动化全面旺盛"},
    {"dimension": "competition",              "label_zh": "低",   "stars": 2, "note": "持证机械工短缺，矿业尤甚"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "矿业重工业体力，FIFO模式"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "FIFO $115k~$180k；关停合同工更高"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "矿业自动化+风电机组新增需求"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "设备维修现场判断难以自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，偏远区491加分"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有机械维修、液压或工业设备保养经验，目标矿业FIFO",
    "接受WA/QLD偏远矿区FIFO工作方式，追求高薪",
    "有PLC/自动化技能，希望进入高端工业维修方向",
]
SUITABILITY_UNFIT = [
    "不接受FIFO和重工业环境",
    "无机械基础",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 323312 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Industrial Mechanic 薪资及岗位量", "url": "https://www.seek.com.au/industrial-mechanic-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲工业机械维修工工资多少？", "answer": "中级年薪约 $85,000~$115,000。矿业FIFO专家可达 $115,000~$180,000，关停合同工更高。"},
    {"faq_type": "demand", "sort_order": 1, "question": "工业机械工好找工作吗？", "answer": "容易。矿业+食品加工+自动化全面旺盛，Seek挂牌300~700个职位，WA/QLD最多。"},
]
MARKDOWN = """# 工业机械维修工（Industrial Machinery Mechanic）职业分析 · 澳大利亚

**职业代码：323312 – Industrial Machinery Mechanic。**

工业机械维修工维护修理工厂和矿山机械设备，是进入澳洲矿业高薪FIFO职位的主要技工通道之一。矿业自动化和风电机组机械服务进一步扩大需求。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0~3年） | $65,000~$85,000 |
| 中级（3~8年） | $85,000~$115,000 |
| 矿业FIFO/自动化专家 | $115,000~$180,000+ |

---

*数据来源：JSA、Seek AU、Department of Home Affairs（2025-2026）*
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
    print("[OK] 工业机械维修工入库+Markdown完成")
if __name__ == "__main__": run()
