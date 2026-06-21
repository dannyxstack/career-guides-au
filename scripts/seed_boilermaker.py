"""Boilermaker (322111) 锅炉工/钢结构制造工 — AU market data 2025-2026"""
import sys, os, re, json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
TODAY = date.today()
OCCUPATION = {
    "anzsco_code": "322111", "anzsco_title": "Boilermaker",
    "category": "技工", "workforce_size": 25000, "shortage_listed": 1,
    "growth_areas": json.dumps(["Mining & Resource Processing","Oil & Gas Vessels & Piping","Renewable Energy Fabrication","Defence Shipbuilding"], ensure_ascii=False),
}
I18N_ZH = {"locale": "zh-CN", "name": "锅炉工",
    "summary": "锅炉工（Boilermaker）负责制造、安装、维修压力容器、储罐、钢结构件和管道系统，广泛应用于矿业、石油天然气、造船和制造业。澳大利亚资源行业旺盛，加上国防造船项目，持证锅炉工长期处于短缺状态。",
    "forecast_note": "WA/QLD矿业和油气行业FIFO锅炉工持续短缺。国防造船（Hunter级驱逐舰/攻击型潜艇）2025年起创造大量制造业岗位。可再生能源（风塔/储能容器）制造需求新增。",
    "trend_summary": "自动化焊接辅助提升效率，但高级焊接技能（TIG/压力容器）仍稀缺。矿业关停（shutdown）期间日薪率极高，是澳洲最高薪技工之一。"}
I18N_EN = {"locale": "en", "name": "Boilermaker",
    "summary": "Boilermakers fabricate, install and repair pressure vessels, tanks, steel structures and pipe systems used in mining, oil and gas, shipbuilding and manufacturing. Classified under ANZSCO 322111, persistent demand from Australia's resource sector and defence shipbuilding program creates sustained shortages.",
    "forecast_note": "WA/QLD mining and oil and gas FIFO boilermaker roles persistently under-staffed. Defence shipbuilding (Hunter-class frigates/Attack-class submarines) creates major manufacturing jobs from 2025. Renewable energy fabrication adding new demand.",
    "trend_summary": "Automated welding aids efficiency but high-grade welding skills (TIG/pressure vessel) remain scarce. Mining shutdown day rates extremely high, making this one of Australia's top-earning trade roles."}
EDUCATION = [
    {"stage": "Certificate III in Engineering (Fabrication Trade)", "duration": "42~48个月（学徒）", "cost_min": 0, "cost_max": 3000, "cost_note": "各州差异；工具费约$1,500~$2,500", "sort_order": 0},
    {"stage": "海外资质互认（TRA）", "duration": "12~18个月", "cost_min": 2000, "cost_max": 5000, "cost_note": "TRA评估费", "sort_order": 1},
    {"stage": "Pressure Vessel Welding Certification（压力容器焊接）", "duration": "1~3个月", "cost_min": 1000, "cost_max": 3000, "cost_note": "AS/NZS 2980焊工认证", "sort_order": 2},
]
QUALIFICATIONS = [
    {"qual_name": "Certificate III in Engineering Fabrication", "issuer": "TAFE / RTO", "note": "执业核心资质", "is_mandatory": 1, "sort_order": 0},
    {"qual_name": "Pressure Vessel Welding Certificate (AS 2980)", "issuer": "WTIA认可机构", "note": "矿业和油气方向必备", "is_mandatory": 0, "sort_order": 1},
    {"qual_name": "TRA Skills Assessment", "issuer": "TRA", "note": "海外学历移民", "is_mandatory": 0, "sort_order": 2},
    {"qual_name": "White Card", "issuer": "各州SafeWork", "note": "工地强制", "is_mandatory": 1, "sort_order": 3},
]
JOB_LISTINGS = [
    {"platform": "Seek", "count_min": 400, "count_max": 800, "note": "全国，WA/QLD矿业集中"},
    {"platform": "Indeed", "count_min": 200, "count_max": 450, "note": "含FIFO职位"},
    {"platform": "LinkedIn", "count_min": 80, "count_max": 200, "note": "偏造船和大型工程"},
]
SALARIES = [
    {"experience": "学徒（0~4年）", "salary_min": 30000, "salary_max": 62000, "salary_note": "Metal Industry Award", "sort_order": 0},
    {"experience": "初级锅炉工（1~3年）", "salary_min": 75000, "salary_max": 95000, "salary_note": "制造业或建筑施工", "sort_order": 1},
    {"experience": "中级锅炉工（3~8年）", "salary_min": 95000, "salary_max": 130000, "salary_note": "Seek均值约$45~$62/hr（2026）", "sort_order": 2},
    {"experience": "矿业FIFO / 关停专家（8年+）", "salary_min": 130000, "salary_max": 200000, "salary_note": "WA/QLD FIFO+关停津贴；日薪$1,000~$1,400", "sort_order": 3},
]
VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS", "description": "雇主担保，最长4年", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "永居", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州提名加5分", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远矿区加15分", "sort_order": 3},
]
RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中高", "stars": 4, "note": "焊接技能（TIG/MIG）和压力容器规范学习量大"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "Certificate III+TRA+压力容器焊接认证"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "矿业+造船+可再生全面旺盛，持续短缺"},
    {"dimension": "competition",              "label_zh": "极低", "stars": 1, "note": "持证锅炉工极度稀缺，矿业FIFO更抢手"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "重工业体力，高温环境，关停期间高强度"},
    {"dimension": "income_level",             "label_zh": "极高", "stars": 5, "note": "FIFO $130k~$200k；关停合同工$200k+"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "国防造船2025+大量新岗，矿业长期高位"},
    {"dimension": "ai_risk",                  "label_zh": "较低", "stars": 2, "note": "焊接自动化在发展，但高难度焊缝仍需人工"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，偏远矿区491加分"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语+积分"},
]
SUITABILITY_FIT = [
    "有焊接、钢结构制造或压力容器经验，目标技能移民来澳",
    "接受FIFO和高强度工业环境，追求矿业顶级薪资",
    "有意在国防造船或矿业行业长期发展",
]
SUITABILITY_UNFIT = [
    "不接受高温重工业环境和FIFO模式",
    "无焊接基础（培训周期长）",
    "期望室内轻体力工作",
]
SOURCES = [
    {"source_name": "JSA", "content": "ANZSCO 322111 数据", "url": "https://www.jobsandskills.gov.au/"},
    {"source_name": "Seek AU", "content": "Boilermaker 薪资及挂牌量（2026）", "url": "https://www.seek.com.au/boilermaker-jobs"},
    {"source_name": "Department of Home Affairs", "content": "CSOL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA", "content": "海外技工互认", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]
FAQS = [
    {"faq_type": "salary", "sort_order": 0, "question": "澳洲锅炉工工资多少？", "answer": "中级锅炉工年薪约 $95,000~$130,000（约$45~$62/hr）。矿业FIFO可达 $130,000~$200,000，关停合同工可达 $200,000+。"},
    {"faq_type": "demand", "sort_order": 1, "question": "澳洲锅炉工容易找工作吗？", "answer": "非常容易。矿业+造船+可再生全面旺盛，持证锅炉工极度稀缺，Seek挂牌400~800个职位。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内焊接经验澳洲认可吗？", "answer": "需TRA评估（12~18个月）。有焊工证书和实操记录者评估顺利，压力容器焊接需单独认证。"},
    {"faq_type": "ai_risk", "sort_order": 3, "question": "锅炉工会被机器人替代吗？", "answer": "较低。焊接自动化在发展，但高难度焊缝（TIG/压力容器）和现场修复仍需持证人员。"},
    {"faq_type": "education_limit", "sort_order": 4, "question": "需要大学文凭吗？", "answer": "不需要。Certificate III+压力容器焊接认证即可入行，FIFO雇主主要看实操经验。"},
]
MARKDOWN = """# 锅炉工（Boilermaker）职业分析 · 澳大利亚

**职业代码：322111 – Boilermaker。**

锅炉工负责制造、安装、维修压力容器、储罐和钢结构件，广泛应用于矿业、油气、造船和制造业。澳大利亚资源行业旺盛和国防造船项目，使持证锅炉工长期处于极度短缺状态，矿业FIFO收入是技工类最高之一。

---

## 1. 薪资范围

**收入水平：极高（★★★★★）。**

| 经验阶段 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $30,000~$62,000 | Metal Industry Award |
| 初级锅炉工（1~3年） | $75,000~$95,000 | 制造业或建筑施工 |
| 中级锅炉工（3~8年） | $95,000~$130,000 | 约$45~$62/hr（2026） |
| 矿业FIFO / 关停专家（8年+） | $130,000~$200,000 | WA/QLD FIFO；关停日薪$1,000~$1,400 |

---

## 2. 谁适合学锅炉工？

- 有焊接、钢结构制造或压力容器经验，目标技能移民来澳
- 接受FIFO和高强度工业环境，追求矿业顶级薪资
- 有意在国防造船或矿业行业长期发展

## 谁不适合学锅炉工？

- 不接受高温重工业环境和FIFO模式
- 无焊接基础（培训周期长）
- 期望室内轻体力工作

---

## 3. 常见问题

**澳洲锅炉工工资多少？**
中级锅炉工年薪约 $95,000~$130,000。矿业FIFO可达 $130,000~$200,000，关停合同工可达 $200,000+。

**澳洲锅炉工容易找工作吗？**
非常容易。矿业+造船+可再生全面旺盛，持证锅炉工极度稀缺。

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
    print("[OK] 锅炉工（Boilermaker）入库+Markdown完成")
if __name__ == "__main__": run()
