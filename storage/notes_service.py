"""
笔记服务 —— 全站唯一的「新建笔记」入口。

为什么要有这一层：
原来「导入笔记」的 4 个 tab、「知识图谱」的添加、「知识广场」的收藏，
各自把 建笔记 → 切块 → 向量化 → 附件 → 遗忘曲线 → 图谱抽取 抄了一遍，
字段和容错各不相同。现在统一收口到 create_note()。

约定：
- 关键步骤（建笔记）失败就抛异常，调用方提示用户；
- 次要步骤（向量化 / 附件 / 图谱）失败只记 warning，不影响「笔记已保存」。
"""

from storage import document_parser, file_store, metadata_store, vector_store

MAX_ATTACHMENTS = 20


def create_note(*, user_id: str, title: str = "", content: str = "",
                tags: list[str] | None = None, importance: str = "normal",
                attachments: list[dict] | None = None, source: str = "manual",
                build_graph: bool = True) -> dict:
    """新建一条笔记（可带多个附件）。

    attachments: [{"name": "讲义.png", "data": b"..."}]，按顺序挂到这条笔记上。
    返回: {"note_id", "chunks", "attachments", "warnings"}
    """
    tags = [str(t).strip() for t in (tags or []) if str(t).strip()]
    attachments = list(attachments or [])[:MAX_ATTACHMENTS]
    title = (title or "").strip()
    content = (content or "").strip()

    warnings: list[str] = []

    # ① 关键一步：先落笔记元数据（失败直接抛给调用方）
    note_id = metadata_store.add_note(
        title=title, content=content, tags=tags,
        source=source, importance=importance, user_id=user_id,
    )

    # ② 正文切块 + 向量化
    chunks = 0
    if content:
        try:
            docs = document_parser.parse_text(content, source=source)
            chunks = vector_store.add_documents(docs, user_id=user_id, note_id=note_id)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"正文分块失败: {type(exc).__name__}: {exc}")

    # ③ 附件落盘 + 挂到这条笔记
    saved: list[dict] = []
    for idx, att in enumerate(attachments):
        try:
            saved.append(file_store.save_file(
                user_id=user_id,
                file_name=att.get("name", "未命名"),
                file_bytes=att.get("data", b""),
                tags=tags,
                importance=importance,
                description=title,
                note_id=note_id,
                position=idx,
            ))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"附件「{att.get('name')}」保存失败: {type(exc).__name__}: {exc}")

    # ④ 附件元数据也进检索（B 档：AI 至少知道"你存过这张图"）
    if saved:
        try:
            kinds = "、".join(
                f"{s['file_name']}（{s['media_type']}，{s['file_size'] // 1024}KB）" for s in saved
            )
            vector_store.add_documents(
                [{
                    "content": f"笔记《{title or '未命名笔记'}》的附件：{kinds}",
                    "metadata": {"kind": "attachment_meta", "source": "attachment"},
                }],
                user_id=user_id,
                note_id=note_id,
            )
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"附件索引失败: {type(exc).__name__}: {exc}")

    # ⑤ 遗忘曲线
    try:
        from scheduler import forgetting_curve as fc
        fc.record_access(note_id, user_id=user_id)
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"遗忘曲线记录失败: {type(exc).__name__}: {exc}")

    # ⑥ 主题统计
    if tags:
        try:
            from memory import long_term
            for tag in tags:
                long_term.add_topic(tag, [note_id], user_id=user_id)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"主题统计失败: {type(exc).__name__}: {exc}")

    # ⑦ 图谱实体抽取（慢，失败无所谓）
    graph = {}
    if build_graph and (content or title):
        try:
            from storage.knowledge_graph import add_note_to_graph
            graph = add_note_to_graph(content or title, user_id=user_id, note_id=note_id)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"图谱抽取失败: {type(exc).__name__}: {exc}")

    return {
        "note_id": note_id,
        "chunks": chunks,
        "attachments": len(saved),
        "graph": graph,
        "warnings": warnings,
    }


def get_note_detail(note_id: str, user_id: str) -> dict | None:
    """笔记详情：元数据 + 正文 + 附件。

    正文优先取 notes.content（v2 新字段）；
    老数据 content 为空时，退回从分块拼接。
    """
    note = metadata_store.get_note(note_id, user_id=user_id)
    if not note:
        return None

    body = (note.get("content") or "").strip()
    if not body:
        try:
            body = vector_store.get_note_full_content(note_id, user_id=user_id)
        except Exception:  # noqa: BLE001
            body = ""

    files = file_store.list_files_for_note(note_id, user_id)

    return {
        "id": note["id"],
        "title": note.get("title") or (note.get("preview") or "")[:40] or "未命名笔记",
        "body": body,
        "tags": note.get("tags") or [],
        "importance": note.get("importance") or "normal",
        "created_at": note.get("created_at") or 0,
        "files": files,
    }


def delete_note(note_id: str, user_id: str) -> bool:
    """删除笔记：先清磁盘附件，再删数据库行（附件行随 notes 级联删除）。"""
    try:
        file_store.delete_files_for_note(note_id, user_id)
    except Exception:  # noqa: BLE001
        pass
    return metadata_store.delete_note(note_id, user_id=user_id)
