"""英文母本 TM：把 translation_src_v2 的英文源串翻成 11 个目标语，写 translations_v2（幂等）。
源=英文，故不翻 en。只翻尚缺的 (src_hash, locale)。
默认只翻 aijobrisk 站实际引用的串（in_aijobrisk=1，先跑 scripts/mark_aijobrisk_src.py 打标记）；
加 --all 翻全部源串（含未引用的）。
后端优先级沿用：百度大模型 -> Azure -> DeepSeek。
运行：python -m scripts.translate_v2 [--locales de,fr,it] [--batch 50] [--limit N] [--dry] [--all]
"""
import sys, os, argparse, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts import _deepseek_rest
from video_pipeline import config

# en 是母本，不在目标语内
LOCALES = ["es", "pt", "vi", "th", "ms", "id", "zh-Hant", "zh-CN", "ja", "de", "it", "nl", "fr"]
LANG_NAME = {"es": "Spanish (español)", "pt": "Portuguese (português)", "vi": "Vietnamese (Tiếng Việt)",
             "th": "Thai (ภาษาไทย)", "ms": "Malay (Bahasa Melayu)", "id": "Indonesian (Bahasa Indonesia)",
             "zh-Hant": "Traditional Chinese (繁體中文)", "zh-CN": "Simplified Chinese (简体中文)",
             "ja": "Japanese (日本語)", "de": "German (Deutsch)", "it": "Italian (italiano)",
             "nl": "Dutch (Nederlands)", "fr": "French (français)"}

SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"t": {"type": "array", "items": {"type": "string"}}}, "required": ["t"]}


def system_prompt(lang):
    return (
        f"You are a professional localization translator for an international careers/occupations website. "
        f"Translate each given English string into {lang}. Return translations in the SAME order and count.\n"
        "Rules:\n"
        "1. Keep proper nouns, classification codes and org names UNTRANSLATED verbatim: ISCO, ANZSCO, visa/permit "
        "codes (e.g. 482/186/189, EU Blue Card, Critical Skills), MLTSSL, TAFE, CPA, AHPRA, and org names "
        "(Eurostat, ISTAT, CBS, CSO, Jobs and Skills Australia, Seek, Indeed, Glassdoor).\n"
        "2. Preserve all numbers, ranges, percentages and currency amounts (keep currency symbols/codes).\n"
        "3. Write for a GENERAL international audience; natural, idiomatic target language.\n"
        "4. Keep it concise and roughly the same length/format as the source. Output the translation text only.\n"
        f"5. CRITICAL: the ENTIRE output for every string must be written in {lang}; do not leave descriptive words in English."
    )


def translate_batch(texts, loc):
    """英文母本翻译：直连 DeepSeek（正确 from-English，覆盖全部目标语）。
    旧的 baidu/azure 后端源语言固定中文、目标映射窄，不适配英文母本，故 v2 不用。"""
    lang = LANG_NAME[loc]
    prompt = "Translate these strings (JSON array) and return {\"t\": [...]} with the same length:\n" + \
        json.dumps(texts, ensure_ascii=False)
    out = _deepseek_rest.complete_json(system_prompt(lang), prompt)
    res = out.get("t") or []
    if len(res) != len(texts):
        raise ValueError(f"长度不匹配 expect {len(texts)} got {len(res)}")
    return res


MODEL = f"deepseek:{config.DEEPSEEK_MODEL}"


def run(locales, batch, limit, dry, include_unreferenced=False):
    model = MODEL
    # 默认只翻 aijobrisk 站实际引用的串（in_aijobrisk=1）；--all 时翻全部。
    ref_clause = "" if include_unreferenced else " AND s.in_aijobrisk=1"
    for loc in locales:
        with get_cursor() as cur:
            sql = ("SELECT s.src_hash, s.src_text FROM translation_src_v2 s "
                   "LEFT JOIN translations_v2 t ON t.src_hash=s.src_hash AND t.locale=%s "
                   "WHERE t.src_hash IS NULL" + ref_clause)
            cur.execute(sql + (" LIMIT %s" % int(limit) if limit else ""), (loc,))
            todo = cur.fetchall()
        scope = "全部源串" if include_unreferenced else "仅 aijobrisk 引用串"
        print(f"[{loc}] 待翻译 {len(todo)} 串 ({scope}, model={model})")
        if dry:
            continue
        done = 0
        for i in range(0, len(todo), batch):
            chunk = todo[i:i + batch]
            texts = [r["src_text"] for r in chunk]
            try:
                res = translate_batch(texts, loc)
            except Exception as e:
                print(f"  批 {i}-{i+len(chunk)} 整批失败({e})，逐条重试")
                res = []
                for tx in texts:
                    try:
                        res.append(translate_batch([tx], loc)[0])
                    except Exception as e2:
                        print(f"    单条失败，跳过: {e2}")
                        res.append(None)
            rows = [(r["src_hash"], loc, t, model) for r, t in zip(chunk, res) if t]
            with get_cursor() as cur:
                cur.executemany("INSERT INTO translations_v2 (src_hash,locale,text,gen_model) VALUES (%s,%s,%s,%s) "
                                "ON DUPLICATE KEY UPDATE text=VALUES(text),gen_model=VALUES(gen_model)", rows)
            done += len(rows)
            print(f"  [{loc}] {done}/{len(todo)}")
        print(f"[{loc}] 完成，写入 {done}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--locales", default=",".join(LOCALES))
    ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--all", dest="include_unreferenced", action="store_true",
                    help="翻译全部源串（含 aijobrisk 未引用的）；默认只翻 in_aijobrisk=1")
    a = ap.parse_args()
    run([x.strip() for x in a.locales.split(",") if x.strip()], a.batch, a.limit, a.dry, a.include_unreferenced)
