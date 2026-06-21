"""把英文 UI 文案翻译成 6 个新语言，输出 site/src/data/ui_i18n.json（{locale:{key:text}}）。
DIM 维度标签一并翻译。幂等：已存在的语言键跳过（除非 --force）。"""
import sys, os, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from video_pipeline import llm

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "src", "data", "ui_i18n.json")
LOCALES = {"es": "Spanish (español)", "pt": "Portuguese (português)", "vi": "Vietnamese (Tiếng Việt)",
           "th": "Thai (ภาษาไทย)", "ms": "Malay (Bahasa Melayu)", "id": "Indonesian (Bahasa Indonesia)",
           "zh-Hant": "Traditional Chinese (繁體中文, 台灣/香港用語)", "ja": "Japanese (日本語)"}

UI_EN = {
    "siteTitle": "AU Career Guides", "tagline": "Data-driven occupation guides",
    "salary": "Salary", "ratings": "Ratings", "overall": "Overall", "education": "Education Path",
    "qualifications": "Qualifications", "visa": "Migration", "suitability": "Who it fits", "faq": "FAQ",
    "compare": "Compare", "nonMig": "Not a skilled migration occupation", "fit": "Fits", "unfit": "Not for",
    "experience": "Experience", "annual": "Annual (AUD)", "code": "Occupation code", "backHome": "← All occupations",
    "growth": "Career outlook", "growthKw": "Growth areas", "compareTitle": "Compare", "vs": "vs", "winner": "Higher",
    "note": "Estimated data, indicative only",
    "sources": "Data sources",
    "sourcesBody": "Salary ranges are estimates aggregated from public listings on Seek, Indeed, Glassdoor and ERI SalaryExpert; employment and demand forecasts cite Jobs and Skills Australia (JSA) and the Australian Bureau of Statistics (ABS); visa and migration details follow the latest occupation lists from the Department of Home Affairs and the relevant assessing authorities. Figures are indicative only — always refer to the latest official sources.",
    "seniorPay": "Senior pay", "training": "Training",
    "heroValue": "Explore Australian careers by salary, PR pathway, training time, job demand, and AI replacement risk.",
    "ctaBrowse": "Browse careers", "ctaCompare": "Compare two careers",
    "searchPh": "Search occupation…", "sortBy": "Sort", "allCareers": "All careers",
    "fPR": "PR pathway", "fHigh": "High salary", "fShort": "Short training", "noResult": "No matching occupations",
    "sortOverall": "Overall score", "sortPay": "Senior pay", "sortTrain": "Training time", "sortPR": "PR friendly",
    "secMigration": "Best for migration", "secIncome": "Best high-income careers", "secFast": "Fastest entry careers",
    "secCats": "Categories",
    "migOcc": "Skilled migration occupation", "byDim": "By dimension", "dimension": "Dimension",
    "stage": "Stage", "period": "Duration", "qualification": "Qualification", "issuer": "Issuer",
    "mandatory": "Required", "optional": "Optional", "visaCol": "Visa", "descCol": "Details",
    "nonMigVisa": "Visa pathways depend on matching the specific duties to the correct ANZSCO; refer to the latest Department of Home Affairs occupation lists and the relevant assessing authorities.",
    "winnerNote": '"Higher" is judged by dimension polarity (for negative dimensions such as AI risk / competition / difficulty, lower is better).',
}
DIM_EN = {"learning_difficulty": "Learning", "learning_duration": "Duration", "certification_difficulty": "Certification",
          "job_demand": "Demand", "competition": "Competition", "work_intensity": "Intensity", "income_level": "Income",
          "future_prospect": "Prospects", "ai_risk": "AI Risk", "pr_friendliness": "PR Friendly", "pr_difficulty": "PR Difficulty"}
DIMDESC_EN = {
    "income_level": "Higher is better: greater pay ceiling and bargaining power",
    "job_demand": "Higher is better: more openings, easier to find work",
    "future_prospect": "Higher is better: stronger industry growth and advancement",
    "pr_friendliness": "Higher is better: smoother skilled-migration pathway",
    "ai_risk": "Lower is better: less likely to be automated",
    "competition": "Lower is better: fewer rivals for jobs and promotion",
    "work_intensity": "Lower is better: less physical strain and overtime",
    "learning_difficulty": "Lower is better: easier to get started",
    "learning_duration": "Shorter is better: faster entry to the field",
    "certification_difficulty": "Lower is better: qualifications easier to obtain",
    "pr_difficulty": "Lower is better: fewer migration hurdles and shorter queues",
}


def schema(keys):
    return {"type": "object", "additionalProperties": False,
            "properties": {k: {"type": "string"} for k in keys}, "required": list(keys)}


def translate_map(src, lang):
    sysmsg = (f"You are a professional UI localization translator for an Australian careers website. "
              f"Translate each value into {lang}. Keep proper nouns/acronyms (Seek, Indeed, Glassdoor, ERI SalaryExpert, "
              f"Jobs and Skills Australia, JSA, ABS, Department of Home Affairs, ANZSCO, AUD, PR, AI, FAQ, vs) as-is. "
              f"Keep it short and UI-appropriate. Return a JSON object with the SAME keys.")
    prompt = "Translate the values of this JSON object:\n" + json.dumps(src, ensure_ascii=False)
    return llm.complete_json(sysmsg, prompt, schema(src.keys()))


def main(force):
    data = {}
    if os.path.exists(OUT) and not force:
        data = json.load(open(OUT, encoding="utf-8"))
    for loc, lang in LOCALES.items():
        if loc in data and not force:
            print(f"[ui] {loc} 已存在，跳过")
            continue
        print(f"[ui] 翻译 {loc} …")
        ui = translate_map(UI_EN, lang)
        dim = translate_map(DIM_EN, lang)
        dimdesc = translate_map(DIMDESC_EN, lang)
        data[loc] = {"ui": ui, "dim": dim, "dimdesc": dimdesc}
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"[ui] 写出 {OUT}（{len(data)} 语言）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    main(ap.parse_args().force)
