"""网络工程师 (263211) Network Engineer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "263211", "anzsco_title": "Network Engineer",
    "category": "IT", "workforce_size": 22000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Cloud Networking & SD-WAN","5G Infrastructure","Cybersecurity Network Defence","Data Centre Networks"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "网络工程师",
    "summary": "网络工程师设计、部署和维护企业及运营商网络基础设施，是澳洲IT行业的核心职业。云计算迁移、5G网络建设和网络安全强化推动持续需求，持有Cisco CCNP/CCIE或云网络认证的工程师尤为抢手。",
    "forecast_note": "澳洲全国宽带网络（NBN）升级和5G网络扩张2025-2030年持续推进，云网络（AWS/Azure网络架构）专家需求大幅增长。网络安全合规要求推动网络+安全复合型工程师薪资上涨。",
    "trend_summary": "传统MPLS向SD-WAN迁移成趋势，网络自动化（Ansible/Python）技能成新标配。纯硬件配置岗位减少，云网络架构和零信任安全方向增长显著。"}
I18N_EN = {"locale": "en", "name": "Network Engineer",
    "summary": "Network engineers design, deploy and maintain enterprise and carrier network infrastructure. Cloud migration, 5G build-out and network security hardening are driving persistent demand; engineers holding Cisco CCNP/CCIE or cloud networking certifications are highly sought after.",
    "forecast_note": "NBN upgrades and 5G expansion 2025-2030 are ongoing; cloud networking (AWS/Azure) specialist demand is growing strongly. Cybersecurity compliance requirements are pushing salaries higher for network-security hybrid engineers.",
    "trend_summary": "SD-WAN is replacing MPLS; network automation (Ansible/Python) is now a standard skill. Pure hardware config roles are declining while cloud networking architecture and zero-trust security are the growth areas."}
EDUCATION = [
    {"stage": "Bachelor of IT / Computer Science / Networking", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "Cisco CCNA / CCNP Certification", "duration": "3~12个月", "cost_min": 500, "cost_max": 3000, "cost_note": "在职备考", "sort_order": 1},
    {"stage": "Cloud Networking (AWS/Azure) Certification", "duration": "1~6个月", "cost_min": 300, "cost_max": 2000, "cost_note": "加分项", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of IT / Networking", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Cisco CCNA / CCNP / CCIE", "issuer": "Cisco", "note": "行业标准认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "AWS Advanced Networking / Azure Network Engineer", "issuer": "AWS / Microsoft", "note": "云网络加分项", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 500, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 180, "count_max": 320, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 250, "count_max": 420, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 70000, "salary_max": 92000, "salary_note": "Junior Network Engineer", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 95000, "salary_max": 135000, "salary_note": "Network Engineer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 140000, "salary_max": 190000, "salary_note": "Senior/Principal Network Engineer", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，IT紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需掌握网络协议和安全知识"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位+认证约4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "CCNP需一定准备时间"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 4, "note": "云化和安全需求持续增长"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "需求大，申请者也多"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "偶有on-call值班"},
    {"dimension": "income_level",             "label_zh": "高", "stars": 4, "note": "AUD 9.5万~19万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 4, "note": "云网络方向前景极好"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "自动化影响部分重复配置工作"},
    {"dimension": "pr_friendliness",          "label_zh": "高", "stars": 4, "note": "IT类移民通道顺畅"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需要认证加持"},
]
SUITABILITY_FIT = ["有IT背景并对网络基础设施感兴趣者", "愿意持续更新云和安全技能者", "能接受偶尔on-call和轮班工作者"]
SUITABILITY_UNFIT = ["不喜欢技术细节深钻者", "偏好软件开发而非基础设施工作者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 263211 网络工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/network-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "网络工程师在澳洲薪资怎么样？", "answer": "初级约AUD 7万~9.2万，中级9.5万~13.5万，高级/主任工程师14万~19万，云网络和安全专家额外溢价10-20%。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲网络工程师需求如何？", "answer": "长期紧缺职业，Seek常年有300~500个活跃职位，5G和云网络方向最热，金融和政府行业薪资最高。"},
]
MARKDOWN = """# 网络工程师（Network Engineer）职业分析 · 澳大利亚

**职业代码：263211 – Network Engineer。**

网络工程师设计和维护澳洲企业与运营商网络基础设施，云网络和5G方向持续高速增长，是IT行业核心紧缺职业。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $70,000~$92,000 |
| 中级（3-8年） | $95,000~$135,000 |
| 高级（8年+） | $140,000~$190,000 |

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
    print("[OK] 网络工程师入库完成")
if __name__ == "__main__": run()
