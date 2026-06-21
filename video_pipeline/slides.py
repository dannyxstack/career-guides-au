"""为每个视频场景渲染一张全画幅"幻灯片"PNG（深色主题），供 Remotion 当背景。

视频画面 = 幻灯片图 + 字幕 + 配音（方案C：PPT 与视频合二为一）。
复用 charts.py 的趋势图、images.py 的 Pexels 实拍图。
"""

import re
import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from video_pipeline import charts  # noqa: E402（顺带设好中文字体 + 颜色常量）

BG, PAST, FUTURE = charts.BG, charts.PAST, charts.FUTURE
WHITE, MUTED, GREEN = charts.WHITE, charts.MUTED, charts.GREEN
RED = "#EF6B6B"

DIM_ZH = {
    "learning_difficulty": "学习难度", "learning_duration": "学习时长",
    "certification_difficulty": "认证难度", "job_demand": "岗位需求",
    "competition": "竞争程度", "work_intensity": "工作强度",
    "income_level": "收入水平", "future_prospect": "未来前景",
    "ai_risk": "AI替代风险", "pr_friendliness": "移民友好度",
    "pr_difficulty": "移民难度",
}


def _wrap(s: str, n: int) -> str:
    """含空格（英文）按单词换行，避免词被从中间切断；无空格（中文）按字符切。"""
    s = s or ""
    out = []
    for para in s.split("\n"):
        if " " in para.strip():
            out.extend(textwrap.wrap(para, width=n) or [""])
        elif para:
            out.extend(para[i:i + n] for i in range(0, len(para), n))
        else:
            out.append("")
    return "\n".join(out)


def _stars(n) -> str:
    n = int(round(n or 0))
    return "★" * n + "☆" * (5 - n)


def _rating(occ: dict, dim: str, default: float = 3) -> float:
    for r in occ.get("ratings", []):
        if r.get("dimension") == dim and r.get("stars"):
            return r["stars"]
    return default


def _new_fig(fmt: str):
    vert = fmt.startswith("short")
    figsize = (7.2, 12.8) if vert else (12.8, 7.2)  # 1080x1920 / 1920x1080 @150dpi
    fig = plt.figure(figsize=figsize, dpi=150)
    fig.patch.set_facecolor(BG)
    return fig, vert


def _title_bar(fig, text, y=0.9, size=30):
    """左侧绿色竖条 + 标题文字（figure 坐标）。"""
    fig.add_artist(Rectangle((0.05, y - 0.035), 0.009, 0.05, color=GREEN,
                             transform=fig.transFigure))
    fig.text(0.075, y, text, fontsize=size, color=WHITE, fontweight="bold", va="center")


def _photo_axes(fig, photo, rect):
    if not photo or not Path(photo).exists():
        return
    try:
        img = mpimg.imread(photo)
    except Exception:  # noqa: BLE001
        return
    ax = fig.add_axes(rect)
    ax.imshow(img, aspect="auto")
    ax.axis("off")


def _save(fig, out_path: Path) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), facecolor=BG)
    plt.close(fig)
    return str(out_path)


# ---------- 各场景 ----------

def _s_title(fig, vert, occ, scene, photo):
    if vert:
        _photo_axes(fig, photo, [0.0, 0.55, 1.0, 0.45])
        ty = 0.4
    else:
        _photo_axes(fig, photo, [0.52, 0.0, 0.48, 1.0])
        ty = 0.6
    fig.text(0.07, ty, occ["name_zh"] or "", fontsize=56, color=WHITE, fontweight="bold")
    fig.text(0.07, ty - 0.08, occ["name_en"] or "", fontsize=26, color=MUTED)
    fig.text(0.07, ty - 0.14, f"ANZSCO {occ['anzsco_code']}", fontsize=20,
             color=GREEN, fontweight="bold")


def _s_summary(fig, vert, occ, scene, photo):
    """速览卡：一句话定义 + 关键数据 + 配图（不再铺整段简介）。"""
    _title_bar(fig, "职业概览")
    defline = re.split(r"(?<=。)", occ["summary"] or "")[0]
    maxsal = max([float(s["max"]) for s in occ["salaries"] if s.get("max")] or [0])
    facts = [
        ("类别", occ["category"] or "—", MUTED),
        ("是否紧缺", "紧缺职业" if occ["shortage_listed"] else "一般",
         GREEN if occ["shortage_listed"] else MUTED),
        ("最高年薪", f"${maxsal/1000:.0f}k / 年", FUTURE),
        ("岗位需求", _stars(_rating(occ, "job_demand")), FUTURE),
        ("移民友好", _stars(_rating(occ, "pr_friendliness")), GREEN),
    ]
    if vert:
        fig.text(0.07, 0.8, _wrap(defline, 14), fontsize=24, color=WHITE,
                 va="top", linespacing=1.5)
        y, lx, vx, step = 0.52, 0.07, 0.42, 0.07
        _photo_axes(fig, photo, [0.07, 0.06, 0.86, 0.16])
    else:
        fig.text(0.07, 0.75, _wrap(defline, 20), fontsize=23, color=WHITE,
                 va="top", linespacing=1.5)
        y, lx, vx, step = 0.5, 0.07, 0.22, 0.085
        _photo_axes(fig, photo, [0.56, 0.18, 0.38, 0.5])
    for label, val, color in facts:
        fig.text(lx, y, label, fontsize=18, color=MUTED)
        fig.text(vx, y, str(val), fontsize=20, color=color, fontweight="bold")
        y -= step


def _s_salary(fig, vert, occ, scene, photo):
    rect = [0.08, 0.18, 0.86, 0.6] if vert else [0.07, 0.12, 0.86, 0.72]
    ax = fig.add_axes(rect)
    charts.draw_salary(ax, occ)
    fig.text(0.07, 0.02, "* 示意性趋势估算，非官方逐年统计", color=MUTED, fontsize=9)


def _s_demand(fig, vert, occ, scene, photo):
    rect = [0.08, 0.18, 0.86, 0.6] if vert else [0.07, 0.12, 0.86, 0.72]
    ax = fig.add_axes(rect)
    charts.draw_demand(ax, occ)
    fig.text(0.07, 0.02, "* 示意性趋势估算，非官方逐年统计", color=MUTED, fontsize=9)


def _s_ratings(fig, vert, occ, scene, photo):
    """与 PPT 评分页一致：全部维度放射（雷达）图 + 标题综合评分。"""
    score = charts.overall_score(occ)
    _title_bar(fig, "职业评分" + (f" · 综合 {score}/10" if score is not None else ""))
    rect = [0.12, 0.18, 0.76, 0.6] if vert else [0.27, 0.1, 0.46, 0.72]
    ax = fig.add_axes(rect, polar=True)
    if not charts.draw_radar(ax, occ, DIM_ZH, label_size=15 if vert else 13):
        ax.remove()
        fig.text(0.07, 0.7, "（暂无评分数据）", fontsize=20, color=MUTED)


def _s_visa(fig, vert, occ, scene, photo):
    _title_bar(fig, "签证 / 移民路径")
    lines = []
    for v in occ["visa_pathways"]:
        lines.append(f"● {v['subclass']}  {v['name'] or ''}")
        if v.get("desc"):
            lines.append(f"    {v['desc']}")
    fig.text(0.07, 0.78, "\n".join(lines) or "（暂无签证数据）", fontsize=22,
             color=WHITE, va="top", linespacing=1.7)


def _s_growth(fig, vert, occ, scene, photo):
    _title_bar(fig, "增长领域")
    bullets = "\n".join(f"•  {g}" for g in occ["growth_areas"]) or "（暂无数据）"
    fig.text(0.07, 0.78, bullets, fontsize=24, color=WHITE, va="top", linespacing=1.9)
    if vert:
        _photo_axes(fig, photo, [0.07, 0.08, 0.86, 0.3])
    else:
        _photo_axes(fig, photo, [0.58, 0.2, 0.36, 0.45])


def _s_suitability(fig, vert, occ, scene, photo):
    """适合 / 不适合 双栏（数据驱动）。横屏左右两栏，竖屏上下两块。"""
    _title_bar(fig, "谁适合 / 谁不适合")
    fit = occ.get("suitability_fit") or []
    unfit = occ.get("suitability_unfit") or []

    def _col(x, y0, header, color, items, wrapn):
        fig.text(x, y0, header, fontsize=24, color=color, fontweight="bold")
        y = y0 - 0.08
        for it in items[:4]:
            fig.text(x, y, "• " + _wrap(it, wrapn), fontsize=19, color=WHITE,
                     va="top", linespacing=1.35)
            y -= 0.13

    if vert:
        _col(0.07, 0.8, "适合", GREEN, fit, 16)
        _col(0.07, 0.42, "不太适合", RED, unfit, 16)
    else:
        _col(0.07, 0.78, "适合", GREEN, fit, 16)
        _col(0.54, 0.78, "不太适合", RED, unfit, 16)


def _fmt_cost(e):
    try:
        lo, hi = float(e.get("cost_min") or 0), float(e.get("cost_max") or 0)
    except (TypeError, ValueError):
        lo = hi = 0
    if hi > 0:
        return f"${int(lo):,}~${int(hi):,}"
    return e.get("cost_note") or ""


def _s_education(fig, vert, occ, scene, photo):
    _title_bar(fig, "教育路径")
    edu = (occ.get("education") or [])[:3]
    if not edu:
        fig.text(0.07, 0.7, "（暂无教育路径数据）", fontsize=20, color=MUTED)
        return
    y = 0.78
    wrapn = 16 if vert else 32
    for i, e in enumerate(edu, start=1):
        stage = _wrap(f"{i}. {e['stage']}", wrapn)
        fig.text(0.07, y, stage, fontsize=18, color=WHITE, fontweight="bold",
                 va="top", linespacing=1.2)
        nlines = stage.count("\n") + 1
        meta = "   ·   ".join([x for x in [str(e.get("duration") or ""), _fmt_cost(e)] if x])
        fig.text(0.1, y - 0.05 * nlines, meta, fontsize=15, color=FUTURE, va="top")
        y -= 0.05 * nlines + 0.11


def _s_qualifications(fig, vert, occ, scene, photo):
    _title_bar(fig, "从业资质 / 证书")
    quals = (occ.get("qualifications") or [])[:5]
    if not quals:
        fig.text(0.07, 0.7, "（暂无资质数据）", fontsize=20, color=MUTED)
        return
    y = 0.78
    wrapn = 14 if vert else 26
    tag_x = 0.92 if vert else 0.9
    for q in quals:
        name = _wrap(q["name"], wrapn)
        fig.text(0.07, y, "• " + name, fontsize=18, color=WHITE, fontweight="bold",
                 va="top", linespacing=1.2)
        fig.text(tag_x, y, "必备" if q["mandatory"] else "可选", fontsize=15,
                 color=GREEN if q["mandatory"] else MUTED, va="top", ha="right")
        nlines = name.count("\n") + 1
        y -= 0.05 * nlines + 0.06


def _s_generic(fig, vert, occ, scene, photo):
    """通用纯文字场景：实拍图压暗作背景 + 顶部小标题，正文交给配音/字幕。"""
    if photo and Path(photo).exists():
        try:
            ax = fig.add_axes([0, 0, 1, 1])
            ax.imshow(mpimg.imread(photo), aspect="auto")
            ax.axis("off")
            fig.add_artist(Rectangle((0, 0), 1, 1, transform=fig.transFigure,
                                     color=BG, alpha=0.62))
        except Exception:  # noqa: BLE001
            pass
    _title_bar(fig, scene.get("name") or "")


def _s_cta(fig, vert, occ, scene, photo):
    fig.text(0.5, 0.6, "想了解更多澳洲紧缺职业？", fontsize=40, color=WHITE,
             ha="center", va="center", fontweight="bold")
    fig.text(0.5, 0.46, "关注我们，每天一个职业深度解析", fontsize=26, color=GREEN,
             ha="center", va="center")


_DISPATCH = {
    "title": _s_title, "summary": _s_summary, "salary": _s_salary,
    "income": _s_salary, "demand": _s_demand, "ratings": _s_ratings,
    "education": _s_education, "qualifications": _s_qualifications,
    "visa": _s_visa, "growth": _s_growth, "suitability": _s_suitability,
    "cta": _s_cta,
}


def render_scene_image(scene: dict, occ: dict, fmt: str, out_path: Path,
                       photo: str | None = None) -> str:
    fig, vert = _new_fig(fmt)
    fn = _DISPATCH.get(scene.get("id"), _s_generic)
    fn(fig, vert, occ, scene, photo)
    return _save(fig, out_path)


if __name__ == "__main__":
    from video_pipeline.data_source import get_occupation
    from video_pipeline import config, images

    oid = int(sys.argv[1]) if len(sys.argv) > 1 else 118
    fmt = sys.argv[2] if len(sys.argv) > 2 else "long-16x9"
    occ = get_occupation(oid)
    photos = images.search_images(occ["name_en"] or "worker", count=2)
    d = config.OUT_DIR / "slides_test"
    for sc in [{"id": "title"}, {"id": "salary"}, {"id": "ratings"},
               {"id": "growth"}, {"id": "visa"}]:
        p = photos[0] if photos else None
        out = render_scene_image(sc, occ, fmt, d / f"{sc['id']}.png", photo=p)
        print(out)
