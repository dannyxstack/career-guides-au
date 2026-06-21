"""样本：2 个加拿大(NOC) + 2 个新西兰(ANZSCO) 职业入库 + 生成 markdown。
演示多国支持：country_code / currency / 本国签证路径 / 本币薪资。
薪资为联网检索(Job Bank/Seek NZ/PayScale/Glassdoor 2025-2026)区间估算，仍需二次核对。
可重复运行(幂等)。运行：python -m scripts.seed_intl_sample（需先跑 migrate_currency）
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from db.connection import get_cursor
from _seed_helper import seed_occupation_v2
from pipeline.generators.md_generator import generate_md


def R(d): return [{"dimension": k, "label_zh": v[0], "stars": v[1]} for k, v in d.items()]
def EDU(rows): return [{"stage": s, "duration": dur, "cost_min": a, "cost_max": b, "cost_note": n, "sort_order": i} for i, (s, dur, a, b, n) in enumerate(rows)]
def QUAL(rows): return [{"qual_name": q, "issuer": iss, "note": nt, "is_mandatory": m, "sort_order": i} for i, (q, iss, nt, m) in enumerate(rows)]
def LIST(rows): return [{"platform": p, "count_min": a, "count_max": b, "note": n} for (p, a, b, n) in rows]
def SAL(rows): return [{"experience": e, "salary_min": a, "salary_max": b, "salary_note": n, "sort_order": i} for i, (e, a, b, n) in enumerate(rows)]
def VISA(rows): return [{"visa_subclass": s, "visa_name": nm, "description": d, "sort_order": i} for i, (s, nm, d) in enumerate(rows)]
def FAQ(rows): return [{"faq_type": t, "sort_order": i, "question": q, "answer": a} for i, (t, q, a) in enumerate(rows)]

OCCS = [
 # ===================== 加拿大 CA (NOC 2021) =====================
 dict(cc="CA", curr="CAD", code="31301", ctype="NOC", en="Registered Nurse", zh="注册护士",
      cat="Healthcare & Care", mig=1, short=1, wf=320000,
      growth=["Express Entry Health", "Provincial Nominee", "Ageing Population", "Acute & Community Care"],
      sum_zh="注册护士在加拿大医院、社区与长期照护机构提供护理，是各省持续紧缺职业，可走快速通道(Express Entry)与省提名(PNP)技术移民，需通过 NNAS 评估与省护理学院注册。",
      sum_en="Registered nurses provide care across hospitals, community and long-term care in Canada; an in-demand occupation with Express Entry and PNP pathways, subject to NNAS assessment and provincial registration.",
      fc="加拿大人口老龄化与护士短缺使注册护士需求长期旺盛，各省提名与联邦快速通道均设护理优先类别。",
      tr="路径：注册护士→专科/高级执业护士(NP)；通过 NNAS 评估、省护理学院注册与英语/法语成绩是关键。",
      edu=[("Bachelor of Science in Nursing (BScN)", "4年", 30000, 90000, "国际生学费更高"),
           ("NNAS 评估 + 省护理学院注册", "6~12个月", 1000, 4000, "执业前提")],
      qual=[("Provincial College of Nurses 注册", "各省护理学院(如 CNO)", "强制执业", 1),
            ("NCLEX-RN 考试", "NCSBN", "注册要求", 1),
            ("NNAS 国际护士评估", "NNAS", "国际申请人", 0)],
      listings=[("Job Bank", 8000, 15000, "全国"), ("Indeed CA", 6000, 12000, "全国")],
      sal=[("初级（0-3年）", 70000, 85000, "Entry"), ("中级（3-8年）", 85000, 100000, "Experienced"), ("资深 / 专科", 100000, 120000, "Senior")],
      visa=VISA([("EE", "Express Entry (FSW/CEC)", "联邦快速通道，含 Healthcare category 类别抽签"),
                 ("PNP", "Provincial Nominee", "省提名，多省设护理优先流"),
                 ("AIP", "Atlantic Immigration", "大西洋四省雇主担保")]),
      rat={"learning_difficulty": ("中高", 4), "learning_duration": ("较长", 4), "certification_difficulty": ("中高", 4),
           "job_demand": ("旺盛", 5), "competition": ("较低", 2), "work_intensity": ("高", 4), "income_level": ("中等", 3),
           "future_prospect": ("良好", 5), "ai_risk": ("很低", 1), "pr_friendliness": ("高", 5), "pr_difficulty": ("较低", 2)},
      fit=["想移民加拿大的护理专业者", "能通过 NNAS 与英语/法语考试者", "愿在各省灵活就业者"],
      unfit=["不愿读护理学位或考注册者", "排斥轮班与高强度临床者"],
      faqs=[("salary", "加拿大注册护士薪资多少？", "约 CAD $7万~$12万，省份与经验差异大，阿尔伯塔/安省/BC 偏高。"),
            ("migration", "注册护士能移民加拿大吗？", "可以。护理是紧缺职业，可走 Express Entry(含医疗类别)与多省 PNP，需 NNAS 评估与省注册。")]),

 dict(cc="CA", curr="CAD", code="21231", ctype="NOC", en="Software Engineer", zh="软件工程师",
      cat="IT & Digital", mig=1, short=1, wf=200000,
      growth=["Express Entry STEM", "Tech PNP (BC/ON)", "Cloud & AI", "Remote Work"],
      sum_zh="软件工程师(NOC 21231)在加拿大设计开发软件系统，是科技移民的核心职业，可走快速通道 STEM 类别抽签及 BC/安省等科技省提名，薪资高、需求稳定。",
      sum_en="Software engineers (NOC 21231) design and build software systems in Canada; a core tech-immigration occupation with Express Entry STEM draws and BC/Ontario tech PNP streams, well-paid and in demand.",
      fc="加拿大科技业与 STEM 类别快速通道抽签推动软件工程师需求强劲，高级与架构岗薪资可观。",
      tr="路径：开发→高级→架构/技术主管；云、AI 与系统设计经验显著提升薪资与移民竞争力。",
      edu=[("计算机相关本科", "4年", 30000, 100000, "国际生学费更高"),
           ("ECA 学历认证(WES 等)", "数周~数月", 200, 500, "移民用")],
      qual=[("相关学历 + ECA 认证", "WES / IQAS 等", "移民评估", 0),
            ("英语 IELTS/CELPIP 或法语 TEF", "认可考点", "移民要求", 0)],
      listings=[("Job Bank", 6000, 12000, "全国"), ("LinkedIn CA", 8000, 16000, "全国")],
      sal=[("初级（0-3年）", 70000, 95000, "Entry"), ("中级（3-8年）", 100000, 130000, "Experienced"), ("资深 / 架构", 150000, 200000, "Senior，含股票更高")],
      visa=VISA([("EE", "Express Entry (STEM)", "联邦快速通道，含 STEM occupations 类别抽签"),
                 ("PNP", "Provincial Nominee (Tech)", "BC PNP Tech / 安省 OINP 科技流"),
                 ("GTS", "Global Talent Stream", "雇主担保快速工签")]),
      rat={"learning_difficulty": ("中高", 4), "learning_duration": ("较长", 4), "certification_difficulty": ("较低", 2),
           "job_demand": ("旺盛", 5), "competition": ("中等", 3), "work_intensity": ("中高", 4), "income_level": ("高", 5),
           "future_prospect": ("良好", 5), "ai_risk": ("中等", 3), "pr_friendliness": ("高", 5), "pr_difficulty": ("较低", 2)},
      fit=["想科技移民加拿大的开发者", "有云/AI/系统设计经验者", "英语或法语达标者"],
      unfit=["不愿持续学习新技术者", "以非技术岗为目标者"],
      faqs=[("salary", "加拿大软件工程师薪资多少？", "约 CAD $7万~$20万，多伦多/温哥华高级岗及含股票更高。"),
            ("migration", "软件工程师能移民加拿大吗？", "可以，且很有优势。Express Entry 设 STEM 类别抽签，BC/安省有科技省提名流。")]),

 # ===================== 新西兰 NZ (ANZSCO) =====================
 dict(cc="NZ", curr="NZD", code="254418", ctype="ANZSCO", en="Registered Nurse", zh="注册护士",
      cat="Healthcare & Care", mig=1, short=1, wf=70000,
      growth=["Green List Tier 1", "Te Whatu Ora", "Ageing Population", "Aged & Community Care"],
      sum_zh="注册护士在新西兰医院与社区提供护理，列入新西兰技能短缺 Green List 一级(可直接申请居留)，可走技术移民(SMC)与认可雇主工签(AEWV)，需经护理委员会(NCNZ)注册。",
      sum_en="Registered nurses provide care across New Zealand hospitals and community settings; on the Green List Tier 1 (straight-to-residence), with SMC and AEWV pathways, subject to Nursing Council (NCNZ) registration.",
      fc="新西兰护士长期短缺、列入 Green List 一级，居留与就业通道顺畅，需求持续旺盛。",
      tr="路径：注册护士→专科/高级护士；通过 NCNZ 注册、CAP 过渡课程与英语成绩是关键。",
      edu=[("Bachelor of Nursing", "3年", 25000, 75000, "国际生学费更高"),
           ("NCNZ 注册 + CAP 过渡课程", "数月", 3000, 12000, "海外护士执业前提")],
      qual=[("Nursing Council of NZ (NCNZ) 注册", "NCNZ", "强制执业", 1),
            ("英语成绩 (IELTS/OET)", "认可考点", "注册要求", 1)],
      listings=[("Seek NZ", 3000, 6000, "全国"), ("Kiwi Health Jobs", 1500, 3000, "公立医疗")],
      sal=[("初级 / 新毕业（0-3年）", 75000, 85000, "Step 起薪"), ("中级（3-8年）", 85000, 100000, "Experienced"), ("资深 / Step 7+", 106000, 128000, "Senior")],
      visa=VISA([("GreenList", "Green List Tier 1", "技能短缺一级，可直接申请居留"),
                 ("SMC", "Skilled Migrant Category", "技术移民打分制"),
                 ("AEWV", "Accredited Employer Work Visa", "认可雇主工签")]),
      rat={"learning_difficulty": ("中高", 4), "learning_duration": ("较长", 4), "certification_difficulty": ("中高", 4),
           "job_demand": ("旺盛", 5), "competition": ("较低", 2), "work_intensity": ("高", 4), "income_level": ("中等", 3),
           "future_prospect": ("良好", 5), "ai_risk": ("很低", 1), "pr_friendliness": ("高", 5), "pr_difficulty": ("很低", 1)},
      fit=["想移民新西兰的护理专业者", "能通过 NCNZ 注册与英语考试者"],
      unfit=["不愿读护理学位或考注册者", "排斥轮班与临床压力者"],
      faqs=[("salary", "新西兰注册护士薪资多少？", "约 NZD $7.5万~$12.8万，资深 Step 7+ 更高，奥克兰偏高。"),
            ("migration", "注册护士能移民新西兰吗？", "可以，且很顺畅。注册护士在 Green List 一级，可直接申请居留，亦可走 SMC/AEWV。")]),

 dict(cc="NZ", curr="NZD", code="341111", ctype="ANZSCO", en="Electrician", zh="电工",
      cat="Trades & Construction", mig=1, short=1, wf=25000,
      growth=["Green List Tier 2", "Construction Boom", "Renewable Energy", "Registration (EWRB)"],
      sum_zh="电工在新西兰从事建筑、工业与维护电气安装，列入 Green List 二级(工作满期后可申请居留)，可走认可雇主工签(AEWV)与技术移民(SMC)，需经 EWRB 注册持牌。",
      sum_en="Electricians install and maintain electrical systems across construction, industry and maintenance in New Zealand; on the Green List Tier 2 (work-to-residence), with AEWV and SMC pathways, requiring EWRB registration/licensing.",
      fc="新西兰建筑与可再生能源推动电工需求，列入 Green List 二级，持 EWRB 牌照者就业与居留通道顺畅。",
      tr="路径：学徒→注册电工→工头/承包；EWRB 注册、牌照等级与专业(高压/可再生)决定收入。",
      edu=[("电工学徒制 (NZ Apprenticeship)", "3~4年", 0, 8000, "边学边赚"),
           ("EWRB 注册与执照", "数周", 300, 1500, "强制持牌")],
      qual=[("Electrical Workers Registration Board (EWRB) 注册", "EWRB", "强制持牌", 1),
            ("NZ Certificate in Electrical Engineering (L4)", "Te Pūkenga/RTO", "入行基础", 1)],
      listings=[("Seek NZ", 1500, 3000, "全国"), ("Trade Me Jobs", 1000, 2200, "全国")],
      sal=[("学徒 / 初级（0-3年）", 55000, 68000, "Apprentice~Entry"), ("中级（3-8年）", 70000, 90000, "Experienced"), ("资深 / 承包", 95000, 130000, "Senior")],
      visa=VISA([("GreenList", "Green List Tier 2", "技能短缺二级，工作满期后可申请居留"),
                 ("AEWV", "Accredited Employer Work Visa", "认可雇主工签"),
                 ("SMC", "Skilled Migrant Category", "技术移民打分制")]),
      rat={"learning_difficulty": ("中等", 3), "learning_duration": ("中等", 3), "certification_difficulty": ("中高", 4),
           "job_demand": ("旺盛", 5), "competition": ("较低", 2), "work_intensity": ("中高", 4), "income_level": ("中等", 3),
           "future_prospect": ("良好", 4), "ai_risk": ("很低", 1), "pr_friendliness": ("高", 4), "pr_difficulty": ("较低", 2)},
      fit=["想走技工移民新西兰者", "动手能力强、愿读学徒制者"],
      unfit=["排斥现场体力作业者", "不愿考 EWRB 注册者"],
      faqs=[("salary", "新西兰电工薪资多少？", "约 NZD $5.5万~$13万，承包与高压专业更高。"),
            ("migration", "电工能移民新西兰吗？", "可以。电工在 Green List 二级(工作满期后可申请居留)，需 EWRB 注册持牌。")]),
]

SRC = lambda cc: ([{"source_name": "Job Bank", "content": "NOC 薪资与需求", "url": "https://www.jobbank.gc.ca/"}] if cc == "CA"
                  else [{"source_name": "Seek NZ", "content": "薪资与岗位量", "url": "https://www.seek.co.nz/"}])


def run():
    ok = 0
    for o in OCCS:
        OCC = {
            "country_code": o["cc"], "occ_code": o["code"], "anzsco_code": o["code"],
            "occ_code_type": o["ctype"], "anzsco_title": o["en"], "category": o["cat"],
            "currency": o["curr"], "workforce_size": o["wf"], "shortage_listed": o["short"],
            "is_migration": o["mig"], "is_public_servant": 0,
            "growth_areas": json.dumps(o["growth"], ensure_ascii=False),
        }
        ZH = {"locale": "zh-CN", "name": o["zh"], "summary": o["sum_zh"], "forecast_note": o["fc"], "trend_summary": o["tr"]}
        EN = {"locale": "en", "name": o["en"], "summary": o["sum_en"], "forecast_note": o["fc"], "trend_summary": o["tr"]}
        with get_cursor() as cur:
            seed_occupation_v2(cur, OCC, ZH, EN, EDU(o["edu"]), QUAL(o["qual"]),
                               LIST(o["listings"]), SAL(o["sal"]), o["visa"], R(o["rat"]),
                               o["fit"], o["unfit"], SRC(o["cc"]), FAQ(o["faqs"]))
        path = generate_md(o["code"], country=o["cc"])
        print(f"  [md] {o['cc']} {o['zh']} -> {getattr(path, 'name', path)}")
        ok += 1
    print(f"[OK] 国际样本入库完成 {ok}/{len(OCCS)}")


if __name__ == "__main__":
    run()
