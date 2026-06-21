---
name: occupation-ppt
description: 为澳洲职业生成有图有表的 PPTX 演示文稿。从数据库 occupations 数据出发，自动配 Pexels 在线职业图片，输出标题/概览/薪资表/评分/签证/增长领域/CTA 共 7 页幻灯片。当用户要求"给某职业做 PPT/幻灯片/演示文稿"、或要为视频内容补充图表/图片素材时使用。
---

# 职业 PPT 生成技能

把数据库里的职业数据做成**有图有表**的 PPTX，弥补纯文字视频的生硬感。

## 何时用

- 用户说"给 XX 职业做个 PPT / 幻灯片 / 演示文稿"
- 用户想为视频补充图表、表格、职业实拍图
- 批量为多个职业产出演示稿

## 怎么用

技能由 `video_pipeline/ppt_builder.py` 实现，**用项目的 conda 环境 `career-video` 运行**：

```bash
# 单个职业（occupation_id 是 occupations.id）
conda run --no-capture-output -n career-video python -m video_pipeline.ppt_builder <occupation_id>

# 不联网取图（纯表格，快速预览）
conda run --no-capture-output -n career-video python -m video_pipeline.ppt_builder <occupation_id> --no-images
```

- 找 occupation_id：`SELECT id, anzsco_code FROM occupations WHERE ...`，或先跑
  `python -m video_pipeline.data_source <id>` 看数据。
- 输出：`video_pipeline/out/ppt/<slug>.pptx`。
- 图片来自 **Pexels**，需 `.env` 配 `PEXELS_API_KEY`；没配则自动降级为无图版本。

## 幻灯片结构（7 页）

1. **标题页** — 中文名 + 英文名 + ANZSCO + 职业实拍图
2. **职业概览** — summary 文案 + 配图
3. **薪资范围** — 经验阶段 × 年薪范围 表格
4. **职业评分** — 11 个维度星级（★）双列
5. **签证 / 移民路径** — 各签证子类 + 说明
6. **增长领域** — 要点列表 + 配图
7. **CTA** — 行动号召 + 数据来源

配色与视频主题一致（深色底 + 绿/琥珀强调色），中文用微软雅黑避免方块字。

## 自定义

- 改页数/版式/配色：编辑 `video_pipeline/ppt_builder.py`（各 `_slide_*` 函数）。
- 改图片数量/检索词：编辑 `build_ppt()` 里的 `images.search_images(...)` 调用。
- 想用已生成的视频文案（platform_contents）做标题/概览：可在 `build_ppt` 中读取
  `content_store.get_content_by_key(occupation_id, locale, platform)` 的 outline。

## 依赖

`python-pptx`、`pillow`、`requests`（已在 `video_pipeline/requirements.txt`）。数据库连接复用 `db/connection.py`。
