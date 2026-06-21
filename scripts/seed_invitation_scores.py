"""按职业大类填充 190/491 的「2025–26 竞争性参考获邀分」到 occupation_invitation_scores。

重要口径：190/491 获邀分由各州自定、按州不同，没有统一的「全国每职业最低分」。
此处按大类给出 2025–26 竞争性参考值（来自各州/SkillSelect 公布区间），仅供参考，
精确的逐职业/逐州数据由后续定时任务覆盖更新。189 为全国按职业公布，本脚本不填(留待定时任务)。

仅对 is_migration=1 且其 visa 路径含 190/491 的 AU 职业写入。幂等(ON DUPLICATE KEY UPDATE)。
运行：python -m scripts.seed_invitation_scores
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

ASOF = "2025–26"
NOTE = "按大类竞争性参考，各州不同，以各州官方最新结果为准"
SRC = "https://immi.homeaffairs.gov.au/visas/working-in-australia/skillselect/invitation-rounds"

# 大类 -> (190 参考分, 491 参考分)，依据 2025–26 各州/SkillSelect 公布的竞争性区间
CAT_SCORES = {
    "Trades & Construction":               (75, 70),
    "Healthcare & Care":                   (75, 70),
    "Engineering & Infrastructure":        (80, 75),
    "IT & Digital":                        (95, 90),
    "Business, Finance & Legal":           (85, 80),
    "Education & Community":               (80, 75),
    "Agriculture & Environment":           (75, 70),
    "Hospitality, Retail & Tourism":       (80, 75),
    "Transport, Logistics & Mining":       (80, 75),
    "Creative, Media & Personal Services": (85, 80),
}


def run():
    n = 0
    with get_cursor() as cur:
        cur.execute("SELECT id, category FROM occupations WHERE country_code='AU' AND is_migration=1")
        occs = cur.fetchall()
        for o in occs:
            scores = CAT_SCORES.get(o["category"])
            if not scores:
                continue
            cur.execute("SELECT DISTINCT visa_subclass FROM occupation_visa_pathways WHERE occupation_id=%s", (o["id"],))
            subs = {r["visa_subclass"] for r in cur.fetchall()}
            for sub, sc in (("190", scores[0]), ("491", scores[1])):
                if sub not in subs:
                    continue
                cur.execute(
                    "INSERT INTO occupation_invitation_scores (occupation_id,visa_subclass,min_score,asof,note,source_url) "
                    "VALUES (%s,%s,%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE min_score=VALUES(min_score),asof=VALUES(asof),note=VALUES(note),source_url=VALUES(source_url)",
                    (o["id"], sub, sc, ASOF, NOTE, SRC))
                n += 1
    print(f"[seed] 写入/更新 {n} 条 190/491 参考获邀分")


if __name__ == "__main__":
    run()
