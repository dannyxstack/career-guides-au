"""Plasterer (333211) 抹灰工 — AU market data 2025-2026"""
import sys, os, json, re
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "333211", "anzsco_title": "Plasterer",
    "category": "技工", "workforce_size": 25000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential New Construction & Renovation","Commercial Fitout","Heritage Restoration","External Render (EIFS/Acrylic)"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "抹灰工",
    "summary": "抹灰工（Plasterer）负责在建筑内外墙、天花板上施加石膏、砂浆、渲染材料，提供装饰和保护性表面。澳大利亚分为内墙石膏板（Fibrous/Plasterboard）和外墙砂浆（Solid Plasterer）两个细分方向，均处于短缺状态，是住宅装修旺盛期的抢手技工。",
    "forecast_note": "住宅新建和翻新双驱动，外墙渲染（render）在中高档住宅普及推高需求。JSA确认技工类岗位持续短缺（2025）。",
    "trend_summary": "Acrylic render和EIFS隔热外墙系统快速普及，扩大了外墙抹灰工需求范围。内墙Plasterboard安装量随住宅建设直接挂钩。"}
I18N_EN = {"locale": "en", "name": "Plasterer",
    "summary": "Plasterers apply plaster, mortar and render to internal and external surfaces of buildings to provide smooth, decorative and protective finishes. Two main streams in Australia: Fibrous/Plasterboard (interior) and Solid Plasterer (exterior render). Both are listed as shortage occupations.",
    "forecast_note": "Housing construction and renovation drive demand. External render (acrylic/EIFS) is growing in mid-to-high-end residential. JSA confirms persistent shortage in trades.",
    "trend_summary": "EIFS and acrylic render systems are growing rapidly. Internal plasterboard installation volumes track housing starts closely."}
EDUCATION = [
    {"stage": "Certificate III in Plastering (CPC31320) — 学徒制", "duration": "42~48个月", "cost_min": 0, "cost_max": 2000, "cost_note": "NSW补贴后接近免费；工具费$600~$1,200", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费用", "sort_order": 1},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Plastering (CPC31320)", "issuer": "TAFE / RTO", "note": "包含内墙石膏和外墙砂浆两个方向", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 350, "count_max": 650, "note": "全国，住宅装修量最大"},
    {"platform": "Indeed", "count_min": 200, "count_max": 450, "note": "含承包商和劳务外包"},
    {"platform": "LinkedIn", "count_min": 60, "count_max": 150, "note": "偏商业装修"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 28000, "salary_max": 55000, "salary_note": "Fair Work Award", "sort_order": 0},
    {"experience": "初级抹灰工（1~3年）", "salary_min": 60000, "salary_max": 78000, "salary_note": "住宅内墙石膏板", "sort_order": 1},
    {"experience": "中级抹灰工（3~8年）", "salary_min": 78000, "salary_max": 100000, "salary_note": "ERI SalaryExpert均值约$83k；Seek AU约$40~$48/hr（2026）", "sort_order": 2},
    {"experience": "资深 / 承包商（8年+）", "salary_min": 100000, "salary_max": 130000, "salary_note": "独立承包商收入更高；ERI高端$107k", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "表面平整度和材料配比是核心技艺"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "住宅繁荣+外墙渲染需求增长，持续短缺"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，外墙render承包商尤其抢手"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "体力+手工艺，高架作业多，材料粉尘影响健康"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "雇员$78k~$100k；承包商$100k~$130k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "住宅新建和翻新双驱动，长期稳定需求"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "手工艺技艺，无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语"},
]
SUITABILITY_FIT = [
    "有装修、批灰、抹灰施工背景，希望技能移民",
    "手工精细，追求表面质量，适合艺术性强的外墙渲染方向",
    "有意自立门户做承包商，收入弹性大",
]
SUITABILITY_UNFIT = [
    "有呼吸系统疾病（粉尘环境）",
    "不能长时间高架作业",
    "期望快速低门槛入行（需4年学徒）",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 333211 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "ERI SalaryExpert", "content": "Plasterer 均值$83k；高端$107k（2025）", "url": "https://www.salaryexpert.com/salary/job/plasterer/australia"},
    {"source_name": "Seek AU", "content": "抹灰工薪资及挂牌量（2026）", "url": "https://www.seek.com.au/career-advice/role/plasterer/salary"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲抹灰工工资多少？", "answer": "中级抹灰工年薪约 $78,000~$100,000（Seek AU 2026，约$40~$48/hr）。独立承包商可达 $100,000~$130,000+。学徒期约 $28,000~$55,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲抹灰工容易找工作吗？", "answer": "容易。住宅建设和翻新市场旺盛，Seek常年挂牌350~650个职位。外墙渲染（render）承包商尤其抢手。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内抹灰经验澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月）取得认定，再取得Certificate III资质。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "抹灰工会被机器人替代吗？", "answer": "极低。表面平整度和材料配比是手工艺技艺，自动化喷涂仅用于简单场景，复杂造型无法替代。"},
    {"faq_type": "age_limit", "sort_order": 4, "question": "澳洲抹灰工有年龄限制吗？", "answer": "法律无上限。40岁以上可通过TRA互认跳过学徒期。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III即可，高中毕业可直接入读TAFE学徒课程。"},
    {"faq_type": "difficulty", "sort_order": 6, "question": "抹灰工难学吗？", "answer": "难度中等。表面平整度要求高，材料调配和干燥时间控制需要大量实操经验。外墙渲染对工艺要求更高。"},
    {"faq_type": "comparison", "sort_order": 7, "question": "抹灰工和贴砖工哪个更适合移民澳洲？", "answer": "两者PR路径相近，薪资接近。抹灰工市场规模更大；贴砖工（Tiler）工艺可见性更强，创业空间相近。详见「抹灰工 vs 贴砖工」职业比较板块（即将上线）。"},
]
MARKDOWN = """# 抹灰工（Plasterer）职业分析 · 澳大利亚

**职业代码：333211 – Plasterer。**

抹灰工负责在建筑内外墙、天花板上施加石膏、砂浆、渲染材料，提供装饰和保护性表面。澳大利亚分为内墙石膏板和外墙砂浆两个细分方向，均处于短缺状态，是住宅装修旺盛期的抢手技工。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 表面平整度和材料配比是核心技艺，需大量实操积累。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate III in Plastering (CPC31320)（学徒） | 42~48个月 | $0~$2,000（NSW补贴接近免费；工具费$600~$1,200） |
| 海外资质互认（TRA） | 12~18个月 | $2,000~$5,000 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。** Certificate III分内/外墙方向，TRA评估中等难度。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Plastering (CPC31320) | TAFE / RTO | 内墙石膏板+外墙砂浆 |
| White Card | 各州SafeWork | 工地强制 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 住宅新建和翻新双驱动，外墙渲染（acrylic render/EIFS）在中高档住宅快速普及。JSA确认技工类持续短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 350~650 个 | 全国，住宅装修量最大 |
| Indeed | 200~450 个 | 含承包商和劳务外包 |
| LinkedIn | 60~150 个 | 偏商业装修 |

**竞争度：较低（★★☆☆☆）。** 供不应求，外墙render承包商尤其抢手。
**工作强度：中高（★★★★☆）。** 体力+手工艺，高架作业多，材料粉尘影响健康需防护。

---

## 4. 收入范围（学徒 / 中级 / 资深）

| 经验水平 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $28,000~$55,000 | Fair Work Award |
| 初级（1~3年） | $60,000~$78,000 | 住宅内墙石膏板 |
| 中级（3~8年） | $78,000~$100,000 | Seek AU约$40~$48/hr（2026） |
| 资深 / 承包商（8年+） | $100,000~$130,000 | 独立承包商收入更高 |

---

## 5. 未来趋势 / AI替代概率

**AI替代风险：极低（★☆☆☆☆）。** 手工艺技艺，自动化喷涂仅适用简单场景，复杂造型无法替代。
**发展前景：极佳（★★★★★）。** 住宅新建+翻新+外墙渲染普及，需求长期稳定。

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

**谁适合学抹灰工？**
- 有装修、批灰、抹灰施工背景，希望技能移民
- 手工精细，追求表面质量，适合外墙渲染方向
- 有意自立门户做承包商，收入弹性大

**谁不适合学抹灰工？**
- 有呼吸系统疾病（粉尘环境）
- 不能长时间高架作业
- 期望快速低门槛入行（需4年学徒）

---

## 8. 数据来源

| 来源 | 内容 |
|---|---|
| Jobs and Skills Australia | ANZSCO 333211 短缺数据 |
| ERI SalaryExpert | Plasterer 均值$83k；高端$107k（2025） |
| Seek AU | 抹灰工薪资及挂牌量（2026） |
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
| 收入水平 | 中高（★★★★☆） |
| PR友好度 | 极高（★★★★★） |

抹灰工是澳洲住宅装修市场长期短缺的技工，外墙渲染和内墙石膏板双方向均有稳定需求。技艺精良的承包商收入可观，是手工艺型技术移民的优质选择。

---

## 9. FAQ 常见问题

**问：澳洲抹灰工工资多少？**
答：中级年薪约 $78,000~$100,000。独立承包商可达 $100,000~$130,000+。学徒期约 $28,000~$55,000。

**问：澳洲抹灰工容易找工作吗？**
答：容易。住宅建设旺盛，Seek常年挂牌350~650个职位，外墙渲染承包商尤其抢手。

**问：国内抹灰经验澳洲认可吗？**
答：不直接认可。需通过TRA评估（12~18个月）。

**问：抹灰工会被机器人替代吗？**
答：极低。表面平整度和造型艺术无法自动化，是手工艺行业。

**问：澳洲抹灰工有年龄限制吗？**
答：法律无上限。40岁以上可通过TRA互认跳过学徒期。

**问：需要大学文凭吗？**
答：不需要。Certificate III即可。

**问：抹灰工难学吗？**
答：难度中等。表面质量要求高，材料配比和干燥控制需大量实操经验。

**问：抹灰工和贴砖工哪个更适合移民澳洲？**
答：两者PR路径相近，薪资接近。抹灰工市场规模更大；贴砖工工艺可见性更强。详见「抹灰工 vs 贴砖工」职业比较板块（即将上线）。
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
    with open(os.path.join(out,"plasterer.md"),"w",encoding="utf-8") as f: f.write(MARKDOWN.strip()+"\n")
    print("[OK] 抹灰工入库+Markdown完成")

if __name__=="__main__": run()
