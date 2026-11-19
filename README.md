# 旅游攻略智能体 · Travel Agent

> 基于 LangChain + RAG + 大模型的旅游攻略助手：智能对话、攻略检索/管理、多维度搜索、MCP 服务。Flask 后端 + 原生前端，支持 OpenAI 兼容接口（智谱 GLM / 通义千问等）。

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Agent-1C3C3C)
![Flask](https://img.shields.io/badge/Flask-3-000000?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2F6B5F)

---

## 功能

- **智能对话**：自然语言咨询旅游攻略
- **多维搜索**：目的地 / 标签 / 预算 / 季节
- **攻略管理**：浏览、添加、详情
- **RAG 检索**：ChromaDB 向量库语义检索
- **工具调用**：LangChain Agent 调用搜索/统计/添加等工具
- **MCP 服务**：可被其他 AI 应用调用
- **健康检查**：`/api/health`

---

## 技术栈

| 模块 | 技术 |
|---|---|
| 后端 | Python、Flask、Flask-CORS |
| LLM/RAG | LangChain、OpenAI 兼容接口、ChromaDB、Embedding |
| 前端 | HTML5 + CSS3 + 原生 JS |
| 工具协议 | MCP（Model Context Protocol） |

---

## 快速开始

### 1. 环境

- Python 3.10+
- 一个 OpenAI 兼容的大模型 API（如通义千问 DashScope）
- 可选：Embedding API

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# Windows PowerShell
$env:LLM_API_KEY="你的API Key"
$env:LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qwen-plus"
$env:EMBEDDING_API_KEY="你的Embedding Key"
$env:EMBEDDING_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:EMBEDDING_MODEL="embedding-3"
```

或复制 `.env.example` 为 `.env` 后自行加载（需 `python-dotenv`）。

> 仓库不包含任何真实 API Key；`backend/config.py` 只从环境变量读取。

### 3. 启动

```bash
cd backend
python app.py
```

打开 <http://localhost:8080>。

MCP 服务：

```bash
cd backend
python mcp/travel_mcp.py
# 默认 9000 端口
```

---

## 目录结构

```text
travel-agent/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── agent/            # LangChain agent / RAG / tools / prompts
│   ├── api/routes.py
│   ├── data/             # 攻略数据
│   └── mcp/travel_mcp.py
├── frontend/
│   ├── templates/index.html
│   └── static/css|js
├── scripts/run.sh
├── requirements.txt
├── .env.example
└── README.md
```

---

## API

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/chat` | POST | 对话 |
| `/api/welcome` | GET | 欢迎消息 |
| `/api/clear` | POST | 清空历史 |
| `/api/guides` | GET/POST | 攻略列表/新增 |
| `/api/guides/<id>` | GET | 攻略详情 |
| `/api/search?q=` | GET | 搜索 |
| `/api/stats` | GET | 统计 |
| `/api/health` | GET | 健康检查 |

---

## 测试与验收

```bash
# 语法检查
python -m py_compile backend/app.py backend/config.py backend/agent/*.py backend/api/*.py backend/data/*.py backend/mcp/*.py

# 启动后
curl http://localhost:8080/api/health
```

手工验收：

- [ ] 页面加载，欢迎语正常
- [ ] 输入“成都三天怎么玩”返回攻略
- [ ] 攻略列表/详情/新增
- [ ] 搜索按目的地/标签/预算/季节
- [ ] MCP 服务可启动

> 大模型问答需要有效 API Key；无 Key 时普通攻略浏览/搜索仍可演示。

---

## 安全说明

- API Key 仅从环境变量读取，仓库不保存。
- 生产环境请关闭 `DEBUG`、限制 CORS、加鉴权与限流。
- 攻略数据为示例数据，出行前请核实实时信息。

---

## License

MIT License，详见 [LICENSE](LICENSE)。
