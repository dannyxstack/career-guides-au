"""为现有(AU)职业批量生成『加拿大(NOC)对应版本』核心数据并入库、出中英 markdown。

对每个 AU 职业，用 DeepSeek 生成加拿大对应职业的：NOC 码/英文名/中文名、中英简介、
教育路径、资质(WES/ECA/省牌照)、薪资(CAD)、移民路径(Express Entry/PNP/AIP)、
11 维评分(10 分制)、适合人群、FAQ(中英)、增长热词。经 seed_occupation_v2 入库，
再 generate_md 出 zh-CN + en 两份 markdown。

注意：NOC 码/薪资/移民资格均为 LLM 最佳估计，上线前需二次核对。
- 幂等：处理过的 AU 职业 id 记到 .codex_tmp/ca_done.json，重跑跳过；
        生成的 NOC 若已存在于 CA(撞码)则跳过该 AU 职业，避免覆盖。
- 批次：--batch-size 每批(默认 50)，--rest 批间休息秒数(默认 1200=20 分钟)。
- 评分 10 分制；FAQ 同时写 zh-CN 与 en。

运行：python -m scripts.gen_ca_occupations [--batch-size 50] [--rest 1200] [--limit N] [--redo]
"""
import sys, os, json, argparse, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from db.connection import get_cursor
from _seed_helper import seed_occupation_v2
from pipeline.generators.md_generator import generate_md
from video_pipeline import config
from gen_ai_disruptors import _parse_list  # 复用容错解析

STATE = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "ca_done.json")

DIMS = ["learning_difficulty", "learning_duration", "certification_difficulty", "job_demand",
        "competition", "work_intensity", "income_level", "future_prospect",
        "ai_risk", "pr_friendliness", "pr_difficulty"]

SYSTEM = (
    "你是加拿大移民与劳动力市场分析师，熟悉 NOC 2021 职业分类、Job Bank 薪资、"
    "Express Entry(FSW/CEC/类别抽签)、各省提名(PNP)与 ECA 学历认证。"
    "针对给定的源职业，输出其在【加拿大】对应职业的务实、具体数据。"
    "薪资用加元(CAD)整数年薪。中文面向国际读者，不要提『华人/中文社区』。"
    "只输出一个 JSON 对象，不要多余文字。"
)


def build_prompt(name_zh, name_en, category, summary_zh):
    dims = "、".join(DIMS)
    return f"""源职业(澳洲)：
- 中文名：{name_zh or name_en}
- 英文名：{name_en}
- 分类：{category}
- 简介：{(summary_zh or '')[:300]}

请输出该职业在【加拿大】对应职业的 JSON，字段如下（全部必填）：
- noc_code：加拿大 NOC 2021 五位代码（字符串，如 "21231"；若加拿大无明确对应职业，填 ""）
- noc_title_en：NOC 对应英文职业名
- name_zh：中文职业名
- summary_zh / summary_en：一句话简介（中/英，各 60-140 字/词，需点明加拿大移民可行性）
- forecast_note_zh：加拿大就业前景一段（60-120 字）
- trend_summary_zh：职业发展/晋升路径一段（60-120 字）
- is_migration：0/1/2（0=非技术移民职业；1=可走 Express Entry/PNP 技术移民；2=受限/仅雇主或省担保）
- shortage：0 或 1（是否加拿大紧缺职业）
- workforce_size：加拿大从业人数估计（整数）
- growth：增长/热点关键词英文数组（4 个，如 "Express Entry STEM"、"Provincial Nominee"）
- education：数组，每项{{stage:中文阶段, duration:如"4年", cost_min:整数CAD, cost_max:整数CAD, cost_note:中文}}（2-3 项）
- qualifications：数组，每项{{qual_name:中文, issuer:机构, note:中文, is_mandatory:0或1}}（2-4 项，含 ECA/省牌照/语言考试）
- salaries：数组，每项{{experience:中文如"初级（0-3年）", salary_min:整数CAD, salary_max:整数CAD, salary_note:中文}}（3 档：初/中/高）
- visa：数组，每项{{visa_subclass:如"EE"/"PNP"/"AIP", visa_name:英文, description:中文}}（2-4 项加拿大移民路径）
- ratings：对象，键为这 11 个维度：{dims}；每个值为 [中文档位label, 分数]，分数是 1.0-10.0 的 10 分制小数（注意：ai_risk/competition/work_intensity/learning_difficulty/learning_duration/certification_difficulty/pr_difficulty 为负向，越高越差）
- fit：适合人群中文数组（2-3 条）
- unfit：不适合人群中文数组（2 条）
- faqs：数组，每项{{faq_type:"salary"或"migration"等, question_zh, answer_zh, question_en, answer_en}}（2-3 条，含薪资与移民各一）
只输出真实合理的加拿大数据；不确定的薪资给保守区间。"""


def clamp10(v, d=5.0):
    try:
        return round(max(1.0, min(10.0, float(v))), 1)
    except (TypeError, ValueError):
        return d


def validate(raw):
    noc = str(raw.get("noc_code") or "").strip()
    if not noc:
        return None
    g = lambda k: (raw.get(k) or "").strip()
    out = {
        "noc": noc, "title_en": g("noc_title_en") or g("name_zh"), "name_zh": g("name_zh"),
        "summary_zh": g("summary_zh"), "summary_en": g("summary_en"),
        "forecast_note_zh": g("forecast_note_zh"), "trend_summary_zh": g("trend_summary_zh"),
        "is_migration": int(raw.get("is_migration")) if str(raw.get("is_migration")) in ("0", "1", "2") else 1,
        "shortage": 1 if raw.get("shortage") in (1, "1", True) else 0,
        "workforce_size": int(raw["workforce_size"]) if str(raw.get("workforce_size", "")).isdigit() else None,
    }
    if not (out["name_zh"] and out["summary_zh"] and out["summary_en"]):
        return None
    out["growth"] = [str(x).strip() for x in (raw.get("growth") or []) if str(x).strip()][:6]
    out["education"] = [{"stage": e.get("stage", ""), "duration": e.get("duration", ""),
                         "cost_min": e.get("cost_min"), "cost_max": e.get("cost_max"),
                         "cost_note": e.get("cost_note", ""), "sort_order": i}
                        for i, e in enumerate(raw.get("education") or []) if e.get("stage")]
    out["qual"] = [{"qual_name": q.get("qual_name", ""), "issuer": q.get("issuer", ""),
                    "note": q.get("note", ""), "is_mandatory": 1 if q.get("is_mandatory") in (1, "1", True) else 0,
                    "sort_order": i} for i, q in enumerate(raw.get("qualifications") or []) if q.get("qual_name")]
    out["sal"] = [{"experience": s.get("experience", ""), "salary_min": s.get("salary_min"),
                   "salary_max": s.get("salary_max"), "salary_note": s.get("salary_note", ""), "sort_order": i}
                  for i, s in enumerate(raw.get("salaries") or []) if s.get("experience")]
    out["visa"] = [{"visa_subclass": v.get("visa_subclass", ""), "visa_name": v.get("visa_name", ""),
                    "description": v.get("description", ""), "sort_order": i}
                   for i, v in enumerate(raw.get("visa") or []) if v.get("visa_subclass")]
    rr = raw.get("ratings") or {}
    out["ratings"] = []
    for d in DIMS:
        val = rr.get(d)
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            label, score = str(val[0]).strip() or "中等", clamp10(val[1])
        else:
            label, score = "中等", clamp10(val)
        out["ratings"].append({"dimension": d, "label_zh": label, "stars": score})
    out["fit"] = [str(x).strip() for x in (raw.get("fit") or []) if str(x).strip()][:4]
    out["unfit"] = [str(x).strip() for x in (raw.get("unfit") or []) if str(x).strip()][:3]
    out["faqs"] = [{"faq_type": f.get("faq_type", "other"), "question_zh": f.get("question_zh", ""),
                    "answer_zh": f.get("answer_zh", ""), "question_en": f.get("question_en", ""),
                    "answer_en": f.get("answer_en", ""), "sort_order": i}
                   for i, f in enumerate(raw.get("faqs") or []) if f.get("question_zh")]
    if not (out["sal"] and out["visa"] and out["ratings"] and out["faqs"]):
        return None
    return out


def gen(name_zh, name_en, category, summary_zh):
    from openai import OpenAI
    client = OpenAI(api_key=config.require("DEEPSEEK_API_KEY"), base_url=config.DEEPSEEK_BASE_URL)
    resp = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL, max_tokens=4000,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": build_prompt(name_zh, name_en, category, summary_zh)}],
        response_format={"type": "json_object"})
    data = _parse_list(resp.choices[0].message.content)  # 容错；可能返回 [obj] 或 obj
    if isinstance(data, list):
        data = data[0] if data else {}
    return data if isinstance(data, dict) else {}


def save(au, v):
    """入库 + 英文 FAQ + 中英 md。返回 (occ_id, noc)。"""
    OCC = {"country_code": "CA", "occ_code": v["noc"], "anzsco_code": v["noc"],
           "occ_code_type": "NOC", "anzsco_title": v["title_en"], "category": au["category"],
           "currency": "CAD", "workforce_size": v["workforce_size"], "shortage_listed": v["shortage"],
           "is_migration": v["is_migration"], "is_public_servant": 0,
           "growth_areas": json.dumps(v["growth"], ensure_ascii=False)}
    ZH = {"locale": "zh-CN", "name": v["name_zh"], "summary": v["summary_zh"],
          "forecast_note": v["forecast_note_zh"], "trend_summary": v["trend_summary_zh"]}
    EN = {"locale": "en", "name": v["title_en"], "summary": v["summary_en"],
          "forecast_note": v["forecast_note_zh"], "trend_summary": v["trend_summary_zh"]}
    faqs_zh = [{"faq_type": f["faq_type"], "sort_order": f["sort_order"],
                "question": f["question_zh"], "answer": f["answer_zh"]} for f in v["faqs"]]
    src = [{"source_name": "Job Bank", "content": "NOC 薪资与需求", "url": "https://www.jobbank.gc.ca/"}]
    with get_cursor() as cur:
        occ_id = seed_occupation_v2(cur, OCC, ZH, EN, v["education"], v["qual"], [], v["sal"],
                                    v["visa"], v["ratings"], v["fit"], v["unfit"], src, faqs_zh)
        # 英文 FAQ：按 sort_order 取回 faq_id，补写 en i18n
        cur.execute("SELECT id FROM occupation_faqs WHERE occupation_id=%s ORDER BY sort_order", (occ_id,))
        fids = [r["id"] for r in cur.fetchall()]
        for f, fid in zip(v["faqs"], fids):
            if f.get("question_en"):
                cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'en',%s,%s) "
                            "ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",
                            (fid, f["question_en"], f.get("answer_en") or f["answer_zh"]))
    generate_md(v["noc"], locale="zh-CN", country="CA")
    generate_md(v["noc"], locale="en", country="CA")
    return occ_id, v["noc"]


def load_state():
    if os.path.exists(STATE):
        try:
            return set(json.load(open(STATE, encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_state(done):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(sorted(done), open(STATE, "w", encoding="utf-8"))


def run(batch_size, rest, limit, redo):
    with get_cursor() as cur:
        cur.execute("SELECT o.id,o.category,i.name AS name_zh,i.summary AS summary_zh,o.anzsco_title AS name_en "
                    "FROM occupations o LEFT JOIN occupations_i18n i ON i.occupation_id=o.id AND i.locale='zh-CN' "
                    "WHERE o.country_code='AU' ORDER BY o.category,o.id")
        au_list = cur.fetchall()
        cur.execute("SELECT occ_code FROM occupations WHERE country_code='CA'")
        ca_nocs = {r["occ_code"] for r in cur.fetchall()}
    done = set() if redo else load_state()
    targets = [o for o in au_list if o["id"] not in done]
    if limit:
        targets = targets[:limit]
    n = len(targets)
    nb = (n + batch_size - 1) // batch_size if batch_size else 1
    print(f"[ca] 待生成 {n} 个(分 {nb} 批，每批 {batch_size}，批间休息 {rest}s) model={config.DEEPSEEK_MODEL}", flush=True)
    okc = fail = skip = 0
    for bi in range(nb):
        chunk = targets[bi * batch_size:(bi + 1) * batch_size]
        print(f"\n===== 批次 {bi+1}/{nb}（{len(chunk)} 个）开始 {time.strftime('%H:%M:%S')} =====", flush=True)
        for idx, au in enumerate(chunk, 1):
            tag = f"b{bi+1} {idx}/{len(chunk)} {au['name_en']}"
            try:
                v = validate(gen(au["name_zh"], au["name_en"], au["category"], au["summary_zh"]))
                if not v:
                    raise ValueError("数据不完整/无 NOC")
                if v["noc"] in ca_nocs:
                    skip += 1
                    done.add(au["id"]); save_state(done)
                    print(f"  [{tag}] 跳过：NOC {v['noc']} 已存在", flush=True)
                    continue
                occ_id, noc = save(au, v)
                ca_nocs.add(noc)
                done.add(au["id"]); save_state(done)
                okc += 1
                print(f"  [{tag}] → CA id={occ_id} NOC={noc} {v['name_zh']} mig={v['is_migration']}", flush=True)
            except Exception as e:
                fail += 1
                print(f"  [{tag}] 失败: {e}", flush=True)
        print(f"===== 批次 {bi+1}/{nb} 完成（累计 成功{okc} 跳过{skip} 失败{fail}）{time.strftime('%H:%M:%S')} =====", flush=True)
        if bi < nb - 1:
            print(f"[rest] 休息 {rest}s……", flush=True)
            time.sleep(rest)
    print(f"\n[OK] 全部完成：成功 {okc}，跳过 {skip}，失败 {fail}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--rest", type=int, default=1200)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    run(a.batch_size, a.rest, a.limit, a.redo)
