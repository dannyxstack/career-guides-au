"""给代表职业写入「AI 职业图谱」数据：cluster + 4 个 1-5 分。
只更新 occupation_ai 的 cluster/automation_exposure/human_moat/entry_risk/ai_upside 列，
不触碰已有文案(verdict_zh 等)。幂等。运行：python -m scripts.seed_ai_graph
（需先跑 migrate_ai_insights + migrate_ai_graph）
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

# 大类原型分（10 分制）：(automation_exposure, human_moat, entry_risk, ai_upside)
CLUSTER_SCORE = {
    "high_ai_exposure":       (10, 4, 10, 4),
    "ai_augmented":           (8, 6, 8, 10),
    "licensed_accountable":   (4, 10, 4, 8),
    "physical_site_based":    (2, 10, 4, 4),
    "human_trust_care":       (4, 10, 4, 6),
    "regulated_public_safety":(4, 10, 6, 6),
}

# occ_code(AU) -> cluster
ASSIGN = {
    # AI 高替代/高压缩
    "532111": "high_ai_exposure",   # General Clerk
    "542111": "high_ai_exposure",   # Receptionist
    "551211": "high_ai_exposure",   # Bookkeeper
    "551112": "high_ai_exposure",   # Payroll Clerk
    "232411": "high_ai_exposure",   # Graphic Designer
    # AI 增强型
    "262199": "ai_augmented",       # BI Analyst
    "261312": "ai_augmented",       # Software Engineer
    "262113": "ai_augmented",       # Database Administrator
    "262111": "ai_augmented",       # ICT Business Analyst
    # 强执照/强责任
    "254422": "licensed_accountable",  # Registered Nurse (Medical Practice)
    "251511": "licensed_accountable",  # Pharmacist
    "341111": "licensed_accountable",  # Electrician (General)
    "334111": "licensed_accountable",  # Plumber (General)
    "233211": "licensed_accountable",  # Civil Engineer
    "241213": "licensed_accountable",  # Primary School Teacher
    # 强现场/强体力
    "331212": "physical_site_based",   # Formwork Carpenter
    "322313": "physical_site_based",   # Welder (First Class)
    "351311": "physical_site_based",   # Chef
    "423111": "physical_site_based",   # Aged Care Worker
    "811211": "physical_site_based",   # Commercial Cleaner
    "362211": "physical_site_based",   # Arborist / Forestry Worker
    # 强人际信任/照护
    "272511": "human_trust_care",      # Social Worker
    "423312": "human_trust_care",      # Disability Support Worker
    "272199": "human_trust_care",      # Counsellor
    # 强监管/公共安全
    "441111": "regulated_public_safety",  # Police Officer
    "441211": "regulated_public_safety",  # Firefighter
    "251311": "regulated_public_safety",  # WHS Officer
    "221214": "regulated_public_safety",  # Compliance Officer
    "441312": "regulated_public_safety",  # Customs Officer
    "312116": "regulated_public_safety",  # Building Inspector
}


def run():
    n = 0
    with get_cursor() as cur:
        for code, cluster in ASSIGN.items():
            cur.execute("SELECT id FROM occupations WHERE country_code='AU' AND occ_code=%s", (code,))
            row = cur.fetchone()
            if not row:
                print(f"[skip] {code} 不存在")
                continue
            oid = row["id"]
            ae, hm, er, up = CLUSTER_SCORE[cluster]
            cur.execute(
                "INSERT INTO occupation_ai (occupation_id,cluster,automation_exposure,human_moat,entry_risk,ai_upside) "
                "VALUES (%s,%s,%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE cluster=VALUES(cluster),automation_exposure=VALUES(automation_exposure),"
                "human_moat=VALUES(human_moat),entry_risk=VALUES(entry_risk),ai_upside=VALUES(ai_upside)",
                (oid, cluster, ae, hm, er, up))
            n += 1
    print(f"[OK] AI 图谱数据写入 {n} 个职业")


if __name__ == "__main__":
    run()
