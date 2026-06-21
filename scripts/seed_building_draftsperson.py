"""Building and Architectural Draftsperson (312111) 建筑绘图师 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "312111", "anzsco_title": "Architectural Draftsperson",
    "category": "技术", "workforce_size": 16000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Design Documentation","Commercial & Mixed-Use Development","BIM (Building Information Modelling)","Aged Care & Healthcare Facilities"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "建筑绘图师",
    "summary": "建筑绘图师（Architectural Draftsperson）负责使用CAD和BIM软件绘制建筑施工图和设计文件。澳大利亚住宅建设繁荣和商业开发旺盛带动持续需求，BIM技能成为核心竞争力，移民背景申请者因设计制图经验丰富而受欢迎。",
    "forecast_note": "联邦「住宅未来基金」新建计划（至2029年120万套）带动设计文件需求。BIM平台（Revit/ArchiCAD）技能成为招聘标准配置。JSA列为短缺职业（2025）。",
    "trend_summary": "BIM协调和3D建模逐步替代2D AutoCAD，但设计文件审核和客户沟通仍需人工。有BIM技能的绘图师薪资溢价明显。"}
I18N_EN = {"locale": "en", "name": "Architectural Draftsperson",
    "summary": "Architectural Draftspersons prepare detailed technical drawings and building documentation using CAD and BIM software for residential and commercial construction projects. Classified under ANZSCO 312111, demand is driven by Australia's strong housing construction pipeline and commercial development activity.",
    "forecast_note": "Federal housing target (1.2M homes by 2029) drives documentation demand. BIM skills (Revit/ArchiCAD) now standard in job listings. JSA confirms shortage.",
    "trend_summary": "BIM coordination and 3D modelling increasingly replace 2D CAD, but documentation review and client liaison remain human roles. BIM-skilled draftspersons command salary premiums."}
EDUCATION = [
    {"stage": "Diploma in Architectural Technology / Cert IV in Building Design", "duration": "12~24个月", "cost_min": 3000, "cost_max": 15000, "cost_note": "TAFE国际学生约$12,000~$15,000；本地补贴后更低", "sort_order": 0},
    {"stage": "Revit / ArchiCAD / AutoCAD 认证培训", "duration": "3~6个月（自学+考试）", "cost_min": 500, "cost_max": 2000, "cost_note": "软件培训费；Autodesk认证考试约$200", "sort_order": 1},
    {"stage": "Vetassess Skills Assessment（移民评估）", "duration": "3~6个月", "cost_min": 800, "cost_max": 1500, "cost_note": "Vetassess评估费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate IV / Diploma in Architectural Technology", "issuer": "TAFE / RTO", "note": "主流入行资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Autodesk Revit Certified User/Professional", "issuer": "Autodesk", "note": "BIM市场标准证书", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Vetassess Skills Assessment", "issuer": "Vetassess", "note": "技能移民评估", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 600, "note": "全国，住宅和商业均有"},
    {"platform": "Indeed", "count_min": 150, "count_max": 350, "note": "含BIM协调员"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 250, "note": "偏商业和大型项目"},
]
SALARIES = [
    {"experience": "初级绘图师（0~2年）", "salary_min": 55000, "salary_max": 70000, "salary_note": "住宅设计公司", "sort_order": 0},
    {"experience": "中级绘图师（2~5年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "Seek AU 均值约$35~$45/hr（2026）", "sort_order": 1},
    {"experience": "资深绘图师 / BIM协调员（5年+）", "salary_min": 90000, "salary_max": 115000, "salary_note": "BIM+项目协调；大型事务所溢价", "sort_order": 2},
    {"experience": "BIM经理 / 技术负责人", "salary_min": 110000, "salary_max": 140000, "salary_note": "大型商业和基建项目", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "积分制独立移民", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "BIM软件学习曲线中等；建筑规范理解需要时间"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "Diploma 1~2年；有建筑背景者更快"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "Diploma + 软件证书；Vetassess评估"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "住宅建设+商业开发双驱动，BIM需求旺盛"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "海外工作经验丰富者有竞争力，BIM技能为分水岭"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "办公室工作，项目截止日前强度提升"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位$70k~$90k；BIM经理可达$140k"},
    {"dimension": "future_prospect",          "label_zh": "佳",   "stars": 4, "note": "BIM技能升级后职业天花板高，可向建筑师过渡"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI辅助设计（Generative Design）在普及，但文件审核仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列，189/190/482均可"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "Vetassess评估+英语+积分"},
]
SUITABILITY_FIT = [
    "有建筑设计、施工图绘制或AutoCAD背景，目标技能移民来澳",
    "愿意学习BIM（Revit/ArchiCAD），提升职业竞争力",
    "希望在建筑行业深耕，未来向建筑师或BIM经理发展",
]
SUITABILITY_UNFIT = [
    "完全没有设计或技术制图经验（起点太低）",
    "不愿意持续更新软件技能（BIM平台每年升级）",
    "期望完全脱离电脑的户外工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 312111 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Draftsperson 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/architectural-draftsperson-jobs"},
    {"source_name": "Vetassess", "content": "技能评估", "url": "https://www.vetassess.com.au/"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲建筑绘图师工资多少？", "answer": "中级绘图师年薪约 $70,000~$90,000（约$35~$45/hr）。BIM协调员/经理可达 $90,000~$140,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲建筑绘图师容易找工作吗？", "answer": "比较容易，尤其有BIM技能者。住宅和商业项目均有需求，Seek挂牌300~600个职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内建筑设计经验澳洲认可吗？", "answer": "需通过Vetassess技能评估（3~6个月）。有AutoCAD/Revit经验者评估通过率较高。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "建筑绘图师会被AI取代吗？", "answer": "部分基础绘图可能被AI辅助，但文件审核、客户沟通和规范合规判断仍需人工。学BIM可以提高职业稳定性。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要建筑学学位吗？", "answer": "不需要。Diploma/Certificate IV即可入行，有海外建筑学位者可直接申请Vetassess。"},
]
MARKDOWN = """# 建筑绘图师（Architectural Draftsperson）职业分析 · 澳大利亚

**职业代码：312111 – Architectural Draftsperson。**

建筑绘图师负责使用CAD和BIM软件绘制建筑施工图和设计文件。澳大利亚住宅建设繁荣和商业开发旺盛带动持续需求，BIM技能成为核心竞争力，移民背景申请者因设计制图经验丰富而受欢迎。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** BIM软件学习曲线中等，建筑规范理解需要时间积累。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate IV / Diploma in Architectural Technology | 12~24个月 | $3,000~$15,000（TAFE国际学生约$12,000~$15,000） |
| Revit / ArchiCAD 认证培训 | 3~6个月 | $500~$2,000 |
| Vetassess 技能评估（移民） | 3~6个月 | $800~$1,500 |

---

## 2. 考证难度 / 从业资质

**考证难度：较低（★★☆☆☆）。** Diploma入门门槛不高，BIM软件证书提升竞争力。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate IV / Diploma in Architectural Technology | TAFE / RTO | 主流入行资质 |
| Autodesk Revit Certified User/Professional | Autodesk | BIM市场标准 |
| Vetassess Skills Assessment | Vetassess | 技能移民评估 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：高（★★★★☆）。** 住宅建设繁荣+商业开发双驱动，BIM人才需求旺盛。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 300~600 个 | 全国，住宅和商业均有 |
| Indeed | 150~350 个 | 含BIM协调员 |
| LinkedIn | 100~250 个 | 偏商业和大型项目 |

**竞争度：中等（★★★☆☆）。** 有BIM技能者竞争力强，纯2D AutoCAD竞争更激烈。

**工作强度：中等（★★★☆☆）。** 办公室工作，项目截止日前强度会提升。

---

## 4. 薪资范围

**收入水平：中等（★★★☆☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 初级绘图师（0~2年） | $55,000~$70,000 | 住宅设计公司 |
| 中级绘图师（2~5年） | $70,000~$90,000 | 均值约$35~$45/hr（2026） |
| 资深绘图师 / BIM协调员（5年+） | $90,000~$115,000 | BIM+项目协调 |
| BIM经理 / 技术负责人 | $110,000~$140,000 | 大型商业和基建项目 |

---

## 5. 职业前景

**未来前景：佳（★★★★☆）。** BIM技能升级后职业天花板高，可向建筑师、BIM经理或项目协调员发展。住宅建设计划（2029年前）持续提供需求。

---

## 6. AI 替代风险

**AI风险：中等（★★★☆☆）。** AI辅助设计（Generative Design）在普及，但文件审核、规范合规和客户沟通仍需人工。主动学习BIM可提高职业稳定性。

---

## 7. 移民路径

**PR友好度：高（★★★★☆）。** CSOL在列，189/190/482均可申请。

| 签证类别 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临居 | 雇主担保，最长4年 |
| 186 ENS | 永居 | 直接永居 |
| 189 Skilled Independent | 永居 | 积分制独立移民 |
| 190 Skilled Nominated | 永居 | 州提名加5分 |

---

## 8. 谁适合学建筑绘图师？

- 有建筑设计、施工图绘制或AutoCAD背景，目标技能移民来澳
- 愿意学习BIM（Revit/ArchiCAD），提升职业竞争力
- 希望在建筑行业深耕，未来向建筑师或BIM经理发展

## 谁不适合学建筑绘图师？

- 完全没有设计或技术制图经验
- 不愿意持续更新软件技能（BIM平台每年升级）
- 期望完全脱离电脑的户外工作

---

## 9. 常见问题

**澳洲建筑绘图师工资多少？**
中级绘图师年薪约 $70,000~$90,000（约$35~$45/hr）。BIM协调员/经理可达 $90,000~$140,000。

**澳洲建筑绘图师容易找工作吗？**
比较容易，尤其有BIM技能者。住宅和商业项目均有需求，Seek挂牌300~600个职位。

**国内建筑设计经验澳洲认可吗？**
需通过Vetassess技能评估（3~6个月）。有AutoCAD/Revit经验者评估通过率较高。

**建筑绘图师会被AI取代吗？**
部分基础绘图可能被AI辅助，但文件审核、规范合规和客户沟通仍需人工。学BIM可以提高职业稳定性。

---

*数据来源：JSA Labour Market Insights、Seek AU、Vetassess、Department of Home Affairs CSOL（2025-2026）*
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
    print("[OK] 建筑绘图师（Architectural Draftsperson）入库+Markdown完成")

if __name__ == "__main__":
    run()
