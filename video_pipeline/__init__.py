"""视频流水线包：从职业数据生成多平台视频。

各模块职责：
- config        读取 .env 配置与路径
- data_source   从 MySQL 取单个职业的完整数据
- scriptwriter  调 Claude，把数据生成"分场景大纲"
- spec_builder  把已审批的大纲拼成 Remotion 的 inputProps.json
- tts           Azure 语音合成（音频 + 词级时间戳）
- renderer      调 Remotion CLI 渲染，管理 video_jobs
- web           FastAPI 本地管理界面（大纲预览/审批）
"""
