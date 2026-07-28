"""北欧5国(NO/SE/FI/DK/IS)职业入库：官方薪资/就业(零LLM) + 规则评分 + DeepSeek文案 + 本地名。

黄金模板同 gen_cn_official，参数化 --country：
- 官方数据来自 downloads/{cc}/{cc}_by_isco.json（build_{cc}_official.py 产出，零 LLM）。
- avg_salary / salary_mean / workforce 直取官方；salary_note 保留官方口径说明。
- 规则评分（仅 2 维有官方依据，其余留空，同 gen_cn_official）：
  · income_level ← 该国四位 avg_salary 的经验百分位映射到 1-10（确定性，非估算）。
  · ai_risk     ← aioe_pct(ILO WP140+Eloundou，ISCO 全球共享) / 10，clamp 1-10。
- 文案 + 本地职业名(name_local, native_lang) 由 DeepSeek 生成；本地名灌 native_locale TM。
- AI 块另跑 copy_ai_blocks_by_code --to {cc} --from IT。

运行：DEEPSEEK_MODEL=deepseek-v4-flash LLM_PROVIDER=deepseek \
      python -m scripts.gen_nordic_official --country NO [--limit N] [--archive] [--codes 2511,...]
"""
import sys, os, json, argparse, time, bisect
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper_v2 import seed_occupation_en
from scripts.gen_intl_v2 import (COUNTRY, CATEGORIES, DIMS, build_system, _clamp,
                                 load_universe, load_archive, save_archive, inject_native_name)
from video_pipeline import config

# 走"官方薪资 by_isco.json + 规则评分 + LLM 文案"完整管线的国家集合。
# 北欧 5 国 + CZ/HU/SG（四位 ISCO 官方薪资可得）。
NORDIC = {"NO", "SE", "FI", "DK", "IS", "CZ", "HU", "SG"}


def official_path(cc):
    return os.path.join("downloads", cc.lower(), f"{cc.lower()}_by_isco.json")


def _income_label(s):
    return "Very high" if s >= 8 else "High" if s >= 6 else "Moderate" if s >= 4.5 else "Modest"


def _airisk_label(s):
    return "High exposure" if s >= 7 else "Moderate exposure" if s >= 4 else "Low exposure"


def make_income_scorer(off_all):
    """该国四位 avg_salary 的经验百分位 -> income_level 1-10（确定性分档）。"""
    sals = sorted(v["avg_salary"] for v in off_all.values() if v.get("avg_salary"))

    def score(s):
        if not s or not sals:
            return None
        rank = bisect.bisect_right(sals, s) / len(sals)   # 0..1
        return max(1.0, min(10.0, round(1 + rank * 9, 1)))
    return score


def rule_ratings(off, aioe_pct, income_score):
    rat = []
    inc = income_score((off or {}).get("avg_salary"))
    if inc is not None:
        rat.append({"dimension": "income_level", "label": _income_label(inc), "stars": float(inc),
                    "note": "Derived from official national wage distribution (percentile)"})
    if aioe_pct is not None:
        s = max(1.0, min(10.0, round(aioe_pct / 10.0, 1)))
        rat.append({"dimension": "ai_risk", "label": _airisk_label(s), "stars": s,
                    "note": "Derived from ILO/OpenAI AIOE percentile (ISCO-shared)"})
    return rat


def build_prompt(cc, isco, title_en):
    c = COUNTRY[cc]
    nl = c["native_lang"]
    return f"""{c['name']} ISCO-08 occupation:
- ISCO code: {isco}
- English title: {title_en}

Return a JSON object (ALL TEXT IN ENGLISH except name_local, all fields required):
- name: standard English occupation name (singular, Title Case)
- name_local: the standard {nl} occupation name (singular), as commonly used locally — THIS FIELD ONLY in {nl}
- summary: one-sentence intro (60-140 words), {c['name']} labour-market context
- forecast_note: one paragraph on {c['name']} employment outlook (60-120 words)
- trend_summary: one paragraph on career/progression path in {c['name']} (60-120 words)
- category: one of these 11 (verbatim): {'; '.join(CATEGORIES)}
- is_migration: 0/1/2 (0=not a migration route, 1=direct skilled-migration friendly, 2=restricted; consider EU/EEA free movement and {c['name']}'s permit thresholds)
- shortage: 0 or 1 (on a shortage/positive-list-relevant list)
- growth: array of 4 English keywords (hot areas in {c['name']})
- education: array of 2-3 {{stage, duration, cost_min (int {c['currency']}), cost_max (int), cost_note}}
- qualifications: array of 2-4 {{qual_name, issuer, note, is_mandatory (0/1)}}
- visa: array of 2-3 {{visa_subclass (code/short), visa_name, description}} ({c['visa']})
- fit: array of 2-3 English strings (who it suits)
- unfit: array of 2 English strings
- faqs: array of 2-3 {{faq_type, question, answer}} (include one salary + one visa)
Do NOT output salary figures, workforce counts, or rating scores (those come from official statistics / rules). Use conservative, realistic {c['name']} data."""


def validate(v):
    need = ["name", "name_local", "summary", "forecast_note", "trend_summary", "category",
            "education", "qualifications", "visa", "fit", "unfit", "faqs"]
    for k in need:
        if k not in v or v[k] in (None, "", []):
            raise ValueError(f"缺字段 {k}")
    if v["category"] not in CATEGORIES:
        raise ValueError(f"非法 category: {v['category']}")
    return v


def to_seed(cc, isco, v, off, aioe_pct, income_score):
    cur_code = COUNTRY[cc]["currency"]
    OCC = {"country_code": cc, "occ_code": isco, "occ_code_type": "ISCO08", "anzsco_code": isco,
           "anzsco_title": v["name"], "category": v["category"], "currency": cur_code,
           "workforce_size": (off or {}).get("workforce"), "shortage_listed": int(v.get("shortage", 0)),
           "is_migration": int(v.get("is_migration", 1)), "is_public_servant": 0,
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
        SAL.append({"experience": "Median (all levels)", "salary_min": _clamp(avg), "salary_max": _clamp(avg),
                    "salary_note": off.get("salary_note"), "currency": cur_code})
    VISA = [{"visa_subclass": str(x["visa_subclass"])[:40], "visa_name": x.get("visa_name"),
             "description": x.get("description")} for x in v["visa"]]
    RAT = rule_ratings(off, aioe_pct, income_score)
    FAQS = [{"faq_type": f.get("faq_type"), "question": f["question"], "answer": f["answer"]} for f in v["faqs"]]
    return OCC, TEXT, EDU, QUAL, SAL, VISA, RAT, v["fit"], v["unfit"], FAQS


def _gen(system, cc, isco, title):
    from scripts import _deepseek_rest
    return _deepseek_rest.complete_json(system, build_prompt(cc, isco, title))


def run(cc, limit, rest, archive, codes=None):
    assert cc in NORDIC, f"仅支持北欧5国 {NORDIC}"
    off_all = json.load(open(official_path(cc), encoding="utf-8"))
    income_score = make_income_scorer(off_all)
    uni = load_universe()
    targets = [uni[x] for x in codes if x in uni] if codes else list(uni.values())
    if limit:
        targets = targets[:limit]
    system = build_system(cc)
    nloc = COUNTRY[cc]["native_locale"]
    print(f"[{cc}] 官方薪资+规则评分+LLM文案 待处理 {len(targets)} | 官方薪资覆盖 "
          f"{sum(1 for v in off_all.values() if v.get('avg_salary'))} | native={nloc} | model={config.DEEPSEEK_MODEL}",
          flush=True)
    arc = load_archive(cc) if archive else None
    okc = fail = 0
    for idx, u in enumerate(targets, 1):
        isco, title = u["isco"], u["label_en"]
        off = off_all.get(isco)
        aioe_pct = u.get("aioe_pct")
        tag = f"{idx}/{len(targets)} {isco} {title[:34]}"
        try:
            v = validate(_gen(system, cc, isco, title))
            args = to_seed(cc, isco, v, off, aioe_pct, income_score)
            # 本地名优先取官方 by_isco（如 CZ 的 czso 捷克名），无则用 LLM 产出。
            name_local = (off or {}).get("name_local") or v.get("name_local")
            with get_cursor() as cur:
                occ_id = seed_occupation_en(cur, *args)
                inject_native_name(cur, v["name"], nloc, name_local, cc)
            okc += 1
            if arc is not None:
                arc[isco] = {"isco": isco, "title_en": title, "official": off, "aioe_pct": aioe_pct, **v}
                save_archive(cc, arc)
            rat = ",".join(f"{r['dimension']}={r['stars']}" for r in args[6])
            print(f"  [{tag}] -> id={occ_id} {v['name']} 〔{nloc}:{v.get('name_local')}〕 "
                  f"[{v['category']}] sal={(off or {}).get('avg_salary')} wf={(off or {}).get('workforce')} {rat}",
                  flush=True)
        except Exception as e:
            fail += 1
            print(f"  [{tag}] 失败: {e}", flush=True)
        if rest and idx < len(targets):
            time.sleep(rest)
    print(f"[{cc}] 完成：成功 {okc}，失败 {fail}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--rest", type=int, default=0)
    ap.add_argument("--archive", action="store_true")
    ap.add_argument("--codes", default="")
    a = ap.parse_args()
    run(a.country.upper(), a.limit, a.rest, a.archive,
        [c.strip() for c in a.codes.split(",") if c.strip()] or None)
