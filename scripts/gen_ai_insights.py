"""批量为职业生成「AI 时代」分析（occupation_ai）：ai_graph(cluster + 4 个 10 分制) + AI 文案。
用 video_pipeline.llm.complete_json（按 LLM_PROVIDER，DeepSeek=json_object）。

要点：
- 分数为 10 分制小数（1.0-10.0，保留 1 位）。
- adjacent：把同国职业清单(occ_code|中文名|英文名)喂给 LLM，让它从清单里挑 3 个相邻 occ_code，
  再校验这些 code 在本国存在（命中才写），避免编造。
- 中文母本写入后，再跑 collect_strings + translate_strings 翻到 10 语言。

幂等：默认只处理缺数据（verdict_zh IS NULL OR cluster IS NULL）的职业；--redo 处理全部。
运行：python -m scripts.gen_ai_insights [--limit N] [--country AU] [--redo]
"""
import sys, os, json, argparse, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import llm

CLUSTERS = ["high_ai_exposure", "ai_augmented", "licensed_accountable",
            "physical_site_based", "human_trust_care", "regulated_public_safety"]
VERDICTS = ["compressed", "amplified", "mixed"]

SYSTEM = (
    "你是职业与劳动力市场分析师，专长 AI/自动化对职业任务结构的影响。"
    "针对给定职业，输出务实、具体、可执行的中文分析（面向国际读者，不要专门提『华人/中文社区』）。"
    "只输出一个 JSON 对象，不要多余文字。"
)

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "verdict_type": {"type": "string", "enum": VERDICTS},
        "verdict_zh": {"type": "string"},
        "entry_narrowing_zh": {"type": "string"},
        "replaced_zh": {"type": "array", "items": {"type": "string"}},
        "augmented_zh": {"type": "array", "items": {"type": "string"}},
        "moat_zh": {"type": "array", "items": {"type": "string"}},
        "skills_zh": {"type": "array", "items": {"type": "string"}},
        "upgrade_path_zh": {"type": "string"},
        "cluster": {"type": "string", "enum": CLUSTERS},
        "automation_exposure": {"type": "number"},
        "human_moat": {"type": "number"},
        "entry_risk": {"type": "number"},
        "ai_upside": {"type": "number"},
        "adjacent_codes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["verdict_type", "verdict_zh", "entry_narrowing_zh", "replaced_zh", "augmented_zh",
                 "moat_zh", "skills_zh", "upgrade_path_zh", "cluster",
                 "automation_exposure", "human_moat", "entry_risk", "ai_upside", "adjacent_codes"],
}


def clamp10(v, default=5.0):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return default
    return round(max(1.0, min(10.0, x)), 1)


def build_prompt(occ, name_zh, name_en, summary_zh, peers):
    peer_lines = "\n".join(f"{p['occ_code']} | {p['zh']} | {p['en']}" for p in peers)
    return f"""职业信息：
- 中文名：{name_zh or name_en}
- 英文名：{name_en}
- 国家：{occ['country_code']}
- 分类：{occ['category']}
- 简介：{(summary_zh or '')[:400]}

同国可选「相邻职业」清单（格式 occ_code | 中文名 | 英文名）：
{peer_lines}

请输出 JSON，字段如下（全部必填）：
- verdict_type：{'/'.join(VERDICTS)} 之一（compressed=被自动化压缩；amplified=被 AI 放大；mixed=喜忧参半）
- verdict_zh：一句话风险结论（60-120 字）
- entry_narrowing_zh：入门岗位是否变窄的叙述（60-120 字）
- replaced_zh：AI 会替代/接管的具体任务，中文数组，3-5 条
- augmented_zh：AI 会增强的任务，中文数组，3-5 条
- moat_zh：人类护城河（难被替代的能力/责任），中文数组，3-5 条
- skills_zh：未来 5 年建议补的技能，中文数组，4-6 条
- upgrade_path_zh：AI 时代升级路线（一段叙述，80-160 字）
- cluster：{'/'.join(CLUSTERS)} 之一
- automation_exposure：AI 可自动化程度，10 分制小数（1.0-10.0，越高越危险）
- human_moat：人类护城河，10 分制小数（越高越稳）
- entry_risk：入门岗位压缩程度，10 分制小数（越高越难入门）
- ai_upside：AI 放大能力潜力，10 分制小数（越高越值得学 AI 工具）
- adjacent_codes：从上面清单里挑 3 个最相邻职业的 occ_code（字符串数组，必须来自清单，不含本职业）
四个分数要与 cluster、verdict_type 相互自洽（如 high_ai_exposure 通常 automation_exposure 高、human_moat 低）。"""


def validate(d, valid_codes, self_code):
    out = {}
    out["verdict_type"] = d.get("verdict_type") if d.get("verdict_type") in VERDICTS else "mixed"
    out["cluster"] = d.get("cluster") if d.get("cluster") in CLUSTERS else "ai_augmented"
    for k in ("verdict_zh", "entry_narrowing_zh", "upgrade_path_zh"):
        out[k] = (d.get(k) or "").strip()
    for k in ("replaced_zh", "augmented_zh", "moat_zh", "skills_zh"):
        arr = [str(x).strip() for x in (d.get(k) or []) if str(x).strip()]
        out[k] = arr
    for k in ("automation_exposure", "human_moat", "entry_risk", "ai_upside"):
        out[k] = clamp10(d.get(k))
    # adjacent：仅保留本国存在且非自身的 code，去重，最多 3
    adj, seen = [], set()
    for c in (d.get("adjacent_codes") or []):
        c = str(c).strip()
        if c and c != self_code and c in valid_codes and c not in seen:
            adj.append(c); seen.add(c)
        if len(adj) >= 3:
            break
    out["adjacent"] = adj
    return out


def ok(v):
    return bool(v["verdict_zh"] and v["entry_narrowing_zh"] and v["replaced_zh"]
               and v["augmented_zh"] and v["moat_zh"] and v["skills_zh"])


def run(limit, country, redo):
    with get_cursor() as cur:
        # 各国职业清单（含中文名）——用于相邻挑选与反查
        cur.execute("SELECT o.id,o.country_code,o.occ_code,o.category,"
                    "i.name AS name_zh, i.summary AS summary_zh, o.anzsco_title AS name_en "
                    "FROM occupations o "
                    "LEFT JOIN occupations_i18n i ON i.occupation_id=o.id AND i.locale='zh-CN' "
                    "ORDER BY o.country_code,o.category,o.id")
        all_occ = cur.fetchall()
        # 已有 ai 数据
        cur.execute("SELECT occupation_id,verdict_zh,cluster FROM occupation_ai")
        have = {r["occupation_id"]: r for r in cur.fetchall()}

    by_country = {}
    for o in all_occ:
        by_country.setdefault(o["country_code"], []).append(o)

    targets = []
    for o in all_occ:
        if country and o["country_code"] != country:
            continue
        h = have.get(o["id"])
        need = redo or (not h) or (h["verdict_zh"] is None) or (h["cluster"] is None)
        if need:
            targets.append(o)
    if limit:
        targets = targets[:limit]
    print(f"[gen] 待生成 {len(targets)} 个职业 (model={llm.current_model()})")

    done = fail = 0
    for idx, o in enumerate(targets, 1):
        peers_all = [p for p in by_country[o["country_code"]] if p["id"] != o["id"]]
        # 同类优先，其余补足，控制清单长度（≤60 行）
        same = [p for p in peers_all if p["category"] == o["category"]]
        others = [p for p in peers_all if p["category"] != o["category"]]
        peers = (same + others)[:60]
        valid_codes = {p["occ_code"] for p in peers}
        peer_view = [{"occ_code": p["occ_code"], "zh": p["name_zh"] or "", "en": p["name_en"] or ""} for p in peers]
        prompt = build_prompt(o, o["name_zh"], o["name_en"], o["summary_zh"], peer_view)
        try:
            raw = llm.complete_json(SYSTEM, prompt, SCHEMA)
            v = validate(raw, valid_codes, o["occ_code"])
            if not ok(v):
                raise ValueError("必填文案/列表为空")
        except Exception as e:
            fail += 1
            print(f"  [{idx}/{len(targets)}] {o['country_code']}/{o['occ_code']} {o['name_en']} 失败: {e}")
            continue
        with get_cursor() as cur:
            cur.execute(
                "REPLACE INTO occupation_ai (occupation_id,verdict_type,verdict_zh,entry_narrowing_zh,"
                "replaced_zh,augmented_zh,moat_zh,skills_zh,upgrade_path_zh,adjacent,"
                "cluster,automation_exposure,human_moat,entry_risk,ai_upside) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (o["id"], v["verdict_type"], v["verdict_zh"], v["entry_narrowing_zh"],
                 json.dumps(v["replaced_zh"], ensure_ascii=False), json.dumps(v["augmented_zh"], ensure_ascii=False),
                 json.dumps(v["moat_zh"], ensure_ascii=False), json.dumps(v["skills_zh"], ensure_ascii=False),
                 v["upgrade_path_zh"], json.dumps(v["adjacent"], ensure_ascii=False),
                 v["cluster"], v["automation_exposure"], v["human_moat"], v["entry_risk"], v["ai_upside"]))
        done += 1
        print(f"  [{idx}/{len(targets)}] {o['country_code']}/{o['occ_code']} {o['name_en']} "
              f"→ {v['cluster']} ae={v['automation_exposure']} hm={v['human_moat']} adj={v['adjacent']}")
    print(f"[OK] 成功 {done}，失败 {fail}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--country", default="")
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    run(a.limit, a.country.strip().upper(), a.redo)
