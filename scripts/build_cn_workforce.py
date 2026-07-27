"""用 2020 七普官方职业就业（CSCO 中类）规则映射出 CN 的 436 ISCO-08 四位 workforce。

输入：downloads/cn/census7/occ_by_csco_2020.json（表4-7 总计行，10% 长表抽样计数，已双重校验）。
方法（零 LLM，纯规则；与 IN 同款「官方组就业 × 跨国组内份额」）：
  1. 每个 CSCO 职业中类 → 一个 ISCO-08 中类(2 位)，按职业语义映射（MAP，见下）。
  2. 中类全国就业 = 官方全国就业总量 × (该中类抽样数 / 抽样合计)。
  3. 归并到 ISCO 中类后，按「各国现有 ISCO 四位 workforce 的组内份额」拆到该中类下的四位（fallback 均分）。
锚点：NAT_TOTAL = 2020 年末全国就业人员 75064 万（《2020 年国民经济和社会发展统计公报》，官方）。
说明：中类→ISCO 中类是官方语义映射；四位组内拆分是跨国份额近似（treemap 面积用途，页面注明）。
      军人/军职（普查未列）→ workforce=None。
运行：python -m scripts.build_cn_workforce
"""
import os, sys, json
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENSUS = os.path.join(REPO, "downloads", "cn", "census7", "occ_by_csco_2020.json")
UNI = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
OUT = os.path.join(REPO, "downloads", "cn", "cn_by_isco_workforce.json")
NAT_TOTAL = 750_640_000  # 2020 年末全国就业人员（官方统计公报）

# CSCO 职业中类 → ISCO-08 中类(2 位)，按职业语义（单值）。key 必须与 census JSON 的中类名逐字一致。
MAP = {
    # 1 负责人 → 管理人员
    "中国共产党机关负责人": "11", "国家机关负责人": "11", "民主党派和工商联负责人": "11",
    "人民团体和群众团体社会组织及其他成员组织负责人": "11", "基层群众自治组织负责人": "11",
    "企事业单位负责人": "13",
    # 2 专业技术人员 → 专业人员/技术员
    "科学研究人员": "21", "工程技术人员": "21", "农业技术人员": "21", "飞机和船舶技术人员": "31",
    "卫生专业技术人员": "22", "经济和金融专业人员": "24", "法律社会和宗教专业人员": "26",
    "教学人员": "23", "文学艺术体育专业人员": "26", "新闻出版文化专业人员": "26", "其他专业技术人员": "21",
    # 3 办事人员和有关人员 → 文书/保护服务
    "办事人员": "41", "安全和消防人员": "54", "其他办事人员和有关人员": "43",
    # 4 社会生产服务和生活服务人员 → 服务销售/ICT/金融/操作
    "批发与零售服务人员": "52", "交通运输仓储和邮政业服务人员": "83", "住宿和餐饮业服务人员": "51",
    "信息传输软件和信息技术服务人员": "25", "金融服务人员": "33", "房地产服务人员": "33",
    "租赁和商务服务人员": "33", "技术辅助服务人员": "31", "水利环境和公共设施管理服务人员": "96",
    "居民服务人员": "51", "电力燃气及水供应服务人员": "81", "修理及制作服务人员": "72",
    "文化体育和娱乐服务人员": "34", "健康服务人员": "53", "其他社会生产和生活服务人员": "51",
    # 5 农林牧渔业生产及辅助人员 → 技术农林渔/初级农工
    "农业生产人员": "61", "林业生产人员": "62", "畜牧业生产人员": "61", "渔业生产人员": "62",
    "农林牧渔专业辅助人员": "92", "其他农林牧渔业生产及辅助人员": "61",
    # 6 生产制造及有关人员 → 手工业/机器操作/装配
    "农副产品加工人员": "75", "食品饮料生产加工人员": "75", "烟草及其制品加工人员": "75",
    "纺织针织印染人员": "75", "纺织品服装和皮革毛皮制品加工制作人员": "75", "木材加工与木家具制作人员": "75",
    "纸及纸制品生产加工人员": "81", "印刷和记录媒介复制人员": "73", "文教工美体育和娱乐用品制造人员": "73",
    "石油加工和炼焦煤化工生产人员": "81", "化学原料和化学制品制造人员": "81", "医药制造人员": "81",
    "化学纤维制造人员": "81", "橡胶和塑料制品制造人员": "81", "非金属矿物制品制造人员": "81",
    "采矿人员": "81", "金属冶炼和压延加工人员": "72", "机械制造基础加工人员": "72", "金属制品制造人员": "72",
    "通用设备制造人员": "72", "专用设备制造人员": "72", "汽车制造人员": "82", "铁路船舶航空设备制造人员": "82",
    "电气机械和器材制造人员": "74", "计算机通信和其他电子设备制造人员": "82", "仪器仪表制造人员": "74",
    "废弃资源综合利用人员": "96", "电力热力气体水生产和输配人员": "81", "建筑施工人员": "71",
    "运输设备和通用工程机械操作人员及有关人员": "83", "生产辅助人员": "93", "其他生产制造及有关人员": "93",
    # 8 不便分类 → 初级职业
    "不便分类的其他从业人员": "96",
}


def main():
    cen = json.load(open(CENSUS, encoding="utf-8"))
    uni = json.load(open(UNI, encoding="utf-8"))
    sample_total = cen["sample_total"]
    # 扁平化中类 -> 抽样数
    mids = {}
    for mj in cen["majors"].values():
        mids.update(mj["mids"])
    missing = [m for m in mids if m not in MAP]
    assert not missing, f"未映射的中类: {missing}"

    # 中类全国就业 -> 归并到 ISCO 中类(2 位)
    isco2_emp = defaultdict(float)
    for mid, samp in mids.items():
        nat = NAT_TOTAL * samp / sample_total
        isco2_emp[MAP[mid]] += nat

    # 跨国份额参考：occ_code 落在 436 universe 集合内、workforce>0 的各国汇总
    uset = {o["isco"] for o in uni}
    ref = defaultdict(float)
    with get_cursor() as cur:
        cur.execute("SELECT occ_code, SUM(workforce_size) w FROM occupations "
                    "WHERE workforce_size>0 GROUP BY occ_code")
        for r in cur.fetchall():
            c = str(r["occ_code"])
            if c in uset:
                ref[c] += float(r["w"] or 0)

    # 按 ISCO 中类分组四位（排除军职 0x：普查未含军人）
    sibs = defaultdict(list)
    for o in uni:
        code = o["isco"]
        if code[0] == "0":
            continue
        sibs[code[:2]].append(code)

    out = {}
    for o in uni:
        code = o["isco"]
        if code[0] == "0":
            out[code] = {"isco": code, "workforce": None, "basis": "armed forces — not in census"}
            continue
        g = code[:2]
        emp = isco2_emp.get(g, 0.0)
        sib = sibs[g]
        rw = {c: ref.get(c, 0.0) for c in sib}
        tot = sum(rw.values())
        share = (rw[code] / tot) if tot > 0 else (1.0 / len(sib))
        out[code] = {"isco": code, "workforce": round(emp * share),
                     "basis": f"CSCO census (major-mid official) -> ISCO {g}; split by cross-country share"}

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    wf_tot = sum(v["workforce"] or 0 for v in out.values())
    have = sum(1 for v in out.values() if v["workforce"])
    # 校验：分派到的 ISCO 中类是否都在 universe（否则就业丢失）
    lost = {g: e for g, e in isco2_emp.items() if g not in sibs}
    print(f"[build_cn_wf] 436 ISCO | 有就业 {have} | 就业合计 {wf_tot:,} | 锚定 {NAT_TOTAL:,}")
    if lost:
        print(f"  ⚠️ 未落地的 ISCO 中类(universe 无四位): {lost}")
    for c in ("2512", "2411", "5223", "6111", "7112", "8322", "9412"):
        m = next((o for o in uni if o["isco"] == c), None)
        if m:
            print(f"   {c} {m['label_en'][:28]}: wf={out[c]['workforce']:,}")


if __name__ == "__main__":
    main()
