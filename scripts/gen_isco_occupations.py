"""为意大利(IT)/荷兰(NL)/爱尔兰(IE) 的 ISCO-08 职业批量生成并入库（骨架）。

【本文件为骨架，待确认后再全量跑】设计要点（本会话已确认）：
- 分类：统一 ISCO-08 4 位（.codex_tmp/isco08_universe.json，436 码，含英文标签 + 现成 AIOE）。
- 三国均 currency=EUR，occ_code_type='ISCO08'，occ_code=ISCO 4 位。
- 母本：复用现有中文管线，出 zh-CN + en 两份母本（中文仅内部，永不对外展示）；
  目标语翻译(IT→it, NL→nl)后续由翻译步骤按母本串产出；IE 只英文。本步不接站点 locale。
- 数据分两层：
  · 官方层（Eurostat / 各国官方）：workforce_size、salaries(median/mean)、shortage、visa 框架。
    → 由 fetch_official() 从预备好的 .codex_tmp/official_{cc}.json 读取（schema 见下）；官方源见 docs 计划。
  · 叙述层（DeepSeek 生成）：summary/education/ratings/fit/FAQ + name_en/name_zh；官方层缺薪资时用 LLM 保守估算兜底。
- AI 块复用：① AIOE 已由 ISCO 4 位直挂（compute_aioe 链路）；② 叙述性 ai-block(replaced/moat/disruptors)
  仍按 match_name 从 AU/CA/US/UK 池匹配复用（同 gen_fr），写 .codex_tmp/isco_{cc}_ai_match.json。
- 幂等：处理过的 (country, isco) 记 .codex_tmp/isco_{cc}_done.json。

运行（确认后）：$env:LLM_PROVIDER="deepseek"; python -m scripts.gen_isco_occupations --country IT [--limit N]
"""
import sys, os, json, argparse, time, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from db.connection import get_cursor
from _seed_helper import seed_occupation_v2
from pipeline.generators.md_generator import generate_md
from video_pipeline import config
from gen_ai_disruptors import _parse_list

TMP = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp")
UNIVERSE = os.path.join(TMP, "isco08_universe.json")

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

# 各国工作/居留框架（进 system 提示 + 兜底 visa）。三国均可走 EU Blue Card + 各国许可。
COUNTRY = {
    "IT": {"name": "Italy", "visa": "EU Blue Card / Decreto Flussi 配额工作签 / Nulla Osta / 欧盟自由流动",
           "official": "ISTAT / Eurostat", "target_locale": "it"},
    "NL": {"name": "Netherlands", "visa": "EU Blue Card / Highly Skilled Migrant(kennismigrant) / Orientation Year / 欧盟自由流动",
           "official": "CBS StatLine / Eurostat", "target_locale": "nl"},
    "IE": {"name": "Ireland", "visa": "Critical Skills Employment Permit / General Employment Permit / EU Blue Card",
           "official": "CSO / Eurostat", "target_locale": "en"},
}


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


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


# ---------------------------------------------------------------------------
# 官方层（TODO：接 Eurostat/各国官方；当前从预备文件读取，缺则返回空由叙述层兜底）
# official_{cc}.json schema: { "<isco4>": {
#     "workforce_size": int|None,
#     "shortage": 0|1,
#     "salaries": [ {"band":"median"|"mean","experience":str,"salary_min":int,"salary_max":int,"salary_note":str}, ... ]
# } }
# 官方源（待各自验证可达性/粒度）：
#   就业人数: Eurostat lfsa_egais(ISCO 1位) + 各国到 4 位(ISTAT / CBS StatLine / CSO PxStat)
#   薪资:     Eurostat earn_ses(SES, 按 ISCO) 或各国官方；median/mean 复用 load_salary_median 口径
#   紧缺:     IE=Critical Skills Occupations List；NL=IND kennismigrant 门槛；IT=Decreto Flussi
# ---------------------------------------------------------------------------
def fetch_official(cc, isco):
    data = _OFFICIAL_CACHE.setdefault(cc, load_json(os.path.join(TMP, f"official_{cc}.json"), {}))
    return data.get(isco, {})


_OFFICIAL_CACHE = {}


# ---------------------------------------------------------------------------
# 叙述层（DeepSeek）：产 name/summary/education/ratings/fit/faq + 薪资兜底 + ai-block 母体匹配
# ---------------------------------------------------------------------------
def build_system(cc, pool):
    names = sorted({p[2] for p in pool if p[2]})
    cats = "、".join(CATEGORIES)
    c = COUNTRY[cc]
    return (
        f"你是{c['name']}劳动力市场与移民分析师，熟悉 ISCO-08 职业分类、{c['official']} 就业与薪资数据、"
        f"欧盟内自由流动，以及工作/居留路径（{c['visa']}）。"
        f"针对给定的 ISCO-08 职业（英文标题），输出务实、具体的{c['name']}数据。薪资用欧元(EUR)整数年薪(税前)。"
        "中文面向国际读者，不要提『华人/中文社区』。\n"
        f"职业分类只能从以下 11 类中选一个（原文照填）：{cats}\n"
        "另需从下列【现有职业候选池】中选出最接近的同一职业，把英文名原样填入 match_name；无则填 \"\"。\n"
        f"候选池：{' | '.join(names)}\n"
        "只输出一个 JSON 对象，不要多余文字。"
    )


def build_prompt(cc, isco, title_en, official):
    dims = "、".join(DIMS)
    hint = ""
    if official.get("salaries"):
        hint = f"\n（已知官方薪资，供参考：{json.dumps(official['salaries'], ensure_ascii=False)}）"
    return f"""{COUNTRY[cc]['name']} ISCO-08 职业：
- ISCO 码：{isco}
- 英文标题：{title_en}{hint}

请输出该国该职业的 JSON，字段如下（全部必填）：
- name_en：标准英文职业名（单数，首字母大写，用于全站英文展示与匹配）
- name_zh：中文职业名（仅内部母本）
- category：从给定 11 类中选一个（原文照填）
- summary_zh / summary_en：一句话简介（中/英，各 60-140 字/词）
- forecast_note_zh：该国就业前景一段（60-120 字）
- trend_summary_zh：职业发展/晋升路径一段（60-120 字）
- is_migration：0/1/2（考虑欧盟自由流动与该国紧缺/许可门槛）
- shortage：0 或 1（该国是否紧缺；若官方层已给以官方为准）
- workforce_size：该国从业人数估计（整数）
- growth：增长/热点关键词英文数组（4 个）
- education：数组，每项{{stage:中文阶段, duration:如"3年（本科）", cost_min:整数EUR, cost_max:整数EUR, cost_note:中文}}（2-3 项）
- qualifications：数组，每项{{qual_name:中文, issuer:机构, note:中文, is_mandatory:0或1}}（2-4 项）
- salaries：数组，每项{{experience:中文如"初级（0-3年）", salary_min:整数EUR, salary_max:整数EUR, salary_note:中文}}（3 档：初/中/高，税前年薪）
- visa：数组，每项{{visa_subclass:如"EU Blue Card"/"{COUNTRY[cc]['visa'].split(' / ')[1] if ' / ' in COUNTRY[cc]['visa'] else 'Work Permit'}", visa_name:英文, description:中文}}（2-4 项工作/居留路径）
- ratings：对象，键为这 11 个维度：{dims}；每个值为 [中文档位label, 分数]，分数是 1.0-10.0 的 10 分制小数（ai_risk/competition/work_intensity/learning_difficulty/learning_duration/certification_difficulty/pr_difficulty 为负向，越高越差）
- fit：适合人群中文数组（2-3 条）
- unfit：不适合人群中文数组（2 条）
- faqs：数组，每项{{faq_type:"salary"或"migration"等, question_zh, answer_zh, question_en, answer_en}}（2-3 条，含薪资与签证各一）
- match_name：现有职业候选池中最接近的同一职业英文名（原样照填）；无则填 ""
- match_country：该匹配职业所属国家代码 "AU"/"CA"/"US"/"UK"；match_name 为空则填 ""
只输出真实合理的{COUNTRY[cc]['name']}数据；不确定的薪资给保守区间。"""


# validate() 复用 gen_fr（结构校验与 ISCO 无关）；gen()/save() 为 ISCO/EUR/cc 特化实现。
from gen_fr_occupations import validate  # noqa: E402


def gen(system, cc, isco, title_en, official):
    from openai import OpenAI
    client = OpenAI(api_key=config.require("DEEPSEEK_API_KEY"), base_url=config.DEEPSEEK_BASE_URL,
                    timeout=90.0, max_retries=2)
    resp = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL, max_tokens=4000, timeout=90.0,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": build_prompt(cc, isco, title_en, official)}],
        response_format={"type": "json_object"})
    data = _parse_list(resp.choices[0].message.content)
    if isinstance(data, list):
        data = data[0] if data else {}
    return data if isinstance(data, dict) else {}


def save(cc, isco, v, official):
    """入库 zh-CN + en 母本 + 英文 FAQ + 英文 md。官方层(若有)覆盖 workforce/shortage/salaries。"""
    name_en = v["name_en"]
    workforce = official.get("workforce_size") if official.get("workforce_size") is not None else v["workforce_size"]
    shortage = official.get("shortage") if official.get("shortage") is not None else v["shortage"]
    OCC = {"country_code": cc, "occ_code": isco, "anzsco_code": isco,
           "occ_code_type": "ISCO08", "anzsco_title": name_en, "category": v["category"],
           "currency": "EUR", "workforce_size": workforce, "shortage_listed": shortage,
           "is_migration": v["is_migration"], "is_public_servant": 0,
           "growth_areas": json.dumps(v["growth"], ensure_ascii=False)}
    ZH = {"locale": "zh-CN", "name": v["name_zh"], "summary": v["summary_zh"],
          "forecast_note": v["forecast_note_zh"], "trend_summary": v["trend_summary_zh"]}
    EN = {"locale": "en", "name": name_en, "summary": v["summary_en"],
          "forecast_note": v["forecast_note_zh"], "trend_summary": v["trend_summary_zh"]}
    # 官方薪资(median/mean)优先；否则用 LLM 三档估算
    sal = official.get("salaries") or v["sal"]
    faqs_zh = [{"faq_type": f["faq_type"], "sort_order": f["sort_order"],
                "question": f["question_zh"], "answer": f["answer_zh"]} for f in v["faqs"]]
    src = [{"source_name": COUNTRY[cc]["official"], "content": "ISCO-08 就业/薪资", "url": ""}]
    with get_cursor() as cur:
        occ_id = seed_occupation_v2(cur, OCC, ZH, EN, v["education"], v["qual"], [], sal,
                                    v["visa"], v["ratings"], v["fit"], v["unfit"], src, faqs_zh)
        cur.execute("SELECT id FROM occupation_faqs WHERE occupation_id=%s ORDER BY sort_order", (occ_id,))
        fids = [r["id"] for r in cur.fetchall()]
        for f, fid in zip(v["faqs"], fids):
            if f.get("question_en"):
                cur.execute("INSERT INTO occupation_faqs_i18n (faq_id,locale,question,answer) VALUES (%s,'en',%s,%s) "
                            "ON DUPLICATE KEY UPDATE question=VALUES(question),answer=VALUES(answer)",
                            (fid, f["question_en"], f.get("answer_en") or f["answer_zh"]))
    generate_md(isco, locale="zh-CN", country=cc)
    generate_md(isco, locale="en", country=cc)
    return occ_id


def run(cc, batch_size, rest, limit, redo, codes=None):
    assert cc in COUNTRY, f"country 只能是 IT/NL/IE，收到 {cc}"
    universe = load_json(UNIVERSE, [])
    if codes:
        want = {c.strip() for c in codes}
        universe = [u for u in universe if u["isco"] in want]
    done_path = os.path.join(TMP, f"isco_{cc}_done.json")
    match_path = os.path.join(TMP, f"isco_{cc}_ai_match.json")
    done = set() if redo else set(load_json(done_path, []))
    matches = load_json(match_path, {})
    with get_cursor() as cur:
        cur.execute("SELECT id,country_code,occ_code,anzsco_title AS name_en FROM occupations "
                    "WHERE country_code IN ('AU','CA','US','UK')")
        pool_rows = cur.fetchall()
        cur.execute("SELECT occ_code FROM occupations WHERE country_code=%s", (cc,))
        exist = {r["occ_code"] for r in cur.fetchall()}
    pool = [(r["country_code"], r["occ_code"], r["name_en"], r["id"]) for r in pool_rows]
    resolver, resolver_cc = {}, {}
    for c, code, nm, oid in pool:
        resolver.setdefault(_norm(nm), (c, code, oid))
        resolver_cc.setdefault((c, _norm(nm)), (c, code, oid))
    system = build_system(cc, pool)
    targets = [u for u in universe if u["isco"] not in done and u["isco"] not in exist]
    if limit:
        targets = targets[:limit]
    print(f"[{cc}] universe {len(universe)} 待生成 {len(targets)} (official={COUNTRY[cc]['official']}, "
          f"target_locale={COUNTRY[cc]['target_locale']}) model={config.DEEPSEEK_MODEL}", flush=True)
    okc = fail = matched = 0
    for idx, u in enumerate(targets, 1):
        isco, title = u["isco"], u["label_en"]
        tag = f"{idx}/{len(targets)} {isco} {title[:40]}"
        try:
            official = fetch_official(cc, isco)
            v = validate(gen(system, cc, isco, title, official))
            if not v:
                raise ValueError("数据不完整")
            occ_id = save(cc, isco, v, official)
            exist.add(isco)
            mn = _norm(v["match_name"]) if v["match_name"] else ""
            hit = (resolver_cc.get((v["match_country"], mn)) or resolver.get(mn)) if mn else None
            if hit:
                matches[str(occ_id)] = {"country": hit[0], "occ_code": hit[1], "src_occ_id": hit[2]}
                matched += 1
            done.add(isco)
            save_json(done_path, sorted(done)); save_json(match_path, matches)
            okc += 1
            mtxt = f"母体={hit[0]}/{hit[1]}" if hit else "无母体(待补ai-block)"
            offt = "官方薪资" if official.get("salaries") else "LLM薪资"
            print(f"  [{tag}] → {cc} id={occ_id} {v['name_en']} / {v['name_zh']} "
                  f"[{v['category']}] mig={v['is_migration']} {offt} {mtxt}", flush=True)
        except Exception as e:
            fail += 1
            print(f"  [{tag}] 失败: {e}", flush=True)
        if rest and idx < len(targets):
            time.sleep(rest)
    print(f"[{cc}] 完成：成功 {okc}，有母体 {matched}，失败 {fail}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, choices=["IT", "NL", "IE"])
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--rest", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--codes", default="")
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    run(a.country, a.batch_size, a.rest, a.limit, a.redo,
        codes=[c for c in a.codes.split(",") if c.strip()] or None)
