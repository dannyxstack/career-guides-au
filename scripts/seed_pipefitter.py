"""Pipefitter / Mechanical Services Plumber (334115) 管道安装工（工业）— AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "334115", "anzsco_title": "Mechanical Services and Air Conditioning Plumber",
    "category": "技工", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Oil & Gas Process Piping","Mining Plant Piping","Industrial HVAC","LNG Facility Maintenance"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "工业管道安装工",
    "summary": "工业管道安装工（Pipefitter）专门安装、维修工业过程管道和机械服务管道系统，广泛应用于油气、矿业、LNG和工业设施。与住宅水暖工不同，工业管道工处理高压/高温管道，薪资和需求均明显偏高。澳洲WA/QLD油气和矿业FIFO职位持续短缺。",
    "forecast_note": "WA LNG设施维护（North West Shelf、Gorgon等）和QLD矿业管道工持续短缺。氢能和绿色制氢基础设施建设将带来新的管道工需求。",
    "trend_summary": "预制管道模块技术发展，但现场安装和焊接仍不可替代。高级管道焊接（TIG/不锈钢）技能溢价明显，FIFO收入是全澳最高技工之一。"}
I18N_EN = {"locale": "en", "name": "Industrial Pipefitter",
    "summary": "Industrial pipefitters install and maintain high-pressure process piping and mechanical services in oil and gas, mining, LNG and industrial facilities. Different from residential plumbers, they handle high-pressure/temperature systems with significantly higher pay. Persistent FIFO shortages in WA/QLD oil and gas and mining.",
    "forecast_note": "WA LNG facility maintenance and QLD mining pipefitting persistently short-staffed. Green hydrogen infrastructure construction will generate new demand.",
    "trend_summary": "Pre-fabricated pipe modules growing, but on-site installation and welding remain irreplaceable. Advanced pipe welding (TIG/stainless) commands premium pay. FIFO income among the highest in Australian trades."}
EDUCATION = [
    {"stage": "Certificate III in Engineering (Fabrication) or Plumbing", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州差异", "sort_order": 0},
    {"stage": "Pipe Welding Certification (AS 2980 / API 1104)", "duration": "1~3个月", "cost_min": 1000, "cost_max": 3000, "cost_note": "油气/LNG职位必备", "sort_order": 1},
    {"stage": "海外资质TRA互认", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Fabrication or Plumbing", "issuer": "TAFE/RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Pipe Welding Certificate (AS 2980)", "issuer": "WTIA认可机构", "note": "工业管道强烈推荐", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 700, "note": "全国，WA/QLD油气矿业集中"},
    {"platform": "Indeed", "count_min": 150, "count_max": 400, "note": "含FIFO职位"},
    {"platform": "LinkedIn", "count_min": 80, "count_max": 200, "note": "大型工程和LNG方向"},
]
SALARIES = [
    {"experience": "学徒/初级（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "制造业基础", "sort_order": 0},
    {"experience": "中级管道工（3~8年）", "salary_min": 90000, "salary_max": 130000, "salary_note": "约$44~$63/hr", "sort_order": 1},
    {"experience": "矿业FIFO / LNG专家（8年+）", "salary_min": 130000, "salary_max": 200000, "salary_note": "FIFO+关停津贴", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "高压管道安装+焊接规范"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+管道焊接认证"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "WA/QLD油气矿业FIFO岗位持续旺盛"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "工业管道工极度短缺"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "工业现场体力强度大，FIFO模式"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "FIFO $130k~$200k；关停合同工更高"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "绿氢/LNG/矿业长期旺盛"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "现场安装焊接难以自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，偏远区491加分"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有工业管道、焊接或油气经验，目标FIFO高薪职位",
    "接受WA/QLD偏远矿区FIFO工作方式",
    "有管道焊接认证（TIG/不锈钢），追求最高收入",
]
SUITABILITY_UNFIT = [
    "不接受FIFO和工业现场环境",
    "无管道或焊接基础",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 334115 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Pipefitter 薪资及岗位量（2026）", "url": "https://www.seek.com.au/pipefitter-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲工业管道工工资多少？", "answer": "中级工业管道工年薪约 $90,000~$130,000（$44~$63/hr）。矿业FIFO专家可达 $130,000~$200,000，关停合同工更高。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲工业管道工好找工作吗？", "answer": "非常容易。WA/QLD油气矿业FIFO岗位极度短缺，全国Seek挂牌300~700个职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "工业管道工与普通水管工有什么区别？", "answer": "工业管道工专处理高压/高温工业管道（油气/矿业），住宅水管工做供排水系统。工业管道工薪资通常高20~50%。"},
]
MARKDOWN = """# 工业管道安装工（Industrial Pipefitter）职业分析 · 澳大利亚

**职业代码：334115 – Mechanical Services and Air Conditioning Plumber（工业管道工）。**

工业管道安装工专门安装维修高压过程管道系统，在油气、矿业、LNG和工业设施广泛应用。WA/QLD FIFO职位是澳洲收入最高的技工类别之一，持续极度短缺。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0~3年） | $65,000~$85,000 |
| 中级（3~8年） | $90,000~$130,000 |
| 矿业FIFO/LNG专家 | $130,000~$200,000+ |

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
    print("[OK] 工业管道安装工（Pipefitter）入库+Markdown完成")
if __name__ == "__main__": run()
