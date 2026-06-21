"""Solar PV Installer (342113) 太阳能安装工 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "342113", "anzsco_title": "Solar Panel Installer",
    "category": "技工", "workforce_size": 30000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Rooftop Solar","Commercial & Industrial Solar","Battery Storage (Solar+ESS)","Utility-Scale Solar Farm"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "太阳能安装工",
    "summary": "太阳能安装工（Solar PV Installer）负责住宅和商业屋顶光伏系统的安装、接线和调试。澳大利亚是全球人均太阳能安装量最高的国家，联邦政府清洁能源目标（2030年82%可再生）带动持续强劲的装机需求，持证安装工供不应求。",
    "forecast_note": "联邦「可再生能源目标」（2030年82%）和家庭电池补贴大幅推动装机量。各州政府屋顶光伏补贴（VIC/QLD/SA）维持旺盛需求。Seek太阳能职位挂牌量2025年同比增长35%。",
    "trend_summary": "太阳能+储能（Solar+Battery）组合安装成为主流，要求双证（太阳能+储能）技术员。商业和工业大型项目（C&I Solar）快速增长，薪资高于住宅方向。"}
I18N_EN = {"locale": "en", "name": "Solar Panel Installer",
    "summary": "Solar Panel Installers mount, wire and commission photovoltaic systems on residential and commercial rooftops. Classified under ANZSCO 342113, Australia's world-leading per-capita solar installation rate and federal renewable energy targets (82% by 2030) create persistent demand for qualified installers.",
    "forecast_note": "Federal Renewable Energy Target (82% by 2030) and household battery subsidies drive installation volumes. State government solar rebates (VIC/QLD/SA) sustain residential demand. Seek solar job listings grew 35% YoY in 2025.",
    "trend_summary": "Solar+Battery combination installs now mainstream, requiring dual accreditation. Commercial and industrial (C&I) solar projects growing rapidly with higher pay than residential."}
EDUCATION = [
    {"stage": "Certificate III in Electrotechnology Electrician + Solar PV", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "电工学徒路径；工具费约$1,000~$2,000", "sort_order": 0},
    {"stage": "Grid-Connect PV Design & Install (GSES短课程)", "duration": "3~5天", "cost_min": 1500, "cost_max": 3000, "cost_note": "已持证电工转型路径；CEC认可", "sort_order": 1},
    {"stage": "Clean Energy Council (CEC) 太阳能安装工认证", "duration": "1~3个月（线上+考试）", "cost_min": 500, "cost_max": 1500, "cost_note": "CEC认证费；澳洲STC补贴强制要求", "sort_order": 2},
    {"stage": "Battery Storage Accreditation（储能附加证）", "duration": "1~2天", "cost_min": 300, "cost_max": 800, "cost_note": "VIC/QLD补贴强制", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Electrical Licence (A Grade)", "issuer": "各州电气监管机构", "note": "太阳能接线强制要求", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "CEC Solar PV Installer Accreditation", "issuer": "Clean Energy Council", "note": "澳洲STC补贴强制要求", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "CEC Battery Storage Accreditation", "issuer": "Clean Energy Council", "note": "储能方向必备", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Working at Heights", "issuer": "各州", "note": "屋顶作业必备", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 600, "count_max": 1200, "note": "全国，住宅和商业均有"},
    {"platform": "Indeed", "count_min": 300, "count_max": 700, "note": "含储能方向"},
    {"platform": "LinkedIn", "count_min": 150, "count_max": 400, "note": "偏C&I和大型项目"},
]
SALARIES = [
    {"experience": "初级安装工（0~2年）", "salary_min": 60000, "salary_max": 80000, "salary_note": "住宅屋顶太阳能", "sort_order": 0},
    {"experience": "中级安装工（2~5年）", "salary_min": 80000, "salary_max": 105000, "salary_note": "Seek均值约$38~$50/hr（2026）", "sort_order": 1},
    {"experience": "资深 / C&I项目（5年+）", "salary_min": 100000, "salary_max": 135000, "salary_note": "商业工业项目+储能溢价", "sort_order": 2},
    {"experience": "太阳能技术主管 / 项目经理", "salary_min": 120000, "salary_max": 160000, "salary_note": "大型公用事业项目", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "有电工证基础者转型快；系统设计需额外学习"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "已持电工证者3~6个月可获CEC认证；新人需4年学徒"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CEC认证+州电气持证；储能附加证较易"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "清洁能源目标驱动，挂牌量持续增长35%+/年"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持证CEC安装工供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "屋顶高空作业，夏季高温挑战；商业项目体力要求高"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "中位$80k~$105k；C&I和储能方向可达$135k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "2030清洁能源目标驱动，长期高增长"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场安装、接线和调试无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列（342113），多路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA/CEC认证+电气持证+英语"},
]
SUITABILITY_FIT = [
    "已持澳洲电工执照（A Grade），目标快速转型可再生能源",
    "有光伏安装或电气施工背景，目标技能移民来澳",
    "追求增长型行业，愿意随技术升级持续学习（储能/V2G）",
]
SUITABILITY_UNFIT = [
    "恐高或不适应屋顶作业（夏季高温）",
    "没有电工执照且不愿意完成4年学徒",
    "期望完全稳定规律的室内工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 342113 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Clean Energy Council", "content": "CEC太阳能安装工认证", "url": "https://www.cleanenergycouncil.org.au/"},
    {"source_name": "Seek AU", "content": "Solar Installer 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/solar-installer-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲太阳能安装工工资多少？", "answer": "中级安装工年薪约 $80,000~$105,000（约$38~$50/hr）。商业工业方向资深安装工可达 $100,000~$135,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲太阳能安装工容易找工作吗？", "answer": "非常容易。清洁能源目标驱动，Seek挂牌600~1,200个职位，同比增长35%+，持CEC证者快速入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内光伏安装经验澳洲认可吗？", "answer": "不直接认可。需先获取澳洲电气执照（或TRA评估），再通过CEC太阳能安装工认证。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "太阳能安装工会被机器人替代吗？", "answer": "极低。屋顶安装、接线和系统调试是现场手工操作，无成熟自动化方案。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "没有电工证可以做太阳能安装吗？", "answer": "不建议。澳洲法规要求太阳能系统的电气接线必须由持证电工完成。没有电工证需先完成4年学徒取证，再考CEC认证。"},
]
MARKDOWN = """# 太阳能安装工（Solar Panel Installer）职业分析 · 澳大利亚

**职业代码：342113 – Solar Panel Installer。**

太阳能安装工负责住宅和商业屋顶光伏系统的安装、接线和调试。澳大利亚是全球人均太阳能安装量最高的国家，联邦清洁能源目标（2030年82%可再生）带动持续强劲的装机需求。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 已持电工证者转型快，系统设计和储能需额外学习。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| 电工学徒 + Solar PV（新人路径） | 42~48个月 | $0~$3,000 |
| Grid-Connect PV 短课程（持证电工转型） | 3~5天 | $1,500~$3,000 |
| CEC Solar PV Installer 认证 | 1~3个月 | $500~$1,500 |
| Battery Storage Accreditation（储能附加） | 1~2天 | $300~$800 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。** CEC认证+州电气持证，储能附加证较易获取。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Electrical Licence (A Grade) | 各州电气监管机构 | 太阳能接线强制要求 |
| CEC Solar PV Installer | Clean Energy Council | 澳洲STC补贴强制要求 |
| CEC Battery Storage | Clean Energy Council | 储能方向必备 |
| Working at Heights | 各州 | 屋顶作业必备 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 清洁能源目标驱动，Seek太阳能职位挂牌量2025年同比增长35%+，是增速最快的技工职位之一。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 600~1,200 个 | 全国，住宅和商业均有 |
| Indeed | 300~700 个 | 含储能方向 |
| LinkedIn | 150~400 个 | 偏C&I和大型项目 |

**竞争度：较低（★★☆☆☆）。** 持CEC证的合格安装工供不应求。

**工作强度：中高（★★★★☆）。** 屋顶高空作业，夏季高温挑战，商业项目体力要求高。

---

## 4. 薪资范围

**收入水平：中等（★★★☆☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 初级安装工（0~2年） | $60,000~$80,000 | 住宅屋顶太阳能 |
| 中级安装工（2~5年） | $80,000~$105,000 | 均值约$38~$50/hr（2026） |
| 资深 / C&I项目（5年+） | $100,000~$135,000 | 商业工业项目+储能溢价 |
| 太阳能技术主管 / 项目经理 | $120,000~$160,000 | 大型公用事业项目 |

---

## 5. 职业前景

**未来前景：极佳（★★★★★）。** 2030清洁能源目标驱动，太阳能+储能组合安装成主流，长期高增长确定性强。

---

## 6. AI 替代风险

**AI风险：极低（★☆☆☆☆）。** 现场安装、接线和系统调试无法自动化，屋顶条件复杂多变。

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

## 8. 谁适合学太阳能安装工？

- 已持澳洲电工执照（A Grade），目标快速转型可再生能源
- 有光伏安装或电气施工背景，目标技能移民来澳
- 追求增长型行业，愿意随技术升级持续学习（储能/V2G）

## 谁不适合学太阳能安装工？

- 恐高或不适应屋顶作业（夏季高温）
- 没有电工执照且不愿意完成4年学徒
- 期望完全稳定规律的室内工作

---

## 9. 常见问题

**澳洲太阳能安装工工资多少？**
中级安装工年薪约 $80,000~$105,000（约$38~$50/hr）。商业工业方向可达 $100,000~$135,000。

**澳洲太阳能安装工容易找工作吗？**
非常容易。Seek挂牌600~1,200个职位，同比增长35%+，持CEC证者快速入职。

**国内光伏安装经验澳洲认可吗？**
需先获取澳洲电气执照（或TRA评估），再通过CEC太阳能安装工认证。

**没有电工证可以做太阳能安装吗？**
不建议。澳洲法规要求电气接线由持证电工完成。没有电工证需先完成4年学徒取证。

---

*数据来源：JSA Labour Market Insights、Clean Energy Council、Seek AU、Department of Home Affairs CSOL（2025-2026）*
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
    print("[OK] 太阳能安装工（Solar Panel Installer）入库+Markdown完成")

if __name__ == "__main__":
    run()
