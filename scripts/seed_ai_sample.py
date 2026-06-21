"""样本：给 2 个 AU 职业填「AI 时代」分析（occupation_ai）。
- General Clerk(532111)：被自动化压缩
- Registered Nurse (Medical Practice)(254422)：被 AI 放大能力
相邻职业用同国 occ_code。幂等(REPLACE)。运行：python -m scripts.seed_ai_sample
（需先跑 migrate_ai_insights）
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

AI = {
    "532111": dict(
        verdict_type="compressed",
        verdict_zh="这是一个被自动化压缩的职业：基础录入、归档与标准文书正被 AI 与 RPA 大量吞噬，入门岗位明显收窄，建议尽快向流程协调、专业或管理方向转型。",
        entry_narrowing_zh="普通文员入门岗位会明显变窄——最基础的录入、整理与归档任务最先被 AI 接管，雇主更愿意招「会用工具、懂业务流程」的人。纯靠基础操作入行将越来越难。",
        replaced_zh=["资料录入与表格整理（人工只需复核）", "标准邮件与基础文案起草", "简单报表的自动生成", "会议纪要的语音转写与归档"],
        augmented_zh=["跨系统数据核对与清洗", "用 AI 起草后人工校订", "流程排程与协调", "知识库检索与整理"],
        moat_zh=["跨部门沟通与协调", "对业务流程的整体把握", "异常与例外情况的判断处理", "客户/同事的人际信任"],
        skills_zh=["办公自动化(Excel/Power Automate)", "AI 办公助手(Copilot 等)", "数据整理与基础分析", "流程与项目协调", "商务沟通与英语"],
        upgrade_path_zh="普通文员 → 熟练办公自动化与 AI 助手 → 流程 / 数据协调 → 办公室经理 / 项目协调 / 专业行政（HR、财务、采购）。越早从「执行基础任务」转向「设计与协调流程」，越能避开被自动化压缩。",
        adjacent=["512111", "551211", "511113"],
    ),
    "254422": dict(
        verdict_type="amplified",
        verdict_zh="注册护士不是会被 AI 替代的职业，而是会被 AI 工具重新分工的职业。AI 会减少记录、提醒、检索和初步风险提示的时间，但最终护理判断、床旁照护、用药核对、患者沟通、家属协调和法律责任仍由注册护士承担。会使用数字健康工具和 AI 辅助系统的护士，会比只会传统流程的护士更有竞争力。",
        entry_narrowing_zh="注册护士入门岗位不会明显变窄——临床照护高度依赖现场与人际，AI 更多是减负而非替人；新人仍有稳定入口，但会用电子病历与数字健康工具的人更有优势。",
        replaced_zh=["护理记录的语音转写与结构化草稿（护士须核对，并对准确、完整、及时的记录负责）", "交班与出院小结的初稿生成", "排班与耗材清点等事务", "标准健康宣教材料的整理与个性化"],
        augmented_zh=["跌倒 / 压疮 / 败血症等风险预警辅助", "用药与剂量核对提醒", "异常生命体征的自动提示", "病例与循证资料检索", "患者沟通准备与随访"],
        moat_zh=["注册执照与法律责任", "床旁照护与现场操作", "与患者及家属的照护关系", "复杂病情的临床判断", "多学科团队协调"],
        skills_zh=["数字健康 / 电子病历(EHR)系统", "AI 辅助风险提醒工具的使用与核验", "数据与循证素养", "沟通与同理心", "英语与跨文化沟通"],
        upgrade_path_zh="普通 RN → 熟练使用电子病历与 AI 风险提醒 → 老年护理 / 精神健康 / ICU 等专科 → Clinical Nurse / Nurse Unit Manager / Nurse Practitioner。越往上越依赖临床判断、领导与协调，AI 难以替代，议价能力更强。",
        adjacent=["411411", "254423", "423111"],
    ),
}


def run():
    n = 0
    with get_cursor() as cur:
        for code, a in AI.items():
            cur.execute("SELECT id FROM occupations WHERE country_code='AU' AND occ_code=%s", (code,))
            row = cur.fetchone()
            if not row:
                print(f"[skip] occ_code {code} 不存在")
                continue
            oid = row["id"]
            cur.execute(
                "REPLACE INTO occupation_ai (occupation_id,verdict_type,verdict_zh,entry_narrowing_zh,"
                "replaced_zh,augmented_zh,moat_zh,skills_zh,upgrade_path_zh,adjacent) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (oid, a["verdict_type"], a["verdict_zh"], a["entry_narrowing_zh"],
                 json.dumps(a["replaced_zh"], ensure_ascii=False), json.dumps(a["augmented_zh"], ensure_ascii=False),
                 json.dumps(a["moat_zh"], ensure_ascii=False), json.dumps(a["skills_zh"], ensure_ascii=False),
                 a["upgrade_path_zh"], json.dumps(a["adjacent"], ensure_ascii=False)))
            n += 1
            print(f"[ai] {code} (id={oid}) {a['verdict_type']}")
    print(f"[OK] AI 样本写入 {n}")


if __name__ == "__main__":
    run()
