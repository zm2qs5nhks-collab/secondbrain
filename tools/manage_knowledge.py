"""
知识管理工具 —— 列表/删除
"""

import json
from storage import metadata_store


def get_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "manage_knowledge",
            "description": "管理知识库中的笔记。支持列出所有笔记、删除指定笔记、查看笔记详情。",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "delete", "detail", "count"],
                        "description": "操作类型：list=列出所有, delete=删除, detail=查看详情, count=统计数量",
                    },
                    "note_id": {
                        "type": "string",
                        "description": "笔记ID（删除和查看详情时必填）",
                    },
                },
                "required": ["action"],
            },
        },
    }


def execute(arguments: dict) -> str:
    action = arguments.get("action", "list")
    note_id = arguments.get("note_id", "")

    if action == "list":
        notes = metadata_store.list_notes()
        items = []
        for n in notes:
            items.append({
                "id": n["id"],
                "preview": n["preview"],
                "tags": n["tags"],
                "importance": n["importance"],
                "access_count": n["access_count"],
            })
        return json.dumps({
            "status": "success",
            "count": len(items),
            "notes": items,
        }, ensure_ascii=False)

    elif action == "delete":
        if not note_id:
            return json.dumps({"error": "需要提供 note_id"}, ensure_ascii=False)
        ok = metadata_store.delete_note(note_id)
        if ok:
            return json.dumps({"status": "success", "message": f"已删除 {note_id}"}, ensure_ascii=False)
        return json.dumps({"error": f"未找到 {note_id}"}, ensure_ascii=False)

    elif action == "detail":
        if not note_id:
            return json.dumps({"error": "需要提供 note_id"}, ensure_ascii=False)
        note = metadata_store.get_note(note_id)
        if note:
            return json.dumps({"status": "success", "note": note}, ensure_ascii=False)
        return json.dumps({"error": f"未找到 {note_id}"}, ensure_ascii=False)

    elif action == "count":
        c = metadata_store.count()
        return json.dumps({"status": "success", "count": c}, ensure_ascii=False)

    return json.dumps({"error": f"未知操作: {action}"}, ensure_ascii=False)
