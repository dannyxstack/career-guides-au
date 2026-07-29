"""装配冰岛(IS)官方薪资+就业代理 -> downloads/is/is_by_isco.json（零 LLM，确定性映射）。

冰岛只有 ISCO-88 体系(Istarf95)且无四位就业真数。补齐方式（用户确认降级入库）：
- 分类：Statistics Iceland VIN02001 的 142 个四位 Istarf95(=ISCO-88) 码，经 ILO 官方
        ISCO-88→ISCO-08 crosswalk(isco88_to_isco08.xlsx) 映射到 ISCO-08（覆盖 ~209/436）。
- 薪资：VIN02001 2025，Total earnings 的 Median / Mean，单位「千 ISK/月」→ ×1000×12 得年薪 ISK。
        sex=Total。
- 就业：冰岛无四位就业官方数 → 用薪资表「Weighted observations」作四位就业覆盖代理
        （同 DK 的 ANTAL 口径，非全体就业，salary_note 标注粗口径）。

多对多：ISCO-88→08 可能一对多/多对一；薪资按加权观测加权聚合到 ISCO-08。
本地名（冰岛语）留空，由 gen_is_official 的 DeepSeek 出 name_local(is)。

运行：python -m scripts.build_is_official
产物：downloads/is/is_by_isco.json
"""
import os, io, csv, json, re, collections, openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UNIVERSE = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
IS = os.path.join(REPO, "downloads", "is")
OUT = os.path.join(IS, "is_by_isco.json")


def main():
    uni_list = json.load(open(UNIVERSE, encoding="utf-8"))
    uni = {o["isco"] for o in uni_list}

    # ISCO-88 -> {ISCO-08}
    wb = openpyxl.load_workbook(os.path.join(IS, "isco88_to_isco08.xlsx"), data_only=True)
    ws = wb["ISCO-88 to 08"]
    m88 = collections.defaultdict(set)
    for r in ws.iter_rows(min_row=2, values_only=True):
        a, b = r[1], r[2]
        if a is None or b is None:
            continue
        try:
            a, b = str(int(a)).zfill(4), str(int(b)).zfill(4)
        except (TypeError, ValueError):
            continue
        m88[a].add(b)

    # 薪资 + 加权观测 by Istarf95 四位
    rows = list(csv.reader(io.StringIO(open(os.path.join(IS, "occupation_earnings_2025.csv"),
                                            "rb").read().decode("utf-8-sig"))))
    hdr = rows[0]
    ci_occ = 1
    ci_sex = 2
    ci_med = hdr.index("Total earnings Median")
    ci_mean = hdr.index("Total earnings Mean")
    ci_wobs = hdr.index("Total earnings Weighted observations")
    med88, mean88, wobs88 = {}, {}, {}
    for x in rows[1:]:
        if len(x) <= ci_wobs or x[ci_sex] != "Total":
            continue
        mo = re.match(r'^\s*(\d{4})\b', x[ci_occ])
        if not mo:
            continue
        c = mo.group(1)
        def num(i):
            try:
                return float(x[i])
            except (TypeError, ValueError):
                return None
        mv, mnv, wv = num(ci_med), num(ci_mean), num(ci_wobs)
        if mv:
            med88[c] = int(mv * 1000 * 12)   # 千ISK/月 -> ISK/年
        if mnv:
            mean88[c] = int(mnv * 1000 * 12)
        if wv:
            wobs88[c] = int(round(wv))

    # 88 四位 -> 目标 ISCO-08（同码优先，否则 crosswalk）
    def targets(c88):
        t = {x for x in m88.get(c88, set()) if x in uni}
        if not t and c88 in uni:
            t = {c88}
        return t

    # 反向：ISCO-08 -> [Istarf95 88 码]
    isco2c88 = collections.defaultdict(list)
    for c88 in set(list(med88) + list(wobs88)):
        for i in targets(c88):
            isco2c88[i].append(c88)

    out = {}
    for o in uni_list:
        isco = o["isco"]
        cs = isco2c88.get(isco, [])
        wf = sum(wobs88[c] for c in cs if c in wobs88) or None

        def wavg(src):
            num = den = 0
            for c in cs:
                if c in src:
                    w = wobs88.get(c, 1) or 1
                    num += src[c] * w
                    den += w
            return int(num / den) if den else None
        mv, mnv = wavg(med88), wavg(mean88)
        out[isco] = {
            "isco": isco, "label_en": o["label_en"],
            "avg_salary": mv,            # median 年薪 (ISK)，官方
            "salary_mean": mnv,          # mean 年薪 (ISK)，官方
            "workforce": wf,             # 加权观测覆盖代理，非全就业（粗口径）
            "name_local": None,          # 冰岛语名由 gen_is_official 的 LLM 出 (is)
            "salary_note": ("Official: Statistics Iceland VIN02001, median total monthly earnings 2025 "
                            "(thousand ISK) ×12 (both sexes). Istarf95/ISCO-88→ISCO-08 via ILO crosswalk. "
                            "Workforce = weighted observations in the earnings statistics (coverage proxy, "
                            "not total employment)." if mv else None),
        }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[build_is_official] {len(out)} ISCO -> is_by_isco.json | median薪资 "
          f"{sum(1 for v in out.values() if v['avg_salary'])} | mean {sum(1 for v in out.values() if v['salary_mean'])} | "
          f"workforce(代理) {sum(1 for v in out.values() if v['workforce'])}")


if __name__ == "__main__":
    main()
