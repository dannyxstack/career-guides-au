"""解析 INEGI 官方 SINCO↔CIUO-08(ISCO-08)交叉表 -> 干净 JSON。
源：downloads/mx/sinco_tablas_comparativas.xlsx 的 'SINCO-CIUO' 表（层级缩进布局，
4 位"Grupo unitario"码固定在第 3 列；CIUO-08 码在第 5 列）。
输出：downloads/mx/sinco_to_isco.json = { "<sinco4>": {name_es, isco, isco_name_es} }
（isco 为空表示"No tiene correspondencia"）。
运行：python -m scripts.parse_mx_crosswalk
"""
import os, re, json
import openpyxl

SRC = os.path.join("downloads", "mx", "sinco_tablas_comparativas.xlsx")
OUT = os.path.join("downloads", "mx", "sinco_to_isco.json")


def run():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb["SINCO-CIUO"]
    out = {}
    nocorr = 0
    for r in ws.iter_rows(values_only=True):
        cells = ["" if c is None else str(c).strip() for c in r]
        cells += [""] * (7 - len(cells))
        sinco, sname, isco, iname = cells[3], cells[4], cells[5], cells[6]
        if not re.fullmatch(r"\d{4}", sinco):
            continue  # 只取 4 位 grupo unitario 行
        isco_code = isco if re.fullmatch(r"\d{4}", isco) else ""
        if not isco_code:
            nocorr += 1
        out[sinco] = {"name_es": sname, "isco": isco_code,
                      "isco_name_es": iname if isco_code else ""}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    mapped = sum(1 for v in out.values() if v["isco"])
    iscos = {v["isco"] for v in out.values() if v["isco"]}
    print(f"[mx-xwalk] SINCO 4位码 {len(out)} 条；有 ISCO 对应 {mapped}，无对应 {nocorr}")
    print(f"[mx-xwalk] 覆盖 ISCO-08 unit group {len(iscos)} 个 -> {OUT}")


if __name__ == "__main__":
    run()
