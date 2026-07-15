"""韩国(KR)职业采集器(v2)：方案 A —— 韩文撰写、英文规范存储。

流程(每个职业)：
  1) DeepSeek 以「韩国の労働市場・ビザ専門家」视角、按 KECO(한국고용직업분류)分类、韩元(KRW)生成**全韩文**职业 JSON
     (category 用 11 个英文大类枚举、数值/代码保持语言中性、内含 AI 暴露块)。
  2) DeepSeek 把其中可读文本**韩译英**(定长数组,按叶子顺序对齐)。
  3) 英文作规范母本写 occupations + *_v2 表(occ_code_type=KECO, currency=KRW)。
  4) 原生韩文按叶子对齐直接挂到 translations_v2 的 ko(键=sha1(英文),与标准 TM 一致),
     从而保留最高保真韩文,后续 translate_v2 --locales ko 只会补漏、不会覆盖。

数据来源(universe)：downloads/kr KECO 세세분류 537 职业(한국고용정보원 KEIS)。

试跑：$env:LLM_PROVIDER="deepseek"; python -m scripts.gen_kr_v2 --limit 10
"""
import sys, os, argparse, time, hashlib, copy, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._seed_helper_v2 import seed_occupation_en
from scripts._i18n_fields_v2 import training_summary_en
from scripts import _deepseek_rest
from video_pipeline import config

UNIVERSE = os.path.join(os.path.dirname(__file__), "..", ".codex_tmp", "keco_universe.json")

CATEGORIES = [
    "Agriculture & Environment", "Business, Finance & Legal", "Creative, Media & Personal Services",
    "Education & Community", "Engineering & Infrastructure", "Government & Public Sector",
    "Healthcare & Care", "Hospitality, Retail & Tourism", "IT & Digital",
    "Trades & Construction", "Transport, Logistics & Mining"]
DIMS = ["learning_difficulty", "learning_duration", "certification_difficulty", "job_demand", "competition",
        "work_intensity", "income_level", "future_prospect", "ai_risk", "pr_friendliness", "pr_difficulty"]

KR = {"name": "South Korea", "currency": "KRW",
      "official": "통계청 인구총조사·경제활동인구조사, 고용노동부 고용형태별근로실태조사(임금), 한국고용정보원 워크넷·KNOW, KOSIS",
      "visa": "E-7(특정활동), E-9(비전문취업), D-2(유학)/D-10(구직), F-2(거주)/F-4(재외동포)/F-5(영주), 지역특화형 비자 등"}


def load_universe():
    """本地 KECO 세세분류码表(한국고용정보원 KEIS 워크넷 직업분류 537 职业)。"""
    return json.load(open(UNIVERSE, encoding="utf-8"))


def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


# ── 1) 韩文生成 ─────────────────────────────────────────────────
def build_system_ko():
    return (
        "당신은 대한민국 노동시장과 체류자격(비자) 제도의 전문가로서, KECO(한국고용직업분류), "
        f"{KR['official']}의 고용·임금 데이터, 체류자격({KR['visa']})에 정통합니다. "
        "주어진 KECO 직업에 대해 현실적이고 구체적인 한국의 데이터를 출력합니다. "
        "급여는 세전 연봉(대한민국 원·정수). 문장은 한국의 일반 독자를 위해 자연스러운 한국어로 작성하세요. "
        f"직업 카테고리는 다음 영어 11종에서 **영어 그대로** 정확히 1개 선택: {'; '.join(CATEGORIES)}. "
        "출력은 단일 JSON 객체만, 그 외 텍스트는 일절 없이."
    )


def build_prompt_ko(code, title_ko, mid_name, major_name):
    dims = ", ".join(DIMS)
    return f"""KECO 직업:
- KECO 코드(세세분류): {code}
- 한국어 명칭: {title_ko}
- 중분류: {mid_name}
- 상위 대분류(KECO): {major_name}

다음 JSON 객체를 반환(모든 필드 필수. 지정 외 문장은 모두 한국어로):
- name: 표준적인 한국어 직업명
- summary: 한 문장 소개(60〜140자)
- forecast_note: 한국에서의 고용 전망(60〜120자, 한 단락)
- trend_summary: 커리어/승진 경로(60〜120자, 한 단락)
- category: 지정된 영어 11개 카테고리 중 1개(**영어 그대로 축자**)
- is_migration: 0/1/2 (0=이민 경로 아님, 1=숙련기능 이민에 적합, 2=제한적. E-7/E-9 등 취업비자 대상 여부 고려)
- shortage: 0 or 1 (인력 부족/고용허가제·E-7 대상 분야인가)
- workforce_size: 한국에서의 취업자 수 정수 추정
- growth: 주목 분야의 한국어 키워드 4개 배열
- education: 2〜3개 배열 {{stage, duration(예 "3년"), cost_min(정수 KRW), cost_max(정수 KRW), cost_note}}
- qualifications: 2〜4개 {{qual_name, issuer, note, is_mandatory(0/1)}}
- salaries: 정확히 3개 {{experience(예 "초급(0〜3년)"), salary_min(정수 KRW 연봉), salary_max(정수 KRW 연봉), salary_note}}
- visa: 2〜4개 {{visa_subclass(짧은 코드/명칭. 예 "E-7"/"E-9"/"F-2"), visa_name, description}}
- ratings: 다음 11개 차원을 키로 하는 객체: {dims}. 각 값 = [한국어 라벨, 점수]이며 점수 = 1.0〜10.0(소수 1자리).
  네거티브 차원(ai_risk, competition, work_intensity, learning_difficulty, learning_duration, certification_difficulty, pr_difficulty)은 높을수록 불리.
- fit: 적합한 사람의 한국어 2〜3개 배열
- unfit: 부적합한 사람의 한국어 2개 배열
- faqs: 2〜3개 {{faq_type("salary"/"migration"/...), question, answer}}(급여 1건과 비자 1건 포함)
- ai: {{ verdict_type("compressed"=AI로 축소/대체 진행 / "amplified"=AI로 확장·강화 / "mixed"=혼재), verdict(한국어 한 단락·AI/자동화의 영향),
        entry_narrowing(한국어·신입 채용에의 영향), upgrade_path(한국어·생존/강화 경로),
        replaced(한국어 배열·AI로 대체되기 쉬운 업무), augmented(한국어 배열·AI로 강화되는 업무),
        moat(한국어 배열·인간의 해자), skills(한국어 배열·키워야 할 스킬),
        cluster("ai_augmented"/"ai_exposed"/"ai_safe"), automation_exposure(0.0〜10.0),
        human_moat(0.0〜10.0), entry_risk(0.0〜10.0), ai_upside(0.0〜10.0) }}
불확실하면 보수적인 범위로. 현실적인 한국 데이터만."""


# ── 叶子文本对齐(英/韩按同序替换) ───────────────────────────────
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


# ── 2) 韩译英(定长数组) ─────────────────────────────────────────
def _tr_system():
    return (
        "You are a professional KO->EN localization translator for an international careers/occupations "
        "website. Translate each given Korean string into natural, idiomatic English. Return translations "
        "in the SAME order and count as a JSON object {\"t\":[...]}.\n"
        "Rules: keep numbers, ranges, percentages and currency (KRW/₩) intact; keep proper nouns, "
        "classification codes and Korean visa/residence status names sensible in English "
        "(e.g. E-7 특정활동 -> 'E-7 (Specific Activities)', E-9 비전문취업 -> 'E-9 (Non-professional "
        "Employment)', F-2 거주 -> 'F-2 (Residence)', F-5 영주 -> 'F-5 (Permanent Residence)'); concise, "
        "roughly the same length; output English only."
    )


def _tr_call(texts):
    import json as _json
    out = _deepseek_rest.complete_json(_tr_system(),
        "Translate these Korean strings and return {\"t\":[...]} with EXACTLY the same length and order. "
        "Never split, merge, add or drop items:\n" + _json.dumps(texts, ensure_ascii=False))
    res = out.get("t") or []
    if len(res) != len(texts):
        raise ValueError(f"len {len(texts)}->{len(res)}")
    return res


def translate_ko_to_en(texts, chunk=25):
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


DEC_MAX = 99999999  # decimal(10,2) 上限。韩元大额薪资/学费 clamp 以防溢出(억대高端会被截,罕见)。


def _clamp(v):
    if v is None:
        return None
    try:
        return min(int(round(float(v))), DEC_MAX)
    except (TypeError, ValueError):
        return None


def to_seed(code, v):
    OCC = {"country_code": "KR", "occ_code": code, "occ_code_type": "KECO", "anzsco_code": code,
           "anzsco_title": v["name"], "category": v["category"], "currency": KR["currency"],
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
          "aioe_soc": None, "aioe_method": "llm_kr"} if aiv else None
    return OCC, TEXT, EDU, QUAL, SAL, VISA, RAT, v["fit"], v["unfit"], FAQS, AI


def inject_ko(cur, en_obj, ko_obj):
    """把原生韩文按叶子对齐挂到 ko(键=sha1(英文))。含派生 training 摘要。"""
    en_leaves = collect_leaves(en_obj)
    ko_leaves = collect_leaves(ko_obj)
    pairs = []  # (en_text, ko_text)
    for en, ko in zip(en_leaves, ko_leaves):
        if en and str(en).strip() and ko and str(ko).strip():
            pairs.append((str(en), str(ko)))
    ten = training_summary_en(en_obj["education"])
    tko = training_summary_en(ko_obj["education"])
    if ten and tko:
        pairs.append((ten, tko))
    src_rows = [(sha1(en), en) for en, _ in pairs]
    tr_rows = [(sha1(en), "ko", ko, f"deepseek-kr:{config.DEEPSEEK_MODEL}") for en, ko in pairs]
    cur.executemany("INSERT INTO translation_src_v2 (src_hash,src_text) VALUES (%s,%s) "
                    "ON DUPLICATE KEY UPDATE src_text=VALUES(src_text)", src_rows)
    cur.executemany("INSERT INTO translations_v2 (src_hash,locale,text,gen_model) VALUES (%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE text=VALUES(text),gen_model=VALUES(gen_model)", tr_rows)
    return len(pairs)


def run(limit, offset, rest, resume, codes):
    uni = load_universe()
    if codes:
        want = set(codes)
        uni = [u for u in uni if u["keco"] in want]
    if resume:
        with get_cursor() as cur:
            cur.execute("SELECT occ_code FROM occupations WHERE country_code='KR'")
            done = {r["occ_code"] for r in cur.fetchall()}
        uni = [u for u in uni if u["keco"] not in done]
    if offset:
        uni = uni[offset:]
    targets = uni[:limit] if limit else uni
    system_ko = build_system_ko()
    print(f"[KR] 待生成 {len(targets)} (KECO, currency=KRW, resume={resume}) model={config.DEEPSEEK_MODEL}", flush=True)
    okc = fail = 0
    for idx, u in enumerate(targets, 1):
        code, title_ko = u["keco"], u["title_ko"]
        mid_name, major_name = u.get("mid_name", ""), u.get("major_name", "")
        tag = f"{idx}/{len(targets)} {code} {title_ko}"
        last = None
        for attempt in (1, 2):  # 一次重试,吸收瞬时 503/JSON/校验抖动
            try:
                ko_obj = validate(_deepseek_rest.complete_json(system_ko, build_prompt_ko(code, title_ko, mid_name, major_name)))
                # 韩译英作规范母本
                leaves = collect_leaves(ko_obj)
                idxs = [i for i, s in enumerate(leaves) if s and str(s).strip()]
                en_vals = translate_ko_to_en([leaves[i] for i in idxs])
                merged = list(leaves)
                for j, i in enumerate(idxs):
                    merged[i] = en_vals[j]
                en_obj = apply_leaves(copy.deepcopy(ko_obj), merged)
                en_obj["category"] = ko_obj["category"]  # 已是英文枚举
                en_obj = validate(en_obj)
                with get_cursor() as cur:
                    occ_id = seed_occupation_en(cur, *to_seed(code, en_obj))
                    nko = inject_ko(cur, en_obj, ko_obj)
                okc += 1
                print(f"  [{tag}] -> KR id={occ_id} {en_obj['name']} [{en_obj['category']}] "
                      f"exp={(en_obj.get('ai') or {}).get('automation_exposure')} ko挂{nko}串", flush=True)
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
    print(f"[KR] 完成：成功 {okc}，失败 {fail}", flush=True)


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
