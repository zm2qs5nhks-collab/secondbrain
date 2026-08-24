"""
文件存储 —— 图片/音频/视频 直接入库
"""

import os
import uuid
import json
from datetime import datetime
from storage.db import execute, query_one, query_all

UPLOAD_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_file(user_id: str, file_name: str, file_bytes: bytes,
              tags: list[str] = None, importance: str = "normal",
              description: str = "") -> dict:
    """保存文件到磁盘 + 写入数据库元信息"""
    ext = os.path.splitext(file_name)[1].lower()
    media_type = _guess_type(ext)
    file_id = uuid.uuid4().hex[:12]
    safe_name = f"{file_id}{ext}"

    user_dir = os.path.join(UPLOAD_ROOT, user_id)
    _ensure_dir(user_dir)
    file_path = os.path.join(user_dir, safe_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    sql = """INSERT INTO media_files (file_id, user_id, original_name, saved_name,
             file_path, media_type, file_size, tags, importance, description)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    execute(sql, (
        file_id, user_id, file_name, safe_name, file_path,
        media_type, len(file_bytes),
        json.dumps(tags or [], ensure_ascii=False),
        importance, description,
    ))

    return {
        "file_id": file_id,
        "file_name": file_name,
        "media_type": media_type,
        "file_size": len(file_bytes),
    }


def list_files(user_id: str, media_type: str = None) -> list[dict]:
    """列出用户的所有媒体文件"""
    if media_type:
        rows = query_all(
            "SELECT * FROM media_files WHERE user_id = %s AND media_type = %s ORDER BY created_at DESC",
            (user_id, media_type),
        )
    else:
        rows = query_all(
            "SELECT * FROM media_files WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
        )
    return rows


def get_file(file_id: str, user_id: str = None) -> dict | None:
    """获取单个文件信息"""
    if user_id:
        return query_one("SELECT * FROM media_files WHERE file_id = %s AND user_id = %s", (file_id, user_id))
    return query_one("SELECT * FROM media_files WHERE file_id = %s", (file_id,))


def delete_file(file_id: str, user_id: str = None) -> bool:
    """删除文件（磁盘+数据库）"""
    info = get_file(file_id, user_id)
    if not info:
        return False
    try:
        if os.path.exists(info["file_path"]):
            os.remove(info["file_path"])
    except Exception:
        pass
    execute("DELETE FROM media_files WHERE file_id = %s", (file_id,))
    return True


def count(user_id: str = None, media_type: str = None) -> int:
    """统计文件数"""
    if user_id and media_type:
        row = query_one("SELECT COUNT(*) AS cnt FROM media_files WHERE user_id = %s AND media_type = %s",
                        (user_id, media_type))
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
    elif ext in audio_exts:
        return "audio"
    elif ext in video_exts:
        return "video"
    return "other"
