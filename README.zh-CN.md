# HealthMate

<p align="center">
  <img src="assets/logo.svg" alt="HealthMate" width="700">
</p>

HealthMate 是一个桌面陪伴式个人健康 AI 助手。后端基于 FastAPI + LangGraph，前端是 Electron 桌宠。

宠物会陪你聊天、记住你的健康档案、每天自动归档对话内容，还会主动提醒你活动、吃饭和休息，并支持免按键的语音对话。

## 演示

<p align="center">
  <img src="https://private-user-images.githubusercontent.com/140865719/643078366-ac7e925a-d94a-4e76-b92d-f61aa3558a4b.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODc5OTE5NjEsIm5iZiI6MTc4Nzk5MTY2MSwicGF0aCI6Ii8xNDA4NjU3MTkvNjQzMDc4MzY2LWFjN2U5MjVhLWQ5NGEtNGU3Ni1iOTJkLWY2MWFhMzU1OGE0Yi5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODI5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgyOVQwODIxMDFaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT01Njk4OWI3NTlkZTM5YmViZGM3NjhlYmY1M2NlZWJkYmRlMjVmODYwYWRkNmNiODQ2N2ViNjczMzc5ZGUxNWFhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZnaWYifQ.11wXATmY-HbyIYCjjyGmSLSYEympnUae_MInq4FP5NU" alt="智能体功能演示" width="720">
  <br><em>智能体功能演示</em>
</p>

<p align="center">
  <img src="https://private-user-images.githubusercontent.com/140865719/643078405-0807fd29-cd88-4295-957c-e8eba4eef373.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODc5OTE5NjEsIm5iZiI6MTc4Nzk5MTY2MSwicGF0aCI6Ii8xNDA4NjU3MTkvNjQzMDc4NDA1LTA4MDdmZDI5LWNkODgtNDI5NS05NTdjLWU4ZWJhNGVlZjM3My5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODI5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgyOVQwODIxMDFaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xYjU0MDA1Mzk4M2EyNWE4ZWY4MTVkODJjM2Y4N2E5ZDExZDIyOTcxNjU1ZGM5OWM3MmY1YzU3YmU0ZmJmYTU5JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZnaWYifQ.dzwnvx35QP4tWnmtOzB_mvwr88-oIzz98C_e_DLFLfI" alt="提醒功能演示" width="720">
  <br><em>提醒功能演示</em>
</p>

## 功能

- **桌面宠物** - 圆角矩形大眼睛、复古 CRT 扫描线屏幕效果、漫画式对话气泡。
- **多模型聊天** - 支持 OpenAI、DeepSeek、通义千问、Ollama 或任意 OpenAI 兼容接口；模型配置在界面中管理并本地保存。
- **语音对话模式** - 持续聆听 + 自动检测人声 + 3 秒静音自动截断，不用按键也能说话。
- **语音识别与合成** - faster-whisper（base 模型）做 ASR，edge-tts 做 TTS，并支持按句流式合成降低延迟。
- **多 Agent LangGraph 流水线** - 数据分析师（总控）、记忆 Agent（归档）、知识 Agent（档案 + 联网检索工具）。
- **健康档案** - 年龄、性别、身高、体重、慢性病、过敏史、用药、饮食、运动、睡眠、吸烟、饮酒、目标。
- **每日归档** - 每天对话结束后自动生成摘要、关键信息、情绪、关注点和建议。
- **历史搜索** - 按日期和关键词查找过往对话。
- **健康看板** - 基于归档对话的趋势图表。
- **主动提醒** - 久坐提醒、饭点提醒、睡前提醒。

## 技术栈

- Python 3.12+
- FastAPI
- LangGraph / LangChain Core
- Pydantic
- SQLite + SQLAlchemy
- faster-whisper（ASR）
- edge-tts（TTS）
- Electron（桌宠）
- Chart.js（看板）

## 项目结构

```text
HealthMate/
├── app/
│   ├── agent/          # LangGraph 多 Agent 流水线
│   │   ├── graph.py    # 图组装：supervisor -> tools -> archiver
│   │   ├── state.py    # Agent 状态定义
│   │   └── nodes/      # supervisor（数据分析师）、archiver（记忆 Agent）
│   ├── agents/         # LangChain 工具（档案读取、联网健康知识检索）
│   ├── api/            # FastAPI 路由（聊天、语音、档案、归档）
│   ├── core/           # 配置、日志、异常
│   ├── database/       # SQLAlchemy 模型、CRUD、SQLite 连接
│   ├── llm/            # 统一 LLM Provider 抽象
│   ├── schemas/        # Pydantic 请求/响应模型
│   ├── voice/          # faster-whisper ASR + edge-tts TTS
│   └── main.py         # FastAPI 入口
├── electron/           # 桌面宠物外壳
│   ├── main.js         # Electron 主进程
│   ├── preload.js      # IPC 桥接
│   └── start-pet.sh    # 一键启动脚本
├── static/             # 前端（index.html）
├── tests/              # Pytest 测试
├── .env.example        # 环境变量模板
├── pyproject.toml
└── uv.lock
```

## 快速开始

### 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)（推荐）或 pip
- Node.js + npx（仅 Electron 桌宠需要）

### 安装依赖

```bash
cd HealthMate
uv sync --extra dev
```

或使用 pip：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 配置

```bash
cp .env.example .env
```

编辑 `.env`，至少填写一个 LLM Provider 的密钥。之后也可以直接在应用设置面板里添加多个模型。

### 启动

仅启动后端（浏览器访问 `http://localhost:8000`）：

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动桌宠（会自动拉起后端）：

```bash
cd electron
bash start-pet.sh
```

### 运行测试

```bash
uv run pytest tests/ -q
```

## 环境变量

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `LLM_PROVIDER` | 默认 Provider：`openai`、`deepseek`、`qwen`、`ollama` | `openai` |
| `OPENAI_API_KEY` | OpenAI / 兼容 API 密钥 | - |
| `OPENAI_BASE_URL` | OpenAI / 兼容 Base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | OpenAI 模型名 | `gpt-4o-mini` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `DEEPSEEK_BASE_URL` | DeepSeek Base URL | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | DeepSeek 模型名 | `deepseek-chat` |
| `QWEN_API_KEY` | 通义千问（DashScope）API 密钥 | - |
| `QWEN_BASE_URL` | 通义千问兼容 Base URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `QWEN_MODEL` | 通义千问模型名 | `qwen-turbo` |
| `OLLAMA_BASE_URL` | Ollama Base URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama 模型名 | `llama3.2` |
| `APP_HOST` | 后端监听地址 | `0.0.0.0` |
| `APP_PORT` | 后端监听端口 | `8000` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## API

所有路由前缀为 `/api/v1`。

| 方法 | 端点 | 说明 |
| --- | --- | --- |
| `POST` | `/chat` | 发送消息并返回回复 |
| `POST` | `/chat/stream` | SSE 逐 token 流式聊天 |
| `POST` | `/asr` | 音频转文字（WAV / WebM / MP3） |
| `POST` | `/tts` | 文本合成 MP3 音频 |
| `GET` | `/profile` | 获取健康档案 |
| `PUT` | `/profile` | 创建或更新健康档案 |
| `DELETE` | `/profile` | 删除健康档案 |
| `GET` | `/profile/check` | 检查档案是否存在 |
| `GET` | `/archives` | 按关键词、年份、月份搜索归档 |
| `GET` | `/archives/{date}` | 获取某天完整归档 |
| `DELETE` | `/archives/{date}` | 删除某天归档 |
| `GET` | `/health` | 健康检查 |

## Agent 架构

对话运行在编译好的 LangGraph 状态图上：

```text
START
  │
  ▼
supervisor（数据分析师）
  │
  ├─ 需要调用工具？──► tools（档案读取 / 知识检索）
  │                        │
  │                        └──► 回到 supervisor
  │
  ▼
archiver（记忆 Agent）
  │
  ▼
END
```

- **数据分析师（supervisor）** - 主对话 Agent，决定是否调用工具并回应用户。
- **知识 Agent（tools）** - 提供用户健康档案，必要时联网检索权威健康参考资料。
- **记忆 Agent（archiver）** - 每轮对话结束后写入当日归档，包含摘要、关键信息、情绪、关注点和建议。

## 路线图

- 更丰富的长期记忆与多日趋势分析
- 基于个人健康记录的检索增强生成（RAG）
- 更多主动健康干预与定时检查
- 扩展多 Agent 系统，加入专门的规划器和总结器
