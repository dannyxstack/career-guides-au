"""Azure 语音合成：逐场景配音 + 采集词级时间戳生成字幕。

设计原则：
- 未配置 Azure key 或未装 SDK 时返回 None，整条流水线仍可在"无音频"下渲染。
- 逐场景合成，按真实音频时长驱动每个场景的画面时长。
- 用 Azure 的 word boundary 事件生成字幕分段（与音频精确对齐）。
"""

import html
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from video_pipeline import config  # noqa: E402

# 匹配阿拉伯数字金额/年限簇（含 $ , . 万千亿 ~ - %），用于加重音
_NUM_RE = re.compile(r"[\$＄]?[0-9０-９][0-9０-９,，.\$＄万千亿~～\-—%]*")


def _build_ssml(text: str, voice: str, locale: str) -> str:
    """把一段旁白包成带解说风格的 SSML：voice + express-as 风格 + 语速 + 数字重音。"""
    safe = html.escape(text, quote=False)
    if config.AZURE_TTS_EMPHASIZE_NUMBERS:
        safe = _NUM_RE.sub(lambda m: f'<emphasis level="moderate">{m.group(0)}</emphasis>', safe)

    inner = f'<prosody rate="{config.AZURE_TTS_RATE}">{safe}</prosody>'
    # 解说风格仅对中文音色套用（en-AU 音色多数不支持 express-as）
    if locale.startswith("zh") and config.AZURE_TTS_STYLE:
        inner = (f'<mstts:express-as style="{config.AZURE_TTS_STYLE}" '
                 f'styledegree="{config.AZURE_TTS_STYLE_DEGREE}">{inner}</mstts:express-as>')
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="https://www.w3.org/2001/mstts" '
        f'xml:lang="{locale}"><voice name="{voice}">{inner}</voice></speak>'
    )


def available() -> bool:
    if not (config.AZURE_SPEECH_KEY and config.AZURE_SPEECH_REGION):
        return False
    try:
        import azure.cognitiveservices.speech  # noqa: F401
        return True
    except ImportError:
        return False


def _chunk_captions(words: list[dict], duration: float, max_chars: int = 12) -> list[dict]:
    """把词级时间戳聚合成短字幕段。

    words: [{"text": str, "start": float(秒)}]
    返回 [{"text", "start", "end"}]，end 取下一段起点（末段取音频时长）。
    """
    if not words:
        return []
    segments: list[dict] = []
    buf = ""
    seg_start = None
    for w in words:
        if seg_start is None:                 # 每段起点 = 段内第一个词的时间
            seg_start = w["start"]
        buf += w["text"]
        # 到达长度阈值或遇到中文/英文断句标点就切段
        if len(buf) >= max_chars or (w["text"] and w["text"][-1] in "。！？，、.!?,"):
            segments.append({"text": buf.strip(), "start": round(seg_start, 3)})
            buf, seg_start = "", None
    if buf.strip():
        segments.append({"text": buf.strip(), "start": round(seg_start or 0.0, 3)})
    # 填 end
    for i, seg in enumerate(segments):
        seg["end"] = round(segments[i + 1]["start"] if i + 1 < len(segments) else duration, 3)
    return segments


def synthesize_scenes(outline: dict, locale: str, base_name: str) -> list[dict] | None:
    """为大纲每个场景的 narration 生成音频 + 字幕。

    返回与 scenes 一一对应的列表：
        [{"src": "audio/<name>_00.wav"(相对 public), "duration_sec": float,
          "captions": [{"text","start","end"}]}, ...]
    不可用时返回 None。
    """
    if not available():
        return None

    import azure.cognitiveservices.speech as speechsdk

    voice = config.AZURE_VOICE_ZH if locale.startswith("zh") else config.AZURE_VOICE_EN
    speech_config = speechsdk.SpeechConfig(
        subscription=config.AZURE_SPEECH_KEY, region=config.AZURE_SPEECH_REGION
    )
    speech_config.speech_synthesis_voice_name = voice
    # 放宽合成超时阈值，避免网络抖动/Azure 偶发变慢导致中断（默认 3000ms / RTF 2）
    speech_config.set_property_by_name("SpeechSynthesis_FrameTimeoutInterval", "30000")
    speech_config.set_property_by_name("SpeechSynthesis_RtfTimeoutThreshold", "10")

    results = []
    for idx, scene in enumerate(outline.get("scenes", [])):
        text = (scene.get("narration") or "").strip()
        fname = f"{base_name}_{idx:02d}.wav"
        out_path = config.AUDIO_DIR / fname
        rel_src = f"{config.AUDIO_PUBLIC_PREFIX}/{fname}"

        if not text:
            results.append({"src": None, "duration_sec": float(scene.get("duration_sec", 3)),
                            "captions": []})
            continue

        ssml = _build_ssml(text, voice, locale)
        words: list[dict] = []
        result = None
        for attempt in range(3):
            words = []
            audio_config = speechsdk.audio.AudioOutputConfig(filename=str(out_path))
            synth = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=audio_config)
            # audio_offset 单位是 100ns 刻度，/1e7 得秒
            synth.synthesis_word_boundary.connect(
                lambda evt: words.append({"text": evt.text, "start": evt.audio_offset / 1e7})
            )
            result = synth.speak_ssml_async(ssml).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                break
            detail = (result.cancellation_details.error_details
                      if result.reason == speechsdk.ResultReason.Canceled else str(result.reason))
            if attempt == 2:
                raise RuntimeError(f"Azure TTS 失败（场景 {idx}，已重试3次）：{detail}")
            print(f"[tts] 场景 {idx} 合成失败/超时，第{attempt + 1}次重试… ({detail[:80]})")
            time.sleep(1.5 * (attempt + 1))

        dur = result.audio_duration.total_seconds() if result.audio_duration else \
            float(scene.get("duration_sec", 3))
        results.append({
            "src": rel_src,
            "duration_sec": round(dur, 3),
            "captions": _chunk_captions(words, dur),
        })

    return results
