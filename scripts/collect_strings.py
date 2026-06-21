"""采集所有可翻译的中文源串到翻译记忆表 translation_src（幂等）。
建表（TM）→ 扫描全部职业字段 → 去重（仅含 CJK 的串）→ upsert。
不删除已有 src（旧串保留），仅新增缺失串。"""
import sys, os, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor
from scripts._i18n_fields import fetch_bundles, collect_from_bundle, needs_translation

DDL = [
    """CREATE TABLE IF NOT EXISTS translation_src (
        src_hash CHAR(40) NOT NULL PRIMARY KEY,
        src_text TEXT NOT NULL,
        field    VARCHAR(40),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='翻译记忆-源串'""",
    """CREATE TABLE IF NOT EXISTS translations (
        src_hash CHAR(40) NOT NULL,
        locale   VARCHAR(10) NOT NULL,
        text     TEXT NOT NULL,
        gen_model VARCHAR(60),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (src_hash, locale)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='翻译记忆-译文'""",
]


def h(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def build():
    with get_cursor() as cur:
        for ddl in DDL:
            cur.execute(ddl)
        bundles = fetch_bundles(cur)
        seen = {}  # hash -> (text, field)
        for b in bundles:
            for field, text in collect_from_bundle(b):
                if not needs_translation(text):
                    continue
                t = text.strip()
                seen.setdefault(h(t), (t, field))
        rows = [(hh, t, f) for hh, (t, f) in seen.items()]
        cur.executemany(
            "INSERT INTO translation_src (src_hash, src_text, field) VALUES (%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE field=VALUES(field)", rows)
        cur.execute("SELECT COUNT(*) n FROM translation_src")
        total = cur.fetchone()["n"]
    print(f"[collect] distinct CJK 源串本次采集 {len(rows)}，表内总计 {total}")


if __name__ == "__main__":
    build()
