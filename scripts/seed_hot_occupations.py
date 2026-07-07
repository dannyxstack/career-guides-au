# -*- coding: utf-8 -*-
"""热门职业启发式预填充（临时热度）。

从 site/src/data/occupations.json 读取（slug 与前端/导出保持一致），
按 workforce_size 0.5 / AI 自动化暴露 0.3 / 短缺清单 0.2 打分，
写入 occ_search_hits.seed_score（幂等：仅覆盖 seed_score，不动 hits）。

真实搜索量入库后，热度 = hits + seed_score 自然从种子过渡到真实数据。

运行：PYTHONIOENCODING=utf-8 python -m scripts.seed_hot_occupations
"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

OCC_JSON = os.path.join(os.path.dirname(__file__), "..", "site", "src", "data", "occupations.json")

W_WORKFORCE = 0.5
W_AI = 0.3
W_SHORTAGE = 0.2


def run():
    with open(OCC_JSON, encoding="utf-8") as f:
        occ = json.load(f)["occupations"]

    # workforce 对数归一化（体量差异悬殊，用 log 压缩）
    wfs = [o["workforce_size"] for o in occ if o.get("workforce_size")]
    lo, hi = math.log(min(wfs)), math.log(max(wfs))
    span = (hi - lo) or 1.0

    rows = []
    for o in occ:
        wf = o.get("workforce_size")
        wf_norm = (math.log(wf) - lo) / span if wf else 0.0
        ai = o.get("ai") or {}
        exp = ai.get("automation_exposure")
        ai_norm = (exp / 10.0) if exp is not None else 0.0
        shortage = 1.0 if o.get("shortage_listed") else 0.0
        score01 = W_WORKFORCE * wf_norm + W_AI * ai_norm + W_SHORTAGE * shortage
        rows.append((o["country"], o["slug"], int(round(score01 * 1000))))

    with get_cursor() as cur:
        cur.executemany(
            "INSERT INTO occ_search_hits (country_code, slug, seed_score) VALUES (%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE seed_score=VALUES(seed_score)",
            rows)
    print(f"[OK] occ_search_hits 预填充 {len(rows)} 行 seed_score（未触碰 hits）")


if __name__ == "__main__":
    run()
