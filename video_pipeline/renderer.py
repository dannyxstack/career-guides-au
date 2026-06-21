"""调 Remotion CLI 渲染视频，并管理 video_jobs 状态。

Python 与 Remotion 的唯一接口：spec.json（inputProps）+ subprocess 调用。
"""

import shutil
import subprocess
import sys
from pathlib import Path

from video_pipeline import config, content_store, spec_builder


def _npx() -> str:
    exe = shutil.which("npx") or shutil.which("npx.cmd")
    if not exe:
        raise RuntimeError("找不到 npx，请先安装 Node.js 并在 video_pipeline/remotion 下 npm install")
    return exe


def render_content(content_id: int, *, with_audio: bool = True) -> dict:
    """渲染一条已审批内容。返回 {job_id, status, output}。"""
    content = content_store.get_content(content_id)
    if not content:
        raise ValueError(f"content {content_id} 不存在")
    if content["status"] != "approved":
        raise RuntimeError(f"content {content_id} 状态为 {content['status']}，需先在界面审批为 approved")
    if not content.get("outline"):
        raise RuntimeError(f"content {content_id} 缺少大纲 body")

    spec = spec_builder.build_spec(
        content_id, content["occupation_id"], content["platform"],
        content["locale"], content["outline"], with_audio=with_audio,
    )

    out_path = config.OUT_DIR / f"{content_id}_{content['platform']}.mp4"
    job_id = content_store.create_job(
        content_id, tool="remotion",
        payload={"comp": spec["comp_id"], "spec": spec["path"]},
    )
    content_store.update_job(job_id, status="processing")

    cmd = [
        _npx(), "remotion", "render", "src/index.ts", spec["comp_id"],
        str(out_path), f"--props={spec['path']}",
    ]
    if config.RENDER_CONCURRENCY:
        cmd.append(f"--concurrency={config.RENDER_CONCURRENCY}")
    try:
        subprocess.run(cmd, cwd=str(config.REMOTION_DIR), check=True,
                       capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        content_store.update_job(job_id, status="failed", error_msg=(e.stderr or "")[:2000])
        return {"job_id": job_id, "status": "failed", "error": e.stderr}

    content_store.update_job(
        job_id, status="done", output_url=str(out_path),
        duration_sec=int(spec["duration_sec"]),
    )
    return {"job_id": job_id, "status": "done", "output": str(out_path)}


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("content_id", type=int)
    ap.add_argument("--no-audio", action="store_true")
    args = ap.parse_args()
    result = render_content(args.content_id, with_audio=not args.no_audio)
    print(result)
    if result["status"] == "failed":
        sys.exit(1)
