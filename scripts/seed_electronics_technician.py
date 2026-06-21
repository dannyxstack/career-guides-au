"""Electronics Technician (315111) 电子技术员 — AU 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "315111", "anzsco_title": "Electronics Technician",
    "category": "技术员", "workforce_size": 28000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Defence Electronics","Telecommunications & 5G","Renewable Energy Systems","Industrial IoT & Automation"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "电子技术员",
    "summary": "电子技术员（Electronics Technician）安装、测试和维修电子设备，涵盖通信、工业控制、医疗设备和国防电子。澳洲国防、5G通信和可再生能源系统快速扩张，持证电子技术员持续短缺。",
    "forecast_note": "AUKUS国防电子（通信/雷达/水下传感器）2025年起大量新增岗位。5G基础设施持续铺开，工业IoT自动化部署带动维护需求。",
    "trend_summary": "AI诊断辅助减少部分故障排查工作，但现场安装、调试和高压系统处理仍需持证人员。跨学科（电气+数字+通信）背景的技术员薪资溢价明显。"}
I18N_EN = {"locale": "en", "name": "Electronics Technician",
    "summary": "Electronics technicians install, test and repair electronic equipment across telecommunications, industrial control, medical devices and defence electronics. Rapid expansion of Australian defence, 5G and renewable energy systems creates sustained shortages under ANZSCO 315111.",
    "forecast_note": "AUKUS defence electronics (communications/radar/underwater sensors) creating substantial new positions from 2025. 5G infrastructure rollout ongoing. Industrial IoT/automation deployment driving maintenance demand.",
    "trend_summary": "AI-assisted diagnostics reducing some fault-finding work, but on-site installation, commissioning and high-voltage system handling still requires licensed personnel. Cross-disciplinary (electrical+digital+comms) backgrounds command significant pay premium."}
EDUCATION = [
    {"stage": "Certificate III in Electronics/Electrotechnology", "duration": "36~42个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州TAFE", "sort_order": 0},
    {"stage": "Associate Degree in Electronics Engineering", "duration": "24个月", "cost_min": 15000, "cost_max": 25000, "cost_note": "TAFE/大学，可选进阶路径", "sort_order": 1},
    {"stage": "海外资质TRA互认", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Electrotechnology (Electronics)", "issuer": "TAFE/RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "Defence Security Clearance (NV1/NV2)", "issuer": "ASD / AGSVA", "note": "国防电子职位必备", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 400, "count_max": 900, "note": "全国，VIC/NSW/QLD集中"},
    {"platform": "Indeed", "count_min": 200, "count_max": 500, "note": "通信和工业自动化"},
    {"platform": "LinkedIn", "count_min": 150, "count_max": 350, "note": "国防和5G方向"},
]
SALARIES = [
    {"experience": "学徒/初级（0~3年）", "salary_min": 55000, "salary_max": 78000, "salary_note": "Electrical Award基础", "sort_order": 0},
    {"experience": "中级电子技术员（3~8年）", "salary_min": 80000, "salary_max": 110000, "salary_note": "Seek均值约$39~$53/hr（2026）", "sort_order": 1},
    {"experience": "国防/通信专家（8年+）", "salary_min": 110000, "salary_max": 150000, "salary_note": "国防安全许可+专业溢价", "sort_order": 2},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "模拟+数字+通信+工业控制跨学科"},
    {"dimension": "learning_duration",        "label_zh": "中等", "stars": 3, "note": "学徒3~3.5年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA；国防另需安全许可"},
    {"dimension": "job_demand",               "label_zh": "高",   "stars": 4, "note": "国防+5G+工业IoT全面旺盛"},
    {"dimension": "competition",              "label_zh": "低",   "stars": 2, "note": "持证电子技术员持续短缺"},
    {"dimension": "work_intensity",           "label_zh": "中等", "stars": 3, "note": "室内室外混合；技术专注度高"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中级 $80k~$110k；国防专家$150k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "AUKUS+AI+5G三线并驱，长期旺盛"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "AI辅助诊断，但现场操作不可替代"},
    {"dimension": "pr_friendliness",          "label_zh": "高",   "stars": 4, "note": "CSOL在列"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语+国防安全许可（外籍受限）"},
]
SUITABILITY_FIT = [
    "有电子、通信或工业控制技术背景，希望进入澳洲国防或5G行业",
    "跨学科技术能力（电气+数字+通信），追求高薪专家路径",
]
SUITABILITY_UNFIT = [
    "无电子或电气基础",
    "希望纯体力或纯管理工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 315111 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Electronics Technician 薪资及岗位量（2026）", "url": "https://www.seek.com.au/electronics-technician-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲电子技术员工资多少？", "answer": "中级电子技术员年薪约 $80,000~$110,000（$39~$53/hr）。国防/通信专家可达 $110,000~$150,000。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲电子技术员需求旺盛吗？", "answer": "旺盛。AUKUS国防电子+5G+工业IoT三线并驱，全国Seek挂牌400~900个职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "中国电子工程经验澳洲认可吗？", "answer": "需TRA技能评估（12~18个月）。国防职位额外需要澳洲安全许可（外籍有限制，通常需永居或公民身份）。"},
    {"faq_type": "future", "sort_order": 3, "question": "AI会替代电子技术员吗？", "answer": "较低风险。AI辅助诊断在增加，但现场安装、调试、高压操作仍需持证人员，AUKUS军事项目更增加需求。"},
]
MARKDOWN = """# 电子技术员（Electronics Technician）职业分析 · 澳大利亚

**职业代码：315111 – Electronics Technician。**

电子技术员安装测试维修各类电子设备，在通信、工业控制、医疗设备和国防电子领域需求旺盛。AUKUS国防计划+5G+工业IoT三线并驱，是澳洲前景最佳的技术员职业之一。

---

## 1. 薪资范围

| 经验阶段 | 年薪（AUD） |
|---|---:|
| 初级（0~3年） | $55,000~$78,000 |
| 中级（3~8年） | $80,000~$110,000 |
| 国防/通信专家 | $110,000~$150,000+ |

---

*数据来源：JSA、Seek AU、Department of Home Affairs（2025-2026）*
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
    print("[OK] 电子技术员（Electronics Technician）入库+Markdown完成")
if __name__ == "__main__": run()
