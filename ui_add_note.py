"""
「添加内容」页 —— 标题 + 正文 + 附件。

设计目标：整页只有一个提交动作，用户只需要回答
「这条笔记里有什么」，不需要理解文本走哪条链路、图片走哪条链路。

后台统一走 storage.notes_service.create_note()。
"""

import os

import streamlit as st

from storage import file_store
from storage.notes_service import create_note
from ui_theme import notebook_line, page_header

_ATTACH_TYPES = [
    "png", "jpg", "jpeg", "gif", "bmp", "webp",
    "pdf", "txt", "md", "doc", "docx",
    "mp3", "wav", "ogg", "flac", "aac", "m4a",
    "mp4", "mov", "webm", "mkv", "avi",
]

_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
_ICON = {"image": "🖼️", "audio": "🎵", "video": "🎬", "document": "📄"}


def _nonce() -> int:
    """用自增 nonce 拼进 widget key，保存成功后可以整体清空表单。"""
    return int(st.session_state.get("add_nonce", 0))


def _human_size(n: int) -> str:
    if n < 1024:
        return f"{n}B"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f}KB"
    return f"{n / 1024 / 1024:.1f}MB"


def _render_last_result() -> None:
    last = st.session_state.pop("add_last_result", None)
    if not last:
        return

    st.success(
        f"已保存：**{last['title']}** ｜ 正文 {last['chunks']} 个分块 ｜ "
        f"附件 {last['attachments']} 个 ｜ 图谱实体 {last.get('entities', 0)} 个"
    )
    if last.get("warnings"):
        with st.expander(f"⚠️ {len(last['warnings'])} 条非致命问题（笔记已保存）", expanded=False):
            for w in last["warnings"]:
                st.caption(w)


def _render_attachment_library(user_id: str) -> None:
    with st.expander("📎 附件库（最近 20 个）", expanded=False):
        files = file_store.list_files(user_id=user_id, limit=20)
        if not files:
            st.caption("还没有附件。")
            return

        st.caption(
            f"共 {file_store.count(user_id=user_id)} 个附件。"
            "附件目前只按「文件名 / 描述 / 标签」被检索到，内容暂不参与问答。"
        )
        for f in files:
            c1, c2 = st.columns([5, 1])
            with c1:
                icon = _ICON.get(f["media_type"], "📄")
                st.markdown(f"**{icon} {f['original_name']}**")
                st.caption(f"{_human_size(f['file_size'])} ｜ {f.get('note_id') or '未关联笔记'}")
            with c2:
                if st.button("删除", key=f"att_del_{f['file_id']}"):
                    file_store.delete_file(f["file_id"], user_id=user_id)
                    st.rerun()


def render_add_note(user_id: str) -> None:
    page_header("➕", "添加内容", "标题 + 正文 + 附件，一条笔记可以同时有文字、图片、音视频")
    notebook_line()

    _render_last_result()

    n = _nonce()

    title = st.text_input(
        "标题",
        key=f"add_title_{n}",
        placeholder="例：第 3 章 · 缓存穿透与布隆过滤器（留空则自动取正文首行）",
    )
    content = st.text_area(
        "正文（可选）",
        key=f"add_content_{n}",
        height=200,
        placeholder="粘贴文字内容；只传图片/录音时这里可以留空",
    )

    uploads = st.file_uploader(
        "附件（图片 / 音频 / 视频 / PDF，可多选）",
        type=_ATTACH_TYPES,
        accept_multiple_files=True,
        key=f"add_files_{n}",
    )

    if uploads:
        st.caption(f"已选 {len(uploads)} 个附件")
        cols = st.columns(min(4, len(uploads)))
        for i, f in enumerate(uploads[:8]):
            with cols[i % len(cols)]:
                ext = os.path.splitext(f.name)[1].lower()
                if ext in _IMAGE_EXT:
                    st.image(f, width=110)
                else:
                    st.caption(f"📄 {f.name}\n\n{_human_size(f.size)}")

    c1, c2 = st.columns([2, 1])
    tags_raw = c1.text_input(
        "标签（逗号分隔）", key=f"add_tags_{n}", placeholder="如：Redis, 缓存, 面试"
    )
    importance = c2.selectbox("重要度", ["normal", "high", "low"], key=f"add_imp_{n}")

    submitted = st.button(
        "保存这条笔记", type="primary", use_container_width=True, key=f"add_submit_{n}"
    )

    if submitted:
        tags = [t.strip() for t in tags_raw.replace("，", ",").split(",") if t.strip()]
        if not (title.strip() or content.strip() or uploads):
            st.error("标题、正文、附件至少要填一项")
            return

        attachments = []
        for f in uploads or []:
            f.seek(0)
            attachments.append({"name": f.name, "data": f.read()})

        with st.spinner("正在保存：切块 → 向量化 → 抽实体，可能要十几秒…"):
            try:
                result = create_note(
                    user_id=user_id,
                    title=title,
                    content=content,
                    tags=tags,
                    importance=importance,
                    attachments=attachments,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"保存失败：{type(exc).__name__}: {exc}")
                return

        st.session_state["add_last_result"] = {
            "title": title.strip() or (content.strip().splitlines() or ["未命名笔记"])[0][:40],
            "chunks": result["chunks"],
            "attachments": result["attachments"],
            "entities": (result.get("graph") or {}).get("entities_count", 0),
            "warnings": result.get("warnings") or [],
        }
        st.session_state["add_nonce"] = n + 1
        st.rerun()

    st.markdown("---")
    st.caption(
        "想从网页导入？去左侧 **🌐 发现** 搜索后一键收藏；"
        "想让 AI 直接帮你记，去 **💬 智能问答** 说「帮我记下来…」。"
    )

    _render_attachment_library(user_id)
