"""老年护理工 (423111) Aged Care Worker — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "423111", "anzsco_title": "Aged Care Worker",
    "category": "医疗", "workforce_size": 180000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Home Care Packages","Dementia Care","Palliative Care Support","Residential Aged Care"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "老年护理工",
    "summary": "老年护理工为老年人提供日常生活照料、个人护理和社交支持，是澳洲规模最大的紧缺医疗职业之一。澳洲人口老龄化加速，老年护理行业2025-2030年需新增超20万名护理工，持Certificate III资质即可入行。",
    "forecast_note": "澳洲65岁以上人口2030年预计达500万，老年护理缺口将达30万人。政府大幅提高老年护理工资（2023年起加薪15%），在家护理（Home Care）方向增长最快。",
    "trend_summary": "个人护理计划和痴呆症护理专业培训成为行业标准，居家护理模式快速扩张。双语护理工在华人社区需求旺盛，是移民进入澳洲医疗系统最便捷的路径。"}
I18N_EN = {"locale": "en", "name": "Aged Care Worker",
    "summary": "Aged care workers provide daily living assistance, personal care and social support to elderly people; this is one of Australia's largest shortage occupations. Accelerating population ageing requires 200,000+ new care workers 2025-2030; Certificate III is the entry requirement.",
    "forecast_note": "Australia's 65+ population is projected to reach 5 million by 2030, creating a shortage of 300,000+ care workers. The government's 15% wage increase from 2023 is attracting more entrants; home care is the fastest-growing sector.",
    "trend_summary": "Person-centred care and dementia care specialisation are becoming industry standards. Home care is rapidly expanding; bilingual workers are in high demand in Chinese-speaking communities."}
EDUCATION = [
    {"stage": "Certificate III in Individual Support (Ageing)", "duration": "6~12个月", "cost_min": 2000, "cost_max": 8000, "cost_note": "TAFE或RTO，政府补贴可用", "sort_order": 0},
    {"stage": "First Aid Certificate HLTAID011", "duration": "1天", "cost_min": 100, "cost_max": 250, "cost_note": "入行必备", "sort_order": 1},
    {"stage": "Certificate IV in Ageing Support", "duration": "12个月", "cost_min": 3000, "cost_max": 8000, "cost_note": "晋升团队领导", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Individual Support", "issuer": "TAFE / RTO", "note": "入行基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "HLTAID011 First Aid", "issuer": "认可培训机构", "note": "急救证书", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "NDIS Worker Screening Check", "issuer": "各州政府", "note": "从事NDIS服务必备", "is_mandatory": 1, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 1500, "count_max": 3000, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 1000, "count_max": 2000, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 800, "count_max": 1500, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-2年）", "salary_min": 50000, "salary_max": 62000, "salary_note": "Entry Level Care Worker", "sort_order": 0},
    {"experience": "中级（2-6年）", "salary_min": 63000, "salary_max": 76000, "salary_note": "Personal Care Worker", "sort_order": 1},
    {"experience": "高级（6年+）", "salary_min": 78000, "salary_max": 95000, "salary_note": "Senior Care / Team Leader", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，医疗紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "实践技能为主"},
    {"dimension": "learning_duration",        "label_zh": "极短", "stars": 1, "note": "6~12个月可入行"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 1, "note": "Cert III入门友好"},
    {"dimension": "job_demand",               "label_zh": "极旺", "stars": 5, "note": "澳洲岗位量最大职业之一"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "严重供不应求"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 4, "note": "含轮班、夜班和体力劳动"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 2, "note": "AUD 5万~9.5万"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "人口老龄化长期驱动"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "人际关怀不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "医疗类移民最易获批职业"},
    {"dimension": "pr_difficulty",            "label_zh": "极易", "stars": 1, "note": "Cert III即可申请"},
]
SUITABILITY_FIT = ["有爱心和耐心、喜欢照顾老人者", "希望快速入行澳洲医疗系统者", "具备中文双语能力服务华人老人群体者"]
SUITABILITY_UNFIT = ["不能承受体力劳动和轮班工作者", "以高薪为首要目标者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 423111 老年护理工数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/aged-care-worker-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "老年护理工在澳洲薪资如何？", "answer": "初级约AUD 5万~6.2万，中级6.3万~7.6万，高级/团队领导7.8万~9.5万，2023年政府加薪15%后薪资有所改善。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲老年护理好找工作吗？", "answer": "是澳洲最易找工作的职业之一，Seek常年有1,500~3,000个活跃职位，几乎所有州都严重缺人，持Cert III即可就业。"},
]
MARKDOWN = """# 老年护理工（Aged Care Worker）职业分析 · 澳大利亚

**职业代码：423111 – Aged Care Worker。**

老年护理工是澳洲需求量最大的紧缺职业，入行门槛低，人口老龄化趋势确保长期就业稳定性，是快速进入澳洲医疗系统的重要通道。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-2年） | $50,000~$62,000 |
| 中级（2-6年） | $63,000~$76,000 |
| 高级（6年+） | $78,000~$95,000 |

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
    print("[OK] 老年护理工入库完成")
if __name__ == "__main__": run()
