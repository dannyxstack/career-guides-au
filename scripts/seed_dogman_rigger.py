"""
Construction Rigger / Dogman (821711) 起重指挥/索具工
数据来源：CFMEU EBA 2026、Seek/Indeed/Glassdoor、JSA (2025-2026)
"""
import sys, os, json, re
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "821711", "anzsco_title": "Construction Rigger",
    "category": "技工", "workforce_size": 14000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Mining & Resources (FIFO WA/QLD)","Renewable Energy (Wind Farm Construction)","Civil Infrastructure & Bridge Construction","Oil & Gas Offshore"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "起重指挥/索具工",
    "summary": "起重指挥（Dogman）负责指挥起重机操作员移动和定位重型设备及结构件；索具工（Rigger）负责连接、绑扎、固定各类起重索具。在澳大利亚，两个职能通常持有同一资质（DG/RB证书），是矿业、风电场建设、大型工程的核心技工之一。",
    "forecast_note": "矿业、基建和风电场建设带动持续需求。WA/QLD矿区FIFO岗需求旺盛，技工类岗位填补率仅54.3%（JSA 2025）。",
    "trend_summary": "风电场大规模扩建（2030年前澳大利亚计划装机82GW）是最大新增需求驱动。矿业维持稳定基本盘。",
}
I18N_EN = {
    "locale": "en", "name": "Dogman / Construction Rigger",
    "summary": "Dogmen direct crane operators to move and position loads; Riggers attach and secure rigging gear to lift, move and position equipment and structural components. Both roles typically hold the same High Risk Work Licence and are in persistent demand across mining, wind farms and civil construction in Australia.",
    "forecast_note": "Wind farm construction and ongoing mining drive demand. JSA reports 54.3% fill rate for trade vacancies. FIFO demand in WA/QLD remains strong.",
    "trend_summary": "Australia's 82GW renewable target by 2030 is driving major wind farm expansion, creating significant rigger demand alongside stable mining work.",
}
EDUCATION = [
    {"stage": "Cert III in Rigging (CPCCRI3001 等) / 学徒或短期课程", "duration": "12~24个月（含OJT）", "cost_min": 1500, "cost_max": 4000, "cost_note": "Rigging课程非传统4年学徒，多为短期结合工作经验；考取各级HRWL证书另需考试费$300~$600/级", "sort_order": 0},
    {"stage": "Dogging Licence (DG) 短课程", "duration": "1~5天（理论+实操）", "cost_min": 600, "cost_max": 1500, "cost_note": "最基础的起重指挥资质，可单独持有", "sort_order": 1},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 2},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "适用于有海外rigging经验的申请人", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "High Risk Work Licence – Dogging (DG)", "issuer": "SafeWork / WorkSafe 各州", "note": "最基础起重指挥资质，入行起点", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "High Risk Work Licence – Rigging Basic (RB)", "issuer": "各州", "note": "含DG功能，提升薪资和就业面", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "High Risk Work Licence – Rigging Intermediate (RI) / Advanced (RA)", "issuer": "各州", "note": "大型工程、预应力和临时建筑需要", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 3},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 4},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 450, "note": "含矿业FIFO和风电场岗"},
    {"platform": "Indeed", "count_min": 100, "count_max": 300, "note": "含承包商"},
    {"platform": "LinkedIn", "count_min": 50, "count_max": 150, "note": "偏工业和矿业"},
]
SALARIES = [
    {"experience": "Dogman / 初级Rigger（持DG证，0~2年）", "salary_min": 65000, "salary_max": 88000, "salary_note": "Glassdoor Sydney ~$80k；一般建筑工程", "sort_order": 0},
    {"experience": "中级Rigger（RB证，3~8年）", "salary_min": 88000, "salary_max": 115000, "salary_note": "Vic EBA Grade 1=$60.46/hr≈$125k；全国均值约$90k~$100k", "sort_order": 1},
    {"experience": "高级Rigger（RI/RA证，8年+）", "salary_min": 110000, "salary_max": 140000, "salary_note": "大型工程和预应力结构专项", "sort_order": 2},
    {"experience": "矿业FIFO / 风电场建设（WA/QLD）", "salary_min": 130000, "salary_max": 190000, "salary_note": "含FIFO津贴、轮班、风电场高空津贴", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年，可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居，TRT流需482满2年", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名永居", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名，加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "入门（DG证）门槛不高，高级证书涉及复杂荷载计算"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "DG证1~5天；RB/RI/RA逐级需现场经验"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "HRWL分级考试，逐级晋升"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "矿业+风电+基建三驱动，FIFO需求旺盛"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持RB以上证书后竞争不激烈"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "户外重工业环境，高空和重物操作，安全意识极重要"},
    {"dimension": "income_level",             "label_zh": "较高", "stars": 4, "note": "中位$90k~$115k；FIFO/风电可达$190k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "风电场扩张是最大新增需求驱动，至2030持续高速增长"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场决策和安全判断高度依赖人工"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，多签证路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估和英语是主要门槛"},
]
SUITABILITY_FIT = [
    "有重工业、建筑或矿业背景，熟悉起重设备操作",
    "接受FIFO轮班或户外重工业环境",
    "目标是矿业/风电场高薪岗",
    "希望快速取证（DG证门槛相对低）再逐步晋升",
]
SUITABILITY_UNFIT = [
    "不接受FIFO轮班或远离家人的工作模式",
    "对重物操作安全规程无法认真遵守",
    "期望室内稳定工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 821711 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "CFMEU Victoria EBA 2026", "content": "Grade 1 = $60.46/hr", "url": "https://vic.cfmeu.org/wp-content/uploads/2026/02/2026-Onsite-EBA-Rates.pdf"},
    {"source_name": "Seek AU", "content": "Rigger 薪资数据（2026）", "url": "https://www.seek.com.au/career-advice/role/rigger/salary"},
    {"source_name": "Glassdoor", "content": "Dogman Rigger Sydney ~$80k", "url": "https://www.glassdoor.com.au/Salaries/sydney-dogman-rigger-salary-SRCH_IL.0,6_IM962_KO7,20.htm"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲起重指挥/索具工工资多少？", "answer": "中级Rigger（RB证）年薪约 $88,000~$115,000。矿业FIFO和风电场可达 $130,000~$190,000。初级Dogman（DG证）约 $65,000~$88,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲起重指挥/索具工容易找工作吗？", "answer": "容易。矿业、风电场建设和大型基建需求旺盛，持RB以上证书通常很快可入职。FIFO矿区岗位竞争较激烈但薪资翻倍。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内起重资质澳洲认可吗？", "answer": "不直接认可。需通过TRA评估（12~18个月），再取得澳洲HRWL（DG/RB/RI/RA）方可合法操作。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "索具工/起重指挥会被机器人替代吗？", "answer": "极低。现场安全判断、复杂荷载决策和应急处置高度依赖人工，自动化方案短期内不可替代。"},
    {"faq_type": "age_limit", "sort_order": 4, "question": "澳洲索具工有年龄限制吗？", "answer": "法律无上限。矿业FIFO通常要求有现场经验，40岁以上走TRA互认路径同样有效。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "需要大学学历吗？", "answer": "不需要。DG/RB证书培训门槛较低，重要的是现场经验和安全意识。"},
    {"faq_type": "difficulty", "sort_order": 6, "question": "DG和RB证书难考吗？", "answer": "DG（Dogging）相对容易，1~5天培训+考核；RB（Rigging Basic）需要更多现场经验和荷载计算知识，难度中等。"},
    {"faq_type": "comparison", "sort_order": 7, "question": "起重指挥/索具工和起重机操作员哪个更适合移民？", "answer": "两者PR路径相近，薪资相当。起重机操作员（Crane Operator）岗位更稳定；索具工/Dogman可配合多种项目，矿业FIFO灵活性更高。详见「索具工 vs 起重机操作员」职业比较板块（即将上线）。"},
]

MARKDOWN = """# 起重指挥/索具工（Dogman / Construction Rigger）职业分析 · 澳大利亚

**职业代码：821711 – Construction Rigger（含 Dogman）。**

起重指挥（Dogman）负责指挥起重机操作员移动和定位重型设备；索具工（Rigger）负责连接和固定起重索具。在澳大利亚，两个职能通常持有同一资质，是矿业、风电场建设和大型工程的核心技工之一。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 入门（DG证）门槛不高，高级证书涉及复杂荷载计算。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Dogging Licence (DG) 短课程 | 1~5天（理论+实操） | $600~$1,500 |
| Rigging Basic/Intermediate/Advanced（逐级） | 需现场经验，逐级考试 | $300~$600/级 |
| 海外资质互认（TRA） | 12~18个月 | $2,000~$5,000 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。** HRWL分级制度，逐级晋升提升薪资空间。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| HRWL – Dogging (DG) | 各州SafeWork/WorkSafe | 最基础起重指挥资质 |
| HRWL – Rigging Basic (RB) | 各州 | 含DG，更广泛岗位 |
| HRWL – Rigging Intermediate (RI) / Advanced (RA) | 各州 | 大型工程专项 |
| White Card | 各州 | 工地强制 |
| TRA Skills Assessment | TRA | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 矿业、风电场建设和大型基建三驱动，长期短缺。澳大利亚82GW风电目标至2030年将持续拉动索具工需求。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 200~450 个 | 含矿业FIFO和风电场岗 |
| Indeed | 100~300 个 | 含承包商 |
| LinkedIn | 50~150 个 | 偏工业和矿业 |

**竞争度：较低（★★☆☆☆）。** 持RB以上证书竞争不激烈，矿业FIFO岗略高。
**工作强度：高（★★★★☆）。** 户外重工业环境，高空和重物操作，安全意识要求极高。

---

## 4. 收入范围（学徒 / 中级 / 资深）

| 经验水平 | 年薪（AUD） | 备注 |
|---|---:|---|
| Dogman / 初级（DG证，0~2年） | $65,000~$88,000 | 一般建筑工程 |
| 中级Rigger（RB证，3~8年） | $88,000~$115,000 | Vic EBA Grade 1=$60.46/hr |
| 高级Rigger（RI/RA，8年+） | $110,000~$140,000 | 大型工程专项 |
| 矿业FIFO / 风电场（WA/QLD） | $130,000~$190,000 | 含FIFO津贴、轮班、高空作业津贴 |

---

## 5. 未来趋势 / AI替代概率

**AI替代风险：极低（★☆☆☆☆）。** 现场安全判断和应急处置高度依赖人工，无自动化替代方案。
**发展前景：极佳（★★★★★）。** 风电场扩张是最大新增驱动，澳大利亚82GW目标至2030年维持高需求。

---

## 6. 移民路径 / PR难度

**PR难度：中等（★★★☆☆）。** CSOL在列，TRA评估和英语是主要门槛。

| 签证 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临时 | 雇主担保最长4年 |
| 186 ENS | 永居 | 雇主担保永居 |
| 190 | 永居 | 州提名加5分 |
| 491 | 临时转永居 | 偏远地区加15分 |

**PR友好度：极高（★★★★★）。**

---

## 7. 适合人群 / 不适合人群

**谁适合学起重指挥/索具工？**
- 有重工业、建筑或矿业背景，熟悉起重设备操作
- 接受FIFO轮班或户外重工业环境
- 目标是矿业/风电场高薪岗
- 希望快速取证（DG证门槛相对低）再逐步晋升

**谁不适合学起重指挥/索具工？**
- 不接受FIFO轮班或长期远离家人的工作模式
- 对重物操作安全规程无法认真遵守
- 期望室内稳定工作

---

## 8. 数据来源

| 来源 | 内容 |
|---|---|
| Jobs and Skills Australia | ANZSCO 821711 短缺数据 |
| CFMEU Victoria EBA 2026 | Grade 1 = $60.46/hr |
| Seek AU | Rigger 薪资及挂牌量（2026） |
| Glassdoor AU | Dogman Rigger Sydney 均值数据 |
| Department of Home Affairs | CSOL 职业清单 |

## 快速结论

| 维度 | 评级 |
|---|---|
| 学习周期 | 中等（★★★☆☆） |
| 学习难度 | 中等（★★★☆☆） |
| 职位需求量 | 极高（★★★★★） |
| 竞争度 | 较低（★★☆☆☆） |
| AI替代风险 | 极低（★☆☆☆☆） |
| 收入水平 | 较高（★★★★☆） |
| PR友好度 | 极高（★★★★★） |

起重指挥/索具工入门门槛相对其他技工更低（DG证1~5天），但薪资极具竞争力，矿业FIFO和风电场是收入最高的方向。风电场扩建至2030年将是最大需求驱动，是技术移民的优质路径。

---

## 9. FAQ 常见问题

**问：澳洲起重指挥/索具工工资多少？**
答：中级Rigger（RB证）年薪约 $88,000~$115,000。矿业FIFO和风电场可达 $130,000~$190,000。初级Dogman（DG证）约 $65,000~$88,000。

**问：澳洲起重指挥/索具工容易找工作吗？**
答：容易。矿业、风电场和大型基建需求旺盛，持RB以上证书通常很快可入职。

**问：国内起重资质澳洲认可吗？**
答：不直接认可。需通过TRA评估（12~18个月），再取得澳洲HRWL方可合法操作。

**问：索具工/起重指挥会被机器人替代吗？**
答：极低。现场安全判断和应急处置高度依赖人工，短期内无替代方案。

**问：澳洲索具工有年龄限制吗？**
答：法律无上限。矿业FIFO通常要求有现场经验，40岁以上走TRA互认同样有效。

**问：需要大学学历吗？**
答：不需要。DG/RB证书培训门槛较低，重要的是现场经验和安全意识。

**问：DG和RB证书难考吗？**
答：DG较容易，1~5天培训+考核；RB需更多现场经验和荷载计算知识，难度中等。

**问：起重指挥/索具工和起重机操作员哪个更适合移民？**
答：两者PR路径相近，薪资相当。起重机操作员岗位更稳定；索具工灵活配合多种项目，矿业FIFO更活跃。详见「索具工 vs 起重机操作员」职业比较板块（即将上线）。
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
        print("[all tables] done")
    out=os.path.join(os.path.dirname(__file__),"..","career-contents","au")
    slug=re.sub(r'-+','-',re.sub(r'[^a-z0-9-]','',re.sub(r'[\s/()]','-',I18N_EN["name"].lower())))
    with open(os.path.join(out,f"{slug}.md"),"w",encoding="utf-8") as f: f.write(MARKDOWN.strip()+"\n")
    print(f"[markdown] {slug}.md\n[OK] 起重指挥/索具工入库完成")

if __name__=="__main__": run()
