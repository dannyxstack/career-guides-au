"""助产士 (254111) Midwife — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "254111", "anzsco_title": "Midwife",
    "category": "医疗", "workforce_size": 20000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Midwifery Group Practice","Remote & Rural Birthing Services","Private Midwifery Practice","Neonatal Intensive Care Support"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "助产士",
    "summary": "助产士为孕妇提供产前、分娩和产后护理，是澳洲医疗系统中不可或缺的核心医疗专业人员。澳洲持续增长的出生率和助产士短缺使该职业长期处于紧缺状态，AHPRA注册助产士可独立开业，职业发展空间广阔。",
    "forecast_note": "澳洲各州推进助产士主导护理（Midwifery-Led Care）模式，2025-2030年对注册助产士的需求持续增长。农村和偏远地区助产服务严重不足，政府提供额外激励吸引助产士赴偏远地区工作。",
    "trend_summary": "助产士主导护理模式（MGP）在各大医院快速扩张，持续助产护理（Caseload Midwifery）成为改善母婴结局的主流实践。远程护理和数字化孕产妇监测技术为偏远地区助产服务提供了新方式。"}
I18N_EN = {"locale": "en", "name": "Midwife",
    "summary": "Midwives provide antenatal, birthing and postnatal care to pregnant women, forming an indispensable part of Australia's healthcare system. Australia's sustained birth rate and midwifery shortage keep this profession in persistent demand; AHPRA-registered midwives can operate independently with broad career development opportunities.",
    "forecast_note": "Australian states are expanding midwifery-led care models 2025-2030, driving continued demand for registered midwives. Rural and remote areas face severe midwifery shortages; governments offer additional incentives to attract midwives to these regions.",
    "trend_summary": "Midwifery group practice (MGP) is rapidly expanding in major hospitals; caseload midwifery is the mainstream practice for improving maternal and infant outcomes. Telehealth and digital maternal monitoring technologies are enabling new approaches to remote midwifery care."}
EDUCATION = [
    {"stage": "Bachelor of Midwifery (3yr direct entry)", "duration": "3年", "cost_min": 25000, "cost_max": 45000, "cost_note": "国际生约$100k~$140k总费", "sort_order": 0},
    {"stage": "Graduate Entry Midwifery (post-nursing)", "duration": "2年", "cost_min": 20000, "cost_max": 38000, "cost_note": "护士转读路径", "sort_order": 1},
    {"stage": "AHPRA Registration as Midwife", "duration": "毕业后申请", "cost_min": 200, "cost_max": 500, "cost_note": "年度注册费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Bachelor of Midwifery", "issuer": "认可大学", "note": "执业必备学历", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "AHPRA Registered Midwife", "issuer": "AHPRA", "note": "法定注册资质", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "Eligible Midwife (Medicare access)", "issuer": "AHPRA / DoH", "note": "独立开业所需", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 550, "note": "2025年均值"},
    {"platform": "Indeed", "count_min": 180, "count_max": 350, "note": "2025年均值"},
    {"platform": "LinkedIn", "count_min": 200, "count_max": 400, "note": "2025年均值"},
]
SALARIES = [
    {"experience": "初级（0-3年）", "salary_min": 68000, "salary_max": 85000, "salary_note": "Graduate/New Grad Midwife", "sort_order": 0},
    {"experience": "中级（3-8年）", "salary_min": 87000, "salary_max": 110000, "salary_note": "Registered Midwife", "sort_order": 1},
    {"experience": "高级（8年+）", "salary_min": 112000, "salary_max": 145000, "salary_note": "Senior Midwife / Team Leader", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，医疗紧缺", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居通道", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名，医疗类优先", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "较高", "stars": 4, "note": "需临床技能和医学知识"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "本科3年+注册+临床经验"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "AHPRA注册流程明确"},
    {"dimension": "job_demand",               "label_zh": "极旺", "stars": 5, "note": "长期紧缺职业"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "供严重不足"},
    {"dimension": "work_intensity",           "label_zh": "较高", "stars": 4, "note": "含夜班和紧急情况处理"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 3, "note": "AUD 8.7万~14.5万"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "政府政策持续支持"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "临床判断和情感护理不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "医疗类移民最优先职业之一"},
    {"dimension": "pr_difficulty",            "label_zh": "较易", "stars": 2, "note": "AHPRA注册后通道畅通"},
]
SUITABILITY_FIT = ["对孕产妇和新生儿护理充满热情者", "能承受轮班和紧急情况高压工作者", "希望在医疗系统中独立执业者"]
SUITABILITY_UNFIT = ["无法承受轮班和夜班工作者", "不擅长在高压情绪化环境下工作者"]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 254111 助产士数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "薪资及岗位量", "url": "https://www.seek.com.au/midwife-jobs"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "助产士在澳洲薪资如何？", "answer": "初级约AUD 6.8万~8.5万，中级8.7万~11万，高级/主任助产士11.2万~14.5万，夜班和农村地区有额外津贴。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲助产士好找工作吗？", "answer": "是长期极度紧缺职业，Seek常年有300~550个活跃职位，农村和偏远地区更缺，AHPRA注册后基本可立即就业。"},
]
MARKDOWN = """# 助产士（Midwife）职业分析 · 澳大利亚

**职业代码：254111 – Midwife。**

助产士为孕妇提供全程护理，是澳洲医疗系统长期极度紧缺的核心职业，AHPRA注册后职业发展空间极为广阔。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0-3年） | $68,000~$85,000 |
| 中级（3-8年） | $87,000~$110,000 |
| 高级（8年+） | $112,000~$145,000 |

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
    print("[OK] 助产士入库完成")
if __name__ == "__main__": run()
