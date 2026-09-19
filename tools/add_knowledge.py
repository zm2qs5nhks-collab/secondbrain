"""
知识入库工具
"""

import json
from storage import vector_store, document_parser, metadata_store
from storage.knowledge_graph import add_note_to_graph
from memory import long_term
from scheduler import forgetting_curve as fc


def get_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "add_knowledge",
            "description": "将知识内容保存到知识库。当用户想要保存笔记、记录学习内容、存储想法时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "要保存的知识内容",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "内容的标签/分类，如 ['Python', 'GIL', '多线程']",
                    },
                    "importance": {
                        "type": "string",
                        "enum": ["high", "normal", "low"],
                        "description": "内容的重要程度",
                    },
                },
                "required": ["content"],
            },
        },
    }


def execute(arguments: dict, user_id: str = None) -> str:
    content = arguments.get("content", "")
    tags = arguments.get("tags", [])
    importance = arguments.get("importance", "normal")

    if not content.strip():
        return json.dumps({"error": "内容不能为空"}, ensure_ascii=False)

    # tags 兼容：模型可能传字符串（如 "Python, 并发"）而非数组
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.replace("，", ",").split(",") if t.strip()]
    if not isinstance(tags, list):
        tags = []
    tags = [str(t) for t in tags]

    # ① 关键写入：保存笔记元数据。只有这一步失败才算整体失败
    note_id = metadata_store.add_note(
        content_preview=content,
        tags=tags,
        source="user_input",
        importance=importance,
        user_id=user_id,
    )

    # ② 后续步骤全部「尽力而为」：任何一步失败都不影响"笔记已保存"这一事实，
    #    否则会出现"笔记已入库、工具却报异常"的错位。
    warnings = []

    count = 0
    try:
        documents = document_parser.parse_text(content, source="user_input")
        count = vector_store.add_documents(documents, user_id=user_id, note_id=note_id)
    except Exception as e:
        warnings.append(f"分块入库失败: {type(e).__name__}: {e}")

    try:
        fc.record_access(note_id, user_id=user_id)
    except Exception as e:
        warnings.append(f"遗忘曲线记录失败: {type(e).__name__}: {e}")

    for tag in tags:
        try:
            long_term.add_topic(tag, [note_id], user_id=user_id)
        except Exception as e:
            warnings.append(f"主题[{tag}]记录失败: {type(e).__name__}: {e}")

    graph_result = {}
    try:
        graph_result = add_note_to_graph(content, user_id=user_id, note_id=note_id)
    except Exception as e:
        warnings.append(f"图谱抽取失败: {type(e).__name__}: {e}")

    payload = {
        "status": "success",
        "note_id": note_id,
        "chunks_stored": count,
        "tags": tags,
        "graph": graph_result,
        "message": f"已保存到知识库（{count}个分块）",
    }
    if warnings:
        payload["warnings"] = warnings
    return json.dumps(payload, ensure_ascii=False)
