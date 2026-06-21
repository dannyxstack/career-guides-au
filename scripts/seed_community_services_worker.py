"""社区服务工作者 (411215) Community Services Worker — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "411215", "anzsco_title": "Community Services Worker",
    "category": "社区服务", "workforce_size": 35000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Australia Wide Growth","Regional Demand","Digital Transformation","Ageing Population"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "社区服务工作者",
    "summary": "社区服务工作者是澳洲社区服务行业的重要职业，需求稳定，具备相关资质即可入行。澳洲社区服务行业持续扩张，为专业人员提供良好的职业发展机会。",
    "forecast_note": "2025-2030年澳洲社区服务行业持续扩张，社区服务工作者需求保持稳定增长，具备相关认证和经验者就业前景良好。",
    "trend_summary": "数字化技术和专业认证要求持续提升，社区服务工作者须不断更新专业技能以适应行业变化。"}
I18N_EN = {"locale": "en", "name": "Community Services Worker",
    "summary": "Community Services Worker is an important role in Australia's 社区服务 sector with stable demand. The sector continues to expand, offering good career development opportunities for qualified professionals.",
    "forecast_note": "The Australian 社区服务 sector will continue to expand 2025-2030; demand for Community Services Workers is expected to grow steadily for those with relevant certifications and experience.",
    "trend_summary": "Digitalisation and rising professional certification requirements mean Community Services Workers must continuously update their skills to keep pace with industry changes."}
EDUCATION = [
    {"stage": "Relevant degree or certificate qualification", "duration": "1~4年", "cost_min": 5000, "cost_max": 50000, "cost_note": "视具体课程而定", "sort_order": 0},
    {"stage": "Industry registration or licensing", "duration": "视情况", "cost_min": 200, "cost_max": 2000, "cost_note": "行业注册费", "sort_order": 1},
]
QUALIFICATIONS = [
    {"qual_name": "Relevant qualification for Community Services Worker", "issuer": "认可机构", "note": "入行基础", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Professional membership / registration", "issuer": "行业协会", "note": "专业会员", "is_mandatory": 0, "sort_order": 1},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 100, "count_max": 300, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 60, "count_max": 180, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 80, "count_max": 220, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 58000, "salary_max": 78000, "salary_note": "Entry Level", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 80000, "salary_max": 110000, "salary_note": "Experienced", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 112000, "salary_max": 150000, "salary_note": "Senior / Specialist", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需专业培训"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "1~4年培训"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "行业认证可考取"},
    {"dimension": "job_demand",               "label_zh": "稳定", "stars": 3, "note": "需求稳定增长"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "适度竞争"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "常规工作强度"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "AUD 8万~15万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 3, "note": "行业持续发展"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "部分技能可被辅助"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "移民通道可行"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需积累经验"},
]
SUITABILITY_FIT = ["对社区服务行业有热情者", "希望在澳洲稳定就业者", "具备相关学历背景者"]
SUITABILITY_UNFIT = ["不了解澳洲社区服务行业规范者", "不愿持续学习更新技能者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 411215 社区服务工作者数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "社区服务工作者在澳洲薪资如何？", "answer": "初级约AUD 5.8万~7.8万，中级8万~11万，高级/专科11.2万~15万，具体因城市和雇主而异。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲社区服务工作者好找工作吗？", "answer": "需求稳定，全澳各地均有职位，具备相关认证和经验者就业前景良好。"},
]
MARKDOWN = """# 社区服务工作者（Community Services Worker）职业分析 · 澳大利亚

**职业代码：411215 – Community Services Worker。**

社区服务工作者是澳洲社区服务行业的重要职业，需求稳定，具备专业资质后职业发展空间广阔。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $58,000~$78,000 |
| 中级（3-8年） | $80,000~$110,000 |
| 高级（8年+） | $112,000~$150,000 |

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
    print("[OK] 社区服务工作者入库完成")
if __name__ == "__main__": run()
