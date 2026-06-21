"""
Scaffolder (821712) 脚手架工
数据来源：CFMEU EBA 2026、Seek/Indeed/Glassdoor、JSA、Dept of Home Affairs (2025-2026)
"""
import sys, os, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "821712", "anzsco_title": "Scaffolder",
    "category": "技工", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential High-Rise Construction","Civil Infrastructure","Industrial Maintenance (Oil, Gas, Mining)","Renewable Energy Projects"], ensure_ascii=False),
}
I18N_ZH = {
    "locale": "zh-CN", "name": "脚手架工",
    "summary": "脚手架工（Scaffolder）负责搭建和拆除各类临时工作平台（脚手架），为建筑工人在高处施工提供安全支撑，广泛服务于住宅、商业建筑、工业设施和矿业项目。澳大利亚长期面临脚手架工短缺，是技工移民的可靠路径之一。",
    "forecast_note": "建筑技工类持续短缺，技工岗位填补率仅54.3%（JSA 2025）。高层住宅建设繁荣和工业维护需求驱动需求增长，澳洲政府住宅计划至2029年新增120万套。",
    "trend_summary": "可调式模块化脚手架系统提升效率，但搭拆操作仍依赖人工。工业关停检修（Shutdown）项目需求周期性爆发，矿业/炼油需求稳定。",
}
I18N_EN = {
    "locale": "en", "name": "Scaffolder",
    "summary": "Scaffolders erect and dismantle temporary work platforms to support construction and maintenance work at height. Classified under ANZSCO 821712, they are in persistent shortage across residential, industrial and mining sectors in Australia.",
    "forecast_note": "JSA identifies construction trades as persistently undersupplied. Skill Level 3/4 fill rate at 54.3%. Federal Housing Future Fund targets 1.2M homes by 2029.",
    "trend_summary": "Modular scaffold systems improve efficiency but assembly remains manual. Industrial shutdown projects drive periodic demand spikes in mining and oil & gas.",
}
EDUCATION = [
    {"stage": "学徒制 Apprenticeship（Cert III in Scaffolding CPC30321）", "duration": "42~48个月", "cost_min": 0, "cost_max": 2500, "cost_note": "各州差异；NSW免费；WA约$1,500~$2,500；工具费约$800~$1,500", "sort_order": 0},
    {"stage": "海外资质互认（TRA Job Ready Program）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估+实习期行政费", "sort_order": 1},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制资质", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Scaffolding (CPC30321)", "issuer": "TAFE / RTO", "note": "执业基础资质，含基础/中级/高级脚手架", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "High Risk Work Licence – Scaffolding (SB/SI/SA)", "issuer": "SafeWork / WorkSafe 各州", "note": "基础(SB)/中级(SI)/高级(SA)三级，依施工类型选取", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民必须", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 600, "note": "全国，含矿业shutdown和住宅工程"},
    {"platform": "Indeed", "count_min": 150, "count_max": 350, "note": "含承包商和劳务外包"},
    {"platform": "LinkedIn", "count_min": 60, "count_max": 180, "note": "偏工业维修和矿业直招"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 28000, "salary_max": 55000, "salary_note": "Fair Work Award", "sort_order": 0},
    {"experience": "初级脚手架工（持证后1~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "住宅和商业工程", "sort_order": 1},
    {"experience": "中级脚手架工（3~8年）", "salary_min": 90000, "salary_max": 115000, "salary_note": "Vic EBA 2026 Grade 2=$58.46/hr；全国均值约$45/hr", "sort_order": 2},
    {"experience": "资深 / 带班（8年+）", "salary_min": 115000, "salary_max": 140000, "salary_note": "含加班和轮班津贴", "sort_order": 3},
    {"experience": "工业shutdown / 矿业FIFO（WA/QLD）", "salary_min": 130000, "salary_max": 185000, "salary_note": "Shutdown项目日薪制，FIFO含住宿餐饮", "sort_order": 4},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保最长4年，可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名永居，加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名，加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "体力为主，技术在结构计算和荷载判断"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年；三级证书逐步取得"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "High Risk Work Licence SB/SI/SA三级"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "住宅、工业维修双驱动，长期短缺"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，工业shutdown岗尤其抢手"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "高空重体力，搬运管材/脚手板，安全意识要求高"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位$90k~$115k；shutdown/FIFO可达$185k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "建设繁荣+工业维护+绿能项目长期需求"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "高空复杂结构搭建，无机器人替代方案"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，多签证路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语要求"},
]
SUITABILITY_FIT = [
    "有施工/高空作业背景，希望通过技能移民来澳",
    "接受重体力户外高空作业，对高处工作无恐惧",
    "目标是矿业FIFO或工业shutdown高薪岗",
    "计划通过190州提名路线获PR",
]
SUITABILITY_UNFIT = [
    "有恐高症或平衡障碍",
    "不愿从事重体力劳动",
    "期望室内或管理类工作",
]
SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 821712 Scaffolder 短缺数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "CFMEU Victoria EBA 2026", "content": "Grade 2 = $58.46/hr", "url": "https://vic.cfmeu.org/wp-content/uploads/2026/02/2026-Onsite-EBA-Rates.pdf"},
    {"source_name": "Seek / Indeed AU", "content": "职位挂牌量及薪资（2026）", "url": "https://www.seek.com.au/scaffolder-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲脚手架工工资多少？", "answer": "中级脚手架工年薪约 $90,000~$115,000；工业shutdown和矿业FIFO可达 $130,000~$185,000。学徒期约 $28,000~$55,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲脚手架工容易找工作吗？", "answer": "容易。全国持续短缺，Seek常年挂牌300~600个职位。尤其WA矿业和大型工业维修岗需求旺盛。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内脚手架经验澳洲认可吗？", "answer": "不直接认可，需通过TRA评估（12~18个月）。还须取得澳洲High Risk Work Licence（SB/SI/SA）才能合法操作。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "脚手架工会被机器人替代吗？", "answer": "极低。高空复杂结构搭建高度依赖人工判断和体力操作，目前无成熟自动化方案。"},
    {"faq_type": "age_limit", "sort_order": 4, "question": "澳洲脚手架工有年龄限制吗？", "answer": "法律无上限。学徒偏好35岁以下；40岁以上可走TRA互认跳过学徒期。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III即可，高中毕业即可入读TAFE学徒课程。"},
    {"faq_type": "difficulty", "sort_order": 6, "question": "脚手架工难学吗？", "answer": "难度中等。关键技能是结构荷载计算、安全规范和高空平衡感。体力要求高，有高空作业经验者上手较快。"},
    {"faq_type": "comparison", "sort_order": 7, "question": "脚手架工和钢筋工哪个更适合移民澳洲？", "answer": "两者PR路径相近，薪资相当。钢筋工岗位总量略多；脚手架工工业shutdown机会更多，FIFO津贴高。详见「脚手架工 vs 钢筋工」职业比较板块（即将上线）。"},
]

MARKDOWN = """# 脚手架工（Scaffolder）职业分析 · 澳大利亚

**职业代码：821712 – Scaffolder。**

脚手架工负责搭建和拆除各类临时工作平台，为建筑工人在高处施工提供安全支撑，广泛服务于住宅、商业、工业和矿业项目。澳大利亚长期面临脚手架工短缺，是技工移民的可靠路径之一。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 关键技能是结构荷载计算、安全规范和高空平衡能力。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| 学徒制 Apprenticeship（Cert III in Scaffolding CPC30321） | 42~48个月 | $0~$2,500（NSW免费；WA约$1,500~$2,500；工具费$800~$1,500） |
| 海外资质互认（TRA Job Ready Program） | 12~18个月 | $2,000~$5,000 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。** High Risk Work Licence 分三级，须逐级取得。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Scaffolding (CPC30321) | TAFE / RTO | 执业基础资质 |
| High Risk Work Licence SB/SI/SA | 各州SafeWork/WorkSafe | 基础/中级/高级，依施工类型持有 |
| White Card | 各州SafeWork | 工地强制 |
| TRA Skills Assessment | TRA | 海外学历移民必须 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 住宅建设繁荣与工业维修双线驱动，长期供不应求。技工类岗位填补率54.3%（JSA 2025），WA矿业和大型shutdown项目需求尤其旺盛。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 300~600 个 | 含矿业shutdown和住宅工程 |
| Indeed | 150~350 个 | 含承包商和劳务外包 |
| LinkedIn | 60~180 个 | 偏工业维修和矿业直招 |

**竞争度：较低（★★☆☆☆）。** 工业shutdown岗尤其抢手，提前排班常见。
**工作强度：高（★★★★☆）。** 高空重体力，搬运管材/脚手板，安全意识要求极高。

---

## 4. 收入范围（学徒 / 中级 / 资深）

| 经验水平 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $28,000~$55,000 | Fair Work Award |
| 初级（持证后1~3年） | $70,000~$90,000 | 住宅和商业工程 |
| 中级（3~8年） | $90,000~$115,000 | Vic EBA 2026 Grade 2=$58.46/hr |
| 资深 / 带班（8年+） | $115,000~$140,000 | 含加班和轮班津贴 |
| 工业shutdown / 矿业FIFO | $130,000~$185,000 | 日薪制，含住宿餐饮 |

---

## 5. 未来趋势 / AI替代概率

**AI替代风险：极低（★☆☆☆☆）。** 高空复杂结构搭建高度依赖人工判断，无成熟自动化方案。
**发展前景：极佳（★★★★★）。** 住宅建设繁荣+大型基建+绿能项目+工业维护，需求长期稳定。

---

## 6. 移民路径 / PR难度

**PR难度：中等（★★★☆☆）。** TRA评估+英语是主要门槛，但CSOL在列，签证路径充裕。

| 签证 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临时 | 雇主担保，最长4年，可转186 |
| 186 ENS | 永居 | 雇主担保永居 |
| 190 | 永居 | 州政府提名，加5分 |
| 491 | 临时转永居 | 偏远地区提名，加15分 |

**PR友好度：极高（★★★★★）。** CSOL在列，多签证路径均可用。

---

## 7. 适合人群 / 不适合人群

**谁适合学脚手架工？**
- 有施工/高空作业背景，希望通过技能移民来澳
- 接受重体力户外高空作业，对高处无恐惧
- 目标是矿业FIFO或工业shutdown高薪项目
- 计划通过190州提名获PR

**谁不适合学脚手架工？**
- 有恐高症或平衡障碍
- 不愿从事重体力劳动
- 期望室内或管理类工作

---

## 8. 数据来源

| 来源 | 内容 |
|---|---|
| Jobs and Skills Australia | ANZSCO 821712 短缺数据 |
| CFMEU Victoria EBA 2026 | Grade 2 = $58.46/hr |
| Seek / Indeed AU | 职位挂牌量及薪资（2026） |
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

脚手架工是澳洲工地最紧缺的技工之一，工业shutdown和矿业FIFO是薪资最高的方向。入行路径清晰，PR通道稳定，适合有施工经验且不惧高空工作的技术移民。

---

## 9. FAQ 常见问题

**问：澳洲脚手架工工资多少？**
答：中级年薪约 $90,000~$115,000；工业shutdown和矿业FIFO可达 $130,000~$185,000。学徒期约 $28,000~$55,000。

**问：澳洲脚手架工容易找工作吗？**
答：容易。全国持续短缺，Seek常年挂牌300~600个职位。WA矿业和大型工业维修岗需求旺盛。

**问：国内脚手架经验澳洲认可吗？**
答：不直接认可，需通过TRA评估（12~18个月）。还须取得High Risk Work Licence（SB/SI/SA）才能合法操作。

**问：脚手架工会被机器人替代吗？**
答：极低。高空复杂结构搭建高度依赖人工判断，目前无成熟自动化方案。

**问：澳洲脚手架工有年龄限制吗？**
答：法律无上限。学徒偏好35岁以下；40岁以上可走TRA互认跳过学徒期。

**问：需要大学文凭吗？**
答：不需要。Certificate III即可，高中毕业即可入读TAFE学徒课程。

**问：脚手架工难学吗？**
答：难度中等。关键是结构荷载计算、安全规范和高空平衡感。体力要求高，有高空作业经验者上手较快。

**问：脚手架工和钢筋工哪个更适合移民澳洲？**
答：两者PR路径相近，薪资相当。钢筋工岗位总量略多；脚手架工工业shutdown机会更多。详见「脚手架工 vs 钢筋工」职业比较板块（即将上线）。
"""

def run():
    import re
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO occupations (anzsco_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE anzsco_title=VALUES(anzsco_title),category=VALUES(category),
              workforce_size=VALUES(workforce_size),shortage_listed=VALUES(shortage_listed),growth_areas=VALUES(growth_areas)
        """, (OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],OCCUPATION["category"],
              OCCUPATION["workforce_size"],OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"]))
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s",(OCCUPATION["anzsco_code"],))
        occ_id = cur.fetchone()["id"]
        print(f"[occupations] id={occ_id}  {OCCUPATION['anzsco_code']} {OCCUPATION['anzsco_title']}")
        for i18n in [I18N_ZH,I18N_EN]:
            cur.execute("INSERT INTO occupations_i18n (occupation_id,locale,name,summary,forecast_note,trend_summary) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name),summary=VALUES(summary),forecast_note=VALUES(forecast_note),trend_summary=VALUES(trend_summary)",
                        (occ_id,i18n["locale"],i18n["name"],i18n["summary"],i18n["forecast_note"],i18n["trend_summary"]))
        print("[i18n] 2 locales")
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
            faq_id=cur.lastrowid
            cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'zh-CN',%s,%s) ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",(faq_id,faq["question"],faq["answer"]))
        print(f"[all tables] done")
    out_dir=os.path.join(os.path.dirname(__file__),"..","career-contents","au")
    os.makedirs(out_dir,exist_ok=True)
    slug=re.sub(r'-+',' ',re.sub(r'[^a-z0-9 ]','',re.sub(r'[/()\[\]]',' ',I18N_EN["name"].lower()))).strip().replace(' ','-')
    with open(os.path.join(out_dir,f"{slug}.md"),"w",encoding="utf-8") as f: f.write(MARKDOWN.strip()+"\n")
    print(f"[markdown] {slug}.md")
    print("\n[OK] 脚手架工（Scaffolder）入库完成")

if __name__=="__main__": run()
