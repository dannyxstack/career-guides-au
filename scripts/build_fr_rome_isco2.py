"""FR：用 DeepSeek 把本地 ROME 职业(英文名)分类到 ISCO-08 2位子大组，产出 crosswalk 缓存。

CEDEFOP France 曲线只到 ISCO 2位组，法国无单一官方 ROME↔ISCO 表，故用 LLM 语义映射：
每个 ROME 职业 → 40 个 ISCO2 组之一（返回 2位码）。结果写
downloads/outlook/EU/crosswalk/FR_rome_isco2_llm.json = {rome_code: "NN"}。

标注：此映射为 LLM 推算(estimate)，非官方；下游 load_outlook_eu_xw.py 据此接 CEDEFOP 曲线。
批量 25/次、可断点续跑（已缓存的跳过）。

用法：LLM_PROVIDER=deepseek DEEPSEEK_MODEL=... PYTHONIOENCODING=utf-8 \
      python -m scripts.build_fr_rome_isco2 [--batch 25] [--dry]
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.load_outlook import load_local_occ
from scripts.load_outlook_eu import ISCO2
from scripts import _deepseek_rest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "downloads", "outlook", "EU", "crosswalk", "FR_rome_isco2_llm.json")
OCC_JSON = os.path.join(ROOT, "site", "src", "data", "occupations_v2.json")

# ISCO2 码->组名（供提示）
CODE2NAME = {v: k for k, v in ISCO2.items()}
GROUP_LIST = "\n".join("%s = %s" % (c, CODE2NAME[c]) for c in sorted(CODE2NAME))

SYS = ("You are an occupation-classification expert. You map job titles to the single best "
       "ISCO-08 sub-major group (2-digit). Output valid JSON only.")


def local_fr():
    data = json.load(open(OCC_JSON, encoding="utf-8"))
    occ = data if isinstance(data, list) else data.get("occupations", data)
    return [(str(o["occ_code"]), o.get("name_en") or "", o.get("category") or "")
            for o in occ if o["country"] == "FR"]


def build_prompt(batch):
    items = "\n".join("- %s | %s | %s" % (c, n, cat) for c, n, cat in batch)
    return ("Assign each occupation to the single best ISCO-08 2-digit sub-major group.\n"
            "Valid 2-digit groups (code = name):\n%s\n\n"
            "Occupations (ROME code | English name | category):\n%s\n\n"
            'Return JSON {"map":{"ROME_CODE":"NN", ...}} where NN is one 2-digit code from the list above. '
            "Every ROME code in the input must appear exactly once." % (GROUP_LIST, items))


def main(batch_size, dry):
    fr = local_fr()
    cache = {}
    if os.path.exists(OUT):
        cache = json.load(open(OUT, encoding="utf-8"))
    todo = [x for x in fr if x[0] not in cache]
    print("FR ROME total=%d ; cached=%d ; todo=%d" % (len(fr), len(cache), len(todo)))
    if dry:
        print(build_prompt(todo[:5]))
        return
    valid = set(ISCO2.values())
    for i in range(0, len(todo), batch_size):
        batch = todo[i:i + batch_size]
        try:
            v = _deepseek_rest.complete_json(SYS, build_prompt(batch))
            m = v.get("map") or {}
        except Exception as e:
            print("  batch %d FAIL: %s" % (i // batch_size, e))
            continue
        ok = 0
        for code, _, _ in batch:
            iscok = str(m.get(code, "")).strip()
            if iscok in valid:
                cache[code] = iscok
                ok += 1
        json.dump(cache, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print("  batch %d/%d: +%d/%d (total cached %d)"
              % (i // batch_size + 1, (len(todo) + batch_size - 1) // batch_size, ok, len(batch), len(cache)))
    miss = [c for c, _, _ in fr if c not in cache]
    print("完成：cached=%d/%d ; 未映射=%d %s" % (len(cache), len(fr), len(miss), miss[:10]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=25)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    main(a.batch, a.dry)
