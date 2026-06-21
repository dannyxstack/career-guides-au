"""试点：为「平面设计师」「律师助理/法务文员」录入 AI 替代工具，并演示跨职业「也影响」。

数据模型见 migrate_ai_disruptors。一个工具录一次（ai_disruptors，品牌名不翻译），
通过 occupation_ai_disruptor 挂到多个职业；scope_zh 描述"替代了该职业的哪部分工作"。
幂等：disruptors 按 name 唯一键 upsert，关联按 (occupation_id,disruptor_id) 主键 upsert。
运行：python -m scripts.seed_ai_disruptors_pilot
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

COUNTRY = "AU"

# 工具目录：name 唯一。type: tool/platform/product/model/research/news
DISRUPTORS = {
    "Midjourney":      {"type": "model", "vendor": "Midjourney, Inc.", "year": 2022, "maturity": "mainstream",
                        "url": "https://www.midjourney.com",
                        "summary_zh": "文本生成图像模型，可由一句描述直接产出高质量插画、概念图、海报与商业视觉。"},
    "DALL·E":          {"type": "model", "vendor": "OpenAI", "year": 2022, "maturity": "mainstream",
                        "url": "https://openai.com/dall-e-3",
                        "summary_zh": "OpenAI 的文本生成图像模型，已集成进 ChatGPT，可快速生成与编辑图像。"},
    "Adobe Firefly":   {"type": "tool", "vendor": "Adobe", "year": 2023, "maturity": "mainstream",
                        "url": "https://www.adobe.com/products/firefly.html",
                        "summary_zh": "内置于 Photoshop 的生成式 AI，可一键扩图、生成填充、改背景，替代大量精修与合成工作。"},
    "Canva Magic Studio": {"type": "platform", "vendor": "Canva", "year": 2023, "maturity": "mainstream",
                        "url": "https://www.canva.com/magic/",
                        "summary_zh": "在线设计平台的 AI 套件，自动排版、生成模板与社媒图，让非专业者也能产出可用设计。"},
    "Harvey":          {"type": "platform", "vendor": "Harvey AI", "year": 2023, "maturity": "adopted",
                        "url": "https://www.harvey.ai",
                        "summary_zh": "面向律所的法律 AI，可做法律检索、合同审阅、起草与尽调，已被多家国际律所采用。"},
    "CoCounsel":       {"type": "platform", "vendor": "Thomson Reuters (Casetext)", "year": 2023, "maturity": "adopted",
                        "url": "https://casetext.com/cocounsel/",
                        "summary_zh": "法律 AI 助手，自动完成文件审阅、案例检索、证词准备与摘要等初级法务工作。"},
    "Lexis+ AI":       {"type": "platform", "vendor": "LexisNexis", "year": 2023, "maturity": "adopted",
                        "url": "https://www.lexisnexis.com/en-us/products/lexis-plus-ai.page",
                        "summary_zh": "LexisNexis 的生成式法律检索，给出带引用的法律答案、文书草稿与案例摘要。"},
    "ChatGPT":         {"type": "tool", "vendor": "OpenAI", "year": 2022, "maturity": "mainstream",
                        "url": "https://chat.openai.com",
                        "summary_zh": "通用大模型对话工具，可起草、摘要、改写文书与邮件，承担大量文字与初稿工作。"},
}

# 职业 → [(disruptor_name, level, scope_zh, evidence_url, sort)]
# level: partial / major / full
LINKS = {
    # ── 平面设计师 232411（主试点）+ 设计相邻职业（演示「也影响」）──
    "232411": [  # 平面设计师
        ("Midjourney", "major", "概念图、插画、海报与社媒视觉的初稿如今可由文字提示直接生成，初级出图岗位明显减少。", "https://www.midjourney.com", 1),
        ("Adobe Firefly", "major", "扩图、生成填充、换背景等精修与合成工作已可一键完成，压缩了大量执行性工时。", "https://www.adobe.com/products/firefly.html", 2),
        ("Canva Magic Studio", "partial", "自动排版与模板让非设计师也能产出可用的社媒图与简单物料，挤压低端排版需求。", "https://www.canva.com/magic/", 3),
        ("DALL·E", "partial", "可快速生成与改图，进一步降低简单视觉素材的外包需求。", "https://openai.com/dall-e-3", 4),
    ],
    "212411": [  # 动画师/游戏设计师
        ("Midjourney", "major", "概念美术、角色与场景设定的初稿可由文字直接生成，前期美术探索的人工大幅减少。", "https://www.midjourney.com", 1),
        ("DALL·E", "partial", "快速产出多版概念草图，压缩了前期视觉探索阶段的投入。", "https://openai.com/dall-e-3", 2),
    ],
    "211212": [  # 摄影师
        ("Adobe Firefly", "partial", "生成式扩图与背景替换减少了棚拍与后期合成需求，部分商业产品图可直接生成。", "https://www.adobe.com/products/firefly.html", 1),
        ("Midjourney", "partial", "广告与概念类图像可由 AI 生成，替代部分商业摄影与图库需求。", "https://www.midjourney.com", 2),
    ],
    "232412": [  # UI/UX 设计师
        ("Canva Magic Studio", "partial", "自动布局与组件生成承担了部分基础界面与营销页排版工作。", "https://www.canva.com/magic/", 1),
    ],
    "232413": [  # 网页设计师
        ("Canva Magic Studio", "partial", "模板化建站与自动排版替代了相当一部分中小企业网页设计需求。", "https://www.canva.com/magic/", 1),
    ],

    # ── 律师助理/法务文员 599411（主试点）+ 法律相邻职业 ──
    "599411": [  # 法律秘书/律师助理
        ("Harvey", "major", "法律检索、文件审阅与文书起草等核心助理工作已能由 AI 完成，初级法务岗位首当其冲。", "https://www.harvey.ai", 1),
        ("CoCounsel", "major", "批量文件审阅、案例检索与摘要等耗时工作被自动化，显著减少人工小时。", "https://casetext.com/cocounsel/", 2),
        ("Lexis+ AI", "partial", "带引用的法律检索与文书草稿替代了大量手工查法条与整理工作。", "https://www.lexisnexis.com/en-us/products/lexis-plus-ai.page", 3),
        ("ChatGPT", "partial", "合同摘要、邮件与文书初稿可由通用大模型快速产出，压缩文字处理工时。", "https://chat.openai.com", 4),
    ],
    "271311": [  # 律师（事务律师）
        ("Harvey", "partial", "尽调、合同审阅与初稿起草被 AI 加速，初级律师的可计费工时受到挤压。", "https://www.harvey.ai", 1),
        ("Lexis+ AI", "partial", "法律检索与备忘录草拟提速，改变了初级法律研究的人力结构。", "https://www.lexisnexis.com/en-us/products/lexis-plus-ai.page", 2),
    ],
}


def run():
    with get_cursor() as cur:
        # 1) upsert 工具目录
        ids = {}
        for name, d in DISRUPTORS.items():
            cur.execute(
                "INSERT INTO ai_disruptors (name,type,vendor,url,summary_zh,year,maturity) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE type=VALUES(type),vendor=VALUES(vendor),url=VALUES(url),"
                "summary_zh=VALUES(summary_zh),year=VALUES(year),maturity=VALUES(maturity)",
                (name, d["type"], d["vendor"], d["url"], d["summary_zh"], d["year"], d["maturity"]))
            cur.execute("SELECT id FROM ai_disruptors WHERE name=%s", (name,))
            ids[name] = cur.fetchone()["id"]
        print(f"[seed] {len(ids)} 个工具就绪")

        # 2) occ_code -> occupation_id
        occ_id = {}
        for code in LINKS:
            cur.execute("SELECT id FROM occupations WHERE country_code=%s AND occ_code=%s", (COUNTRY, code))
            row = cur.fetchone()
            if not row:
                print(f"[seed] 警告：找不到 occ_code={code}，跳过")
                continue
            occ_id[code] = row["id"]

        # 3) upsert 关联
        n = 0
        for code, links in LINKS.items():
            oid = occ_id.get(code)
            if not oid:
                continue
            for dname, level, scope, ev, sort in links:
                cur.execute(
                    "INSERT INTO occupation_ai_disruptor "
                    "(occupation_id,disruptor_id,replacement_level,scope_zh,evidence_url,sort_order) "
                    "VALUES (%s,%s,%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE replacement_level=VALUES(replacement_level),"
                    "scope_zh=VALUES(scope_zh),evidence_url=VALUES(evidence_url),sort_order=VALUES(sort_order)",
                    (oid, ids[dname], level, scope, ev, sort))
                n += 1
        print(f"[seed] {n} 条职业-工具关联就绪（涉及 {len(occ_id)} 个职业）")


if __name__ == "__main__":
    run()
