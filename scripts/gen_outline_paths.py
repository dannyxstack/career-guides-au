# -*- coding: utf-8 -*-
"""生成 job-risk-map 背景水印用的 SVG path 数据（内联，供 CSS 主题控制大陆颜色）。

产出 site/src/data/outline-paths.json = { "AU": "M..Z", ..., "WORLD": "M..Z" }：
  - 各国路径：从 country-outline.json 按「每国 bbox 等距投影 + cos(midLat) 校正、等比居中」
    （与旧 gen_outline_svg.py / riskmap.ts outlineToPath 完全一致，保持国家图观感不变）。
  - WORLD 路径：从 Natural Earth 110m admin_0 GeoJSON 用全球等距柱状（plate carrée）投影，
    剔除南极洲、按面积丢弃极小岛屿、Douglas–Peucker 简化以控体积。

画布/边距须与 riskmap.ts 一致（W=1600, H=720, margin=30），页面 <svg> 用同 viewBox 铺满。
运行：python -m scripts.gen_outline_paths <ne_110m_admin_0_countries.geojson>
"""
import sys, os, json, math

HERE = os.path.dirname(__file__)
CO = os.path.join(HERE, "..", "site", "src", "data", "country-outline.json")
OUT = os.path.join(HERE, "..", "site", "src", "data", "outline-paths.json")
W, H, MARGIN = 1600, 720, 30

# —— 世界地图投影范围（剔除南极；北到格陵兰/西伯利亚，南到火地岛）——
WLON0, WLON1 = -180.0, 180.0
WLAT0, WLAT1 = -56.0, 84.0
WORLD_DP_TOL = 0.35     # 世界轮廓 DP 简化容差（度）
WORLD_MIN_AREA = 0.6    # 丢弃面积（度²）小于此的岛屿，减负


def country_path(rings):
    """每国 bbox 等距投影 + cos(midLat) 横向校正，等比居中。
    bbox 只用「显著环」(面积≥最大环 3%)计算，避免远洋小岛(如西班牙加那利群岛)撑大 bbox
    致主陆块偏小；所有环仍按同一变换绘制（远岛可能越界被 viewBox 裁掉，可接受）。"""
    if not rings:
        return ""
    areas = [ring_area(r) for r in rings]
    amax = max(areas) or 1
    sig = [r for r, a in zip(rings, areas) if a >= amax * 0.03] or rings
    bbox_pts = [p for ring in sig for p in ring]
    lons = [p[0] for p in bbox_pts]; lats = [p[1] for p in bbox_pts]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    kx = math.cos((min_lat + max_lat) / 2 * math.pi / 180)
    gw = (max_lon - min_lon) * kx or 1
    gh = (max_lat - min_lat) or 1
    s = min((W - 2 * MARGIN) / gw, (H - 2 * MARGIN) / gh)
    ox = (W - gw * s) / 2; oy = (H - gh * s) / 2
    def proj(ring):
        pts = [f"{ox + (lon - min_lon) * kx * s:.1f} {oy + (max_lat - lat) * s:.1f}" for lon, lat in ring]
        return "M" + "L".join(pts) + "Z"
    return "".join(proj(r) for r in rings)


def ring_area(r):
    s = 0.0
    for i in range(len(r) - 1):
        s += r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]
    return abs(s) / 2.0


def dp(points, tol):
    """Douglas–Peucker 简化（保端点）。"""
    if len(points) < 3:
        return points[:]
    a, b = points[0], points[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = math.hypot(dx, dy) or 1e-9
    idx, dmax = 0, 0.0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        d = abs((px - a[0]) * dy - (py - a[1]) * dx) / den
        if d > dmax:
            idx, dmax = i, d
    if dmax > tol:
        return dp(points[:idx + 1], tol)[:-1] + dp(points[idx:], tol)
    return [a, b]


def simplify_ring(ring, tol):
    pts = ring[:-1] if ring and ring[0] == ring[-1] else ring[:]
    if len(pts) < 4:
        return ring
    a = 0
    b = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[a][0]) ** 2 + (pts[i][1] - pts[a][1]) ** 2)
    merged = dp(pts[a:b + 1], tol)[:-1] + dp(pts[b:] + pts[:a + 1], tol)[:-1]
    merged.append(merged[0])
    return merged


def polygons_of(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [poly[0] for poly in c]
    return []


def world_path(gj):
    gw, gh = WLON1 - WLON0, WLAT1 - WLAT0
    s = min((W - 2 * MARGIN) / gw, (H - 2 * MARGIN) / gh)
    ox = (W - gw * s) / 2; oy = (H - gh * s) / 2
    def clamp_lat(v): return max(WLAT0, min(WLAT1, v))
    parts = []
    nring = 0
    for f in gj["features"]:
        if f["properties"].get("ADM0_A3") == "ATA":
            continue  # 剔除南极洲
        for ring in polygons_of(f["geometry"]):
            if len(ring) < 4 or ring_area(ring) < WORLD_MIN_AREA:
                continue
            simp = simplify_ring([[float(x), float(y)] for x, y in ring], WORLD_DP_TOL)
            if len(simp) < 4:
                continue
            pts = [f"{ox + (lon - WLON0) * s:.1f} {oy + (WLAT1 - clamp_lat(lat)) * s:.1f}" for lon, lat in simp]
            parts.append("M" + "L".join(pts) + "Z")
            nring += 1
    print(f"[world] {nring} rings kept")
    return "".join(parts)


def main():
    gj_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "world.geojson")
    out = {}
    co = json.load(open(CO, encoding="utf-8"))
    for cc, rings in co.items():
        out[cc] = country_path(rings)
        print(f"[country] {cc}: {len(out[cc])} chars")
    gj = json.load(open(gj_path, encoding="utf-8"))
    out["WORLD"] = world_path(gj)
    print(f"[world] path {len(out['WORLD'])} chars")
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[OK] -> {OUT}  ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
