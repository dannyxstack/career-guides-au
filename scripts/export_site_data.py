"""导出职业数据为 JSON，供 Astro 站点构建期消费（site/src/data/occupations.json）。
复用 DB 为唯一数据源；多语言/多国家通过 country + i18n 表表达。"""
import sys, os, json, re, hashlib, glob
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._i18n_fields import fetch_bundles, collect_from_bundle, needs_translation

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "src", "data")
HOT_N = 16  # 首页「热门职业搜索」标签数

# 评分维度极性：负向（越高越差）算综合分时反转
POLARITY = {"income_level": 1, "job_demand": 1, "future_prospect": 1, "pr_friendliness": 1,
            "ai_risk": -1, "learning_difficulty": -1, "learning_duration": -1,
            "certification_difficulty": -1, "competition": -1, "work_intensity": -1, "pr_difficulty": -1}
DIM_ZH = {"learning_difficulty": "学习难度", "learning_duration": "学习周期", "certification_difficulty": "考证难度",
          "job_demand": "职位需求量", "competition": "竞争度", "work_intensity": "工作强度", "income_level": "收入水平",
          "future_prospect": "发展前景", "ai_risk": "AI替代风险", "pr_friendliness": "PR友好度", "pr_difficulty": "PR难度"}


def slug(name):
    s = re.sub(r"[/()\[\]]", " ", (name or "occ").lower())
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", "-", s.strip()) or "occ"


def overall_score(ratings):
    vals = []
    for r in ratings:
        if r["stars"] is None:
            continue
        s = float(r["stars"])  # 10 分制
        vals.append(12 - s if POLARITY.get(r["dimension"], 1) < 0 else s)
    return round(sum(vals) / len(vals), 1) if vals else None


def build():
    with get_cursor() as cur:
        bundles = fetch_bundles(cur)
        # 各职业签证最低获邀分：{occupation_id: {subclass: {min_score, asof, note}}}
        inv = {}
        try:
            cur.execute("SELECT occupation_id, visa_subclass, min_score, asof, note FROM occupation_invitation_scores")
            for r in cur.fetchall():
                inv.setdefault(r["occupation_id"], {})[r["visa_subclass"]] = {
                    "min_score": r["min_score"], "asof": r["asof"], "note": r["note"]}
        except Exception as e:
            print(f"[export] 警告：读取 invitation_scores 失败（{e}），跳过获邀分")
        # 社区投票聚合：{occ_key(slug): {poll_code: {counts:{answer_key:cnt}, total}}}，供构建期烘焙首屏
        poll_by_key = {}
        try:
            cur.execute("SELECT poll_code, occ_key, answer_key, cnt FROM poll_agg")
            for r in cur.fetchall():
                p = poll_by_key.setdefault(r["occ_key"], {}).setdefault(r["poll_code"], {"counts": {}, "total": 0})
                p["counts"][r["answer_key"]] = r["cnt"]
                p["total"] += r["cnt"]
        except Exception as e:
            print(f"[export] 警告：读取 poll_agg 失败（{e}），跳过投票烘焙")
        # 热门职业热度：{(country, slug): hits+seed_score}，供首页「热门职业搜索」板块
        hot_score = {}
        try:
            cur.execute("SELECT country_code, slug, (hits + seed_score) AS score FROM occ_search_hits")
            for r in cur.fetchall():
                hot_score[(r["country_code"], r["slug"])] = int(r["score"])
        except Exception as e:
            print(f"[export] 警告：读取 occ_search_hits 失败（{e}），跳过热门职业")
        out = []
        for b in bundles:
            o = b["o"]
            z = b["i18n_zh"]
            en_name = (b["i18n"].get("en") or {}).get("name") or o["anzsco_title"]
            sg = slug(en_name)
            ratings = [{"dimension": r["dimension"], "label_zh": r["label_zh"],
                        "stars": r["stars"], "name_zh": DIM_ZH.get(r["dimension"], r["dimension"])}
                       for r in b["ratings"]]
            out.append({
                "id": b["id"], "country": o["country_code"], "occ_code": o["occ_code"],
                "occ_code_type": o["occ_code_type"], "anzsco_code": o["anzsco_code"],
                "category": o["category"], "currency": o.get("currency") or "AUD",
                "is_migration": int(o["is_migration"] or 0),  # 0=非移民 1=可直接技术移民 2=受限
                "is_public_servant": bool(o.get("is_public_servant")),
                "shortage_listed": bool(o["shortage_listed"]), "workforce_size": o["workforce_size"],
                "slug": sg, "name_en": en_name, "growth_areas": b["growth"],
                "polls": poll_by_key.get(sg) or None,
                # i18n 仅保留中文母本，其余语言前端经 tr() 解析
                "i18n": {"zh-CN": {"name": z.get("name"), "summary": z.get("summary"),
                                   "forecast_note": z.get("forecast_note"), "trend_summary": z.get("trend_summary")}},
                "training_zh": b["training_zh"],
                "salaries": [{"label": s["label"], "min": s["min"], "max": s["max"], "note": s["note"]} for s in b["salaries"]],
                "ratings": ratings, "overall_score": overall_score(ratings),
                # 官方平均薪资（band='mean' 行，label=平均薪资），供 risk map 弹层等展示
                "avg_salary": next((s["min"] for s in b["salaries"] if s["label"] == "平均薪资"), None),
                "visa": [{**v, **({"min_score": inv[b["id"]][v["subclass"]]["min_score"],
                                   "score_asof": inv[b["id"]][v["subclass"]]["asof"]}
                                  if inv.get(b["id"], {}).get(v["subclass"]) else {})}
                         for v in b["visa"]],
                "education": b["education"], "qualifications": b["qualifications"],
                "suitability": {"fit": b["suitability_fit"], "unfit": b["suitability_unfit"]},
                "faqs": [{"type": f["type"], "question": f["question"], "answer": f["answer"]} for f in b["faqs"]],
                "ai": b.get("ai"),
            })

        # 相邻职业：把 ai.adjacent 的 occ_code 解析为同国 {slug,name_en,category}
        code_map = {(o["country"], o["occ_code"]): o for o in out}
        for o in out:
            ai = o.get("ai")
            if not ai:
                continue
            links = []
            for code in (ai.get("adjacent") or []):
                tgt = code_map.get((o["country"], code))
                if tgt:
                    links.append({"slug": tgt["slug"], "name_en": tgt["name_en"], "category": tgt["category"]})
            ai["adjacent"] = links

        # 「也影响」跨职业链接：同一工具(disruptor_id)挂在同国其它职业上
        dis_occ = {}  # (country, disruptor_id) -> [occ,...]
        for o in out:
            for d in (o.get("ai") or {}).get("disruptors", []):
                dis_occ.setdefault((o["country"], d["id"]), []).append(o)
        for o in out:
            for d in (o.get("ai") or {}).get("disruptors", []):
                d["also"] = [{"slug": x["slug"], "name_en": x["name_en"], "category": x["category"]}
                             for x in dis_occ.get((o["country"], d["id"]), []) if x["id"] != o["id"]]
                d.pop("id", None)

        # 热门职业 top-N：按热度降序 + 分散（限每国/每类占比），标签各带国旗
        ranked = sorted(
            [o for o in out if hot_score.get((o["country"], o["slug"]))],
            key=lambda o: hot_score[(o["country"], o["slug"])], reverse=True)
        hot_list = []
        for cap_c, cap_cat in ((2, 2), (3, 3), (99, 99)):  # 逐步放宽直到凑够
            if len(hot_list) >= HOT_N:
                break
            per_country, per_cat = {}, {}
            for o in hot_list:  # 复算已选计数
                per_country[o["country"]] = per_country.get(o["country"], 0) + 1
                per_cat[o["category"]] = per_cat.get(o["category"], 0) + 1
            picked = {(o["country"], o["slug"]) for o in hot_list}
            for o in ranked:
                if len(hot_list) >= HOT_N:
                    break
                key = (o["country"], o["slug"])
                if key in picked:
                    continue
                if per_country.get(o["country"], 0) >= cap_c or per_cat.get(o["category"], 0) >= cap_cat:
                    continue
                hot_list.append({"country": o["country"], "slug": o["slug"],
                                 "cat": o["category"], "name_en": o["name_en"]})
                picked.add(key)
                per_country[o["country"]] = per_country.get(o["country"], 0) + 1
                per_cat[o["category"]] = per_cat.get(o["category"], 0) + 1

        # 翻译记忆：{src_text: {locale: text}}，只导出实际存在的源串
        tr = {}
        try:
            cur.execute("SELECT s.src_text, t.locale, t.text FROM translations t JOIN translation_src s ON s.src_hash=t.src_hash")
            for r in cur.fetchall():
                tr.setdefault(r["src_text"], {})[r["locale"]] = r["text"]
        except Exception as e:
            print(f"[export] 警告：读取 translations 失败（{e}），仅导出中文母本")

    os.makedirs(OUT, exist_ok=True)
    payload = {"generated_at": str(date.today()), "count": len(out), "occupations": out}
    path = os.path.join(OUT, "occupations.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, default=str)
    # 热门职业（首页板块）
    with open(os.path.join(OUT, "hot_occupations.json"), "w", encoding="utf-8") as f:
        json.dump(hot_list, f, ensure_ascii=False)
    # 翻译记忆按语言 + 分片导出：{src_text:{locale:text}} -> data/translations/{loc}.{i}.json
    # （单文件 9 语言 ~195MB 超 GitHub 100MB 上限；按 locale 拆后 th 仍达 ~51MB 触发 50MB 软警告，
    #  故再按 md5(源串)%N_TR_SHARDS 分片，各片 <7MB。data.ts 用 import.meta.glob 合并加载）
    N_TR_SHARDS = 8
    tr_dir = os.path.join(OUT, "translations")
    os.makedirs(tr_dir, exist_ok=True)
    for old in glob.glob(os.path.join(tr_dir, "*.json")):  # 清空旧分片避免残留
        os.remove(old)
    by_locale: dict = {}
    for src, locs in tr.items():
        for loc, text in locs.items():
            by_locale.setdefault(loc, {})[src] = text
    for loc, mp in by_locale.items():
        shards = [dict() for _ in range(N_TR_SHARDS)]
        for src, text in mp.items():
            h = int(hashlib.md5(src.encode("utf-8")).hexdigest(), 16) % N_TR_SHARDS
            shards[h][src] = text
        for i, sh in enumerate(shards):
            with open(os.path.join(tr_dir, f"{loc}.{i}.json"), "w", encoding="utf-8") as f:
                json.dump(sh, f, ensure_ascii=False, default=str)
    # 分类清单
    cats = sorted({o["category"] for o in out if o["category"]})
    with open(os.path.join(OUT, "categories.json"), "w", encoding="utf-8") as f:
        json.dump({"category_slug": {c: slug(c) for c in cats}, "categories": cats}, f, ensure_ascii=False)
    print(f"[export] {len(out)} occupations -> {path}")
    print(f"[export] {len(tr)} 源串带译文 -> translations.<locale>.json × {len(by_locale)}")
    print(f"[export] {len(cats)} categories")
    print(f"[export] {len(hot_list)} hot occupations -> hot_occupations.json")


if __name__ == "__main__":
    build()
