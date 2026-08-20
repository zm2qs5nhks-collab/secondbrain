"""
向量存储 —— PostgreSQL 版
"""

import json
from storage.db import query_one, query_all, execute


def add_documents(documents: list[dict], user_id: str = None, note_id: str = None) -> int:
    count = 0
    for doc in documents:
        content = doc["content"]
        metadata = doc.get("metadata", {})
        if note_id:
            metadata["note_id"] = note_id
        execute(
            """INSERT INTO note_embeddings (content, metadata, embedding, user_id)
               VALUES (%s, %s, %s, %s)""",
            (content, json.dumps(metadata, ensure_ascii=False), None, user_id),
        )
        count += 1
    return count


def search(query: str, top_k: int = 5, user_id: str = None) -> list[dict]:
    if user_id:
        rows = query_all("SELECT content, metadata FROM note_embeddings WHERE user_id = %s", (user_id,))
    else:
        rows = query_all("SELECT content, metadata FROM note_embeddings")

    results = []
    for row in rows:
        results.append({
            "content": row["content"],
            "metadata": row.get("metadata") or {},
            "distance": 0.5,
        })
    return results[:top_k]


def count(user_id: str = None):
    if user_id:
        row = query_one("SELECT COUNT(*) AS cnt FROM note_embeddings WHERE user_id = %s", (user_id,))
    else:
        row = query_one("SELECT COUNT(*) AS cnt FROM note_embeddings")
    return row["cnt"] if row else 0


def delete_all(user_id: str = None):
    if user_id:
        execute("DELETE FROM note_embeddings WHERE user_id = %s", (user_id,))
    else:
        execute("DELETE FROM note_embeddings")


def delete_by_note_id(note_id: str, user_id: str = None):
    all_rows = query_all("SELECT id, metadata FROM note_embeddings")
    ids_to_delete = []
    for row in all_rows:
        meta = row.get("metadata") or {}
        if meta.get("note_id") == note_id:
            if user_id:
                check = query_one("SELECT id FROM note_embeddings WHERE id = %s AND user_id = %s", (row["id"], user_id))
                if check:
                    ids_to_delete.append(row["id"])
            else:
                ids_to_delete.append(row["id"])
    for rid in ids_to_delete:
        execute("DELETE FROM note_embeddings WHERE id = %s", (rid,))


def get_note_full_content(note_id: str, user_id: str = None) -> str:
    all_rows = query_all("SELECT content, metadata FROM note_embeddings")
    chunks = []
    for row in all_rows:
        meta = row.get("metadata") or {}
        if meta.get("note_id") == note_id:
            chunks.append({
                "content": row["content"],
                "chunk_index": meta.get("chunk_index", 0),
            })
    if not chunks:
        return ""
    chunks.sort(key=lambda x: x["chunk_index"])
    return "\n\n".join(c["content"] for c in chunks)
