"""把 CA/NZ「数据来源」中文文案纳入翻译记忆(translation_src)，供 translate_strings 翻成 10 语言。
文案须与 site/src/lib/data.ts 的 SOURCES_BODY[*]['zh-CN'] 完全一致。幂等。
运行：python -m scripts.add_sources_strings
"""
import sys, os, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

STRINGS = [
    "本页薪资为综合 Job Bank、Indeed、Glassdoor、ERI SalaryExpert 等公开区间的估算；就业与需求预测引用加拿大统计局（Statistics Canada）及加拿大就业与社会发展部（ESDC / Job Bank）；移民信息以加拿大移民部（IRCC）的快速通道（Express Entry）与各省提名（PNP）最新规则为准。数据仅供参考，请以官方最新发布为准。",
    "本页薪资为综合 Seek NZ、Trade Me Jobs、Glassdoor、PayScale 等公开区间的估算；就业与需求预测引用新西兰统计局（Stats NZ）及商业、创新与就业部（MBIE）；移民信息以新西兰移民局（Immigration New Zealand）的 Green List 及技术移民（SMC / AEWV）最新规则为准。数据仅供参考，请以官方最新发布为准。",
]


def h(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def run():
    rows = [(h(s.strip()), s.strip(), "ui_sources") for s in STRINGS]
    with get_cursor() as cur:
        cur.executemany(
            "INSERT INTO translation_src (src_hash, src_text, field) VALUES (%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE field=VALUES(field)", rows)
    print(f"[add] 已纳入 {len(rows)} 条来源文案到 translation_src")


if __name__ == "__main__":
    run()
