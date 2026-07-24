"""
抓取 BLS 全国就业矩阵（National Employment Matrix, data.bls.gov）的"职业→行业"关系，
用于验证 occupation↔industry 多对多关系对本站数据的覆盖度。

说明：O*NET OnLine 的"按行业浏览"底层数据即来自 BLS 就业矩阵；O*NET Resource Center
自身不发布 occupation→NAICS 下载文件（见 downloads/onet-industry/README.md）。

来源端点（公开可达，2026-07 实测 200；www.bls.gov 直连 403）：
  https://data.bls.gov/projections/nationalMatrix?queryParams={SOC}&ioType=o

抽取：每个 SOC 页里 NAICS 大类（2 位，code 以 0000 结尾、type=Summary）行业行，
记录 (naics, title, 该职业中占比%, 就业量千)。

输出：downloads/onet-industry/us_soc_industry.json
"""
import json
import os
import re
import html
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "downloads", "onet-industry")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"
URL = "https://data.bls.gov/projections/nationalMatrix?queryParams={soc}&ioType=o"


def base_soc(code):
    """合成码 17-2071-BESS -> 基础 SOC 17-2071。"""
    m = re.match(r"(\d{2}-\d{4})", code)
    return m.group(1) if m else code


def parse_sectors(text):
    out = []
    for seg in re.findall(r"<TR[^>]*>(.*?)</TR>", text, re.S | re.I):
        c = re.findall(r"<T[DH][^>]*>(.*?)</T[DH]>", seg, re.S | re.I)
        c = [html.unescape(re.sub(r"<[^>]+>", " ", x)).strip() for x in c]
        if len(c) < 6:
            continue
        title, code, typ = c[0], c[1], c[2]
        # 保留 2 位大类(xx0000)与 3 位子类(xxx000)汇总行；
        # 制造/零售/运输(31-33,44-45,48-49)无 2 位汇总，只能靠 3 位子类聚合。
        if not re.fullmatch(r"\d{6}", code) or not code.endswith("000"):
            continue
        if typ.lower() != "summary":
            continue
        try:
            f = lambda x: float(x.replace(",", ""))   # 千位逗号，如 "2,850.7"
            emp = f(c[3]); pct_occ = f(c[4]); pct_ind = f(c[5])
        except ValueError:
            continue
        out.append({"naics": code[:2], "naics6": code, "title": title,
                    "pct_of_occ": pct_occ, "pct_of_ind": pct_ind, "emp_k": emp})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    codes = open(os.path.join(OUT, "_us_soc_list.txt"), encoding="utf-8").read().split()
    sess = requests.Session()
    sess.headers["User-Agent"] = UA

    result = {}
    fails = []
    n = len(codes)
    for i, code in enumerate(codes, 1):
        soc = base_soc(code)
        try:
            r = sess.get(URL.format(soc=soc), timeout=40)
            r.raise_for_status()
            sect = parse_sectors(r.text)
            result[code] = {"query_soc": soc, "sectors": sect}
            # 前 3 个存原始 HTML 作样本
            if i <= 3:
                with open(os.path.join(OUT, f"_sample_{soc}.html"), "w",
                          encoding="utf-8") as f:
                    f.write(r.text)
        except Exception as e:  # noqa
            result[code] = {"query_soc": soc, "sectors": [], "error": str(e)[:120]}
            fails.append(code)
        if i % 50 == 0 or i == n:
            print(f"  {i}/{n}  ok={i-len(fails)} fail={len(fails)}", flush=True)
        time.sleep(0.25)

    with open(os.path.join(OUT, "us_soc_industry.json"), "w", encoding="utf-8") as f:
        json.dump({"source": "data.bls.gov National Employment Matrix (ioType=o)",
                   "fetched": time.strftime("%Y-%m-%d"),
                   "level": "NAICS 2-digit sector",
                   "count": len(result), "fails": fails, "data": result},
                  f, ensure_ascii=False, indent=1)
    # 清理探测文件
    probe = os.path.join(OUT, "_probe")
    if os.path.isdir(probe):
        for fn in os.listdir(probe):
            os.remove(os.path.join(probe, fn))
        os.rmdir(probe)
    print(f"[done] {len(result)} SOC 写入 us_soc_industry.json，失败 {len(fails)}")


if __name__ == "__main__":
    main()
