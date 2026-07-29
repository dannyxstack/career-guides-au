"""DeepSeek 的极简 REST 调用（用 requests，避免引入 openai 依赖）。
仅供 v2 新管线使用。OpenAI 兼容的 /chat/completions + json_object 模式。
"""
import json
import requests
from video_pipeline import config


def complete_json(system, prompt, timeout=120):
    """返回解析好的 JSON dict。DeepSeek json_object 模式。"""
    url = config.DEEPSEEK_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {config.require('DEEPSEEK_API_KEY')}",
               "Content-Type": "application/json"}
    body = {"model": config.DEEPSEEK_MODEL, "max_tokens": 8000,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}}
    r = requests.post(url, headers=headers, json=body, timeout=timeout)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    return json.loads(content)
