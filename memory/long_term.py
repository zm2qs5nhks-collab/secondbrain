"""
长期记忆 —— 云端版 (Supabase)
"""

from storage.db import table


def update_preference(key: str, value):
    existing = table("user_prefs").select("*").eq("key", key).execute()
    if existing.data:
        table("user_prefs").update({"value": value}).eq("key", key).execute()
    else:
        table("user_prefs").insert({"key": key, "value": value}).execute()


def get_preference(key: str, default=None):
    res = table("user_prefs").select("value").eq("key", key).execute()
    if res.data:
        return res.data[0]["value"]
    return default


def add_topic(topic: str, related_notes: list[str] = None):
    existing = table("topics").select("*").eq("topic", topic).execute()
    if existing.data:
        old_notes = existing.data[0].get("related_notes") or []
        new_notes = list(set(old_notes + (related_notes or [])))
        table("topics").update({
            "related_notes": new_notes,
            "count": existing.data[0].get("count", 0) + 1,
        }).eq("topic", topic).execute()
    else:
        table("topics").insert({
            "topic": topic,
            "related_notes": related_notes or [],
            "count": 1,
        }).execute()


def get_context_summary() -> str:
    topics_res = table("topics").select("topic, count").execute()
    notes_count_res = table("notes").select("id", count="exact").execute()
    notes_count = len(notes_count_res.data)
    topics = [t["topic"] for t in (topics_res.data or [])]

    lines = ["[长期记忆]"]
    lines.append(f"  知识库共 {notes_count} 条笔记")
    if topics:
        lines.append(f"  常关注主题: {', '.join(topics[:10])}")
    return "\n".join(lines)


def get_all_topics() -> list[str]:
    res = table("topics").select("topic").execute()
    return [t["topic"] for t in (res.data or [])]
