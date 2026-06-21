"""Wall and Floor Tiler (333111) 贴砖工 — AU market data 2025-2026"""
import sys, os, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "333111", "anzsco_title": "Wall and Floor Tiler",
    "category": "技工", "workforce_size": 20000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Bathroom & Kitchen Renovation","New Apartment & House Construction","Commercial Fitout","Pool & Outdoor Living Areas"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "贴砖工",
    "summary": "贴砖工（Wall and Floor Tiler）负责在住宅、商业建筑的地面、墙面、泳池等铺设各类瓷砖。澳大利亚翻新市场旺盛和新房建设带动稳定需求，技艺精良的承包商收入可观，是生活类技工中就业率较高的职业之一。",
    "forecast_note": "住宅翻新市场（尤其浴室/厨房改造）是最大需求驱动。新建公寓和住宅每套均需瓷砖工程。JSA确认技工类短缺持续（2025）。",
    "trend_summary": "大型格式瓷砖（600×600mm+）和定制马赛克流行，技艺要求提升。独立承包商市场活跃，收入远高于打工。"}
I18N_EN = {"locale": "en", "name": "Wall and Floor Tiler",
    "summary": "Wall and Floor Tilers prepare surfaces and lay tiles on walls, floors, bathrooms, kitchens and pool areas in residential and commercial buildings. Classified under ANZSCO 333111, demand is driven by Australia's strong renovation market and ongoing new construction.",
    "forecast_note": "Bathroom/kitchen renovation is the largest demand driver. New residential construction adds consistent volume. JSA confirms persistent trade shortage.",
    "trend_summary": "Large format tiles and custom mosaic work increase skill requirements. Subcontractor market is active with earnings well above employment wages."}
EDUCATION = [
    {"stage": "Certificate III in Wall and Floor Tiling (CPC31120)（学徒）", "duration": "42~48个月", "cost_min": 0, "cost_max": 2000, "cost_note": "各州差异；工具费约$800~$1,500（刀具、切割机等）", "sort_order": 0},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 1},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Wall and Floor Tiling (CPC31120)", "issuer": "TAFE / RTO", "note": "全国统一课程，执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 250, "count_max": 500, "note": "全国，住宅翻新和新建"},
    {"platform": "Indeed", "count_min": 120, "count_max": 350, "note": "含承包商"},
    {"platform": "LinkedIn", "count_min": 40, "count_max": 120, "note": "偏商业装修"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 28000, "salary_max": 55000, "salary_note": "Fair Work Award", "sort_order": 0},
    {"experience": "初级贴砖工（1~3年）", "salary_min": 58000, "salary_max": 75000, "salary_note": "住宅卫浴和厨房", "sort_order": 1},
    {"experience": "中级贴砖工（3~8年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "Seek均值约$38/hr；WorldSalaries均值$73k（2025）", "sort_order": 2},
    {"experience": "资深 / 承包商（8年+）", "salary_min": 95000, "salary_max": 130000, "salary_note": "独立承包商按件计价；高端定制项目更高", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "技艺核心：对缝精度、切割、防水层处理"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "住宅翻新市场持续旺盛，短缺明显"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，定制高端瓷砖工更抢手"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "跪地作业多，膝关节负担重，切割粉尘需防护"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "雇员$75k~$95k；独立承包商可达$130k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "翻新+新建双驱动，长期需求稳定"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "手工艺技艺，对缝和切割判断无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有瓷砖、装修施工背景，目标技能移民",
    "追求手工艺精度，有耐心做复杂对缝和定制设计",
    "有意自立门户做承包商，收入弹性大",
]
SUITABILITY_UNFIT = [
    "有膝关节或腰部慢性伤病（跪地作业多）",
    "期望快速低门槛入行",
    "不接受粉尘工作环境",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 333111 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "WorldSalaries", "content": "贴砖工均值$73,409（2025）", "url": "https://worldsalaries.com/average-wall-and-floor-tiler-salary-in-australia/"},
    {"source_name": "Seek AU", "content": "Tiler 薪资及挂牌量（2026）", "url": "https://au.seek.com/career-advice/role/tiler/salary/in-melbourne"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲贴砖工工资多少？", "answer": "中级贴砖工年薪约 $75,000~$95,000（Seek AU 2026，约$38/hr）。独立承包商可达 $95,000~$130,000+。学徒期约 $28,000~$55,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲贴砖工容易找工作吗？", "answer": "容易。住宅翻新（浴室/厨房）市场持续旺盛，Seek常年挂牌250~500个职位，持证后通常很快入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内贴砖经验澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月）。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "贴砖工会被机器人替代吗？", "answer": "极低。对缝精度、切割判断和防水层处理是手工艺技艺，无成熟自动化方案。"},
    {"faq_type": "age_limit", "sort_order": 4, "question": "澳洲贴砖工有年龄限制吗？", "answer": "法律无上限。40岁以上可通过TRA互认跳过学徒期。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III即可，高中毕业可入读TAFE。"},
    {"faq_type": "difficulty", "sort_order": 6, "question": "贴砖工难学吗？", "answer": "难度中等。对缝精度和切割技能需要大量实操。大型格式瓷砖（600mm+）和定制马赛克要求更高技艺。"},
    {"faq_type": "comparison", "sort_order": 7, "question": "贴砖工和抹灰工哪个更适合移民澳洲？", "answer": "两者PR路径相近。贴砖工工艺可见性强，定制高端市场单价高；抹灰工市场规模更大。详见「贴砖工 vs 抹灰工」职业比较板块（即将上线）。"},
]
MARKDOWN = """# 贴砖工（Wall and Floor Tiler）职业分析 · 澳大利亚

**职业代码：333111 – Wall and Floor Tiler。**

贴砖工负责在住宅、商业建筑的地面、墙面、泳池等铺设各类瓷砖。澳大利亚翻新市场旺盛和新房建设带动稳定需求，技艺精良的承包商收入可观，是生活类技工中就业率较高的职业之一。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 技艺核心是对缝精度、切割技能和防水层处理。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate III in Wall and Floor Tiling (CPC31120)（学徒） | 42~48个月 | $0~$2,000（各州差异；工具费$800~$1,500） |
| 海外资质互认（TRA） | 12~18个月 | $2,000~$5,000 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。**

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Wall and Floor Tiling (CPC31120) | TAFE / RTO | 执业基础资质 |
| White Card | 各州SafeWork | 工地强制 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 住宅翻新（浴室/厨房）是最大需求，加上新建公寓和住宅，每个项目均需瓷砖工程。JSA确认技工类持续短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 250~500 个 | 全国，住宅翻新和新建 |
| Indeed | 120~350 个 | 含承包商 |
| LinkedIn | 40~120 个 | 偏商业装修 |

**竞争度：较低（★★☆☆☆）。** 定制高端瓷砖工尤其抢手。
**工作强度：中高（★★★★☆）。** 跪地作业多，膝关节负担重，切割粉尘需防护。

---

## 4. 收入范围（学徒 / 中级 / 资深）

| 经验水平 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $28,000~$55,000 | Fair Work Award |
| 初级（1~3年） | $58,000~$75,000 | 住宅卫浴和厨房 |
| 中级（3~8年） | $75,000~$95,000 | 均值约$38/hr（Seek 2026） |
| 资深 / 承包商（8年+） | $95,000~$130,000 | 按件计价，高端定制更高 |

---

## 5. 未来趋势 / AI替代概率

**AI替代风险：极低（★☆☆☆☆）。** 对缝精度和切割判断是手工艺，无法自动化。
**发展前景：极佳（★★★★★）。** 翻新+新建双驱动，大型格式瓷砖流行推高单价。

---

## 6. 移民路径 / PR难度

**PR难度：中等（★★★☆☆）。** CSOL在列，TRA评估和英语是主要门槛。

| 签证 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临时 | 雇主担保最长4年 |
| 186 ENS | 永居 | 雇主担保 |
| 190 | 永居 | 州提名加5分 |
| 491 | 临时转永居 | 偏远地区加15分 |

**PR友好度：极高（★★★★★）。**

---

## 7. 适合人群 / 不适合人群

**谁适合学贴砖工？**
- 有瓷砖、装修施工背景，目标技能移民
- 追求手工艺精度，有耐心做复杂对缝和定制设计
- 有意自立门户做承包商，收入弹性大

**谁不适合学贴砖工？**
- 有膝关节或腰部慢性伤病（跪地作业多）
- 期望快速低门槛入行
- 不接受粉尘工作环境

---

## 8. 数据来源

| 来源 | 内容 |
|---|---|
| Jobs and Skills Australia | ANZSCO 333111 短缺数据 |
| WorldSalaries | 贴砖工均值$73,409（2025） |
| Seek AU | 薪资及挂牌量（2026） |
| Department of Home Affairs | CSOL 职业清单 |
| TRA | 海外技工互认 |

## 快速结论

| 维度 | 评级 |
|---|---|
| 学习周期 | 较长（★★★★☆） |
| 学习难度 | 中等（★★★☆☆） |
| 职位需求量 | 极高（★★★★★） |
| 竞争度 | 较低（★★☆☆☆） |
| AI替代风险 | 极低（★☆☆☆☆） |
| 收入水平 | 中等（★★★☆☆） |
| PR友好度 | 极高（★★★★★） |

贴砖工是澳洲住宅翻新市场最稳定的技工之一，大型格式瓷砖和定制设计推高了技艺门槛和单价。独立承包商是收入最高的方向，适合追求手艺精细和自主经营的技术移民。

---

## 9. FAQ 常见问题

**问：澳洲贴砖工工资多少？**
答：中级年薪约 $75,000~$95,000。独立承包商可达 $95,000~$130,000+。学徒期约 $28,000~$55,000。

**问：澳洲贴砖工容易找工作吗？**
答：容易。翻新市场旺盛，Seek常年挂牌250~500个职位，持证后通常很快入职。

**问：国内贴砖经验澳洲认可吗？**
答：不直接认可。需通过TRA评估（12~18个月）。

**问：贴砖工会被机器人替代吗？**
答：极低。对缝精度和切割判断是手工艺，无成熟自动化方案。

**问：澳洲贴砖工有年龄限制吗？**
答：法律无上限。40岁以上可通过TRA互认跳过学徒期。

**问：需要大学文凭吗？**
答：不需要。Certificate III即可。

**问：贴砖工难学吗？**
答：难度中等。对缝精度和切割技能需大量实操。大型格式和定制马赛克要求更高。

**问：贴砖工和抹灰工哪个更适合移民澳洲？**
答：两者PR路径相近。贴砖工定制市场单价高；抹灰工整体市场规模更大。详见「贴砖工 vs 抹灰工」职业比较板块（即将上线）。
"""

def run():
    with get_cursor() as cur:
        cur.execute("INSERT INTO occupations (anzsco_code,occ_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE occ_code=VALUES(occ_code),anzsco_title=VALUES(anzsco_title),category=VALUES(category),workforce_size=VALUES(workforce_size),shortage_listed=VALUES(shortage_listed),growth_areas=VALUES(growth_areas)",
            (OCCUPATION["anzsco_code"],OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],OCCUPATION["category"],OCCUPATION["workforce_size"],OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"]))
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s",(OCCUPATION["anzsco_code"],))
        occ_id=cur.fetchone()["id"]
        for i18n in [I18N_ZH,I18N_EN]:
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
            fid=cur.lastrowid
            cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'zh-CN',%s,%s) ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",(fid,faq["question"],faq["answer"]))
    out=os.path.join(os.path.dirname(__file__),"..","career-contents","au")
    with open(os.path.join(out,"wall-and-floor-tiler.md"),"w",encoding="utf-8") as f: f.write(MARKDOWN.strip()+"\n")
    print("[OK] 贴砖工入库+Markdown完成")

if __name__=="__main__": run()
