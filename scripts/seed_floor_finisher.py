"""Floor Finisher (394111) 地板工 — AU market data 2025-2026"""
import sys, os, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "394111", "anzsco_title": "Floor Finisher",
    "category": "技工", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Timber Flooring","Commercial Carpet & Vinyl","New Apartment Fitout","Renovation & Restoration"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "地板工",
    "summary": "地板工（Floor Finisher）负责铺设、磨光和修复木地板、地毯、乙烯基等各类地面材料。澳大利亚住宅翻新市场强劲，新建公寓装修需求稳定，持证地板工需求量持续超过供给。",
    "forecast_note": "住宅翻新（木地板修复/更换）是最大需求驱动，Seek挂牌量稳定。JSA列为短缺职业（2025）。新公寓竣工带来装修装饰阶段的地板安装需求。",
    "trend_summary": "工程木地板（engineered timber）和豪华乙烯基（LVP）安装量增长，替代传统实木。独立承包商市场活跃，熟练工人供不应求。"}
I18N_EN = {"locale": "en", "name": "Floor Finisher",
    "summary": "Floor Finishers lay, sand, polish and repair timber, carpet, vinyl and other floor coverings in residential and commercial buildings. Classified under ANZSCO 394111, they are in sustained demand across Australia's renovation and new construction markets.",
    "forecast_note": "Residential renovation (timber floor restoration) is the dominant demand driver. JSA confirms shortage. New apartment completions add consistent fitout volume.",
    "trend_summary": "Engineered timber and luxury vinyl plank (LVP) are displacing solid hardwood. Active subcontractor market with skilled workers in short supply."}
EDUCATION = [
    {"stage": "Certificate III in Flooring Technology (MSF30313)（学徒）", "duration": "36~42个月", "cost_min": 0, "cost_max": 2000, "cost_note": "各州差异；工具费约$800~$1,500（打磨机、铺设工具等）", "sort_order": 0},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 1},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Flooring Technology (MSF30313)", "issuer": "TAFE / RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 400, "note": "全国，住宅翻新和新建均有"},
    {"platform": "Indeed", "count_min": 100, "count_max": 250, "note": "含承包商"},
    {"platform": "LinkedIn", "count_min": 30, "count_max": 80, "note": "偏商业装修"},
]
SALARIES = [
    {"experience": "学徒（0~3年）", "salary_min": 28000, "salary_max": 52000, "salary_note": "Fair Work Award", "sort_order": 0},
    {"experience": "初级地板工（1~3年）", "salary_min": 55000, "salary_max": 72000, "salary_note": "住宅铺设", "sort_order": 1},
    {"experience": "中级地板工（3~8年）", "salary_min": 72000, "salary_max": 92000, "salary_note": "Seek AU 均值约$35~$42/hr（2026）", "sort_order": 2},
    {"experience": "资深 / 承包商（8年+）", "salary_min": 90000, "salary_max": 120000, "salary_note": "独立承包商按平米计价，高端硬木修复溢价", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "打磨工艺和木纹修复技能学习曲线较长"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学徒3~3.5年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA互认"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "住宅翻新市场强劲，持续短缺"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "跪地作业多，化学品（清漆/涂料）接触"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位$72k~$92k；独立承包商可达$120k+"},
    {"dimension": "future_prospect",          "label_zh": "佳",   "stars": 4, "note": "翻新需求持续旺盛，新建公寓稳步提供增量"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "手工艺技艺，木纹修复和打磨判断无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有地板、木工或装修背景，目标技能移民来澳",
    "追求手工艺精度，喜欢看到地板修复前后的对比效果",
    "考虑独立创业做承包商，住宅翻新市场空间大",
]
SUITABILITY_UNFIT = [
    "膝关节或腰部有慢性伤病（跪地作业多）",
    "对化学品（清漆、溶剂）过敏",
    "期望快速低门槛入行",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 394111 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Floor Finisher 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/floor-finisher-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲地板工工资多少？", "answer": "中级地板工年薪约 $72,000~$92,000（约$35~$42/hr）。独立承包商按平米计价可达 $90,000~$120,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲地板工容易找工作吗？", "answer": "容易。住宅翻新市场持续旺盛，Seek挂牌200~400个职位，JSA确认持续短缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内地板安装经验澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月）。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "地板工会被机器人替代吗？", "answer": "极低。打磨工艺判断和木纹修复技艺是手工技能，无成熟自动化方案。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III即可，高中毕业可入读TAFE。"},
]
MARKDOWN = """# 地板工（Floor Finisher）职业分析 · 澳大利亚

**职业代码：394111 – Floor Finisher。**

地板工负责铺设、磨光和修复木地板、地毯、乙烯基等各类地面材料。澳大利亚住宅翻新市场强劲，新建公寓装修需求稳定，持证地板工需求量持续超过供给。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 打磨工艺和木纹修复技能需要大量实操，学习曲线较长。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate III in Flooring Technology (MSF30313)（学徒） | 36~42个月 | $0~$2,000（各州差异；工具费$800~$1,500） |
| 海外资质互认（TRA） | 12~18个月 | $2,000~$5,000 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。**

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Flooring Technology | TAFE / RTO | 执业核心资质 |
| White Card | 各州SafeWork | 工地强制 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：高（★★★★☆）。** 住宅翻新（木地板修复/更换）是最大需求，新建公寓装修提供稳定增量。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 200~400 个 | 全国，住宅翻新和新建均有 |
| Indeed | 100~250 个 | 含承包商 |
| LinkedIn | 30~80 个 | 偏商业装修 |

**竞争度：较低（★★☆☆☆）。** 供不应求，熟练工人抢手。

**工作强度：中高（★★★★☆）。** 跪地作业多，长期接触清漆和溶剂，需做好防护。

---

## 4. 薪资范围

**收入水平：中等（★★★☆☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~3年） | $28,000~$52,000 | Fair Work Award |
| 初级地板工（1~3年） | $55,000~$72,000 | 住宅铺设 |
| 中级地板工（3~8年） | $72,000~$92,000 | 均值约$35~$42/hr（2026） |
| 资深 / 承包商（8年+） | $90,000~$120,000 | 独立承包商按平米计价 |

---

## 5. 职业前景

**未来前景：佳（★★★★☆）。** 住宅翻新需求持续旺盛，工程木地板（engineered timber）和豪华乙烯基（LVP）安装量增长，新建公寓稳步提供增量。

---

## 6. AI 替代风险

**AI风险：极低（★☆☆☆☆）。** 打磨工艺判断和木纹修复技艺是手工技能，无成熟自动化方案。

---

## 7. 移民路径

**PR友好度：高（★★★★☆）。** CSOL在列，多签证路径可选。

| 签证类别 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临居 | 雇主担保，最长4年 |
| 186 ENS | 永居 | 直接永居 |
| 190 Skilled Nominated | 永居 | 州提名加5分 |
| 491 Skilled Work Regional | 临居→永居 | 偏远地区加15分 |

---

## 8. 谁适合学地板工？

- 有地板、木工或装修背景，目标技能移民来澳
- 追求手工艺精度，喜欢看到地板修复前后的对比效果
- 考虑独立创业做承包商，住宅翻新市场空间大

## 谁不适合学地板工？

- 膝关节或腰部有慢性伤病（跪地作业多）
- 对化学品（清漆、溶剂）过敏
- 期望快速低门槛入行

---

## 9. 常见问题

**澳洲地板工工资多少？**
中级地板工年薪约 $72,000~$92,000（约$35~$42/hr）。独立承包商按平米计价可达 $90,000~$120,000。

**澳洲地板工容易找工作吗？**
容易。住宅翻新市场持续旺盛，Seek挂牌200~400个职位，JSA确认持续短缺。

**国内地板安装经验澳洲认可吗？**
不直接认可。需通过TRA评估（12~18个月）。

**地板工会被机器人替代吗？**
极低。打磨工艺判断和木纹修复技艺是手工技能，无成熟自动化方案。

---

*数据来源：JSA Labour Market Insights、Seek AU、Department of Home Affairs CSOL（2025-2026）*
"""

def run():
    import re
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO occupations (anzsco_code,occ_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas) VALUES (%s,%s,%s,%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE occ_code=VALUES(occ_code),anzsco_title=VALUES(anzsco_title),category=VALUES(category),workforce_size=VALUES(workforce_size),shortage_listed=VALUES(shortage_listed),growth_areas=VALUES(growth_areas)",
            (OCCUPATION["anzsco_code"],OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],OCCUPATION["category"],OCCUPATION["workforce_size"],OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"])
        )
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s AND country_code='AU'", (OCCUPATION["anzsco_code"],))
        occ_id = cur.fetchone()["id"]
        print(f"[occupations] id={occ_id}")
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
    with open(os.path.join(out_dir, f"{slug}.md"), "w", encoding="utf-8") as f:
        f.write(MARKDOWN.strip()+"\n")
    print(f"[markdown] {slug}.md")
    print("[OK] 地板工（Floor Finisher）入库+Markdown完成")

if __name__ == "__main__":
    run()
