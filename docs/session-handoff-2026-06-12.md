# 会话交接 · 2026-06-12（视频流水线）

> 本会话主线：搭建并打磨「职业介绍视频自动生成流水线」`video_pipeline/`。
> 数据库里的 191 个 AU 职业入库工作已在更早会话完成（见 `session-handoff-2026-06-09.md` / `todo.md`）。

---

## 一、当前能力（已打通，可用）

完整链路：

```
DB职业数据 → LLM生成分场景大纲(字数受控/含语气词)
          → [Web界面 预览/编辑/审批]            ← 人在环中
          → Azure SSML 配音 + 词级字幕
          → Remotion 数据驱动渲染(并行)
          → 成片 mp4（有声、有烧录字幕）
```

一条竖屏短视频已验证：55 秒、AAC 音轨、烧录字幕、薪资动态条形图。

---

## 二、运行环境

| 项 | 值 |
|---|---|
| conda 环境 | `career-video`（Python 3.12），位于 `e:\run\conda_envs\career-video` |
| 数据库 | MySQL `192.168.194.135:13306`，库 `career_guides_au`（注意端口 13306，不是 3306） |
| Node/Remotion | `video_pipeline/remotion`，Remotion `4.0.475`，Node v20.10 |
| 启动脚本 | 根目录 `start_python_web.bat`（Web 界面）/ `start_node_studio.bat`（Remotion Studio）。**纯 ASCII**，双击运行 |

启动方式：
- 双击 `start_python_web.bat` → http://127.0.0.1:8000（生成大纲→审批→渲染→下载）
- 双击 `start_node_studio.bat` → http://localhost:3000（仅模板预览，生产不依赖它）
- 命令行：`conda run --no-capture-output -n career-video python -m video_pipeline.web.app`

> **PowerShell + conda 坑**：`conda run` 跑 `python -c "多行"` 会报 NotImplementedError；要么写临时 .py 文件，要么用 `python -m`。中文输出加 `$env:PYTHONUTF8=1` + `--no-capture-output` 避免 GBK 崩溃。

---

## 三、代码结构 `video_pipeline/`

| 文件 | 职责 |
|---|---|
| `config.py` | 读 `.env` + 路径；含 LLM provider、Azure TTS、渲染并行度等配置 |
| `data_source.py` | MySQL → 单职业结构化数据 |
| `prompts.py` | 大纲 prompt + `OUTLINE_SCHEMA`（结构化输出 schema）；含字数预算 + 中文语气词指令 |
| `llm.py` | **LLM 后端分派**：claude / openai / deepseek，统一 `complete_json()` |
| `scriptwriter.py` | 调 `llm` 生成大纲 → 写 `platform_contents`（状态 reviewing） |
| `content_store.py` | `platform_contents` / `video_jobs` 读写与审批状态流转 |
| `spec_builder.py` | 已审批大纲 + 数据 + 配音 → Remotion `inputProps.json`（唯一数据契约） |
| `tts.py` | Azure SSML 配音（音色/风格/语速/数字重音）+ 词级时间戳生成字幕 |
| `renderer.py` | 调 Remotion CLI 渲染（含 `--concurrency`），管理 `video_jobs` |
| `web/app.py` + templates | FastAPI 本地管理界面（列表/生成/预览/审批/渲染/下载） |
| `remotion/` | Remotion(TS) 工程：`schema.ts`、`VideoRoot.tsx`、scenes（Title/Salary/Generic/Captions） |

复用的 DB 表（更早设计好的）：`platform_contents`（大纲+审批状态 draft→reviewing→approved→published）、`video_jobs`（渲染任务）、`publish_metadata`（发布元信息）。

---

## 四、本会话完成的改动

1. **结构化输出修复 JSONDecodeError**：横屏长大纲曾因模型手写 JSON 混入未转义引号报错。改用各家结构化输出（Claude `output_config.format` / OpenAI `json_schema` strict / DeepSeek `json_object`）。
2. **多 LLM 后端**：`.env` 的 `LLM_PROVIDER=claude|openai|deepseek` 切换。默认 claude（Sonnet 4.6）。已装 `openai` SDK。
3. **音频 + 字幕接入 Remotion**：Azure 逐场景配音写到 `remotion/public/audio/`，`<Audio>` 接入；词级时间戳烧录字幕。
4. **真人解说调优**：SSML 支持音色/风格/语速/风格强度/数字重音（默认 `zh-CN-YunyangNeural` + `narration-professional`）；prompt 里让中文旁白自然点缀 2~3 处语气词（呢/嗯/呃/哦/嘛）。
5. **短视频长度预算**：prompt 限制中文≤240字，短视频落在 ~55 秒。
6. **渲染并行度**：`VIDEO_RENDER_CONCURRENCY` 默认 80%（24 核 → ~19 路）。
7. **Remotion 升级** 4.0.0 → 4.0.475（修了 Studio「打开文件」ENOENT）。
8. **两个 .bat 启动器**（ASCII，避免 GBK 乱码）。

---

## 五、⚠️ 待你处理的配置项

1. **Azure 音色还是旧值**：你 `.env` 里 `AZURE_VOICE_ZH` 仍是 `zh-CN-XiaoxiaoNeural`，而 `narration-professional` 是 Yunyang 的风格。要用上「专业男声播音」，把 `.env` 改成：
   ```
   AZURE_VOICE_ZH=zh-CN-YunyangNeural
   ```
2. **改 `.env` 或代码后要重启 Web 服务**（config 在启动时读取，uvicorn 不热重载）。

---

## 六、待办 / 下一步（按价值排序）

- [ ] **批量渲染（bundle 复用）** ⭐最关键：现在每条视频都重新 esbuild 打包（冷启动 15~30s）。用 Remotion `bundle()` 打包一次、循环渲染全部职业，摊销开销。规模化 191×2 条的核心提速。
- [ ] **更多数据动画场景**：`ratings`（星级/雷达）、`visa`（签证路径）、`growth`（增长领域）目前走通用文字卡片，做成专属动画提升专业度。
- [ ] **Pexels B-roll 自动插入**：按场景 `broll_hint` 检索实拍视频垫背景（需 `PEXELS_API_KEY`）。
- [ ] **发布自动化**：YouTube/TikTok/Instagram 上传 API + `publish_metadata`（各平台需审核开通）。
- [ ] **长视频(16:9) 流程完善** + 批量。
- [ ] 小优化：Web 加 `--reload`、职业名搜索框、界面显示当前 provider/model、`start_all.bat` 一键双开。
- [ ] （更早 todo）Score 精细化（方案B）、NZ 国家扩展。

---

## 七、快速自检命令（充值后验证环境还在）

```powershell
# DB 通不通 + 191 职业
conda run --no-capture-output -n career-video python -c "from video_pipeline.data_source import list_occupations; print(len(list_occupations()))"

# 当前 LLM provider
conda run --no-capture-output -n career-video python -c "from video_pipeline import llm,config; print(config.LLM_PROVIDER, llm.current_model())"

# 起界面
.\start_python_web.bat
```

> MySQL VM 偶尔会停（连接超时 192.168.194.135:13306）；先确认 VM 和 MySQL 服务起来了。
