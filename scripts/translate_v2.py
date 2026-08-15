"""英文母本 TM：把 translation_src_v2 的英文源串翻成 11 个目标语，写 translations_v2（幂等）。
源=英文，故不翻 en。只翻尚缺的 (src_hash, locale)。
默认只翻 aijobrisk 站实际引用的串（in_aijobrisk=1，先跑 scripts/mark_aijobrisk_src.py 打标记）；
加 --all 翻全部源串（含未引用的）。
后端优先级沿用：百度大模型 -> Azure -> DeepSeek。
运行：python -m scripts.translate_v2 [--locales de,fr,it] [--batch 50] [--limit N] [--dry] [--all]
"""
import sys, os, argparse, json, time, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import requests
from db.connection import get_cursor
from scripts import _deepseek_rest
from video_pipeline import azure_translate as _azure
from video_pipeline import config

# 网络类错误（DNS 解析失败、连接中断、超时）应重试而非跳过；
# 内容类错误（返回长度不匹配等）交由上层逐条隔离。
_NET_ERRORS = (requests.exceptions.ConnectionError, requests.exceptions.Timeout)


def _is_net_error(e):
    """真·网络类错误：DNS/连接/超时/429/5xx——可长时间退避重试（扛断网窗口）。"""
    if isinstance(e, _NET_ERRORS):
        return True
    if isinstance(e, requests.exceptions.HTTPError):
        return getattr(getattr(e, "response", None), "status_code", 0) in (429, 500, 502, 503, 504)
    return False

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


# Azure 字符预算：累计送 Azure 翻译的字符数达阈值后自动切 DeepSeek（0=不限）。
AZURE_CHAR_BUDGET = 0
_azure_chars = 0
_azure_lock = threading.Lock()


def _azure_over_budget():
    if not AZURE_CHAR_BUDGET:
        return False
    with _azure_lock:
        return _azure_chars >= AZURE_CHAR_BUDGET


def _add_azure_chars(n):
    global _azure_chars
    with _azure_lock:
        _azure_chars += n
        over = AZURE_CHAR_BUDGET and _azure_chars >= AZURE_CHAR_BUDGET
    if over:
        print(f"  [Azure 预算已达 {_azure_chars:,}/{AZURE_CHAR_BUDGET:,} 字符，后续切 DeepSeek]")


def translate_batch(texts, loc, backend="deepseek", max_net_retries=20, max_content_retries=2):
    """英文母本翻译（from-English）。backend=azure 走 Azure Translator（直译文本、等长返回，
    无 JSON 空体/截断问题，自带 4 次重试）；否则直连 DeepSeek（json_object 模式）。
    backend=azure 且已达字符预算或配额耗尽（403）时，自动改用 DeepSeek。"""
    if backend == "azure" and not _azure_over_budget():
        try:
            res = _azure.translate(texts, loc, src_lang="en")
            _add_azure_chars(sum(len(t) for t in texts))
            return res
        except _azure.AzureQuotaExhausted:
            print("  [Azure 配额耗尽，切 DeepSeek]")
        # 落到下方 DeepSeek 路径
    lang = LANG_NAME[loc]
    prompt = "Translate these strings (JSON array) and return {\"t\": [...]} with the same length:\n" + \
        json.dumps(texts, ensure_ascii=False)
    net_tries = content_tries = 0
    while True:
        try:
            out = _deepseek_rest.complete_json(system_prompt(lang), prompt)
            res = out.get("t") or []
            if len(res) != len(texts):
                raise ValueError(f"长度不匹配 expect {len(texts)} got {len(res)}")
            return res
        except Exception as e:
            if _is_net_error(e):
                # 断网可能持续数分钟：长退避、大重试预算，绝不跳过。
                net_tries += 1
                if net_tries > max_net_retries:
                    raise
                wait = min(60, 2 ** net_tries)
                print(f"    网络失败，{wait}s 后重试 ({net_tries}/{max_net_retries}): {e}")
                time.sleep(wait)
            else:
                # 空体/截断（JSONDecodeError）或长度不匹配：少量软重试即可清掉瞬时空体；
                # 确定性截断则快速抛出，交由上层拆成更小/逐条重试，不空耗网络预算。
                content_tries += 1
                if content_tries > max_content_retries:
                    raise
                time.sleep(1)


MODEL = f"deepseek:{config.DEEPSEEK_MODEL}"


def _translate_chunk(chunk, loc, backend="deepseek"):
    """翻译一个 chunk：整批失败则逐条重试隔离（截断/坏串）。返回可写入的 (src_hash, text) 列表。"""
    texts = [r["src_text"] for r in chunk]
    try:
        res = translate_batch(texts, loc, backend)
    except Exception as e:
        print(f"  整批失败({e})，逐条重试")
        res = []
        for tx in texts:
            try:
                res.append(translate_batch([tx], loc, backend)[0])
            except Exception as e2:
                print(f"    单条失败，跳过: {e2}")
                res.append(None)
    return [(r["src_hash"], t) for r, t in zip(chunk, res) if t]


def _write_chunk(pairs, loc, model):
    if not pairs:
        return 0
    rows = [(h, loc, t, model) for (h, t) in pairs]
    with get_cursor() as cur:
        cur.executemany("INSERT INTO translations_v2 (src_hash,locale,text,gen_model) VALUES (%s,%s,%s,%s) "
                        "ON DUPLICATE KEY UPDATE text=VALUES(text),gen_model=VALUES(gen_model)", rows)
    return len(rows)


def run(locales, batch, limit, dry, include_unreferenced=False, workers=1, backend="deepseek"):
    model = _azure.MODEL_LABEL if backend == "azure" else MODEL
    if backend == "azure":
        # 补 Azure 目标语映射（模块默认缺 fr）。
        _azure.LOCALE_TO_AZURE.update({"fr": "fr", "es": "es", "zh-CN": "zh-Hans"})
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
        print(f"[{loc}] 待翻译 {len(todo)} 串 ({scope}, model={model}, workers={workers})")
        if dry:
            continue
        chunks = [todo[i:i + batch] for i in range(0, len(todo), batch)]
        total = len(todo)
        done = 0
        if workers <= 1:
            for chunk in chunks:
                done += _write_chunk(_translate_chunk(chunk, loc, backend), loc, model)
                print(f"  [{loc}] {done}/{total}")
        else:
            # 网络 I/O 密集，多线程可并发发批（每线程各自的 DB 连接，天然安全）。
            lock = threading.Lock()

            def work(chunk):
                nonlocal done
                n = _write_chunk(_translate_chunk(chunk, loc, backend), loc, model)
                with lock:
                    done += n
                    print(f"  [{loc}] {done}/{total}")

            with ThreadPoolExecutor(max_workers=workers) as ex:
                list(ex.map(work, chunks))
        print(f"[{loc}] 完成，写入 {done}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--locales", default=",".join(LOCALES))
    ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--all", dest="include_unreferenced", action="store_true",
                    help="翻译全部源串（含 aijobrisk 未引用的）；默认只翻 in_aijobrisk=1")
    ap.add_argument("--workers", type=int, default=1, help="并发 worker 数（网络 I/O，>1 提速）")
    ap.add_argument("--backend", choices=["deepseek", "azure"], default="deepseek",
                    help="翻译后端；azure 达字符预算或配额耗尽后自动切 deepseek")
    ap.add_argument("--azure-char-budget", type=int, default=0,
                    help="Azure 累计字符预算，达到后切 DeepSeek（0=不限）")
    a = ap.parse_args()
    AZURE_CHAR_BUDGET = a.azure_char_budget
    run([x.strip() for x in a.locales.split(",") if x.strip()], a.batch, a.limit, a.dry,
        a.include_unreferenced, a.workers, a.backend)
