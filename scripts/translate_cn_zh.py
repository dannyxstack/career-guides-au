"""限定翻译：只把 CN 采集产生的缺失 zh-CN 源串翻成简体中文（不波及全局 --all）。
待翻清单由 collect 阶段写入 .codex_tmp/cn_zh_todo.json(+_hash.json)。英文=母本不翻 en。
幂等：每批写库后可续跑（重跑会跳过已存在的 zh-CN）。
运行：python -m scripts.translate_cn_zh [--batch 50]
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts.translate_v2 import translate_batch, MODEL

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODO = os.path.join(REPO, ".codex_tmp", "cn_zh_todo.json")
TODO_H = os.path.join(REPO, ".codex_tmp", "cn_zh_todo_hash.json")
LOC = "zh-CN"


def main(batch):
    texts = json.load(open(TODO, encoding="utf-8"))
    hashes = json.load(open(TODO_H, encoding="utf-8"))
    assert len(texts) == len(hashes)
    # 续跑：跳过已有 zh-CN
    with get_cursor() as cur:
        ph = ",".join(["%s"] * len(hashes))
        cur.execute(f"SELECT src_hash FROM translations_v2 WHERE locale=%s AND src_hash IN ({ph})", [LOC] + hashes)
        have = {r["src_hash"] for r in cur.fetchall()}
    todo = [(h, t) for h, t in zip(hashes, texts) if h not in have]
    print(f"[cn-zh] 待翻 {len(todo)} (已有 {len(have)}) model={MODEL}", flush=True)
    done = 0
    for i in range(0, len(todo), batch):
        chunk = todo[i:i + batch]
        txts = [t for _, t in chunk]
        try:
            res = translate_batch(txts, LOC)
        except Exception as e:
            print(f"  批 {i} 整批失败({e})，逐条", flush=True)
            res = []
            for tx in txts:
                try:
                    res.append(translate_batch([tx], LOC)[0])
                except Exception:
                    res.append(None)
        rows = [(h, LOC, t, MODEL) for (h, _), t in zip(chunk, res) if t]
        with get_cursor() as cur:
            cur.executemany("INSERT INTO translations_v2 (src_hash,locale,text,gen_model) VALUES (%s,%s,%s,%s) "
                            "ON DUPLICATE KEY UPDATE text=VALUES(text),gen_model=VALUES(gen_model)", rows)
        done += len(rows)
        print(f"  [cn-zh] {done}/{len(todo)}", flush=True)
    print(f"[cn-zh] 完成，写入 {done}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=50)
    main(ap.parse_args().batch)
