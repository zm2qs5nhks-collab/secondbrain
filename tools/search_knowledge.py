"""
知识检索工具
"""

import json
from storage import vector_store, metadata_store
from scheduler import forgetting_curve as fc


def get_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "从知识库中搜索相关知识。当用户询问'我学过XX吗'、'找一下关于XX的内容'、'XX相关笔记'时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询内容",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回的结果数量，默认5",
                    },
                },
                "required": ["query"],
            },
        },
    }


def execute(arguments: dict) -> str:
    query = arguments.get("query", "")
    top_k = arguments.get("top_k", 5)

    if not query.strip():
        return json.dumps({"error": "搜索内容不能为空"}, ensure_ascii=False)

    results = vector_store.search(query, top_k=top_k)

    if not results:
        return json.dumps({
            "status": "empty",
            "message": "知识库中没有找到相关内容",
            "results": [],
        }, ensure_ascii=False)

    formatted = []
    for i, r in enumerate(results, 1):
        source = r["metadata"].get("source", "未知")
        score = round(1 - r["distance"], 2)
        formatted.append({
            "rank": i,
            "content": r["content"],
            "source": source,
            "relevance_score": score,
        })

    return json.dumps({
        "status": "success",
        "count": len(formatted),
        "results": formatted,
    }, ensure_ascii=False)
