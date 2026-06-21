"""批量为职业生成「已经在替代/部分替代该职业的 AI 工具」(ai_disruptors + occupation_ai_disruptor)。

用 video_pipeline.llm.complete_json（按 LLM_PROVIDER，DeepSeek=json_object）让模型列出
真实、知名、可验证的 AI 工具/产品/平台/模型/研究/新闻，禁止编造。

数据模型见 migrate_ai_disruptors：
- ai_disruptors：全站共享工具目录（name 唯一，品牌名不翻译，summary_zh 走 TM）。
  已存在的工具(如人工录入的试点)不覆盖（INSERT ... ON DUPLICATE KEY UPDATE id=id 保留首版）。
- occupation_ai_disruptor：职业↔工具关联，scope_zh 描述替代了该职业的哪部分工作。

批次：--batch-size 每批职业数（默认 50），--rest 批次间休息秒数（默认 1800=30 分钟）。
幂等：默认只处理「尚无任何 disruptor 关联」的职业；--redo 处理全部。
中文母本写入后，需再跑 collect_strings + translate_strings + export + build 才进多语言上线。

运行：python -m scripts.gen_ai_disruptors [--batch-size 50] [--rest 1800] [--limit N] [--country AU] [--redo]
"""
import sys, os, json, re, argparse, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from video_pipeline import llm, config

TYPES = ["tool", "platform", "product", "model", "research", "news"]
LEVELS = ["partial", "major", "full"]
MATURITY = ["emerging", "adopted", "mainstream"]

SYSTEM = (
    "你是 AI 工具与劳动力市场分析师。针对给定职业，列出『已经在替代或部分替代该职业工作』的"
    "真实、知名、可被验证的 AI 工具 / 产品 / 平台 / 模型 / 研究项目 / 重大新闻。"
    "严禁编造不存在的产品；只列你确信真实存在的。"
    "url 只在你确信是官方域名时填写，否则留空字符串。中文叙述面向国际读者，不要提『华人/中文社区』。"
    "只输出一个 JSON 对象，不要多余文字。"
)

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "disruptors": {
            "type": "array",
            "items": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string", "enum": TYPES},
                    "vendor": {"type": "string"},
                    "url": {"type": "string"},
                    "year": {"type": "integer"},
                    "maturity": {"type": "string", "enum": MATURITY},
                    "summary_zh": {"type": "string"},
                    "level": {"type": "string", "enum": LEVELS},
                    "scope_zh": {"type": "string"},
                    "evidence_url": {"type": "string"},
                },
                "required": ["name", "type", "summary_zh", "level", "scope_zh"],
            },
        }
    },
    "required": ["disruptors"],
}


def _parse_list(text):
    """容错解析：模型可能返回对象 {"disruptors":[...]}、顶层数组 [...] 或代码块包裹。返回 list。"""
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    if not (text.startswith("[") or text.startswith("{")):
        i, j = text.find("["), text.find("{")
        cand = [x for x in (i, j) if x != -1]
        if cand:
            text = text[min(cand):]
    data = json.loads(text)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("disruptors"), list):
            return data["disruptors"]
        return [data]  # 单个对象
    return []


def get_disruptors(system, prompt):
    """取工具列表。DeepSeek 直连（容忍数组/对象）；其他 provider 走 llm.complete_json。"""
    if config.LLM_PROVIDER == "deepseek":
        from openai import OpenAI
        client = OpenAI(api_key=config.require("DEEPSEEK_API_KEY"), base_url=config.DEEPSEEK_BASE_URL)
        resp = client.chat.completions.create(
            model=config.DEEPSEEK_MODEL, max_tokens=4000,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"})
        return _parse_list(resp.choices[0].message.content)
    raw = llm.complete_json(system, prompt, SCHEMA)
    return raw.get("disruptors") or (raw if isinstance(raw, list) else [])


def build_prompt(occ, name_zh, name_en, summary_zh):
    return f"""职业信息：
- 中文名：{name_zh or name_en}
- 英文名：{name_en}
- 国家：{occ['country_code']}
- 分类：{occ['category']}
- 简介：{(summary_zh or '')[:400]}

请列出『已经在替代或部分替代这个职业工作』的真实 AI 工具/产品/平台/模型/研究/新闻，3-6 个，按影响从大到小。
每个对象字段：
- name：产品/工具的真实品牌名（英文原名，不翻译，如 "Midjourney"、"ChatGPT"、"GitHub Copilot"）
- type：{'/'.join(TYPES)} 之一
- vendor：厂商/机构（如 OpenAI、Adobe）
- url：官网链接（不确定就填空字符串 ""）
- year：出现或走红的年份（整数，如 2023）
- maturity：{'/'.join(MATURITY)} 之一（emerging=新兴/adopted=已被采用/mainstream=主流普及）
- summary_zh：这个工具是做什么的（中文，40-80 字）
- level：对【本职业】的替代程度，{'/'.join(LEVELS)} 之一（partial=部分替代/major=大幅替代/full=几乎完全替代）
- scope_zh：它替代了【本职业】的哪部分工作（中文，40-90 字，要具体到任务）
- evidence_url：相关新闻/研究链接（不确定就填空字符串 ""）
要求：只列真实存在、广为人知的工具；宁可少列也不要编造。"""


def clean(d):
    """规整一个 disruptor dict，非法/缺失返回 None。"""
    name = (d.get("name") or "").strip()
    summ = (d.get("summary_zh") or "").strip()
    scope = (d.get("scope_zh") or "").strip()
    if not (name and summ and scope):
        return None
    typ = d.get("type") if d.get("type") in TYPES else "tool"
    level = d.get("level") if d.get("level") in LEVELS else "partial"
    mat = d.get("maturity") if d.get("maturity") in MATURITY else "adopted"
    try:
        year = int(d.get("year")) if d.get("year") not in (None, "", 0) else None
        if year and (year < 1990 or year > 2100):
            year = None
    except (TypeError, ValueError):
        year = None
    url = (d.get("url") or "").strip() or None
    ev = (d.get("evidence_url") or "").strip() or None
    return {"name": name[:120], "type": typ, "vendor": (d.get("vendor") or "").strip()[:120] or None,
            "url": url[:300] if url else None, "year": year, "maturity": mat,
            "summary_zh": summ[:400], "level": level, "scope_zh": scope[:400],
            "evidence_url": ev[:300] if ev else None}


def upsert_disruptor(cur, d):
    """工具目录：已存在则保留首版（不覆盖人工/早期数据），返回 id。"""
    cur.execute(
        "INSERT INTO ai_disruptors (name,type,vendor,url,summary_zh,year,maturity) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
        (d["name"], d["type"], d["vendor"], d["url"], d["summary_zh"], d["year"], d["maturity"]))
    cur.execute("SELECT id FROM ai_disruptors WHERE name=%s", (d["name"],))
    return cur.fetchone()["id"]


def save(oid, items):
    with get_cursor() as cur:
        for i, d in enumerate(items, 1):
            did = upsert_disruptor(cur, d)
            cur.execute(
                "INSERT INTO occupation_ai_disruptor "
                "(occupation_id,disruptor_id,replacement_level,scope_zh,evidence_url,sort_order) "
                "VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE "
                "replacement_level=VALUES(replacement_level),scope_zh=VALUES(scope_zh),"
                "evidence_url=VALUES(evidence_url),sort_order=VALUES(sort_order)",
                (oid, did, d["level"], d["scope_zh"], d["evidence_url"], i))


def get_targets(country, redo, limit):
    with get_cursor() as cur:
        cur.execute("SELECT o.id,o.country_code,o.occ_code,o.category,"
                    "i.name AS name_zh, i.summary AS summary_zh, o.anzsco_title AS name_en "
                    "FROM occupations o "
                    "LEFT JOIN occupations_i18n i ON i.occupation_id=o.id AND i.locale='zh-CN' "
                    "ORDER BY o.country_code,o.category,o.id")
        all_occ = cur.fetchall()
        cur.execute("SELECT DISTINCT occupation_id FROM occupation_ai_disruptor")
        have = {r["occupation_id"] for r in cur.fetchall()}
    targets = []
    for o in all_occ:
        if country and o["country_code"] != country:
            continue
        if redo or o["id"] not in have:
            targets.append(o)
    return targets[:limit] if limit else targets


def run(batch_size, rest, country, redo, limit):
    targets = get_targets(country, redo, limit)
    n = len(targets)
    nb = (n + batch_size - 1) // batch_size if batch_size else 1
    print(f"[gen] 待生成 {n} 个职业，分 {nb} 批（每批 {batch_size}，批间休息 {rest}s）model={llm.current_model()}", flush=True)
    done = fail = 0
    for bi in range(nb):
        chunk = targets[bi * batch_size:(bi + 1) * batch_size]
        print(f"\n===== 批次 {bi+1}/{nb}（{len(chunk)} 个）开始 {time.strftime('%H:%M:%S')} =====", flush=True)
        for idx, o in enumerate(chunk, 1):
            prompt = build_prompt(o, o["name_zh"], o["name_en"], o["summary_zh"])
            try:
                items = [c for c in (clean(d) for d in get_disruptors(SYSTEM, prompt)) if c]
                if not items:
                    raise ValueError("无有效工具")
                save(o["id"], items)
            except Exception as e:
                fail += 1
                print(f"  [b{bi+1} {idx}/{len(chunk)}] {o['country_code']}/{o['occ_code']} {o['name_en']} 失败: {e}", flush=True)
                continue
            done += 1
            print(f"  [b{bi+1} {idx}/{len(chunk)}] {o['country_code']}/{o['occ_code']} {o['name_en']} → {len(items)} 个工具: "
                  + ", ".join(f"{x['name']}({x['level']})" for x in items), flush=True)
        print(f"===== 批次 {bi+1}/{nb} 完成（累计 成功{done} 失败{fail}）{time.strftime('%H:%M:%S')} =====", flush=True)
        if bi < nb - 1:
            print(f"[rest] 休息 {rest}s 后继续下一批……", flush=True)
            time.sleep(rest)
    print(f"\n[OK] 全部完成：成功 {done}，失败 {fail}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--rest", type=int, default=1800)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--country", default="")
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    run(a.batch_size, a.rest, a.country.strip().upper(), a.redo, a.limit)
