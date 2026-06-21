"""
回填以下字段（从文本提取，无需 web 检索）：
  occupation_salaries:  salary_band, exp_years_min, exp_years_max
  occupation_education: duration_months_min, duration_months_max, is_core_path
"""
import re
import sys
sys.path.insert(0, '.')
from db.connection import get_cursor

# ── salary_band 规则 ────────────────────────────────────────────────────────────
PEAK_KEYWORDS = [
    'FIFO', '矿区', '专科医生', '私诊', 'CLO', 'CPO', 'CTO', 'VP Supply',
    'Chief Supply', 'Chief Learning', '农场/偏远', '农村/偏远', '专科护士',
    '专科会诊', 'Road Train',
]
SENIOR_KEYWORDS = ['高级', 'senior', 'Senior', '资深', 'Principal', 'Director',
                   'CHRO', 'ML架构师', 'Head Chef', '农业总监', '供应链总监',
                   '首席', '总监', '架构师', 'Chief', 'Officer']
ENTRY_KEYWORDS  = ['初级', '学员', '学徒', 'ABF学员', 'apprentice', '毕业',
                   '新手', '实习', 'Graduate', 'graduate', 'entry', 'Entry',
                   '见习', '助理', 'Coordinator', '协调员', '助理护士']

def classify_band(exp: str) -> str | None:
    if not exp:
        return None
    # peak
    if any(k in exp for k in PEAK_KEYWORDS):
        return 'peak'
    # senior：年数 >= 8 的"X年+"，或含高级关键词
    if re.search(r'([89]|1\d)\d*\s*年\s*\+', exp):
        return 'senior'
    if any(k in exp for k in SENIOR_KEYWORDS):
        return 'senior'
    # entry：0~X年 或 entry 关键词
    if re.search(r'0\s*[~～]\s*\d', exp):
        return 'entry'
    if any(k in exp for k in ENTRY_KEYWORDS):
        return 'entry'
    # mid：X~Y年 且 X >= 1，或显示年数在 1~7 之间的"X年+"
    if re.search(r'[1-7]\s*~\s*\d+\s*年', exp):
        return 'mid'
    if re.search(r'[1-7]\s*年\s*\+', exp):
        return 'mid'
    return None  # 无法识别，保持 NULL

# ── exp_years 提取 ──────────────────────────────────────────────────────────────
def extract_exp_years(exp: str):
    if not exp:
        return None, None
    # X~Y年
    m = re.search(r'(\d+)\s*[~～]\s*(\d+)\s*年', exp)
    if m:
        return int(m.group(1)), int(m.group(2))
    # X年+
    m = re.search(r'(\d+)\s*年\s*\+', exp)
    if m:
        return int(m.group(1)), None
    # 单值 X年
    m = re.search(r'(\d+)\s*年', exp)
    if m:
        v = int(m.group(1))
        return v, v
    return None, None

# ── duration_months 提取 ────────────────────────────────────────────────────────
def extract_duration_months(dur: str):
    if not dur:
        return None, None
    # 天/周 → 忽略（设为 0,0 表示"极短，非入行周期"）
    if re.search(r'\d+\s*[~～]?\s*\d*\s*[天周]', dur):
        return 0, 0
    if re.search(r'^[约]?\d+\s*[天周]', dur):
        return 0, 0
    # X~Y个月
    m = re.search(r'(\d+)\s*[~～]\s*(\d+)\s*个?月', dur)
    if m:
        return int(m.group(1)), int(m.group(2))
    # 单值 X个月 或 X月
    m = re.search(r'(\d+)\s*个?月', dur)
    if m:
        v = int(m.group(1))
        return v, v
    # X~Y年
    m = re.search(r'(\d+)\s*[~～]\s*(\d+)\s*年', dur)
    if m:
        return int(m.group(1)) * 12, int(m.group(2)) * 12
    # 单值 X年
    m = re.search(r'(\d+)\s*年', dur)
    if m:
        v = int(m.group(1)) * 12
        return v, v
    # 无 / 不适用
    if dur.strip() in ('无', '不适用', 'N/A', '-'):
        return None, None
    return None, None

# ── is_core_path 规则 ───────────────────────────────────────────────────────────
OPTIONAL_KEYWORDS = [
    'Vetassess', 'VETASSESS', 'TRA ', 'ANMAC', 'AIM', '技能评估', '移民评估',
    'MR驾照', 'HR驾照', 'HC驾照', 'MC驾照', '无人机', 'RPL', '额外认证',
    '可选', '加分', '非必须',
]

def is_optional(stage: str, cost_note: str) -> bool:
    text = (stage or '') + ' ' + (cost_note or '')
    return any(k in text for k in OPTIONAL_KEYWORDS)

# ── 主逻辑 ──────────────────────────────────────────────────────────────────────
def run():
    with get_cursor() as cur:
        # 1. occupation_salaries
        cur.execute('SELECT id, experience, salary_band, exp_years_min, exp_years_max FROM occupation_salaries')
        salary_rows = cur.fetchall()

        band_updated = exp_updated = 0
        band_unknown = []

        for row in salary_rows:
            exp = row['experience'] or ''
            updates = {}

            if row['salary_band'] is None:
                band = classify_band(exp)
                if band:
                    updates['salary_band'] = band
                    band_updated += 1
                else:
                    band_unknown.append((row['id'], exp))

            if row['exp_years_min'] is None and row['exp_years_max'] is None:
                ymin, ymax = extract_exp_years(exp)
                if ymin is not None or ymax is not None:
                    updates['exp_years_min'] = ymin
                    updates['exp_years_max'] = ymax
                    exp_updated += 1

            if updates:
                set_clause = ', '.join(f'{k}=%s' for k in updates)
                cur.execute(
                    f'UPDATE occupation_salaries SET {set_clause} WHERE id=%s',
                    list(updates.values()) + [row['id']]
                )

        print(f'salary_band 回填: {band_updated} 条')
        print(f'exp_years 回填:   {exp_updated} 条')
        if band_unknown:
            print(f'salary_band 无法识别（需人工）: {len(band_unknown)} 条')
            for rid, exp in band_unknown[:20]:
                print(f'  id={rid}: {exp}')

        # 2. occupation_education
        cur.execute('SELECT id, stage, duration, cost_note, duration_months_min, duration_months_max, is_core_path FROM occupation_education')
        edu_rows = cur.fetchall()

        dur_updated = core_updated = 0

        for row in edu_rows:
            dur = row['duration'] or ''
            updates = {}

            if row['duration_months_min'] is None and row['duration_months_max'] is None:
                dmin, dmax = extract_duration_months(dur)
                if dmin is not None or dmax is not None:
                    updates['duration_months_min'] = dmin
                    updates['duration_months_max'] = dmax
                    dur_updated += 1

            # is_core_path 只将明确可选项改为 0，默认不动
            if row['is_core_path'] == 1:
                if is_optional(row['stage'], row['cost_note']):
                    updates['is_core_path'] = 0
                    core_updated += 1

            if updates:
                set_clause = ', '.join(f'{k}=%s' for k in updates)
                cur.execute(
                    f'UPDATE occupation_education SET {set_clause} WHERE id=%s',
                    list(updates.values()) + [row['id']]
                )

        print(f'duration_months 回填: {dur_updated} 条')
        print(f'is_core_path → 0:    {core_updated} 条')

        # 3. 回填统计
        cur.execute('''
            SELECT salary_band, COUNT(*) n FROM occupation_salaries
            GROUP BY salary_band ORDER BY salary_band
        ''')
        print('\nsalary_band 分布:')
        for r in cur.fetchall():
            print(f'  {r["salary_band"]}: {r["n"]}')

        cur.execute('''
            SELECT
              SUM(exp_years_min IS NOT NULL) exp_filled,
              SUM(exp_years_min IS NULL) exp_null,
              SUM(duration_months_min IS NOT NULL) dur_filled,
              SUM(duration_months_min IS NULL) dur_null
            FROM occupation_salaries s
            LEFT JOIN occupation_education e ON 1=1
            LIMIT 1
        ''')
        # Simpler check
        cur.execute('SELECT SUM(exp_years_min IS NOT NULL) n FROM occupation_salaries')
        print(f'\nexp_years_min 非NULL: {cur.fetchone()["n"]}')
        cur.execute('SELECT SUM(duration_months_min IS NOT NULL) n FROM occupation_education')
        print(f'duration_months_min 非NULL: {cur.fetchone()["n"]}')
        cur.execute('SELECT SUM(is_core_path=0) n FROM occupation_education')
        print(f'is_core_path=0: {cur.fetchone()["n"]}')

if __name__ == '__main__':
    run()
