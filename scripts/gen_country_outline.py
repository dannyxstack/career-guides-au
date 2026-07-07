# -*- coding: utf-8 -*-
"""生成 job-risk-map 背景水印用的国家轮廓（多环，含周边岛屿）。

源：Natural Earth 50m admin_0 countries GeoJSON（按 ADM0_A3 匹配，避开法国 ISO_A2=-99 坑）。
每国取「全部多边形外环」（含塔斯马尼亚/新西兰南北岛/英国各岛/西班牙加那利等周边岛屿），
但剔除距主陆块中心 >MAX_DEG 的远洋海外领地（法属圭亚那/留尼汪/夏威夷/阿拉斯加等，
否则水印会横跨整个大洋、主陆块被压得极小）。每环做 Douglas–Peucker 简化以控制体积。

输出 site/src/data/country-outline.json：{国家码: [ [[lon,lat],...], ... ]}（环数组）。
运行：python -m scripts.gen_country_outline <ne_50m_admin_0_countries.geojson>
"""
import sys, os, json, math

# ADM0_A3 -> 站点国家码
A3 = {"AUS": "AU", "NZL": "NZ", "CAN": "CA", "USA": "US",
      "GBR": "UK", "DEU": "DE", "FRA": "FR", "ESP": "ES"}
MAX_DEG = 30.0      # 多边形中心距主陆块中心超过此度数则视为远洋领地，剔除
DP_TOL = 0.05       # Douglas–Peucker 简化容差（度）
OUT = os.path.join(os.path.dirname(__file__), "..", "site", "src", "data", "country-outline.json")


def ring_area(r):
    """有向面积（度²），用于取最大多边形与丢弃退化环。"""
    s = 0.0
    for i in range(len(r) - 1):
        s += r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]
    return abs(s) / 2.0


def centroid(r):
    xs = [p[0] for p in r]; ys = [p[1] for p in r]
    return sum(xs) / len(xs), sum(ys) / len(ys)


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
        left = dp(points[:idx + 1], tol)
        right = dp(points[idx:], tol)
        return left[:-1] + right
    return [a, b]


def simplify_ring(ring, tol):
    """闭合环简化：在「距起点最远点」处拆成两段弧分别 DP，避免首尾同点导致 DP 坍缩。"""
    pts = ring[:-1] if ring[0] == ring[-1] else ring[:]
    if len(pts) < 4:
        return ring
    a = 0
    b = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[a][0]) ** 2 + (pts[i][1] - pts[a][1]) ** 2)
    arc1 = pts[a:b + 1]
    arc2 = pts[b:] + pts[:a + 1]
    merged = dp(arc1, tol)[:-1] + dp(arc2, tol)[:-1]
    merged.append(merged[0])
    return merged


def polygons_of(geom):
    """返回该 feature 所有多边形的外环列表（忽略内环/孔洞）。"""
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [poly[0] for poly in c]
    return []


def build(src_path):
    gj = json.load(open(src_path, encoding="utf-8"))
    feat = {f["properties"].get("ADM0_A3"): f for f in gj["features"]}
    out = {}
    for a3, cc in A3.items():
        rings = polygons_of(feat[a3]["geometry"])
        rings = [r for r in rings if len(r) >= 4]
        # 主陆块 = 面积最大的环，其中心作为距离基准
        main = max(rings, key=ring_area)
        cx, cy = centroid(main)
        kept = []
        for r in rings:
            gx, gy = centroid(r)
            if math.hypot(gx - cx, gy - cy) > MAX_DEG:
                continue  # 远洋海外领地，剔除
            simp = [[round(x, 3), round(y, 3)] for x, y in simplify_ring(r, DP_TOL)]
            if len(simp) >= 4:
                kept.append(simp)
        kept.sort(key=ring_area, reverse=True)
        out[cc] = kept
        pts = sum(len(r) for r in kept)
        print(f"{cc} ({a3}): {len(kept)} 环, {pts} 点")
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[OK] -> {OUT}  ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    build(sys.argv[1])
