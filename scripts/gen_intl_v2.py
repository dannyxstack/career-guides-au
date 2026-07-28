"""英文母本采集器（v2 新管线）：按 ISCO-08 生成职业并直接以英文写入 v2 表。
本步接入瑞士(CH)；结构可扩展到其它国家。母本=英文，非英文译文后续由 translate_v2 产出。

运行：$env:LLM_PROVIDER="deepseek"; python -m scripts.gen_intl_v2 --country CH --codes 2512,2611,3112 [--limit N]
"""
import sys, os, json, argparse, time, re, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper_v2 import seed_occupation_en
from video_pipeline import config

TMP = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp")
UNIVERSE = os.path.join(TMP, "isco08_universe.json")

CATEGORIES = [
    "Agriculture & Environment", "Business, Finance & Legal", "Creative, Media & Personal Services",
    "Education & Community", "Engineering & Infrastructure", "Government & Public Sector",
    "Healthcare & Care", "Hospitality, Retail & Tourism", "IT & Digital",
    "Trades & Construction", "Transport, Logistics & Mining"]
DIMS = ["learning_difficulty", "learning_duration", "certification_difficulty", "job_demand", "competition",
        "work_intensity", "income_level", "future_prospect", "ai_risk", "pr_friendliness", "pr_difficulty"]

COUNTRY = {
    "CH": {"name": "Switzerland", "currency": "CHF", "official": "BFS/OFS (Swiss Federal Statistical Office), Eurostat",
           "visa": "EU/EFTA free movement / L permit (short-term) / B permit (residence) / third-country quota permit"},
    "IN": {"name": "India", "currency": "INR", "occ_type": "NCO2015",
           "official": "MoSPI Periodic Labour Force Survey (PLFS) & NSSO, NCO-2015 (Directorate General of Employment, Ministry of Labour & Employment)",
           "visa": "Employment Visa / E-Visa (high-skill, ~USD 25k min annual salary threshold) / Intra-Company Transfer / Business Visa / OCI & PIO for persons of Indian origin. India has no points-based skilled-migration scheme; inbound work authorisation is employer-sponsored and largely restricted to specialist roles"},
    # BR/MX：骨架统一 ISCO-08（occ_code_type=ISCO08）；本国分类(CBO/SINCO)仅作 official 数据参照。
    # native_locale：把 LLM 产出的本国语言职业名(name_local)直灌该语种 TM，translate_v2 不再重译。
    "BR": {"name": "Brazil", "currency": "BRL", "native_locale": "pt", "native_lang": "Brazilian Portuguese",
           "official": "IBGE / PNAD Contínua (Continuous National Household Sample Survey), CBO (Classificação Brasileira de Ocupações, Ministério do Trabalho e Emprego)",
           "visa": "Employer-sponsored work visa VITEM V (temporary residence for work) / Mercosur Residence Agreement (regional free movement) / CNIg professional authorisation. Brazil has no points-based skilled-migration scheme; inbound work authorisation is employer-sponsored"},
    "MX": {"name": "Mexico", "currency": "MXN", "native_locale": "es", "native_lang": "Mexican Spanish",
           "official": "INEGI / ENOE (National Survey of Occupation and Employment), SINCO (Sistema Nacional de Clasificación de Ocupaciones)",
           "visa": "Employer-sponsored Temporary Resident Visa with work permit (INM, via job offer) / Permanent Resident by points or family. Mexico has no dedicated points-based skilled-migration route for most roles; inbound work authorisation is employer-sponsored"},
    "CN": {"name": "China", "currency": "CNY", "native_locale": "zh-CN", "native_lang": "Simplified Chinese",
           "official": "National Bureau of Statistics (国家统计局) / China Population Census Yearbook 2020, MOHRSS CSCO occupation classification (GB/T 6565)",
           "visa": "Employer-sponsored Z work visa via the Foreigner's Work Permit (tiered A/B/C talent classification) / R visa for high-level foreign talent. China has no points-based skilled-migration or general PR route; inbound work authorisation is employer-sponsored"},
    # 北欧5国：骨架统一 ISCO-08；官方薪资/就业来自各国统计局(见 downloads/{cc}/{cc}_by_isco.json)，
    # 数字零 LLM；native_locale 灌本国语言职业名进 TM。
    "NO": {"name": "Norway", "currency": "NOK", "native_locale": "nb", "native_lang": "Norwegian (Bokmål)",
           "official": "Statistics Norway (SSB), STYRK-08 occupations — earnings table 11418 & employment table 11658; NAV Business Survey shortage data",
           "visa": "EEA/EFTA free movement (EU/EEA nationals) / Skilled Worker residence permit (job offer, completed degree or trade certificate, salary threshold) / Jobseeker permit. Norway is in the EEA/EFTA but not the EU"},
    "SE": {"name": "Sweden", "currency": "SEK", "native_locale": "sv", "native_lang": "Swedish",
           "official": "Statistics Sweden (SCB), SSYK 2012 (→ISCO-08) — wage structure & YREG employment; Swedish Public Employment Service Occupational Barometer",
           "visa": "EU/EEA free movement / employer-tied Work Permit (job offer meeting collective-agreement pay) / EU Blue Card for the highly qualified"},
    "FI": {"name": "Finland", "currency": "EUR", "native_locale": "fi", "native_lang": "Finnish",
           "official": "Statistics Finland, Classification of Occupations 2010 (ISCO-08 based) — Structure of Earnings & register-based employment; Labour Force Barometer",
           "visa": "EU/EEA free movement / Residence permit for an employed person (TTOL) / Specialist & EU Blue Card routes / D-visa fast track"},
    "DK": {"name": "Denmark", "currency": "DKK", "native_locale": "da", "native_lang": "Danish",
           "official": "Statistics Denmark, DISCO-08 occupations — LONS20 earnings; SIRI Positive Lists (shortage)",
           "visa": "EU/EEA free movement / Pay Limit Scheme / Positive List (skilled & higher-education shortage) / Fast-track & Researcher schemes. Denmark has EU opt-outs but labour free movement applies"},
    "IS": {"name": "Iceland", "currency": "ISK", "native_locale": "is", "native_lang": "Icelandic",
           "official": "Statistics Iceland, Istarf95/ISCO-88 occupations (mapped to ISCO-08 via ILO crosswalk) — VIN02001 earnings",
           "visa": "EEA/EFTA free movement (EU/EEA nationals) / work & residence permit for qualified professionals tied to a job offer & labour-market test. Iceland is in the EEA/EFTA but not the EU"},
    # CZ/HU/SG：四位 ISCO 官方薪资可得，升级为完整管线（官方薪资 + 规则评分 + LLM 文案）。
    # SG 工作语言即英文 → native_locale=None（不灌本地名）；CZ 官方捷克名已在 by_isco.json，
    # gen_nordic_official 运行时优先取官方 name_local。
    "CZ": {"name": "Czechia", "currency": "CZK", "native_locale": "cs", "native_lang": "Czech",
           "official": "Czech Statistical Office (ČSÚ) & ISPV Regional Wage Survey 2025 (private + public sector), CZ-ISCO (ISCO-08) occupations; Eurostat LFS employment",
           "visa": "EU/EEA free movement / Employee Card (long-term work & residence, job offer) / EU Blue Card for the highly qualified / Intra-Company Transfer"},
    "HU": {"name": "Hungary", "currency": "HUF", "native_locale": "hu", "native_lang": "Hungarian",
           "official": "Hungarian Central Statistical Office (KSH) 2023 gross earnings by occupation, HSCO'08 (ISCO-08 aligned); Eurostat LFS employment",
           "visa": "EU/EEA free movement / Work & residence permit (job offer) / EU Blue Card / Guest Worker permit for non-EU nationals"},
    "SG": {"name": "Singapore", "currency": "SGD", "native_locale": None, "native_lang": "English",
           "official": "Ministry of Manpower (MOM) Occupational Wage Survey 2025 & Comprehensive Labour Force Survey, SSOC 2024 (built on ISCO-08); Department of Statistics",
           "visa": "Employer-sponsored Employment Pass (professionals, points-based COMPASS framework) / S Pass (mid-skill, quota & levy) / Work Permit (semi-skilled). Singapore has no general points-based PR-by-migration route; work authorisation is employer-sponsored"},
}


def load_universe():
    return {u["isco"]: u for u in json.load(open(UNIVERSE, encoding="utf-8"))}


def build_system(cc):
    c = COUNTRY[cc]
    return (
        f"You are a labour-market and migration analyst for {c['name']}, fluent in the ISCO-08 occupation "
        f"classification, {c['official']} employment and salary data, and work/residence pathways "
        f"({c['visa']}). For a given ISCO-08 occupation you output pragmatic, concrete {c['name']} data. "
        f"Salaries are pre-tax annual figures in {c['currency']} (integers). Write for a general international "
        f"audience in natural English. Pick the occupation category from exactly these 11: {'; '.join(CATEGORIES)}. "
        "Output a single JSON object, no extra text."
    )


def build_prompt(cc, isco, title_en):
    c = COUNTRY[cc]
    dims = ", ".join(DIMS)
    nl = c.get("native_locale")
    eng_note = "ALL TEXT IN ENGLISH" if not nl else "ALL TEXT IN ENGLISH except name_local"
    name_local_line = ""
    if nl:
        name_local_line = (f"\n- name_local: the standard {c['native_lang']} occupation name (singular), "
                           f"as commonly used locally — THIS FIELD ONLY in {c['native_lang']}, everything else in English")
    return f"""{c['name']} ISCO-08 occupation:
- ISCO code: {isco}
- English title: {title_en}

Return a JSON object (all fields required, {eng_note}):
- name: standard English occupation name (singular, Title Case){name_local_line}
- summary: one-sentence intro (60-140 words)
- forecast_note: one paragraph on {c['name']} employment outlook (60-120 words)
- trend_summary: one paragraph on career/progression path (60-120 words)
- category: one of the 11 given categories (verbatim)
- is_migration: 0/1/2 (0=not a migration route, 1=direct skilled-migration friendly, 2=restricted; consider EU/EFTA free movement and {c['name']} permit thresholds)
- shortage: 0 or 1 (is it on a shortage/quota-relevant list)
- workforce_size: integer estimate of people employed in {c['name']}
- growth: array of 4 English keywords (hot areas)
- education: array of 2-3 {{stage, duration (e.g. "3 years"), cost_min (int {c['currency']}), cost_max (int), cost_note}}
- qualifications: array of 2-4 {{qual_name, issuer, note, is_mandatory (0/1)}}
- salaries: array of exactly 3 {{experience (e.g. "Entry (0-3 yrs)"), salary_min (int {c['currency']}), salary_max (int), salary_note}}
- visa: array of 2-4 {{visa_subclass (code/short, e.g. "B permit"/"EU/EFTA"), visa_name, description}}
- ratings: object keyed by these 11 dimensions: {dims}; each value = [english_label, score] where score is 1.0-10.0 (one decimal). Negative dimensions (ai_risk, competition, work_intensity, learning_difficulty, learning_duration, certification_difficulty, pr_difficulty): higher = worse.
- fit: array of 2-3 English strings (who it suits)
- unfit: array of 2 English strings
- faqs: array of 2-3 {{faq_type ("salary"/"migration"/...), question, answer}} (include one salary + one visa)
Only output realistic {c['name']} data; use conservative ranges when unsure."""


def gen(system, cc, isco, title_en):
    from scripts._deepseek_rest import complete_json
    return complete_json(system, build_prompt(cc, isco, title_en))


def validate(v):
    need = ["name", "summary", "forecast_note", "trend_summary", "category", "education", "qualifications",
            "salaries", "visa", "ratings", "fit", "unfit", "faqs"]
    for k in need:
        if k not in v or v[k] in (None, "", []):
            raise ValueError(f"缺字段 {k}")
    if v["category"] not in CATEGORIES:
        raise ValueError(f"非法 category: {v['category']}")
    for d in DIMS:
        if d not in v["ratings"]:
            raise ValueError(f"ratings 缺 {d}")
    return v


DEC_MAX = 99999999  # decimal(10,2) 上限。高收入国家/高端岗（如 CEO 卢比薪资）clamp 以防溢出。


def _clamp(x):
    if x is None:
        return None
    try:
        return min(int(round(float(x))), DEC_MAX)
    except (TypeError, ValueError):
        return None


def to_seed(cc, isco, v):
    c = COUNTRY[cc]
    OCC = {"country_code": cc, "occ_code": isco, "occ_code_type": c.get("occ_type", "ISCO08"), "anzsco_code": isco,
           "anzsco_title": v["name"], "category": v["category"], "currency": c["currency"],
           "workforce_size": v.get("workforce_size"), "shortage_listed": int(v.get("shortage", 0)),
           "is_migration": int(v.get("is_migration", 1)), "is_public_servant": 0,
           "growth_areas": v.get("growth", [])}
    TEXT = {"name": v["name"], "summary": v["summary"], "forecast_note": v["forecast_note"],
            "trend_summary": v["trend_summary"]}
    EDU = [{"stage": e["stage"], "duration": e.get("duration"), "cost_min": _clamp(e.get("cost_min")),
            "cost_max": _clamp(e.get("cost_max")), "cost_note": e.get("cost_note")} for e in v["education"]]
    QUAL = [{"qual_name": q["qual_name"], "issuer": q.get("issuer"), "note": q.get("note"),
             "is_mandatory": int(q.get("is_mandatory", 1))} for q in v["qualifications"]]
    SAL = [{"experience": s["experience"], "salary_min": _clamp(s.get("salary_min")), "salary_max": _clamp(s.get("salary_max")),
            "salary_note": s.get("salary_note")} for s in v["salaries"]]
    VISA = [{"visa_subclass": str(x["visa_subclass"])[:40], "visa_name": x.get("visa_name"),
             "description": x.get("description")} for x in v["visa"]]
    RAT = [{"dimension": d, "label": v["ratings"][d][0], "stars": float(v["ratings"][d][1])} for d in DIMS]
    FAQS = [{"faq_type": f.get("faq_type"), "question": f["question"], "answer": f["answer"]} for f in v["faqs"]]
    return OCC, TEXT, EDU, QUAL, SAL, VISA, RAT, v["fit"], v["unfit"], FAQS


def inject_native_name(cur, en_name, native_locale, name_local, cc):
    """把本国语言职业名直灌 TM（translate_v2 靠 src_hash=sha1(英文) 判重，预填即跳过重译）。"""
    if not (native_locale and name_local and en_name):
        return
    h = hashlib.sha1(en_name.encode("utf-8")).hexdigest()
    cur.execute("INSERT INTO translation_src_v2 (src_hash,src_text) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE src_text=VALUES(src_text)", (h, en_name))
    cur.execute("INSERT INTO translations_v2 (src_hash,locale,text,gen_model) VALUES (%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE text=VALUES(text),gen_model=VALUES(gen_model)",
                (h, native_locale, name_local, f"collected:{cc}"))


def archive_path(cc):
    d = os.path.join(os.path.dirname(__file__), "..", "downloads", cc.lower())
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "collected.json")


def load_archive(cc):
    p = archive_path(cc)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_archive(cc, arc):
    json.dump(arc, open(archive_path(cc), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def run(cc, codes, limit, rest, archive=False):
    assert cc in COUNTRY, f"暂只支持 {list(COUNTRY)}"
    c = COUNTRY[cc]
    native_locale = c.get("native_locale")
    uni = load_universe()
    if codes:
        targets = [uni[c2] for c2 in codes if c2 in uni]
    else:
        targets = list(uni.values())
    if limit:
        targets = targets[:limit]
    system = build_system(cc)
    print(f"[{cc}] 待生成 {len(targets)} (currency={c['currency']}) "
          f"native_locale={native_locale or '-'} archive={archive} model={config.DEEPSEEK_MODEL}", flush=True)
    arc = load_archive(cc) if archive else None
    okc = fail = 0
    for idx, u in enumerate(targets, 1):
        isco, title = u["isco"], u["label_en"]
        tag = f"{idx}/{len(targets)} {isco} {title[:40]}"
        try:
            v = validate(gen(system, cc, isco, title))
            args = to_seed(cc, isco, v)
            with get_cursor() as cur:
                occ_id = seed_occupation_en(cur, *args)
                inject_native_name(cur, v["name"], native_locale, v.get("name_local"), cc)
            okc += 1
            if arc is not None:
                arc[isco] = {"isco": isco, "title_en": title, **v}
                save_archive(cc, arc)
            nl_show = f" 〔{native_locale}:{v.get('name_local')}〕" if native_locale else ""
            print(f"  [{tag}] -> {cc} id={occ_id} {v['name']}{nl_show} [{v['category']}] mig={v.get('is_migration')}", flush=True)
        except Exception as e:
            fail += 1
            print(f"  [{tag}] 失败: {e}", flush=True)
        if rest and idx < len(targets):
            time.sleep(rest)
    print(f"[{cc}] 完成：成功 {okc}，失败 {fail}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--codes", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--rest", type=int, default=0)
    ap.add_argument("--archive", action="store_true", help="归档原始 LLM 输出到 downloads/<cc>/collected.json")
    a = ap.parse_args()
    run(a.country, [c.strip() for c in a.codes.split(",") if c.strip()] or None, a.limit, a.rest, a.archive)
