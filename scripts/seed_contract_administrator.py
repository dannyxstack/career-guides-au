"""Contract Administrator (511112) 合同管理员 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()

OCCUPATION = {
    "anzsco_code": "511112", "anzsco_title": "Contract Administrator",
    "category": "专业", "workforce_size": 25000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Construction & Infrastructure Projects","Government Procurement","IT & Professional Services Contracts","Defence & Mining Projects"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "合同管理员",
    "summary": "合同管理员（Contract Administrator）负责起草、谈判、执行和监控各类商业合同，确保项目合规和成本控制。澳大利亚大型建设和政府采购项目旺盛，加上合同法律复杂度高，合格的合同管理员供不应求。",
    "forecast_note": "联邦政府采购和基建合同管理需求旺盛（2025-2029）。建筑和工程行业合同管理员需求量最大，数字化合同管理（CLM平台）成为核心技能。",
    "trend_summary": "合同生命周期管理（CLM）平台（如Ironclad/Agiloft）普及，但合同谈判和风险条款判断仍是核心人工技能。有法律背景的合同管理员溢价明显。"}
I18N_EN = {"locale": "en", "name": "Contract Administrator",
    "summary": "Contract Administrators draft, negotiate, execute and monitor commercial contracts across construction, government and professional services sectors. Classified under ANZSCO 511112, they are in sustained demand driven by Australia's major project pipeline and complex procurement landscape.",
    "forecast_note": "Federal government procurement and major infrastructure contracts (2025-2029) drive demand. Construction and engineering sectors have the highest CA volumes. CLM platforms becoming core skill.",
    "trend_summary": "Contract Lifecycle Management (CLM) platforms gaining adoption, but negotiation and risk clause interpretation remain core human skills. Legal background commands salary premium."}
EDUCATION = [
    {"stage": "Bachelor of Commerce / Law / Construction Management", "duration": "3年（全日制）", "cost_min": 20000, "cost_max": 40000, "cost_note": "澳洲大学学费；国际生每年约$30,000~$40,000", "sort_order": 0},
    {"stage": "Certificate IV in Procurement and Contracting", "duration": "6~12个月", "cost_min": 3000, "cost_max": 8000, "cost_note": "职业培训路径；TAFE或RTO", "sort_order": 1},
    {"stage": "Certified Practising Contracts Manager (CPCM)", "duration": "2年工作经验后申请", "cost_min": 500, "cost_max": 1500, "cost_note": "AIPM认证费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Commerce / Law / Construction Mgmt", "issuer": "澳洲认可大学", "note": "入行主流学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Certified Practising Contracts Manager (CPCM)", "issuer": "AIPM", "note": "行业认可专业证书", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "CIPSA / MCIPS（采购方向）", "issuer": "Chartered Institute of Procurement & Supply", "note": "政府采购和供应链方向", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 500, "count_max": 1000, "note": "全国，建筑/政府/IT均有"},
    {"platform": "Indeed", "count_min": 300, "count_max": 600, "note": "含合规和采购类"},
    {"platform": "LinkedIn", "count_min": 300, "count_max": 700, "note": "白领职位，LinkedIn活跃"},
]
SALARIES = [
    {"experience": "初级合同管理员（0~3年）", "salary_min": 65000, "salary_max": 85000, "salary_note": "建筑或政府部门", "sort_order": 0},
    {"experience": "中级合同管理员（3~7年）", "salary_min": 85000, "salary_max": 115000, "salary_note": "Seek均值约$90,000~$110,000（2026）", "sort_order": 1},
    {"experience": "资深合同经理（7年+）", "salary_min": 115000, "salary_max": 160000, "salary_note": "大型基建/国防项目", "sort_order": 2},
    {"experience": "合同总监 / 法律顾问", "salary_min": 150000, "salary_max": 220000, "salary_note": "跨国企业或政府高级职位", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "积分制独立移民", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "合同法、风险管理和谈判技巧学习量大"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "大学3年+2~3年工作经验获专业认证"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CPCM/CIPSA需工作经验，无笔试门槛"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "建筑+政府+IT全行业需求旺盛"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "有法律或工程背景者竞争力强"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "办公室为主，谈判截止前强度大"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中位$85k~$115k；资深/顾问$160k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "基建和政府采购长期旺盛，CLM技能提升价值"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "CLM平台和AI合同审查在普及，但谈判仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列，189/190/482均可"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "Vetassess评估+英语+积分"},
]
SUITABILITY_FIT = [
    "有法律、工程或商务背景，目标技能移民来澳",
    "擅长谈判和文件管理，细心谨慎",
    "有意在建筑、政府或国防采购领域发展",
]
SUITABILITY_UNFIT = [
    "不喜欢大量文件阅读和合同条款审核",
    "完全没有商务或法律背景（起点低）",
    "期望完全户外体力工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 511112 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Contract Administrator 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/contract-administrator-jobs"},
    {"source_name": "AIPM", "content": "澳洲项目管理协会 CPCM认证", "url": "https://www.aipm.com.au/"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲合同管理员工资多少？", "answer": "中级合同管理员年薪约 $85,000~$115,000。资深合同经理和法律顾问可达 $150,000~$220,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲合同管理员容易找工作吗？", "answer": "容易。建筑、政府和IT行业均有需求，Seek挂牌500~1,000个职位，有相关经验者入职快。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内合同管理经验澳洲认可吗？", "answer": "需通过Vetassess技能评估。有英文合同处理经验和相关学历者评估通过率较高。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "合同管理员会被AI取代吗？", "answer": "部分。AI合同审查工具在普及，但风险条款谈判和争议解决仍是核心人工技能。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要法律学位吗？", "answer": "不一定。商务、工程、建筑管理学位均可入行，法律背景有薪资溢价。"},
]
MARKDOWN = """# 合同管理员（Contract Administrator）职业分析 · 澳大利亚

**职业代码：511112 – Contract Administrator。**

合同管理员负责起草、谈判、执行和监控各类商业合同。澳大利亚大型建设和政府采购项目旺盛，加上合同法律复杂度高，合格的合同管理员供不应求，是商务白领中薪资增长空间较大的职业之一。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中高（★★★★☆）。** 合同法、风险管理和谈判技巧学习量大。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| Bachelor of Commerce / Law / Construction Management | 3年全日制 | $20,000~$40,000（国际生每年$30,000~$40,000） |
| Certificate IV in Procurement and Contracting | 6~12个月 | $3,000~$8,000 |
| CPCM 认证（AIPM） | 2年工作经验后 | $500~$1,500 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。** 专业认证需工作经验，无高难度笔试。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Bachelor of Commerce / Law | 澳洲认可大学 | 主流入行学历 |
| CPCM | AIPM | 行业认可专业证书 |
| MCIPS | CIPSA | 政府采购方向 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** 建筑、政府和IT行业全面旺盛，JSA确认持续短缺（2025）。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 500~1,000 个 | 全国，建筑/政府/IT均有 |
| Indeed | 300~600 个 | 含合规和采购类 |
| LinkedIn | 300~700 个 | 白领职位，平台活跃 |

**竞争度：中等（★★★☆☆）。** 有法律或工程双背景者竞争力强。

**工作强度：中等（★★★☆☆）。** 办公室为主，合同谈判截止期前强度会提升。

---

## 4. 薪资范围

**收入水平：高（★★★★☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 初级合同管理员（0~3年） | $65,000~$85,000 | 建筑或政府部门 |
| 中级合同管理员（3~7年） | $85,000~$115,000 | 均值约$90,000~$110,000（2026） |
| 资深合同经理（7年+） | $115,000~$160,000 | 大型基建/国防项目 |
| 合同总监 / 法律顾问 | $150,000~$220,000 | 跨国企业或政府高级职位 |

---

## 5. 职业前景

**未来前景：极佳（★★★★★）。** 联邦基建和政府采购长期旺盛，CLM平台技能成为加分项，职业天花板高。

---

## 6. AI 替代风险

**AI风险：中等（★★★☆☆）。** CLM平台和AI合同审查工具在普及，但风险条款谈判和争议解决仍需人工处理。

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

## 8. 谁适合学合同管理员？

- 有法律、工程或商务背景，目标技能移民来澳
- 擅长谈判和文件管理，细心谨慎
- 有意在建筑、政府或国防采购领域发展

## 谁不适合学合同管理员？

- 不喜欢大量文件阅读和合同条款审核
- 完全没有商务或法律背景
- 期望完全户外体力工作

---

## 9. 常见问题

**澳洲合同管理员工资多少？**
中级合同管理员年薪约 $85,000~$115,000。资深合同经理和法律顾问可达 $150,000~$220,000。

**澳洲合同管理员容易找工作吗？**
容易。建筑、政府和IT行业均有需求，Seek挂牌500~1,000个职位。

**国内合同管理经验澳洲认可吗？**
需通过Vetassess技能评估。有英文合同处理经验者评估通过率较高。

**合同管理员会被AI取代吗？**
部分。AI合同审查工具在普及，但风险条款谈判和争议解决仍是核心人工技能。

---

*数据来源：JSA Labour Market Insights、AIPM、Seek AU、Department of Home Affairs CSOL（2025-2026）*
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
    print("[OK] 合同管理员（Contract Administrator）入库+Markdown完成")

if __name__ == "__main__":
    run()
