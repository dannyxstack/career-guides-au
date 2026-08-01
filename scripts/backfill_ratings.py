"""零 LLM 补齐职业评分（幂等）。

四步（详见会话交接 2026-07-31）：
1. pr 维全局合并：
   - full 档国（AU NZ CA US UK DE IE）：pr_friendliness = clamp(0.75×友好度 + 0.25×(10−难度), 1, 10)，
     就地更新；删除 pr_difficulty。仅 full 档保留并展示"移民友好度"。
   - info/none 档：不记录移民相关维 → 删除该国全部 pr_friendliness / pr_difficulty。
   - 结果：pr_difficulty 全站清除；pr_friendliness 仅存于 full 档。
2. ai_risk：缺则用 aioe_pct/10（clamp 1-10）公式补，label 按暴露分档。
3. 7 个内在主观维（learning_difficulty, learning_duration, certification_difficulty,
   job_demand, competition, work_intensity, future_prospect）：ISCO08 缺则按 occ_code
   从"捐赠"职业复制 label+stars（436 码全有捐赠源）。
4. income_level：有官方薪资的按该国国内薪资分位映射 1-10 补；无薪资留空（不虚构）。

只补缺失，不改已有值（pr 合并除外）。--dry 只统计不写。
运行：PYTHONIOENCODING=utf-8 python scripts/backfill_ratings.py [--dry]
"""
import sys, os, argparse
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

# 移民档位（对齐 aijobrisk-go/internal/data/migration.go migrationTier）
FULL = {"AU", "NZ", "CA", "US", "UK", "DE", "IE"}
INFO = {"FR", "ES", "IT", "NL", "BE", "AT", "PL", "PT", "GR", "HU", "CZ", "RO", "LU", "SK",
        "SI", "HR", "DK", "FI", "SE", "NO", "IS", "CH", "SG", "JP", "KR", "EE", "LV", "LT"}


def tier(cc):
    return "full" if cc in FULL else ("info" if cc in INFO else "none")


INTRINSIC = ["learning_difficulty", "learning_duration", "certification_difficulty",
             "job_demand", "competition", "work_intensity", "future_prospect"]
# 捐赠国优先级（评分成熟度高→低），用于按 occ_code 选复制源
DONOR_PRIORITY = ["AU", "US", "UK", "DE", "CA", "NZ", "IE", "FR", "ES", "IT", "NL"]


def clamp(x, lo=1.0, hi=10.0):
    return max(lo, min(hi, round(float(x), 1)))


def airisk_label(s):
    return "High exposure" if s >= 7 else "Moderate exposure" if s >= 4 else "Low exposure"


def income_label(s):
    return "Very high" if s >= 8 else "High" if s >= 6 else "Moderate" if s >= 4.5 else "Modest"


def rep_salary(bands):
    """代表薪资：优先含 median 的档，否则各档中点均值。"""
    med = [b for b in bands if "median" in (b["experience"] or "").lower()]
    src = med or bands
    vals = []
    for b in src:
        lo, hi = b["salary_min"], b["salary_max"]
        if lo is None and hi is None:
            continue
        lo = float(lo) if lo is not None else float(hi)
        hi = float(hi) if hi is not None else float(lo)
        vals.append((lo + hi) / 2.0)
    return sum(vals) / len(vals) if vals else None


def main(dry):
    with get_cursor() as cur:
        cur.execute("SELECT id, country_code, occ_code, occ_code_type FROM occupations")
        occs = cur.fetchall()
        occ_cc = {o["id"]: o["country_code"] for o in occs}

        cur.execute("SELECT occupation_id, dimension, label, stars FROM occupation_ratings_v2")
        rat = defaultdict(dict)
        for r in cur.fetchall():
            rat[r["occupation_id"]][r["dimension"]] = (r["label"], float(r["stars"]))

        cur.execute("SELECT occupation_id, aioe_pct FROM occupation_ai_v2 WHERE aioe_pct IS NOT NULL")
        aioe = {r["occupation_id"]: float(r["aioe_pct"]) for r in cur.fetchall()}

        cur.execute("SELECT occupation_id, experience, salary_min, salary_max FROM occupation_salaries_v2")
        sal_bands = defaultdict(list)
        for r in cur.fetchall():
            sal_bands[r["occupation_id"]].append(r)

    # ---- 1. pr 合并 ----
    pr_update = []          # (stars, occ_id) 更新 full 档 pr_friendliness
    del_prdiff_ids = []     # 删 pr_difficulty 的 occ（全部有该维者）
    del_prfriend_ids = []   # 删 pr_friendliness 的 occ（仅 info/none）
    full_missing = 0
    for o in occs:
        oid, cc = o["id"], o["country_code"]
        dims = rat[oid]
        has_f, has_d = "pr_friendliness" in dims, "pr_difficulty" in dims
        if tier(cc) == "full":
            if has_f and has_d:
                f, d = dims["pr_friendliness"][1], dims["pr_difficulty"][1]
                pr_update.append((clamp(0.75 * f + 0.25 * (10.0 - d)), oid))
            elif has_f or has_d:
                full_missing += 1  # 只有单维，缺数据→报告（保留现状，不猜）
            if has_d:
                del_prdiff_ids.append(oid)
        else:  # info / none：不记录移民维
            if has_d:
                del_prdiff_ids.append(oid)
            if has_f:
                del_prfriend_ids.append(oid)

    # ---- 2. ai_risk 公式补 ----
    ai_ins = []
    for o in occs:
        oid = o["id"]
        if "ai_risk" not in rat[oid] and oid in aioe:
            s = clamp(aioe[oid] / 10.0)
            ai_ins.append((oid, "ai_risk", airisk_label(s), s))

    # ---- 3. 7 内在维按 occ_code 复制 ----
    # 捐赠源：每个 (occ_code_type, occ_code) 选一个含全部 7 维的职业
    donor = {}  # key=(type,code) -> {dim:(label,stars)}
    donor_rank = {}
    for o in occs:
        oid = o["id"]
        dims = rat[oid]
        if not all(d in dims for d in INTRINSIC):
            continue
        key = (o["occ_code_type"], o["occ_code"])
        cc = o["country_code"]
        pr = DONOR_PRIORITY.index(cc) if cc in DONOR_PRIORITY else len(DONOR_PRIORITY)
        if key not in donor or pr < donor_rank[key]:
            donor[key] = {d: dims[d] for d in INTRINSIC}
            donor_rank[key] = pr

    intr_ins = []
    no_donor = defaultdict(int)
    for o in occs:
        oid = o["id"]
        dims = rat[oid]
        miss = [d for d in INTRINSIC if d not in dims]
        if not miss:
            continue
        key = (o["occ_code_type"], o["occ_code"])
        src = donor.get(key)
        if not src:
            no_donor[o["country_code"]] += 1
            continue
        for d in miss:
            label, stars = src[d]
            intr_ins.append((oid, d, label, stars))

    # ---- 4. income_level 国内薪资分位 ----
    # 每国：所有有代表薪资的职业 -> 排序求分位
    country_sal = defaultdict(list)  # cc -> [(occ_id, rep)]
    for oid, bands in sal_bands.items():
        rep = rep_salary(bands)
        if rep is not None:
            country_sal[occ_cc[oid]].append((oid, rep))
    inc_ins = []
    for cc, lst in country_sal.items():
        lst.sort(key=lambda x: x[1])
        n = len(lst)
        rank = {oid: i for i, (oid, _) in enumerate(lst)}
        for oid, _ in lst:
            if "income_level" in rat[oid]:
                continue
            p = rank[oid] / (n - 1) if n > 1 else 0.5
            s = clamp(1.0 + p * 9.0)
            inc_ins.append((oid, "income_level", income_label(s), s))

    # ---- 报告 ----
    print("=== 计划变更（%s）===" % ("DRY" if dry else "APPLY"))
    print("1. pr 合并：full 档 pr_friendliness 重算 %d 条；删 pr_difficulty %d 条；"
          "info/none 删 pr_friendliness %d 条；full 档缺单维(保留)%d 条"
          % (len(pr_update), len(del_prdiff_ids), len(del_prfriend_ids), full_missing))
    print("2. ai_risk 公式补：%d 条" % len(ai_ins))
    print("3. 7 内在维复制补：%d 条（涉及职业 %d 个）"
          % (len(intr_ins), len(set(x[0] for x in intr_ins))))
    if no_donor:
        print("   无捐赠源(非ISCO或该码无成熟评分)：%s" % dict(no_donor))
    print("4. income_level 分位补：%d 条（%d 国有薪资分布）"
          % (len(inc_ins), len(country_sal)))

    if dry:
        return

    inserts = ai_ins + intr_ins + inc_ins
    with get_cursor() as cur:
        # 删除
        for i in range(0, len(del_prdiff_ids), 1000):
            ch = del_prdiff_ids[i:i + 1000]
            cur.execute("DELETE FROM occupation_ratings_v2 WHERE dimension='pr_difficulty' "
                        "AND occupation_id IN (%s)" % ",".join(["%s"] * len(ch)), ch)
        for i in range(0, len(del_prfriend_ids), 1000):
            ch = del_prfriend_ids[i:i + 1000]
            cur.execute("DELETE FROM occupation_ratings_v2 WHERE dimension='pr_friendliness' "
                        "AND occupation_id IN (%s)" % ",".join(["%s"] * len(ch)), ch)
        # 更新 full 档 pr_friendliness
        cur.executemany("UPDATE occupation_ratings_v2 SET stars=%s "
                        "WHERE occupation_id=%s AND dimension='pr_friendliness'", pr_update)
        # 插入（幂等：只补内存判定缺失的；唯一键防重）
        cur.executemany("INSERT INTO occupation_ratings_v2 (occupation_id,dimension,label,stars) "
                        "VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE stars=stars", inserts)
    print("已写入。inserts=%d, pr_update=%d, del_prdiff=%d, del_prfriend=%d"
          % (len(inserts), len(pr_update), len(del_prdiff_ids), len(del_prfriend_ids)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    main(a.dry)
