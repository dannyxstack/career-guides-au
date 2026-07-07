# -*- coding: utf-8 -*-
"""用百度大模型翻译补译 UI 文案（ui_i18n.json）尚缺的 key（en 母本 -> 各语言）。

与 translate_ui.py 同数据面（读 _ui_src.json，写 ui_i18n.json，indent=0），但走百度而非 LLM。
幂等：仅翻译目标语言尚缺的 key。含 {占位符} 的模板会做完整性校验——若译文丢了占位符，
回退保留英文源串（宁可英文也不出破损模板）。

先跑：node scripts/_extract_ui.mjs
运行：PYTHONIOENCODING=utf-8 python -m scripts.translate_ui_baidu [--locales de,ja]
"""
import sys, os, re, json, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from video_pipeline import baidu_translate
from scripts.translate_ui import OUT, SRC_UI, LOCALES, DIM_EN, DIMDESC_EN

_PH = re.compile(r"\{[a-zA-Z0-9_.]+\}")


def placeholders(s):
    return set(_PH.findall(s or ""))


def normalize(s):
    """把百度可能输出的全角花括号归一化回半角，保护占位符。"""
    return (s or "").replace("｛", "{").replace("｝", "}")


def fill_missing(src_map, existing, loc):
    """对 src_map 中缺失或上次回退成英文的键，用百度 en->loc 翻译；占位符校验失败则回退英文。"""
    out = dict(existing)
    added = 0
    for k, en in src_map.items():
        # 已有且不等于英文源（即已真正翻译）的跳过；等于英文源的视为上次回退，重试
        if k in out and out[k] != en:
            continue
        try:
            dst = normalize(baidu_translate.translate([en], loc, src_lang="en")[0])
        except Exception as e:
            print(f"    [{loc}] {k} 翻译失败，暂留英文：{e}")
            dst = en
        if placeholders(en) != placeholders(dst):
            print(f"    [{loc}] {k} 占位符丢失，回退英文：{dst!r}")
            dst = en
        out[k] = dst
        added += 1
    return out, added


def main(locales):
    UI_EN = json.load(open(SRC_UI, encoding="utf-8"))["ui"]
    data = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for loc in LOCALES:
        if locales and loc not in locales:
            continue
        cur = data.get(loc, {})
        ui, nu = fill_missing(UI_EN, cur.get("ui", {}), loc)
        dim, nd = fill_missing(DIM_EN, cur.get("dim", {}), loc)
        dd, ndd = fill_missing(DIMDESC_EN, cur.get("dimdesc", {}), loc)
        data[loc] = {"ui": ui, "dim": dim, "dimdesc": dd}
        print(f"[ui] {loc}: +{nu} ui, +{nd} dim, +{ndd} dimdesc (total ui={len(ui)})", flush=True)
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"[ui] 写出 {OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--locales", default="")
    a = ap.parse_args()
    main([x.strip() for x in a.locales.split(",") if x.strip()])
