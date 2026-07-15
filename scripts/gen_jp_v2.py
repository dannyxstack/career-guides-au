"""日本(JP)职业采集器(v2)：方案 A —— 日文撰写、英文规范存储。

流程(每个职业)：
  1) DeepSeek 以「日本の労働市場・移民専門家」视角、按 JSCO 分类、日元(JPY)生成**全日文**职业 JSON
     (category 用 11 个英文大类枚举、数值/代码保持语言中性、内含 AI 暴露块)。
  2) DeepSeek 把其中可读文本**日译英**(定长数组,按叶子顺序对齐)。
  3) 英文作规范母本写 occupations + *_v2 表(occ_code_type=JSCO, currency=JPY)。
  4) 原生日文按叶子对齐直接挂到 translations_v2 的 ja(键=sha1(英文),与标准 TM 一致),
     从而保留最高保真日文,后续 translate_v2 --locales ja 只会补漏、不会覆盖。

试跑：$env:LLM_PROVIDER="deepseek"; python -m scripts.gen_jp_v2 --limit 10
"""
import sys, os, argparse, time, hashlib, copy, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper_v2 import seed_occupation_en
from scripts._i18n_fields_v2 import training_summary_en
from scripts import _deepseek_rest
from video_pipeline import config

UNIVERSE = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "jsco_universe.json")

CATEGORIES = [
    "Agriculture & Environment", "Business, Finance & Legal", "Creative, Media & Personal Services",
    "Education & Community", "Engineering & Infrastructure", "Government & Public Sector",
    "Healthcare & Care", "Hospitality, Retail & Tourism", "IT & Digital",
    "Trades & Construction", "Transport, Logistics & Mining"]
DIMS = ["learning_difficulty", "learning_duration", "certification_difficulty", "job_demand", "competition",
        "work_intensity", "income_level", "future_prospect", "ai_risk", "pr_friendliness", "pr_difficulty"]

JP = {"name": "Japan", "currency": "JPY",
      "official": "総務省統計局 国勢調査・労働力調査、厚生労働省 賃金構造基本統計調査(賃金センサス)、e-Stat",
      "visa": "特定技能(SSW 1号/2号)、技術・人文知識・国際業務、高度専門職、介護、技能、経営・管理 等"}

def load_universe():
    """本地 JSCO 小分類码表(总务省 日本標準職業分類 平成21 解析)。"""
    return json.load(open(UNIVERSE, encoding="utf-8"))


def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


# ── 1) 日文生成 ─────────────────────────────────────────────────
def build_system_ja():
    return (
        "あなたは日本の労働市場・在留資格(ビザ)制度の専門家であり、JSCO(日本標準職業分類)、"
        f"{JP['official']} の雇用・賃金データ、在留資格({JP['visa']})に精通しています。"
        "与えられた JSCO 職業について、現実的で具体的な日本のデータを出力します。"
        "給与は税引き前の年収(日本円・整数)。文章は日本の一般読者向けに自然な日本語で書いてください。"
        f"職業カテゴリは次の英語 11 種から**英語のまま**厳密に 1 つ選ぶ: {'; '.join(CATEGORIES)}。"
        "出力は単一の JSON オブジェクトのみ、余計なテキストは一切なし。"
    )


def build_prompt_ja(code, title_ja, major_name):
    dims = ", ".join(DIMS)
    return f"""JSCO 職業:
- JSCO コード(小分類): {code}
- 日本語名称: {title_ja}
- 上位分類(JSCO 大分類): {major_name}

次の JSON オブジェクトを返す(全フィールド必須。指定以外の文章はすべて日本語で):
- name: 標準的な日本語の職業名
- summary: 一文の紹介(60〜140 文字)
- forecast_note: 日本での雇用見通し(60〜120 文字、一段落)
- trend_summary: キャリア/昇進の道筋(60〜120 文字、一段落)
- category: 指定の英語 11 カテゴリから 1 つ(**英語のまま逐語**)
- is_migration: 0/1/2 (0=移民ルートでない, 1=技能移民に向く, 2=制限的。特定技能・技人国の対象可否を考慮)
- shortage: 0 or 1 (人手不足/特定技能の対象分野か)
- workforce_size: 日本での就業者数の整数推計
- growth: 注目分野の日本語キーワード 4 個の配列
- education: 2〜3 個の配列 {{stage, duration(例 "3年"), cost_min(整数 JPY), cost_max(整数 JPY), cost_note}}
- qualifications: 2〜4 個 {{qual_name, issuer, note, is_mandatory(0/1)}}
- salaries: ちょうど 3 個 {{experience(例 "初級(0〜3年)"), salary_min(整数 JPY), salary_max(整数 JPY), salary_note}}
- visa: 2〜4 個 {{visa_subclass(短いコード/名称。例 "特定技能1号"/"技人国"), visa_name, description}}
- ratings: 次の 11 次元をキーとするオブジェクト: {dims}。各値 = [日本語ラベル, スコア] でスコアは 1.0〜10.0(小数1桁)。
  ネガティブ次元(ai_risk, competition, work_intensity, learning_difficulty, learning_duration, certification_difficulty, pr_difficulty)は高いほど不利。
- fit: 向いている人の日本語 2〜3 個の配列
- unfit: 向かない人の日本語 2 個の配列
- faqs: 2〜3 個 {{faq_type("salary"/"migration"/...), question, answer}}(給与 1 件とビザ 1 件を含む)
- ai: {{ verdict_type("compressed"=AIで縮小/代替が進む / "amplified"=AIで拡張・強化される / "mixed"=混在), verdict(日本語一段落・AI/自動化の影響),
        entry_narrowing(日本語・新人枠への影響), upgrade_path(日本語・生き残り/強化の道),
        replaced(日本語配列・AI に代替されやすい業務), augmented(日本語配列・AI で強化される業務),
        moat(日本語配列・人間の堀), skills(日本語配列・伸ばすべきスキル),
        cluster("ai_augmented"/"ai_exposed"/"ai_safe"), automation_exposure(0.0〜10.0),
        human_moat(0.0〜10.0), entry_risk(0.0〜10.0), ai_upside(0.0〜10.0) }}
不確かな場合は保守的な範囲で。現実的な日本のデータのみ。"""


# ── 叶子文本对齐(英/日按同序替换) ───────────────────────────────
def collect_leaves(o):
    """返回可翻译文本叶子(固定顺序)。数值/代码/category 不在内。"""
    L = [o["name"], o["summary"], o["forecast_note"], o["trend_summary"]]
    for e in o["education"]:
        L += [e.get("stage"), e.get("duration"), e.get("cost_note")]
    for q in o["qualifications"]:
        L += [q.get("qual_name"), q.get("issuer"), q.get("note")]
    for s in o["salaries"]:
        L += [s.get("experience"), s.get("salary_note")]
    for v in o["visa"]:
        L += [v.get("visa_name"), v.get("description")]
    for d in DIMS:
        L.append(o["ratings"][d][0])
    L += list(o["fit"]) + list(o["unfit"])
    for f in o["faqs"]:
        L += [f.get("question"), f.get("answer")]
    L += list(o.get("growth") or [])
    ai = o.get("ai") or {}
    L += [ai.get("verdict"), ai.get("entry_narrowing"), ai.get("upgrade_path")]
    for key in ("replaced", "augmented", "moat", "skills"):
        L += list(ai.get(key) or [])
    return L


def apply_leaves(o, vals):
    """把 vals(与 collect_leaves 同序)写回 o 的对应叶子。"""
    it = iter(vals)
    def nx(): return next(it)
    o["name"], o["summary"], o["forecast_note"], o["trend_summary"] = nx(), nx(), nx(), nx()
    for e in o["education"]:
        e["stage"], e["duration"], e["cost_note"] = nx(), nx(), nx()
    for q in o["qualifications"]:
        q["qual_name"], q["issuer"], q["note"] = nx(), nx(), nx()
    for s in o["salaries"]:
        s["experience"], s["salary_note"] = nx(), nx()
    for v in o["visa"]:
        v["visa_name"], v["description"] = nx(), nx()
    for d in DIMS:
        o["ratings"][d][0] = nx()
    o["fit"] = [nx() for _ in o["fit"]]
    o["unfit"] = [nx() for _ in o["unfit"]]
    for f in o["faqs"]:
        f["question"], f["answer"] = nx(), nx()
    o["growth"] = [nx() for _ in (o.get("growth") or [])]
    ai = o.get("ai") or {}
    ai["verdict"], ai["entry_narrowing"], ai["upgrade_path"] = nx(), nx(), nx()
    for key in ("replaced", "augmented", "moat", "skills"):
        ai[key] = [nx() for _ in (ai.get(key) or [])]
    return o


# ── 2) 日译英(定长数组) ─────────────────────────────────────────
def _tr_system():
    return (
        "You are a professional JA->EN localization translator for an international careers/occupations "
        "website. Translate each given Japanese string into natural, idiomatic English. Return translations "
        "in the SAME order and count as a JSON object {\"t\":[...]}.\n"
        "Rules: keep numbers, ranges, percentages and currency (JPY/¥) intact; keep proper nouns, "
        "classification codes and Japanese visa/residence status names sensible in English "
        "(e.g. 特定技能1号 -> 'Specified Skilled Worker (i)', 技人国 -> 'Engineer/Specialist in Humanities/"
        "International Services'); concise, roughly the same length; output English only."
    )


def _tr_call(texts):
    import json as _json
    out = _deepseek_rest.complete_json(_tr_system(),
        "Translate these Japanese strings and return {\"t\":[...]} with EXACTLY the same length and order. "
        "Never split, merge, add or drop items:\n" + _json.dumps(texts, ensure_ascii=False))
    res = out.get("t") or []
    if len(res) != len(texts):
        raise ValueError(f"len {len(texts)}->{len(res)}")
    return res


def translate_ja_to_en(texts, chunk=25):
    """分块翻译；整块长度漂移时对该块逐条重试,保证与输入等长对齐。"""
    if not texts:
        return []
    res = []
    for i in range(0, len(texts), chunk):
        part = texts[i:i + chunk]
        try:
            res += _tr_call(part)
        except Exception:
            for tx in part:  # 逐条：单串不会与自身错位
                try:
                    res.append(_tr_call([tx])[0])
                except Exception:
                    res.append(tx)  # 兜底保留原文,长度不塌
    if len(res) != len(texts):
        raise ValueError(f"翻译长度不匹配 expect {len(texts)} got {len(res)}")
    return res


# ── validate / to_seed ─────────────────────────────────────────
def validate(v):
    need = ["name", "summary", "forecast_note", "trend_summary", "category", "education", "qualifications",
            "salaries", "visa", "ratings", "fit", "unfit", "faqs"]
    for k in need:
        if k not in v or v[k] in (None, "", []):
            raise ValueError(f"缺字段 {k}")
    if v["category"] not in CATEGORIES:
        raise ValueError(f"非法 category: {v['category']}")
    # 列表字段元素必须是 dict(模型偶把元素返成字符串)
    for k in ("education", "qualifications", "salaries", "visa", "faqs"):
        if not isinstance(v[k], list) or not all(isinstance(x, dict) for x in v[k]):
            raise ValueError(f"{k} 元素非 dict")
    if not isinstance(v["ratings"], dict):
        raise ValueError("ratings 非对象")
    for d in DIMS:
        r = v["ratings"].get(d)
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            raise ValueError(f"ratings[{d}] 结构错")
    return v


DEC_MAX = 99999999  # decimal(10,2) 上限(≈1億)。日元大额薪资/学费 clamp 以防溢出。


def _clamp(v):
    if v is None:
        return None
    try:
        return min(int(round(float(v))), DEC_MAX)
    except (TypeError, ValueError):
        return None


def to_seed(code, v):
    OCC = {"country_code": "JP", "occ_code": code, "occ_code_type": "JSCO", "anzsco_code": code,
           "anzsco_title": v["name"], "category": v["category"], "currency": JP["currency"],
           "workforce_size": v.get("workforce_size"), "shortage_listed": int(v.get("shortage", 0)),
           "is_migration": int(v.get("is_migration", 1)), "is_public_servant": 0,
           "growth_areas": v.get("growth", [])}
    TEXT = {"name": v["name"], "summary": v["summary"], "forecast_note": v["forecast_note"],
            "trend_summary": v["trend_summary"]}
    EDU = [{"stage": e["stage"], "duration": e.get("duration"), "cost_min": _clamp(e.get("cost_min")),
            "cost_max": _clamp(e.get("cost_max")), "cost_note": e.get("cost_note")} for e in v["education"]]
    QUAL = [{"qual_name": q["qual_name"], "issuer": q.get("issuer"), "note": q.get("note"),
             "is_mandatory": int(q.get("is_mandatory", 1))} for q in v["qualifications"]]
    SAL = [{"experience": s["experience"], "salary_min": _clamp(s.get("salary_min")),
            "salary_max": _clamp(s.get("salary_max")), "salary_note": s.get("salary_note")} for s in v["salaries"]]
    VISA = [{"visa_subclass": str(x["visa_subclass"])[:40], "visa_name": x.get("visa_name"),
             "description": x.get("description")} for x in v["visa"]]
    RAT = [{"dimension": d, "label": v["ratings"][d][0], "stars": float(v["ratings"][d][1])} for d in DIMS]
    FAQS = [{"faq_type": f.get("faq_type"), "question": f["question"], "answer": f["answer"]} for f in v["faqs"]]
    aiv = v.get("ai") or {}
    VT = {"compressed": "compressed", "amplified": "amplified", "mixed": "mixed",
          "augment": "amplified", "augmented": "amplified", "replace": "compressed",
          "replaced": "compressed", "safe": "mixed"}
    vt = VT.get(str(aiv.get("verdict_type", "mixed")).strip().lower(), "mixed")
    AI = {"verdict_type": vt, "verdict": aiv.get("verdict"),
          "entry_narrowing": aiv.get("entry_narrowing"), "upgrade_path": aiv.get("upgrade_path"),
          "replaced": aiv.get("replaced", []), "augmented": aiv.get("augmented", []),
          "moat": aiv.get("moat", []), "skills": aiv.get("skills", []), "adjacent": [],
          "cluster": aiv.get("cluster"), "automation_exposure": aiv.get("automation_exposure"),
          "human_moat": aiv.get("human_moat"), "entry_risk": aiv.get("entry_risk"),
          "ai_upside": aiv.get("ai_upside"), "aioe_score": None, "aioe_pct": None,
          "aioe_soc": None, "aioe_method": "llm_jp"} if aiv else None
    return OCC, TEXT, EDU, QUAL, SAL, VISA, RAT, v["fit"], v["unfit"], FAQS, AI


def inject_ja(cur, en_obj, ja_obj):
    """把原生日文按叶子对齐挂到 ja(键=sha1(英文))。含派生 training 摘要。"""
    en_leaves = collect_leaves(en_obj)
    ja_leaves = collect_leaves(ja_obj)
    pairs = []  # (en_text, ja_text)
    for en, ja in zip(en_leaves, ja_leaves):
        if en and str(en).strip() and ja and str(ja).strip():
            pairs.append((str(en), str(ja)))
    # 派生 training 摘要(export/collect 会产出该英文串)
    ten = training_summary_en(en_obj["education"])
    tja = training_summary_en(ja_obj["education"])
    if ten and tja:
        pairs.append((ten, tja))
    src_rows = [(sha1(en), en) for en, _ in pairs]
    tr_rows = [(sha1(en), "ja", ja, f"deepseek-jp:{config.DEEPSEEK_MODEL}") for en, ja in pairs]
    cur.executemany("INSERT INTO translation_src_v2 (src_hash,src_text) VALUES (%s,%s) "
                    "ON DUPLICATE KEY UPDATE src_text=VALUES(src_text)", src_rows)
    cur.executemany("INSERT INTO translations_v2 (src_hash,locale,text,gen_model) VALUES (%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE text=VALUES(text),gen_model=VALUES(gen_model)", tr_rows)
    return len(pairs)


def run(limit, offset, rest, resume, codes):
    uni = load_universe()
    if codes:
        want = set(codes)
        uni = [u for u in uni if u["jsco"] in want]
    if resume:
        with get_cursor() as cur:
            cur.execute("SELECT occ_code FROM occupations WHERE country_code='JP'")
            done = {r["occ_code"] for r in cur.fetchall()}
        uni = [u for u in uni if u["jsco"] not in done]
    if offset:
        uni = uni[offset:]
    targets = uni[:limit] if limit else uni
    system_ja = build_system_ja()
    print(f"[JP] 待生成 {len(targets)} (JSCO, currency=JPY, resume={resume}) model={config.DEEPSEEK_MODEL}", flush=True)
    okc = fail = 0
    for idx, u in enumerate(targets, 1):
        code, title_ja, major_name = u["jsco"], u["title_ja"], u.get("major_name", "")
        tag = f"{idx}/{len(targets)} {code} {title_ja}"
        last = None
        for attempt in (1, 2):  # 一次重试,吸收瞬时 503/JSON/校验抖动
            try:
                ja_obj = validate(_deepseek_rest.complete_json(system_ja, build_prompt_ja(code, title_ja, major_name)))
                # 日译英作规范母本
                leaves = collect_leaves(ja_obj)
                idxs = [i for i, s in enumerate(leaves) if s and str(s).strip()]
                en_vals = translate_ja_to_en([leaves[i] for i in idxs])
                merged = list(leaves)
                for j, i in enumerate(idxs):
                    merged[i] = en_vals[j]
                en_obj = apply_leaves(copy.deepcopy(ja_obj), merged)
                en_obj["category"] = ja_obj["category"]  # 已是英文枚举
                en_obj = validate(en_obj)
                with get_cursor() as cur:
                    occ_id = seed_occupation_en(cur, *to_seed(code, en_obj))
                    nja = inject_ja(cur, en_obj, ja_obj)
                okc += 1
                print(f"  [{tag}] -> JP id={occ_id} {en_obj['name']} [{en_obj['category']}] "
                      f"exp={(en_obj.get('ai') or {}).get('automation_exposure')} ja挂{nja}串", flush=True)
                last = None
                break
            except Exception as e:
                last = e
                if attempt == 1:
                    time.sleep(2)
        if last is not None:
            fail += 1
            print(f"  [{tag}] 失败: {last}", flush=True)
        if rest and idx < len(targets):
            time.sleep(rest)
    print(f"[JP] 完成：成功 {okc}，失败 {fail}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--rest", type=int, default=0)
    ap.add_argument("--codes", default="")
    ap.add_argument("--no-resume", dest="resume", action="store_false")
    ap.set_defaults(resume=True)
    a = ap.parse_args()
    run(a.limit, a.offset, a.rest, a.resume, [c.strip() for c in a.codes.split(",") if c.strip()])
