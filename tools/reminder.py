"""
提醒推送工具
"""

import json
from scheduler import forgetting_curve as fc
from storage import metadata_store


def get_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "send_reminder",
            "description": "检查知识库中需要复习的内容并生成提醒。当用户问'有什么需要复习的'、'提醒我'、'今日提醒'时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "number",
                        "description": "遗忘阈值(0-1)，低于此值的笔记会被提醒，默认0.5",
                    },
                },
            },
        },
    }


def execute(arguments: dict) -> str:
    threshold = arguments.get("threshold", 0.5)
    reminders = fc.get_notes_for_review(threshold=threshold)

    if not reminders:
        return json.dumps({
            "status": "success",
            "message": "目前没有需要复习的内容，继续保持！",
            "reminders": [],
        }, ensure_ascii=False)

    formatted = []
    for r in reminders[:5]:
        note = metadata_store.get_note(r["note_id"])
        preview = note["preview"] if note else "未知内容"
        formatted.append({
            "note_id": r["note_id"],
            "preview": preview,
            "urgency": r["urgency"],
            "retention": f"{r['retention']*100:.0f}%",
            "days_since_review": r["days_since_review"],
            "review_count": r["review_count"],
        })

    return json.dumps({
        "status": "success",
        "count": len(formatted),
        "reminders": formatted,
    }, ensure_ascii=False)
