"""测试工程师 (261314) QA Engineer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "261314", "anzsco_title": "QA Engineer",
    "category": "IT", "workforce_size": 14000, "shortage_listed": 0,
    "growth_areas": json.dumps(["Test Automation (Selenium/Playwright)","Performance & Load Testing","Security Testing","AI-Assisted Testing"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "测试工程师",
    "summary": "测试工程师（QA Engineer）负责软件测试、缺陷发现和质量保证，确保产品符合功能和性能要求。澳洲软件行业高速发展，自动化测试（Selenium、Playwright、Cypress）技能的测试工程师需求持续增长，是进入IT行业的重要路径之一。",
    "forecast_note": "敏捷开发和DevOps的普及推动测试左移（Shift-Left Testing），测试工程师须深度融入开发流程。AI辅助测试工具快速普及改变了传统手工测试方式，但测试架构设计和质量策略制定仍需专业人员。",
    "trend_summary": "手工测试岗位快速减少，自动化测试框架（Selenium、Playwright）和API测试（Postman/RestAssured）成为必备技能。性能测试（JMeter、k6）和安全测试（OWASP）方向薪资溢价明显，CI/CD集成测试技能是招聘热点。"}
I18N_EN = {"locale": "en", "name": "QA Engineer",
    "summary": "QA engineers are responsible for software testing, defect identification and quality assurance to ensure products meet functional and performance requirements. Australia's fast-growing software industry sustains demand for test automation (Selenium, Playwright, Cypress) specialists; QA is also an accessible entry point to IT careers.",
    "forecast_note": "Agile and DevOps adoption is driving shift-left testing, requiring QA engineers to be deeply integrated into the development process. AI-assisted testing tools are rapidly changing traditional manual testing, but test architecture design and quality strategy remain specialist human roles.",
    "trend_summary": "Manual testing roles are declining rapidly; automation frameworks (Selenium, Playwright) and API testing (Postman/RestAssured) are now essential skills. Performance testing (JMeter, k6) and security testing (OWASP) command salary premiums; CI/CD integration testing is a key hiring focus."}
EDUCATION = [
    {"stage": "Bachelor of IT / Computer Science", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "ISTQB Foundation / Advanced Certification", "duration": "1~3个月", "cost_min": 400, "cost_max": 1500, "cost_note": "行业基础认证", "sort_order": 1},
    {"stage": "Test Automation Tools Portfolio (Selenium/Playwright)", "duration": "3~6个月自学", "cost_min": 0, "cost_max": 500, "cost_note": "实战项目组合", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of IT / Software Engineering", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "ISTQB Certified Tester Foundation Level", "issuer": "ISTQB", "note": "行业基础认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "ISTQB Advanced Test Automation Engineer", "issuer": "ISTQB", "note": "自动化测试高级认证", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 200, "count_max": 380, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 130, "count_max": 260, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 170, "count_max": 310, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 62000, "salary_max": 82000, "salary_note": "Junior QA Engineer", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 85000, "salary_max": 120000, "salary_note": "QA/Automation Engineer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 123000, "salary_max": 165000, "salary_note": "Senior QA / Test Lead", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，IT类", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较低", "stars": 2, "note": "入门门槛比开发低"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "需积累自动化实战经验"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "ISTQB入门友好"},
    {"dimension": "job_demand",               "label_zh": "稳定", "stars": 3, "note": "自动化方向需求旺盛"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "自动化测试竞争激烈"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "发版前压力集中"},
    {"dimension": "income_level",             "label_zh": "中等", "stars": 3, "note": "AUD 8.5万~16.5万"},
    {"dimension": "future_prospect",          "label_zh": "中等", "stars": 3, "note": "需持续提升自动化技能"},
    {"dimension": "ai_risk",                  "label_zh": "中高", "stars": 4, "note": "手工测试岗位受AI冲击较大"},
    {"dimension": "pr_friendliness",          "label_zh": "中等", "stars": 3, "note": "IT类移民可行"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需要自动化技能加持"},
]
SUITABILITY_FIT = ["有编程基础并希望进入IT行业的转行者", "注重代码质量和系统可靠性的开发人员", "希望通过测试方向进入金融科技公司者"]
SUITABILITY_UNFIT = ["不愿学习自动化框架、只做手工测试者", "偏好快速开发新功能而非测试验证者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 261314 测试工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/qa-engineer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "测试工程师在澳洲薪资如何？", "answer": "初级约AUD 6.2万~8.2万，中级8.5万~12万，高级/测试负责人12.3万~16.5万，自动化测试和性能测试专家额外溢价。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲QA工程师好找工作吗？", "answer": "手工测试需求在减少，自动化测试工程师持续紧缺，Seek常年有200~380个活跃职位，需掌握Selenium或Playwright等框架。"},
]
MARKDOWN = """# 测试工程师（QA Engineer）职业分析 · 澳大利亚

**职业代码：261314 – QA Engineer。**

测试工程师确保软件质量，自动化测试技能是当前最重要的核心竞争力，是进入澳洲IT行业门槛较低的职业方向之一。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $62,000~$82,000 |
| 中级（3-8年） | $85,000~$120,000 |
| 高级（8年+） | $123,000~$165,000 |

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
    print("[OK] 测试工程师入库完成")
if __name__ == "__main__": run()
