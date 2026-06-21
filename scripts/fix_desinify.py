"""定向修复：对含「华人/中文社区」框架的源串，在所有外语 locale（zh-Hant 除外）
重新翻译并强制中和（删除该从句、面向国际读者），覆盖 translations。
DeepSeek 对中和规则执行偏弱，故单独加强 prompt 重跑这一小批。"""
import sys, os, hashlib, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import llm

# 需中和的外语（zh-CN 母本不动；zh-Hant 须保留华人表述，排除）
LOCALES = {"en": "English", "es": "Spanish (español)", "pt": "Portuguese (português)",
           "vi": "Vietnamese (Tiếng Việt)", "th": "Thai (ภาษาไทย)",
           "ms": "Malay (Bahasa Melayu)", "id": "Indonesian (Bahasa Indonesia)", "ja": "Japanese (日本語)"}
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"t": {"type": "string"}}, "required": ["t"]}


def h(s):
    return hashlib.sha1(s.strip().encode("utf-8")).hexdigest()


def sysmsg(lang):
    return (
        f"You translate Australian careers content from Simplified Chinese into {lang}. "
        f"CRITICAL: the source may mention the Chinese / Mandarin-speaking / 华人 community or a Chinese-language "
        f"advantage. You MUST NOT translate or mention that. DELETE such clauses/sentences entirely and write the "
        f"rest for a GENERAL international audience — do not replace '华人' with '中国系/Chinese/Trung Quốc' etc. "
        f"Keep proper nouns/acronyms (ANZSCO, visa numbers, Skills in Demand, JSA, ABS, Department of Home Affairs, "
        f"Seek, Indeed, Glassdoor) and all numbers/ranges/currency. Output only the translated text in {lang}."
    )


def one(src, lang):
    prompt = ('Translate the text below, omitting any Chinese-community wording, and return JSON '
              '{"t": "<translation>"}:\n' + src)
    out = llm.complete_json(sysmsg(lang), prompt, SCHEMA)
    return out.get("t", "")


def main():
    with get_cursor() as cur:
        cur.execute("SELECT src_hash, src_text FROM translation_src WHERE src_text LIKE %s OR src_text LIKE %s",
                    ("%华人%", "%中文%"))
        srcs = cur.fetchall()
    print(f"[fix] 需中和源串 {len(srcs)}，locale {len(LOCALES)}")
    model = llm.current_model()
    for loc, lang in LOCALES.items():
        rows = []
        for s in srcs:
            try:
                rows.append((s["src_hash"], loc, one(s["src_text"], lang), model))
            except Exception as e:
                print(f"  [{loc}] 跳过一条: {e}")
        with get_cursor() as cur:
            cur.executemany(
                "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", rows)
        print(f"  [{loc}] 覆盖 {len(rows)}")
    print("[fix] 完成")


if __name__ == "__main__":
    main()
