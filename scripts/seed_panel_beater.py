"""Panel Beater (324111) 汽车钣金工 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "324111", "anzsco_title": "Panel Beater",
    "category": "技工", "workforce_size": 20000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Insurance Repair (AAMI/NRMA)","EV Body Repair","Fleet Vehicle Maintenance","Accident Repair Centres"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "汽车钣金工",
    "summary": "汽车钣金工（Panel Beater）修复车辆碰撞损伤，包括矫正车身、更换面板和修补结构件。澳洲车辆保险维修市场庞大，加上近年极端天气（冰雹）引发大规模理赔，汽车钣金工需求持续高位。CSOL短缺职业。",
    "forecast_note": "澳洲冰雹事件（2024-2025）导致大量车辆损毁，保险维修积压严重，钣金工需求暴增。EV电动车高压系统钣金维修需要额外安全培训，技能溢价上升。",
    "trend_summary": "车身铝合金化趋势对钣金工技能提出新要求（不同于传统钢板修复）。独立小型碰撞维修店到大型连锁（如Repco Authorised）均持续招聘。"}
I18N_EN = {"locale": "en", "name": "Panel Beater",
    "summary": "Panel beaters repair collision-damaged vehicle bodywork, including straightening panels, replacing components and restoring structural integrity. Australia has a large insurance repair market, and extreme weather events (hailstorms) create sustained demand. Listed as CSOL shortage occupation.",
    "forecast_note": "Major Australian hailstorm events (2024-2025) created massive insurance repair backlogs, significantly boosting panel beater demand. EV high-voltage system body repair requires additional safety training, increasing skill premium.",
    "trend_summary": "Vehicle aluminium body adoption requires new skills (different from traditional steel repair). Both independent collision repairers and large chains (e.g., Repco Authorised) continuously recruit."}
EDUCATION = [
    {"stage": "Certificate III in Automotive Body Repair Technology", "duration": "36~48个月（学徒）", "cost_min": 0, "cost_max": 2500, "cost_note": "各州TAFE；工具费约$1,500", "sort_order": 0},
    {"stage": "EV High Voltage Safety Training", "duration": "1~2天", "cost_min": 300, "cost_max": 800, "cost_note": "电动车钣金维修额外要求", "sort_order": 1},
    {"stage": "海外资质TRA互认", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Automotive Body Repair Technology", "issuer": "TAFE/RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 700, "note": "全国各州均有，城市集中"},
    {"platform": "Indeed", "count_min": 150, "count_max": 350, "note": "保险维修中心"},
    {"platform": "LinkedIn", "count_min": 50, "count_max": 150, "note": "大型连锁维修集团"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 25000, "salary_max": 55000, "salary_note": "Motor Vehicle Repair Award", "sort_order": 0},
    {"experience": "初级钣金工（1~3年）", "salary_min": 65000, "salary_max": 80000, "salary_note": "独立店铺", "sort_order": 1},
    {"experience": "中级钣金工（3~8年）", "salary_min": 80000, "salary_max": 100000, "salary_note": "Seek均值约$38~$48/hr（2026）", "sort_order": 2},
    {"experience": "高级/承包工（8年+）", "salary_min": 100000, "salary_max": 130000, "salary_note": "冰雹季承包商日薪极高", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "车身修复工艺和测量技能"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学徒3~4年"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Certificate III + TRA"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "保险维修稳定，冰雹事件额外暴增"},
    {"dimension": "competition",              "label_zh": "低",   "stars": 2, "note": "CSOL短缺，技工缺口大"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "车间工作，体力适中"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中级 $80k~$100k；承包工季节性更高"},
    {"dimension": "future_prospect",          "label_zh": "较好", "stars": 4, "note": "EV维修新技能溢价，保险维修稳定"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "车身修复手工艺难以自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有汽车钣金或车身修复经验，目标技能移民澳洲",
    "接受车间工作环境，擅长手工精细操作",
]
SUITABILITY_UNFIT = [
    "无汽车维修背景",
    "期望高薪办公室工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 324111 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Panel Beater 薪资及岗位量（2026）", "url": "https://www.seek.com.au/panel-beater-jobs"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲钣金工工资多少？", "answer": "中级钣金工年薪约 $80,000~$100,000（$38~$48/hr）。冰雹季承包商收入可大幅超出。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲钣金工需求量大吗？", "answer": "需求旺盛。保险维修市场稳定，近年极端冰雹事件额外拉动大量需求，CSOL持续短缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内汽车钣金经验澳洲认可吗？", "answer": "需TRA技能评估（12~18个月），提交车身修复工作记录和照片，通过率较高。"},
]
MARKDOWN = """# 汽车钣金工（Panel Beater）职业分析 · 澳大利亚

**职业代码：324111 – Panel Beater。**

汽车钣金工修复车辆碰撞损伤，澳洲保险维修市场庞大，冰雹季额外带来大量维修需求。CSOL短缺职业，EV电动车新技能溢价上升。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 学徒（0~4年） | $25,000~$55,000 |
| 初级（1~3年） | $65,000~$80,000 |
| 中级（3~8年） | $80,000~$100,000 |
| 高级/承包工 | $100,000~$130,000+ |

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
    print("[OK] 汽车钣金工（Panel Beater）入库+Markdown完成")
if __name__ == "__main__": run()
