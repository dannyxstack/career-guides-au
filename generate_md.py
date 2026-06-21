"""
从数据库生成职业分析 Markdown 文件。

用法：
  python generate_md.py              # 生成数据库中所有职业
  python generate_md.py 341111       # 生成指定职业代码
  python generate_md.py 341111 en    # 指定语言（默认 zh-CN）
"""
import sys
from pipeline.generators.md_generator import generate_md
from db.connection import get_cursor


def get_all_codes() -> list[str]:
    with get_cursor() as cur:
        cur.execute("SELECT anzsco_code FROM occupations ORDER BY id")
        return [r["anzsco_code"] for r in cur.fetchall()]


def main():
    locale = "zh-CN"
    codes  = []

    args = sys.argv[1:]
    for arg in args:
        if "-" in arg or arg.lower() in ("zh-cn", "en", "ko"):
            locale = arg
        else:
            codes.append(arg)

    if not codes:
        codes = get_all_codes()

    if not codes:
        print("数据库中暂无职业数据")
        return

    print(f"[generate_md] {len(codes)} 个职业  locale={locale}\n")
    errors = []
    for code in codes:
        try:
            path = generate_md(code, locale=locale)
            print(f"  [OK] {code}  ->  {path.name}")
        except Exception as e:
            print(f"  [FAIL] {code}: {e}")
            errors.append((code, str(e)))

    print(f"\n完成：{len(codes) - len(errors)} 成功，{len(errors)} 失败")
    for code, err in errors:
        print(f"  [FAIL] {code}: {err}")


if __name__ == "__main__":
    main()
