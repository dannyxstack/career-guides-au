"""装配中国官方薪资映射 -> downloads/cn/cn_by_isco.json（不估算，纯官方+确定性映射）。

中国无逐职业官方工资；官方最细=NBS《2022 规模以上企业分岗位就业人员年平均工资》的 5 个岗位大类。
本脚本把 436 ISCO-08 四位职业按其 major(首位) 确定性映射到一个 CSCO 岗位大类，取该岗位的全国官方
平均工资作为 avg_salary。映射依据 CSCO《职业分类大典》的岗位大类↔ISCO 大类对应（官方口径，非估算），
但工资是"岗位大类级"而非"逐职业"，note 中注明粗口径。

运行：python -m scripts.build_cn_salary
产物：downloads/cn/cn_by_isco.json
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UNIVERSE = os.path.join(REPO, ".codex_tmp", "isco08_universe.json")
WAGES = os.path.join(REPO, "downloads", "cn", "post_wages_2022.json")
OUT = os.path.join(REPO, "downloads", "cn", "cn_by_isco.json")

# ISCO-08 major group(首位) -> CSCO 岗位大类(NBS 分岗位工资的 5 类) 官方对应。
# 1 管理 / 2·3 专业技术 / 4 办事 / 5·9 社会生产服务和生活服务 / 6·7·8 生产制造 / 0 军职(无工资)。
MAJOR_TO_POST = {
    "1": "中层及以上管理人员",
    "2": "专业技术人员",
    "3": "专业技术人员",
    "4": "办事人员和有关人员",
    "5": "社会生产服务和生活服务人员",
    "6": "生产制造及有关人员",
    "7": "生产制造及有关人员",
    "8": "生产制造及有关人员",
    "9": "社会生产服务和生活服务人员",
    "0": None,
}


def main():
    uni = json.load(open(UNIVERSE, encoding="utf-8"))
    wages = json.load(open(WAGES, encoding="utf-8"))
    by_post = wages["national_by_post"]
    year = wages["_year"]
    out = {}
    for o in uni:
        isco = o["isco"]
        major = o.get("major") or isco[0]
        post = MAJOR_TO_POST.get(major)
        avg = by_post.get(post) if post else None
        out[isco] = {
            "isco": isco,
            "label_en": o["label_en"],
            "post": post,
            "avg_salary": avg,           # CNY/年，官方岗位大类级（非逐职业）
            "workforce": None,           # 中国无逐职业官方就业数；普查仅到中类，本次留空不估算
            "name_zh": None,             # 官方 ISCO-08 中文名待补；否则由翻译管线出 zh-CN
            "salary_note": (f"官方口径：{post}全国年平均工资（规模以上企业，NBS {year}）。"
                            f"中国无逐职业级工资，此为岗位大类级映射。" if post else None),
        }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    covered = sum(1 for v in out.values() if v["avg_salary"])
    print(f"[build_cn_salary] {len(out)} ISCO -> cn_by_isco.json | 有官方薪资 {covered} | 军职留空 {len(out)-covered}")
    # 分布核对
    from collections import Counter
    c = Counter(v["post"] for v in out.values())
    for k, n in c.most_common():
        print(f"   {k or '(军职/无)'}: {n}")


if __name__ == "__main__":
    main()
