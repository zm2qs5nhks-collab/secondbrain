"""
在线搜索工具 —— DuckDuckGo 搜索 + 一键入库
"""

import json
from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 8) -> list[dict]:
    """搜索并返回结果列表"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            })
        return formatted
    except Exception as e:
        return [{"error": str(e)}]
