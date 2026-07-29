"""中国(CN)职业入库：官方薪资(岗位大类映射) + 规则评分(零LLM) + LLM文案 + AI块复用。

约定（用户指令）：
- 数字零 LLM：薪资走官方岗位大类映射(downloads/cn/cn_by_isco.json)；评分按官方信号规则推导；
  workforce 中国无逐职业官方数→留空(不估算)。
- 文案(name/summary/forecast/trend/category/education/qualifications/visa/faq/fit/unfit/growth/
  is_migration/shortage) 由 DeepSeek 生成(针对中国语境)。
- AI 块另行 copy_ai_blocks_by_code --to CN --from IT（本脚本不生成 AI 块）。
- 中文名：本次留空，由翻译管线出 zh-CN（官方 ISCO-08 中文名为后续升级）。英文为翻译母本。

评分规则（DIMS 中仅这两维有官方依据，其余留空）：
- income_level ← 官方岗位大类年平均工资分档(1-10)。
- ai_risk     ← aioe_pct(ILO WP140+Eloundou，ISCO 全球共享) / 10，clamp 1-10。

运行：DEEPSEEK_MODEL=deepseek-v4-flash LLM_PROVIDER=deepseek python -m scripts.gen_cn_official [--limit N] [--archive] [--codes 2512,...]
"""
import sys, os, json, argparse, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper_v2 import seed_occupation_en
from scripts.gen_intl_v2 import (COUNTRY, CATEGORIES, build_system, _clamp,
                                 load_universe, load_archive, save_archive, inject_native_name)
from video_pipeline import config

CC = "CN"
OFFICIAL = os.path.join("downloads", "cn", "cn_by_isco.json")

# 官方岗位大类年平均工资 -> income_level(1-10) 分档（确定性，非估算）。
POST_INCOME = {
    "中层及以上管理人员": 9.0,
    "专业技术人员": 7.0,
    "办事人员和有关人员": 5.0,
    "生产制造及有关人员": 4.0,
    "社会生产服务和生活服务人员": 4.0,
}


def _income_label(s):
    return "Very high" if s >= 8 else "High" if s >= 6 else "Moderate" if s >= 4.5 else "Modest"


def _airisk_label(s):
    return "High exposure" if s >= 7 else "Moderate exposure" if s >= 4 else "Low exposure"


def rule_ratings(off, aioe_pct):
    """仅 income_level(官方工资) + ai_risk(aioe_pct)；其余 9 维无官方依据→不写。"""
    rat = []
    post = (off or {}).get("post")
    inc = POST_INCOME.get(post)
    if inc is not None:
        rat.append({"dimension": "income_level", "label": _income_label(inc), "stars": float(inc),
                    "note": "Derived from official post-category average wage (NBS 2022)"})
    if aioe_pct is not None:
        s = max(1.0, min(10.0, round(aioe_pct / 10.0, 1)))
        rat.append({"dimension": "ai_risk", "label": _airisk_label(s), "stars": s,
                    "note": "Derived from ILO/OpenAI AIOE percentile (ISCO-shared)"})
    return rat


def build_prompt_cn(isco, title_en):
    c = COUNTRY[CC]
    return f"""China ISCO-08 occupation:
- ISCO code: {isco}
- English title: {title_en}

Return a JSON object (ALL TEXT IN ENGLISH, all fields required):
- name: standard English occupation name (singular, Title Case)
- summary: one-sentence intro (60-140 words), China labour-market context
- forecast_note: one paragraph on China employment outlook (60-120 words)
- trend_summary: one paragraph on career/progression path in China (60-120 words)
- category: one of these 11 (verbatim): {'; '.join(CATEGORIES)}
- is_migration: 0/1/2 (0=not a migration route, 1=direct skilled-migration friendly, 2=restricted). China has no points-based scheme, so use 0 or 2 for most roles.
- shortage: 0 or 1 (on a shortage/《紧缺职业》-relevant list)
- growth: array of 4 English keywords (hot areas in China)
- education: array of 2-3 {{stage, duration, cost_min (int CNY), cost_max (int), cost_note}}
- qualifications: array of 2-4 {{qual_name, issuer, note, is_mandatory (0/1)}} (use China's 职业资格/职业技能等级 where relevant)
- visa: array of 2-3 {{visa_subclass (code/short), visa_name, description}} ({c['visa']})
- fit: array of 2-3 English strings (who it suits)
- unfit: array of 2 English strings
- faqs: array of 2-3 {{faq_type, question, answer}} (include one salary + one visa)
Do NOT output salary figures, workforce counts, or rating scores (those come from official statistics / rules). Use conservative, realistic China data."""


def validate(v):
    need = ["name", "summary", "forecast_note", "trend_summary", "category", "education",
            "qualifications", "visa", "fit", "unfit", "faqs"]
    for k in need:
        if k not in v or v[k] in (None, "", []):
            raise ValueError(f"缺字段 {k}")
    if v["category"] not in CATEGORIES:
        raise ValueError(f"非法 category: {v['category']}")
    return v


def to_seed(isco, v, off, aioe_pct):
    cur_code = COUNTRY[CC]["currency"]
    OCC = {"country_code": CC, "occ_code": isco, "occ_code_type": "ISCO08", "anzsco_code": isco,
           "anzsco_title": v["name"], "category": v["category"], "currency": cur_code,
           "workforce_size": (off or {}).get("workforce"), "shortage_listed": int(v.get("shortage", 0)),
           "is_migration": int(v.get("is_migration", 0)), "is_public_servant": 0,
           "growth_areas": v.get("growth", [])}
    TEXT = {"name": v["name"], "summary": v["summary"], "forecast_note": v["forecast_note"],
            "trend_summary": v["trend_summary"]}
    EDU = [{"stage": e["stage"], "duration": e.get("duration"), "cost_min": _clamp(e.get("cost_min")),
            "cost_max": _clamp(e.get("cost_max")), "cost_note": e.get("cost_note")} for e in v["education"]]
    QUAL = [{"qual_name": q["qual_name"], "issuer": q.get("issuer"), "note": q.get("note"),
             "is_mandatory": int(q.get("is_mandatory", 1))} for q in v["qualifications"]]
    SAL = []
    avg = (off or {}).get("avg_salary")
    if avg:
        SAL.append({"experience": "Average salary", "salary_min": _clamp(avg), "salary_max": _clamp(avg),
                    "salary_note": off.get("salary_note"), "currency": cur_code})
    VISA = [{"visa_subclass": str(x["visa_subclass"])[:40], "visa_name": x.get("visa_name"),
             "description": x.get("description")} for x in v["visa"]]
    RAT = rule_ratings(off, aioe_pct)
    FAQS = [{"faq_type": f.get("faq_type"), "question": f["question"], "answer": f["answer"]} for f in v["faqs"]]
    return OCC, TEXT, EDU, QUAL, SAL, VISA, RAT, v["fit"], v["unfit"], FAQS


def _gen(system, isco, title):
    from scripts import _deepseek_rest
    return _deepseek_rest.complete_json(system, build_prompt_cn(isco, title))


def run(limit, rest, archive, codes=None):
    off_all = json.load(open(OFFICIAL, encoding="utf-8"))
    uni = load_universe()
    targets = [uni[x] for x in codes if x in uni] if codes else list(uni.values())
    if limit:
        targets = targets[:limit]
    system = build_system(CC)
    print(f"[CN] 官方薪资+规则评分+LLM文案 待处理 {len(targets)} | 官方薪资覆盖 "
          f"{sum(1 for v in off_all.values() if v.get('avg_salary'))} | model={config.DEEPSEEK_MODEL}", flush=True)
    arc = load_archive(CC) if archive else None
    okc = fail = 0
    for idx, u in enumerate(targets, 1):
        isco, title = u["isco"], u["label_en"]
        off = off_all.get(isco)
        aioe_pct = u.get("aioe_pct")
        tag = f"{idx}/{len(targets)} {isco} {title[:36]}"
        try:
            v = validate(_gen(system, isco, title))
            args = to_seed(isco, v, off, aioe_pct)
            with get_cursor() as cur:
                occ_id = seed_occupation_en(cur, *args)
                inject_native_name(cur, v["name"], COUNTRY[CC]["native_locale"], (off or {}).get("name_zh"), CC)
            okc += 1
            if arc is not None:
                arc[isco] = {"isco": isco, "title_en": title, "official": off, "aioe_pct": aioe_pct, **v}
                save_archive(CC, arc)
            rat = ",".join(f"{r['dimension']}={r['stars']}" for r in args[6])
            print(f"  [{tag}] -> id={occ_id} {v['name']} [{v['category']}] sal={(off or {}).get('avg_salary')} {rat}", flush=True)
        except Exception as e:
            fail += 1
            print(f"  [{tag}] 失败: {e}", flush=True)
        if rest and idx < len(targets):
            time.sleep(rest)
    print(f"[CN] 完成：成功 {okc}，失败 {fail}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--rest", type=int, default=0)
    ap.add_argument("--archive", action="store_true")
    ap.add_argument("--codes", default="", help="逗号分隔 ISCO 码，定向重试")
    a = ap.parse_args()
    run(a.limit, a.rest, a.archive, [c.strip() for c in a.codes.split(",") if c.strip()] or None)
