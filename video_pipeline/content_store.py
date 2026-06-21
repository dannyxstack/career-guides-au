"""platform_contents / video_jobs 的读写助手，集中管理审批状态流转。"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.connection import get_cursor  # noqa: E402

# 审批状态流转：draft → reviewing → approved → published
VALID_STATUS = ("draft", "reviewing", "approved", "published")


def get_content(content_id: int) -> dict | None:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM platform_contents WHERE id=%s", (content_id,))
        row = cur.fetchone()
    if row and row.get("body"):
        try:
            row["outline"] = json.loads(row["body"])
        except json.JSONDecodeError:
            row["outline"] = None
    return row


def get_content_by_key(occupation_id: int, locale: str, platform: str) -> dict | None:
    with get_cursor() as cur:
        cur.execute(
            "SELECT id FROM platform_contents "
            "WHERE occupation_id=%s AND locale=%s AND platform=%s",
            (occupation_id, locale, platform),
        )
        row = cur.fetchone()
    return get_content(row["id"]) if row else None


def update_body(content_id: int, outline: dict) -> None:
    """保存用户在界面上编辑后的大纲。"""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE platform_contents SET body=%s WHERE id=%s",
            (json.dumps(outline, ensure_ascii=False), content_id),
        )


def set_status(content_id: int, status: str) -> None:
    if status not in VALID_STATUS:
        raise ValueError(f"非法状态 {status}")
    with get_cursor() as cur:
        cur.execute("UPDATE platform_contents SET status=%s WHERE id=%s", (status, content_id))


# ---- video_jobs ----

def create_job(content_id: int, tool: str = "remotion", payload: dict | None = None) -> int:
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO video_jobs (content_id, tool, status, input_payload) "
            "VALUES (%s, %s, 'pending', %s)",
            (content_id, tool, json.dumps(payload or {}, ensure_ascii=False)),
        )
        return cur.lastrowid


def update_job(job_id: int, *, status: str, output_url: str | None = None,
               duration_sec: int | None = None, error_msg: str | None = None) -> None:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE video_jobs SET status=%s, output_url=%s, duration_sec=%s, error_msg=%s "
            "WHERE id=%s",
            (status, output_url, duration_sec, error_msg, job_id),
        )


def latest_job(content_id: int) -> dict | None:
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM video_jobs WHERE content_id=%s ORDER BY id DESC LIMIT 1",
            (content_id,),
        )
        return cur.fetchone()


def index_by_occupation() -> dict[int, list[dict]]:
    """返回 {occupation_id: [{id, platform, status}, ...]}，给列表页展示已有内容。"""
    with get_cursor() as cur:
        cur.execute("SELECT id, occupation_id, platform, status FROM platform_contents")
        rows = cur.fetchall()
    out: dict[int, list[dict]] = {}
    for r in rows:
        out.setdefault(r["occupation_id"], []).append(
            {"id": r["id"], "platform": r["platform"], "status": r["status"]}
        )
    return out
