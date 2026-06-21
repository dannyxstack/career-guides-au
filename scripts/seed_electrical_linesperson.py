"""Electrical Linesperson (341112) 电力线工 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "341112", "anzsco_title": "Electrical Linesperson",
    "category": "技工", "workforce_size": 20000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Renewable Energy Grid Connection","Transmission Line Upgrades","Underground Cable Installation","Storm Restoration & Emergency Response"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "电力线工",
    "summary": "电力线工（Electrical Linesperson）负责架空和地下输配电线路的建设、维护和修复。澳大利亚电网升级以支持可再生能源接入，加上老化基础设施更新，使电力线工处于极度短缺状态，是技工类中薪资最高的职业之一。",
    "forecast_note": "联邦电网现代化计划（Transmission Infrastructure，$650亿+）带动大量线路建设需求。可再生能源（风电/太阳能）并网需要大量新建和升级输电线路。各州电网老化更新周期加快。",
    "trend_summary": "地下电缆（Underground Cable）替代架空线路成为城市趋势，技术要求和薪资更高。紧急风暴恢复（Storm Restoration）跨州应急部署薪资可达普通工资的3~4倍。"}
I18N_EN = {"locale": "en", "name": "Electrical Linesperson",
    "summary": "Electrical Linespersons construct, maintain and repair overhead and underground power transmission and distribution lines. Classified under ANZSCO 341112, Australia's grid modernisation program and renewable energy connection requirements create extreme shortages of qualified linespersons.",
    "forecast_note": "Federal grid modernisation ($65B+ Transmission Infrastructure) drives line construction demand. Renewable energy (wind/solar) grid connection requires large new and upgraded transmission lines. Ageing network replacement accelerating.",
    "trend_summary": "Underground cabling replacing overhead lines in urban areas with higher technical and pay requirements. Storm restoration emergency deployment pays 3-4x normal rates."}
EDUCATION = [
    {"stage": "Certificate III in ESI (Power Systems - Distribution Overhead)", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州差异；工具费约$1,500~$2,500", "sort_order": 0},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 1},
    {"stage": "Underground Cable Jointing（地下电缆接头，加分）", "duration": "2~4周", "cost_min": 1000, "cost_max": 3000, "cost_note": "厂商认证；城市地下方向必备", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in ESI Power Systems", "issuer": "TAFE / RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Electrical Linesperson Licence", "issuer": "各州电气监管机构", "note": "强制持证执业", "is_mandatory": 1, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 2},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 300, "count_max": 600, "note": "全国，网络公司和承包商均有"},
    {"platform": "Indeed", "count_min": 150, "count_max": 350, "note": "含应急恢复职位"},
    {"platform": "LinkedIn", "count_min": 80, "count_max": 200, "note": "偏输电大型项目"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 35000, "salary_max": 65000, "salary_note": "ESI Award", "sort_order": 0},
    {"experience": "初级线工（0~3年）", "salary_min": 80000, "salary_max": 105000, "salary_note": "配电网络公司", "sort_order": 1},
    {"experience": "中级线工（3~8年）", "salary_min": 105000, "salary_max": 140000, "salary_note": "Seek均值约$50~$65/hr（2026）", "sort_order": 2},
    {"experience": "资深 / 输电专家（8年+）", "salary_min": 135000, "salary_max": 180000, "salary_note": "输电大项目；风暴恢复加倍", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远输电线路加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "高压安全规范和架空/地下系统技术要求高"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年+州持证"},
    {"dimension": "certification_difficulty", "label_zh": "中高", "stars": 4, "note": "州持证+TRA评估；高压作业要求严格"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "电网现代化+可再生并网，需求爆发式增长"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "持证线工极度稀缺，全行业争抢"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "高空架线，全天候作业，风暴恢复高强度应急"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "中位$105k~$140k；输电大项目和风暴恢复$180k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "电网现代化十年规划，长期需求确定"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "高压现场作业和应急响应无法自动化"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，多路径，偏远地区491加分"},
    {"dimension": "pr_difficulty",            "label_zh": "中高", "stars": 4, "note": "TRA评估+州持证+英语"},
]
SUITABILITY_FIT = [
    "有电力线路、配电网络或电气施工背景，目标技能移民来澳",
    "不惧全天候高空作业和紧急应急响应，追求顶级技工薪资",
    "有意在电网基础设施行业长期发展，职业路径清晰",
]
SUITABILITY_UNFIT = [
    "恐高或对高压作业有心理障碍",
    "不接受全天候紧急值班模式",
    "期望稳定规律的室内工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 341112 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Electrical Linesperson 薪资（2026）", "url": "https://www.seek.com.au/electrical-linesperson-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲电力线工工资多少？", "answer": "中级线工年薪约 $105,000~$140,000（约$50~$65/hr）。输电大项目和风暴恢复应急可达 $135,000~$180,000+。是技工类薪资最高的职业之一。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲电力线工容易找工作吗？", "answer": "非常容易。电网现代化十年规划，Seek挂牌300~600个职位，持证线工极度稀缺，几乎零失业。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内输电线路工经验澳洲认可吗？", "answer": "需TRA评估（12~18个月）后申请各州持证。有高压作业经验和NPTC/相关资质者评估更顺利。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "电力线工会被机器人替代吗？", "answer": "极低。高压现场作业、架线判断和紧急应急响应需要持证人员现场负责，无法自动化。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III+州持证即可，高中毕业可入读TAFE学徒。"},
]
MARKDOWN = """# 电力线工（Electrical Linesperson）职业分析 · 澳大利亚

**职业代码：341112 – Electrical Linesperson。**

电力线工负责架空和地下输配电线路的建设、维护和修复。澳大利亚电网升级和可再生能源并网需求使电力线工处于极度短缺状态，是技工类中薪资最高的职业之一。

---

## 1. 薪资范围

**收入水平：极高（★★★★★）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $35,000~$65,000 | ESI Award |
| 初级线工（0~3年） | $80,000~$105,000 | 配电网络公司 |
| 中级线工（3~8年） | $105,000~$140,000 | 约$50~$65/hr（2026） |
| 资深 / 输电专家（8年+） | $135,000~$180,000 | 输电大项目；风暴恢复加倍 |

---

## 2. 谁适合学电力线工？

- 有电力线路、配电网络或电气施工背景，目标技能移民来澳
- 不惧全天候高空作业和紧急应急响应，追求顶级技工薪资
- 有意在电网基础设施行业长期发展

## 谁不适合学电力线工？

- 恐高或对高压作业有心理障碍
- 不接受全天候紧急值班模式
- 期望稳定规律的室内工作

---

## 3. 常见问题

**澳洲电力线工工资多少？**
中级线工年薪约 $105,000~$140,000（约$50~$65/hr）。输电大项目和风暴恢复应急可达 $135,000~$180,000+。

**澳洲电力线工容易找工作吗？**
非常容易。电网现代化十年规划，持证线工极度稀缺，几乎零失业。

**电力线工会被机器人替代吗？**
极低。高压现场作业和紧急应急响应需要持证人员，无法自动化。

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
    print("[OK] 电力线工（Electrical Linesperson）入库+Markdown完成")
if __name__ == "__main__": run()
