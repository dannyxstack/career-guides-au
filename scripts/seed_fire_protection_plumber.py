"""Fire Protection Plumber (334114) 消防管道工 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "334114", "anzsco_title": "Fire Protection Plumber",
    "category": "技工", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["High-Rise Residential Sprinkler Systems","Commercial & Industrial Fire Suppression","Aged Care & Healthcare Compliance","Data Centre Fire Protection"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "消防管道工",
    "summary": "消防管道工（Fire Protection Plumber）负责设计、安装、测试和维护建筑消防喷淋、灭火剂和消防水系统。澳大利亚高层建筑和医疗机构消防合规要求严格，持证消防管道工供不应求，薪资在技工类中属于较高水平。",
    "forecast_note": "高层住宅建设（NCC消防规范升级）带动喷淋系统需求。老年护理机构合规改造市场扩大（皇家委员会推动）。数据中心防火系统升级需求增加。",
    "trend_summary": "无卤素灭火剂（HFC替代）和电气火灾探测系统成为新增需求。持证消防管道工稀缺，独立承包商市场活跃，收入高于普通管道工。"}
I18N_EN = {"locale": "en", "name": "Fire Protection Plumber",
    "summary": "Fire Protection Plumbers design, install, test and maintain fire sprinkler systems, suppression agents and fire water systems in buildings. Classified under ANZSCO 334114, strict licensing requirements and growing construction volumes create persistent shortages of qualified fire protection plumbers across Australia.",
    "forecast_note": "High-rise residential construction (NCC fire code upgrades) drives sprinkler demand. Aged care compliance retrofits expanding. Data centre fire suppression upgrades adding specialist demand.",
    "trend_summary": "HFC-free suppression agents and electrical fire detection integration create new technical demand. Licensed fire protection plumbers are scarce; subcontractors earn well above trade average."}
EDUCATION = [
    {"stage": "Certificate III in Plumbing (Fire Protection Stream)", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州差异；工具费约$500~$1,000", "sort_order": 0},
    {"stage": "Fire Protection Licence（各州单独颁发）", "duration": "含在学徒或独立考试", "cost_min": 400, "cost_max": 1200, "cost_note": "各州持证费用", "sort_order": 1},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Plumbing (Fire Protection)", "issuer": "TAFE / RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "State Fire Protection Licence", "issuer": "各州建筑/消防监管机构", "note": "强制持证执业", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 150, "count_max": 350, "note": "全国，建筑和维护均有"},
    {"platform": "Indeed", "count_min": 80, "count_max": 200, "note": "含承包商职位"},
    {"platform": "LinkedIn", "count_min": 40, "count_max": 100, "note": "偏商业和工业项目"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 30000, "salary_max": 58000, "salary_note": "Fair Work Award + 消防津贴", "sort_order": 0},
    {"experience": "初级消防管道工（1~3年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "住宅高层和商业项目", "sort_order": 1},
    {"experience": "中级消防管道工（3~8年）", "salary_min": 95000, "salary_max": 125000, "salary_note": "Seek均值约$45~$58/hr（2026）", "sort_order": 2},
    {"experience": "资深 / 承包商（8年+）", "salary_min": 120000, "salary_max": 165000, "salary_note": "独立承包商，工业和数据中心溢价", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "消防系统规范复杂，液压计算和测试要求高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年+各州持证"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "各州单独持证，消防安全标准严格"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "高层建设+合规改造需求旺盛，持续短缺"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持证要求高导致供给稀缺"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "高层作业，压力测试准确性要求高"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中位$95k~$125k；独立承包商$165k+"},
    {"dimension": "future_prospect",          "label_zh": "佳",   "stars": 4, "note": "NCC升级和老年护理合规持续驱动，中期稳定"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场安全检测和压力测试需要持证人员，无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "TRA评估+各州持证认证+英语"},
]
SUITABILITY_FIT = [
    "有管道、水力或消防系统安装背景，目标技能移民来澳",
    "注重安全规范，擅长系统化检测，细心谨慎",
    "考虑独立创业做承包商，高层和工业方向收入可观",
]
SUITABILITY_UNFIT = [
    "对高风险安全作业（消防系统失效危害）心理压力大",
    "不愿意学习持续更新的消防法规",
    "期望快速入行（持证周期长）",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 334114 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Fire Protection Plumber 薪资（2026）", "url": "https://www.seek.com.au/fire-protection-plumber-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲消防管道工工资多少？", "answer": "中级消防管道工年薪约 $95,000~$125,000（约$45~$58/hr）。独立承包商和工业/数据中心方向可达 $120,000~$165,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲消防管道工容易找工作吗？", "answer": "容易。高层建设和合规改造需求旺盛，持证门槛高导致供给稀缺，持证后通常快速入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内消防安装经验澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月）后再申请各州消防持证。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "消防管道工会被机器人替代吗？", "answer": "极低。消防系统压力测试和安全检测需要持证人员现场负责，法规也要求如此。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III+州持证即可，高中毕业可入读TAFE学徒。"},
]
MARKDOWN = """# 消防管道工（Fire Protection Plumber）职业分析 · 澳大利亚

**职业代码：334114 – Fire Protection Plumber。**

消防管道工负责设计、安装、测试和维护建筑消防喷淋、灭火剂和消防水系统。严格的持证要求和高层建设合规需求，使持证消防管道工处于持续短缺状态，薪资在技工类中属于较高水平。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中高（★★★★☆）。** 消防系统规范复杂，液压计算和压力测试要求严格。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate III in Plumbing (Fire Protection)（学徒） | 42~48个月 | $0~$3,000（各州差异） |
| 各州 Fire Protection Licence | 含在学徒或独立考试 | $400~$1,200 |
| 海外资质互认（TRA） | 12~18个月 | $2,000~$5,000 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中高（★★★★☆）。** 各州单独颁发消防持证，安全标准严格。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Plumbing (Fire Protection) | TAFE / RTO | 执业核心资质 |
| State Fire Protection Licence | 各州建筑/消防监管机构 | 强制持证执业 |
| White Card | 各州SafeWork | 工地强制 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：高（★★★★☆）。** 高层建设合规需求和老年护理改造市场旺盛，JSA确认持续短缺。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 150~350 个 | 全国，建筑和维护均有 |
| Indeed | 80~200 个 | 含承包商职位 |
| LinkedIn | 40~100 个 | 偏商业和工业项目 |

**竞争度：较低（★★☆☆☆）。** 持证要求高导致供给稀缺，持证工人抢手。

**工作强度：中高（★★★★☆）。** 高层作业，压力测试准确性要求高，需高度安全意识。

---

## 4. 薪资范围

**收入水平：高（★★★★☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $30,000~$58,000 | Fair Work Award + 消防津贴 |
| 初级消防管道工（1~3年） | $75,000~$95,000 | 住宅高层和商业项目 |
| 中级消防管道工（3~8年） | $95,000~$125,000 | 均值约$45~$58/hr（2026） |
| 资深 / 承包商（8年+） | $120,000~$165,000 | 独立承包商，工业和数据中心溢价 |

---

## 5. 职业前景

**未来前景：佳（★★★★☆）。** NCC消防规范升级和老年护理合规改造持续驱动，中期稳定，数据中心防火系统升级为新增需求。

---

## 6. AI 替代风险

**AI风险：极低（★☆☆☆☆）。** 消防系统压力测试和安全检测需要持证人员现场负责，法规明确要求，无法自动化。

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

## 8. 谁适合学消防管道工？

- 有管道、水力或消防系统安装背景，目标技能移民来澳
- 注重安全规范，擅长系统化检测，细心谨慎
- 考虑独立创业做承包商，高层和工业方向收入可观

## 谁不适合学消防管道工？

- 对高风险安全作业心理压力大
- 不愿意学习持续更新的消防法规
- 期望快速入行（持证周期长）

---

## 9. 常见问题

**澳洲消防管道工工资多少？**
中级消防管道工年薪约 $95,000~$125,000（约$45~$58/hr）。独立承包商可达 $120,000~$165,000。

**澳洲消防管道工容易找工作吗？**
容易。高层建设和合规改造需求旺盛，持证门槛高导致供给稀缺，持证后快速入职。

**国内消防安装经验澳洲认可吗？**
不直接认可。需通过TRA评估（12~18个月）后再申请各州消防持证。

**消防管道工会被机器人替代吗？**
极低。消防系统压力测试需要持证人员现场负责，法规要求如此，无法自动化。

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
    print("[OK] 消防管道工（Fire Protection Plumber）入库+Markdown完成")

if __name__ == "__main__":
    run()
