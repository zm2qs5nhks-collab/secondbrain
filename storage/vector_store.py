"""
向量存储 —— 云端版 (Supabase)
使用 OpenAI Embedding + Supabase 存储 + Python 余弦相似度计算
"""

import numpy as np
from storage.db import table
from agent.llm import get_embedding


def add_documents(documents: list[dict]) -> int:
    rows = []
    for doc in documents:
        content = doc["content"]
        try:
            embedding = get_embedding(content)
        except Exception:
            embedding = None
        rows.append({
            "content": content,
            "metadata": doc.get("metadata", {}),
            "embedding": embedding,
        })

    valid_rows = [r for r in rows if r["embedding"] is not None]
    if valid_rows:
        table("note_embeddings").insert(valid_rows).execute()
    return len(valid_rows)


def search(query: str, top_k: int = 5) -> list[dict]:
    try:
        query_embedding = get_embedding(query)
    except Exception:
        return []

    res = table("note_embeddings").select("content, metadata, embedding").execute()
    if not res.data:
        return []

    scored = []
    for row in res.data:
        emb = row.get("embedding")
        if emb is None:
            continue
        sim = _cosine_similarity(query_embedding, emb)
        scored.append({
            "content": row["content"],
            "metadata": row.get("metadata", {}),
            "distance": 1 - sim,
        })

    scored.sort(key=lambda x: x["distance"])
    return scored[:top_k]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_np = np.array(a, dtype=float)
    b_np = np.array(b, dtype=float)
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_np, b_np) / (norm_a * norm_b))


def count() -> int:
    res = table("note_embeddings").select("id", count="exact").execute()
    return len(res.data)


def delete_all():
    table("note_embeddings").delete().neq("id", -1).execute()
