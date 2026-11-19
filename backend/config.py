import os

# 旅游攻略智能体 - 配置文件
# 请在下方填入你的大模型API Key

# ============ 大模型配置 ============
# 支持 OpenAI / 智谱GLM / 通义千问 / 文心一言 等兼容OpenAI接口的模型
LLM_API_KEY = os.getenv("LLM_API_KEY", "")  # ← 请替换为你的API Key
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")  # 智谱GLM示例，可替换
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")  # 模型名称

# ============ Embedding配置 ============
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "")  # ← 请替换
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embedding-3")

# ============ 服务配置 ============
HOST = "0.0.0.0"
PORT = 8080
DEBUG = True

# ============ 知识库配置 ============
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "travel_guides"

# ============ MCP服务配置 ============
MCP_HOST = "0.0.0.0"
MCP_PORT = 9000
