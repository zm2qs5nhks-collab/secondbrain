"""
MCP 服务器 —— 把 tools/* 暴露为标准 MCP 工具

- 复用 tools/*.execute(arguments, user_id)，逻辑零改动
- 多用户鉴权：客户端在 HTTP 头携带 `Authorization: Bearer <api_token>`
- 工具描述复用 tools/*.get_schema()，避免重复维护
- 挂载方式见 api.py：FastAPI lifespan 运行 session_manager，并 mount 到 /mcp
"""

import json
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP, Context

from storage.api_tokens import verify_token
from tools import (
    add_knowledge,
    search_knowledge,
    manage_knowledge,
    reminder,
    fetch_web,
    knowledge_graph_tool,
)

try:
    from mcp.server.transport_security import TransportSecuritySettings

    # 部署在公网/反向代理后时，关闭 DNS rebinding 的 Host 白名单（鉴权由 Bearer token 负责）
    _TRANSPORT_SECURITY = TransportSecuritySettings(enable_dns_rebinding_protection=False)
except Exception:  # pragma: no cover
    _TRANSPORT_SECURITY = None

_MODULES = {
    "add_knowledge": add_knowledge,
    "search_knowledge": search_knowledge,
    "manage_knowledge": manage_knowledge,
    "send_reminder": reminder,
    "fetch_web_content": fetch_web,
    "knowledge_graph": knowledge_graph_tool,
}
_FUNCS = {name: mod.get_schema()["function"] for name, mod in _MODULES.items()}


def _desc(name: str) -> str:
    return _FUNCS[name]["description"]


def _user_id(ctx: Context) -> str:
    """从当前 MCP 请求的 HTTP 头解析并校验 API Token"""
    req = getattr(ctx.request_context, "request", None)
    auth = ""
    if req is not None:
        try:
            auth = req.headers.get("authorization", "") or ""
        except Exception:
            auth = ""
    user_id = verify_token(auth)
    if not user_id:
        raise ValueError("未授权：请在请求头携带 Authorization: Bearer <api_token>")
    return user_id


def _call(name: str, arguments: dict, ctx: Context) -> str:
    user_id = _user_id(ctx)
    try:
        return _MODULES[name].execute(arguments, user_id=user_id)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"}, ensure_ascii=False)


mcp = FastMCP(
    "second-brain",
    instructions=(
        "个人知识管理助手（第二大脑）。可保存/检索笔记、管理知识库、"
        "基于遗忘曲线给出复习提醒、抓取网页入库、操作知识图谱。"
        "所有操作都作用于当前 API Token 对应的用户。"
    ),
    streamable_http_path="/",
    transport_security=_TRANSPORT_SECURITY,
)


@mcp.tool(name="add_knowledge", description=_desc("add_knowledge"))
def add_knowledge_tool(
    ctx: Context,
    content: str,
    tags: Optional[list[str]] = None,
    importance: Literal["high", "normal", "low"] = "normal",
) -> str:
    return _call("add_knowledge", {"content": content, "tags": tags or [], "importance": importance}, ctx)


@mcp.tool(name="search_knowledge", description=_desc("search_knowledge"))
def search_knowledge_tool(ctx: Context, query: str, top_k: int = 5) -> str:
    return _call("search_knowledge", {"query": query, "top_k": top_k}, ctx)


@mcp.tool(name="manage_knowledge", description=_desc("manage_knowledge"))
def manage_knowledge_tool(
    ctx: Context,
    action: Literal["list", "delete", "detail", "count"],
    note_id: str = "",
) -> str:
    return _call("manage_knowledge", {"action": action, "note_id": note_id}, ctx)


@mcp.tool(name="send_reminder", description=_desc("send_reminder"))
def send_reminder_tool(ctx: Context, threshold: float = 0.5) -> str:
    return _call("send_reminder", {"threshold": threshold}, ctx)


@mcp.tool(name="fetch_web_content", description=_desc("fetch_web_content"))
def fetch_web_content_tool(ctx: Context, url: str, tags: Optional[list[str]] = None) -> str:
    return _call("fetch_web_content", {"url": url, "tags": tags or []}, ctx)


@mcp.tool(name="knowledge_graph", description=_desc("knowledge_graph"))
def knowledge_graph_tool_fn(
    ctx: Context,
    action: Literal["add", "query", "discover", "stats"],
    content: str = "",
    node: str = "",
    max_hops: int = 2,
) -> str:
    return _call(
        "knowledge_graph",
        {"action": action, "content": content, "node": node, "max_hops": max_hops},
        ctx,
    )
