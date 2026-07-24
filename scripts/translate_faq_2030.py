"""一次性：用 Azure Translator 把职业详情 FAQ 的通用问句译成 7 种主流语言。
源串（英文母本）：Will AI replace {name} by 2030?
{name} 用 HTML notranslate span 包裹，Azure 保留占位符并放在正确的语法位置，
故译文跨职业通用（渲染时把 {name} 替换成英文职业名）。
输出 aijobrisk/src/data/faq_2030.json：{ locale: "…{name}…" }。
"""
import json
import os
import pathlib
import sys
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]

# —— 读 .env 里的 Azure 凭据（不打印 KEY）——
def load_env():
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env()
KEY = ENV.get("AZURE_TRANSLATOR_KEY", "")
REGION = ENV.get("AZURE_TRANSLATOR_REGION", "")
ENDPOINT = ENV.get("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
if not KEY:
    sys.exit("缺少 AZURE_TRANSLATOR_KEY")

# 英文母本模板 + notranslate 占位符（HTML 模式）
PLACEHOLDER = "{name}"
SRC_HTML = f'Will AI replace <span class="notranslate">{PLACEHOLDER}</span> by 2030?'
SRC_PLAIN = f"Will AI replace {PLACEHOLDER} by 2030?"

# 7 种主流语言（Azure 目标码）
TARGETS = {
    "es": "es",       # Spanish
    "fr": "fr",       # French
    "de": "de",       # German
    "pt": "pt",       # Portuguese
    "ja": "ja",       # Japanese
    "zh-Hans": "zh-Hans",  # Simplified Chinese
    "ko": "ko",       # Korean
}

def translate(to_code):
    url = ENDPOINT.rstrip("/") + "/translate"
    params = {"api-version": "3.0", "from": "en", "to": to_code, "textType": "html"}
    headers = {
        "Ocp-Apim-Subscription-Key": KEY,
        "Content-Type": "application/json",
    }
    if REGION:
        headers["Ocp-Apim-Subscription-Region"] = REGION
    r = requests.post(url, params=params, headers=headers, json=[{"text": SRC_HTML}], timeout=30)
    r.raise_for_status()
    txt = r.json()[0]["translations"][0]["text"]
    # 去掉 span 包裹，仅留 {name} 占位符
    txt = txt.replace(f'<span class="notranslate">{PLACEHOLDER}</span>', PLACEHOLDER)
    # 兜底：某些语言 Azure 可能改写 span 属性顺序/大小写，用正则清掉任何包住占位符的 span
    import re
    txt = re.sub(r"<span[^>]*>\s*(\{name\})\s*</span>", r"\1", txt)
    txt = re.sub(r"</?span[^>]*>", "", txt)  # 清残留 span
    return txt.strip()

out = {"en": SRC_PLAIN}
for loc, code in TARGETS.items():
    t = translate(code)
    if PLACEHOLDER not in t:
        print(f"⚠ {loc}: 占位符丢失 -> {t!r}", file=sys.stderr)
    out[loc] = t
    print(f"{loc}: {t}")

dest = ROOT / "aijobrisk" / "src" / "data" / "faq_2030.json"
dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n写入 {dest}")
