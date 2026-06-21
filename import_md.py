"""
将 output/ 目录下的 Markdown 文件批量导入数据库。

用法：
  python import_md.py                  # 导入全部
  python import_md.py electrician.md   # 导入单个文件
"""

import sys
from pathlib import Path
from pipeline.parsers.md_parser import parse_md
from pipeline.importer import import_occupation

OUTPUT_DIR = Path(__file__).parent / "output"


def import_file(md_path: Path):
    print(f"  parsing  {md_path.name} ...", end=" ")
    data = parse_md(md_path)

    code = data.get("anzsco_code", "?")
    name = data.get("name_zh", "?")
    print(f"[{code}] {name}", end=" → ")

    occupation_id = import_occupation(data)
    print(f"id={occupation_id}  OK")


def main():
    if len(sys.argv) > 1:
        targets = [OUTPUT_DIR / sys.argv[1]]
    else:
        targets = sorted(OUTPUT_DIR.glob("*.md"))

    if not targets:
        print("output/ 目录下没有 .md 文件")
        return

    print(f"[import] {len(targets)} file(s)\n")
    errors = []
    for path in targets:
        try:
            import_file(path)
        except Exception as e:
            print(f"FAIL: {e}")
            errors.append((path.name, str(e)))

    print(f"\n{'='*40}")
    print(f"完成：{len(targets) - len(errors)} 成功，{len(errors)} 失败")
    for fname, err in errors:
        print(f"  [FAIL] {fname}: {err}")


if __name__ == "__main__":
    main()
