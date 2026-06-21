"""按关键词从 Pexels 搜索并下载职业相关图片。无 key 时返回空列表。"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from video_pipeline import config  # noqa: E402

PEXELS_SEARCH = "https://api.pexels.com/v1/search"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "img").lower()).strip("-") or "img"


def search_images(query: str, count: int = 3, out_dir: Path | None = None) -> list[str]:
    """搜索并下载 count 张图片，返回本地文件路径列表。失败/无 key 时返回 []。"""
    if not config.PEXELS_API_KEY:
        return []
    import requests

    out_dir = Path(out_dir or (config.OUT_DIR / "img"))
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(
            PEXELS_SEARCH,
            headers={"Authorization": config.PEXELS_API_KEY},
            params={"query": query, "per_page": count, "orientation": "landscape"},
            timeout=20,
        )
        resp.raise_for_status()
        photos = resp.json().get("photos", [])
    except Exception as e:  # noqa: BLE001 — 图片是锦上添花，失败不应中断
        print(f"[images] 搜索失败 query={query!r}: {e}")
        return []

    paths = []
    for i, p in enumerate(photos):
        src = p.get("src", {})
        url = src.get("large") or src.get("medium") or src.get("original")
        if not url:
            continue
        try:
            img = requests.get(url, timeout=30)
            img.raise_for_status()
        except Exception:  # noqa: BLE001
            continue
        fp = out_dir / f"{_slug(query)}_{i}.jpg"
        fp.write_bytes(img.content)
        paths.append(str(fp))
    return paths
