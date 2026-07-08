# -*- coding: utf-8 -*-
"""从 country-outline.json 一次性导出每国轮廓 SVG（供 job-risk-map 做静态背景图）。

投影与画布须与 riskmap.ts 的 outlineToPath 完全一致（W=1600, H=720, margin=30），
这样 <image> 以同一 viewBox 铺满即可与 treemap 精确对齐。含两条路径：
深色填充（透过分类块缝隙成形）+ 白色描边。生成到 site/public/outlines/{cc}.svg。

运行：python -m scripts.gen_outline_svg
"""
import os, json, math

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "..", "site", "src", "data", "country-outline.json")
OUT_DIR = os.path.join(HERE, "..", "site", "public", "outlines")
W, H, MARGIN = 1600, 720, 30


def outline_to_path(rings):
    """与 riskmap.ts outlineToPath 同款：等距投影 + cos(midLat) 横向校正，等比居中。"""
    all_pts = [p for ring in rings for p in ring]
    if not all_pts:
        return ""
    lons = [p[0] for p in all_pts]
    lats = [p[1] for p in all_pts]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    kx = math.cos((min_lat + max_lat) / 2 * math.pi / 180)
    gw = (max_lon - min_lon) * kx or 1
    gh = (max_lat - min_lat) or 1
    s = min((W - 2 * MARGIN) / gw, (H - 2 * MARGIN) / gh)
    ox = (W - gw * s) / 2
    oy = (H - gh * s) / 2

    def proj(ring):
        pts = [
            f"{ox + (lon - min_lon) * kx * s:.1f} {oy + (max_lat - lat) * s:.1f}"
            for lon, lat in ring
        ]
        return "M" + "L".join(pts) + "Z"

    return "".join(proj(r) for r in rings)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    data = json.load(open(SRC, encoding="utf-8"))
    for cc, rings in data.items():
        d = outline_to_path(rings)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'preserveAspectRatio="xMidYMid meet">'
            f'<path d="{d}" fill="#000" fill-opacity="0.38"/>'
            f'<path d="{d}" fill="none" stroke="#ffffff" stroke-opacity="0.2" '
            f'stroke-width="2" stroke-linejoin="round"/>'
            f'</svg>\n'
        )
        path = os.path.join(OUT_DIR, f"{cc}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"[outline] {cc} -> {path} ({len(rings)} rings, {len(d)} chars)")


if __name__ == "__main__":
    main()
