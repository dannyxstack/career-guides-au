#!/usr/bin/env python3
"""校验 output/ 下的职业分析 Markdown 文件是否符合 rules.md 要求。"""

import os
import re
import sys

REQUIRED_SECTIONS = [
    "教育路径",
    "考证难度",
    "职位需求量",
    "收入范围",
    "未来趋势",
    "移民路径",
    "适合人群",
    "数据来源",
]

def check_file(path):
    errors = []
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # 1. 检查8个必须部分
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"缺少必须部分: {section}")

    # 2. 检查金额格式：只检查含薪资/费用关键词的行
    money_keywords = re.compile(r'(薪|费|AUD|salary|wage|cost|price|earn|income|年薪|月薪|周薪|收入|费用|学费|工资)')
    # 已知非货币数字模式：职位数量/人数（数字后跟计数词或+，或行含从业人数/岗位/就业）
    job_count_line = re.compile(r'从业人数|就业人数|岗位|Seek|Indeed|LinkedIn|职位数量|挂牌')
    for line in content.splitlines():
        if money_keywords.search(line):
            # 跳过明显是职位数量统计的行
            if job_count_line.search(line):
                continue
            candidates = re.findall(r'(?<!\$)\b\d{1,3},\d{3}', line)
            bare = []
            for num in candidates:
                idx = line.find(num)
                after = line[idx + len(num):idx + len(num) + 2] if idx >= 0 else ''
                # 跳过后接计数词（个/人/名/+）的数字——这些是数量而非金额
                if re.match(r'[个人名+]', after):
                    continue
                bare.append(num)
            if bare:
                errors.append(f"金额缺少 $ 符号（行: {line.strip()[:60]}）")
                break

    # 3. 检查五角星评级
    if "★" not in content:
        errors.append("缺少五角星评级（★）")

    # 4. 检查职业代码为单行（不允许职业代码后跟代码块）
    if re.search(r'\*\*职业代码[：:]\*\*\s*\n', content):
        errors.append("职业代码不能单独成行后接代码块，必须在同一行内")

    # 5. 检查一级标题存在
    if not re.search(r'^# .+', content, re.MULTILINE):
        errors.append("缺少一级标题")

    return errors

def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    files = [f for f in os.listdir(output_dir) if f.endswith(".md")]
    if not files:
        print("output/ 目录下没有 .md 文件")
        sys.exit(1)

    all_pass = True
    for fname in sorted(files):
        path = os.path.join(output_dir, fname)
        errors = check_file(path)
        if errors:
            all_pass = False
            print(f"[FAIL] {fname}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"[PASS] {fname}")

    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    main()
