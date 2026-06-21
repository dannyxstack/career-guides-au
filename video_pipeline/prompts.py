"""大纲生成的 Prompt 模板。大纲是分场景结构，供 Web 界面预览/审批后再渲染。"""

import json

# 不同平台的节奏指引
PLATFORM_GUIDE = {
    "tiktok_short": (
        "目标平台：TikTok / Reels / YouTube Shorts（竖屏 9:16）。"
        "总时长严格控制在 35~55 秒。开场 3 秒必须有强 Hook 抓住注意力。"
        "节奏快、口语化、每个场景一个信息点，结尾给明确 CTA。建议 5~7 个场景。"
        "【字数预算】配音语速约：中文 4.5 字/秒、英文 2.5 词/秒。"
        "所有场景 narration 加起来：中文不超过 240 字 / 英文不超过 135 词。"
        "宁可精炼也不要超时——每段 narration 只说一句最关键的话。"
    ),
    "youtube_long": (
        "目标平台：YouTube 长视频（横屏 16:9）。"
        "总时长 5~8 分钟。结构完整：开场→职业概览→薪资→教育路径→从业资质→评分→"
        "签证移民→前景与适合人群→总结 CTA。语气专业但易懂。"
        "建议 8~11 个场景。其中 education（教育路径）讲怎么学/学多久/花多少钱，"
        "qualifications（从业资质）讲需要哪些证书/是否强制。"
    ),
}

# 合法的场景类型（Remotion 端按 id 决定布局；未知 id 走通用旁白卡片）
SCENE_IDS = ["title", "summary", "salary", "education", "qualifications",
             "ratings", "visa", "growth", "suitability", "cta"]

SYSTEM = "你是澳大利亚职业科普短视频的资深编导，擅长把结构化数据转成有节奏的分镜脚本。"

# 结构化输出 Schema：交给 Anthropic output_config.format，API 保证返回合法 JSON，
# 彻底避免模型手写 JSON 时未转义引号/换行导致的 JSONDecodeError。
OUTLINE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "platform": {"type": "string"},
        "title": {"type": "string"},
        "hook": {"type": "string"},
        "est_duration_sec": {"type": "integer"},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string", "enum": SCENE_IDS},
                    "name": {"type": "string"},
                    "narration": {"type": "string"},
                    "duration_sec": {"type": "integer"},
                    "data_points": {"type": "array", "items": {"type": "string"}},
                    "broll_hint": {"type": "string"},
                },
                "required": ["id", "name", "narration", "duration_sec",
                             "data_points", "broll_hint"],
            },
        },
    },
    "required": ["platform", "title", "hook", "est_duration_sec", "scenes"],
}


# ---------- PPT 决策文案 brief（PPT 专用，区别于视频分场景大纲）----------
# 用于补足 DB 里没有的"决策视频"内容：强钩子标题、首屏关键数字、每天做什么、
# 30 天入门行动清单、贴近搜索流量的增长关键词、ANZSCO/签证风险提示。
PPT_BRIEF_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "hook_title": {"type": "string"},
        "key_stats": {"type": "array", "items": {"type": "string"}},
        "daily_tasks": {"type": "array", "items": {"type": "string"}},
        "action_plan_30d": {"type": "array", "items": {"type": "string"}},
        "growth_keywords": {"type": "array", "items": {"type": "string"}},
        "anzsco_note": {"type": "string"},
    },
    "required": ["hook_title", "key_stats", "daily_tasks",
                 "action_plan_30d", "growth_keywords", "anzsco_note"],
}

PPT_BRIEF_SYSTEM = (
    "你是澳大利亚职业决策内容的资深编辑，把结构化职业数据转成'决策视频'式的 PPT 文案："
    "钩子要抓人、数字要具体、行动清单要可执行，且只用给定数据、不杜撰官方数字。"
)


def build_ppt_brief_prompt(occ: dict) -> str:
    data = json.dumps(occ, ensure_ascii=False, indent=2, default=str)
    return f"""下面是某澳洲职业的真实结构化数据（只能用这些数据，不要杜撰官方预测/精确数字）：

```json
{data}
```

请生成一份**决策视频式 PPT 文案 brief**，严格只输出一个 JSON 对象，结构如下：

{{
  "hook_title": "强钩子主标题（中文，含职业名，像短视频标题那样抓人，可用疑问句）",
  "key_stats": ["首屏3个关键卖点/数字，每条≤14字，例如薪资锚点、核心技能、移民路径"],
  "daily_tasks": ["这个职业'每天做什么'，4~6条具体动作，口语、可感知"],
  "action_plan_30d": ["30天入门行动清单，4~5条，覆盖约4周/30天内，每条以阶段词开头如'第1周：'，不要超过第4周"],
  "growth_keywords": ["5个贴近YouTube/TikTok搜索流量的细分方向关键词，优先英文岗位名/技术名"],
  "anzsco_note": "一句ANZSCO/签证风险提示：说明该职业签证需按具体职责匹配ANZSCO、以Home Affairs与相关评估机构为准"
}}

要求：
- key_stats 的薪资数字必须取自上面 salaries 数据，不要编造。
- daily_tasks / action_plan_30d 要贴合该职业实际，避免空话。
- growth_keywords 用于视频标题与字幕命中搜索，尽量是真实存在的细分岗位/技术词。
- 只输出 JSON，不要解释、不要 Markdown 代码块标记。"""


def build_outline_prompt(occ: dict, platform: str) -> str:
    guide = PLATFORM_GUIDE.get(platform, PLATFORM_GUIDE["tiktok_short"])
    data = json.dumps(occ, ensure_ascii=False, indent=2, default=str)
    scene_ids = ", ".join(SCENE_IDS)
    # 中文旁白：自然点缀极少量语气词，模拟真人解说的思考与停顿
    humanize = ""
    if occ.get("locale", "zh-CN").startswith("zh"):
        humanize = (
            "\n- 口语自然化：在旁白里**自然地、极克制地**点缀少量语气词"
            "（呢/嗯/呃/哦/嘛），模拟真人解说的思考与迟疑。整条视频总共只放 2~3 处，"
            "每处最多一个字，放在句首或自然停顿处；绝不要每句都加，也不要影响信息清晰度。"
        )
    return f"""{guide}

下面是该职业的真实数据（来自澳大利亚官方来源，务必只用这些数据，不要杜撰数字）：

```json
{data}
```

请生成一份**分场景视频大纲**。严格只输出一个 JSON 对象，不要任何解释或 Markdown 代码块标记，结构如下：

{{
  "platform": "{platform}",
  "title": "适合该平台的视频标题（中文，含职业名）",
  "hook": "开场第一句话（要抓人）",
  "est_duration_sec": 估算总秒数(整数),
  "scenes": [
    {{
      "id": "场景类型，从 [{scene_ids}] 中选",
      "name": "场景简短名称",
      "narration": "这一段的旁白文字（口语化，会被用来配音）",
      "duration_sec": 该场景秒数(整数),
      "data_points": ["这段用到的数据字段名"],
      "broll_hint": "建议的 B-roll 画面英文关键词，用于素材检索"
    }}
  ]
}}

要求：
- narration 用 {occ.get('locale', 'zh-CN')} 语言，自然口语，可直接朗读。
- 各场景 duration_sec 之和应接近 est_duration_sec。
- 薪资、评分等数字必须与上面数据一致。
- 签证术语：482 现为 **Skills in Demand**（不要再写旧的"TSS"）；不要把移民路径说得绝对（如"都走得通"），
  要点明"需看 ANZSCO 匹配、雇主和州政策"。可参考表达：
  "482 Skills in Demand 雇主担保、186 ENS、190 州担保都有可能，但要看 ANZSCO 匹配、雇主和州政策。"
- 第一个场景 id 用 "title"，最后一个用 "cta"。{humanize}"""
