# -*- coding: utf-8 -*-
"""把本会话 aijobrisk-go 新增英文文案（口径 B 全量：EU Blue Card 18 国各一条）
翻译到 5 语言（es/pt/ja/fr/zh-CN），用 Azure Translator（en 为源），
写入 aijobrisk-go/data/translations-v2/{loc}.{md5(src)%8}.json（幂等合并）。

Blue Card 段落在 Go 运行时是 Tr(replaceCountry(tmpl, CountryName(cc,L)), L)，
故 TM key 内嵌该 locale 的本地化国名，须逐 locale 生成 key。
"""
import os, sys, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from video_pipeline import azure_translate as az

GO = os.path.join(os.path.dirname(__file__), "..", "aijobrisk-go", "data")
TR_DIR = os.path.join(GO, "translations-v2")
N_SHARDS = 8
LOCALES = ["es", "pt", "ja", "fr", "zh-CN", "de"]
# 站点 locale -> Azure 目标语言码（补 fr / zh-CN / de，不动共享模块）
AZ_TO = {"es": "es", "pt": "pt", "ja": "ja", "fr": "fr", "zh-CN": "zh-Hans", "de": "de"}

# ---- EU Blue Card 模板 + 18 国（对齐 migration.go） ----
BLUE_TMPL = ("As an EU member state, {C} admits skilled foreign professionals mainly through "
             "the EU Blue Card and national work-permit routes. Eligibility depends on your "
             "qualifications, a qualifying job offer and salary threshold — not on any single "
             "occupation. Rules and salary thresholds change yearly, so always check the official "
             "source before making plans.")
BLUE_CC = ["FR", "ES", "IT", "NL", "BE", "AT", "PL", "PT", "GR", "HU",
           "CZ", "RO", "LU", "SK", "SI", "HR", "FI", "SE", "EE", "LV", "LT"]

# ---- locale 无关的其余 27 条英文母本 ----
FLAT = [
    # 7 特殊国 body
    "Denmark does not take part in the EU Blue Card but runs its own skilled-migration schemes, such as the Pay Limit Scheme and the Positive List for occupations facing shortages. Eligibility depends on your job offer and salary, not on any single occupation.",
    "As an EEA country, Norway grants skilled-worker residence permits to qualified professionals who hold a concrete job offer meeting local pay and qualification rules; long-term residence can follow. Requirements are set nationally and change over time.",
    "As an EEA country, Iceland issues residence and work permits to qualified professionals with a job offer, subject to labour-market and qualification checks; permanent residence can follow after several years.",
    "Switzerland admits non-EU/EFTA professionals under an annually capped quota system for qualified specialists with a Swiss job offer, via bilateral agreements; settlement permits can follow after several years of residence.",
    "Singapore's main professional work pass is the Employment Pass, granted to qualifying professionals with a job offer above a salary threshold; long-term holders may apply for Permanent Residence. Criteria are set by the Ministry of Manpower and updated regularly.",
    "Japan issues status-of-residence work visas by field, and high-scoring professionals can use the Highly Skilled Professional route, which offers a faster path to permanent residence. Eligibility depends on your qualifications and employer, not on any single occupation.",
    "Korea's E-7 skilled-worker visa is granted to qualifying professionals with a local job offer, and long-term holders may move to F-2/F-5 residence. Requirements are set by the Korea Immigration Service and change over time.",
    # 7 link text
    "Danish Immigration Service (nyidanmark.dk)",
    "Norwegian Directorate of Immigration (UDI)",
    "Directorate of Immigration Iceland (utl.is)",
    "State Secretariat for Migration (SEM)",
    "Ministry of Manpower (MOM)",
    "Immigration Services Agency of Japan",
    "Korea Immigration Service",
    "EU Immigration Portal",
    # tier labels
    "National statistics office (self-collected / register / census)",
    "Eurostat EU-LFS (employment official; 4-digit modelled)",
    "ILOSTAT (UN ILO)",
    # static_pages
    "Official",
    "Data sources & authority by country",
    "We currently cover 43 countries. Occupation employment and pay come from each country's own official statistics, graded by a three-level authority scale.",
    # table headers
    "Country", "Data source", "Classification", "Authority", "Occupation pay",
    # job.html
    "Immigration pathways",
    # 新增国国名（es/pt/ja/fr 的 TM 缺，导致国名标题/标签回退英文；zh-CN 走 ZhCN 字段不受影响）
    "Estonia", "Latvia", "Lithuania", "Switzerland",
    # —— Career outlook 图表（从业人数 + 薪资）——
    "Projected employment", "Chart scale", "Indexed", "Absolute",
    "Historical", "Projected", "Source",
    "Trend shown for the ISCO 2-digit occupational group (shared by all occupations in the group), not measured for this occupation alone.",
    "Indexed view sets the base year to 100.",
    "Salary trend & forecast", "Forecast (estimate)", "monthly",
    "Trend shown for the ISCO 1-digit occupational major group (shared by all occupations in the group), not measured for this occupation alone.",
    "Future years are an estimate: IMF WEO inflation outlook plus the group's observed real-wage trend.",
    # —— SEO/GEO 批次：职业页答案优先 + Human Moat + /data 开放数据集 ——
    "AI risk score",
    "How we score the human moat",
    "Last updated",
    "Data",
    # methodology #human-moat
    "The Human Moat",
    "The human moat is the part of a job that stays hard for AI to do — the tasks that depend on physical presence, accountability, human trust, judgement under ambiguity, or tacit skill. The wider the moat, the more resilient the occupation, even when parts of it are automatable.",
    "We score every occupation on four dimensions that together shape its moat:",
    "How much of the day-to-day work generative AI can already do.",
    "How much of the role rests on skills AI cannot easily replicate.",
    "Whether AI is narrowing the entry-level and junior pathways.",
    "How much AI can augment the role and lift productivity rather than replace it.",
    "A wide human moat with low task exposure signals a resilient career; a narrow moat with high exposure signals a role to reshape early. Every occupation page reuses this same framework so scores are comparable across jobs and countries.",
    # /data page
    "AI Job Risk data",
    "An open ranking of occupations by generative-AI task exposure. Below are the 100 most-exposed and 100 safest jobs across all countries we cover; the full dataset is available as JSON.",
    "Covering", "occupations",
    "Top 100 most exposed to AI", "Top 100 safest from AI",
    "AI exposure",
    "Exposure is the generative-AI task-exposure percentile (ILO Working Paper 140, calibrated with Eloundou et al.). Figures are indicative estimates. Data is licensed CC BY 4.0.",
    # —— 行业 AI 采纳率图 + methodology 说明 ——
    "AI adoption across all industries", "AI adoption in",
    "Measured & to date",
    "AI-adoption rate = share of firms using AI in any business function.",
    "US trajectory shown as a benchmark; national data pending for this country.",
    "This sector is a proxy (not separately measured by the source).",
    "Values after 2026 are a modelled projection.",
    "AI adoption rate by industry",
    "The chart on each industry page tracks the AI adoption rate — the share of firms in a sector using AI in any of their business functions. This is different from AI exposure above: exposure measures how automatable the work is, while adoption measures how many firms have actually started using AI.",
    "Adoption levels come from the US Census Bureau's Business Trends and Outlook Survey (BTOS), the authoritative measured series of firm AI use by industry over time. Each sector is anchored to its latest measured BTOS reading (current use and firms' six-month expectation), and the national BTOS series is used to fit the timing of a logistic diffusion curve.",
    "The curve is shown from five years ago to five years ahead. Values through the present are measured or anchored to BTOS; values after 2026 are a modelled projection (shown as a dashed line), and the pre-2023 segment is a back-cast, since firm AI use was negligible before generative AI. Figures are indicative, not forecasts.",
    "Two limitations: a few sectors not separately measured by BTOS (for example management of companies and public administration) use a proxy value; and BTOS covers the United States only, so other countries currently display the US trajectory as a benchmark until national data is available.",
    # —— industry 页三段式 + 数据驱动 FAQ ——
    "Occupations by AI exposure",
    "which occupations are most exposed to AI?",
    "The most AI-exposed occupations in this industry are",
    "which occupations are most resilient to AI?",
    "The most AI-resilient occupations in this industry are",
    "what is the AI adoption rate?",
    "Around",
    "of firms in this sector currently use AI in a business function, projected to reach about",
    "by 2031.",
    "(US benchmark; national data pending.)",
    "is it a high-risk industry for AI?",
    "The median AI exposure across these occupations is",
    "A higher score means more day-to-day tasks are exposed to AI — it does not mean the jobs disappear.",
    "how many people work in these occupations?",
    "About",
    "people are employed across the tracked occupations in",
    "Occupations can belong to several industries, so this sums occupation employment rather than industry totals.",
    "low", "moderate", "high",
]


def load_country_names():
    d = json.load(open(os.path.join(GO, "derived", "COUNTRY_NAME.json"), encoding="utf-8"))
    return d


def load_tm(loc):
    """载入某 locale 现有 TM（合并所有分片），用于解析本地化国名。"""
    tm = {}
    for i in range(N_SHARDS):
        p = os.path.join(TR_DIR, f"{loc}.{i}.json")
        if os.path.exists(p):
            tm.update(json.load(open(p, encoding="utf-8")))
    return tm


def country_name(cc, loc, cnames, tm):
    """复刻 Go CountryName(cc, loc)。"""
    v = cnames.get(cc)
    if not v or not v.get("en"):
        return cc
    if loc == "zh-CN":
        return v.get("zh-CN") or v["en"]
    return tm.get(v["en"], v["en"])  # 缺译回退英文名


def az_translate(texts, loc):
    return az.translate(texts, loc, src_lang="en", )  # 见下方 monkeypatch 说明


def main():
    cnames = load_country_names()
    # 给 azure 模块补 fr / zh-CN 目标映射
    az.LOCALE_TO_AZURE.update(AZ_TO)

    for loc in LOCALES:
        tm = load_tm(loc)
        pairs = {}  # src_key(runtime) -> english_to_translate

        # 1) flat：key == english
        for s in FLAT:
            pairs[s] = s
        # 2) blue card：key 用本地化国名，翻译源用英文名版本
        for cc in BLUE_CC:
            en_name = cnames[cc]["en"]
            loc_name = country_name(cc, loc, cnames, tm)
            key = BLUE_TMPL.replace("{C}", loc_name)      # 运行时 Tr 的 key
            en_src = BLUE_TMPL.replace("{C}", en_name)    # 送 Azure 的英文
            pairs[key] = en_src

        # 已存在译文则跳过（幂等）
        todo = {k: v for k, v in pairs.items() if not tm.get(k)}
        print(f"[{loc}] 待翻 {len(todo)}/{len(pairs)}")
        if not todo:
            continue

        keys = list(todo.keys())
        srcs = [todo[k] for k in keys]
        out = {}
        B = 25
        for i in range(0, len(srcs), B):
            res = az.translate(srcs[i:i+B], loc, src_lang="en")
            for k, t in zip(keys[i:i+B], res):
                out[k] = t
            print(f"  {min(i+B,len(srcs))}/{len(srcs)}")

        # 合并写回分片
        shard_new = {}
        for k, t in out.items():
            h = int(hashlib.md5(k.encode("utf-8")).hexdigest(), 16) % N_SHARDS
            shard_new.setdefault(h, {})[k] = t
        for h, kv in shard_new.items():
            p = os.path.join(TR_DIR, f"{loc}.{h}.json")
            cur = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
            cur.update(kv)  # 新键追加到末尾，保持原有顺序与紧凑单行格式
            json.dump(cur, open(p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(f"[{loc}] 写入 {len(out)} 条，覆盖分片 {sorted(shard_new)}")


if __name__ == "__main__":
    main()
