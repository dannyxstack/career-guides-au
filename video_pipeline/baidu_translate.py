"""百度翻译开放平台·大模型文本翻译封装（appid + Bearer Token，JSON 接口）。

端点 /ait/api/aiTextTranslate；鉴权 Authorization: Bearer <API_KEY>；请求体 JSON：
{"appid","from","to","q"}；响应 {"trans_result":[{"src","dst"}]}。
源语言固定简体中文（zh）。为与批量输入等长对齐，逐条翻译（一次一个 q），源串含换行时
把返回的多行 dst 用换行重组回一条。

设计要点（与 azure_translate 对齐，便于上层统一回退）：
- enabled()：配置了 APPID + API_KEY 且本进程未被禁用时为真（线程安全）。
- 永久性失败（token 无效/账户/授权等）-> BaiduAuthError，触发 disable() + 回退。
- 频率/超时类 -> 退避重试。
- 全局限速：多线程共享一个最小请求间隔（1/QPS）。
"""
import time
import threading
import requests

from video_pipeline import config

# translation_src 源串均为简体中文
FROM_LANG = "zh"

# 站点 locale -> 百度翻译语言码（注意：spa/vie/may/cht/jp 为百度私有码，非 ISO）
LOCALE_TO_BAIDU = {
    "en": "en", "es": "spa", "pt": "pt", "vi": "vie", "th": "th",
    "ms": "may", "id": "id", "zh-Hant": "cht", "ja": "jp", "de": "de",
}

MODEL_LABEL = "baidu-llm-mt"

# 永久性错误码：本进程重试无意义，禁用并回退（凭据/账户/授权层面问题）
_FATAL_CODES = {"54001", "52003", "54004", "58000", "58002", "90107"}
# 可退避重试的错误码：超时/系统错误/频率限制
_RETRY_CODES = {"52001", "52002", "54003", "54005"}

_disabled = False
_lock = threading.Lock()

# —— 全局限速（多线程共享最小请求间隔）——
_rate_lock = threading.Lock()
_last_call = 0.0


class BaiduAuthError(Exception):
    """百度不可用（token 无效/未授权/余额不足等永久性失败），应回退到其它后端。"""


def enabled() -> bool:
    """配置了 APPID + API_KEY 且本进程未被禁用。"""
    if not (config.BAIDU_TRANSLATE_APPID and config.BAIDU_TRANSLATE_API_KEY):
        return False
    with _lock:
        return not _disabled


def disable():
    global _disabled
    with _lock:
        _disabled = True


def _throttle():
    """阻塞到距上次请求满足最小间隔（1/QPS），线程安全的全局限速。"""
    global _last_call
    qps = config.BAIDU_TRANSLATE_QPS or 10
    min_interval = 1.0 / qps if qps > 0 else 0
    with _rate_lock:
        wait = min_interval - (time.time() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()


def _translate_one(text: str, to: str, src_lang: str) -> str:
    """翻译单条，返回译文。源串含换行时把多行 dst 用换行重组。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + config.BAIDU_TRANSLATE_API_KEY,
    }
    for attempt in range(5):
        _throttle()
        body = {"appid": config.BAIDU_TRANSLATE_APPID, "from": src_lang, "to": to, "q": text}
        try:
            resp = requests.post(config.BAIDU_TRANSLATE_ENDPOINT, headers=headers,
                                 json=body, timeout=30)
        except requests.RequestException:
            time.sleep(1.5 * (attempt + 1))
            continue

        if resp.status_code != 200:
            time.sleep(1.5 * (attempt + 1))
            continue

        j = resp.json()
        if j.get("trans_result"):
            return "\n".join(item["dst"] for item in j["trans_result"])

        code = str(j.get("error_code", ""))
        msg = j.get("error_msg", "")
        if code in _FATAL_CODES:
            raise BaiduAuthError(f"{code} {msg}")
        if code in _RETRY_CODES:
            time.sleep(2.0 * (attempt + 1))  # 频率/超时：退避
            continue
        # 其它（如 58001 语言方向不支持、54000 参数为空）：不可重试
        raise RuntimeError(f"百度翻译错误 {code} {msg}")

    raise RuntimeError(f"百度翻译重试耗尽: {text[:40]!r}")


def translate(texts, loc, src_lang=FROM_LANG):
    """把 texts 批量译为 loc 对应语言，返回等长列表（内部逐条翻译，保证对齐）。"""
    to = LOCALE_TO_BAIDU.get(loc)
    if not to:
        raise ValueError(f"未知 locale={loc!r}，无百度目标语言映射")
    return [_translate_one(t, to, src_lang) for t in texts]
