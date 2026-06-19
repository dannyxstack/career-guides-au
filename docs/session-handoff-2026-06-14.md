# 会话交接 · 2026-06-14（视频流水线 + PPT + 方案C 合二为一）

> 接续 `session-handoff-2026-06-12.md`。本会话把视频从"纯文字"升级为"幻灯片(图/表/图表)+配音+字幕"，
> 并新增职业 PPT 生成技能。数据库 191 个 AU 职业入库见更早交接文档。

---

## 一、当前能力（已打通）

```
DB职业数据 ─┬─ LLM大纲(claude/openai/deepseek, 字数受控+语气词)
            │      → [Web界面 预览/审批]
            ├─ slides.py 每场景渲染一张全画幅"幻灯片"PNG(图表/实拍图/数据可视化)
            ├─ tts.py Azure SSML 配音(Yunyang专业播音, 数字重音) + 词级字幕
            └─→ Remotion: 幻灯片当背景 <Img> + 字幕 + 音频 → 同步视频(方案C)

另有独立产物：ppt_builder.py → 11 页职业 PPTX(给人看)
```

视频画面 = 幻灯片，与配音/字幕**天然同步**，不再纯文字。

---

## 二、运行环境（不变）

| 项 | 值 |
|---|---|
| conda 环境 | `career-video`（Python 3.12）@ `e:\run\conda_envs\career-video` |
| 数据库 | MySQL `192.168.194.135:**13306**`，库 `career_guides_au`（VM 偶尔停，先确认服务起来） |
| Remotion | `video_pipeline/remotion`，4.0.475，Node v20.10 |
| 启动脚本（ASCII，双击） | `start_python_web.bat`（界面 :8000）/ `start_node_studio.bat`（Studio :3000） |
| 新增依赖 | openai, python-pptx, pillow, matplotlib, requests（均已装；见 requirements.txt） |

> **PowerShell+conda 坑**：`conda run python -c "多行"` 会报错；用 `python -m` 或临时 .py。
> 中文输出加 `$env:PYTHONUTF8=1` + `--no-capture-output`。
> **改任何代码/.env 后必须重启 Web 服务**（config 启动时读，uvicorn 不热重载）。

---

## 三、代码结构 `video_pipeline/`

| 文件 | 职责 |
|---|---|
| `config.py` | .env + 路径；LLM provider / Azure TTS / 渲染并行度 / SLIDES_DIR |
| `data_source.py` | MySQL → 单职业数据（含 salaries/ratings/visa/**suitability/education/qualifications**/growth/summary） |
| `prompts.py` | 大纲 prompt + `OUTLINE_SCHEMA`；`SCENE_IDS`=title,summary,salary,education,qualifications,ratings,visa,growth,suitability,cta |
| `llm.py` | 大纲后端分派 claude/openai/deepseek，统一 `complete_json()` |
| `scriptwriter.py` | 调 llm 生成大纲 → 写 `platform_contents`(reviewing) |
| `content_store.py` | platform_contents / video_jobs 读写、审批状态 |
| `charts.py` | 薪资折线图 / 需求柱状图（过去5年+未来5年**估算**，预测段琥珀高亮）；`draw_salary/draw_demand(ax)` 供幻灯片复用 |
| `images.py` | Pexels 职业图搜索下载（需 PEXELS_API_KEY，已配） |
| `slides.py` | **每场景渲染全画幅幻灯片 PNG**（9:16/16:9）；`_DISPATCH` 按场景 id 分派 |
| `spec_builder.py` | 每场景：配音+渲幻灯片+配图 → spec.json（scene 带 `bgImage`/`audioSrc`/`captions`/`durationSec`） |
| `tts.py` | Azure SSML 配音 + 词级字幕；**超时阈值放宽 + 失败重试3次** |
| `renderer.py` | 调 Remotion CLI 渲染（`--concurrency` 默认80%），管理 video_jobs |
| `ppt_builder.py` | 11 页 PPTX：标题/概览/收入折线/需求柱/薪资表/教育路径/从业资质/评分/签证/增长/CTA |
| `web/app.py` + templates | FastAPI 界面（列表/生成/预览/审批/渲染/下载） |
| `remotion/` | schema.ts（scene 含 bgImage）/ VideoRoot.tsx（bgImage 整幅背景 + 字幕 + 音频） |

复用表：`platform_contents`(大纲+审批) / `video_jobs`(渲染) / `publish_metadata`(发布)。

PPT 技能：`.claude/skills/occupation-ppt/SKILL.md` → 调 `python -m video_pipeline.ppt_builder <occId>`。

---

## 四、本会话完成

1. **职业 PPT 技能**（occupation-ppt）：11 页有图有表 PPTX，Pexels 配图。
2. **趋势图表**：收入(折线)/需求(柱状) 过去5+未来5年估算，含"非官方估算"声明；标题带职业名。
3. **方案C 合二为一**：slides.py 每场景出全画幅幻灯片图 → Remotion 当背景；视频=幻灯片+配音+字幕，同步、不再纯文字。
4. **场景专属布局**：title(实拍图)/summary(图+文)/salary(折线)/ratings(横向评分条)/visa/growth(图+要点)/**suitability(适合·不适合双栏)**/**education(阶段+时长+费用)**/**qualifications(必备·可选)**/cta；其余落通用渲染器走 broll 实拍图背景。
5. **修复**：Azure TTS 超时(放宽阈值+重试)、JSONDecodeError(结构化输出)、评分页缺维度名、`$`被matplotlib当公式解析、教育页溢出、.bat GBK 乱码、Remotion 升级 4.0.0→4.0.475。

---

## 五、⚠️ 待办 / 重要提醒

1. **`.env` 音色**：`AZURE_VOICE_ZH` 可能仍是 Xiaoxiao；要专业男声播音改成 `zh-CN-YunyangNeural`。
2. **新场景(教育/资质)进视频需重新生成大纲**：PPT 自动有这两页；但视频场景来自 LLM 大纲，**已有旧大纲不含**，要对该职业在界面**重新「生成大纲」→审批→渲染**（prompt 已更新会包含）。
3. 改代码后**重启 Web 服务**。

---

## 六、下一步（按价值）

- [ ] **批量渲染（Remotion bundle 复用）** ⭐：现每条都重新 esbuild 打包(15~30s)。打包一次循环渲全部职业，规模化关键提速。
- [ ] 验证"教育路径/从业资质"在重生成大纲后的视频里效果（用户上次问要不要重渲 content 9，未执行）。
- [ ] 真实时间序列替换图表估算（JSA 就业预测 / ABS 薪资）。
- [ ] 发布自动化（YouTube/TikTok/IG API + publish_metadata）。
- [ ] 小优化：Web `--reload`、职业搜索框、界面显示当前 provider/model、清理 out/ppt 下 _v2/_v3/_v4/_fixed 临时产物。
- [ ] （更早）Score 精细化、NZ 扩展。

---

## 七、充值后自检命令

```powershell
# DB + 职业数
conda run --no-capture-output -n career-video python -c "from video_pipeline.data_source import list_occupations; print(len(list_occupations()))"
# 当前 LLM provider
conda run --no-capture-output -n career-video python -c "from video_pipeline import llm,config; print(config.LLM_PROVIDER, llm.current_model())"
# 生成一个职业 PPT（occId 用 occupations.id）
conda run --no-capture-output -n career-video python -m video_pipeline.ppt_builder 118
# 起界面
.\start_python_web.bat
```

> 恢复任务直接说「读取 docs/session-handoff-2026-06-14.md 继续」。
