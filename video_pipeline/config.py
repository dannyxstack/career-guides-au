"""集中读取 .env 配置与项目路径。所有第三方密钥仅从环境变量读取，绝不硬编码。"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---- 路径 ----
REPO_ROOT = Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "video_pipeline"
REMOTION_DIR = PKG_ROOT / "remotion"
SPECS_DIR = PKG_ROOT / "specs"        # 生成的 inputProps.json
OUT_DIR = PKG_ROOT / "out"            # 渲染成片 mp4
# TTS 音频写到 Remotion 的 public/ 下，渲染时用 staticFile() 加载
AUDIO_DIR = REMOTION_DIR / "public" / "audio"
AUDIO_PUBLIC_PREFIX = "audio"
# 每个场景的幻灯片背景图（方案C：视频画面=幻灯片）
SLIDES_DIR = REMOTION_DIR / "public" / "slides"
SLIDES_PUBLIC_PREFIX = "slides"

for _d in (SPECS_DIR, OUT_DIR, AUDIO_DIR, SLIDES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---- 大纲生成 LLM 提供方（claude / openai / deepseek）----
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude").strip().lower()
PROMPT_VERSION = "outline-v1"

# Claude
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")  # 留空用官方地址

# DeepSeek（OpenAI 兼容接口）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# ---- Azure 语音合成 ----
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "")
# 中文/英文音色，可在 .env 覆盖。默认专业男声播音腔。
AZURE_VOICE_ZH = os.getenv("AZURE_VOICE_ZH", "zh-CN-YunyangNeural")
AZURE_VOICE_EN = os.getenv("AZURE_VOICE_EN", "en-AU-NatashaNeural")

# SSML 解说风格调优（让语音更像真人解说）
# style 需匹配音色支持的风格；不支持会被忽略（回到中性，不报错）。
AZURE_TTS_STYLE = os.getenv("AZURE_TTS_STYLE", "narration-professional")
AZURE_TTS_STYLE_DEGREE = os.getenv("AZURE_TTS_STYLE_DEGREE", "1.1")  # 风格强度 0.01~2
AZURE_TTS_RATE = os.getenv("AZURE_TTS_RATE", "+6%")                  # 语速微调
AZURE_TTS_EMPHASIZE_NUMBERS = os.getenv("AZURE_TTS_EMPHASIZE_NUMBERS", "1") \
    in ("1", "true", "yes", "True")

# ---- Pexels（B-roll，后期阶段）----
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# ---- Web 界面 ----
WEB_HOST = os.getenv("VIDEO_WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("VIDEO_WEB_PORT", "8000"))

# ---- 渲染并行度 ----
# Remotion --concurrency：同时渲染的帧数。可填整数或百分比（如 "80%"）。
# 默认 80% 核心；内存紧张时调低（每路并发约占一个 Chromium 页 + 数百 MB 内存）。
# 留空则用 Remotion 自身默认（约 50% 核心）。
RENDER_CONCURRENCY = os.getenv("VIDEO_RENDER_CONCURRENCY", "80%")


def require(name: str) -> str:
    """取一个必填配置，缺失时报清晰的错误（不打印值）。"""
    val = os.getenv(name, "")
    if not val:
        raise RuntimeError(f"缺少必填环境变量 {name}，请在 .env 中配置（参考 .env.example）")
    return val
