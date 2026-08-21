"""
向量存储 —— PostgreSQL 版
"""

import json
import numpy as np
from storage.db import query_one, query_all, execute


def add_documents(documents: list[dict], user_id: str = None, note_id: str = None) -> int:
    from agent.llm import get_embedding
    count = 0
    for doc in documents:
        content = doc["content"]
        metadata = doc.get("metadata", {})
        if note_id:
            metadata["note_id"] = note_id
        try:
            embedding = get_embedding(content, user_id=user_id)
            embedding_json = json.dumps(embedding)
        except Exception as e:
            print(f"[vector_store] Embedding 计算失败: {e}")
            embedding_json = None
        execute(
            """INSERT INTO note_embeddings (content, metadata, embedding, user_id)
               VALUES (%s, %s, %s, %s)""",
            (content, json.dumps(metadata, ensure_ascii=False), embedding_json, user_id),
        )
        count += 1
    return count


def search(query: str, top_k: int = 5, user_id: str = None) -> list[dict]:
    from agent.llm import get_embedding
    try:
        query_vec = np.array(get_embedding(query, user_id=user_id))
    except Exception as e:
        raise RuntimeError(f"Embedding 计算失败，无法进行向量搜索: {e}")

    if user_id:
        rows = query_all(
            "SELECT content, metadata, embedding FROM note_embeddings WHERE user_id = %s AND embedding IS NOT NULL",
            (user_id,),
        )
    else:
        rows = query_all(
            "SELECT content, metadata, embedding FROM note_embeddings WHERE embedding IS NOT NULL"
        )

    if not rows:
        return []

    scored = []
    for row in rows:
        try:
            vec = np.array(row["embedding"])
            similarity = float(np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec) + 1e-8))
        except Exception:
            continue
        scored.append({
            "content": row["content"],
            "metadata": row.get("metadata") or {},
            "distance": round(1 - similarity, 4),
        })

    scored.sort(key=lambda x: x["distance"])
    return scored[:top_k]


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
