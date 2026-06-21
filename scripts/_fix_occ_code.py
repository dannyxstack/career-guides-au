"""一次性修复脚本：为尚未包含 occ_code 的 seed 脚本批量添加 occ_code 字段"""
import os, re

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__))

OLD_INSERT = (
    'cur.execute("INSERT INTO occupations (anzsco_code,anzsco_title,category,'
    'workforce_size,shortage_listed,growth_areas) VALUES (%s,%s,%s,%s,%s,%s) '
    'ON DUPLICATE KEY UPDATE anzsco_title=VALUES(anzsco_title),category=VALUES(category),'
    'workforce_size=VALUES(workforce_size),shortage_listed=VALUES(shortage_listed),'
    'growth_areas=VALUES(growth_areas)",'
)
NEW_INSERT = (
    'cur.execute("INSERT INTO occupations (anzsco_code,occ_code,anzsco_title,category,'
    'workforce_size,shortage_listed,growth_areas) VALUES (%s,%s,%s,%s,%s,%s,%s) '
    'ON DUPLICATE KEY UPDATE occ_code=VALUES(occ_code),anzsco_title=VALUES(anzsco_title),'
    'category=VALUES(category),workforce_size=VALUES(workforce_size),'
    'shortage_listed=VALUES(shortage_listed),growth_areas=VALUES(growth_areas)",'
)

OLD_VALS = (
    '(OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],OCCUPATION["category"],'
    'OCCUPATION["workforce_size"],OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"])'
)
NEW_VALS = (
    '(OCCUPATION["anzsco_code"],OCCUPATION["anzsco_code"],OCCUPATION["anzsco_title"],'
    'OCCUPATION["category"],OCCUPATION["workforce_size"],'
    'OCCUPATION["shortage_listed"],OCCUPATION["growth_areas"])'
)

targets = [
    'seed_scaffolder.py', 'seed_dogman_rigger.py',
    'seed_concreter.py', 'seed_plasterer.py', 'seed_tiler.py',
]

for fn in targets:
    path = os.path.join(SCRIPTS_DIR, fn)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    changed = False
    if OLD_INSERT in content:
        content = content.replace(OLD_INSERT, NEW_INSERT)
        changed = True
    if OLD_VALS in content:
        content = content.replace(OLD_VALS, NEW_VALS)
        changed = True
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'fixed: {fn}')
    else:
        print(f'no change needed: {fn}')

# 同时也修复 steel_fixer（它用的是更长的 run() 函数，格式略不同）
# steel_fixer 已成功入库，只需确保 occ_code 已设置（已手动 UPDATE）
print('Done.')
