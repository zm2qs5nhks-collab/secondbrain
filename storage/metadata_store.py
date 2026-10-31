"""
元数据存储 —— PostgreSQL 版
"""

import json
import time
import uuid
from storage.db import query_one, query_all, execute


def _first_line(text: str, limit: int = 80) -> str:
    for line in (text or "").replace("\r", "").split("\n"):
        line = line.strip()
        if line:
            return line[:limit]
    return ""


def add_note(content_preview: str = None, tags: list[str] = None,
             source: str = "user_input", importance: str = "normal",
             user_id: str = None, title: str = None, content: str = None) -> str:
    """新建一条笔记。

    v2：新增 title / content 两个字段。
    兼容旧调用——只传 content_preview 时，把它当作正文处理。
    """
    body = (content if content is not None else content_preview) or ""
    body = body.strip()
    title = (title or "").strip() or _first_line(body) or "未命名笔记"

    note_id = f"note_{uuid.uuid4().hex[:8]}"
    execute(
        """INSERT INTO notes (id, preview, tags, source, importance, user_id,
                              created_at, last_accessed, access_count, title, content)
           VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (note_id, body[:200], json.dumps(tags or [], ensure_ascii=False), source, importance,
         user_id, time.time(), time.time(), 0, title, body),
    )
    return note_id


def update_access(note_id: str, user_id: str = None):
    if user_id:
        execute(
            "UPDATE notes SET last_accessed = %s, access_count = access_count + 1 WHERE id = %s AND user_id = %s",
            (time.time(), note_id, user_id),
        )
    else:
        execute(
            "UPDATE notes SET last_accessed = %s, access_count = access_count + 1 WHERE id = %s",
            (time.time(), note_id),
        )


def get_note(note_id: str, user_id: str = None):
    if user_id:
        return query_one("SELECT * FROM notes WHERE id = %s AND user_id = %s", (note_id, user_id))
    return query_one("SELECT * FROM notes WHERE id = %s", (note_id,))


def list_notes(user_id: str = None):
    if user_id:
        return query_all("SELECT * FROM notes WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    return query_all("SELECT * FROM notes ORDER BY created_at DESC")


def delete_note(note_id: str, user_id: str = None) -> bool:
    from storage import vector_store
    vector_store.delete_by_note_id(note_id, user_id=user_id)
    if user_id:
        execute("DELETE FROM notes WHERE id = %s AND user_id = %s", (note_id, user_id))
    else:
        execute("DELETE FROM notes WHERE id = %s", (note_id,))
    return True


def search_by_tags(tags: list[str], user_id: str = None):
    if user_id:
        rows = query_all("SELECT * FROM notes WHERE user_id = %s", (user_id,))
    else:
        rows = query_all("SELECT * FROM notes")
    return [n for n in rows if any(t in (n.get("tags") or []) for t in tags)]


def count(user_id: str = None):
    if user_id:
        row = query_one("SELECT COUNT(*) AS cnt FROM notes WHERE user_id = %s", (user_id,))
    else:
        row = query_one("SELECT COUNT(*) AS cnt FROM notes")
    return row["cnt"] if row else 0
