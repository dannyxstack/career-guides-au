"""定点修复：把含「华人」的源串，针对非中文语言从英文枢纽重译并覆盖。

英文译文已用带「去华人化」规则的 LLM 翻好（neutralised），以英文为 source 用 Azure
重译这些条，可天然避开 vi/th/ms/id/ja 中保留「华人社区」措辞的问题。
zh-Hant 故意保留华人表述、且须简→繁直转，**不在修复范围**。
en 是枢纽本身，也不改。

幂等：ON DUPLICATE KEY UPDATE 直接覆盖。须在全量 translate_parallel 跑完后执行，
否则会被并发任务从中文源清回。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import azure_translate

# 从英文枢纽重译的目标语言：仅这些是用 Azure 从中文 MT 翻的、会带「华人」措辞。
# en/es/pt 是 LLM 带去华人化规则翻的、已干净，不覆盖；zh-Hant 故意保留、且须简→繁，排除。
PIVOT_LOCALES = ["vi", "th", "ms", "id", "ja"]
MODEL_LABEL = "azure-translator(en-pivot)"


def main():
    with get_cursor() as cur:
        cur.execute(
            "SELECT s.src_hash, t.text AS en FROM translation_src s "
            "JOIN translations t ON t.src_hash=s.src_hash AND t.locale='en' "
            "WHERE s.src_text LIKE '%华人%'")
        rows = cur.fetchall()
    print(f"含华人源串 {len(rows)} 条，从英文枢纽重译 {len(PIVOT_LOCALES)} 个语言")
    en_texts = [r["en"] for r in rows]
    hashes = [r["src_hash"] for r in rows]
    for loc in PIVOT_LOCALES:
        out = azure_translate.translate(en_texts, loc, src_lang="en")
        recs = [(h, loc, t, MODEL_LABEL) for h, t in zip(hashes, out) if t]
        with get_cursor() as cur:
            cur.executemany(
                "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", recs)
        print(f"  [{loc}] 覆盖 {len(recs)} 条")
    print("完成")


if __name__ == "__main__":
    main()
