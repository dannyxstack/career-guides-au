"""Instrumentation Technician (312311) 仪表技术员 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "312311", "anzsco_title": "Instrumentation Technician",
    "category": "技术", "workforce_size": 18000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Oil & Gas Processing","Mining & Minerals Processing","Water Treatment Plants","Renewable Energy (SCADA)"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "仪表技术员",
    "summary": "仪表技术员（Instrumentation Technician）负责工业生产过程中测量、控制和自动化仪器仪表的安装、校准、维护和故障排除。澳大利亚石油天然气、矿业和水处理行业对仪表技术员需求旺盛，FIFO模式下收入极具竞争力。",
    "forecast_note": "WA/QLD油气行业FIFO仪表技术员持续短缺。矿山自动化和SCADA系统升级需求增加。水处理基础设施投资扩大。JSA确认短缺（2025）。",
    "trend_summary": "工业4.0和过程自动化升级增加仪表系统需求。掌握SCADA/DCS（ABB/Honeywell/Siemens）的技术员薪资溢价明显。矿业关停（shutdown）期间日薪率极高。"}
I18N_EN = {"locale": "en", "name": "Instrumentation Technician",
    "summary": "Instrumentation Technicians install, calibrate, maintain and troubleshoot measurement and control instruments in industrial processes. Classified under ANZSCO 312311, they are in sustained demand across oil and gas, mining, water treatment and renewable energy sectors in Australia.",
    "forecast_note": "WA/QLD oil and gas FIFO instrumentation roles persistently short-staffed. Mine automation and SCADA upgrades add demand. Water infrastructure investment expanding. JSA confirms shortage.",
    "trend_summary": "Industry 4.0 and process automation drive instrument system demand. SCADA/DCS expertise (ABB/Honeywell/Siemens) commands salary premium. Mining shutdown day rates extremely high."}
EDUCATION = [
    {"stage": "Certificate III/IV in Instrumentation and Control", "duration": "36~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州差异；工具费约$1,000", "sort_order": 0},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 1},
    {"stage": "SCADA/DCS 专项培训（ABB/Honeywell等）", "duration": "1~4周", "cost_min": 1000, "cost_max": 4000, "cost_note": "厂商认证费；雇主通常负担", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate IV in Instrumentation and Control", "issuer": "TAFE / RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Electrical Licence (Restricted)", "issuer": "各州", "note": "部分州要求", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 600, "note": "全国，WA/QLD油气和矿业集中"},
    {"platform": "Indeed", "count_min": 150, "count_max": 350, "note": "含FIFO职位"},
    {"platform": "LinkedIn", "count_min": 100, "count_max": 250, "note": "偏工业自动化公司"},
]
SALARIES = [
    {"experience": "初级仪表技术员（0~3年）", "salary_min": 70000, "salary_max": 90000, "salary_note": "水处理或制造业", "sort_order": 0},
    {"experience": "中级技术员（3~7年）", "salary_min": 90000, "salary_max": 125000, "salary_note": "Seek均值约$45~$58/hr（2026）", "sort_order": 1},
    {"experience": "资深 / FIFO油气（7年+）", "salary_min": 120000, "salary_max": 170000, "salary_note": "WA/QLD FIFO含轮班津贴", "sort_order": 2},
    {"experience": "矿业Shutdown合同工", "salary_min": 150000, "salary_max": 220000, "salary_note": "关停期间日薪$900~$1,200+", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "电气+控制+过程仪表多领域交叉，学习量大"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3~4年+SCADA专项培训"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate IV+TRA评估"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "油气/矿业/水处理全面旺盛，FIFO短缺严重"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "持证技术员极度稀缺，矿业FIFO更抢手"},
    {"dimension": "work_intensity",           "label_zh": "中高", "stars": 4, "note": "工业现场作业，关停期间高强度连续班"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "FIFO $120k~$170k；矿业关停合同$220k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "工业4.0和过程自动化升级，长期需求高位"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "自动化提升效率但故障排除仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，偏远矿区491加分"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语+积分"},
]
SUITABILITY_FIT = [
    "有工业仪表、DCS/PLC控制或过程自动化背景，目标技能移民来澳",
    "接受FIFO工作模式，追求矿业高薪",
    "有意在油气或矿业行业长期发展，薪资天花板高",
]
SUITABILITY_UNFIT = [
    "不接受偏远地区FIFO模式",
    "完全没有电气或仪表背景",
    "期望完全城市内工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 312311 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Instrumentation Technician 薪资（2026）", "url": "https://www.seek.com.au/instrumentation-technician-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲仪表技术员工资多少？", "answer": "中级技术员年薪约 $90,000~$125,000。FIFO油气方向可达 $120,000~$170,000，矿业关停合同工可达 $220,000+。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲仪表技术员容易找工作吗？", "answer": "非常容易。油气/矿业/水处理全面旺盛，FIFO持证技术员极度稀缺，持证后通常快速入职。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内仪表工程师经验澳洲认可吗？", "answer": "需TRA评估（12~18个月）。有DCS/PLC经验者评估通过率高，矿业雇主认可度高。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "仪表技术员会被AI取代吗？", "answer": "较低。工业现场故障排除和安全判断需要人工，AI辅助诊断是效率工具而非替代。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate IV即可入行，有工程技术学历可通过TRA快速认证。"},
]
MARKDOWN = """# 仪表技术员（Instrumentation Technician）职业分析 · 澳大利亚

**职业代码：312311 – Instrumentation Technician。**

仪表技术员负责工业生产过程中测量、控制和自动化仪器仪表的安装、校准、维护和故障排除。澳大利亚石油天然气、矿业和水处理行业对仪表技术员需求旺盛，矿业FIFO模式下收入极具竞争力。

---

## 1. 薪资范围

**收入水平：极高（★★★★★）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 初级仪表技术员（0~3年） | $70,000~$90,000 | 水处理或制造业 |
| 中级技术员（3~7年） | $90,000~$125,000 | 均值约$45~$58/hr（2026） |
| 资深 / FIFO油气（7年+） | $120,000~$170,000 | WA/QLD FIFO含轮班津贴 |
| 矿业Shutdown合同工 | $150,000~$220,000 | 关停期间日薪$900~$1,200+ |

---

## 2. 谁适合学仪表技术员？

- 有工业仪表、DCS/PLC控制或过程自动化背景，目标技能移民来澳
- 接受FIFO工作模式，追求矿业高薪
- 有意在油气或矿业行业长期发展

## 谁不适合学仪表技术员？

- 不接受偏远地区FIFO模式
- 完全没有电气或仪表背景
- 期望完全城市内工作

---

## 3. 常见问题

**澳洲仪表技术员工资多少？**
中级技术员年薪约 $90,000~$125,000。FIFO油气方向可达 $120,000~$170,000，矿业关停合同工可达 $220,000+。

**澳洲仪表技术员容易找工作吗？**
非常容易。油气/矿业/水处理全面旺盛，FIFO技术员极度稀缺。

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
    print("[OK] 仪表技术员（Instrumentation Technician）入库+Markdown完成")
if __name__ == "__main__": run()
