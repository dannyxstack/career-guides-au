# -*- coding: utf-8 -*-
"""纯百度翻译 FR（法国）职业数据，直到百度额度用尽即停（不回退 Azure/DeepSeek）。

与 translate_scope 的区别：直接调用 baidu_translate.translate（绕开会自动回退到
Azure/DeepSeek 的 translate_batch）。语义：
  - 遇 BaiduAuthError（额度用尽 54004 / 凭据失效等永久错误）-> 立即置 STOP，停全部。
  - 遇单条内容错误（如敏感词 20003、方向不支持）-> 跳过该条，继续。
  - 每 FLUSH 条增量写库（幂等 ON DUPLICATE KEY UPDATE），随时中断不丢已翻进度。
  - 按 locale 分组顺序处理：额度中途耗尽时，已处理完的语言是完整的。

复用 translate_scope 的 in_scope_src / pending 收集待翻源串。

运行：
  PYTHONIOENCODING=utf-8 python -m scripts.translate_fr_baidu \
    [--locales es,pt,vi,th,ms,id,zh-Hant,ja,de] [--workers 8] [--limit N]
"""
import sys, os, argparse, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import baidu_translate
from scripts.translate_scope import in_scope_src, pending

STOP = threading.Event()
_lock = threading.Lock()
_cnt = {"ok": 0, "skip": 0}
_stop_reason = [""]

FLUSH = 50  # 每积累这么多条译文写一次库


def log(m):
    with _lock:
        print(m, flush=True)


def task(unit):
    """翻一条：成功返回入库行；额度用尽置 STOP；单条错误跳过。"""
    loc, h, text = unit
    if STOP.is_set():
        return None
    try:
        dst = baidu_translate.translate([text], loc)[0]
    except baidu_translate.BaiduAuthError as e:
        if not STOP.is_set():
            _stop_reason[0] = str(e)
            STOP.set()
            log(f"[STOP] 百度不可用（额度用尽/凭据失效）：{e}")
        return None
    except Exception as e:  # 单条内容错误（敏感词/方向不支持等）：跳过
        with _lock:
            _cnt["skip"] += 1
        return None
    if not dst:
        return None
    with _lock:
        _cnt["ok"] += 1
    return (h, loc, dst, baidu_translate.MODEL_LABEL)


def flush(buf):
    if not buf:
        return
    rows, buf[:] = list(buf), []
    with get_cursor() as cur:
        cur.executemany(
            "INSERT INTO translations (src_hash, locale, text, gen_model) VALUES (%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE text=VALUES(text), gen_model=VALUES(gen_model)", rows)


def run(countries, locales, workers, limit):
    if not baidu_translate.enabled():
        log("[abort] 百度翻译未配置（BAIDU_TRANSLATE_APPID / API_KEY）或已禁用")
        return
    scope = in_scope_src(countries)
    log(f"[scope] 国家={','.join(countries)} 范围内唯一源串 {len(scope):,}")

    # 按 locale 分组构建工作单元（保持 locale 顺序，便于额度耗尽时按语言完整落地）
    units = []
    for loc in locales:
        todo = pending(loc, scope)
        log(f"[{loc}] 待翻 {len(todo):,}")
        for r in todo:
            units.append((loc, r["src_hash"], r["src_text"]))
    if limit:
        units = units[:limit]
    total = len(units)
    log(f"[start] 共 {total:,} 条待翻（workers={workers}, QPS={__import__('video_pipeline.config', fromlist=['x']).BAIDU_TRANSLATE_QPS}）")

    buf = []
    WINDOW = max(workers * 20, 200)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        i = 0
        while i < total and not STOP.is_set():
            window = units[i:i + WINDOW]
            for f in [ex.submit(task, u) for u in window]:
                r = f.result()
                if r:
                    buf.append(r)
                    if len(buf) >= FLUSH:
                        flush(buf)
                        log(f"  进度 写入 {_cnt['ok']:,} / 跳过 {_cnt['skip']:,}")
            i += WINDOW
    flush(buf)
    log(f"[结束] 写入 {_cnt['ok']:,} 条 · 跳过 {_cnt['skip']:,} 条"
        + (f" · 停因：{_stop_reason[0]}" if _stop_reason[0] else " · 全部处理完"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default="FR")
    ap.add_argument("--locales", default="es,pt,vi,th,ms,id,zh-Hant,ja,de")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    run([x.strip() for x in a.countries.split(",") if x.strip()],
        [x.strip() for x in a.locales.split(",") if x.strip()], a.workers, a.limit)
