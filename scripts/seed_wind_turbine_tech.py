"""Wind Turbine Technician (342114) 风力涡轮机技术员 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "342114", "anzsco_title": "Wind Turbine Technician",
    "category": "技工", "workforce_size": 8000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Onshore Wind Farm O&M","Offshore Wind (emerging)","Wind+Storage Hybrid Projects","Regional & Remote Wind"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "风力涡轮机技术员",
    "summary": "风力涡轮机技术员（Wind Turbine Technician）负责陆上和海上风力涡轮机的安装、运营维护和故障排除。澳大利亚清洁能源目标驱动风电装机快速增长，技术员严重短缺，FIFO模式收入更可观。",
    "forecast_note": "联邦清洁能源目标（2030年82%）和各州大型风电项目快速推进。海上风电（Bass Strait）2026年起进入建设阶段。风电技术员需求年增约20%。",
    "trend_summary": "海上风电将在2027-2030年创造大量新技术员需求，薪资比陆上高20~30%。已有陆上经验者可优先转型海上方向。"}
I18N_EN = {"locale": "en", "name": "Wind Turbine Technician",
    "summary": "Wind Turbine Technicians install, commission, operate and maintain onshore and offshore wind turbines. Classified under ANZSCO 342114, Australia's clean energy targets and rapid wind farm expansion create significant demand for qualified technicians.",
    "forecast_note": "Federal clean energy target (82% by 2030) and state wind projects drive fast capacity expansion. Offshore wind entering construction phase from 2026. Technician demand growing ~20% annually.",
    "trend_summary": "Offshore wind will create large technician demand 2027-2030, paying 20-30% more than onshore. Experienced onshore techs well positioned to transition."}
EDUCATION = [
    {"stage": "Certificate III in Electrotechnology Electrician (学徒)", "duration": "42~48个月", "cost_min": 0, "cost_max": 3000, "cost_note": "电工基础路径", "sort_order": 0},
    {"stage": "GWO Basic Safety Training (BST)", "duration": "5天", "cost_min": 1500, "cost_max": 3000, "cost_note": "全球风能组织基础安全，行业强制", "sort_order": 1},
    {"stage": "OEM厂商认证（Vestas/Siemens Gamesa等）", "duration": "2~8周", "cost_min": 2000, "cost_max": 6000, "cost_note": "雇主通常负担；大型风场必备", "sort_order": 2},
    {"stage": "Working at Heights + 海上GWO模块", "duration": "3~5天", "cost_min": 500, "cost_max": 1500, "cost_note": "海上方向附加", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Electrical Licence (A Grade)", "issuer": "各州电气监管机构", "note": "主流入行路径", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "GWO Basic Safety Training", "issuer": "Global Wind Organisation", "note": "行业标准安全培训，全球通用", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "OEM 认证（Vestas/Siemens等）", "issuer": "各OEM厂商", "note": "大型风场必备", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Working at Heights / Confined Space", "issuer": "各州", "note": "风机塔筒作业必备", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 150, "count_max": 350, "note": "全国，SA/VIC/QLD风场集中"},
    {"platform": "Indeed", "count_min": 80, "count_max": 200, "note": "含FIFO职位"},
    {"platform": "LinkedIn", "count_min": 60, "count_max": 150, "note": "OEM和运营商直招"},
]
SALARIES = [
    {"experience": "初级技术员（0~2年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "陆上风场运维", "sort_order": 0},
    {"experience": "中级技术员（2~5年）", "salary_min": 90000, "salary_max": 120000, "salary_note": "约$42~$55/hr；含FIFO津贴", "sort_order": 1},
    {"experience": "资深技术员 / 主管（5年+）", "salary_min": 115000, "salary_max": 150000, "salary_note": "多机型OEM认证溢价", "sort_order": 2},
    {"experience": "海上风电技术员（2027+）", "salary_min": 130000, "salary_max": 180000, "salary_note": "Bass Strait项目预估；比陆上高20~30%", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远风场加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "电气+机械+液压多系统，高空作业技术要求高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "电工学徒4年+GWO+OEM培训"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "电气持证+GWO+OEM认证"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "年增20%，清洁能源目标驱动"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "技术员严重短缺，OEM主动争抢"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "高空作业（80~120m），FIFO制，恶劣天气挑战"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中位$90k~$120k；FIFO和海上可达$150k~$180k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "海上风电2027+将创造大量高薪新职位"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场机械维护和高空故障排除无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列，偏远风场491加分"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA/电气持证+GWO+英语"},
]
SUITABILITY_FIT = [
    "已持澳洲电工证（A Grade），希望转入高增长可再生能源行业",
    "不惧高空FIFO作业，追求高薪和清晰的海上风电职业路径",
    "有机械维修或电气背景，目标技能移民来澳",
]
SUITABILITY_UNFIT = [
    "恐高（风机塔筒高度80~120m）",
    "不接受偏远地区FIFO工作模式",
    "期望完全城市内稳定工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 342114 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Clean Energy Council", "content": "澳洲风能行业数据", "url": "https://www.cleanenergycouncil.org.au/"},
    {"source_name": "Seek AU", "content": "Wind Turbine Technician 薪资（2026）", "url": "https://www.seek.com.au/wind-turbine-technician-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲风力涡轮机技术员工资多少？", "answer": "中级技术员年薪约 $90,000~$120,000（含FIFO津贴）。海上风电技术员预估 $130,000~$180,000（2027年后）。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲风机技术员容易找工作吗？", "answer": "非常容易。需求年增约20%，技术员严重短缺，持证后OEM和运营商主动争抢。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内风机维护经验澳洲认可吗？", "answer": "需TRA评估获取澳洲电气资质，再考GWO基础安全培训。OEM认证经验有加分。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "风机技术员会被机器人替代吗？", "answer": "极低。高空机械维护和故障排除需现场专业判断，塔筒内作业复杂，无成熟自动化方案。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。电工执照+GWO认证即可入行，OEM培训通常由雇主提供。"},
]
MARKDOWN = """# 风力涡轮机技术员（Wind Turbine Technician）职业分析 · 澳大利亚

**职业代码：342114 – Wind Turbine Technician。**

风力涡轮机技术员负责陆上和海上风力涡轮机的安装、运营维护和故障排除。澳大利亚清洁能源目标驱动风电装机快速增长，技术员严重短缺，海上风电（2027年后）将提供大量高薪职位。

---

## 1. 教育路径 / 周期 / 费用

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| 电工学徒（基础路径） | 42~48个月 | $0~$3,000 |
| GWO Basic Safety Training | 5天 | $1,500~$3,000 |
| OEM厂商认证（Vestas/Siemens等） | 2~8周 | $2,000~$6,000（雇主通常负担） |
| Working at Heights + 海上GWO模块 | 3~5天 | $500~$1,500 |

---

## 2. 薪资范围

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 初级技术员（0~2年） | $70,000~$90,000 | 陆上风场运维 |
| 中级技术员（2~5年） | $90,000~$120,000 | 约$42~$55/hr；含FIFO津贴 |
| 资深技术员 / 主管（5年+） | $115,000~$150,000 | 多机型OEM认证溢价 |
| 海上风电技术员（2027+） | $130,000~$180,000 | Bass Strait项目预估 |

---

## 3. 谁适合学风力涡轮机技术员？

- 已持澳洲电工证（A Grade），希望转入高增长可再生能源行业
- 不惧高空FIFO作业，追求高薪和清晰的海上风电职业路径
- 有机械维修或电气背景，目标技能移民来澳

## 谁不适合学风力涡轮机技术员？

- 恐高（风机塔筒高度80~120m）
- 不接受偏远地区FIFO工作模式
- 期望完全城市内稳定工作

---

## 4. 常见问题

**澳洲风机技术员工资多少？**
中级技术员年薪约 $90,000~$120,000（含FIFO津贴）。海上风电预估 $130,000~$180,000（2027年后）。

**澳洲风机技术员容易找工作吗？**
非常容易。需求年增约20%，技术员严重短缺，持证后主动被争抢。

**风机技术员会被机器人替代吗？**
极低。高空机械维护和故障排除需现场专业判断，无成熟自动化方案。

---

*数据来源：JSA、Clean Energy Council、Seek AU、Department of Home Affairs CSOL（2025-2026）*
"""
def run():
    with get_cursor() as cur:
        cur.execute("INSERT INTO occupations (anzsco_code,occ_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE occ_code=VALUES(occ_code),anzsco_title=VALUES(anzsco_title),category=VALUES(category),workforce_size=VALUES(workforce_size),shortage_listed=VALUES(shortage_listed),growth_areas=VALUES(growth_areas)",
            (OCCUPATION["anzsco_code"],OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],OCCUPATION["category"],OCCUPATION["workforce_size"],OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"]))
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s AND country_code='AU'", (OCCUPATION["anzsco_code"],))
        occ_id = cur.fetchone()["id"]; print(f"[occupations] id={occ_id}")
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
    with open(os.path.join(out_dir, f"{slug}.md"), "w", encoding="utf-8") as f: f.write(MARKDOWN.strip()+"\n")
    print(f"[markdown] {slug}.md")
    print("[OK] 风力涡轮机技术员入库+Markdown完成")
if __name__ == "__main__": run()
