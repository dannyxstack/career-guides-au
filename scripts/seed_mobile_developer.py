"""移动应用开发工程师 (261319) Mobile Developer — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "261319", "anzsco_title": "Mobile Developer",
    "category": "IT", "workforce_size": 12000, "shortage_listed": 1,
    "growth_areas": json.dumps(["React Native Cross-Platform Apps","Flutter Development","Health & Fintech Mobile Apps","Government Digital Services"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "移动应用开发工程师",
    "summary": "移动应用开发工程师为iOS和Android平台设计和构建移动应用程序，是澳洲数字经济的重要组成部分。金融科技、医疗健康和政府数字服务领域的移动化需求持续增长，React Native和Flutter跨平台技能尤为受到雇主青睐。",
    "forecast_note": "澳洲移动支付、数字健康管理和政府服务App化趋势2025-2030年持续推进，跨平台开发（React Native/Flutter）技能使单人开发者效率倍增，推动对高质量移动开发人才的需求持续增长。",
    "trend_summary": "原生iOS（Swift）和Android（Kotlin）开发仍是高薪方向，但React Native和Flutter正在快速获得市场份额。AI功能集成（机器学习SDK、LLM API调用）成为高级移动开发工程师的新差异化技能。"}
I18N_EN = {"locale": "en", "name": "Mobile Developer",
    "summary": "Mobile developers design and build applications for iOS and Android platforms, forming an important part of Australia's digital economy. Fintech, digital health and government digital services are driving sustained demand; React Native and Flutter cross-platform skills are particularly sought by employers.",
    "forecast_note": "Australia's mobile payments, digital health management and government service app trends will continue 2025-2030. Cross-platform development (React Native/Flutter) skills multiply single-developer output, sustaining demand for high-quality mobile talent.",
    "trend_summary": "Native iOS (Swift) and Android (Kotlin) development remain the highest-paid directions, but React Native and Flutter are rapidly gaining market share. AI feature integration (ML SDKs, LLM API calls) is an emerging differentiator for senior mobile developers."}
EDUCATION = [
    {"stage": "Bachelor of IT / Computer Science / Software Eng", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "iOS / Android Developer Portfolio Projects", "duration": "6~12个月自学", "cost_min": 0, "cost_max": 2000, "cost_note": "开源项目和App Store上架经验", "sort_order": 1},
    {"stage": "Google Associate Android Dev / Apple Dev Cert", "duration": "2~3个月", "cost_min": 200, "cost_max": 1000, "cost_note": "平台认证加分", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of IT / Software Engineering", "issuer": "认可大学", "note": "入行基础", "is_mandatory": 0, "sort_order": 0},
    {"qual_name": "Google Associate Android Developer", "issuer": "Google", "note": "Android认证", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Apple Developer Program Certification", "issuer": "Apple", "note": "iOS开发账号+上架经验", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 150, "count_max": 280, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 100, "count_max": 200, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 130, "count_max": 250, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 70000, "salary_max": 92000, "salary_note": "Junior Mobile Developer", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 95000, "salary_max": 140000, "salary_note": "Mobile Developer", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 145000, "salary_max": 200000, "salary_note": "Senior / Lead Mobile Dev", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，IT紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "需掌握移动平台特性"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学位+项目组合约3~4年"},
    {"dimension": "certification_difficulty", "label_zh": "较低", "stars": 2, "note": "作品集比证书更重要"},
    {"dimension": "job_demand",               "label_zh": "旺盛", "stars": 4, "note": "金融科技和政府App需求强"},
    {"dimension": "competition",              "label_zh": "中等", "stars": 3, "note": "跨平台开发者竞争上升"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "发版周期压力"},
    {"dimension": "income_level",             "label_zh": "高", "stars": 4, "note": "AUD 9.5万~20万"},
    {"dimension": "future_prospect",          "label_zh": "良好", "stars": 4, "note": "AI集成和可穿戴设备新机遇"},
    {"dimension": "ai_risk",                  "label_zh": "中等", "stars": 3, "note": "AI可辅助但架构设计仍需人"},
    {"dimension": "pr_friendliness",          "label_zh": "高", "stars": 4, "note": "IT类移民通道顺畅"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "需要强作品集"},
]
SUITABILITY_FIT = ["热爱移动产品开发，有强烈的产品感者", "希望在金融科技或数字健康领域发展者", "能同时掌握iOS和Android跨平台开发者"]
SUITABILITY_UNFIT = ["偏好后端或基础设施开发者", "不喜欢频繁适配不同设备和系统版本者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 261319 移动开发工程师数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/mobile-developer-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "移动应用开发工程师在澳洲薪资如何？", "answer": "初级约AUD 7万~9.2万，中级9.5万~14万，高级/Lead开发工程师14.5万~20万，金融科技公司薪资溢价明显。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲移动开发岗位好找吗？", "answer": "需求持续旺盛，Seek常年有150~280个活跃职位，React Native和Flutter跨平台技能最受欢迎，悉尼和墨尔本金融科技集群需求最旺。"},
]
MARKDOWN = """# 移动应用开发工程师（Mobile Developer）职业分析 · 澳大利亚

**职业代码：261319 – Mobile Developer。**

移动应用开发工程师构建iOS和Android应用，在澳洲金融科技、数字健康和政府服务数字化浪潮中需求持续增长。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $70,000~$92,000 |
| 中级（3-8年） | $95,000~$140,000 |
| 高级（8年+） | $145,000~$200,000 |

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
    print("[OK] 移动应用开发工程师入库完成")
if __name__ == "__main__": run()
