"""把 occupations.growth_areas 里的中文关键词翻成英文（就地更新共享列，旧站与 v2 同时受益）。
前端 JobDetail 直接原样渲染 growth_areas（不走 tr），故中文会漏到英文页；此脚本根治。
幂等：只处理仍含中文的行。备份原值到 .codex_tmp/growth_zh_backup.json。
运行：python -m scripts.fix_growth_en [--dry]
"""
import sys, os, json, re, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts import _deepseek_rest

CJK = re.compile(r"[一-鿿]")
TMP = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp")
BACKUP = os.path.join(TMP, "growth_zh_backup.json")


def _load(ga):
    return json.loads(ga) if isinstance(ga, str) else (ga or [])


def translate_items(items):
    """中文关键词数组 -> 英文数组（等长）。"""
    system = ("You translate Chinese career 'growth area' tags into concise English tags for an occupations "
              "website. Keep existing English words/acronyms and parenthetical English terms as-is. Keep it short "
              "(tag-style, not sentences).")
    prompt = ('Translate these tags to English. Return a JSON object {"t":[...]} with the SAME length and order:\n'
              + json.dumps(items, ensure_ascii=False))
    out = _deepseek_rest.complete_json(system, prompt)
    res = out.get("t") or []
    if len(res) != len(items):
        raise ValueError(f"长度不匹配 expect {len(items)} got {len(res)}")
    return res


def run(dry):
    with get_cursor() as cur:
        cur.execute("SELECT id, country_code, growth_areas FROM occupations")
        rows = cur.fetchall()
    targets = []
    uniq = set()
    for r in rows:
        ga = _load(r["growth_areas"])
        cn = [x for x in ga if isinstance(x, str) and CJK.search(x)]
        if cn:
            targets.append((r["id"], r["country_code"], ga))
            uniq.update(cn)
    print(f"[fix_growth] 含中文的职业 {len(targets)}，去重中文标签 {len(uniq)}")
    if dry:
        return
    # 备份
    os.makedirs(TMP, exist_ok=True)
    json.dump({str(i): ga for i, _c, ga in targets}, open(BACKUP, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[fix_growth] 已备份原值 -> {BACKUP}")
    # 批量翻译唯一标签
    items = sorted(uniq)
    tmap = {}
    B = 40
    for i in range(0, len(items), B):
        chunk = items[i:i + B]
        try:
            res = translate_items(chunk)
        except Exception as e:
            print(f"  批 {i} 失败({e})，逐条重试")
            res = []
            for x in chunk:
                try:
                    res.append(translate_items([x])[0])
                except Exception:
                    res.append(x)
        tmap.update({z: en for z, en in zip(chunk, res)})
        print(f"  翻译 {min(i+B,len(items))}/{len(items)}")
    # 就地更新
    upd = 0
    with get_cursor() as cur:
        for oid, _cc, ga in targets:
            new = [tmap.get(x, x) if isinstance(x, str) and CJK.search(x) else x for x in ga]
            cur.execute("UPDATE occupations SET growth_areas=%s WHERE id=%s",
                        (json.dumps(new, ensure_ascii=False), oid))
            upd += 1
    print(f"[fix_growth] 更新 {upd} 行 growth_areas -> 英文")
    # 复核
    with get_cursor() as cur:
        cur.execute("SELECT growth_areas FROM occupations")
        left = sum(1 for r in cur.fetchall() if CJK.search(json.dumps(_load(r["growth_areas"]), ensure_ascii=False)))
    print(f"[fix_growth] 复核：仍含中文的行 {left}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    run(a.dry)
