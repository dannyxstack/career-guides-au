"""NL 官方薪资层：CBS 表 85517NED（时薪×职业，BRC 2014）→ 覆盖 median 汇总薪资档。

数据源：`.codex_tmp/cbs_brc_2024.json`（由 CBS OData 拉取，114 个 BRC 4 位组，
含员工数×1000 与时薪 P25/P50(中位)/P75；其中 74 组有中位数，其余样本过小被压制）。

流程：
  1. DeepSeek 把本国 436 个 ISCO-08 职业映射到最接近的 BRC 组（分批，结果缓存 official_NL_xwalk.json）。
  2. BRC 中位时薪 × 1976（38h/周×52，荷兰全职工时）→ 税前年薪；P25/P75 同法给区间，写 salary_note。
  3. 覆盖 occupation_salaries 的 band='median' 行（salary_note 标官方来源，不再含"估算"），
     仅对映射到「有中位数」BRC 组的职业生效；其余保留估算基线（见 fill_isco_salary_bands）。
  mean 档 CBS 无对应，保持估算不动。

运行：$env:LLM_PROVIDER="deepseek"; python -m scripts.fetch_official_nl [--redo-xwalk] [--dry]
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import llm

TMP = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp")
BRC = os.path.join(TMP, "cbs_brc_2024.json")
XWALK = os.path.join(TMP, "official_NL_xwalk.json")
OFFICIAL = os.path.join(TMP, "official_NL.json")
HOURS_YEAR = 1976  # 38h/周 × 52，荷兰全职工时口径
PERIOD = "CBS 2024"


def build_system(brc):
    lines = "\n".join(f"{code} | {v['title_nl']}" for code, v in sorted(brc.items()))
    return ("你是荷兰劳动力市场分类专家，熟悉 ISCO-08 职业分类与荷兰 BRC 2014 职业分组的对应。"
            "给定若干 ISCO-08 职业（4 位码 + 英文名），把每个映射到下面最接近的一个 BRC 2014 职业组（4 位码）。"
            "只能从下列清单选，选不到合适的填 \"\"。只输出 JSON 对象 {isco码: brc码}，不要多余文字。\n"
            f"BRC 2014 组清单（码 | 荷兰语名）：\n{lines}")


def crosswalk(occs, brc, redo):
    if os.path.exists(XWALK) and not redo:
        return json.load(open(XWALK, encoding="utf-8"))
    system = build_system(brc)
    valid = set(brc.keys())
    out = {}
    B = 40
    for i in range(0, len(occs), B):
        batch = occs[i:i + B]
        prompt = ("把这些 ISCO-08 职业各映射到一个 BRC 码：\n"
                  + "\n".join(f"{o['occ_code']} | {o['name_en']}" for o in batch)
                  + "\n只输出 {isco码: brc码}。")
        try:
            raw = llm.complete_json(system, prompt, {"type": "object"})
            for k, v in (raw or {}).items():
                v = str(v).strip()
                if v in valid:
                    out[str(k).strip()] = v
        except Exception as e:
            print(f"  批 {i//B+1} 失败: {e}", flush=True)
        print(f"  crosswalk {min(i+B,len(occs))}/{len(occs)} 累计命中 {len(out)}", flush=True)
    json.dump(out, open(XWALK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--redo-xwalk", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    brc = json.load(open(BRC, encoding="utf-8"))
    with get_cursor() as cur:
        cur.execute("SELECT id, occ_code, anzsco_title AS name_en FROM occupations WHERE country_code='NL'")
        occs = cur.fetchall()
    print(f"[NL] 职业 {len(occs)}，BRC 组 {len(brc)}（有中位数 {sum(1 for v in brc.values() if v['p50'])}）"
          f" model={llm.current_model()}", flush=True)

    xw = crosswalk(occs, brc, a.redo_xwalk)
    print(f"[NL] crosswalk 命中 {len(xw)}/{len(occs)}", flush=True)

    official, rows = {}, []
    for o in occs:
        code = o["occ_code"]
        bc = xw.get(code)
        v = brc.get(bc) if bc else None
        if not v or not v.get("p50"):
            continue
        med = int(round(v["p50"] * HOURS_YEAR))
        lo = int(round(v["p25"] * HOURS_YEAR)) if v.get("p25") else med
        hi = int(round(v["p75"] * HOURS_YEAR)) if v.get("p75") else med
        note = (f"薪资中位数（官方：CBS 员工时薪中位 €{v['p50']}/小时 × {HOURS_YEAR}h 年化，"
                f"BRC 组 {bc} {v['title_nl']}；P25–P75 €{lo:,}–€{hi:,}，{PERIOD}）")
        official[code] = {"brc": bc, "median": med, "p25": lo, "p75": hi, "employees_k": v.get("employees_k")}
        rows.append((o["id"], med, lo, hi, note))
    print(f"[NL] 官方 median 可覆盖 {len(rows)} 个职业（映射到有中位数 BRC 组者）", flush=True)
    json.dump(official, open(OFFICIAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if a.dry:
        print("[dry] 样本:", [(r[0], r[1]) for r in rows[:5]])
        return
    # 覆盖 median 档：删旧 median 行（含估算），写官方 median 点值（min=max=中位；P25–P75 见 note）
    with get_cursor() as cur:
        for oid, med, lo, hi, note in rows:
            cur.execute("DELETE FROM occupation_salaries WHERE occupation_id=%s AND salary_band='median'", (oid,))
            cur.execute("INSERT INTO occupation_salaries "
                        "(occupation_id,currency,experience,salary_min,salary_max,salary_note,sort_order,salary_band) "
                        "VALUES (%s,'EUR','薪资中位数',%s,%s,%s,-1,'median')", (oid, med, med, note))
    print(f"[NL] 已写官方 median {len(rows)} 行（覆盖估算基线）", flush=True)


if __name__ == "__main__":
    main()
