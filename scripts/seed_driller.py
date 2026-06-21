"""Driller (712212) 钻探操作工 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "712212", "anzsco_title": "Driller",
    "category": "采矿", "workforce_size": 15000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Mineral Exploration (Critical Minerals)","Geotechnical Investigation","Water Well Drilling","Oil & Gas Directional Drilling"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "钻探操作工",
    "summary": "钻探操作工（Driller）操作钻机进行矿产勘探、岩土调查、水井钻探和油气定向钻井。澳洲关键矿产勘探热潮和资源行业扩张，使钻探操作工成为极度短缺职业，尤其是有RC钻/金刚石钻经验者。",
    "forecast_note": "关键矿产（锂/稀土/铜）勘探项目激增，WA和NT矿产勘探投入2025-2026年持续高位。地热能钻探新需求出现。",
    "trend_summary": "定向钻（HDD）技术在城市基础设施管网铺设中快速增长。RC（旋转冲击）和金刚石岩心钻技能是最高薪方向。"}
I18N_EN = {"locale": "en", "name": "Driller",
    "summary": "Drillers operate drilling rigs for mineral exploration, geotechnical investigation, water well drilling and oil and gas directional drilling. Australia's critical minerals exploration boom and resource sector expansion makes drillers extremely scarce, especially those with RC and diamond core drilling experience.",
    "forecast_note": "Critical minerals (lithium/rare earth/copper) exploration projects surging, with WA and NT mineral exploration spend remaining high in 2025-2026. Geothermal energy drilling creating new demand.",
    "trend_summary": "Horizontal directional drilling (HDD) growing rapidly in urban infrastructure. RC (rotary percussion) and diamond core drilling skills are the highest-paid specialisations."}
EDUCATION = [
    {"stage": "Certificate II in Drilling Operations", "duration": "6~12个月", "cost_min": 1500, "cost_max": 4000, "cost_note": "入行基础", "sort_order": 0},
    {"stage": "Certificate III in Drilling Operations", "duration": "12~24个月（在职）", "cost_min": 2000, "cost_max": 5000, "cost_note": "雇主通常赞助", "sort_order": 1},
    {"stage": "RC / Diamond Core Drilling Specialist", "duration": "在职经验积累", "cost_min": 0, "cost_max": 1000, "cost_note": "专业钻探方向", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Drilling Operations", "issuer": "RTO", "note": "核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "HR Truck Licence", "issuer": "各州交通厅", "note": "矿区钻机搬运", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "施工类必备", "is_mandatory": 1, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 700, "note": "全国，WA/NT/QLD集中"},
    {"platform": "Indeed", "count_min": 150, "count_max": 350, "note": "矿产勘探方向"},
    {"platform": "LinkedIn", "count_min": 60, "count_max": 150, "note": "大型勘探公司"},
]
SALARIES = [
    {"experience": "初级钻探工（0~2年）", "salary_min": 75000, "salary_max": 100000, "salary_note": "Drilling Award基础", "sort_order": 0},
    {"experience": "中级（2~6年）", "salary_min": 100000, "salary_max": 140000, "salary_note": "RC/金刚石钻专科", "sort_order": 1},
    {"experience": "高级/首席钻探工（6年+）", "salary_min": 140000, "salary_max": 200000, "salary_note": "FIFO+专业溢价", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "矿业雇主担保", "sort_order": 0},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 1},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "机械操作+地质基础"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "Cert II可6~12个月入行"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Cert II/III+驾照"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "矿产勘探热潮，极度短缺"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "RC/金刚石钻工极度稀缺"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "户外偏远，FIFO模式"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中级FIFO $100k~$140k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "关键矿产勘探热潮长期持续"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "钻机操作和现场判断难以自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，偏远区491"},
    {"dimension": "pr_difficulty",            "label_zh": "较低", "stars": 2, "note": "技能门槛低，入行快"},
]
SUITABILITY_FIT = [
    "接受FIFO和偏远户外工作，追求矿业高收入",
    "有重型机械操作或钻探背景，快速进入关键矿产勘探",
]
SUITABILITY_UNFIT = [
    "不接受FIFO和长期偏远驻扎",
    "期望城市室内工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 712212 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Driller 薪资及岗位量", "url": "https://www.seek.com.au/driller-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲钻探工工资多少？", "answer": "中级RC/金刚石钻探工年薪约 $100,000~$140,000 FIFO。高级/首席钻探工可达 $200,000+。"},
    {"faq_type": "demand", "sort_order": 1, "question": "钻探工在澳洲容易找工作吗？", "answer": "非常容易。关键矿产勘探热潮使RC和金刚石钻工极度稀缺，WA/NT/QLD岗位大量空缺。"},
]
MARKDOWN = """# 钻探操作工（Driller）职业分析 · 澳大利亚

**职业代码：712212 – Driller。**

钻探操作工为矿产勘探和岩土调查执行钻探作业，关键矿产（锂/铜/稀土）勘探热潮使RC和金刚石钻专才极度短缺。FIFO收入极高，入行门槛相对较低。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0~2年） | $75,000~$100,000 |
| 中级 FIFO（2~6年） | $100,000~$140,000 |
| 高级/首席 | $140,000~$200,000+ |

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
    print("[OK] 钻探操作工入库完成")
if __name__ == "__main__": run()
