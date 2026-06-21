"""Gas Fitter (334112) 燃气管道工 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "334112", "anzsco_title": "Gas Fitter",
    "category": "技工", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Gas Appliance Installation","Commercial Kitchen & HVAC","LPG Rural & Remote","Industrial Gas Systems"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "燃气管道工",
    "summary": "燃气管道工（Gas Fitter）负责安装、维护和修理住宅、商业及工业场所的天然气和LPG管道系统。澳大利亚住宅燃气设备安装和商业厨房改造需求稳定，加上严格的持证要求，使持证燃气工处于持续短缺状态。",
    "forecast_note": "住宅新建和翻新持续带动燃气设备安装需求。氢气基础设施试点项目（2025-2030）将创造新的专项技能需求。JSA确认短缺（2025）。",
    "trend_summary": "天然气向可再生天然气（biogas/hydrogen blend）的过渡期创造技能升级需求。持证燃气工稀缺，独立承包商薪资溢价显著。"}
I18N_EN = {"locale": "en", "name": "Gas Fitter",
    "summary": "Gas Fitters install, maintain and repair natural gas and LPG pipe systems for residential, commercial and industrial premises. Classified under ANZSCO 334112, strict licensing requirements create persistent shortages of qualified gas fitters across Australia.",
    "forecast_note": "Residential new builds and renovations sustain appliance installation demand. Hydrogen infrastructure pilots (2025-2030) add specialist demand. JSA confirms shortage.",
    "trend_summary": "Transition to renewable gas (biogas/hydrogen blend) creates upskilling demand. Licensed gas fitters are scarce, with subcontractors commanding significant premiums."}
EDUCATION = [
    {"stage": "Certificate III in Gas Fitting / Plumbing (Gas Stream)（学徒）", "duration": "42~48个月", "cost_min": 0, "cost_max": 3000, "cost_note": "各州差异；燃气持证考试费约$500~$1,000", "sort_order": 0},
    {"stage": "Gas Fitting Licence（各州单独颁发）", "duration": "含在学徒内或考试获取", "cost_min": 300, "cost_max": 800, "cost_note": "各州持证费用不同", "sort_order": 1},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Gas Fitting / Plumbing (Gas Stream)", "issuer": "TAFE / RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "State Gas Fitting Licence", "issuer": "各州能源安全监管机构", "note": "各州单独颁发，强制执行", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 450, "note": "全国，住宅和商业均有"},
    {"platform": "Indeed", "count_min": 100, "count_max": 250, "note": "含LPG农村/偏远地区"},
    {"platform": "LinkedIn", "count_min": 40, "count_max": 100, "note": "偏工业和商业"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 30000, "salary_max": 58000, "salary_note": "Fair Work Award + 燃气津贴", "sort_order": 0},
    {"experience": "初级燃气工（1~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "住宅设备安装", "sort_order": 1},
    {"experience": "中级燃气工（3~8年）", "salary_min": 90000, "salary_max": 115000, "salary_note": "Seek AU 均值约$42~$52/hr（2026）", "sort_order": 2},
    {"experience": "资深 / 承包商（8年+）", "salary_min": 110000, "salary_max": 150000, "salary_note": "独立承包商，商业厨房/工业系统溢价", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远LPG需求旺盛，加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "燃气安全法规复杂，泄漏检测和压力测试技能要求严格"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年+各州持证考试"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "各州单独持证，安全标准严格"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "住宅+商业+工业需求稳定，持续短缺"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持证要求高导致供给稀缺"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "室内外均有，需高度注意安全规范"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位$90k~$115k；独立承包商$150k+"},
    {"dimension": "future_prospect",          "label_zh": "佳",   "stars": 4, "note": "氢气过渡期创造新需求，中期稳定"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "安全检测和压力测试需要现场判断，无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "TRA评估+各州持证认证+英语"},
]
SUITABILITY_FIT = [
    "有管道、燃气设备安装背景，目标技能移民来澳",
    "注重安全规范，对细节要求高（燃气泄漏容错率为零）",
    "考虑独立创业做承包商，商业厨房和工业系统收入可观",
]
SUITABILITY_UNFIT = [
    "对高风险作业（燃气泄漏危害）心理压力大",
    "不愿意持续学习更新（法规和技术标准每年更新）",
    "期望快速入行（持证周期长）",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 334112 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Gas Fitter 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/gas-fitter-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲燃气管道工工资多少？", "answer": "中级燃气工年薪约 $90,000~$115,000（约$42~$52/hr）。独立承包商和工业方向可达 $110,000~$150,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲燃气工容易找工作吗？", "answer": "容易。住宅和商业需求持续，加上持证门槛高导致供给稀缺，持证后通常快速入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内燃气安装经验澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月）后再申请各州燃气持证。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "燃气工会被机器人替代吗？", "answer": "极低。燃气安全检测和泄漏判断需要现场专业判断，法规也要求持证人员负责。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III+州持证即可，高中毕业可入读TAFE学徒。"},
]
MARKDOWN = """# 燃气管道工（Gas Fitter）职业分析 · 澳大利亚

**职业代码：334112 – Gas Fitter。**

燃气管道工负责安装、维护和修理住宅、商业及工业场所的天然气和LPG管道系统。严格的持证要求和稳定的住宅/商业需求，使持证燃气工处于持续短缺状态。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中高（★★★★☆）。** 燃气安全法规复杂，泄漏检测和压力测试技能要求严格。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate III in Gas Fitting / Plumbing (Gas Stream)（学徒） | 42~48个月 | $0~$3,000（各州差异；持证考试费$500~$1,000） |
| 各州 Gas Fitting Licence | 含在学徒内或考试 | $300~$800 |
| 海外资质互认（TRA） | 12~18个月 | $2,000~$5,000 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中高（★★★★☆）。** 各州单独颁发燃气持证，安全标准严格。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Gas Fitting | TAFE / RTO | 执业核心资质 |
| State Gas Fitting Licence | 各州能源安全监管机构 | 强制执行 |
| White Card | 各州SafeWork | 工地强制 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：高（★★★★☆）。** 住宅设备安装、商业厨房改造和工业系统需求稳定，JSA确认持续短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 200~450 个 | 全国，住宅和商业均有 |
| Indeed | 100~250 个 | 含LPG农村/偏远地区 |
| LinkedIn | 40~100 个 | 偏工业和商业 |

**竞争度：较低（★★☆☆☆）。** 持证要求高导致供给稀缺，持证工人抢手。

**工作强度：中等（★★★☆☆）。** 室内外均有，需高度注意安全规范，零容错操作。

---

## 4. 薪资范围

**收入水平：中高（★★★★☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $30,000~$58,000 | Fair Work Award + 燃气津贴 |
| 初级燃气工（1~3年） | $70,000~$90,000 | 住宅设备安装 |
| 中级燃气工（3~8年） | $90,000~$115,000 | 均值约$42~$52/hr（2026） |
| 资深 / 承包商（8年+） | $110,000~$150,000 | 独立承包商，商业厨房/工业系统溢价 |

---

## 5. 职业前景

**未来前景：佳（★★★★☆）。** 氢气和可再生天然气基础设施试点（2025-2030）将创造新的专项技能需求，持证燃气工中期前景稳定。

---

## 6. AI 替代风险

**AI风险：极低（★☆☆☆☆）。** 燃气安全检测和泄漏判断需要现场专业判断，法规也明确要求持证人员负责，无法自动化。

---

## 7. 移民路径

**PR友好度：高（★★★★☆）。** CSOL在列，多签证路径可选。偏远LPG地区需求旺盛，491签证加分明显。

| 签证类别 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临居 | 雇主担保，最长4年 |
| 186 ENS | 永居 | 直接永居 |
| 190 Skilled Nominated | 永居 | 州提名加5分 |
| 491 Skilled Work Regional | 临居→永居 | 偏远地区加15分 |

---

## 8. 谁适合学燃气管道工？

- 有管道、燃气设备安装背景，目标技能移民来澳
- 注重安全规范，对细节要求高（燃气泄漏容错率为零）
- 考虑独立创业做承包商，商业厨房和工业系统收入可观

## 谁不适合学燃气管道工？

- 对高风险作业（燃气泄漏危害）心理压力大
- 不愿意持续学习更新（法规和技术标准每年更新）
- 期望快速入行（持证周期长）

---

## 9. 常见问题

**澳洲燃气管道工工资多少？**
中级燃气工年薪约 $90,000~$115,000（约$42~$52/hr）。独立承包商和工业方向可达 $110,000~$150,000。

**澳洲燃气工容易找工作吗？**
容易。住宅和商业需求持续，持证门槛高导致供给稀缺，持证后通常快速入职。

**国内燃气安装经验澳洲认可吗？**
不直接认可。需通过TRA评估（12~18个月）后再申请各州燃气持证。

**燃气工会被机器人替代吗？**
极低。燃气安全检测需要现场专业判断，法规要求持证人员负责，无法自动化。

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
    print("[OK] 燃气管道工（Gas Fitter）入库+Markdown完成")

if __name__ == "__main__":
    run()
