"""Building Inspector (312116) 建筑检查员 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "312116", "anzsco_title": "Building Inspector",
    "category": "技术", "workforce_size": 10000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Residential Building Approvals","Commercial Construction Compliance","Post-Disaster Structural Assessment","Private Building Certifier Market"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "建筑检查员",
    "summary": "建筑检查员（Building Inspector）负责在建筑施工各阶段进行合规检查，确保符合建筑规范（NCC）和地方法规要求。澳大利亚住宅建设繁荣带动持证检查员需求，加上政府监管趋严，私人认证师（Private Certifier）市场快速增长。",
    "forecast_note": "住宅建设计划（120万套，至2029年）带动大量合规检查需求。各州建筑法规改革（NCC 2022/2025能效升级）增加检查内容。JSA确认短缺（2025）。",
    "trend_summary": "私人建筑认证师（Private Building Certifier）市场在NSW/QLD/VIC快速增长，持证检查员自营收入可观。无人机和数字平台辅助远程检查逐步普及。"}
I18N_EN = {"locale": "en", "name": "Building Inspector",
    "summary": "Building Inspectors carry out compliance inspections at all stages of construction to ensure adherence to the National Construction Code (NCC) and local regulations. Classified under ANZSCO 312116, demand is driven by Australia's housing construction boom and tightening regulatory requirements.",
    "forecast_note": "Federal housing target (1.2M homes by 2029) generates high inspection volumes. NCC 2022/2025 energy efficiency upgrades add new inspection requirements. JSA confirms shortage.",
    "trend_summary": "Private Building Certifier market expanding rapidly in NSW/QLD/VIC. Licensed inspectors operating independently earn strong incomes. Drone and digital platform tools supplementing inspections."}
EDUCATION = [
    {"stage": "Certificate IV in Building and Construction (Building)", "duration": "12~18个月", "cost_min": 3000, "cost_max": 10000, "cost_note": "TAFE或RTO；本地学生补贴后更低", "sort_order": 0},
    {"stage": "Building Inspector Licence（各州单独颁发）", "duration": "含在学习中或考试获取", "cost_min": 400, "cost_max": 1200, "cost_note": "各州持证费用不同", "sort_order": 1},
    {"stage": "海外资质互认（Vetassess）", "duration": "3~6个月", "cost_min": 800, "cost_max": 1500, "cost_note": "技能评估费", "sort_order": 2},
    {"stage": "WHS White Card", "duration": "1天", "cost_min": 50, "cost_max": 150, "cost_note": "工地强制", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate IV in Building and Construction", "issuer": "TAFE / RTO", "note": "执业基础资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "State Building Inspector Licence", "issuer": "各州建筑监管机构", "note": "强制持证执业", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 2},
    {"qual_name": "Vetassess Skills Assessment", "issuer": "Vetassess", "note": "海外学历移民评估", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 150, "count_max": 350, "note": "全国，政府和私人认证公司均有"},
    {"platform": "Indeed", "count_min": 80, "count_max": 200, "note": "含私人认证师职位"},
    {"platform": "LinkedIn", "count_min": 50, "count_max": 130, "note": "偏政府和咨询公司"},
]
SALARIES = [
    {"experience": "初级检查员（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "政府地方议会（Council）", "sort_order": 0},
    {"experience": "中级检查员（3~7年）", "salary_min": 85000, "salary_max": 110000, "salary_note": "Seek均值约$40~$50/hr（2026）", "sort_order": 1},
    {"experience": "资深 / 私人认证师（7年+）", "salary_min": 110000, "salary_max": 150000, "salary_note": "私人认证公司或自营", "sort_order": 2},
    {"experience": "建筑认证师经理 / 顾问", "salary_min": 130000, "salary_max": 180000, "salary_note": "大型认证公司或独立执业", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "积分制独立移民", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "NCC建筑规范学习量大，但有实操经验者上手快"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "Certificate IV 1~1.5年 + 州持证"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "州持证考试+Vetassess评估"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "住宅建设旺盛，合规检查需求持续，短缺明确"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "持证检查员供不应求"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "现场+办公室混合，报告撰写量大"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位$85k~$110k；私人认证师可达$150k+"},
    {"dimension": "future_prospect",          "label_zh": "佳",   "stars": 4, "note": "住宅和商业建设长期旺盛，私人认证市场扩大"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "现场判断和合规责任需人工，AI辅助工具在普及"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "Vetassess评估+州持证+英语"},
]
SUITABILITY_FIT = [
    "有建筑施工、工程监理或质检背景，目标技能移民来澳",
    "细心严谨，熟悉建筑规范，有意转向合规检查领域",
    "考虑未来注册私人认证师，自营收入弹性大",
]
SUITABILITY_UNFIT = [
    "完全没有建筑或施工经验（规范学习门槛较高）",
    "不擅长书面报告撰写（检查报告是日常核心工作）",
    "期望快速低门槛入行",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 312116 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Building Inspector 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/building-inspector-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "Vetassess", "content": "技能评估", "url": "https://www.vetassess.com.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲建筑检查员工资多少？", "answer": "中级建筑检查员年薪约 $85,000~$110,000（约$40~$50/hr）。私人认证师自营可达 $110,000~$150,000+。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲建筑检查员容易找工作吗？", "answer": "容易。住宅建设旺盛，Seek挂牌150~350个职位，JSA确认持续短缺。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内建筑监理经验澳洲认可吗？", "answer": "需通过Vetassess技能评估。有NCC或AS建筑规范知识者评估更顺利。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "建筑检查员会被AI取代吗？", "answer": "较低。现场合规判断和法律责任需持证人员，AI辅助工具（无人机/数字平台）是效率提升而非替代。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate IV即可入行，有建筑背景者快速取证。"},
]
MARKDOWN = """# 建筑检查员（Building Inspector）职业分析 · 澳大利亚

**职业代码：312116 – Building Inspector。**

建筑检查员负责在建筑施工各阶段进行合规检查，确保符合NCC建筑规范和地方法规。澳大利亚住宅建设繁荣带动持证检查员需求，私人认证师（Private Certifier）市场快速增长。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** NCC建筑规范学习量大，有施工经验者上手快。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Certificate IV in Building and Construction | 12~18个月 | $3,000~$10,000（本地补贴后更低） |
| 各州 Building Inspector Licence | 含在学习中或考试 | $400~$1,200 |
| 海外资质互认（Vetassess） | 3~6个月 | $800~$1,500 |
| WHS White Card | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。**

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate IV in Building and Construction | TAFE / RTO | 执业基础资质 |
| State Building Inspector Licence | 各州建筑监管机构 | 强制持证执业 |
| White Card | 各州SafeWork | 工地强制 |
| Vetassess Skills Assessment | Vetassess | 海外学历移民 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：高（★★★★☆）。** 住宅建设旺盛，合规检查需求持续增长，JSA确认短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 150~350 个 | 全国，政府和私人认证公司均有 |
| Indeed | 80~200 个 | 含私人认证师职位 |
| LinkedIn | 50~130 个 | 偏政府和咨询公司 |

**竞争度：较低（★★☆☆☆）。** 持证检查员供不应求。

**工作强度：中等（★★★☆☆）。** 现场+办公室混合，检查报告撰写量大。

---

## 4. 薪资范围

**收入水平：中高（★★★★☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 初级检查员（0~3年） | $65,000~$85,000 | 政府地方议会（Council） |
| 中级检查员（3~7年） | $85,000~$110,000 | 均值约$40~$50/hr（2026） |
| 资深 / 私人认证师（7年+） | $110,000~$150,000 | 私人认证公司或自营 |
| 建筑认证经理 / 顾问 | $130,000~$180,000 | 大型认证公司或独立执业 |

---

## 5. 职业前景

**未来前景：佳（★★★★☆）。** 住宅和商业建设长期旺盛，私人认证市场扩大，持证检查员自营收入弹性大。

---

## 6. AI 替代风险

**AI风险：较低（★★☆☆☆）。** 现场合规判断和法律责任需持证人员，无人机辅助检查是效率工具而非替代。

---

## 7. 移民路径

**PR友好度：高（★★★★☆）。** CSOL在列，多签证路径可选。

| 签证类别 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临居 | 雇主担保，最长4年 |
| 186 ENS | 永居 | 直接永居 |
| 189 Skilled Independent | 永居 | 积分制独立移民 |
| 190 Skilled Nominated | 永居 | 州提名加5分 |

---

## 8. 谁适合学建筑检查员？

- 有建筑施工、工程监理或质检背景，目标技能移民来澳
- 细心严谨，熟悉建筑规范，有意转向合规检查领域
- 考虑未来注册私人认证师，自营收入弹性大

## 谁不适合学建筑检查员？

- 完全没有建筑或施工经验
- 不擅长书面报告撰写
- 期望快速低门槛入行

---

## 9. 常见问题

**澳洲建筑检查员工资多少？**
中级建筑检查员年薪约 $85,000~$110,000（约$40~$50/hr）。私人认证师自营可达 $110,000~$150,000+。

**澳洲建筑检查员容易找工作吗？**
容易。住宅建设旺盛，Seek挂牌150~350个职位，JSA确认持续短缺。

**国内建筑监理经验澳洲认可吗？**
需通过Vetassess技能评估。有NCC建筑规范知识者评估更顺利。

**建筑检查员会被AI取代吗？**
较低。现场合规判断和法律责任需持证人员，AI辅助工具是效率提升而非替代。

---

*数据来源：JSA Labour Market Insights、Seek AU、Vetassess、Department of Home Affairs CSOL（2025-2026）*
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
    print("[OK] 建筑检查员（Building Inspector）入库+Markdown完成")

if __name__ == "__main__":
    run()
