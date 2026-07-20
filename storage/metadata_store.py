"""
元数据存储 —— 云端版 (Supabase)
"""

import time
import uuid
from storage.db import table


def add_note(content_preview: str, tags: list[str] = None,
             source: str = "user_input", importance: str = "normal") -> str:
    note_id = f"note_{uuid.uuid4().hex[:8]}"
    table("notes").insert({
        "id": note_id,
        "preview": content_preview[:200],
        "tags": tags or [],
        "source": source,
        "importance": importance,
        "created_at": time.time(),
        "last_accessed": time.time(),
        "access_count": 0,
    }).execute()
    return note_id


def update_access(note_id: str):
    row = table("notes").select("access_count").eq("id", note_id).execute()
    if row.data:
        cnt = row.data[0].get("access_count", 0) + 1
        table("notes").update({
            "last_accessed": time.time(),
            "access_count": cnt,
        }).eq("id", note_id).execute()


def get_note(note_id: str) -> dict | None:
    res = table("notes").select("*").eq("id", note_id).execute()
    return res.data[0] if res.data else None


def list_notes() -> list[dict]:
    res = table("notes").select("*").order("created_at", desc=True).execute()
    return res.data


def delete_note(note_id: str) -> bool:
    res = table("notes").delete().eq("id", note_id).execute()
    return True


def search_by_tags(tags: list[str]) -> list[dict]:
    res = table("notes").select("*").execute()
    return [n for n in res.data if any(t in (n.get("tags") or []) for t in tags)]


def count() -> int:
    res = table("notes").select("id", count="exact").execute()
    return len(res.data)
