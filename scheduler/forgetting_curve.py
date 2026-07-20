"""
遗忘曲线 —— 云端版 (Supabase)
"""

import math
import time
from storage.db import table


def record_access(note_id: str):
    existing = table("forgetting").select("*").eq("note_id", note_id).execute()
    now = time.time()

    if existing.data:
        rec = existing.data[0]
        review_dates = rec.get("review_dates") or []
        review_dates.append(now)
        access_count = rec.get("access_count", 0) + 1
        difficulty = rec.get("difficulty", 1.0)

        if len(review_dates) >= 2:
            interval = (review_dates[-1] - review_dates[-2]) / 86400
            if interval < 2:
                difficulty = min(3.0, difficulty + 0.1)
            elif interval > 7:
                difficulty = max(0.5, difficulty - 0.1)

        table("forgetting").update({
            "review_dates": review_dates,
            "access_count": access_count,
            "difficulty": difficulty,
        }).eq("note_id", note_id).execute()
    else:
        table("forgetting").insert({
            "note_id": note_id,
            "first_seen": now,
            "access_count": 1,
            "review_dates": [now],
            "difficulty": 1.0,
        }).execute()


def calculate_retention(note_id: str) -> float:
    res = table("forgetting").select("*").eq("note_id", note_id).execute()
    if not res.data:
        return 0.0

    rec = res.data[0]
    review_dates = rec.get("review_dates") or []
    if not review_dates:
        return 0.0

    last_review = review_dates[-1]
    days_since = (time.time() - last_review) / 86400
    stability = rec.get("difficulty", 1.0) * (rec.get("access_count", 0) + 1)
    retention = math.exp(-days_since / (stability * 7))
    return round(min(1.0, max(0.0, retention)), 2)


def get_notes_for_review(threshold: float = 0.5) -> list[dict]:
    res = table("forgetting").select("*").execute()
    reminders = []

    for rec in (res.data or []):
        note_id = rec["note_id"]
        review_dates = rec.get("review_dates") or []
        if not review_dates:
            continue

        retention = calculate_retention(note_id)
        days_since = (time.time() - review_dates[-1]) / 86400

        if retention < threshold:
            priority = (1 - retention) * rec.get("access_count", 0)
            urgency = _get_urgency(retention, days_since)
            reminders.append({
                "note_id": note_id,
                "retention": retention,
                "days_since_review": round(days_since),
                "review_count": rec.get("access_count", 0),
                "priority": priority,
                "urgency": urgency,
            })

    reminders.sort(key=lambda x: x["priority"], reverse=True)
    return reminders


def _get_urgency(retention: float, days: float) -> str:
    if retention < 0.2 or days > 14:
        return "紧急"
    elif retention < 0.4 or days > 7:
        return "重要"
    return "一般"


def get_curve_data(note_id: str, days_range: int = 30) -> list[dict]:
    """生成单条笔记的遗忘曲线数据点 (天数, 保留率)"""
    res = table("forgetting").select("*").eq("note_id", note_id).execute()
    if not res.data:
        return []

    rec = res.data[0]
    review_dates = rec.get("review_dates") or []
    if not review_dates:
        return []

    stability = rec.get("difficulty", 1.0) * (rec.get("access_count", 0) + 1)

    points = []
    for d in range(0, days_range + 1):
        retention = math.exp(-d / (stability * 7))
        retention = min(1.0, max(0.0, retention))
        points.append({"day": d, "retention": round(retention, 3)})

    return points


def get_all_curves_data() -> list[dict]:
    """获取所有笔记的遗忘曲线数据"""
    res = table("forgetting").select("*").execute()
    notes_curve = []

    for rec in (res.data or []):
        note_id = rec["note_id"]
        review_dates = rec.get("review_dates") or []
        if not review_dates:
            continue

        last_review = review_dates[-1]
        days_since = (time.time() - last_review) / 86400
        stability = rec.get("difficulty", 1.0) * (rec.get("access_count", 0) + 1)

        points = []
        for d in range(0, 31):
            ret = math.exp(-d / (stability * 7))
            points.append({"day": d, "retention": round(min(1.0, max(0.0, ret)), 3)})

        notes_curve.append({
            "note_id": note_id,
            "days_since": round(days_since),
            "access_count": rec.get("access_count", 1),
            "stability": round(stability, 1),
            "current_retention": round(calculate_retention(note_id), 3),
            "points": points,
        })

    return notes_curve
