"""
配置管理模块
"""

import os
import ssl
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-v4-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# 单次 LLM/Embedding 请求超时（秒）与重试次数，避免长任务把工具调用拖到客户端超时
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "1"))
# 单次生成的最大 token（长笔记抽取 JSON 可能被默认值截断）
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
# 遇到 429 限流时的额外重试次数（每次退避等待）
LLM_RATE_RETRIES = int(os.getenv("LLM_RATE_RETRIES", "3"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "secondbrain")
DB_USER = os.getenv("DB_USER", "secondbrain")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")

# 对外暴露的 API/MCP 基地址（用于在网页里展示给用户接入智能体），如 http://39.96.27.17:8000
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

AGENT_MAX_ITERATIONS = 5
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50
RAG_TOP_K = 5
