"""
配置管理模块
"""

import os
import certifi

# 让 requests / urllib 使用 certifi 的 CA 包（企业内网自签证书可另配环境变量）
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
# 注意：这里绝不能设置 ssl._create_unverified_context —— 那会全局关闭
# HTTPS 证书校验，任何网络位置都能截获 LLM API Key。

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
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "8192"))
# 遇到 429 限流时的额外重试次数（每次退避等待）
LLM_RATE_RETRIES = int(os.getenv("LLM_RATE_RETRIES", "3"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "secondbrain")
DB_USER = os.getenv("DB_USER", "secondbrain")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")

# 对外暴露的 API/MCP 基地址（用于在网页里展示给用户接入智能体），如 http://39.96.27.17:8000
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

# ── 站点形态 ──────────────────────────────────────────
# 是否允许公开注册。默认关闭：本站定位为「个人知识库，内容私有，仅本人登录使用」，
# 与备案时填写的"仅本人使用、不对外开放注册"保持一致。
ALLOW_SIGNUP = os.getenv("ALLOW_SIGNUP", "false").strip().lower() in ("1", "true", "yes", "on")

# 页脚备案号，如 京ICP备2026000000号-1；留空则不渲染
SITE_ICP = os.getenv("SITE_ICP", "")
# 页脚联系方式（邮箱/主页）；留空则不渲染
SITE_CONTACT = os.getenv("SITE_CONTACT", "")
# 站点名（页脚、邮件里用）
SITE_NAME = os.getenv("SITE_NAME", "第二大脑")

# ── 功能开关（下线不等于删代码，改 true 重启即恢复）──────────
def _flag(name: str, default: bool = False) -> bool:
    return os.getenv(name, "true" if default else "false").strip().lower() in (
        "1", "true", "yes", "on",
    )


# 智能问答（接入大模型对话）。暂时下线：既减少 AI 对外服务的合规面，也省 token
ENABLE_CHAT = _flag("ENABLE_CHAT", False)
# 设置页（API Key 配置、Token 生成、清空知识库）。暂时下线：不对外开放管理入口
ENABLE_SETTINGS = _flag("ENABLE_SETTINGS", False)

# ── 邮件（找回密码验证码）─────────────────────────────
# QQ 邮箱：SMTP_HOST=smtp.qq.com SMTP_PORT=465，SMTP_PASS 填「授权码」不是登录密码
# 未配置时找回密码会提示"邮件服务未配置"，其它功能不受影响
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "") or SMTP_USER
# 验证码有效期（秒）
RESET_CODE_TTL = int(os.getenv("RESET_CODE_TTL", "600"))

AGENT_MAX_ITERATIONS = 5
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50
RAG_TOP_K = 5
