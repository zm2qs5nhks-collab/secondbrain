"""
第二大脑 —— 小艺云插件 HTTP 接口
部署方式: streamlit run api.py  或  uvicorn api:app --host 0.0.0.0 --port 8000
"""

import os
import sys
import hashlib
import hmac
import time
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

# ─── AK/SK 配置 ───
XIAOYI_AK = os.getenv("XIAOYI_AK", "")
XIAOYI_SK = os.getenv("XIAOYI_SK", "")

app = FastAPI(title="第二大脑 API", version="1.0")


# ─── 鉴权中间件 ───
def verify_ak_sk(request: Request):
    """校验小艺 AK/SK"""
    if not XIAOYI_AK or not XIAOYI_SK:
        return
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


# ─── 请求模型 ───
class AddNoteRequest(BaseModel):
    content: str
    user_id: str = "default"


class SearchRequest(BaseModel):
    question: str
    user_id: str = "default"


class ReminderRequest(BaseModel):
    user_id: str = "default"


# ─── 接口 1: 新增笔记 ───
@app.post("/api/add_note")
async def add_note(req: AddNoteRequest, request: Request):
    verify_ak_sk(request)

    if not req.content.strip():
        return JSONResponse({"error": "内容不能为空"}, status_code=400)

    from storage import vector_store, document_parser, metadata_store
    from storage.knowledge_graph import add_note_to_graph
    from scheduler import forgetting_curve as fc

    documents = document_parser.parse_text(req.content, source="api")
    count = vector_store.add_documents(documents)

    note_id = metadata_store.add_note(
        content_preview=req.content,
        tags=[],
        source="api",
        importance="normal",
        user_id=req.user_id,
    )
    fc.record_access(note_id)

    graph_info = {}
    try:
        graph_info = add_note_to_graph(req.content)
    except Exception:
        pass

    return {
        "status": "success",
        "note_id": note_id,
        "chunks_stored": count,
        "graph": graph_info,
    }


# ─── 接口 2: 知识问答 ───
@app.post("/api/search")
async def search(req: SearchRequest, request: Request):
    verify_ak_sk(request)

    if not req.question.strip():
        return JSONResponse({"error": "问题不能为空"}, status_code=400)

    from storage import vector_store, metadata_store
    from agent.llm import chat_completion

    results = vector_store.search(req.question, top_k=5)

    if not results:
        return {"answer": "知识库中暂无相关内容，请先添加笔记。", "sources": []}

    context_parts = []
    sources = []
    for r in results:
        note = metadata_store.get_note(r["note_id"])
        preview = note["preview"] if note else r["text"][:100]
        context_parts.append(f"[{r['note_id']}] {preview}")
        sources.append({"note_id": r["note_id"], "score": round(r["score"], 3)})

    context = "\n".join(context_parts)
    messages = [
        {"role": "system", "content": "你是第二大脑知识助手。根据用户的知识库内容回答问题，引用来源。"},
        {"role": "user", "content": f"知识库内容：\n{context}\n\n问题：{req.question}"},
    ]
    response = chat_completion(messages)

    return {"answer": response["content"], "sources": sources}


# ─── 接口 3: 每日待复习清单 ───
@app.post("/api/reminders")
async def reminders(req: ReminderRequest, request: Request):
    verify_ak_sk(request)

    from scheduler import forgetting_curve as fc
    from storage import metadata_store

    notes = metadata_store.list_notes()
    result = []

    for note in notes:
        retention = fc.calculate_retention(note["id"])
        if retention < 0.6:
            days = fc.get_days_since_review(note["id"])
            result.append({
                "note_id": note["id"],
                "preview": note["preview"][:80],
                "retention": retention,
                "days_since_review": days,
                "tags": note.get("tags", []),
            })

    result.sort(key=lambda x: x["retention"])

    return {"reminders": result, "total": len(result)}


# ─── 健康检查 ───
@app.get("/api/health")
async def health():
    from storage import metadata_store
    return {"status": "ok", "notes_count": metadata_store.count()}
