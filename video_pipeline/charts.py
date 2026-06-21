"""生成"过去5年 + 未来5年"的薪资/需求趋势图（深色主题，预测段高亮）。

数据说明：DB 只有当前薪资与评分，没有逐年时间序列。这里基于**当前水平 + 行业前景评分**
做**示意性趋势估算**（非官方逐年统计），图上明确标注，仅用于直观呈现增长态势。
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from video_pipeline import config  # noqa: E402

# 中文字体（Windows 自带微软雅黑）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["text.parse_math"] = False  # 让 $ 当普通字符，不解析成数学公式

BG = "#0B1120"
PAST = "#3B5B8C"     # 历史：柔和蓝
FUTURE = "#F59E0B"   # 预测：琥珀高亮
WHITE = "#E6EBF5"
MUTED = "#8B97B0"
GREEN = "#10B981"

CUR_YEAR = 2025


def _rating(occ: dict, dim: str, default: float = 3.0) -> float:
    for r in occ.get("ratings", []):
        if r.get("dimension") == dim and r.get("stars"):
            return float(r["stars"])
    return default


def _salary_anchor(occ: dict) -> float:
    mids = []
    for s in occ.get("salaries", []):
        try:
            lo, hi = float(s["min"]), float(s["max"])
            mids.append((lo + hi) / 2)
        except (TypeError, ValueError):
            continue
    return sum(mids) / len(mids) if mids else 90000.0


def _series(anchor: float, back_rate: float, fwd_rate: float, round_to: int = 1000):
    """以 CUR_YEAR 为锚点，回推过去5年、预测未来5年。返回 (years, values, n_past)。"""
    past_years = list(range(CUR_YEAR - 4, CUR_YEAR + 1))   # 含当前年，共5个历史点
    fwd_years = list(range(CUR_YEAR + 1, CUR_YEAR + 6))    # 未来5个点
    vals = {CUR_YEAR: anchor}
    for y in range(CUR_YEAR - 1, CUR_YEAR - 5, -1):
        vals[y] = vals[y + 1] / (1 + back_rate)
    for y in range(CUR_YEAR + 1, CUR_YEAR + 6):
        vals[y] = vals[y - 1] * (1 + fwd_rate)
    years = past_years + fwd_years
    values = [round(vals[y] / round_to) * round_to for y in years]
    return years, values, len(past_years)


LINE_ALPHA = "#26304A"


def _occ_name(occ: dict) -> str:
    return occ.get("name_zh") or occ.get("name_en") or "该职业"


def draw_trend(ax, years, values, n_past, *, title, ylabel, fmt, kind="bar"):
    """把趋势图画到给定坐标轴上（供独立 png 和幻灯片复用）。"""
    ax.set_facecolor(BG)
    x = list(range(len(years)))
    vmax, vmin = max(values), min(values)

    if kind == "line":
        ax.plot(x[:n_past], values[:n_past], color=PAST, marker="o", lw=3,
                markersize=9, zorder=3)
        ax.plot(x[n_past - 1:], values[n_past - 1:], color=FUTURE, marker="o",
                lw=3.5, markersize=10, zorder=3)
        off = (vmax - vmin) * 0.04 or vmax * 0.02
        for xi, v in zip(x, values):
            ax.text(xi, v + off, fmt(v), ha="center", va="bottom", color=WHITE,
                    fontsize=9, zorder=4)
        ax.set_ylim(vmin * 0.85, vmax * 1.12)
        top = vmax * 1.08
    else:
        colors = [PAST] * n_past + [FUTURE] * (len(years) - n_past)
        bars = ax.bar(x, values, color=colors, width=0.66, zorder=3)
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, v, fmt(v), ha="center", va="bottom",
                    color=WHITE, fontsize=9, zorder=4)
        ax.set_ylim(0, vmax * 1.18)
        top = vmax * 1.02

    ax.axvline(n_past - 0.5, color=MUTED, ls="--", lw=1, alpha=0.6, zorder=2)
    ax.text(n_past - 0.5, top, "  预测 →", color=FUTURE, fontsize=12,
            fontweight="bold", va="bottom")
    ax.text(n_past - 0.55, top, "← 历史估算  ", color=MUTED, fontsize=11,
            va="bottom", ha="right")

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_title(title, color=WHITE, fontsize=16, fontweight="bold", pad=16, loc="left")
    ax.set_ylabel(ylabel, color=MUTED, fontsize=11)
    ax.tick_params(colors=MUTED)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(axis="y", color=LINE_ALPHA, lw=0.6, alpha=0.25, zorder=0)
    ax.margins(x=0.02)


def draw_salary(ax, occ: dict):
    anchor = _salary_anchor(occ)
    fwd_rate = 0.03 + 0.012 * max(0.0, _rating(occ, "future_prospect", 3) - 2)
    years, values, n_past = _series(anchor, back_rate=0.035, fwd_rate=fwd_rate)
    draw_trend(ax, years, values, n_past,
               title=f"{_occ_name(occ)}｜澳大利亚薪资走势：过去5年 vs 未来5年（估算）",
               ylabel="年薪 (AUD)", fmt=lambda v: f"${v/1000:.0f}k", kind="line")


def draw_demand(ax, occ: dict):
    demand = _rating(occ, "job_demand", 3)
    fwd_rate = 0.025 + 0.018 * max(0.0, demand - 2)
    years, values, n_past = _series(100.0, back_rate=0.04, fwd_rate=fwd_rate, round_to=1)
    draw_trend(ax, years, values, n_past,
               title=f"{_occ_name(occ)}｜澳大利亚岗位需求指数：过去5年 vs 未来5年（示意，2025=100）",
               ylabel="需求指数", fmt=lambda v: f"{v:.0f}", kind="bar")


def _png(draw_fn, occ, out_path: Path) -> str:
    fig, ax = plt.subplots(figsize=(11.5, 4.6), dpi=150)
    fig.patch.set_facecolor(BG)
    draw_fn(ax, occ)
    fig.text(0.01, 0.01, "* 基于当前水平与行业前景的示意性趋势估算，非官方逐年统计",
             color=MUTED, fontsize=8)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)


def salary_trend_png(occ: dict, out_path: Path) -> str:
    return _png(draw_salary, occ, out_path)


def demand_trend_png(occ: dict, out_path: Path) -> str:
    return _png(draw_demand, occ, out_path)


# 评分维度极性：+1 越高越好；-1 越高越差（算综合分时反转，避免负向维度拉高总分）
RATING_POLARITY = {
    "income_level": 1, "job_demand": 1, "future_prospect": 1, "pr_friendliness": 1,
    "ai_risk": -1, "learning_difficulty": -1, "learning_duration": -1,
    "certification_difficulty": -1, "competition": -1, "work_intensity": -1,
    "pr_difficulty": -1,
}


def overall_score(occ: dict) -> float | None:
    """按极性把负向维度反转后平均，换算成 0~10 的综合评分。"""
    vals = []
    for r in occ.get("ratings", []):
        if not r.get("stars"):
            continue
        s = float(r["stars"])
        if RATING_POLARITY.get(r["dimension"], 1) < 0:
            s = 6 - s
        vals.append(s)
    if not vals:
        return None
    return round(sum(vals) / len(vals) / 5 * 10, 1)


def draw_radar(ax, occ: dict, labels: dict | None = None, *, label_size: int = 12) -> bool:
    """把各评分维度画成放射（雷达）图到给定 polar 轴（供 png 和幻灯片复用）。
    原始星级 1~5；labels: 维度→中文名。无数据返回 False。"""
    import math

    labels = labels or {}
    rs = [r for r in occ.get("ratings", []) if r.get("stars")]
    if not rs:
        return False
    names = [labels.get(r["dimension"], r["dimension"]) for r in rs]
    vals = [float(r["stars"]) for r in rs]
    n = len(vals)
    angles = [i / n * 2 * math.pi for i in range(n)]
    angles += angles[:1]
    vv = vals + vals[:1]

    ax.set_facecolor(BG)
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.plot(angles, vv, color=GREEN, lw=2.5, zorder=3)
    ax.fill(angles, vv, color=GREEN, alpha=0.25, zorder=2)
    ax.set_ylim(0, 5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(names, color=WHITE, fontsize=label_size)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], color=MUTED, fontsize=8)
    ax.tick_params(colors=MUTED)
    ax.grid(color=LINE_ALPHA, alpha=0.5)
    ax.spines["polar"].set_color(LINE_ALPHA)
    return True


def rating_radar_png(occ: dict, out_path: Path, labels: dict | None = None) -> str:
    """把各评分维度画成放射（雷达）图 PNG，原始星级 1~5。labels: 维度→中文名。"""
    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=150, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG)
    if not draw_radar(ax, occ, labels):
        plt.close(fig)
        return ""
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)


if __name__ == "__main__":
    from video_pipeline.data_source import get_occupation
    occ = get_occupation(int(sys.argv[1]) if len(sys.argv) > 1 else 118)
    d = config.OUT_DIR / "img"
    print(salary_trend_png(occ, d / "test_salary.png"))
    print(demand_trend_png(occ, d / "test_demand.png"))
