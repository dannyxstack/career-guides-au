"""Quantity Surveyor (233213) 工程造价师 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "233213", "anzsco_title": "Quantity Surveyor",
    "category": "专业", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Infrastructure Project Cost Management","Residential & Commercial Construction","Government & Defence Procurement","PPP / Major Project Advisory"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "工程造价师",
    "summary": "工程造价师（Quantity Surveyor）负责建设项目的成本估算、预算管理和合同价款结算。澳大利亚大型基建投资和住宅建设旺盛，合格QS供不应求，是高薪白领移民路径中竞争压力相对较小的职业之一。",
    "forecast_note": "联邦基建投资（2025-2029超过$1700亿）带动工程造价专业需求。住宅建设繁荣叠加建材价格波动，成本控制专家需求增加。JSA列为短缺（2025）。",
    "trend_summary": "5D BIM成本集成（BIM+QS）成为大型项目标准配置，掌握Revit+CostX的QS薪资溢价显著。独立顾问（consultant）市场活跃。"}
I18N_EN = {"locale": "en", "name": "Quantity Surveyor",
    "summary": "Quantity Surveyors manage the financial aspects of construction projects, including cost estimation, budgeting, tender documentation and contract administration. Classified under ANZSCO 233213, they are in sustained demand across Australia's construction and infrastructure sectors.",
    "forecast_note": "Federal infrastructure pipeline (>$170B, 2025-2029) drives QS demand. Housing construction and material cost volatility increase need for cost management specialists. JSA confirms shortage.",
    "trend_summary": "5D BIM (Revit + CostX) integration becoming standard on major projects. QS professionals with BIM skills command salary premiums. Active independent consultant market."}
EDUCATION = [
    {"stage": "Bachelor of Quantity Surveying / Construction Management", "duration": "3年（全日制）", "cost_min": 25000, "cost_max": 45000, "cost_note": "澳洲大学学费；国际生约$30,000~$45,000/年", "sort_order": 0},
    {"stage": "AIQS 会员评估（Graduate→AIQS Member）", "duration": "2~3年工作经验后", "cost_min": 500, "cost_max": 1500, "cost_note": "AIQS年费约$500", "sort_order": 1},
    {"stage": "CostX / Revit 专业培训", "duration": "1~3个月", "cost_min": 500, "cost_max": 2000, "cost_note": "软件培训费", "sort_order": 2},
    {"stage": "AIQS / RICS 海外资质互认（移民）", "duration": "3~6个月", "cost_min": 800, "cost_max": 2000, "cost_note": "评估费用", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Quantity Surveying / Construction Economics", "issuer": "AIQS认可大学", "note": "入行核心学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AIQS Member (MAIQS)", "issuer": "Australian Institute of Quantity Surveyors", "note": "行业认可专业资质", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "RICS Member (MRICS)", "issuer": "Royal Institution of Chartered Surveyors", "note": "国际认可，海外背景移民常用", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 400, "count_max": 800, "note": "全国，建筑和基建均有"},
    {"platform": "Indeed", "count_min": 200, "count_max": 450, "note": "含顾问公司"},
    {"platform": "LinkedIn", "count_min": 200, "count_max": 500, "note": "专业白领职位，LinkedIn活跃"},
]
SALARIES = [
    {"experience": "初级QS（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "建筑公司或顾问公司", "sort_order": 0},
    {"experience": "中级QS（3~7年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "Seek AU 均值约$90,000~$110,000（2026）", "sort_order": 1},
    {"experience": "资深QS / 项目QS（7年+）", "salary_min": 115000, "salary_max": 150000, "salary_note": "大型基建项目，含福利", "sort_order": 2},
    {"experience": "QS经理 / 顾问合伙人", "salary_min": 140000, "salary_max": 200000, "salary_note": "顾问公司合伙人级别", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "积分制独立移民", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "合同法、成本工程和BIM集成学习量大"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "大学3年+2~3年工作经验获专业资质"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "AIQS/RICS会员评估，需工作经验支撑"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "基建+住宅双驱动，QS供不应求"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "合格QS稀缺，有3年经验者抢手"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "办公室工作，项目投标截止日前强度大"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中位$85k~$115k；资深/顾问$150k~$200k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "基建投资长期高位，BIM技能提升职业天花板"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI辅助估价在发展，但合同判断和谈判仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，189/190/482均可"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "AIQS/RICS评估+英语+积分"},
]
SUITABILITY_FIT = [
    "有工程造价、建筑成本或工程预算背景，目标技能移民来澳",
    "数字敏感、擅长合同谈判，有意在顾问公司发展",
    "有RICS或国内注册造价师资质，可快速获得AIQS认可",
]
SUITABILITY_UNFIT = [
    "完全没有建筑或工程背景（需要从本科重新学习）",
    "不愿意投标截止前加班应对高强度",
    "期望完全户外现场工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 233213 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "AIQS", "content": "澳洲工程造价师协会", "url": "https://www.aiqs.com.au/"},
    {"source_name": "Seek AU", "content": "Quantity Surveyor 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/quantity-surveyor-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲工程造价师工资多少？", "answer": "中级QS年薪约 $85,000~$115,000。资深QS和顾问公司合伙人可达 $150,000~$200,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲QS容易找工作吗？", "answer": "容易。联邦基建投资旺盛，Seek挂牌400~800个职位，有3年经验的QS抢手。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内造价工程师澳洲认可吗？", "answer": "需通过AIQS或RICS评估。有RICS资质者可快速互认。国内造价师资质需补充英文材料。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "QS会被AI取代吗？", "answer": "部分。AI辅助估价（CostX/Buildsoft）在发展，但合同法律判断、风险评估和甲方谈判仍需人工。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要澳洲本地学位吗？", "answer": "不一定。海外相关学历经AIQS/RICS评估认可后可直接申请，英语雅思通常要求6.5+。"},
]
MARKDOWN = """# 工程造价师（Quantity Surveyor）职业分析 · 澳大利亚

**职业代码：233213 – Quantity Surveyor。**

工程造价师负责建设项目的成本估算、预算管理和合同价款结算。澳大利亚大型基建投资和住宅建设旺盛，合格QS供不应求，是高薪白领移民路径中竞争压力相对较小的职业之一。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中高（★★★★☆）。** 合同法、成本工程和BIM集成学习量大。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Bachelor of Quantity Surveying | 3年全日制 | $25,000~$45,000（国际生约$30,000~$45,000/年） |
| AIQS Member 评估 | 2~3年工作经验后 | $500~$1,500 |
| CostX / Revit 培训 | 1~3个月 | $500~$2,000 |
| AIQS/RICS 海外资质互认 | 3~6个月 | $800~$2,000 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。** AIQS/RICS会员资质需工作经验支撑，非学历考试。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Bachelor of Quantity Surveying | AIQS认可大学 | 入行核心学历 |
| AIQS Member (MAIQS) | Australian Institute of QS | 行业认可专业资质 |
| RICS Member (MRICS) | Royal Institution of Chartered Surveyors | 海外背景移民常用 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 基建+住宅双驱动，合格QS供不应求，JSA确认持续短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 400~800 个 | 全国，建筑和基建均有 |
| Indeed | 200~450 个 | 含顾问公司 |
| LinkedIn | 200~500 个 | 专业白领职位，平台活跃 |

**竞争度：较低（★★☆☆☆）。** 合格QS稀缺，有3年经验者极为抢手。

**工作强度：中等（★★★☆☆）。** 主要是办公室工作，投标截止前有高强度时段。

---

## 4. 薪资范围

**收入水平：高（★★★★☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 初级QS（0~3年） | $65,000~$85,000 | 建筑公司或顾问公司 |
| 中级QS（3~7年） | $85,000~$115,000 | 均值约$90,000~$110,000（2026） |
| 资深QS / 项目QS（7年+） | $115,000~$150,000 | 大型基建项目 |
| QS经理 / 顾问合伙人 | $140,000~$200,000 | 顾问公司合伙人级别 |

---

## 5. 职业前景

**未来前景：极佳（★★★★★）。** 联邦基建投资（$1700亿+，2025-2029）带动长期需求，5D BIM掌握者职业天花板更高。

---

## 6. AI 替代风险

**AI风险：中等（★★★☆☆）。** AI辅助估价工具在普及，但合同法律判断、风险评估和谈判仍需人工。主动学习BIM+AI工具可提升竞争力。

---

## 7. 移民路径

**PR友好度：极高（★★★★★）。** CSOL在列，189/190/482均可申请。

| 签证类别 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临居 | 雇主担保，最长4年 |
| 186 ENS | 永居 | 直接永居 |
| 189 Skilled Independent | 永居 | 积分制独立移民 |
| 190 Skilled Nominated | 永居 | 州提名加5分 |

---

## 8. 谁适合学工程造价师？

- 有工程造价、建筑成本或工程预算背景，目标技能移民来澳
- 数字敏感、擅长合同谈判，有意在顾问公司发展
- 有RICS或国内注册造价师资质，可快速获得AIQS认可

## 谁不适合学工程造价师？

- 完全没有建筑或工程背景
- 不愿意在投标截止前应对高强度
- 期望完全户外现场工作

---

## 9. 常见问题

**澳洲工程造价师工资多少？**
中级QS年薪约 $85,000~$115,000。资深QS和顾问合伙人可达 $150,000~$200,000。

**澳洲QS容易找工作吗？**
容易。联邦基建投资旺盛，Seek挂牌400~800个职位，有3年经验的QS抢手。

**国内造价工程师澳洲认可吗？**
需通过AIQS或RICS评估。有RICS资质者可快速互认。

**QS会被AI取代吗？**
部分。AI辅助估价在发展，但合同法律判断和风险评估仍需人工。

---

*数据来源：JSA Labour Market Insights、AIQS、Seek AU、Department of Home Affairs CSOL（2025-2026）*
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
    print("[OK] 工程造价师（Quantity Surveyor）入库+Markdown完成")

if __name__ == "__main__":
    run()
