"""修复个别国家 workforce 总量明显失真（> 该国总人口 80%）的问题。

根因：
- VN/AR/CL：build_ilostat_official.major_employment 选到膨胀的 source-year（大类就业值虚高
  且分布异常扁平），导致四位 workforce 整体放大数倍。ILOSTAT 权威 OCU_ISCO08_TOTAL（XA 全就业源）
  才是真实总量，但该源无大类分解，故形状无法重取——只能按权威 TOTAL 等比缩放回真实量级。
- SE：SCB 职业就业源跨年份重复计数，总量约 1.7×（分布形状本身合理），按官方就业总量缩放。

修法：对每个受影响国家，factor = 权威就业总量 / 当前总量，逐职业 workforce_size ×factor。
幂等：修好后当前总量≈目标，再次运行 factor≈1 不再变动。
同步补丁 site/src/data/occupations_v2.json（treemap 数据源），避免必须跑整套 export。

运行：PYTHONIOENCODING=utf-8 python scripts/fix_workforce_totals.py [--dry]
"""
import sys, os, json, argparse
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

# 权威就业总量（人）。来源见文件头/下方注释。
TARGET = {
    "VN": (56_173_066, "ILOSTAT OCU_ISCO08_TOTAL XA:2184 2025"),
    "AR": (20_819_930, "ILOSTAT OCU_ISCO08_TOTAL XA:1868 2025"),
    "CL": (9_414_853,  "ILOSTAT OCU_ISCO08_TOTAL XA:1943 2025"),
    "SE": (5_200_000,  "SCB AKU 2023 employed 15-74 ~5.2M"),
}
JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "site", "src", "data", "occupations_v2.json")


def main(dry):
    with get_cursor() as cur:
        cur.execute("SELECT country_code, id, workforce_size FROM occupations WHERE country_code IN (%s)"
                    % ",".join(["%s"] * len(TARGET)), list(TARGET))
        rows = cur.fetchall()
    cur_tot = defaultdict(int)
    for r in rows:
        cur_tot[r["country_code"]] += r["workforce_size"] or 0

    factor = {}
    print("=== workforce 缩放计划 ===")
    for cc, (tgt, src) in TARGET.items():
        ct = cur_tot[cc]
        f = tgt / ct if ct else 1.0
        factor[cc] = f
        print(f"  {cc}: 当前 {ct:,} -> 目标 {tgt:,}  (×{f:.4f})  [{src}]")

    if dry:
        return

    # 1) 更新 DB
    updates = []
    for r in rows:
        w = r["workforce_size"]
        if w is None:
            continue
        updates.append((int(round(w * factor[r["country_code"]])), r["id"]))
    with get_cursor() as cur:
        cur.executemany("UPDATE occupations SET workforce_size=%s WHERE id=%s", updates)
    print(f"DB 已更新 {len(updates)} 条")

    # 2) 同步补丁 treemap 数据源 JSON
    if os.path.exists(JSON_PATH):
        data = json.load(open(JSON_PATH, encoding="utf-8"))
        n = 0
        for o in data["occupations"]:
            cc = o.get("country")
            if cc in factor and o.get("workforce_size") is not None:
                o["workforce_size"] = int(round(o["workforce_size"] * factor[cc]))
                n += 1
        json.dump(data, open(JSON_PATH, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"occupations_v2.json 已补丁 {n} 条")
    else:
        print("警告：未找到 occupations_v2.json，跳过补丁（下次 export 会从 DB 生成正确值）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    main(a.dry)
