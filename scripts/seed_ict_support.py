"""IT技术支持 (313113) ICT Support Technician — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "313113", "anzsco_title": "ICT Support Technician",
    "category": "IT", "workforce_size": 45000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Managed Service Providers","Remote Work Infrastructure","Cloud Desktop Support","Cybersecurity Helpdesk"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "IT技术支持",
    "summary": "IT技术支持人员为企业和个人用户提供硬件、软件和网络问题的诊断与解决服务。澳洲是IT支持岗位最多的职业之一，入行门槛相对较低，适合IT入行人员积累经验，晋升路径可通向系统管理员、网络工程师或信息安全等方向。",
    "forecast_note": "远程办公常态化和企业云化持续推动对IT支持的需求，托管服务提供商（MSP）模式快速扩张。自动化工具处理部分简单工单，但复杂技术支持和现场服务仍需人工处理。",
    "trend_summary": "Level 1/2支持向Level 3和专业化方向分化，持有CompTIA A+/Network+或Microsoft 365认证的支持人员更受青睐。MSP行业是IT支持最主要的就业渠道，提供快速积累技术经验的机会。"}
I18N_EN = {"locale": "en", "name": "ICT Support Technician",
    "summary": "ICT support technicians diagnose and resolve hardware, software and network issues for business and individual users. This is one of Australia's highest-volume IT roles with relatively low entry barriers, making it ideal for building experience before advancing to sysadmin, network engineer or cybersecurity roles.",
    "forecast_note": "Permanent remote work and enterprise cloud adoption continue to drive IT support demand; managed service providers (MSP) are expanding rapidly. Automation handles some simple tickets but complex technical support and on-site service still requires people.",
    "trend_summary": "Support roles are stratifying: Level 1/2 commoditising while Level 3 and specialist roles grow. CompTIA A+/Network+ or Microsoft 365 certifications are preferred. The MSP sector is the primary employment channel, offering fast-paced technical experience accumulation."}
EDUCATION = [
    {"stage": "Certificate III/IV in IT or Diploma of IT", "duration": "6~18个月", "cost_min": 3000, "cost_max": 15000, "cost_note": "TAFE或私立学院", "sort_order": 0},
    {"stage": "CompTIA A+ / Network+ Certification", "duration": "1~3个月备考", "cost_min": 400, "cost_max": 1200, "cost_note": "行业基础认证", "sort_order": 1},
    {"stage": "Microsoft 365 Fundamentals / Azure Fundamentals", "duration": "1~2个月", "cost_min": 200, "cost_max": 800, "cost_note": "云支持加分项", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III/IV in Information Technology", "issuer": "TAFE / RTO", "note": "入行可选", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "CompTIA A+ / Network+", "issuer": "CompTIA", "note": "行业基础认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "ITIL Foundation", "issuer": "Axelos", "note": "服务管理加分", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 500, "count_max": 900, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 350, "count_max": 600, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 400, "count_max": 700, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-2年）", "salary_min": 52000, "salary_max": 68000, "salary_note": "Level 1 Support", "sort_order": 0},
    {"experience": "中级（2-6年）", "salary_min": 70000, "salary_max": 95000, "salary_note": "Level 2/3 Support", "sort_order": 1},
    {"experience": "高级（6年+）", "salary_min": 98000, "salary_max": 130000, "salary_note": "Senior Support / Team Lead", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "入门门槛低"},
    {"dimension": "learning_duration",        "label_zh": "较短", "stars": 2, "note": "证书课程6~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "CompTIA A+入门容易"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 4, "note": "岗位量大，机会多"},
    {"dimension": "competition",              "label_zh": "较高", "stars": 4, "note": "入门级竞争激烈"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "含现场出勤"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "AUD 5.2万~13万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 3, "note": "可横向发展至网络/安全"},
    {"dimension": "ai_risk",                  "label_zh": "中高", "stars": 4, "note": "简单工单自动化风险较高"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "IT职业类别移民可行"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需积累经验和认证"},
]
SUITABILITY_FIT = ["IT行业新入行者积累经验的理想起点", "喜欢解决问题和与用户互动者", "希望通过实战快速积累IT技能者"]
SUITABILITY_UNFIT = ["希望直接高薪入行者", "不喜欢处理用户投诉和重复性工单者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 313113 IT技术支持数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/it-support-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "IT技术支持在澳洲薪资如何？", "answer": "初级Level 1约AUD 5.2万~6.8万，Level 2/3约7万~9.5万，高级/团队负责人可达9.8万~13万。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲IT支持岗位好找吗？", "answer": "是澳洲岗位量最大的IT职位之一，Seek常年有500~900个活跃职位，MSP公司和大型企业是主要雇主，入行门槛低。"},
]
MARKDOWN = """# IT技术支持（ICT Support Technician）职业分析 · 澳大利亚

**职业代码：313113 – ICT Support Technician。**

IT技术支持是澳洲IT行业岗位量最大的职业之一，是新人进入IT行业积累经验的理想起点，向网络工程师、系统管理员方向晋升路径清晰。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-2年） | $52,000~$68,000 |
| 中级（2-6年） | $70,000~$95,000 |
| 高级（6年+） | $98,000~$130,000 |

---

*数据来源：JSA、Seek AU（2025-2026）*
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
    print("[OK] IT技术支持入库完成")
if __name__ == "__main__": run()
