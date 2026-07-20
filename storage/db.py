"""
Supabase 云数据库初始化与管理
替代本地 JSON + ChromaDB，所有数据存储在云端 PostgreSQL
"""

import os
from supabase import create_client, Client

_url = os.getenv("SUPABASE_URL", "")
_key = os.getenv("SUPABASE_KEY", "")
_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not _url or not _key:
            raise RuntimeError(
                "请配置 SUPABASE_URL 和 SUPABASE_KEY 环境变量。\n"
                "1. 去 https://supabase.com 免费注册\n"
                "2. 创建项目，获取 URL 和 anon key\n"
                "3. 在 .env 中填入"
            )
        _client = create_client(_url, _key)
    return _client


def table(name: str):
    return get_client().table(name)


def rpc(fn_name: str, params: dict = None):
    return get_client().rpc(fn_name, params or {})
