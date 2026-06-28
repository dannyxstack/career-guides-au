"""Azure Translator（Cognitive Services 文本翻译）批量翻译封装。

源语言固定简体中文（zh-Hans）。一次请求翻译一个 batch（数组），返回等长译文列表。
配额耗尽时抛 AzureQuotaExhausted，由上层切换到 LLM（DeepSeek）回退。

设计要点：
- enabled()：仅当配置了 KEY 且本进程未因配额耗尽被禁用时为真（线程安全）。
- 403 + 配额类错误码 -> AzureQuotaExhausted（永久性，触发全局禁用 + 回退）。
- 429 限流 -> 退避重试若干次，仍失败抛普通异常（由上层拆批/跳过重跑）。
"""
import time
import threading
import requests

from video_pipeline import config

# translation_src 源串均为简体中文
FROM_LANG = "zh-Hans"

# 站点 locale -> Azure Translator 目标语言码
LOCALE_TO_AZURE = {
    "en": "en", "es": "es", "pt": "pt", "vi": "vi", "th": "th",
    "ms": "ms", "id": "id", "zh-Hant": "zh-Hant", "ja": "ja", "de": "de",
}

MODEL_LABEL = "azure-translator"

_disabled = False
_lock = threading.Lock()


class AzureQuotaExhausted(Exception):
    """Azure 不可用（配额耗尽 403 或凭据无效/缺失 401），应永久回退到其它后端。
    两者都属于本进程内重试无意义的永久性失败，统一触发 disable() + 回退。"""


def enabled() -> bool:
    """配置了 KEY 且本进程未被禁用（配额未耗尽）。"""
    if not config.AZURE_TRANSLATOR_KEY:
        return False
    with _lock:
        return not _disabled


def disable():
    """配额耗尽后调用，停止本进程后续 Azure 调用，全部走回退后端。"""
    global _disabled
    with _lock:
        _disabled = True


def translate(texts, loc, src_lang=FROM_LANG):
    """把 texts 批量译为 loc 对应语言，返回等长列表。src_lang 默认简体中文，
    定点修复时可传 'en' 以英文为枢纽（避开‘华人社区’措辞）。"""
    to = LOCALE_TO_AZURE.get(loc)
    if not to:
        raise ValueError(f"未知 locale={loc!r}，无 Azure 目标语言映射")
    url = config.AZURE_TRANSLATOR_ENDPOINT.rstrip("/") + "/translate"
    params = {"api-version": "3.0", "from": src_lang, "to": to}
    headers = {
        "Ocp-Apim-Subscription-Key": config.AZURE_TRANSLATOR_KEY,
        "Content-Type": "application/json",
    }
    if config.AZURE_TRANSLATOR_REGION:
        headers["Ocp-Apim-Subscription-Region"] = config.AZURE_TRANSLATOR_REGION
    body = [{"text": t} for t in texts]

    last_err = None
    for attempt in range(4):
        try:
            resp = requests.post(url, params=params, headers=headers,
                                 json=body, timeout=60)
        except requests.RequestException as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
            continue

        if resp.status_code == 200:
            data = resp.json()
            out = [item["translations"][0]["text"] for item in data]
            if len(out) != len(texts):
                raise ValueError(f"Azure 返回长度不匹配 expect {len(texts)} got {len(out)}")
            return out

        # 401（凭据无效/缺失）/ 403（配额耗尽）：本进程内重试无意义 -> 永久禁用并回退
        if resp.status_code in (401, 403):
            raise AzureQuotaExhausted(f"{resp.status_code} {resp.text[:200]}")
        # 429：限流 -> 退避重试
        if resp.status_code == 429:
            retry_after = float(resp.headers.get("Retry-After", 2 * (attempt + 1)))
            last_err = RuntimeError(f"429 限流: {resp.text[:120]}")
            time.sleep(retry_after)
            continue
        # 其它错误（如 400 请求格式）：抛普通异常，由上层拆批/跳过重跑。
        last_err = RuntimeError(f"Azure {resp.status_code}: {resp.text[:200]}")
        break

    raise RuntimeError(f"Azure 翻译失败: {last_err}")
