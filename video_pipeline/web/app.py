"""FastAPI 本地管理界面：浏览职业 → 生成大纲 → 预览/编辑/审批 → 渲染。

启动： python -m video_pipeline.web.app
然后浏览器打开 http://127.0.0.1:8000
"""

import json
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from video_pipeline import config, content_store, ppt_builder, renderer, scriptwriter
from video_pipeline.data_source import list_occupations

app = FastAPI(title="职业视频流水线")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

PLATFORM_LABELS = {"tiktok_short": "竖屏短视频", "youtube_long": "横屏长视频"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request, category: str | None = None):
    occs = list_occupations()
    if category:
        occs = [o for o in occs if o["category"] == category]
    categories = sorted({o["category"] for o in list_occupations() if o["category"]})
    content_index = content_store.index_by_occupation()
    return templates.TemplateResponse(request, "index.html", {
        "occupations": occs, "categories": categories,
        "current_category": category, "content_index": content_index,
        "platform_labels": PLATFORM_LABELS,
    })


@app.post("/generate")
def generate(occupation_id: int = Form(...), platform: str = Form("tiktok_short")):
    try:
        result = scriptwriter.generate_outline(occupation_id, platform)
        return RedirectResponse(f"/outline/{result['content_id']}", status_code=303)
    except Exception as e:  # noqa: BLE001 — 界面上回显错误
        return RedirectResponse(f"/?err={type(e).__name__}: {e}", status_code=303)


@app.get("/ppt/{occupation_id}")
def generate_ppt(occupation_id: int):
    """生成该职业的 PPTX 并直接返回下载（数据来自 DB，与大纲无关）。"""
    try:
        path = Path(ppt_builder.build_ppt(occupation_id))
    except Exception as e:  # noqa: BLE001 — 界面上回显错误
        return RedirectResponse(f"/?err={type(e).__name__}: {e}", status_code=303)
    return FileResponse(
        str(path), filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


@app.get("/outline/{content_id}", response_class=HTMLResponse)
def outline_view(request: Request, content_id: int):
    content = content_store.get_content(content_id)
    if not content:
        return RedirectResponse("/", status_code=303)
    job = content_store.latest_job(content_id)
    return templates.TemplateResponse(request, "outline.html", {
        "content": content, "outline": content.get("outline"),
        "job": job, "platform_labels": PLATFORM_LABELS,
        "outline_json": json.dumps(content.get("outline"), ensure_ascii=False, indent=2),
    })


@app.post("/outline/{content_id}/save")
def outline_save(content_id: int, body: str = Form(...)):
    try:
        content_store.update_body(content_id, json.loads(body))
    except json.JSONDecodeError:
        return RedirectResponse(f"/outline/{content_id}?err=JSON 格式错误", status_code=303)
    return RedirectResponse(f"/outline/{content_id}", status_code=303)


@app.post("/outline/{content_id}/approve")
def outline_approve(content_id: int):
    content_store.set_status(content_id, "approved")
    return RedirectResponse(f"/outline/{content_id}", status_code=303)


@app.post("/outline/{content_id}/render")
def outline_render(content_id: int):
    try:
        renderer.render_content(content_id, with_audio=True)
    except Exception as e:  # noqa: BLE001
        return RedirectResponse(f"/outline/{content_id}?err={type(e).__name__}: {e}",
                                status_code=303)
    return RedirectResponse(f"/outline/{content_id}", status_code=303)


@app.get("/out/{filename}")
def serve_output(filename: str):
    path = config.OUT_DIR / filename
    if not path.exists():
        return HTMLResponse("not found", status_code=404)
    return FileResponse(str(path))


def main():
    import uvicorn
    uvicorn.run(app, host=config.WEB_HOST, port=config.WEB_PORT)


if __name__ == "__main__":
    main()
