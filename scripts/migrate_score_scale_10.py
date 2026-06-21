"""迁移：把评分类字段从 5 分制改为 10 分制（小数，保留 1 位）。
- occupation_ratings.stars / score：×2（decimal(3,1) 已可容纳）。
- occupation_ai.automation_exposure / human_moat / entry_risk / ai_upside：
  列类型 TINYINT → DECIMAL(3,1)，并把现有 1-5 值 ×2。
移民获邀分 occupation_invitation_scores.min_score（65-90）非五分制，不动。

幂等：每个表先看当前最大值，若已 > 5 视为已迁移，跳过 ×2（避免重复翻倍）。
列类型变更用 SHOW COLUMNS 判断，已是 decimal 则跳过。
运行：python -m scripts.migrate_score_scale_10
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

AI_COLS = ["automation_exposure", "human_moat", "entry_risk", "ai_upside"]


def run():
    with get_cursor() as cur:
        # 1) occupation_ratings：stars / score ×2
        cur.execute("SELECT MAX(stars) mx FROM occupation_ratings")
        mx = cur.fetchone()["mx"]
        if mx is not None and float(mx) <= 5:
            cur.execute("UPDATE occupation_ratings SET stars=ROUND(stars*2,1), score=ROUND(score*2,1)")
            print(f"[ratings] stars/score ×2 完成（迁移前 max={mx}）")
        else:
            print(f"[ratings] 跳过（max={mx}，已是 10 分制）")

        # 2) occupation_ai 4 列：先改类型，再 ×2
        for col in AI_COLS:
            cur.execute("SHOW COLUMNS FROM occupation_ai LIKE %s", (col,))
            row = cur.fetchone()
            if row and "decimal" not in row["Type"].lower():
                cur.execute(f"ALTER TABLE occupation_ai MODIFY COLUMN {col} DECIMAL(3,1) "
                            f"COMMENT '10 分制（小数）'")
                print(f"[ai] {col} 类型 → DECIMAL(3,1)")
        cur.execute("SELECT MAX(automation_exposure) mx FROM occupation_ai")
        mx = cur.fetchone()["mx"]
        if mx is not None and float(mx) <= 5:
            sets = ", ".join(f"{c}=ROUND({c}*2,1)" for c in AI_COLS)
            cur.execute(f"UPDATE occupation_ai SET {sets} WHERE automation_exposure IS NOT NULL")
            print(f"[ai] 4 列 ×2 完成（迁移前 max={mx}）")
        else:
            print(f"[ai] 跳过 ×2（max={mx}，已是 10 分制或无数据）")
    print("[OK] 评分刻度迁移完成")


if __name__ == "__main__":
    run()
