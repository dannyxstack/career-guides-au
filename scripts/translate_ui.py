"""把全站 UI 文案（data.ts 的 UI['en'] 全量）翻译成各语言，输出/合并到
site/src/data/ui_i18n.json（{locale:{ui:{...},dim:{...},dimdesc:{...}}}）。

源以 data.ts 为单一真相：先用 `node scripts/_extract_ui.mjs` 生成 scripts/_ui_src.json，
本脚本读取其中的 ui 全量键。幂等：仅翻译目标语言尚缺的 key（新增 key 或新语言如 de），
已存在的键跳过（除非 --force）。维度标签 dim/dimdesc 一并补译。

必须 LLM_PROVIDER=deepseek。运行：
  node scripts/_extract_ui.mjs
  LLM_PROVIDER=deepseek python -m scripts.translate_ui [--force] [--locales de,ja] [--batch 40]
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from video_pipeline import llm

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "site", "src", "data", "ui_i18n.json")
SRC_UI = os.path.join(HERE, "_ui_src.json")

# 目标语言（zh-CN / en 为母本，不在此翻译）
LOCALES = {"es": "Spanish (español)", "pt": "Portuguese (português)", "vi": "Vietnamese (Tiếng Việt)",
           "th": "Thai (ภาษาไทย)", "ms": "Malay (Bahasa Melayu)", "id": "Indonesian (Bahasa Indonesia)",
           "zh-Hant": "Traditional Chinese (繁體中文, 台灣/香港用語)", "ja": "Japanese (日本語)",
           "de": "German (Deutsch)", "it": "Italian (italiano)", "nl": "Dutch (Nederlands)"}

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
    sysmsg = (f"You are a professional UI localization translator for an AI-era careers website ‘AI Career Graph’. "
              f"Translate each value into {lang}. "
              f"Keep proper nouns/acronyms as-is (AI Career Graph, AI, PR, FAQ, vs, ANZSCO, NOC, SOC, KldB, ROME, CNO, "
              f"Seek, Indeed, Glassdoor, ERI SalaryExpert, JSA, ABS, USCIS, IRCC, UKVI, INZ). "
              f"IMPORTANT: keep any placeholder tokens such as {{n}}, {{name}}, {{c}}, {{asof}} EXACTLY as-is (do not translate or remove them). "
              f"Preserve arrow/middot symbols (→ · — ×) and keep the wording short and UI-appropriate. "
              f"Return a JSON object with the SAME keys.")
    prompt = "Translate the values of this JSON object:\n" + json.dumps(src, ensure_ascii=False)
    return llm.complete_json(sysmsg, prompt, schema(src.keys()))


def chunked(d, n):
    items = list(d.items())
    for i in range(0, len(items), n):
        yield dict(items[i:i + n])


def translate_missing(src_map, existing, lang, batch):
    missing = {k: v for k, v in src_map.items() if k not in existing}
    out = dict(existing)
    for ch in chunked(missing, batch):
        res = translate_map(ch, lang)
        out.update({k: res.get(k, ch[k]) for k in ch})
    return out, len(missing)


def main(force, locales, batch):
    src = json.load(open(SRC_UI, encoding="utf-8"))
    UI_EN = src["ui"]
    data = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for loc, lang in LOCALES.items():
        if locales and loc not in locales:
            continue
        cur = data.get(loc, {})
        ui, nui = translate_missing(UI_EN, {} if force else cur.get("ui", {}), lang, batch)
        dim, nd = translate_missing(DIM_EN, {} if force else cur.get("dim", {}), lang, batch)
        dd, ndd = translate_missing(DIMDESC_EN, {} if force else cur.get("dimdesc", {}), lang, batch)
        data[loc] = {"ui": ui, "dim": dim, "dimdesc": dd}
        print(f"[ui] {loc}: +{nui} ui, +{nd} dim, +{ndd} dimdesc (total ui={len(ui)})", flush=True)
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"[ui] 写出 {OUT}（{len(data)} 语言）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--locales", default="")
    ap.add_argument("--batch", type=int, default=40)
    a = ap.parse_args()
    locs = [x.strip() for x in a.locales.split(",") if x.strip()]
    main(a.force, locs, a.batch)
