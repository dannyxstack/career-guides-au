"""并行批量翻译 translation_src 缺失的 (src_hash, locale) 到目标语言（幂等）。

替代单线程 translate_strings.py 跑全量大任务：用线程池并发多个 DeepSeek 批次，
吞吐 ~workers 倍。复用 translate_strings 的 system_prompt / translate_batch（同样的
去华人化、保留专名/数字/货币规则），写 translations 表（ON DUPLICATE KEY 幂等）。

每个工作单元 = 一个 locale 的一批 src（默认 batch 20，避免 50 串超 max_tokens 触发逐条回退）。
失败的批次记录后跳过（下次重跑补齐，幂等）。

运行：python -m scripts.translate_parallel [--workers 12] [--batch 20] [--locales en,es,...] [--limit N]
"""
import sys, os, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from db.connection import get_cursor
from video_pipeline import config, llm, azure_translate, baidu_translate
from scripts.translate_strings import LOCALES, LANG_NAME, system_prompt, translate_batch

_print_lock = threading.Lock()


def log(msg):
    with _print_lock:
        print(msg, flush=True)


def pending(loc, limit):
    with get_cursor() as cur:
        sql = ("SELECT s.src_hash, s.src_text FROM translation_src s "
               "LEFT JOIN translations t ON t.src_hash=s.src_hash AND t.locale=%s "
               "WHERE t.src_hash IS NULL")
        cur.execute(sql + (" LIMIT %s" % int(limit) if limit else ""), (loc,))
        return cur.fetchall()


def do_chunk(loc, chunk, model):
    texts = [r["src_text"] for r in chunk]
    try:
        res = translate_batch(texts, LANG_NAME[loc], loc)
    except Exception:
        # 整批失败（多为长度不匹配/超时）→ 拆半重试，避免逐条
        if len(chunk) > 1:
            mid = len(chunk) // 2
            return do_chunk(loc, chunk[:mid], model) + do_chunk(loc, chunk[mid:], model)
        return []  # 单条仍失败，跳过（下次重跑补）
    # 按实际后端打 gen_model 标签（百度 -> Azure -> LLM 的优先级）
    used = (baidu_translate.MODEL_LABEL if baidu_translate.enabled()
            else azure_translate.MODEL_LABEL if azure_translate.enabled() else model)
    rows = [(r["src_hash"], loc, t, used) for r, t in zip(chunk, res) if t]
    if rows:
        with get_cursor() as cur:
            cur.executemany(
                "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", rows)
    return rows


def run(locales, workers, batch, limit):
    model = llm.current_model()
    # 组装所有 (loc, chunk) 工作单元
    units = []
    for loc in locales:
        todo = pending(loc, limit)
        for i in range(0, len(todo), batch):
            units.append((loc, todo[i:i + batch]))
        log(f"[plan] {loc}: {len(todo)} 串 -> {(len(todo)+batch-1)//batch} 批")
    total_units = len(units)
    log(f"[start] {total_units} 批 × ~{batch} 串，workers={workers} model={model}")
    done_units = written = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(do_chunk, loc, ch, model): (loc, len(ch)) for loc, ch in units}
        for fut in as_completed(futs):
            loc, _ = futs[fut]
            try:
                rows = fut.result()
                written += len(rows)
            except Exception as e:
                log(f"  [{loc}] 批异常: {e}")
            done_units += 1
            if done_units % 50 == 0 or done_units == total_units:
                log(f"  进度 {done_units}/{total_units} 批，累计写入 {written}")
    log(f"[done] 写入 {written} 条译文")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--locales", default=",".join(LOCALES))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    run([x.strip() for x in a.locales.split(",") if x.strip()], a.workers, a.batch, a.limit)
