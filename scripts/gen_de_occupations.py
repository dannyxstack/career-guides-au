"""为德国(KldB 2010)职业批量生成核心数据并入库、出中英 markdown。

对 KldB 2010 四位 Berufsuntergruppen 清单（.codex_tmp/soc_de.json，已剔除 "sonstige" 兜底类）
中的每个职业，用 DeepSeek 生成：英文职业名、中文名、中英简介、教育路径、资质/认证、薪资(EUR)、
德国工作/居留路径(EU Blue Card / 技术移民法 Skilled Worker / 机会卡 Chancenkarte / 资质认证 Anerkennung)、
11 维评分(10 分制)、适合人群、FAQ(中英)、增长热词，并从【现有 AU/CA/US/UK 职业候选池】中选出
最接近的母体（match_name/match_country，方式 a），供后续复制 ai-block。
经 seed_occupation_v2 入库，再 generate_md 出 zh-CN + en 两份 markdown。

注意：KldB 标题为德文，英文名(name_en)由 LLM 产出；薪资/签证资格/评分均为 LLM 最佳估计，上线前需二次核对。
- 分类：LLM 从站点现有 11 个分类中择一。
- 移民语义(is_migration)：考虑欧盟自由流动——0=第三国难担保/几乎无技术移民路径；
  1=可走 EU Blue Card / 技术移民法担保（紧缺或对口学历）；2=受限（需资质认证 Anerkennung/受规管职业/门槛高）。
- ai-block 母体匹配写入 .codex_tmp/de_ai_match.json：{occ_id: {country, occ_code, src_occ_id}}（无匹配则不写）。
- 幂等：处理过的 KldB 码记到 .codex_tmp/de_done.json，重跑跳过；码已存在于 DE 则跳过。
- 批次：--batch-size 每批(默认 50)，--rest 批间休息秒数(默认 0)。

运行：python -m scripts.gen_de_occupations [--batch-size 50] [--rest 0] [--limit N] [--redo]
"""
import sys, os, json, argparse, time, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from db.connection import get_cursor
from _seed_helper import seed_occupation_v2
from pipeline.generators.md_generator import generate_md
from video_pipeline import config
from gen_ai_disruptors import _parse_list

SOC_LIST = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "soc_de.json")
STATE = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "de_done.json")
MATCH = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "de_ai_match.json")

CATEGORIES = [
    "Agriculture & Environment", "Business, Finance & Legal",
    "Creative, Media & Personal Services", "Education & Community",
    "Engineering & Infrastructure", "Government & Public Sector",
    "Healthcare & Care", "Hospitality, Retail & Tourism", "IT & Digital",
    "Trades & Construction", "Transport, Logistics & Mining",
]

DIMS = ["learning_difficulty", "learning_duration", "certification_difficulty", "job_demand",
        "competition", "work_intensity", "income_level", "future_prospect",
        "ai_risk", "pr_friendliness", "pr_difficulty"]


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def build_system(pool):
    """pool: [(country, occ_code, name_en, occ_id)]，作为 ai-block 母体匹配候选（进 system，命中缓存）。"""
    names = sorted({p[2] for p in pool if p[2]})
    cats = "、".join(CATEGORIES)
    listing = " | ".join(names)
    return (
        "你是德国劳动力市场与移民分析师，熟悉 KldB 2010 职业分类、德国联邦劳工局(BA)与联邦统计局(destatis)薪资数据、"
        "欧盟内自由流动，以及第三国技术移民路径(EU Blue Card 蓝卡 / 技术移民法 Fachkräfteeinwanderungsgesetz / "
        "机会卡 Chancenkarte / 资质认证 Anerkennung)。"
        "针对给定的德国 KldB 职业（标题为德文），输出务实、具体的德国数据。薪资用欧元(EUR)整数年薪(税前 brutto)。"
        "中文面向国际读者，不要提『华人/中文社区』。\n"
        f"职业分类只能从以下 11 类中选一个（原文照填）：{cats}\n"
        "另需从下列【现有职业候选池】中选出与该德国职业最接近的同一职业（用于复用分析），"
        "把候选池中的英文名原样填入 match_name；若没有足够接近的则 match_name 填 \"\"。\n"
        f"候选池：{listing}\n"
        "只输出一个 JSON 对象，不要多余文字。"
    )


def build_prompt(kldb, title_de, definition):
    dims = "、".join(DIMS)
    return f"""德国 KldB 2010 职业：
- KldB 码：{kldb}
- 德文名：{title_de}

请输出该德国职业的 JSON，字段如下（全部必填）：
- name_en：标准英文职业名（把德文职业名译成地道、通用的英文职业名，单数，首字母大写，用于全站英文展示与匹配）
- name_zh：中文职业名
- category：从给定 11 类中选一个（原文照填）
- summary_zh / summary_en：一句话简介（中/英，各 60-140 字/词）
- forecast_note_zh：德国就业前景一段（60-120 字）
- trend_summary_zh：职业发展/晋升路径一段（60-120 字）
- is_migration：0/1/2（考虑欧盟自由流动；0=第三国难担保/几乎无技术移民路径；1=可走 EU Blue Card/技术移民法担保（紧缺或对口学历）；2=受限/需资质认证/受规管职业）
- shortage：0 或 1（是否德国紧缺职业 Engpassberuf）
- workforce_size：德国从业人数估计（整数）
- growth：增长/热点关键词英文数组（4 个）
- education：数组，每项{{stage:中文阶段, duration:如"3年（双元制）", cost_min:整数EUR, cost_max:整数EUR, cost_note:中文}}（2-3 项，注意德国双元制 Ausbildung）
- qualifications：数组，每项{{qual_name:中文, issuer:机构, note:中文, is_mandatory:0或1}}（2-4 项，含执照/认证/学位/资质认证 Anerkennung）
- salaries：数组，每项{{experience:中文如"初级（0-3年）", salary_min:整数EUR, salary_max:整数EUR, salary_note:中文}}（3 档：初/中/高，税前年薪）
- visa：数组，每项{{visa_subclass:如"EU Blue Card"/"Skilled Worker"/"Chancenkarte"/"Job Seeker", visa_name:英文, description:中文}}（2-4 项德国工作/居留路径）
- ratings：对象，键为这 11 个维度：{dims}；每个值为 [中文档位label, 分数]，分数是 1.0-10.0 的 10 分制小数（注意：ai_risk/competition/work_intensity/learning_difficulty/learning_duration/certification_difficulty/pr_difficulty 为负向，越高越差）
- fit：适合人群中文数组（2-3 条）
- unfit：不适合人群中文数组（2 条）
- faqs：数组，每项{{faq_type:"salary"或"migration"等, question_zh, answer_zh, question_en, answer_en}}（2-3 条，含薪资与签证各一）
- match_name：现有职业候选池中最接近的同一职业英文名（原样照填）；无则填 ""
- match_country：该匹配职业所属国家代码 "AU"/"CA"/"US"/"UK"；match_name 为空则填 ""
只输出真实合理的德国数据；不确定的薪资给保守区间。"""


def clamp10(v, d=5.0):
    try:
        return round(max(1.0, min(10.0, float(v))), 1)
    except (TypeError, ValueError):
        return d


def validate(raw):
    g = lambda k: (raw.get(k) or "").strip()
    cat = g("category")
    if cat not in CATEGORIES:
        cat = "Business, Finance & Legal"
    out = {
        "name_en": g("name_en"), "name_zh": g("name_zh"), "category": cat,
        "summary_zh": g("summary_zh"), "summary_en": g("summary_en"),
        "forecast_note_zh": g("forecast_note_zh"), "trend_summary_zh": g("trend_summary_zh"),
        "is_migration": int(raw.get("is_migration")) if str(raw.get("is_migration")) in ("0", "1", "2") else 1,
        "shortage": 1 if raw.get("shortage") in (1, "1", True) else 0,
        "workforce_size": int(raw["workforce_size"]) if str(raw.get("workforce_size", "")).isdigit() else None,
        "match_name": g("match_name"), "match_country": g("match_country").upper(),
    }
    if not (out["name_en"] and out["name_zh"] and out["summary_zh"] and out["summary_en"]):
        return None
    out["name_en"] = out["name_en"][:150]
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
    out["visa"] = [{"visa_subclass": (v.get("visa_subclass") or "")[:20], "visa_name": v.get("visa_name", ""),
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


def gen(system, kldb, title_de, definition):
    from openai import OpenAI
    client = OpenAI(api_key=config.require("DEEPSEEK_API_KEY"), base_url=config.DEEPSEEK_BASE_URL,
                    timeout=90.0, max_retries=2)
    resp = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL, max_tokens=4000, timeout=90.0,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": build_prompt(kldb, title_de, definition)}],
        response_format={"type": "json_object"})
    data = _parse_list(resp.choices[0].message.content)
    if isinstance(data, list):
        data = data[0] if data else {}
    return data if isinstance(data, dict) else {}


def save(kldb, v):
    """入库 + 英文 FAQ + 中英 md。返回 occ_id。name_en 由 LLM 产出。"""
    name_en = v["name_en"]
    OCC = {"country_code": "DE", "occ_code": kldb, "anzsco_code": kldb,
           "occ_code_type": "KldB", "anzsco_title": name_en, "category": v["category"],
           "currency": "EUR", "workforce_size": v["workforce_size"], "shortage_listed": v["shortage"],
           "is_migration": v["is_migration"], "is_public_servant": 0,
           "growth_areas": json.dumps(v["growth"], ensure_ascii=False)}
    ZH = {"locale": "zh-CN", "name": v["name_zh"], "summary": v["summary_zh"],
          "forecast_note": v["forecast_note_zh"], "trend_summary": v["trend_summary_zh"]}
    EN = {"locale": "en", "name": name_en, "summary": v["summary_en"],
          "forecast_note": v["forecast_note_zh"], "trend_summary": v["trend_summary_zh"]}
    faqs_zh = [{"faq_type": f["faq_type"], "sort_order": f["sort_order"],
                "question": f["question_zh"], "answer": f["answer_zh"]} for f in v["faqs"]]
    src = [{"source_name": "BA / destatis", "content": "KldB 薪资与需求", "url": "https://statistik.arbeitsagentur.de/"}]
    with get_cursor() as cur:
        occ_id = seed_occupation_v2(cur, OCC, ZH, EN, v["education"], v["qual"], [], v["sal"],
                                    v["visa"], v["ratings"], v["fit"], v["unfit"], src, faqs_zh)
        cur.execute("SELECT id FROM occupation_faqs WHERE occupation_id=%s ORDER BY sort_order", (occ_id,))
        fids = [r["id"] for r in cur.fetchall()]
        for f, fid in zip(v["faqs"], fids):
            if f.get("question_en"):
                cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'en',%s,%s) "
                            "ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",
                            (fid, f["question_en"], f.get("answer_en") or f["answer_zh"]))
    generate_md(kldb, locale="zh-CN", country="DE")
    generate_md(kldb, locale="en", country="DE")
    return occ_id


def load_json(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            return default
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)


def run(batch_size, rest, limit, redo):
    soc_list = load_json(SOC_LIST, [])
    with get_cursor() as cur:
        cur.execute("SELECT o.id,o.country_code,o.occ_code,o.anzsco_title AS name_en "
                    "FROM occupations o WHERE o.country_code IN ('AU','CA','US','UK')")
        pool_rows = cur.fetchall()
        cur.execute("SELECT occ_code FROM occupations WHERE country_code='DE'")
        de_codes = {r["occ_code"] for r in cur.fetchall()}
    pool = [(r["country_code"], r["occ_code"], r["name_en"], r["id"]) for r in pool_rows]
    resolver = {}
    resolver_cc = {}
    for c, code, nm, oid in pool:
        resolver.setdefault(_norm(nm), (c, code, oid))
        resolver_cc.setdefault((c, _norm(nm)), (c, code, oid))
    system = build_system(pool)

    done = set() if redo else set(load_json(STATE, []))
    matches = load_json(MATCH, {})
    targets = [s for s in soc_list if s["soc"] not in done and s["soc"] not in de_codes]
    if limit:
        targets = targets[:limit]
    n = len(targets)
    nb = (n + batch_size - 1) // batch_size if batch_size else 1
    print(f"[de] 待生成 {n} 个(分 {nb} 批，每批 {batch_size}，批间休息 {rest}s) model={config.DEEPSEEK_MODEL}", flush=True)
    okc = fail = matched = 0
    for bi in range(nb):
        chunk = targets[bi * batch_size:(bi + 1) * batch_size]
        print(f"\n===== 批次 {bi+1}/{nb}（{len(chunk)} 个）开始 {time.strftime('%H:%M:%S')} =====", flush=True)
        for idx, s in enumerate(chunk, 1):
            tag = f"b{bi+1} {idx}/{len(chunk)} {s['soc']} {s['title'][:40]}"
            try:
                v = validate(gen(system, s["soc"], s["title"], s.get("definition")))
                if not v:
                    raise ValueError("数据不完整")
                occ_id = save(s["soc"], v)
                de_codes.add(s["soc"])
                mn = _norm(v["match_name"]) if v["match_name"] else ""
                hit = (resolver_cc.get((v["match_country"], mn)) or resolver.get(mn)) if mn else None
                if hit:
                    matches[str(occ_id)] = {"country": hit[0], "occ_code": hit[1], "src_occ_id": hit[2]}
                    matched += 1
                done.add(s["soc"])
                save_json(STATE, sorted(done)); save_json(MATCH, matches)
                okc += 1
                mtxt = f"母体={hit[0]}/{hit[1]}" if hit else "无母体(待LLM生成ai-block)"
                print(f"  [{tag}] → DE id={occ_id} {v['name_en']} / {v['name_zh']} [{v['category']}] mig={v['is_migration']} {mtxt}", flush=True)
            except Exception as e:
                fail += 1
                print(f"  [{tag}] 失败: {e}", flush=True)
        print(f"===== 批次 {bi+1}/{nb} 完成（累计 成功{okc} 匹配{matched} 失败{fail}）{time.strftime('%H:%M:%S')} =====", flush=True)
        if bi < nb - 1 and rest:
            print(f"[rest] 休息 {rest}s……", flush=True)
            time.sleep(rest)
    print(f"\n[OK] 全部完成：成功 {okc}，其中有母体 {matched}，失败 {fail}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--rest", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    run(a.batch_size, a.rest, a.limit, a.redo)
