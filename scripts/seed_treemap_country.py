"""Treemap 层最小入库（零 LLM）：workforce + ISCO 英文名 + category(借 IT) + ai_risk 评分。

用于 20 国批次中「无四位官方薪资、只做 treemap 层」的国家。数字零 LLM：
- workforce ← downloads/{cc}/{cc}_by_isco.json（Eurostat 大类按跨国份额拆四位 / 或 ILOSTAT）。
- name(英文母本) ← ISCO-08 universe label_en。
- category ← 复用 IT 的 occ_code→category（同一 ISCO 骨架）。
- ai_risk 评分 ← aioe_pct/10（ISCO 全球共享，clamp 1-10）。
- 薪资 / 文案 / 教育 / 签证 / FAQ 一律留空（treemap 不需要；aijobrisk-go 详情页诚实为空）。
- 本地名：仅当 {cc}_by_isco.json 的 name_local 有值（来自本国官方文档）才灌 native_locale TM，否则跳过（英文兜底）。
- AI 暴露块（automation_exposure，treemap 上色用）另跑：copy_ai_blocks_by_code --to {cc} --from IT。

用法：python -m scripts.seed_treemap_country --country BE
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper_v2 import seed_occupation_en
from scripts.gen_intl_v2 import inject_native_name, load_universe

# 仅数字所需的最小配置：货币 + 本地名 locale（无官方本地名的国 native_locale=None）。
CFG = {
    "BE": {"currency": "EUR", "native_locale": None},
    "AT": {"currency": "EUR", "native_locale": None},
    "PL": {"currency": "PLN", "native_locale": None},
    "PT": {"currency": "EUR", "native_locale": None},
    "GR": {"currency": "EUR", "native_locale": None},
    "HU": {"currency": "HUF", "native_locale": None},
    "CZ": {"currency": "CZK", "native_locale": "cs"},
    "RO": {"currency": "RON", "native_locale": None},
    "LU": {"currency": "EUR", "native_locale": None},
    "SK": {"currency": "EUR", "native_locale": None},
    "SI": {"currency": "EUR", "native_locale": "sl"},
    "HR": {"currency": "EUR", "native_locale": None},
    "TR": {"currency": "TRY", "native_locale": None},
    # 非 EU（ILOSTAT workforce）
    "AR": {"currency": "ARS", "native_locale": "es"},
    "CL": {"currency": "CLP", "native_locale": "es"},
    "MY": {"currency": "MYR", "native_locale": None},
    "ID": {"currency": "IDR", "native_locale": "id"},
    "TH": {"currency": "THB", "native_locale": "th"},
    "VN": {"currency": "VND", "native_locale": "vi"},
    "SG": {"currency": "SGD", "native_locale": None},
    # 波罗的海三国 + 瑞士补全（薪资已合并进 {cc}_by_isco.json，本脚本读取）。
    # 站点无 et/lv/lt 显示语言 → native_locale=None（英文兜底）；CH 有官方语言槽但 by_isco 无本地名。
    "EE": {"currency": "EUR", "native_locale": None},  # 官方 PA633 四位薪资
    "LV": {"currency": "EUR", "native_locale": None},  # Eurostat SES 宽口径薪资
    "LT": {"currency": "EUR", "native_locale": None},  # Eurostat SES 宽口径薪资
    "CH": {"currency": "CHF", "native_locale": None},  # 补全覆盖；无官方四位薪资（by_isco 薪资为空）
}


def salary_rows(off):
    """从 by_isco 记录构建 occupation_salaries_v2 行（供 export pick_avg_salary 取用）。
    avg_salary=年化中位（或均值），salary_mean=年化均值。标签 Median/Average 供 export 识别。"""
    rows, i = [], 0
    note = off.get("salary_note")
    avg, mean = off.get("avg_salary"), off.get("salary_mean")
    if mean is not None:
        rows.append({"experience": "Average", "salary_min": mean, "salary_max": mean,
                     "salary_note": note, "sort_order": i}); i += 1
    # avg 存官方中位（与 mean 不同才单列）；EE 仅有均值时 avg==mean，不重复。
    if avg is not None and avg != mean:
        rows.append({"experience": "Median", "salary_min": avg, "salary_max": avg,
                     "salary_note": note, "sort_order": i})
    return rows


def _airisk_label(s):
    return "High exposure" if s >= 7 else "Moderate exposure" if s >= 4 else "Low exposure"


def official_path(cc):
    return os.path.join("downloads", cc.lower(), f"{cc.lower()}_by_isco.json")


def it_category_map():
    with get_cursor() as cur:
        cur.execute("SELECT occ_code, category FROM occupations WHERE country_code='IT'")
        return {r["occ_code"]: r["category"] for r in cur.fetchall()}


def run(cc):
    cc = cc.upper()
    assert cc in CFG, f"未配置 {cc}"
    cur_code = CFG[cc]["currency"]
    nloc = CFG[cc]["native_locale"]
    off_all = json.load(open(official_path(cc), encoding="utf-8"))
    cats = it_category_map()
    uni = load_universe()
    okc = wf_c = loc_c = sal_c = 0
    for isco, u in uni.items():
        off = off_all.get(isco) or {}
        title_en = u["label_en"]
        wf = off.get("workforce")
        aioe_pct = u.get("aioe_pct")
        OCC = {"country_code": cc, "occ_code": isco, "occ_code_type": "ISCO08", "anzsco_code": isco,
               "anzsco_title": title_en, "category": cats.get(isco, "Other"), "currency": cur_code,
               "workforce_size": wf, "shortage_listed": 0, "is_migration": 1, "is_public_servant": 0,
               "growth_areas": []}
        TEXT = {"name": title_en}
        RAT = []
        if aioe_pct is not None:
            s = max(1.0, min(10.0, round(aioe_pct / 10.0, 1)))
            RAT.append({"dimension": "ai_risk", "label": _airisk_label(s), "stars": s,
                        "note": "Derived from ILO/OpenAI AIOE percentile (ISCO-shared)"})
        SAL = salary_rows(off)
        with get_cursor() as c:
            occ_id = seed_occupation_en(c, OCC, TEXT, [], [], SAL, [], RAT, [], [], [])
            if nloc and off.get("name_local"):
                inject_native_name(c, title_en, nloc, off["name_local"], cc)
                loc_c += 1
        okc += 1
        if wf:
            wf_c += 1
        if SAL:
            sal_c += 1
    print(f"[seed_treemap {cc}] 入库 {okc} | 有 workforce {wf_c} | 有薪资 {sal_c} | 本地名({nloc}) {loc_c} | 货币 {cur_code}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    a = ap.parse_args()
    run(a.country)
