# 职业视频流水线（video_pipeline）

从已入库的澳洲职业数据，自动生成多平台短/长视频。**数据 → Claude 大纲 →
[Web 界面预览/审批] → Azure 配音 → Remotion 数据驱动渲染 → 成片**。

## 架构

```
video_pipeline/
├── config.py         读取 .env 与路径
├── data_source.py    MySQL → 单职业结构化数据
├── prompts.py        大纲生成 Prompt
├── scriptwriter.py   Claude → 分场景大纲 → platform_contents
├── content_store.py  platform_contents / video_jobs 读写与状态流转
├── spec_builder.py   已审批大纲 → Remotion inputProps.json（唯一数据契约）
├── tts.py            Azure 逐场景配音（无 key 时降级为无音频）
├── renderer.py       调 Remotion CLI 渲染，管理 video_jobs
├── web/              FastAPI 本地管理界面（大纲预览/审批）
└── remotion/         Remotion(TS) 数据驱动渲染工程
```

复用数据库表：`platform_contents`（大纲/脚本 + 审批状态）、`video_jobs`（渲染任务）、
`publish_metadata`（发布元信息）。

## 安装

```bash
# 1. Python 依赖
pip install -r video_pipeline/requirements.txt

# 2. 配置密钥：复制 .env.example 为 .env，手动填 ANTHROPIC_API_KEY / AZURE_SPEECH_*
copy .env.example .env

# 3. Remotion（需 Node.js 18+）
cd video_pipeline/remotion && npm install
```

## 用法

### A. 命令行单步验证
```bash
python -m video_pipeline.data_source 118              # 看某职业数据
python -m video_pipeline.scriptwriter 118 --platform tiktok_short   # 生成大纲
python -m video_pipeline.renderer <content_id>        # 渲染（需先审批为 approved）
```

### B. Web 界面（推荐）
```bash
python -m video_pipeline.web.app
# 打开 http://127.0.0.1:8000
# 流程：选职业 → 生成大纲 → 预览/编辑 → 审批通过 → 渲染 → 下载 mp4
```

### C. 只预览画面（不接 DB / 不配音）
```bash
cd video_pipeline/remotion && npm run studio   # 用 mock 数据预览 Short / Long
```

## Phase 0 现状与后续

已打通：数据 → 大纲 → 审批界面 → 渲染（含 TitleScene + SalaryScene 两个数据动画）。

待接（Phase 1+）：
- 把 TTS 音频轨接入 Remotion（当前渲染为静音，场景时长已按真实配音长度排好）
- 字幕（用 Azure 词级时间戳烧录）
- ratings / visa / growth 专属数据动画（当前走通用卡片）
- Pexels B-roll 自动检索插入
- 发布 API（YouTube/TikTok/IG）+ publish_metadata
