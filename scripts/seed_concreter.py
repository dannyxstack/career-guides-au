"""Concreter (821211) 混凝土工 — AU market data 2025-2026"""
import sys, os, json, re
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "821211", "anzsco_title": "Concreter",
    "category": "技工", "workforce_size": 28000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Slab & Driveway Construction","Civil Infrastructure (Roads, Bridges)","Tilt-Up Panel Construction","Mining & Industrial Flooring"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "混凝土工",
    "summary": "混凝土工（Concreter）负责准备、浇筑、整平和养护混凝土，用于地基、地板、路面、挡墙等各类结构。澳大利亚住宅建设繁荣和大型基建投资持续拉动需求，是技工类招聘量最大的职业之一。",
    "forecast_note": "联邦政府「住宅未来基金」计划至2029年新建120万套住宅，基础和楼板工程量巨大。基建投资（公路、隧道）持续高位。技工类岗位填补率54.3%（JSA 2025）。",
    "trend_summary": "高效泵送和激光整平设备提升效率，但浇筑、收面、缝切仍需大量人工。独立承包商（subcontractor）收入远高于雇员。"}
I18N_EN = {"locale": "en", "name": "Concreter",
    "summary": "Concreters prepare, place, compact, finish and cure concrete for structures including foundations, floors, driveways, paths and civil infrastructure. Classified under ANZSCO 821211, they are in consistent demand across residential, commercial and civil construction in Australia.",
    "forecast_note": "Federal Housing Future Fund targets 1.2M new homes by 2029. Infrastructure investment remains high. JSA reports 54.3% fill rate for trade vacancies.",
    "trend_summary": "Laser screed and pump technology improve efficiency but finishing and curing remain labour-intensive. Subcontractors earn significantly more than employees."}
EDUCATION = [
    {"stage": "Certificate III in Concreting (CPC30820)", "duration": "36~48个月（学徒）", "cost_min": 0, "cost_max": 2000, "cost_note": "各州差异；NSW补贴后接近免费；工具费约$500~$1,000", "sort_order": 0},
    {"stage": "Short Course / On-the-Job（部分工人通过工地经验取证）", "duration": "6~12个月", "cost_min": 500, "cost_max": 2000, "cost_note": "RPL（认定工作经验）路径可更快取得Certificate", "sort_order": 1},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Concreting (CPC30820)", "issuer": "TAFE / RTO", "note": "全国统一课程，执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Tilt-Up Endorsement（预制墙板）", "issuer": "各州", "note": "商业建筑专项加分", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 500, "count_max": 900, "note": "全国，住宅施工量最大"},
    {"platform": "Indeed", "count_min": 300, "count_max": 600, "note": "含承包商"},
    {"platform": "LinkedIn", "count_min": 80, "count_max": 200, "note": "偏商业和基建"},
]
SALARIES = [
    {"experience": "学徒（0~3年）", "salary_min": 28000, "salary_max": 55000, "salary_note": "Fair Work Award", "sort_order": 0},
    {"experience": "初级混凝土工（1~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "住宅地基和楼板", "sort_order": 1},
    {"experience": "中级混凝土工（3~8年）", "salary_min": 85000, "salary_max": 110000, "salary_note": "Seek AU均值约$42~$48/hr（2026）", "sort_order": 2},
    {"experience": "资深 / 带班（8年+）", "salary_min": 108000, "salary_max": 135000, "salary_note": "Vic EBA Grade 2含津贴", "sort_order": 3},
    {"experience": "承包商 / 矿业FIFO（WA/QLD）", "salary_min": 120000, "salary_max": 175000, "salary_note": "独立承包商收入更高；矿业含FIFO津贴", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "技术核心在收面质量和养护判断"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学徒3~4年；RPL路径可缩短"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "White Card+Certificate III，门槛不高"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "住宅繁荣+基建双驱动，挂牌量居技工前列"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，尤其住宅地基方向"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "重体力，弯腰工作多，时间窗口紧（混凝土凝固前必须完成）"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "雇员中位$85k~$110k；独立承包商可达$175k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "住宅计划+基建投资，2030前需求高位"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "浇筑收面技艺和临场判断无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，多路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有土木、建筑施工背景，目标技能移民来澳",
    "接受重体力户外工作，不介意早起（混凝土浇筑常在清晨开始）",
    "考虑独立创业做承包商，收入弹性大",
    "目标通过190或491路线获PR",
]
SUITABILITY_UNFIT = [
    "腰背部有慢性伤病，无法长时间弯腰作业",
    "对时间压力敏感（混凝土凝固前必须完成作业）",
    "期望室内稳定工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 821211 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Concreter 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/concreter-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
    {"source_name": "CFMEU Victoria EBA 2026", "content": "建筑行业工资协议", "url": "https://vic.cfmeu.org/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲混凝土工工资多少？", "answer": "中级混凝土工年薪约 $85,000~$110,000；独立承包商和矿业FIFO可达 $120,000~$175,000。学徒期约 $28,000~$55,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲混凝土工容易找工作吗？", "answer": "容易。住宅建设繁荣，Seek常年挂牌500~900个职位，是挂牌量最多的技工类别之一，持证后通常1~2周可入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内混凝土工经验澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月），或通过RPL认定工作经验路径取得Certificate III。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "混凝土工会被机器人替代吗？", "answer": "极低。浇筑、收面的工艺判断和临场应变无法自动化，泵送和激光整平是辅助工具而非替代。"},
    {"faq_type": "age_limit", "sort_order": 4, "question": "澳洲混凝土工有年龄限制吗？", "answer": "法律无上限。40岁以上可通过RPL或TRA互认跳过完整学徒期。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III即可，高中毕业可直接入读TAFE。"},
    {"faq_type": "difficulty", "sort_order": 6, "question": "混凝土工难学吗？", "answer": "难度中等。关键是收面工艺（技术含量高）、混合比例判断和凝固时间控制。体力要求大，工作节奏紧。"},
    {"faq_type": "comparison", "sort_order": 7, "question": "混凝土工和钢筋工哪个更适合移民澳洲？", "answer": "两者PR路径相近。混凝土工岗位总量更多，独立创业空间大；钢筋工矿业方向薪资略高。详见「混凝土工 vs 钢筋工」职业比较板块（即将上线）。"},
]
MARKDOWN = """# 混凝土工（Concreter）职业分析 · 澳大利亚

**职业代码：821211 – Concreter。**

混凝土工负责准备、浇筑、整平和养护混凝土，用于地基、地板、路面、挡墙等各类结构。澳大利亚住宅建设繁荣和大型基建投资持续拉动需求，是技工类招聘量最大的职业之一。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 技术核心在于收面质量和养护时机判断。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate III in Concreting (CPC30820)（学徒） | 36~48个月 | $0~$2,000（NSW补贴后接近免费；工具费$500~$1,000） |
| RPL（认定工作经验）路径 | 6~12个月 | $500~$2,000 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：较低（★★☆☆☆）。** Certificate III门槛不高，White Card一日完成。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Concreting (CPC30820) | TAFE / RTO | 核心执业资质 |
| White Card | 各州SafeWork | 工地强制 |
| Tilt-Up Endorsement | 各州 | 商业建筑专项加分 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 住宅+基建双驱动，Seek挂牌量居技工前列。联邦「住宅未来基金」计划2029年前新建120万套住宅，混凝土工是每个项目的起点。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 500~900 个 | 全国，住宅施工量最大 |
| Indeed | 300~600 个 | 含承包商 |
| LinkedIn | 80~200 个 | 偏商业和基建 |

**竞争度：较低（★★☆☆☆）。** 供不应求，尤其住宅地基方向。
**工作强度：高（★★★★☆）。** 重体力，弯腰工作多，时间窗口紧（混凝土凝固前必须完成）。

---

## 4. 收入范围（学徒 / 中级 / 资深）

| 经验水平 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~3年） | $28,000~$55,000 | Fair Work Award |
| 初级（1~3年） | $65,000~$85,000 | 住宅地基和楼板 |
| 中级（3~8年） | $85,000~$110,000 | Seek均值约$42~$48/hr（2026） |
| 资深 / 带班（8年+） | $108,000~$135,000 | 含EBA津贴 |
| 承包商 / 矿业FIFO | $120,000~$175,000 | 独立承包商收入弹性大 |

---

## 5. 未来趋势 / AI替代概率

**AI替代风险：极低（★☆☆☆☆）。** 浇筑、收面的工艺判断无法自动化，泵送和激光整平是辅助而非替代。
**发展前景：极佳（★★★★★）。** 住宅计划+大型基建+矿业工业地坪，需求2030前维持高位。

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

**谁适合学混凝土工？**
- 有土木、建筑施工背景，目标技能移民来澳
- 接受重体力户外工作，不介意早起（浇筑常在清晨）
- 考虑独立创业做承包商，收入弹性大
- 目标通过190或491路线获PR

**谁不适合学混凝土工？**
- 腰背部有慢性伤病，无法长时间弯腰
- 对时间压力敏感（凝固前必须完成）
- 期望室内稳定工作

---

## 8. 数据来源

| 来源 | 内容 |
|---|---|
| Jobs and Skills Australia | ANZSCO 821211 短缺数据 |
| Seek / Indeed AU | 挂牌量及薪资（2026） |
| CFMEU Victoria EBA 2026 | 建筑行业工资协议 |
| Department of Home Affairs | CSOL 职业清单 |
| TRA | 海外技工互认 |

## 快速结论

| 维度 | 评级 |
|---|---|
| 学习周期 | 中等（★★★☆☆） |
| 学习难度 | 中等（★★★☆☆） |
| 职位需求量 | 极高（★★★★★） |
| 竞争度 | 较低（★★☆☆☆） |
| AI替代风险 | 极低（★☆☆☆☆） |
| 收入水平 | 中高（★★★★☆） |
| PR友好度 | 极高（★★★★★） |

混凝土工是澳洲住宅建设最大的劳动力需求点，入行门槛在技工中偏低，独立承包商收入可观。适合有施工背景、目标快速就业或创业的技术移民首选。

---

## 9. FAQ 常见问题

**问：澳洲混凝土工工资多少？**
答：中级年薪约 $85,000~$110,000；独立承包商和矿业FIFO可达 $120,000~$175,000。学徒期约 $28,000~$55,000。

**问：澳洲混凝土工容易找工作吗？**
答：容易。住宅建设繁荣，Seek常年挂牌500~900个职位，持证后通常1~2周可入职。

**问：国内混凝土工经验澳洲认可吗？**
答：不直接认可。需通过TRA评估（12~18个月），或RPL认定工作经验路径取得Certificate III。

**问：混凝土工会被机器人替代吗？**
答：极低。浇筑、收面的临场判断无法自动化，泵送和激光整平是辅助工具。

**问：澳洲混凝土工有年龄限制吗？**
答：法律无上限。40岁以上通过RPL或TRA互认可跳过完整学徒期。

**问：需要大学文凭吗？**
答：不需要。Certificate III即可，高中毕业可直接入读TAFE。

**问：混凝土工难学吗？**
答：难度中等。关键是收面工艺、混合比例和凝固时间控制。体力要求大，节奏紧张。

**问：混凝土工和钢筋工哪个更适合移民澳洲？**
答：两者PR路径相近。混凝土工岗位总量更多，创业空间大；钢筋工矿业方向薪资略高。详见「混凝土工 vs 钢筋工」职业比较板块（即将上线）。
"""

def run():
    with get_cursor() as cur:
        cur.execute("INSERT INTO occupations (anzsco_code,occ_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE occ_code=VALUES(occ_code),anzsco_title=VALUES(anzsco_title),category=VALUES(category),workforce_size=VALUES(workforce_size),shortage_listed=VALUES(shortage_listed),growth_areas=VALUES(growth_areas)",
            (OCCUPATION["anzsco_code"],OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],OCCUPATION["category"],OCCUPATION["workforce_size"],OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"]))
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s",(OCCUPATION["anzsco_code"],))
        occ_id=cur.fetchone()["id"]
        print(f"[occupations] id={occ_id}")
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
    slug="concreter"
    with open(os.path.join(out,f"{slug}.md"),"w",encoding="utf-8") as f: f.write(MARKDOWN.strip()+"\n")
    print(f"[OK] 混凝土工 入库+Markdown完成")

if __name__=="__main__": run()
