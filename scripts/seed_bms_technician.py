"""BMS Technician (342115) 楼宇自动化技术员 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "342115", "anzsco_title": "Building Automation Technician",
    "category": "技术", "workforce_size": 10000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Smart Building Retrofit","Data Centre BMS","Hospital & Healthcare BMS","Green Building NABERS Compliance"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "楼宇自动化技术员",
    "summary": "楼宇自动化技术员（BMS Technician）负责建筑管理系统（BMS/BAS）的安装、调试、编程和维护，控制楼宇的暖通空调、照明、安防等系统。澳大利亚绿建改造和数据中心扩张带动BMS专业人才需求旺盛，是电气类中最具技术含量的新兴职业。",
    "forecast_note": "绿建改造（NABERS/Green Star达标）带动大量BMS系统升级需求。数据中心扩张（AWS/Azure/Google在澳大量投资）需要精密BMS控制。智能楼宇物联网化趋势加速。",
    "trend_summary": "IoT和IP化BMS（BACnet/Modbus/KNX）替代传统专有系统，有IT背景的BMS技术员薪资溢价显著。数据中心BMS专家是市场最抢手的细分方向。"}
I18N_EN = {"locale": "en", "name": "Building Automation Technician",
    "summary": "Building Automation Technicians install, commission, program and maintain Building Management Systems (BMS/BAS) that control HVAC, lighting, security and energy systems in commercial buildings. Classified under ANZSCO 342115, demand is driven by Australia's green building retrofit market and rapid data centre expansion.",
    "forecast_note": "Green building retrofits (NABERS/Green Star compliance) drive BMS upgrade demand. Data centre expansion (AWS/Azure/Google) requires precision BMS control. Smart building IoT integration accelerating.",
    "trend_summary": "IP-based BMS (BACnet/Modbus/KNX) replacing legacy proprietary systems. BMS techs with IT/networking skills command significant salary premium. Data centre BMS is the most sought-after specialisation."}
EDUCATION = [
    {"stage": "Certificate III in Electrotechnology (Electrician) + BMS OJT", "duration": "42~48个月（电工学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "BMS通常由雇主在职培训", "sort_order": 0},
    {"stage": "BMS厂商认证（Honeywell/Siemens/Johnson Controls等）", "duration": "1~4周", "cost_min": 1500, "cost_max": 5000, "cost_note": "厂商认证费；雇主通常负担", "sort_order": 1},
    {"stage": "Certificate IV in Building Automation", "duration": "12~18个月", "cost_min": 3000, "cost_max": 8000, "cost_note": "部分RTO提供专项课程", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Electrical Licence (A Grade)", "issuer": "各州电气监管机构", "note": "主流入行路径", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "BMS厂商认证（Honeywell/Siemens/JCI等）", "issuer": "各BMS厂商", "note": "商业项目实际要求", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 450, "note": "全国，商业楼宇和数据中心均有"},
    {"platform": "Indeed", "count_min": 100, "count_max": 250, "note": "含系统集成商职位"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 300, "note": "偏大型楼宇和数据中心"},
]
SALARIES = [
    {"experience": "初级BMS技术员（0~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "商业楼宇基础维护", "sort_order": 0},
    {"experience": "中级BMS技术员（3~7年）", "salary_min": 90000, "salary_max": 120000, "salary_note": "Seek均值约$42~$56/hr（2026）", "sort_order": 1},
    {"experience": "资深BMS工程师（7年+）", "salary_min": 115000, "salary_max": 155000, "salary_note": "数据中心或大型商业，编程+项目管理溢价", "sort_order": 2},
    {"experience": "BMS项目经理 / 方案设计", "salary_min": 140000, "salary_max": 190000, "salary_note": "系统集成公司高级职位", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "189", "visa_name": "Skilled Independent", "description": "积分制独立移民", "sort_order": 2},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "电气+控制编程+网络协议多领域交叉"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "电工学徒4年+BMS厂商认证"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "电气持证+厂商认证；无高难笔试"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "绿建改造+数据中心扩张，需求持续增长"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "BMS专业人才供不应求，数据中心方向更抢手"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "技术性工作，调试和编程需要专注力"},
    {"dimension": "income_level",             "label_zh": "高",   "stars": 4, "note": "中位$90k~$120k；数据中心BMS专家$155k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "智能楼宇+数据中心+绿建长期驱动"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助楼宇控制在发展，但系统集成仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列，189/190/482均可"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA/电气持证+英语+积分"},
]
SUITABILITY_FIT = [
    "已持电工证，对控制编程和自动化系统感兴趣，希望进入高科技方向",
    "有楼宇控制、HVAC或弱电集成背景，目标技能移民来澳",
    "有意进入数据中心行业，BMS是高薪入口职业",
]
SUITABILITY_UNFIT = [
    "完全没有电气或控制系统基础",
    "不喜欢持续学习新的BMS平台和协议",
    "期望完全体力的户外工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 342115 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "BMS Technician 薪资（2026）", "url": "https://www.seek.com.au/bms-technician-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "AIRAH", "content": "澳洲制冷暖通空调学会", "url": "https://www.airah.org.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲楼宇自动化技术员工资多少？", "answer": "中级BMS技术员年薪约 $90,000~$120,000（约$42~$56/hr）。数据中心BMS专家资深可达 $115,000~$155,000+。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲BMS技术员容易找工作吗？", "answer": "容易。绿建改造和数据中心扩张带动需求，Seek挂牌200~450个职位，专业人才供不应求。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内楼宇控制经验澳洲认可吗？", "answer": "需TRA评估获取澳洲电气资质，再通过BMS厂商认证。有Honeywell/Siemens/JCI经验者评估顺利。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "BMS技术员会被AI取代吗？", "answer": "较低。AI辅助楼宇控制优化在发展，但系统集成、调试和跨系统故障排除仍需人工。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。电工证+BMS厂商认证即可入行，数据中心方向更看重实战经验。"},
]
MARKDOWN = """# 楼宇自动化技术员（BMS Technician）职业分析 · 澳大利亚

**职业代码：342115 – Building Automation Technician。**

楼宇自动化技术员负责建筑管理系统（BMS）的安装、调试、编程和维护。澳大利亚绿建改造和数据中心扩张带动BMS专业人才需求旺盛，是电气类中最具技术含量的新兴高薪职业。

---

## 1. 薪资范围

**收入水平：高（★★★★☆）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 初级BMS技术员（0~3年） | $70,000~$90,000 | 商业楼宇基础维护 |
| 中级BMS技术员（3~7年） | $90,000~$120,000 | 约$42~$56/hr（2026） |
| 资深BMS工程师（7年+） | $115,000~$155,000 | 数据中心或大型商业 |
| BMS项目经理 / 方案设计 | $140,000~$190,000 | 系统集成公司高级职位 |

---

## 2. 谁适合学楼宇自动化技术员？

- 已持电工证，对控制编程和自动化系统感兴趣
- 有楼宇控制、HVAC或弱电集成背景，目标技能移民来澳
- 有意进入数据中心行业，BMS是高薪入口职业

## 谁不适合学楼宇自动化技术员？

- 完全没有电气或控制系统基础
- 不喜欢持续学习新的BMS平台和协议
- 期望完全体力的户外工作

---

## 3. 常见问题

**澳洲BMS技术员工资多少？**
中级技术员年薪约 $90,000~$120,000。数据中心BMS专家可达 $115,000~$155,000+。

**澳洲BMS技术员容易找工作吗？**
容易。绿建改造和数据中心扩张需求旺盛，专业人才供不应求。

**BMS技术员会被AI取代吗？**
较低。系统集成、调试和跨系统故障排除仍需人工处理。

---

*数据来源：JSA、Seek AU、Department of Home Affairs CSOL（2025-2026）*
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
    print("[OK] 楼宇自动化技术员（BMS Technician）入库+Markdown完成")
if __name__ == "__main__": run()
