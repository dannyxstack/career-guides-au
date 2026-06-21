"""Toolmaker (323211) 模具制造工 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "323211", "anzsco_title": "Toolmaker",
    "category": "技工", "workforce_size": 8000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Defence Manufacturing","Aerospace Precision Parts","Medical Device Manufacturing","Automotive Aftermarket"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "模具制造工",
    "summary": "模具制造工（Toolmaker）专门制造和维修金属模具、夹具和精密工装，是制造业最高技能技工之一。在澳洲高精密制造、国防零部件和医疗器械领域持续短缺。",
    "forecast_note": "澳洲本地精密制造业虽规模较小，但高价值零部件（航空/国防/医疗）保持稳定需求。AUKUS潜艇计划将带动SA/VIC精密制造扩张。",
    "trend_summary": "CNC辅助加工普及，但模具设计和精密配合能力仍是核心竞争力。年龄结构老化，熟练模具工日趋稀缺。"}
I18N_EN = {"locale": "en", "name": "Toolmaker",
    "summary": "Toolmakers produce and maintain metal dies, jigs, fixtures and precision tooling. Classified ANZSCO 323211, they are among the most skilled trade workers. Persistent shortage in defence, aerospace and medical device manufacturing.",
    "forecast_note": "High-value precision manufacturing (aerospace/defence/medical) maintains stable demand. AUKUS submarine project will expand SA/VIC precision manufacturing.",
    "trend_summary": "CNC-assisted machining is widespread, but die design and precision-fit skill remains core. Ageing workforce makes experienced toolmakers increasingly scarce."}
EDUCATION = [
    {"stage": "Certificate III in Engineering (Toolmaking Trade)", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州TAFE差异", "sort_order": 0},
    {"stage": "海外资质TRA互认", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 1},
    {"stage": "CAD/CAM进阶培训（Mastercam/CATIA）", "duration": "3~6个月", "cost_min": 1000, "cost_max": 3000, "cost_note": "可选；提升竞争力", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Engineering (Toolmaking Trade)", "issuer": "TAFE/RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 100, "count_max": 250, "note": "全国，VIC/NSW集中"},
    {"platform": "Indeed", "count_min": 60, "count_max": 150, "note": "精密加工和模具设计"},
    {"platform": "LinkedIn", "count_min": 30, "count_max": 80, "note": "国防/航空方向"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 30000, "salary_max": 60000, "salary_note": "Metal Industry Award", "sort_order": 0},
    {"experience": "初级模具工（1~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "制造业平均", "sort_order": 1},
    {"experience": "中级模具工（3~8年）", "salary_min": 90000, "salary_max": 120000, "salary_note": "精密加工；Seek均值约$45~$58/hr", "sort_order": 2},
    {"experience": "高级/专家（8年+）", "salary_min": 110000, "salary_max": 140000, "salary_note": "航空/国防合同工更高", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "VIC/SA优先制造业", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "高",   "stars": 4, "note": "精密公差、模具设计技能要求高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA"},
    {"dimension": "job_demand",               "label_zh": "中高", "stars": 4, "note": "规模较小但持续短缺，岗位精准"},
    {"dimension": "competition",              "label_zh": "低",   "stars": 2, "note": "熟练模具工稀缺，雇主求贤若渴"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "精密车间工作，强度适中"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中级 $90k~$120k，专家可达 $140k+"},
    {"dimension": "future_prospect",          "label_zh": "较好", "stars": 4, "note": "AUKUS + 医疗器械制造新机会"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "CNC自动化已介入，但模具设计判断难以替代"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列，VIC/SA制造业提名"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有精密加工或CNC操作经验，希望移民制造业大州（VIC/SA）",
    "擅长金属精密加工，追求高技能职业发展通道",
]
SUITABILITY_UNFIT = [
    "无制造/机械背景，缺乏精密加工基础",
    "不接受车间环境",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 323211 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Toolmaker 薪资及岗位量", "url": "https://www.seek.com.au/toolmaker-jobs"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲模具工工资多少？", "answer": "中级模具工年薪约 $90,000~$120,000（$45~$58/hr）。高级/专家可达 $140,000+，国防/航空合同工更高。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲模具工好找工作吗？", "answer": "较容易。精密制造规模不大，但持证模具工极度稀缺，岗位竞争少。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国模具经验澳洲认可吗？", "answer": "需TRA技能评估，提交作业样本和工作证明，通过率较高。"},
]
MARKDOWN = """# 模具制造工（Toolmaker）职业分析 · 澳大利亚

**职业代码：323211 – Toolmaker。**

模具制造工专门制造和维修金属模具、精密夹具和工装，是澳洲最高技能技工之一。在航空、国防精密零件和医疗器械领域持续短缺，年龄结构老化使熟练模具工日益稀缺。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 学徒（0~4年） | $30,000~$60,000 |
| 初级（1~3年） | $70,000~$90,000 |
| 中级（3~8年） | $90,000~$120,000 |
| 高级/专家 | $110,000~$140,000+ |

---

## 2. 谁适合做模具工？

- 有精密加工或CNC操作经验，希望移民VIC/SA制造业大州
- 擅长金属精密加工，追求高技能职业通道

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
    print("[OK] 模具制造工（Toolmaker）入库+Markdown完成")
if __name__ == "__main__": run()
