"""
API Token —— 供 REST / MCP 外部调用鉴权

- 明文 token 只在创建时返回一次，数据库仅存 sha256 哈希
- token 形如 sb_xxxxxxxx...
"""

import hashlib
import secrets

from storage.db import query_one, query_all, execute, execute_returning

PREFIX = "sb_"


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_token(user_id: str, name: str = "default") -> str:
    """为用户创建一个 API Token，返回明文（仅此一次可见）"""
    token = PREFIX + secrets.token_urlsafe(32)
    execute_returning(
        "INSERT INTO api_tokens (user_id, name, token_prefix, token_hash) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (user_id, name, token[:10], _hash(token)),
    )
    return token


def verify_token(token: str) -> str | None:
    """校验 token，有效则返回 user_id，否则 None"""
    if not token:
        return None
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token:
        return None
    row = query_one(
        "SELECT user_id FROM api_tokens WHERE token_hash = %s AND revoked = FALSE",
        (_hash(token),),
    )
    if not row:
        return None
    execute(
        "UPDATE api_tokens SET last_used_at = EXTRACT(EPOCH FROM NOW()) WHERE token_hash = %s",
        (_hash(token),),
    )
    return str(row["user_id"])


def list_tokens(user_id: str) -> list[dict]:
    return query_all(
        "SELECT id, name, token_prefix, created_at, last_used_at, revoked "
        "FROM api_tokens WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,),
    )


def revoke_token(user_id: str, token_id: str) -> bool:
    row = query_one(
        "SELECT id FROM api_tokens WHERE id = %s AND user_id = %s",
        (token_id, user_id),
    )
    if not row:
        return False
    execute(
        "UPDATE api_tokens SET revoked = TRUE WHERE id = %s AND user_id = %s",
        (token_id, user_id),
    )
    return True
