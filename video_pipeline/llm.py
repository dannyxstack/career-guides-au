"""大纲生成的 LLM 后端分派。按 config.LLM_PROVIDER 选择 claude / openai / deepseek。

统一入口 complete_json(system, prompt, schema) -> dict：
- claude：output_config.format（json_schema）
- openai：response_format=json_schema（strict，要求 schema 全字段 required + additionalProperties:false）
- deepseek：OpenAI 兼容接口的 json_object 模式（不强制 schema，靠 prompt 约束）
"""

import json
import re

from video_pipeline import config


def _extract_json(text: str) -> dict:
    """从模型输出里稳健地抽出 JSON 对象（容忍代码块包裹）。"""
    text = (text or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end + 1]
    return json.loads(text)


def current_model() -> str:
    """当前 provider 实际使用的模型名（写入 platform_contents.gen_model）。"""
    return {
        "claude": config.CLAUDE_MODEL,
        "openai": config.OPENAI_MODEL,
        "deepseek": config.DEEPSEEK_MODEL,
    }.get(config.LLM_PROVIDER, config.LLM_PROVIDER)


def complete_json(system: str, prompt: str, schema: dict) -> dict:
    """调当前 provider，返回解析好的 JSON dict。"""
    provider = config.LLM_PROVIDER
    if provider == "claude":
        return _claude(system, prompt, schema)
    if provider == "openai":
        return _openai(system, prompt, schema)
    if provider == "deepseek":
        return _deepseek(system, prompt)
    raise ValueError(f"未知 LLM_PROVIDER={provider!r}（可选 claude/openai/deepseek）")


def _claude(system: str, prompt: str, schema: dict) -> dict:
    from anthropic import Anthropic

    client = Anthropic(api_key=config.require("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=4000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    text = next(b.text for b in resp.content if b.type == "text")
    return _extract_json(text)


def _openai(system: str, prompt: str, schema: dict) -> dict:
    from openai import OpenAI

    client = OpenAI(
        api_key=config.require("OPENAI_API_KEY"),
        base_url=config.OPENAI_BASE_URL or None,
    )
    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        max_tokens=4000,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "video_outline", "strict": True, "schema": schema},
        },
    )
    return _extract_json(resp.choices[0].message.content)


def _deepseek(system: str, prompt: str) -> dict:
    from openai import OpenAI

    client = OpenAI(
        api_key=config.require("DEEPSEEK_API_KEY"),
        base_url=config.DEEPSEEK_BASE_URL,
    )
    # DeepSeek 仅支持 json_object 模式（prompt 里已含 JSON 结构说明，且出现 "json" 字样）
    resp = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        max_tokens=4000,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return _extract_json(resp.choices[0].message.content)
