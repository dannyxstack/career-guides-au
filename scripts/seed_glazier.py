"""Glazier (333311) 玻璃安装工 — AU market data 2025-2026"""
import sys, os, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "333311", "anzsco_title": "Glazier",
    "category": "技工", "workforce_size": 14000, "shortage_listed": 1,
    "growth_areas": json.dumps(["High-Rise Curtain Wall & Facade","Residential Window Replacement","Commercial Fitout","Energy-Efficient Double Glazing"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "玻璃安装工",
    "summary": "玻璃安装工（Glazier）负责测量、切割和安装玻璃于建筑门窗、幕墙及隔断系统。澳大利亚高层建筑幕墙工程旺盛，叠加住宅节能改造需求，持证玻璃工处于持续短缺状态。",
    "forecast_note": "高层玻璃幕墙（curtain wall）需求随城市核心区建设增长。住宅双层隔热玻璃改造市场扩大。JSA列为短缺职业（2025）。",
    "trend_summary": "双层Low-E玻璃和结构胶粘合（structural glazing）成主流，技能要求提升。高层作业需绳索下降（abseiling）资质，薪资溢价明显。"}
I18N_EN = {"locale": "en", "name": "Glazier",
    "summary": "Glaziers measure, cut and install glass in windows, doors, shopfronts, curtain walls and partitions. Classified under ANZSCO 333311, they are in sustained demand across residential, commercial and high-rise construction in Australia.",
    "forecast_note": "High-rise curtain wall demand grows with CBD development. Residential energy-efficient glazing market expanding. JSA confirms shortage.",
    "trend_summary": "Structural glazing and Low-E insulating glass now dominant. Abseiling-certified glaziers command salary premiums for high-rise facade work."}
EDUCATION = [
    {"stage": "Certificate III in Glass and Glazing (CPC31220)（学徒）", "duration": "42~48个月", "cost_min": 0, "cost_max": 2000, "cost_note": "各州学费差异；工具费约$500~$1,000（玻璃刀、吸盘等）", "sort_order": 0},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 1},
    {"stage": "Abseiling Certification（高层幕墙加分项）", "duration": "3~5天", "cost_min": 800, "cost_max": 1500, "cost_note": "各州工作高空证", "sort_order": 2},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Glass and Glazing (CPC31220)", "issuer": "TAFE / RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Working at Heights", "issuer": "各州", "note": "建筑工地强制", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 150, "count_max": 350, "note": "全国，幕墙和住宅均有"},
    {"platform": "Indeed", "count_min": 80, "count_max": 200, "note": "含商铺玻璃"},
    {"platform": "LinkedIn", "count_min": 30, "count_max": 80, "note": "偏商业幕墙"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 28000, "salary_max": 55000, "salary_note": "Fair Work Award", "sort_order": 0},
    {"experience": "初级玻璃工（1~3年）", "salary_min": 60000, "salary_max": 80000, "salary_note": "住宅门窗和商业隔断", "sort_order": 1},
    {"experience": "中级玻璃工（3~8年）", "salary_min": 80000, "salary_max": 100000, "salary_note": "Seek AU 均值约$38~$45/hr（2026）", "sort_order": 2},
    {"experience": "高层幕墙专家 / 资深（8年+）", "salary_min": 100000, "salary_max": 130000, "salary_note": "含绳索下降津贴；CBD项目溢价", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "切割精度和安装防漏是核心技能"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA互认"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "CBD幕墙+住宅翻新，持续短缺"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持证工人供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "重玻璃搬运，高空作业体力要求高"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位$80k~$100k；高层幕墙可达$130k"},
    {"dimension": "future_prospect",          "label_zh": "佳",   "stars": 4, "note": "节能改造需求推动中长期增长"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "精密安装和现场判断无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有玻璃、幕墙或铝合金门窗安装背景，目标技能移民",
    "不惧高空作业，愿考取绳索下降资质获溢价",
    "追求精细手工艺，对切割精度有耐心",
]
SUITABILITY_UNFIT = [
    "恐高或有高空工作禁忌",
    "体力较弱（大板玻璃搬运需要）",
    "期望完全室内工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 333311 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Glazier 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/glazier-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲玻璃安装工工资多少？", "answer": "中级玻璃工年薪约 $80,000~$100,000（约$38~$45/hr）。高层幕墙专家可达 $100,000~$130,000，含绳索下降津贴。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲玻璃工容易找工作吗？", "answer": "容易。CBD幕墙和住宅翻新双驱动，Seek常年挂牌150~350个职位，JSA确认持续短缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内门窗安装经验澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月）。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "玻璃工会被机器人替代吗？", "answer": "极低。精密安装和现场防漏判断是手工艺技艺，无成熟自动化方案。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III即可，高中毕业可入读TAFE学徒。"},
]
MARKDOWN = """# 玻璃安装工（Glazier）职业分析 · 澳大利亚

**职业代码：333311 – Glazier。**

玻璃安装工负责测量、切割和安装玻璃于建筑门窗、幕墙及隔断系统。澳大利亚高层建筑幕墙工程旺盛，叠加住宅节能改造需求，持证玻璃工处于持续短缺状态。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 核心技能是切割精度、安装防漏处理和大型玻璃面板操作。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate III in Glass and Glazing (CPC31220)（学徒） | 42~48个月 | $0~$2,000（各州差异；工具费$500~$1,000） |
| 海外资质互认（TRA） | 12~18个月 | $2,000~$5,000 |
| Abseiling Certification（高层加分项） | 3~5天 | $800~$1,500 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。**

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Glass and Glazing (CPC31220) | TAFE / RTO | 执业核心资质 |
| White Card | 各州SafeWork | 工地强制 |
| Working at Heights | 各州 | 建筑工地强制 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：高（★★★★☆）。** CBD幕墙建设和住宅节能双层玻璃翻新是主驱动。JSA确认持续短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 150~350 个 | 全国，幕墙和住宅均有 |
| Indeed | 80~200 个 | 含商铺玻璃 |
| LinkedIn | 30~80 个 | 偏商业幕墙 |

**竞争度：较低（★★☆☆☆）。** 持证工人供不应求。

**工作强度：中高（★★★★☆）。** 重玻璃搬运，高空作业体力要求高，需专注防止破损。

---

## 4. 薪资范围

**收入水平：中等（★★★☆☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $28,000~$55,000 | Fair Work Award |
| 初级玻璃工（1~3年） | $60,000~$80,000 | 住宅门窗和商业隔断 |
| 中级玻璃工（3~8年） | $80,000~$100,000 | Seek均值约$38~$45/hr（2026） |
| 高层幕墙专家 / 资深（8年+） | $100,000~$130,000 | 含绳索下降津贴；CBD项目溢价 |

---

## 5. 职业前景

**未来前景：佳（★★★★☆）。** 节能建筑法规推动双层玻璃改造，CBD高层建设带动幕墙需求，中长期趋势向好。

---

## 6. AI 替代风险

**AI风险：极低（★☆☆☆☆）。** 精密切割、安装防漏和高空幕墙固定是手工艺技能，无成熟自动化方案。

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

## 8. 谁适合学玻璃安装工？

- 有玻璃、幕墙或铝合金门窗安装背景，目标技能移民
- 不惧高空作业，愿考取绳索下降资质获溢价
- 追求精细手工艺，对切割精度有耐心

## 谁不适合学玻璃安装工？

- 恐高或有高空工作禁忌
- 体力较弱（大板玻璃搬运需要）
- 期望完全室内工作

---

## 9. 常见问题

**澳洲玻璃安装工工资多少？**
中级玻璃工年薪约 $80,000~$100,000（约$38~$45/hr）。高层幕墙专家可达 $100,000~$130,000，含绳索下降津贴。

**澳洲玻璃工容易找工作吗？**
容易。CBD幕墙和住宅翻新双驱动，Seek常年挂牌150~350个职位，JSA确认持续短缺。

**国内门窗安装经验澳洲认可吗？**
不直接认可。需通过TRA评估（12~18个月）。

**玻璃工会被机器人替代吗？**
极低。精密安装和现场防漏判断是手工艺技艺，无成熟自动化方案。

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
    print("[OK] 玻璃安装工（Glazier）入库+Markdown完成")

if __name__ == "__main__":
    run()
