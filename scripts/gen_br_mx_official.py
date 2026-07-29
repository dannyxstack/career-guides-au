"""BR/MX 官方硬数据 + LLM 补文案 的合并入库(不估算薪资/人数/本地名)。
- 官方(来自 downloads/{br,mx}/{br,mx}_by_isco.json）：
    薪资 mean/median -> occupation_salaries_v2 两行(experience="Average salary"/"Median salary"，
      "Average salary" 喂 export 的 avg_salary)；人数 -> occupations.workforce_size；
    本地语言名(pt/es) -> 直灌 translations_v2(免重译)。
- LLM(DeepSeek，仅无官方源字段）：英文母本名、category、summary/forecast/trend、11维评分、
    签证、教育、资历、FAQ、fit/unfit、growth、is_migration、shortage。
- 无官方薪资的 ISCO(BR~7/MX~125）：仍生成 LLM 文案，薪资/人数留空(不估算)，本地名若有仍灌。
运行：DEEPSEEK_MODEL=deepseek-v4-flash LLM_PROVIDER=deepseek python -m scripts.gen_br_mx_official --country BR [--limit N] [--archive]
"""
import sys, os, json, argparse, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper_v2 import seed_occupation_en
from scripts.gen_intl_v2 import (COUNTRY, CATEGORIES, DIMS, build_system, gen, _clamp,
                                 inject_native_name, load_universe, load_archive, save_archive)
from video_pipeline import config

OFFICIAL = {"BR": os.path.join("downloads", "br", "br_by_isco.json"),
            "MX": os.path.join("downloads", "mx", "mx_by_isco.json")}
NAME_KEY = {"BR": "name_pt", "MX": "name_es"}


def build_prompt_official(cc, isco, title_en):
    """与 gen_intl_v2 同框架，但去掉 salaries/workforce_size/name_local(官方提供)。"""
    c = COUNTRY[cc]
    dims = ", ".join(DIMS)
    return f"""{c['name']} ISCO-08 occupation:
- ISCO code: {isco}
- English title: {title_en}

Return a JSON object (all fields required, ALL TEXT IN ENGLISH):
- name: standard English occupation name (singular, Title Case)
- summary: one-sentence intro (60-140 words)
- forecast_note: one paragraph on {c['name']} employment outlook (60-120 words)
- trend_summary: one paragraph on career/progression path (60-120 words)
- category: one of these 11 (verbatim): {'; '.join(CATEGORIES)}
- is_migration: 0/1/2 (0=not a migration route, 1=direct skilled-migration friendly, 2=restricted)
- shortage: 0 or 1 (on a shortage/quota-relevant list)
- growth: array of 4 English keywords (hot areas)
- education: array of 2-3 {{stage, duration, cost_min (int {c['currency']}), cost_max (int), cost_note}}
- qualifications: array of 2-4 {{qual_name, issuer, note, is_mandatory (0/1)}}
- visa: array of 2-4 {{visa_subclass (code/short), visa_name, description}}
- ratings: object keyed by these 11 dimensions: {dims}; each value = [english_label, score 1.0-10.0 one decimal]. Negative dims (ai_risk, competition, work_intensity, learning_difficulty, learning_duration, certification_difficulty, pr_difficulty): higher = worse.
- fit: array of 2-3 English strings (who it suits)
- unfit: array of 2 English strings
- faqs: array of 2-3 {{faq_type, question, answer}} (include one salary + one visa)
Do NOT output salary figures or workforce counts (those come from official statistics). Use conservative, realistic {c['name']} data."""


def validate(v):
    need = ["name", "summary", "forecast_note", "trend_summary", "category", "education",
            "qualifications", "visa", "ratings", "fit", "unfit", "faqs"]
    for k in need:
        if k not in v or v[k] in (None, "", []):
            raise ValueError(f"缺字段 {k}")
    if v["category"] not in CATEGORIES:
        raise ValueError(f"非法 category: {v['category']}")
    for d in DIMS:
        if d not in v["ratings"]:
            raise ValueError(f"ratings 缺 {d}")
    return v


def to_seed(cc, isco, v, off):
    """off = 该 isco 的官方记录(可能 None)。薪资/人数走官方，其余走 LLM。"""
    c = COUNTRY[cc]
    cur_code = c["currency"]
    workforce = off.get("workforce") if off else None
    OCC = {"country_code": cc, "occ_code": isco, "occ_code_type": "ISCO08", "anzsco_code": isco,
           "anzsco_title": v["name"], "category": v["category"], "currency": cur_code,
           "workforce_size": workforce, "shortage_listed": int(v.get("shortage", 0)),
           "is_migration": int(v.get("is_migration", 1)), "is_public_servant": 0,
           "growth_areas": v.get("growth", [])}
    TEXT = {"name": v["name"], "summary": v["summary"], "forecast_note": v["forecast_note"],
            "trend_summary": v["trend_summary"]}
    EDU = [{"stage": e["stage"], "duration": e.get("duration"), "cost_min": _clamp(e.get("cost_min")),
            "cost_max": _clamp(e.get("cost_max")), "cost_note": e.get("cost_note")} for e in v["education"]]
    QUAL = [{"qual_name": q["qual_name"], "issuer": q.get("issuer"), "note": q.get("note"),
             "is_mandatory": int(q.get("is_mandatory", 1))} for q in v["qualifications"]]
    # 官方薪资:mean -> "Average salary"(喂 avg_salary)，median -> "Median salary"
    SAL = []
    if off:
        src = f"Official {'PNAD-C (IBGE)' if cc == 'BR' else 'ENOE (INEGI)'}, annualized"
        if off.get("mean_annual"):
            SAL.append({"experience": "Average salary", "salary_min": _clamp(off["mean_annual"]),
                        "salary_max": _clamp(off["mean_annual"]), "salary_note": src, "currency": cur_code})
        if off.get("median_annual"):
            SAL.append({"experience": "Median salary", "salary_min": _clamp(off["median_annual"]),
                        "salary_max": _clamp(off["median_annual"]), "salary_note": src, "currency": cur_code})
    VISA = [{"visa_subclass": str(x["visa_subclass"])[:40], "visa_name": x.get("visa_name"),
             "description": x.get("description")} for x in v["visa"]]
    RAT = [{"dimension": d, "label": v["ratings"][d][0], "stars": float(v["ratings"][d][1])} for d in DIMS]
    FAQS = [{"faq_type": f.get("faq_type"), "question": f["question"], "answer": f["answer"]} for f in v["faqs"]]
    return OCC, TEXT, EDU, QUAL, SAL, VISA, RAT, v["fit"], v["unfit"], FAQS


def run(cc, limit, rest, archive, codes=None):
    assert cc in OFFICIAL, "仅 BR/MX"
    c = COUNTRY[cc]
    native_locale = c["native_locale"]
    off_all = json.load(open(OFFICIAL[cc], encoding="utf-8"))
    name_field = NAME_KEY[cc]
    uni = load_universe()
    if codes:
        targets = [uni[x] for x in codes if x in uni]
    else:
        targets = list(uni.values())
    if limit:
        targets = targets[:limit]
    system = build_system(cc)
    print(f"[{cc}] 官方+LLM 合并入库 待处理 {len(targets)} | 官方薪资覆盖 "
          f"{sum(1 for v in off_all.values() if v.get('mean_annual'))} | model={config.DEEPSEEK_MODEL}", flush=True)
    arc = load_archive(cc) if archive else None
    okc = fail = 0
    for idx, u in enumerate(targets, 1):
        isco, title = u["isco"], u["label_en"]
        off = off_all.get(isco)
        tag = f"{idx}/{len(targets)} {isco} {title[:36]}"
        try:
            v = validate(_gen_official(system, cc, isco, title))
            args = to_seed(cc, isco, v, off)
            with get_cursor() as cur:
                occ_id = seed_occupation_en(cur, *args)
                name_local = (off or {}).get(name_field)
                inject_native_name(cur, v["name"], native_locale, name_local, cc)
            okc += 1
            if arc is not None:
                arc[isco] = {"isco": isco, "title_en": title, "official": off, **v}
                save_archive(cc, arc)
            sal = f"{off.get('mean_annual')}/{off.get('median_annual')}" if off else "—(无官方)"
            print(f"  [{tag}] -> id={occ_id} {v['name']} [{v['category']}] sal={sal} wf={(off or {}).get('workforce')}", flush=True)
        except Exception as e:
            fail += 1
            print(f"  [{tag}] 失败: {e}", flush=True)
        if rest and idx < len(targets):
            time.sleep(rest)
    print(f"[{cc}] 完成：成功 {okc}，失败 {fail}", flush=True)


def _gen_official(system, cc, isco, title):
    from scripts import _deepseek_rest
    return _deepseek_rest.complete_json(system, build_prompt_official(cc, isco, title))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--rest", type=int, default=0)
    ap.add_argument("--archive", action="store_true")
    ap.add_argument("--codes", default="", help="逗号分隔的 ISCO 码，定向重试")
    a = ap.parse_args()
    run(a.country, a.limit, a.rest, a.archive, [c.strip() for c in a.codes.split(",") if c.strip()] or None)
