"""
文件存储 —— 图片 / 音频 / 视频 / 文档

v2 变化：
- 附件可以挂到笔记上（note_id + position），一条笔记支持多个附件
- 增加 extracted_text 列，为后期 OCR / 语音转写预留（现在恒为 NULL）
- 文件名只取 basename，扩展名做白名单清洗，避免路径穿越
"""

import os
import re
import uuid
import json

from storage.db import execute, query_one, query_all

UPLOAD_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

# 与 Nginx client_max_body_size / Streamlit 默认上限保持一致
MAX_FILE_BYTES = 200 * 1024 * 1024

_EXT_RE = re.compile(r"^[a-z0-9]{1,10}$")


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _safe_ext(file_name: str) -> str:
    """只保留形如 .png 的扩展名；异常扩展名一律丢弃。"""
    ext = os.path.splitext(os.path.basename(file_name or ""))[1].lower().lstrip(".")
    return f".{ext}" if _EXT_RE.match(ext) else ""


def save_file(user_id: str, file_name: str, file_bytes: bytes,
              tags: list[str] = None, importance: str = "normal",
              description: str = "", note_id: str = None,
              position: int = 0, extracted_text: str = None) -> dict:
    """保存文件到磁盘 + 写入数据库元信息。

    note_id 不为空表示「这个附件属于某条笔记」。
    """
    if not file_bytes:
        raise ValueError("文件内容为空")
    if len(file_bytes) > MAX_FILE_BYTES:
        raise ValueError(f"文件超过上限 {MAX_FILE_BYTES // (1024 * 1024)}MB")

    ext = _safe_ext(file_name)
    media_type = _guess_type(ext)
    file_id = uuid.uuid4().hex[:12]
    safe_name = f"{file_id}{ext}"

    user_dir = os.path.join(UPLOAD_ROOT, str(user_id))
    _ensure_dir(user_dir)
    file_path = os.path.join(user_dir, safe_name)

    with open(file_path, "wb") as fh:
        fh.write(file_bytes)

    execute(
        """INSERT INTO media_files (file_id, user_id, original_name, saved_name,
                                    file_path, media_type, file_size, tags, importance,
                                    description, note_id, position, extracted_text)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (file_id, user_id, os.path.basename(file_name or "未命名"), safe_name, file_path,
         media_type, len(file_bytes), json.dumps(tags or [], ensure_ascii=False),
         importance, description, note_id, position, extracted_text),
    )

    return {
        "file_id": file_id,
        "file_name": os.path.basename(file_name or "未命名"),
        "media_type": media_type,
        "file_size": len(file_bytes),
        "note_id": note_id,
    }


def list_files(user_id: str, media_type: str = None, limit: int = 200) -> list[dict]:
    """列出用户的全部媒体文件（最新在前）。"""
    if media_type:
        return query_all(
            "SELECT * FROM media_files WHERE user_id = %s AND media_type = %s "
            "ORDER BY created_at DESC LIMIT %s",
            (user_id, media_type, limit),
        )
    return query_all(
        "SELECT * FROM media_files WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
        (user_id, limit),
    )


def list_files_for_note(note_id: str, user_id: str) -> list[dict]:
    """某条笔记的附件，按 position 排序。"""
    return query_all(
        "SELECT * FROM media_files WHERE note_id = %s AND user_id = %s "
        "ORDER BY position ASC, created_at ASC",
        (note_id, user_id),
    )


def count_files_for_notes(note_ids: list[str], user_id: str) -> dict[str, int]:
    """批量统计每条笔记的附件数，避免列表页 N+1 查询。"""
    if not note_ids:
        return {}
    rows = query_all(
        "SELECT note_id, COUNT(*) AS cnt FROM media_files "
        "WHERE user_id = %s AND note_id = ANY(%s) GROUP BY note_id",
        (user_id, list(note_ids)),
    )
    return {r["note_id"]: r["cnt"] for r in rows if r.get("note_id")}


def get_file(file_id: str, user_id: str = None) -> dict | None:
    if user_id:
        return query_one(
            "SELECT * FROM media_files WHERE file_id = %s AND user_id = %s",
            (file_id, user_id),
        )
    return query_one("SELECT * FROM media_files WHERE file_id = %s", (file_id,))


def delete_file(file_id: str, user_id: str = None) -> bool:
    """删除文件（磁盘 + 数据库）。"""
    info = get_file(file_id, user_id)
    if not info:
        return False
    try:
        if os.path.exists(info["file_path"]):
            os.remove(info["file_path"])
    except OSError:
        pass

    if user_id:
        execute("DELETE FROM media_files WHERE file_id = %s AND user_id = %s", (file_id, user_id))
    else:
        execute("DELETE FROM media_files WHERE file_id = %s", (file_id,))
    return True


def delete_files_for_note(note_id: str, user_id: str) -> int:
    """删除一条笔记的所有附件（数据库行随 notes 级联删除，磁盘文件要手动清）。"""
    rows = list_files_for_note(note_id, user_id)
    for row in rows:
        try:
            if os.path.exists(row["file_path"]):
                os.remove(row["file_path"])
        except OSError:
            pass
    return len(rows)


def count(user_id: str = None, media_type: str = None) -> int:
    if user_id and media_type:
        row = query_one(
            "SELECT COUNT(*) AS cnt FROM media_files WHERE user_id = %s AND media_type = %s",
            (user_id, media_type),
        )
    elif user_id:
        row = query_one("SELECT COUNT(*) AS cnt FROM media_files WHERE user_id = %s", (user_id,))
    else:
        row = query_one("SELECT COUNT(*) AS cnt FROM media_files")
    return row["cnt"] if row else 0


def _guess_type(ext: str) -> str:
    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}
    audio_exts = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma"}
    video_exts = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}
    if ext in image_exts:
        return "image"
    if ext in audio_exts:
        return "audio"
    if ext in video_exts:
        return "video"
    if ext in {".pdf", ".txt", ".md", ".doc", ".docx"}:
        return "document"
    return "other"
