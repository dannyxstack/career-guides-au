"""
Steel Fixer (821713) 钢筋工
数据来源：Jobs and Skills Australia、CFMEU Victoria EBA 2026、Seek/Indeed/Glassdoor、
         Department of Home Affairs、Fair Work Commission (2025-2026)
"""
import sys, os, json, re
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

TODAY = date.today()

OCCUPATION = {
    "anzsco_code":    "821713",
    "anzsco_title":   "Steel Fixer",
    "category":       "技工",
    "workforce_size": 22000,
    "shortage_listed": 1,
    "growth_areas":   json.dumps([
        "Residential & High-Rise Construction",
        "Civil Infrastructure (Roads, Bridges, Tunnels)",
        "Wind Farm & Renewable Energy Structures",
        "Mining & Industrial Construction",
    ], ensure_ascii=False),
}

I18N_ZH = {
    "locale": "zh-CN",
    "name": "钢筋工",
    "summary": "钢筋工（Steel Fixer）负责在混凝土结构中放置、绑扎和固定钢筋，适用于住宅、桥梁、隧道、大坝等各类工程。在澳大利亚，钢筋工属于技工短缺职业，住宅建设繁荣与基建投资双线驱动需求持续增长。",
    "forecast_note": "Jobs and Skills Australia 将建筑技工类列为持续短缺职业，技工类（Skill Level 3/4）岗位填补率仅54.3%（2025）。联邦政府「住宅未来基金」计划至2029年新建120万套住宅，将进一步拉动钢筋工需求。",
    "trend_summary": "大型基建（地铁、隧道、桥梁）和风电场建设带动需求稳定增长。机械辅助（钢筋弯折机、绑扎机器人）在大型项目应用增加，但现场人工作业仍不可替代。",
}

I18N_EN = {
    "locale": "en",
    "name": "Steel Fixer",
    "summary": "Steel Fixers position, cut, bend and fasten steel reinforcing bars in concrete structures including buildings, bridges, tunnels and dams. In Australia, they are classified under ANZSCO 821713 and remain in consistent demand across residential, civil and industrial construction.",
    "forecast_note": "JSA identifies construction trades as persistently undersupplied. Skill Level 3/4 vacancy fill rate has dropped to 54.3%. Federal Housing Future Fund targets 1.2M new homes by 2029, underpinning long-term demand.",
    "trend_summary": "Major civil infrastructure and wind farm construction drive steady demand. Rebar tying robots are used on large sites but on-site manual work remains dominant.",
}

EDUCATION = [
    {
        "stage": "学徒制 Apprenticeship（含TAFE课程 CPC32320）",
        "duration": "42~48个月（约3.5~4年）",
        "cost_min": 0,
        "cost_max": 2000,
        "cost_note": "各州差异：NSW/QLD 补贴后几乎免费；WA约$800~$2,000；书本工具费$500~$1,000",
        "sort_order": 0,
    },
    {
        "stage": "海外资质互认（TRA Job Ready Program）",
        "duration": "12~18个月",
        "cost_min": 2000,
        "cost_max": 5000,
        "cost_note": "TRA评估费、补考、实习期行政费",
        "sort_order": 1,
    },
    {
        "stage": "WHS建筑业入职白卡（Construction Induction）",
        "duration": "1天",
        "cost_min": 50,
        "cost_max": 150,
        "cost_note": "全国强制，在工地开工前必须持有",
        "sort_order": 2,
    },
]

QUALIFICATIONS = [
    {
        "qual_name": "Certificate III in Concreting (CPC30820) 或 Certificate III in Formwork/Falsework",
        "issuer": "TAFE / RTO",
        "note": "全国统一课程，钢筋绑扎与混凝土施工核心资质",
        "is_mandatory": 1,
        "sort_order": 0,
    },
    {
        "qual_name": "White Card（WHS建筑业入职卡）",
        "issuer": "SafeWork NSW / WorkSafe 各州",
        "note": "工地开工前强制持有",
        "is_mandatory": 1,
        "sort_order": 1,
    },
    {
        "qual_name": "Basic Rigging Licence（RB）",
        "issuer": "SafeWork / WorkSafe 各州",
        "note": "矿业和大型工程现场常要求，提升薪资竞争力",
        "is_mandatory": 0,
        "sort_order": 2,
    },
    {
        "qual_name": "TRA Skills Assessment",
        "issuer": "Trades Recognition Australia (TRA)",
        "note": "海外学历移民必须，澳洲学徒豁免",
        "is_mandatory": 0,
        "sort_order": 3,
    },
]

JOB_LISTINGS = [
    {"platform": "Seek",     "count_min": 400,  "count_max": 700,  "note": "全国，含矿业FIFO和住宅工程岗"},
    {"platform": "Indeed",   "count_min": 200,  "count_max": 450,  "note": "含承包商和劳务外包岗位"},
    {"platform": "LinkedIn", "count_min": 80,   "count_max": 200,  "note": "偏大型工程及矿业直招"},
]

SALARIES = [
    {
        "experience": "学徒（0~4年）",
        "salary_min": 28000, "salary_max": 55000,
        "salary_note": "Fair Work Award，按年级递增",
        "sort_order": 0,
    },
    {
        "experience": "初级钢筋工（持证后 1~3年）",
        "salary_min": 70000, "salary_max": 88000,
        "salary_note": "Seek AU 2026，住宅与商业工程",
        "sort_order": 1,
    },
    {
        "experience": "中级钢筋工（3~8年）",
        "salary_min": 88000, "salary_max": 110000,
        "salary_note": "Indeed 全国均值约 $45.47/hr；含EBA加班津贴",
        "sort_order": 2,
    },
    {
        "experience": "资深钢筋工 / 带班（8年+）",
        "salary_min": 110000, "salary_max": 135000,
        "salary_note": "Vic EBA 2026 Grade 2 = $58.46/hr×2080h≈$121k；含津贴更高",
        "sort_order": 3,
    },
    {
        "experience": "矿业 FIFO 钢筋工（WA/QLD）",
        "salary_min": 130000, "salary_max": 180000,
        "salary_note": "含FIFO津贴、轮班费，WA矿区顶端可达$180k+",
        "sort_order": 4,
    },
]

VISA_PATHWAYS = [
    {"visa_subclass": "482", "visa_name": "TSS（Skills in Demand）", "description": "雇主担保，中期技能流最长4年，2年后可转186", "sort_order": 0},
    {"visa_subclass": "186", "visa_name": "ENS", "description": "雇主担保永久居留，TRT流需持482满2年", "sort_order": 1},
    {"visa_subclass": "190", "visa_name": "Skilled Nominated", "description": "州政府提名，加5分，永居", "sort_order": 2},
    {"visa_subclass": "491", "visa_name": "Skilled Work Regional", "description": "偏远地区提名加15分，临居转PR，适合189分数不够者", "sort_order": 3},
]

RATINGS = [
    {"dimension": "learning_difficulty",      "label_zh": "中等", "stars": 3, "note": "体力为主，技术进阶在绑扎精度和图纸读取"},
    {"dimension": "learning_duration",        "label_zh": "较长", "stars": 4, "note": "学徒3.5~4年；TRA互认12~18个月"},
    {"dimension": "certification_difficulty", "label_zh": "中等", "stars": 3, "note": "White Card强制；TRA评估中等难度"},
    {"dimension": "job_demand",               "label_zh": "极高", "stars": 5, "note": "建筑住宅+基建双驱动，持续短缺职业"},
    {"dimension": "competition",              "label_zh": "较低", "stars": 2, "note": "供不应求，持证后工作机会多"},
    {"dimension": "work_intensity",           "label_zh": "高",   "stars": 4, "note": "重体力劳动，户外高温/严寒，弯腰跪地作业多"},
    {"dimension": "income_level",             "label_zh": "中高", "stars": 4, "note": "中位 $88k~$110k；FIFO可达 $180k"},
    {"dimension": "future_prospect",          "label_zh": "极佳", "stars": 5, "note": "住宅短缺政策驱动，2030前需求量持续增加"},
    {"dimension": "ai_risk",                  "label_zh": "极低", "stars": 1, "note": "现场人工绑扎，机器人仅在大型项目试点"},
    {"dimension": "pr_friendliness",          "label_zh": "极高", "stars": 5, "note": "CSOL在列，多签证路径可用"},
    {"dimension": "pr_difficulty",            "label_zh": "中等", "stars": 3, "note": "TRA评估+英语是主要障碍"},
]

SUITABILITY_FIT = [
    "有建筑、土木施工背景，希望通过技能移民来澳",
    "接受重体力户外劳动，不抵触高温、噪音、泥泞工地环境",
    "目标是矿业FIFO高薪或长期定居澳洲",
    "年龄25~40岁，有充裕时间完成TRA评估",
]

SUITABILITY_UNFIT = [
    "不愿意从事重体力劳动，或有腰背部慢性伤病",
    "期望坐办公室、从事技术/管理类工作",
    "英语基础极弱且无意改善（工地沟通和安全培训均需英语）",
]

SOURCES = [
    {"source_name": "Jobs and Skills Australia", "content": "ANZSCO 821713 Steel Fixer 职业短缺数据", "url": "https://www.jobsandskills.gov.au/data/occupation-and-industry-profiles/occupations/821713-steel-fixers"},
    {"source_name": "CFMEU Victoria EBA 2026",  "content": "建筑行业工资协议 Grade 2 = $58.46/hr", "url": "https://vic.cfmeu.org/wp-content/uploads/2026/02/2026-Onsite-EBA-Rates.pdf"},
    {"source_name": "Seek AU",                  "content": "钢筋工职位挂牌量及薪资数据（2026）", "url": "https://www.seek.com.au/steel-fixer-jobs"},
    {"source_name": "Indeed AU",                "content": "Steel Fixer 平均时薪 $45.47（2025-2026）", "url": "https://au.indeed.com/career/ironworker/salaries"},
    {"source_name": "Department of Home Affairs","content": "CSOL / MLTSSL 职业清单", "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list"},
    {"source_name": "TRA",                      "content": "海外技工互认 Job Ready Program", "url": "https://www.tradesrecognitionaustralia.gov.au/"},
]

FAQS = [
    {"faq_type": "salary",      "sort_order": 0, "question": "澳洲钢筋工工资多少？",           "answer": "中级钢筋工年薪（AUD）约 $88,000~$110,000，全国均值约 $45/hr（Indeed 2026）。矿业FIFO可达 $130,000~$180,000+。学徒期间约 $28,000~$55,000。"},
    {"faq_type": "demand",      "sort_order": 1, "question": "澳洲钢筋工容易找工作吗？",       "answer": "容易。建筑行业持续短缺，Seek常年挂牌400~700个职位。持证钢筋工通常1~2周内可入职，矿业FIFO岗竞争略高但薪资翻倍。"},
    {"faq_type": "recognition", "sort_order": 2, "question": "国内钢筋工资质澳洲认可吗？",     "answer": "不直接认可。需通过TRA Job Ready Program评估，周期约12~18个月，费用约$2,000~$5,000。完成评估后还需取得各州White Card方可上工地。"},
    {"faq_type": "ai_risk",     "sort_order": 3, "question": "钢筋工会被AI或机器人替代吗？",   "answer": "短期内几乎不会。钢筋绑扎机器人（如TyBot）仅在特定大型工程试用，复杂结构和空间受限区域仍需人工。AI替代风险极低。"},
    {"faq_type": "age_limit",   "sort_order": 4, "question": "澳洲钢筋工有年龄限制吗？",       "answer": "法律无上限。学徒入学偏好35岁以下；40岁以上可走TRA互认跳过学徒期。技术移民打分45岁以上无加分。"},
    {"faq_type": "education_limit", "sort_order": 5, "question": "需要大学文凭吗？",          "answer": "不需要。Certificate III（职业技术证书）即可执业，相当于高中+职校水平。重要的是体力素质和施工经验。"},
    {"faq_type": "difficulty",  "sort_order": 6, "question": "钢筋工难学吗？",                "answer": "难度中等。技术核心在于看懂结构图纸、精准计算钢筋规格和绑扎顺序，以及安全意识。体力要求高，上手需半年到一年现场实操经验。"},
    {"faq_type": "comparison",  "sort_order": 7, "question": "钢筋工和脚手架工（Scaffolder）哪个更适合移民澳洲？", "answer": "两者均在CSOL列表，PR路径相近。钢筋工需求量略大，更易进入住宅和矿业市场；脚手架工薪资相当但岗位总量较少。详见「钢筋工 vs 脚手架工」职业比较板块（即将上线）。"},
]

MD_SLUG = "steel-fixer"

MARKDOWN = f"""# 钢筋工（Steel Fixer）职业分析 · 澳大利亚

**职业代码：821713 – Steel Fixer。**

钢筋工（Steel Fixer）负责在混凝土结构中放置、绑扎和固定钢筋，适用于住宅、桥梁、隧道、大坝等各类工程。在澳大利亚，钢筋工属于技工短缺职业，住宅建设繁荣与基建投资双线驱动需求持续增长。

---

## 1. 教育路径 / 周期 / 费用

**学习难度：中等（★★★☆☆）。** 核心技能在于读懂结构图纸、精准计算钢筋规格，以及安全意识和体力适应。

| 阶段 | 周期 | 费用（AUD） |
|---|---|---:|
| 学徒制 Apprenticeship（含TAFE课程 CPC32320） | 42~48个月（约3.5~4年） | $0~$2,000（NSW/QLD补贴后接近免费；WA约$800~$2,000；工具费$500~$1,000） |
| 海外资质互认（TRA Job Ready Program） | 12~18个月 | $2,000~$5,000 |
| WHS建筑业入职白卡（Construction Induction） | 1天 | $50~$150 |

---

## 2. 考证难度 / 从业资质

**考证难度：中等（★★★☆☆）。** 必须持有White Card方可进入任何工地，Certificate III是执业基础资质。

| 资质 | 发证机构 | 备注 |
|---|---|---|
| Certificate III in Concreting (CPC30820) | TAFE / RTO | 全国统一课程，核心执业资质 |
| White Card（WHS建筑业入职卡） | SafeWork / WorkSafe 各州 | 工地开工前强制持有 |
| Basic Rigging Licence（RB） | 各州 | 矿业和大型工程现场常要求 |
| TRA Skills Assessment | TRA | 海外学历移民必须 |

---

## 3. 职位需求量 / 竞争度 / 工作强度

**职位需求量：极高（★★★★★）。** Jobs and Skills Australia 将建筑技工类列为持续短缺，技工类岗位填补率仅54.3%（2025）。联邦「住宅未来基金」计划2029年新建120万套住宅，将进一步拉动需求。

| 平台 | 实时挂牌量（约） | 备注 |
|---|---:|---|
| Seek | 400~700 个 | 全国，含矿业FIFO和住宅工程岗 |
| Indeed | 200~450 个 | 含承包商和劳务外包岗 |
| LinkedIn | 80~200 个 | 偏大型工程及矿业直招 |

**竞争度：较低（★★☆☆☆）。** 供不应求，持证后工作机会多，尤其是WA/QLD矿业方向。
**工作强度：高（★★★★☆）。** 重体力劳动，户外高温/严寒，弯腰跪地作业多，腰背负担较重。

---

## 4. 收入范围（学徒 / 中级 / 资深）

| 经验水平 | 年薪（AUD） | 备注 |
|---|---:|---|
| 学徒（0~4年） | $28,000~$55,000 | Fair Work Award，按年级递增 |
| 初级（持证后1~3年） | $70,000~$88,000 | 住宅与商业工程 |
| 中级（3~8年） | $88,000~$110,000 | Indeed均值~$45/hr；含EBA加班津贴 |
| 资深 / 带班（8年+） | $110,000~$135,000 | Vic EBA 2026 Grade 2 = $58.46/hr |
| 矿业 FIFO（WA/QLD） | $130,000~$180,000 | 含FIFO津贴、轮班费 |

---

## 5. 未来趋势 / AI替代概率

**AI替代风险：极低（★☆☆☆☆）。** 钢筋绑扎机器人（如TyBot）在特定大型项目试用，但复杂结构和受限空间仍需人工，短期内不构成威胁。
**发展前景：极佳（★★★★★）。** 联邦和各州基建投资（地铁、高铁、公路）及住宅短缺政策将维持高需求至2030年以后。

主要增长方向：住宅建设、大型基建（地铁/隧道）、风电场结构、矿业工业设施。

---

## 6. 移民路径 / PR难度

**PR难度：中等（★★★☆☆）。** TRA评估周期长（12~18个月）和英语要求是主要障碍，但签证路径多样。

| 签证 | 类型 | 说明 |
|---|---|---|
| 482 TSS | 临时 | 雇主担保，最长4年，可转186 |
| 186 ENS | 永居 | 雇主担保，TRT流需持482满2年 |
| 190 | 永居 | 州政府提名，加5分 |
| 491 | 临时转永居 | 偏远地区提名，加15分 |

**PR友好度：极高（★★★★★）。** 列入CSOL，四条主流签证路径均可用。

---

## 7. 适合人群 / 不适合人群

**谁适合学钢筋工？**
- 有建筑、土木施工背景，希望通过技能移民来澳
- 接受重体力户外劳动，不抵触高温、噪音、泥泞工地环境
- 目标是矿业FIFO高薪或长期定居澳洲
- 年龄25~40岁，有充裕时间完成TRA评估

**谁不适合学钢筋工？**
- 不愿意从事重体力劳动，或有腰背部慢性伤病
- 期望坐办公室、从事技术/管理类工作
- 英语基础极弱且无意改善

---

## 8. 数据来源

| 来源 | 内容 |
|---|---|
| Jobs and Skills Australia | ANZSCO 821713 短缺数据、就业预测 |
| CFMEU Victoria EBA 2026 | 建筑行业工资协议 Grade 2 = $58.46/hr |
| Seek / Indeed AU | 职位挂牌量及薪资数据（2026） |
| Department of Home Affairs | CSOL 职业清单、签证条件 |
| TRA | 海外技工互认 Job Ready Program |
| Fair Work Commission | 学徒 Award 最低工资 |

## 快速结论

| 维度 | 评级 |
|---|---|
| 学习周期 | 较长（★★★★☆） |
| 学习难度 | 中等（★★★☆☆） |
| 职位需求量 | 极高（★★★★★） |
| 竞争度 | 较低（★★☆☆☆） |
| AI替代风险 | 极低（★☆☆☆☆） |
| 收入水平 | 中高（★★★★☆） |
| PR友好度 | 极高（★★★★★） |

钢筋工是澳大利亚建筑行业最紧缺的技工之一，技术门槛中等、入行路径清晰，适合有施工背景的技术移民。FIFO矿业方向薪资最高，普通住宅工程也稳定可靠。建议优先完成TRA评估，结合190州提名或482雇主担保路线规划移民路径。

---

## 9. FAQ 常见问题

**问：澳洲钢筋工工资多少？**
答：中级钢筋工年薪（AUD）约 $88,000~$110,000，全国均值约 $45/hr（Indeed 2026）。矿业FIFO可达 $130,000~$180,000+。学徒期间约 $28,000~$55,000。

**问：澳洲钢筋工容易找工作吗？**
答：容易。建筑行业持续短缺，Seek常年挂牌400~700个职位。持证钢筋工通常1~2周内可入职，矿业FIFO岗竞争略高但薪资翻倍。

**问：国内钢筋工资质澳洲认可吗？**
答：不直接认可。需通过TRA Job Ready Program评估，周期约12~18个月，费用约$2,000~$5,000。完成评估后还需取得各州White Card方可上工地。

**问：钢筋工会被AI或机器人替代吗？**
答：短期内几乎不会。钢筋绑扎机器人仅在特定大型工程试用，复杂结构和空间受限区域仍需人工。AI替代风险极低。

**问：澳洲钢筋工有年龄限制吗？**
答：法律无上限。学徒入学偏好35岁以下；40岁以上可走TRA互认跳过学徒期。技术移民打分45岁以上无加分。

**问：需要大学文凭吗？**
答：不需要。Certificate III（职业技术证书）即可执业，高中毕业+技校水平即可入读TAFE学徒课程。

**问：钢筋工难学吗？**
答：难度中等。技术核心在于读懂结构图纸、精准计算钢筋规格，以及安全意识。体力要求高，上手需半年到一年现场实操。

**问：钢筋工和脚手架工（Scaffolder）哪个更适合移民澳洲？**
答：两者均在CSOL列表，PR路径相近。钢筋工需求量略大，更易进入住宅和矿业市场；脚手架工薪资相当但岗位总量较少。详见「钢筋工 vs 脚手架工」职业比较板块（即将上线）。
"""


def to_slug(name):
    import re
    s = name.lower()
    s = re.sub(r'[/()\[\]]', ' ', s)
    s = re.sub(r'[^a-z0-9 ]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    return re.sub(r'-+', '-', s)


def run():
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO occupations
              (anzsco_code,anzsco_title,category,workforce_size,shortage_listed,growth_areas)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              anzsco_title=VALUES(anzsco_title), category=VALUES(category),
              workforce_size=VALUES(workforce_size), shortage_listed=VALUES(shortage_listed),
              growth_areas=VALUES(growth_areas)
        """, (OCCUPATION["anzsco_code"], OCCUPATION["anzsco_title"], OCCUPATION["category"],
              OCCUPATION["workforce_size"], OCCUPATION["shortage_listed"], OCCUPATION["growth_areas"]))
        cur.execute("SELECT id FROM occupations WHERE anzsco_code=%s", (OCCUPATION["anzsco_code"],))
        occ_id = cur.fetchone()["id"]
        print(f"[occupations] id={occ_id}  {OCCUPATION['anzsco_code']} {OCCUPATION['anzsco_title']}")

        for i18n in [I18N_ZH, I18N_EN]:
            cur.execute("""
                INSERT INTO occupations_i18n (occupation_id,locale,name,summary,forecast_note,trend_summary)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE name=VALUES(name),summary=VALUES(summary),
                  forecast_note=VALUES(forecast_note),trend_summary=VALUES(trend_summary)
            """, (occ_id, i18n["locale"], i18n["name"], i18n["summary"], i18n["forecast_note"], i18n["trend_summary"]))
        print("[occupations_i18n] 2 locales")

        cur.execute("DELETE FROM occupation_ratings WHERE occupation_id=%s", (occ_id,))
        for r in RATINGS:
            cur.execute("INSERT INTO occupation_ratings (occupation_id,dimension,label_zh,stars,note) VALUES (%s,%s,%s,%s,%s)",
                        (occ_id, r["dimension"], r["label_zh"], r["stars"], r.get("note")))
        print(f"[ratings] {len(RATINGS)}")

        cur.execute("DELETE FROM occupation_education WHERE occupation_id=%s", (occ_id,))
        for e in EDUCATION:
            cur.execute("INSERT INTO occupation_education (occupation_id,stage,duration,cost_min,cost_max,cost_note,sort_order) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (occ_id, e["stage"], e["duration"], e["cost_min"], e["cost_max"], e["cost_note"], e["sort_order"]))
        print(f"[education] {len(EDUCATION)}")

        cur.execute("DELETE FROM occupation_qualifications WHERE occupation_id=%s", (occ_id,))
        for q in QUALIFICATIONS:
            cur.execute("INSERT INTO occupation_qualifications (occupation_id,qual_name,issuer,note,is_mandatory,sort_order) VALUES (%s,%s,%s,%s,%s,%s)",
                        (occ_id, q["qual_name"], q.get("issuer"), q.get("note"), q["is_mandatory"], q["sort_order"]))
        print(f"[qualifications] {len(QUALIFICATIONS)}")

        cur.execute("DELETE FROM occupation_job_listings WHERE occupation_id=%s", (occ_id,))
        for jl in JOB_LISTINGS:
            cur.execute("INSERT INTO occupation_job_listings (occupation_id,platform,count_min,count_max,note,snapshot_date) VALUES (%s,%s,%s,%s,%s,%s)",
                        (occ_id, jl["platform"], jl["count_min"], jl["count_max"], jl["note"], TODAY))
        print(f"[job_listings] {len(JOB_LISTINGS)}")

        cur.execute("DELETE FROM occupation_salaries WHERE occupation_id=%s", (occ_id,))
        for s in SALARIES:
            cur.execute("INSERT INTO occupation_salaries (occupation_id,experience,salary_min,salary_max,salary_note,sort_order) VALUES (%s,%s,%s,%s,%s,%s)",
                        (occ_id, s["experience"], s["salary_min"], s["salary_max"], s["salary_note"], s["sort_order"]))
        print(f"[salaries] {len(SALARIES)}")

        cur.execute("DELETE FROM occupation_visa_pathways WHERE occupation_id=%s", (occ_id,))
        for v in VISA_PATHWAYS:
            cur.execute("INSERT INTO occupation_visa_pathways (occupation_id,visa_subclass,visa_name,description,sort_order) VALUES (%s,%s,%s,%s,%s)",
                        (occ_id, v["visa_subclass"], v["visa_name"], v["description"], v["sort_order"]))
        print(f"[visa_pathways] {len(VISA_PATHWAYS)}")

        cur.execute("DELETE FROM occupation_suitability WHERE occupation_id=%s", (occ_id,))
        for i, item in enumerate(SUITABILITY_FIT):
            cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'fit',%s,%s)", (occ_id, item, i))
        for i, item in enumerate(SUITABILITY_UNFIT):
            cur.execute("INSERT INTO occupation_suitability (occupation_id,type,item,sort_order) VALUES(%s,'unfit',%s,%s)", (occ_id, item, i))
        print(f"[suitability] {len(SUITABILITY_FIT)} fit / {len(SUITABILITY_UNFIT)} unfit")

        cur.execute("DELETE FROM occupation_sources WHERE occupation_id=%s", (occ_id,))
        for s in SOURCES:
            cur.execute("INSERT INTO occupation_sources (occupation_id,source_name,content,url) VALUES (%s,%s,%s,%s)",
                        (occ_id, s["source_name"], s.get("content"), s.get("url")))
        print(f"[sources] {len(SOURCES)}")

        cur.execute("DELETE FROM occupation_faqs WHERE occupation_id=%s", (occ_id,))
        for faq in FAQS:
            cur.execute("INSERT INTO occupation_faqs (occupation_id,faq_type,sort_order) VALUES(%s,%s,%s)",
                        (occ_id, faq["faq_type"], faq["sort_order"]))
            faq_id = cur.lastrowid
            cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'zh-CN',%s,%s) ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",
                        (faq_id, faq["question"], faq["answer"]))
        print(f"[faqs] {len(FAQS)}")

    # 写 Markdown
    out_dir = os.path.join(os.path.dirname(__file__), "..", "career-contents", "au")
    os.makedirs(out_dir, exist_ok=True)
    slug = to_slug(I18N_EN["name"])
    md_path = os.path.join(out_dir, f"{slug}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(MARKDOWN.strip() + "\n")
    print(f"[markdown] {md_path}")
    print("\n[OK] 钢筋工（Steel Fixer）数据入库完成")


if __name__ == "__main__":
    run()
