"""
长期记忆 —— PostgreSQL 版
"""

import json
from storage.db import query_one, query_all, execute
from storage.crypto import encrypt, decrypt, is_encrypted

_SENSITIVE_KEYS = {"api_key"}


def update_preference(key: str, value, user_id: str = None):
    if key in _SENSITIVE_KEYS and isinstance(value, str) and value and not is_encrypted(value):
        value = encrypt(value)

    if user_id:
        existing = query_one("SELECT key FROM user_prefs WHERE key = %s AND user_id = %s", (key, user_id))
    else:
        existing = query_one("SELECT key FROM user_prefs WHERE key = %s", (key,))

    if existing:
        if user_id:
            execute("UPDATE user_prefs SET value = %s WHERE key = %s AND user_id = %s",
                    (json.dumps(value, ensure_ascii=False), key, user_id))
        else:
            execute("UPDATE user_prefs SET value = %s WHERE key = %s",
                    (json.dumps(value, ensure_ascii=False), key))
    else:
        row_data = {"key": key, "value": json.dumps(value, ensure_ascii=False)}
        if user_id:
            row_data["user_id"] = user_id
        cols = ", ".join(row_data.keys())
        vals = ", ".join(["%s"] * len(row_data))
        execute(f"INSERT INTO user_prefs ({cols}) VALUES ({vals})", list(row_data.values()))


def get_preference(key: str, default=None, user_id: str = None):
    if user_id:
        row = query_one("SELECT value FROM user_prefs WHERE key = %s AND user_id = %s", (key, user_id))
    else:
        row = query_one("SELECT value FROM user_prefs WHERE key = %s", (key,))
    if row:
        raw = row["value"]
        if isinstance(raw, str):
            try:
                decoded = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                decoded = raw
        else:
            decoded = raw
        if key in _SENSITIVE_KEYS and isinstance(decoded, str) and is_encrypted(decoded):
            result = decrypt(decoded)
            if result.startswith("ENC:"):
                return default
            return result
        return decoded
    return default


def add_topic(topic: str, related_notes: list[str] = None, user_id: str = None):
    if user_id:
        existing = query_one("SELECT * FROM topics WHERE topic = %s AND user_id = %s", (topic, user_id))
    else:
        existing = query_one("SELECT * FROM topics WHERE topic = %s", (topic,))

    if existing:
        old_notes = existing.get("related_notes") or []
        new_notes = list(set(old_notes + (related_notes or [])))
        if user_id:
            execute("UPDATE topics SET related_notes = %s, count = count + 1 WHERE topic = %s AND user_id = %s",
                    (json.dumps(new_notes, ensure_ascii=False), topic, user_id))
        else:
            execute("UPDATE topics SET related_notes = %s, count = count + 1 WHERE topic = %s",
                    (json.dumps(new_notes, ensure_ascii=False), topic))
    else:
        row_data = {
            "topic": topic,
            "related_notes": json.dumps(related_notes or [], ensure_ascii=False),
            "count": 1,
        }
        if user_id:
            row_data["user_id"] = user_id
        cols = ", ".join(row_data.keys())
        vals = ", ".join(["%s"] * len(row_data))
        execute(f"INSERT INTO topics ({cols}) VALUES ({vals})", list(row_data.values()))


def get_context_summary(user_id: str = None) -> str:
    if user_id:
        topics_res = query_all("SELECT topic, count FROM topics WHERE user_id = %s", (user_id,))
        notes_count_row = query_one("SELECT COUNT(*) AS cnt FROM notes WHERE user_id = %s", (user_id,))
    else:
        topics_res = query_all("SELECT topic, count FROM topics")
        notes_count_row = query_one("SELECT COUNT(*) AS cnt FROM notes")

    notes_count = notes_count_row["cnt"] if notes_count_row else 0
    topics = [t["topic"] for t in topics_res]

    lines = ["[长期记忆]"]
    lines.append(f"  知识库共 {notes_count} 条笔记")
    if topics:
        lines.append(f"  常关注主题: {', '.join(topics[:10])}")
    return "\n".join(lines)


def get_all_topics(user_id: str = None) -> list[str]:
    if user_id:
        rows = query_all("SELECT topic FROM topics WHERE user_id = %s", (user_id,))
    else:
        rows = query_all("SELECT topic FROM topics")
    return [t["topic"] for t in rows]
