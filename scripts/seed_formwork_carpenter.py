"""Formwork Carpenter (331212) 模板木工 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "331212", "anzsco_title": "Formwork Carpenter",
    "category": "技工", "workforce_size": 22000, "shortage_listed": 1,
    "growth_areas": json.dumps(["High-Rise Concrete Structure","Civil Infrastructure (Bridges/Tunnels)","Tilt-Up Panel Construction","Mining & Industrial Facilities"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "模板木工",
    "summary": "模板木工（Formwork Carpenter）负责搭建和拆卸混凝土浇筑用的临时模板结构，是高层建筑和大型基建项目的核心技工。澳大利亚城市核心区高密度建设持续旺盛，模板工供不应求，薪资在技工类中属于较高水平。",
    "forecast_note": "城市高层住宅和商业开发带动混凝土结构施工量。基建大型项目（隧道、桥梁、高铁预研）增加专项模板需求。JSA确认短缺（2025）。",
    "trend_summary": "铝合金模板系统（Aluma/Doka等）普及提升效率，但搭设和监控仍需大量人工。高层项目工期紧，轮班加班收入远超普通技工。"}
I18N_EN = {"locale": "en", "name": "Formwork Carpenter",
    "summary": "Formwork Carpenters erect and dismantle the temporary mould structures used to contain poured concrete in buildings and civil infrastructure. Classified under ANZSCO 331212, they are in sustained demand across high-rise residential, commercial and civil construction in Australia.",
    "forecast_note": "Urban high-rise and CBD commercial construction sustain concrete structure demand. Large civil projects (tunnels, bridges) add specialist formwork demand. JSA confirms shortage.",
    "trend_summary": "Aluminium form systems (Aluma/Doka) improve cycle times but erection and supervision remain labour-intensive. Shift-work and overtime income well above trade average."}
EDUCATION = [
    {"stage": "Certificate III in Carpentry (CPC30220) — Formwork Stream（学徒）", "duration": "36~42个月", "cost_min": 0, "cost_max": 2000, "cost_note": "各州差异；工具费约$500~$1,000", "sort_order": 0},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 1},
    {"stage": "Working at Heights + EWP Licence", "duration": "2~3天", "cost_min": 200, "cost_max": 600, "cost_note": "高层模板必备", "sort_order": 2},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Carpentry (Formwork Stream)", "issuer": "TAFE / RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Working at Heights", "issuer": "各州", "note": "高层作业必备", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 400, "count_max": 800, "note": "全国，高层住宅和基建均有"},
    {"platform": "Indeed", "count_min": 200, "count_max": 450, "note": "含劳务公司外包"},
    {"platform": "LinkedIn", "count_min": 60, "count_max": 150, "note": "偏大型商业项目"},
]
SALARIES = [
    {"experience": "学徒（0~3年）", "salary_min": 30000, "salary_max": 58000, "salary_note": "Fair Work Award", "sort_order": 0},
    {"experience": "初级模板工（1~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "住宅高层项目", "sort_order": 1},
    {"experience": "中级模板工（3~8年）", "salary_min": 90000, "salary_max": 120000, "salary_note": "Seek均值约$45~$55/hr；EBA项目更高", "sort_order": 2},
    {"experience": "资深 / 高层专家（8年+）", "salary_min": 120000, "salary_max": 160000, "salary_note": "CBD高层+轮班津贴；FIFO基建项目$170k+", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "荷载计算、高层安全规范和铝合金系统操作要求高"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学徒3~3.5年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA+高空证"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "高层建设旺盛，供不应求，短缺持续"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "高层模板工极度稀缺，待遇好"},
    {"dimension": "work_intensity",           "label_zh": "极高", "stars": 5, "note": "高强度体力，高空作业，工期紧，轮班制"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中位$90k~$120k；高层CBD项目含EBA津贴可达$160k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "城市化加速，高层施工2030前持续旺盛"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场搭设和安全监控无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，多路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有模板、木工或混凝土施工背景，目标技能移民来澳",
    "体能好，不惧高空和轮班作业，追求高薪",
    "目标通过190/491获PR，建筑技工类路径清晰",
]
SUITABILITY_UNFIT = [
    "体力较弱或有恐高症",
    "不接受轮班和加班制度",
    "期望稳定室内工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 331212 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Formwork Carpenter 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/formwork-carpenter-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲模板木工工资多少？", "answer": "中级模板工年薪约 $90,000~$120,000（约$45~$55/hr）。CBD高层项目含EBA津贴和轮班费可达 $120,000~$160,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲模板工容易找工作吗？", "answer": "非常容易。高层建设旺盛，Seek挂牌400~800个职位，持证后通常1~2周内入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内模板工经验澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月）。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "模板工会被机器人替代吗？", "answer": "极低。现场搭设、安全监控和高层作业判断无法自动化。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III即可，高中毕业可入读TAFE。"},
]
MARKDOWN = """# 模板木工（Formwork Carpenter）职业分析 · 澳大利亚

**职业代码：331212 – Formwork Carpenter。**

模板木工负责搭建和拆卸混凝土浇筑用的临时模板结构，是高层建筑和大型基建项目的核心技工。澳大利亚城市高层建设旺盛，模板工极度短缺，薪资在技工类中属于较高水平。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中高（★★★★☆）。** 荷载计算、高层安全规范和铝合金系统操作要求较高。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate III in Carpentry (Formwork Stream)（学徒） | 36~42个月 | $0~$2,000 |
| 海外资质互认（TRA） | 12~18个月 | $2,000~$5,000 |
| Working at Heights + EWP Licence | 2~3天 | $200~$600 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。**

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Carpentry (Formwork) | TAFE / RTO | 执业核心资质 |
| White Card | 各州SafeWork | 工地强制 |
| Working at Heights | 各州 | 高层作业必备 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 城市高层住宅和商业开发持续旺盛，JSA确认持续短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 400~800 个 | 全国，高层住宅和基建均有 |
| Indeed | 200~450 个 | 含劳务公司外包 |
| LinkedIn | 60~150 个 | 偏大型商业项目 |

**竞争度：极低（★☆☆☆☆）。** 高层模板工极度稀缺，雇主主动争抢。

**工作强度：极高（★★★★★）。** 高强度体力，高空作业，工期紧，轮班制，需高度安全意识。

---

## 4. 薪资范围

**收入水平：高（★★★★☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~3年） | $30,000~$58,000 | Fair Work Award |
| 初级模板工（1~3年） | $70,000~$90,000 | 住宅高层项目 |
| 中级模板工（3~8年） | $90,000~$120,000 | 约$45~$55/hr；EBA项目更高 |
| 资深 / 高层专家（8年+） | $120,000~$160,000 | CBD高层+轮班津贴 |

---

## 5. 职业前景

**未来前景：极佳（★★★★★）。** 城市化加速，高层住宅和商业建设2030前持续旺盛，模板工需求长期高位。

---

## 6. AI 替代风险

**AI风险：极低（★☆☆☆☆）。** 现场搭设判断、安全监控和高层精度控制无法自动化。

---

## 7. 移民路径

**PR友好度：极高（★★★★★）。** CSOL在列，多签证路径可选。

| 签证类别 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临居 | 雇主担保，最长4年 |
| 186 ENS | 永居 | 直接永居 |
| 190 Skilled Nominated | 永居 | 州提名加5分 |
| 491 Skilled Work Regional | 临居→永居 | 偏远地区加15分 |

---

## 8. 谁适合学模板木工？

- 有模板、木工或混凝土施工背景，目标技能移民来澳
- 体能好，不惧高空和轮班作业，追求高薪
- 目标通过190/491获PR，建筑技工类路径清晰

## 谁不适合学模板木工？

- 体力较弱或有恐高症
- 不接受轮班和加班制度
- 期望稳定室内工作

---

## 9. 常见问题

**澳洲模板木工工资多少？**
中级模板工年薪约 $90,000~$120,000（约$45~$55/hr）。CBD高层项目含EBA津贴可达 $120,000~$160,000。

**澳洲模板工容易找工作吗？**
非常容易。高层建设旺盛，Seek挂牌400~800个职位，持证后通常1~2周内入职。

**国内模板工经验澳洲认可吗？**
不直接认可。需通过TRA评估（12~18个月）。

---

*数据来源：JSA Labour Market Insights、Seek AU、Department of Home Affairs CSOL（2025-2026）*
"""

def run():
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
    print("[OK] 模板木工（Formwork Carpenter）入库+Markdown完成")

if __name__ == "__main__":
    run()
