"""Refrigeration and Air Conditioning Mechanic (342112) 制冷/冷冻技师 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "342112", "anzsco_title": "Refrigeration and Air Conditioning Mechanic",
    "category": "技工", "workforce_size": 30000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Commercial HVAC-R Systems","Data Centre Cooling","Cold Chain Logistics","Renewable Cooling/Heat Pump"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "制冷与空调技师",
    "summary": "制冷与空调技师（Refrigeration and Air Conditioning Mechanic）安装、维修和保养商用空调、冷藏和工业制冷系统。澳洲气候极端高温使HVAC-R成为强需求行业，数据中心冷却和冷链物流进一步拉动需求。CSOL短缺职业，各州持续招聘。",
    "forecast_note": "数据中心制冷（AI算力驱动）快速扩张，冷链物流（食品/医药）持续增长，热泵节能改造国家政策扶持，三条线同时驱动制冷技师需求大增。",
    "trend_summary": "新型制冷剂（低GWP）转型需要持证技师持续更新知识。自动化监控介入但现场安装和维修不可替代。全澳最高需求技工之一，尤其是有商用HVAC经验者。"}
I18N_EN = {"locale": "en", "name": "Refrigeration and Air Conditioning Mechanic",
    "summary": "HVAC-R mechanics install, service and maintain commercial air conditioning, refrigeration and industrial cooling systems. Australia's extreme climate makes HVAC-R a consistently high-demand trade. Data centre cooling and cold chain logistics add new demand. Listed on CSOL shortage occupation list.",
    "forecast_note": "Data centre cooling (AI-driven compute expansion) growing rapidly. Cold chain logistics (food/pharmaceutical) sustained growth. Government heat pump incentives driving renovation demand. Three parallel growth drivers significantly increasing HVAC-R mechanic demand.",
    "trend_summary": "New low-GWP refrigerant transition requires continuous certification updates. Monitoring automation advances but on-site installation and repair remains irreplaceable. One of highest-demand trades nationally, especially with commercial HVAC experience."}
EDUCATION = [
    {"stage": "Certificate III in Air Conditioning and Refrigeration", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州TAFE", "sort_order": 0},
    {"stage": "ARCTick Refrigerant Handling Licence", "duration": "1~2个月", "cost_min": 500, "cost_max": 1500, "cost_note": "制冷剂操作执照，行业强制", "sort_order": 1},
    {"stage": "海外资质TRA互认", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Air Conditioning and Refrigeration", "issuer": "TAFE/RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "ARCTick Refrigerant Handling Licence", "issuer": "ARC (Australian Refrigeration Council)", "note": "法规强制要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Electrical Licence (Restricted)", "issuer": "各州", "note": "部分州要求", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 500, "count_max": 1200, "note": "全国，各州普遍旺盛"},
    {"platform": "Indeed", "count_min": 250, "count_max": 600, "note": "商用HVAC方向"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 250, "note": "数据中心和工业冷链"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 30000, "salary_max": 65000, "salary_note": "Air Conditioning Award", "sort_order": 0},
    {"experience": "初级HVAC-R（1~3年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "商用基础", "sort_order": 1},
    {"experience": "中级（3~8年）", "salary_min": 95000, "salary_max": 130000, "salary_note": "Seek均值约$47~$62/hr（2026）", "sort_order": 2},
    {"experience": "高级/数据中心专家（8年+）", "salary_min": 120000, "salary_max": 160000, "salary_note": "数据中心冷却系统", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "制冷剂处理+电气基础"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+ARCTick制冷剂执照"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "全澳最紧缺技工之一，各州普遍旺盛"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "数千个岗位持续招聘，竞争极低"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "服务型工作，需上屋顶和狭小空间"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中级 $95k~$130k；数据中心专家$160k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "数据中心+冷链+热泵三条增长线"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "监控自动化发展，现场安装维修不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，各州提名均开放"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+ARCTick+英语"},
]
SUITABILITY_FIT = [
    "有空调、制冷或HVAC经验，目标技能移民澳洲",
    "愿意持续更新制冷剂技术知识，追求数据中心高薪方向",
    "喜欢多样化工作场所（商用楼宇/工业/冷链）",
]
SUITABILITY_UNFIT = [
    "不接受需要在屋顶和狭小机房工作的环境",
    "无任何机械或电气基础",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 342112 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Refrigeration Mechanic 薪资及岗位量（2026）", "url": "https://www.seek.com.au/refrigeration-mechanic-jobs"},
    {"source_name": "ARC", "content": "ARCTick 制冷剂执照", "url": "https://www.arctick.org/"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲制冷技师工资多少？", "answer": "中级制冷技师年薪约 $95,000~$130,000（$47~$62/hr）。数据中心冷却专家可达 $120,000~$160,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "制冷技师在澳洲好找工作吗？", "answer": "非常容易，全澳最紧缺技工之一。Seek挂牌500~1200个职位，各州普遍旺盛。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内空调制冷经验澳洲认可吗？", "answer": "需TRA技能评估（12~18个月）。到澳后还需取得ARCTick制冷剂操作执照（法规强制）。"},
    {"faq_type": "future", "sort_order": 3, "question": "为什么数据中心方向薪资更高？", "answer": "AI算力驱动数据中心制冷需求爆发，对24×7不停机系统维护要求极高，薪资溢价明显。"},
]
MARKDOWN = """# 制冷与空调技师（HVAC-R Mechanic）职业分析 · 澳大利亚

**职业代码：342112 – Refrigeration and Air Conditioning Mechanic。**

制冷与空调技师安装维修商用HVAC、冷藏和工业制冷系统，是澳洲全国最紧缺技工之一。数据中心冷却（AI驱动）、冷链物流和热泵改造三条增长线并驱，未来前景极佳。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 学徒（0~4年） | $30,000~$65,000 |
| 初级（1~3年） | $75,000~$95,000 |
| 中级（3~8年） | $95,000~$130,000 |
| 数据中心/工业专家 | $120,000~$160,000 |

---

*数据来源：JSA、Seek AU、ARC、Department of Home Affairs（2025-2026）*
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
    print("[OK] 制冷与空调技师（HVAC-R Mechanic）入库+Markdown完成")
if __name__ == "__main__": run()
