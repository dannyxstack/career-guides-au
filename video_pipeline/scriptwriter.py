"""把职业数据生成分场景大纲，存入 platform_contents（状态 reviewing）。

实际调用的 LLM 后端由 config.LLM_PROVIDER 决定（claude / openai / deepseek），见 llm.py。
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.connection import get_cursor  # noqa: E402
from video_pipeline import config, llm  # noqa: E402
from video_pipeline.data_source import get_occupation  # noqa: E402
from video_pipeline.prompts import (  # noqa: E402
    OUTLINE_SCHEMA, PPT_BRIEF_SCHEMA, PPT_BRIEF_SYSTEM, SYSTEM,
    build_outline_prompt, build_ppt_brief_prompt,
)


def generate_outline(occupation_id: int, platform: str = "tiktok_short",
                     locale: str = "zh-CN") -> dict:
    """生成大纲并写库，返回 {content_id, outline}。"""
    occ = get_occupation(occupation_id, locale=locale)
    prompt = build_outline_prompt(occ, platform)

    outline = llm.complete_json(SYSTEM, prompt, OUTLINE_SCHEMA)
    outline["occupation_id"] = occupation_id

    content_id = _save_content(occupation_id, locale, platform, outline)
    outline_file = _export_outline(content_id, occ, platform, outline)
    return {"content_id": content_id, "outline": outline, "outline_file": str(outline_file)}


def _slug(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "occ").lower())).strip("-")


def _export_outline(content_id: int, occ: dict, platform: str, outline: dict) -> Path:
    """把大纲导出为可读的 Markdown 文案稿，存到 out/outlines/。返回文件路径。"""
    out_dir = config.OUT_DIR / "outlines"
    out_dir.mkdir(parents=True, exist_ok=True)
    name = occ.get("name_en") or str(occ.get("occupation_id") or content_id)
    path = out_dir / f"{content_id}_{_slug(name)}_{platform}.md"

    lines = [
        f"# {outline.get('title') or occ.get('name_zh') or name}",
        "",
        f"- 职业：{occ.get('name_zh') or ''} / {occ.get('name_en') or ''}（occ {occ.get('occupation_id')}）",
        f"- 平台：{platform}　|　content_id：{content_id}",
        f"- 预计时长：{outline.get('est_duration_sec', '—')} 秒　|　模型：{llm.current_model()}",
        "",
        f"**Hook：** {outline.get('hook') or ''}",
        "",
        "---",
        "",
    ]
    for i, sc in enumerate(outline.get("scenes") or [], start=1):
        lines.append(f"## {i}. {sc.get('name') or sc.get('id')}　({sc.get('duration_sec', '—')}s)")
        lines.append("")
        lines.append(sc.get("narration") or "")
        lines.append("")
        if sc.get("broll_hint"):
            lines.append(f"> 画面提示：{sc['broll_hint']}")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def generate_ppt_brief(occupation_id: int, locale: str = "zh-CN") -> dict:
    """用 LLM 生成 PPT 决策文案 brief，存到 platform_contents（platform='ppt'）。返回 brief。"""
    occ = get_occupation(occupation_id, locale=locale)
    prompt = build_ppt_brief_prompt(occ)
    brief = llm.complete_json(PPT_BRIEF_SYSTEM, prompt, PPT_BRIEF_SCHEMA)
    brief["occupation_id"] = occupation_id
    _save_content(occupation_id, locale, "ppt", brief)
    return brief


def _save_content(occupation_id: int, locale: str, platform: str, outline: dict) -> int:
    """Upsert 到 platform_contents，body 存大纲 JSON，状态置 reviewing。"""
    body = json.dumps(outline, ensure_ascii=False)
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO platform_contents
                (occupation_id, locale, platform, status, gen_model, gen_prompt_ver, body)
            VALUES (%s, %s, %s, 'reviewing', %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status='reviewing', gen_model=VALUES(gen_model),
                gen_prompt_ver=VALUES(gen_prompt_ver), body=VALUES(body)
            """,
            (occupation_id, locale, platform, llm.current_model(), config.PROMPT_VERSION, body),
        )
        cur.execute(
            "SELECT id FROM platform_contents "
            "WHERE occupation_id=%s AND locale=%s AND platform=%s",
            (occupation_id, locale, platform),
        )
        return cur.fetchone()["id"]


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("occupation_id", type=int)
    ap.add_argument("--platform", default="tiktok_short")
    args = ap.parse_args()
    result = generate_outline(args.occupation_id, args.platform)
    print(f"content_id={result['content_id']}")
    print(json.dumps(result["outline"], ensure_ascii=False, indent=2))
