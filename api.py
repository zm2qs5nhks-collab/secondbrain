"""
第二大脑 —— 小艺云插件 HTTP 接口
部署方式: uvicorn api:app --host 0.0.0.0 --port $PORT
"""

import os
import sys
import hashlib
import hmac
import time
import json
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

XIAOYI_AK = os.getenv("XIAOYI_AK", "")
XIAOYI_SK = os.getenv("XIAOYI_SK", "")
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")

app = FastAPI(title="第二大脑 API", version="3.0")


def _get_user_id_from_token(request: Request) -> str:
    """从 Authorization header 中提取 user_id"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Authorization 头")
    token = auth_header.replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Token 为空")

    from storage.db import query_one
    user = query_one("SELECT id FROM users WHERE id = %s", (token,))
    if user:
        return str(user["id"])
    raise HTTPException(status_code=401, detail="Token 无效或已过期")


def verify_ak_sk(request: Request):
    if not API_SECRET_KEY and not XIAOYI_AK:
        return
    if API_SECRET_KEY:
        auth_key = request.headers.get("X-API-KEY", "") or request.headers.get("Authorization", "").replace("Bearer ", "")
        if not auth_key:
            raise HTTPException(status_code=403, detail="缺少鉴权头")
        if auth_key != API_SECRET_KEY:
            raise HTTPException(status_code=403, detail="密钥无效")
        return
    if XIAOYI_AK and XIAOYI_SK:
        auth_ak = request.headers.get("X-AK", "")
        auth_sign = request.headers.get("X-Sign", "")
        auth_ts = request.headers.get("X-Timestamp", "")

        if not auth_ak or not auth_sign:
            raise HTTPException(status_code=403, detail="缺少鉴权头")
        if auth_ak != XIAOYI_AK:
            raise HTTPException(status_code=403, detail="AK 无效")

        sign_str = f"{auth_ak}{auth_ts}{XIAOYI_SK}"
        expected = hashlib.sha256(sign_str.encode()).hexdigest()
        if not hmac.compare_digest(auth_sign, expected):
            raise HTTPException(status_code=403, detail="签名校验失败")
        if abs(time.time() - int(auth_ts)) > 300:
            raise HTTPException(status_code=403, detail="请求已过期")


class AddNoteRequest(BaseModel):
    content: str
    tags: list[str] = []
    importance: str = "normal"

class SearchRequest(BaseModel):
    question: str
    top_k: int = 5

class ReminderRequest(BaseModel):
    threshold: float = 0.5

class ManageRequest(BaseModel):
    action: str = "list"
    note_id: str = ""

class WebFetchRequest(BaseModel):
    url: str

class GraphRequest(BaseModel):
    action: str = "stats"
    content: str = ""
    node: str = ""
    max_hops: int = 2


@app.post("/api/add_note")
async def add_note(req: AddNoteRequest, request: Request):
    user_id = _get_user_id_from_token(request)
    if not req.content.strip():
        return JSONResponse({"error": "内容不能为空"}, status_code=400)

    from storage import vector_store, document_parser, metadata_store
    from storage.knowledge_graph import add_note_to_graph
    from scheduler import forgetting_curve as fc

    documents = document_parser.parse_text(req.content, source="api")
    note_id = metadata_store.add_note(
        content_preview=req.content, tags=req.tags, source="api",
        importance=req.importance, user_id=user_id,
    )
    count = vector_store.add_documents(documents, user_id=user_id, note_id=note_id)
    fc.record_access(note_id, user_id=user_id)

    graph_info = {}
    try:
        graph_info = add_note_to_graph(req.content, user_id=user_id)
    except Exception:
        pass

    return {"status": "success", "note_id": note_id, "chunks_stored": count, "graph": graph_info}


@app.post("/api/search")
async def search(req: SearchRequest, request: Request):
    user_id = _get_user_id_from_token(request)
    if not req.question.strip():
        return JSONResponse({"error": "问题不能为空"}, status_code=400)

    from storage import vector_store, metadata_store
    from agent.llm import chat_completion

    results = vector_store.search(req.question, top_k=req.top_k, user_id=user_id)
    if not results:
        return {"answer": "知识库中暂无相关内容，请先添加笔记。", "sources": []}

    context_parts, sources = [], []
    for r in results:
        meta = r.get("metadata", {})
        note = metadata_store.get_note(meta.get("note_id", ""), user_id=user_id)
        preview = note["preview"] if note else r["content"][:100]
        context_parts.append(f"[{meta.get('note_id', '?')}] {preview}")
        sources.append({"note_id": meta.get("note_id", ""), "score": round(1 - r["distance"], 3)})

    messages = [
        {"role": "system", "content": "你是第二大脑知识助手。根据用户的知识库内容回答问题，引用来源。"},
        {"role": "user", "content": f"知识库内容：\n{chr(10).join(context_parts)}\n\n问题：{req.question}"},
    ]
    response = chat_completion(messages)
    return {"answer": response["content"], "sources": sources}


@app.post("/api/reminders")
async def reminders(req: ReminderRequest, request: Request):
    user_id = _get_user_id_from_token(request)
    from scheduler import forgetting_curve as fc
    from storage import metadata_store

    reminders_list = fc.get_notes_for_review(threshold=req.threshold, user_id=user_id)
    result = []
    for r in reminders_list:
        note = metadata_store.get_note(r["note_id"], user_id=user_id)
        result.append({
            "note_id": r["note_id"],
            "preview": note["preview"][:80] if note else "未知",
            "retention": r["retention"],
            "urgency": r["urgency"],
        })
    return {"reminders": result, "total": len(result)}


@app.post("/api/manage")
async def manage(req: ManageRequest, request: Request):
    user_id = _get_user_id_from_token(request)
    from storage import metadata_store

    if req.action == "list":
        notes = metadata_store.list_notes(user_id=user_id)
        return {"notes": [{"id": n["id"], "preview": n["preview"][:60], "tags": n.get("tags", []), "importance": n.get("importance", "normal")} for n in notes], "total": len(notes)}

    elif req.action == "delete" and req.note_id:
        metadata_store.delete_note(req.note_id, user_id=user_id)
        return {"status": "success", "message": f"已删除 {req.note_id}"}

    elif req.action == "detail" and req.note_id:
        note = metadata_store.get_note(req.note_id, user_id=user_id)
        if note:
            return {"note": note}
        return JSONResponse({"error": "笔记不存在"}, status_code=404)

    return JSONResponse({"error": "无效操作"}, status_code=400)


@app.post("/api/fetch_web")
async def fetch_web(req: WebFetchRequest, request: Request):
    user_id = _get_user_id_from_token(request)
    if not req.url.strip():
        return JSONResponse({"error": "URL不能为空"}, status_code=400)

    from tools.fetch_web import fetch_url
    from storage.knowledge_graph import add_note_to_graph

    result = fetch_url(req.url)
    if not result.get("content"):
        return JSONResponse({"error": "抓取失败"}, status_code=400)

    from storage import vector_store, document_parser, metadata_store
    from scheduler import forgetting_curve as fc

    full_content = f"[来源: {result.get('title', req.url)}]\n\n{result['content']}"
    documents = document_parser.parse_text(full_content, source="web")
    note_id = metadata_store.add_note(content_preview=full_content, tags=["网页收藏"], source="web", importance="normal", user_id=user_id)
    count = vector_store.add_documents(documents, user_id=user_id, note_id=note_id)
    fc.record_access(note_id, user_id=user_id)

    graph_info = {}
    try:
        graph_info = add_note_to_graph(result["content"], user_id=user_id)
    except Exception:
        pass

    return {"status": "success", "note_id": note_id, "title": result.get("title", ""), "length": result.get("length", 0)}


@app.post("/api/knowledge_graph")
async def knowledge_graph_api(req: GraphRequest, request: Request):
    user_id = _get_user_id_from_token(request)
    from storage.graph import KnowledgeGraph
    from storage.extractor import extract_from_text
    from storage.reasoning import discover_cross_domain_links, find_related_concepts

    kg = KnowledgeGraph(user_id=user_id)

    if req.action == "add":
        if not req.content.strip():
            return JSONResponse({"error": "内容不能为空"}, status_code=400)
        result = extract_from_text(req.content)
        entities = result.get("entities", [])
        relations = result.get("relations", [])
        kg.add_entities(entities)
        kg.add_relations(relations)
        kg.save()
        return {"status": "success", "entities": len(entities), "relations": len(relations), "total_nodes": len(kg.graph.nodes), "total_edges": len(kg.graph.edges)}

    elif req.action == "query":
        if not req.node:
            return JSONResponse({"error": "请指定节点"}, status_code=400)
        related = find_related_concepts(kg, req.node, max_hops=req.max_hops)
        if not related:
            neighbors = kg.get_neighbors(req.node, depth=1)
            neighbor_names = [n["name"] for n in neighbors["nodes"] if n["name"] != req.node]
            return {"node": req.node, "neighbors": neighbor_names[:10]}
        return {"node": req.node, "related": [{"concept": r["concept"], "type": r["type"], "hops": r["hops"], "path": " → ".join(r["path"])} for r in related[:5]]}

    elif req.action == "discover":
        links = discover_cross_domain_links(kg)
        return {"links": [{"from": f"{l['source']}({l['source_type']})", "to": f"{l['target']}({l['target_type']})", "hops": l["hops"], "path": " → ".join(l["path"])} for l in links[:5]]}

    elif req.action == "stats":
        pr = kg.pagerank()
        return {"nodes": len(kg.graph.nodes), "edges": len(kg.graph.edges), "top_nodes": [{"name": n, "score": round(s, 4)} for n, s in list(pr.items())[:5]]}

    return JSONResponse({"error": "无效操作"}, status_code=400)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
