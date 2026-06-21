"""把"已审批大纲 + 职业数据 + 配音"拼成 Remotion 的 inputProps.json。

这份 JSON 是 Python 与 Remotion 之间唯一的数据契约。
"""

import json
from decimal import Decimal

from video_pipeline import config, images, slides, tts
from video_pipeline.data_source import get_occupation

# 平台 → Remotion composition id + 画幅
PLATFORM_COMP = {
    "tiktok_short": ("Short", "short-9x16"),
    "youtube_long": ("Long", "long-16x9"),
}

THEME = {"primary": "#10B981", "bg": "#0B1120", "accent": "#F59E0B", "font": "Inter"}


def _num(v):
    """Decimal/字符串金额 → int，便于前端动画。"""
    if v is None:
        return None
    if isinstance(v, Decimal):
        return int(v)
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return v


def build_spec(content_id: int, occupation_id: int, platform: str, locale: str,
               outline: dict, *, with_audio: bool = True) -> dict:
    """构建 inputProps 并写到 specs/<content_id>.json，返回 {path, comp_id, props}。"""
    comp_id, fmt = PLATFORM_COMP.get(platform, PLATFORM_COMP["tiktok_short"])
    occ = get_occupation(occupation_id, locale=locale)

    base_name = f"{occupation_id}_{platform}"
    audio = tts.synthesize_scenes(outline, locale, base_name) if with_audio else None

    # 取几张 Pexels 实拍图，循环分配给需要配图的场景
    photos = images.search_images(occ["name_en"] or occ["name_zh"] or "professional", count=4)
    photo_i = 0

    scenes = []
    for idx, sc in enumerate(outline.get("scenes", [])):
        sid = sc.get("id", "summary")
        dur = audio[idx]["duration_sec"] if audio else float(sc.get("duration_sec", 3))

        # 每个场景分配一张实拍图（title/summary/growth/通用broll 会用到，图表类忽略）
        photo = photos[photo_i % len(photos)] if photos else None
        photo_i += 1

        # 渲染该场景的幻灯片背景图 → remotion/public/slides/
        fname = f"{base_name}_{idx:02d}.png"
        slides.render_scene_image(
            {"id": sid, "name": sc.get("name", ""), "narration": sc.get("narration", "")},
            occ, fmt, config.SLIDES_DIR / fname, photo=photo,
        )

        scenes.append({
            "id": sid,
            "name": sc.get("name", ""),
            "narration": sc.get("narration", ""),
            "durationSec": max(1.5, dur),
            "broll": sc.get("broll_hint", ""),
            "audioSrc": audio[idx]["src"] if audio else None,
            "captions": audio[idx]["captions"] if audio else [],
            "bgImage": f"{config.SLIDES_PUBLIC_PREFIX}/{fname}",
        })

    props = {
        "format": fmt,
        "title": outline.get("title", occ["name_zh"]),
        "occupation": {
            "nameZh": occ["name_zh"],
            "nameEn": occ["name_en"],
            "anzscoCode": occ["anzsco_code"],
            "summary": occ["summary"],
            "salaries": [
                {"label": s["label"], "min": _num(s["min"]), "max": _num(s["max"])}
                for s in occ["salaries"]
            ],
            "ratings": [
                {"labelZh": r["label_zh"], "dimension": r["dimension"], "stars": r["stars"]}
                for r in occ["ratings"]
            ],
            "visaPathways": [
                {"subclass": v["subclass"], "name": v["name"]} for v in occ["visa_pathways"]
            ],
            "growthAreas": occ["growth_areas"],
        },
        "scenes": scenes,
        "theme": THEME,
    }

    spec_path = config.SPECS_DIR / f"{content_id}.json"
    spec_path.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    total = round(sum(s["durationSec"] for s in scenes), 2)
    return {"path": str(spec_path), "comp_id": comp_id, "props": props, "duration_sec": total}
