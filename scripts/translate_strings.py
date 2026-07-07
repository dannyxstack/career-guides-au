"""用 LLM 批量翻译 translation_src 中的源串到目标语言，写入 translations（幂等）。
只翻译尚缺的 (src_hash, locale)。支持 --locales / --batch / --limit / --dry。

翻译规则（见 system prompt）：保留专有名词/代码、数字区间、货币；
英文输出纯英文；并中和掉专门面向「华人/中文社区」的表述，改写为面向国际读者的通用表达。
"""
import sys, os, argparse, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import config, llm, azure_translate, baidu_translate

LOCALES = ["en", "es", "pt", "vi", "th", "ms", "id", "zh-Hant", "ja", "de"]
LANG_NAME = {"en": "English", "es": "Spanish (español)", "pt": "Portuguese (português)",
             "vi": "Vietnamese (Tiếng Việt)", "th": "Thai (ภาษาไทย)",
             "ms": "Malay (Bahasa Melayu)", "id": "Indonesian (Bahasa Indonesia)",
             "zh-Hant": "Traditional Chinese (繁體中文)", "ja": "Japanese (日本語)",
             "de": "German (Deutsch)"}

SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"t": {"type": "array", "items": {"type": "string"}}},
          "required": ["t"]}


def system_prompt(lang, loc=None):
    if loc == "zh-Hant":
        # 繁体中文：面向中文读者，做简→繁转换 + 用词在地化，保留原意与「华人」相关表述
        return (
            "你是繁体中文（台湾/香港用语习惯）本地化译者。把每个简体中文字符串转换为自然的繁體中文。\n"
            "规则：\n"
            "1. 保留专有名词与代码不变：ANZSCO、签证子类号（如 482/186/189/190）、Skills in Demand、MLTSSL、STSOL、"
            "TAFE、CPA、CA、CAANZ、AHPRA、TRA、ACS，以及机构名（Jobs and Skills Australia、JSA、ABS、"
            "Department of Home Affairs、Seek、Indeed、Glassdoor）。\n"
            "2. 保留所有数字、区间、百分比与货币金额。\n"
            "3. 这是面向中文读者的版本，**保留**与「華人/中文社群」相关的内容，不要删改其语义；仅做字形与用词的繁体在地化。\n"
            "4. 用词在地化（如：软件→軟體、网络→網路、信息→資訊、视频→影片，但勿过度），保持简洁、与原文等长等格式。仅输出译文。"
        )
    return (
        f"You are a professional localization translator for an Australian careers/occupations website. "
        f"Translate each given Simplified Chinese string into {lang}. Return translations in the SAME order and count.\n"
        "Rules:\n"
        "1. Keep these UNTRANSLATED verbatim: ANZSCO, visa subclass numbers (e.g. 482/186/189/190), "
        "'Skills in Demand', MLTSSL, STSOL, TAFE, CPA, CA, CAANZ, AHPRA, TRA, ACS, and organisation names "
        "(Jobs and Skills Australia, JSA, ABS, Department of Home Affairs, Seek, Indeed, Glassdoor).\n"
        "2. Preserve all numbers, ranges (e.g. 3~4年 -> '3-4 years' equivalent), percentages and currency amounts.\n"
        "3. Write for a GENERAL international audience. Remove or neutralise any wording specifically aimed at "
        "Chinese / Mandarin-speaking communities (e.g. '对华人' framing); never mention the Chinese community unless "
        "it is essential factual content. English output must be pure, natural English.\n"
        "4. Keep it concise and roughly the same length/format as the source. Output the translation text only, no notes.\n"
        f"5. CRITICAL: the ENTIRE output for every string must be written in {lang}. Even strings dominated by "
        f"proper nouns, salary figures or numbers must have all their connecting and descriptive words translated "
        f"into {lang} — do NOT leave them in English (unless the target language itself is English)."
    )


def translate_batch(texts, lang, loc=None):
    # 后端优先级：百度大模型翻译 -> Azure Translator -> LLM（DeepSeek）。
    # 每个专用后端遇永久性失败（凭据/配额）时本进程禁用并回退到下一个。
    if baidu_translate.enabled():
        try:
            return baidu_translate.translate(texts, loc)
        except baidu_translate.BaiduAuthError as e:
            baidu_translate.disable()
            print(f"[baidu] 不可用，回退 Azure/DeepSeek：{e}", flush=True)
    if azure_translate.enabled():
        try:
            return azure_translate.translate(texts, loc)
        except azure_translate.AzureQuotaExhausted as e:
            azure_translate.disable()
            print(f"[azure] 配额耗尽，后续回退 DeepSeek：{e}", flush=True)
    prompt = "Translate these strings (JSON array) and return {\"t\": [...]} with the same length:\n" + \
        json.dumps(texts, ensure_ascii=False)
    out = llm.complete_json(system_prompt(lang, loc), prompt, SCHEMA)
    res = out.get("t") or []
    if len(res) != len(texts):
        raise ValueError(f"长度不匹配 expect {len(texts)} got {len(res)}")
    return res


def run(locales, batch, limit, dry):
    model = llm.current_model()
    for loc in locales:
        with get_cursor() as cur:
            sql = ("SELECT s.src_hash, s.src_text FROM translation_src s "
                   "LEFT JOIN translations t ON t.src_hash=s.src_hash AND t.locale=%s "
                   "WHERE t.src_hash IS NULL")
            cur.execute(sql + (" LIMIT %s" % int(limit) if limit else ""), (loc,))
            todo = cur.fetchall()
        print(f"[{loc}] 待翻译 {len(todo)} 串 (model={model})")
        if dry:
            continue
        done = 0
        for i in range(0, len(todo), batch):
            chunk = todo[i:i + batch]
            texts = [r["src_text"] for r in chunk]
            try:
                res = translate_batch(texts, LANG_NAME[loc], loc)
            except Exception as e:
                print(f"  批 {i}-{i+len(chunk)} 整批失败({e})，逐条重试")
                res = []
                for tx in texts:
                    try:
                        res.append(translate_batch([tx], LANG_NAME[loc], loc)[0])
                    except Exception as e2:
                        print(f"    单条失败，跳过: {e2}")
                        res.append(None)
            rows = [(r["src_hash"], loc, t, model) for r, t in zip(chunk, res) if t]
            with get_cursor() as cur:
                cur.executemany(
                    "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", rows)
            done += len(rows)
            print(f"  [{loc}] {done}/{len(todo)}")
        print(f"[{loc}] 完成，写入 {done}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--locales", default=",".join(LOCALES))
    ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    run([x.strip() for x in a.locales.split(",") if x.strip()], a.batch, a.limit, a.dry)
