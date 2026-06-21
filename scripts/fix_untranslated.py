"""修复"译文与源串完全相同"的可疑未翻条目（多为 LLM 回退/回显导致）。
对每个非 zh-CN locale，取 text==src_text 的条目，用 DeepSeek 按该 locale 的 prompt 重译并覆盖。
zh-Hant 走简→繁转换 prompt：真正简繁无差异的会原样返回，无害。"""
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import llm
from scripts.translate_strings import translate_batch, LANG_NAME

LOCALES = ["zh-Hant", "en", "es", "pt", "vi", "th", "ms", "id", "ja"]


def run(locales, batch):
    model = llm.current_model()
    for loc in locales:
        with get_cursor() as cur:
            cur.execute("SELECT s.src_hash, s.src_text FROM translations t JOIN translation_src s "
                        "ON s.src_hash=t.src_hash WHERE t.locale=%s AND t.text=s.src_text", (loc,))
            todo = cur.fetchall()
        if not todo:
            print(f"[{loc}] 无需修复")
            continue
        print(f"[{loc}] 待修复 {len(todo)}")
        fixed = 0
        for i in range(0, len(todo), batch):
            chunk = todo[i:i + batch]
            texts = [r["src_text"] for r in chunk]
            try:
                res = translate_batch(texts, LANG_NAME[loc], loc)
            except Exception:
                res = []
                for tx in texts:
                    try:
                        res.append(translate_batch([tx], LANG_NAME[loc], loc)[0])
                    except Exception:
                        res.append(None)
            rows = [(r["src_hash"], loc, t, model) for r, t in zip(chunk, res) if t]
            with get_cursor() as cur:
                cur.executemany(
                    "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", rows)
            fixed += len(rows)
        print(f"[{loc}] 重译写入 {fixed}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--locales", default=",".join(LOCALES))
    ap.add_argument("--batch", type=int, default=30)
    a = ap.parse_args()
    run([x.strip() for x in a.locales.split(",") if x.strip()], a.batch)
