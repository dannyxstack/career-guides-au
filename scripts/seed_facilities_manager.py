"""Facilities Manager (149913) 设施管理员 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "149913", "anzsco_title": "Facilities Manager",
    "category": "管理", "workforce_size": 35000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Commercial Office & Retail FM","Healthcare & Aged Care FM","Data Centre Operations","Government & Defence FM"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "设施管理员",
    "summary": "设施管理员（Facilities Manager）负责建筑物和设施的运营维护、服务协调和合规管理，确保工作环境的安全、效率和可持续性。澳大利亚商业地产和医疗健康机构对FM人才的需求旺盛，是稳定白领职业中移民友好度较高的选项。",
    "forecast_note": "商业写字楼和大型零售设施FM外包市场扩大。医疗健康和老年护理行业大量新增基础设施带动FM需求。政府和国防设施管理外包增加。JSA列为短缺（2025）。",
    "trend_summary": "智能楼宇技术（IoT/BMS）和CAFM（计算机辅助FM）平台成为FM核心工具。可持续性（ESG合规）成为FM的重要职能，绿建认证（Green Star/NABERS）知识溢价明显。"}
I18N_EN = {"locale": "en", "name": "Facilities Manager",
    "summary": "Facilities Managers oversee the operation, maintenance and service coordination of buildings and facilities to ensure safe, efficient and sustainable working environments. Classified under ANZSCO 149913, they are in sustained demand across commercial, healthcare, government and data centre sectors in Australia.",
    "forecast_note": "Commercial FM outsourcing market expanding. Healthcare and aged care new builds drive FM demand. Government and defence FM outsourcing increasing. JSA confirms shortage.",
    "trend_summary": "Smart building technology (IoT/BMS) and CAFM platforms now core FM tools. ESG compliance and green building (Green Star/NABERS) knowledge commands salary premium."}
EDUCATION = [
    {"stage": "Bachelor of Facilities Management / Property / Business", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 40000, "cost_note": "国际生每年约$25,000~$40,000", "sort_order": 0},
    {"stage": "Diploma of Facilities Management", "duration": "12~18个月", "cost_min": 5000, "cost_max": 12000, "cost_note": "TAFE或RTO；职业转型路径", "sort_order": 1},
    {"stage": "TEFMA / FMA 专业会员认证", "duration": "2~3年工作经验后", "cost_min": 500, "cost_max": 1500, "cost_note": "行业协会年费", "sort_order": 2},
    {"stage": "Vetassess 技能评估（移民）", "duration": "3~6个月", "cost_min": 800, "cost_max": 1500, "cost_note": "评估费用", "sort_order": 3},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Facilities Management / Property", "issuer": "澳洲认可大学", "note": "主流入行学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "FMA Member / TEFMA Member", "issuer": "Facility Management Association of Australia", "note": "行业认可资质", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "NABERS / Green Star 知识认证", "issuer": "NABERS / Green Building Council", "note": "ESG和可持续性方向", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "Vetassess Skills Assessment", "issuer": "Vetassess", "note": "技能移民评估", "is_mandatory": 0, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 600, "count_max": 1200, "note": "全国，商业/医疗/政府均有"},
    {"platform": "Indeed", "count_min": 300, "count_max": 700, "note": "含FM协调员职位"},
    {"platform": "LinkedIn", "count_min": 400, "count_max": 900, "note": "高活跃度，外包公司招聘多"},
]
SALARIES = [
    {"experience": "FM协调员（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "商业或政府设施", "sort_order": 0},
    {"experience": "FM专员 / 助理经理（3~7年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "Seek均值约$90,000~$110,000（2026）", "sort_order": 1},
    {"experience": "资深FM / 设施经理（7年+）", "salary_min": 115000, "salary_max": 150000, "salary_note": "大型商业或医疗设施", "sort_order": 2},
    {"experience": "FM总监 / 区域FM经理", "salary_min": 145000, "salary_max": 200000, "salary_note": "外包公司全国级别或国防FM", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "积分制独立移民", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "涉及技术、合规和管理多维度，但无单一高难度考试"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "Diploma 1~1.5年；有工程背景者转型更快"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "FMA/TEFMA会员资质需工作经验，无高难笔试"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "商业/医疗/政府全面旺盛，挂牌量大"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "市场大但竞争者也多；有工程背景者有优势"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "办公室+现场混合，紧急设施故障时压力大"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中位$85k~$115k；资深和外包公司$150k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "智能楼宇+ESG合规+医疗新建，长期需求高位"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "IoT和CAFM提升效率，但设施决策和供应商管理仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列，多签证路径"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "Vetassess评估+英语+积分"},
]
SUITABILITY_FIT = [
    "有工程、物业管理、工程维保或建筑运营背景，目标技能移民来澳",
    "擅长协调多方服务供应商，处理紧急故障不慌乱",
    "有意在医疗、政府或商业地产领域长期发展",
]
SUITABILITY_UNFIT = [
    "完全没有建筑或运营管理经验",
    "不适应随时处理突发设施故障",
    "期望完全规律不变的纯办公室工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 149913 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "FMA Australia", "content": "澳洲设施管理协会", "url": "https://www.fma.com.au/"},
    {"source_name": "Seek AU", "content": "Facilities Manager 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/facilities-manager-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲设施管理员工资多少？", "answer": "FM专员年薪约 $85,000~$115,000。资深设施经理和外包公司区域级别可达 $145,000~$200,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲FM容易找工作吗？", "answer": "容易。商业、医疗和政府均有需求，Seek挂牌600~1,200个职位，是白领类挂牌量较大的职业。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内物业管理经验澳洲认可吗？", "answer": "需通过Vetassess技能评估。有大型建筑运营管理经验者评估通过率较高。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "设施管理会被AI取代吗？", "answer": "较低。IoT和CAFM平台提升效率，但供应商协调、紧急决策和ESG合规管理仍需人工。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学学位吗？", "answer": "有学历优势但非强制。Diploma路径可入行，有工程维保经验者可以RPL申请快速认证。"},
]
MARKDOWN = """# 设施管理员（Facilities Manager）职业分析 · 澳大利亚

**职业代码：149913 – Facilities Manager。**

设施管理员负责建筑物和设施的运营维护、服务协调和合规管理。澳大利亚商业地产、医疗健康和政府机构对FM人才需求旺盛，是稳定白领职业中移民友好度较高的选项。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 涉及技术、合规和管理多维度，但无单一高难度考试。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Bachelor of Facilities Management / Property | 3年全日制 | $20,000~$40,000（国际生每年$25,000~$40,000） |
| Diploma of Facilities Management | 12~18个月 | $5,000~$12,000 |
| FMA/TEFMA 专业会员认证 | 2~3年工作经验后 | $500~$1,500 |
| Vetassess 技能评估（移民） | 3~6个月 | $800~$1,500 |

---

## 2. 考证难度 / 从业资质

**考证难度：较低（★★☆☆☆）。** FMA/TEFMA会员资质需工作经验，无高难笔试。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Bachelor of FM / Property | 澳洲认可大学 | 主流入行学历 |
| FMA Member | Facility Management Association | 行业认可资质 |
| NABERS / Green Star | NABERS / GBCA | ESG和可持续性方向 |
| Vetassess Skills Assessment | Vetassess | 技能移民评估 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 商业、医疗和政府全面旺盛，Seek挂牌量位居白领类前列，JSA确认短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 600~1,200 个 | 全国，商业/医疗/政府均有 |
| Indeed | 300~700 个 | 含FM协调员职位 |
| LinkedIn | 400~900 个 | 高活跃度，外包公司招聘多 |

**竞争度：中等（★★★☆☆）。** 市场大但竞争者也多，有工程或建筑运营背景者有明显优势。

**工作强度：中等（★★★☆☆）。** 办公室+现场混合，紧急设施故障时压力较大。

---

## 4. 薪资范围

**收入水平：高（★★★★☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| FM协调员（0~3年） | $65,000~$85,000 | 商业或政府设施 |
| FM专员 / 助理经理（3~7年） | $85,000~$115,000 | 均值约$90,000~$110,000（2026） |
| 资深FM / 设施经理（7年+） | $115,000~$150,000 | 大型商业或医疗设施 |
| FM总监 / 区域FM经理 | $145,000~$200,000 | 外包公司全国级别或国防FM |

---

## 5. 职业前景

**未来前景：极佳（★★★★★）。** 智能楼宇技术、ESG合规需求和医疗新建推动FM长期高位需求，职业天花板高。

---

## 6. AI 替代风险

**AI风险：较低（★★☆☆☆）。** IoT和CAFM平台提升效率，但供应商协调、紧急决策和ESG合规管理仍需人工处理。

---

## 7. 移民路径

**PR友好度：高（★★★★☆）。** CSOL在列，189/190/482均可申请。

| 签证类别 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临居 | 雇主担保，最长4年 |
| 186 ENS | 永居 | 直接永居 |
| 189 Skilled Independent | 永居 | 积分制独立移民 |
| 190 Skilled Nominated | 永居 | 州提名加5分 |

---

## 8. 谁适合学设施管理员？

- 有工程、物业管理、工程维保或建筑运营背景，目标技能移民来澳
- 擅长协调多方服务供应商，处理紧急故障不慌乱
- 有意在医疗、政府或商业地产领域长期发展

## 谁不适合学设施管理员？

- 完全没有建筑或运营管理经验
- 不适应随时处理突发设施故障
- 期望完全规律不变的纯办公室工作

---

## 9. 常见问题

**澳洲设施管理员工资多少？**
FM专员年薪约 $85,000~$115,000。资深设施经理和外包公司区域级别可达 $145,000~$200,000。

**澳洲FM容易找工作吗？**
容易。商业、医疗和政府均有需求，Seek挂牌600~1,200个职位，是白领类挂牌量较大的职业。

**国内物业管理经验澳洲认可吗？**
需通过Vetassess技能评估。有大型建筑运营管理经验者评估通过率较高。

**设施管理会被AI取代吗？**
较低。IoT和CAFM平台提升效率，但供应商协调、紧急决策和ESG合规管理仍需人工。

---

*数据来源：JSA Labour Market Insights、FMA Australia、Seek AU、Department of Home Affairs CSOL（2025-2026）*
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
    print("[OK] 设施管理员（Facilities Manager）入库+Markdown完成")

if __name__ == "__main__":
    run()
