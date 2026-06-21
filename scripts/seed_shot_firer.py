"""Shot Firer / Blaster (712611) 爆破工 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "712611", "anzsco_title": "Shot Firer",
    "category": "采矿", "workforce_size": 5000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Mining Blast Operations","Quarrying & Civil Blasting","Tunnel Blasting (Infrastructure)","Critical Minerals New Mines"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "爆破工",
    "summary": "爆破工（Shot Firer/Blaster）持有爆破许可证，在矿山、采石场和隧道工程中执行钻孔爆破作业。澳洲爆破执照是严格监管的专业资质，持证爆破工极度稀缺，FIFO薪资在技工中排名最高之一。",
    "forecast_note": "新矿山开发（关键矿产）和基础设施隧道（城市轨道/公路）双线驱动爆破工需求增长。现有执照持有者年龄偏大，退休缺口扩大。",
    "trend_summary": "电子爆破系统（EBS）逐步取代传统导爆索，要求爆破工持续更新技能。爆破工是澳洲薪资最高的技工之一，因执照门槛高而严重短缺。"}
I18N_EN = {"locale": "en", "name": "Shot Firer",
    "summary": "Shot firers hold explosive work licences and carry out drilling and blasting operations in mines, quarries and tunnel construction. Australian blasting licences are strictly regulated; licensed shot firers are extremely scarce, with FIFO pay ranking among the highest of all trade workers.",
    "forecast_note": "New mine development (critical minerals) and infrastructure tunnelling (urban rail/road) driving dual-lane growth in shot firer demand. Existing licence holder population is ageing, widening retirement gap.",
    "trend_summary": "Electronic blasting systems (EBS) gradually replacing traditional detonating cord, requiring continuous skills updates. Shot firers are among Australia's highest-paid trade workers due to high licence barriers and severe scarcity."}
EDUCATION = [
    {"stage": "Certificate III in Extractive Technologies (Blasting)", "duration": "12~18个月", "cost_min": 3000, "cost_max": 8000, "cost_note": "含爆破执照考试费", "sort_order": 0},
    {"stage": "各州爆破工执照（Shotfirer Licence）", "duration": "已含在培训中", "cost_min": 500, "cost_max": 2000, "cost_note": "各州矿监/安监局颁发", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "State Shotfirer/Blaster Licence", "issuer": "各州矿监/爆炸物监管机构", "note": "法规强制，无证不得操作", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Certificate III in Extractive Technologies", "issuer": "RTO", "note": "核心资质", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "EBS Electronic Blasting Certification", "issuer": "Orica/Dyno Nobel认可机构", "note": "现代矿山必备", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 100, "count_max": 250, "note": "全国，WA/QLD/NSW集中"},
    {"platform": "Indeed", "count_min": 50, "count_max": 130, "note": "矿山爆破专职"},
    {"platform": "LinkedIn", "count_min": 30, "count_max": 80, "note": "Orica/Dyno Nobel等爆破服务公司"},
]
SALARIES = [
    {"experience": "初级爆破工（0~2年）", "salary_min": 100000, "salary_max": 130000, "salary_note": "持证即高薪，无初级之分", "sort_order": 0},
    {"experience": "中级（2~6年）FIFO", "salary_min": 130000, "salary_max": 180000, "salary_note": "矿山FIFO均值", "sort_order": 1},
    {"experience": "高级/首席爆破工（6年+）", "salary_min": 170000, "salary_max": 250000, "salary_note": "大型矿山或承包商", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "矿业雇主担保", "sort_order": 0},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 1},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "高",   "stars": 4, "note": "爆炸物技术+安全法规+精确计算"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "12~18个月培训"},
    {"dimension": "certification_difficulty", "label_zh": "高",   "stars": 4, "note": "州级爆破执照门槛高，考试严格"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "执照持有者严重不足"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "持证爆破工是澳洲最稀缺职业之一"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "高危环境，精神高度集中"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级FIFO $130k~$180k；高级$250k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "新矿山+基础设施隧道双线需求"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "爆炸物操作需持证人员，法规不允许无人化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "执照认可需额外评估，但需求大"},
]
SUITABILITY_FIT = [
    "有采矿背景，愿意进阶高薪爆破专业资质",
    "接受FIFO高危工作环境，追求矿业最高薪水平",
]
SUITABILITY_UNFIT = [
    "不接受高危工作环境和爆炸物操作",
    "不愿承担严格安全法规责任",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 712611 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Shot Firer 薪资及岗位量", "url": "https://www.seek.com.au/shot-firer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲爆破工工资多少？", "answer": "持证后即高薪，中级FIFO年薪约 $130,000~$180,000。高级/首席爆破工可达 $250,000+，是澳洲薪资最高的技工之一。"},
    {"faq_type": "demand", "sort_order": 1, "question": "爆破工容易找工作吗？", "answer": "极容易。持证爆破工是澳洲最稀缺职业之一，Orica/Dyno Nobel等公司常年大量招聘。"},
]
MARKDOWN = """# 爆破工（Shot Firer）职业分析 · 澳大利亚

**职业代码：712611 – Shot Firer。**

爆破工是澳洲薪资最高、最稀缺的技工之一。持有州级爆破执照方可操作，门槛高但收入极丰厚。新矿山开发和基础设施隧道工程双线驱动需求。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级持证（0~2年） | $100,000~$130,000 |
| 中级 FIFO（2~6年） | $130,000~$180,000 |
| 高级/首席 | $170,000~$250,000+ |

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
    print("[OK] 爆破工入库完成")
if __name__ == "__main__": run()
