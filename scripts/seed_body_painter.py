"""Motor Vehicle Body Painter (324211) 汽车喷漆工 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "324211", "anzsco_title": "Motor Vehicle Body Painter",
    "category": "技工", "workforce_size": 14000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Insurance Smash Repair","EV Colour Matching","Fleet Resprays","Hail Damage Restoration"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "汽车喷漆工",
    "summary": "汽车喷漆工（Motor Vehicle Body Painter）负责车辆油漆修复、颜色匹配和喷涂，是碰撞修复行业的核心工种。澳洲持证喷漆工持续短缺，尤其在保险维修中心，CSOL在列。",
    "forecast_note": "极端冰雹事件导致大量翻新任务，喷漆工需求与钣金工同步暴增。EV车型特殊漆面（哑光/特效）需要新技能培训。",
    "trend_summary": "水性漆技术转型（VOC法规）对传统油漆技师提出升级要求。高质量喷漆承包商季节性收入极高，尤其在冰雹季节。"}
I18N_EN = {"locale": "en", "name": "Motor Vehicle Body Painter",
    "summary": "Motor vehicle body painters restore vehicle paint finishes, perform colour matching and spray painting as part of collision repair. Persistent shortage of qualified painters in Australia's insurance smash repair industry. Listed on CSOL.",
    "forecast_note": "Extreme hail events creating large volumes of restoration work for painters alongside panel beaters. EV special paint finishes (matte/effect) requiring new skills training.",
    "trend_summary": "Water-based paint technology transition (VOC regulations) requires skills update for traditional painters. High-quality paint contractors earn significantly during hail seasons."}
EDUCATION = [
    {"stage": "Certificate III in Automotive Refinishing Technology", "duration": "36~48个月（学徒）", "cost_min": 0, "cost_max": 2500, "cost_note": "各州TAFE", "sort_order": 0},
    {"stage": "Water-Based Paint Technology Training", "duration": "1~3天", "cost_min": 200, "cost_max": 800, "cost_note": "厂商培训，转型要求", "sort_order": 1},
    {"stage": "海外资质TRA互认", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Automotive Refinishing Technology", "issuer": "TAFE/RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 500, "note": "全国，城市保险维修中心集中"},
    {"platform": "Indeed", "count_min": 100, "count_max": 280, "note": "smash repair中心"},
    {"platform": "LinkedIn", "count_min": 40, "count_max": 120, "note": "连锁维修集团"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 25000, "salary_max": 55000, "salary_note": "Motor Vehicle Repair Award", "sort_order": 0},
    {"experience": "初级喷漆工（1~3年）", "salary_min": 60000, "salary_max": 78000, "salary_note": "独立维修店", "sort_order": 1},
    {"experience": "中级（3~8年）", "salary_min": 78000, "salary_max": 100000, "salary_note": "Seek均值约$37~$47/hr（2026）", "sort_order": 2},
    {"experience": "高级/颜色调配专家（8年+）", "salary_min": 95000, "salary_max": 125000, "salary_note": "高端修复或冰雹承包商", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "颜色调配和喷涂工艺"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学徒3~4年"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Certificate III + TRA"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "保险维修市场稳定，冰雹季额外暴增"},
    {"dimension": "competition",              "label_zh": "低",   "stars": 2, "note": "CSOL短缺，全国缺口持续"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "喷漆环境需佩戴防护设备"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级 $78k~$100k；承包商季节性更高"},
    {"dimension": "future_prospect",          "label_zh": "较好", "stars": 4, "note": "EV特殊漆面技能溢价，稳定需求"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "颜色匹配AI辅助，喷涂工艺仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有汽车喷漆或油漆工艺经验，目标技能移民澳洲",
    "擅长颜色感知和精细手工操作",
]
SUITABILITY_UNFIT = [
    "对油漆化学品和呼吸防护要求有顾虑",
    "无汽车维修或喷漆背景",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 324211 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Body Painter 薪资及岗位量（2026）", "url": "https://www.seek.com.au/automotive-painter-jobs"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲汽车喷漆工工资多少？", "answer": "中级汽车喷漆工年薪约 $78,000~$100,000（$37~$47/hr）。冰雹季承包商收入可大幅超出。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲汽车喷漆工需求大吗？", "answer": "需求稳定且持续增长。保险维修市场庞大，冰雹事件额外拉动需求，CSOL列明短缺。"},
]
MARKDOWN = """# 汽车喷漆工（Motor Vehicle Body Painter）职业分析 · 澳大利亚

**职业代码：324211 – Motor Vehicle Body Painter。**

汽车喷漆工是碰撞修复行业的核心工种，澳洲保险维修市场庞大，冰雹季额外带来大量修复任务。EV特殊漆面技能溢价上升，CSOL持续短缺职业。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 学徒（0~4年） | $25,000~$55,000 |
| 初级（1~3年） | $60,000~$78,000 |
| 中级（3~8年） | $78,000~$100,000 |
| 高级/颜色专家 | $95,000~$125,000+ |

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
    print("[OK] 汽车喷漆工（Body Painter）入库+Markdown完成")
if __name__ == "__main__": run()
