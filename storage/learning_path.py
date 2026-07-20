"""
个性化学习路径推荐 —— 基于遗忘曲线+标签掌握度
"""

from storage.db import table
from scheduler import forgetting_curve as fc


def get_learning_path() -> dict:
    """生成个性化学习路径"""
    notes_res = table("notes").select("id, preview, tags, importance, access_count").execute()
    notes = notes_res.data or []

    tag_stats = {}
    for note in notes:
        tags = note.get("tags") or []
        for tag in tags:
            if tag not in tag_stats:
                tag_stats[tag] = {
                    "total_notes": 0,
                    "high_importance": 0,
                    "total_access": 0,
                    "avg_retention": 0,
                    "retentions": [],
                    "notes": [],
                }
            stats = tag_stats[tag]
            stats["total_notes"] += 1
            if note.get("importance") == "high":
                stats["high_importance"] += 1
            stats["total_access"] += note.get("access_count", 0)
            retention = fc.calculate_retention(note["id"])
            stats["retentions"].append(retention)
            stats["notes"].append({
                "id": note["id"],
                "preview": note.get("preview", "")[:50],
                "retention": retention,
                "importance": note.get("importance", "normal"),
            })

    for tag, stats in tag_stats.items():
        rets = stats["retentions"]
        stats["avg_retention"] = sum(rets) / len(rets) if rets else 0
        del stats["retentions"]

    weak_tags = []
    strong_tags = []
    for tag, stats in tag_stats.items():
        score = stats["avg_retention"] * 0.6 + (1 - min(stats["total_notes"], 5) / 5) * 0.4
        entry = {"tag": tag, "stats": stats, "score": score}
        if stats["avg_retention"] < 0.6:
            weak_tags.append(entry)
        else:
            strong_tags.append(entry)

    weak_tags.sort(key=lambda x: x["score"])
    strong_tags.sort(key=lambda x: x["score"], reverse=True)

    recommendations = []
    for entry in weak_tags[:5]:
        stats = entry["stats"]
        weakest_notes = sorted(stats["notes"], key=lambda x: x["retention"])[:2]
        recommendations.append({
            "tag": entry["tag"],
            "reason": f"记忆保留率仅 {stats['avg_retention']*100:.0f}%，需要重点复习",
            "urgency": "high" if stats["avg_retention"] < 0.4 else "medium",
            "notes": weakest_notes,
            "total_notes": stats["total_notes"],
        })

    for entry in strong_tags[:3]:
        stats = entry["stats"]
        recommendations.append({
            "tag": entry["tag"],
            "reason": f"掌握良好（{stats['avg_retention']*100:.0f}%），可以拓展深入",
            "urgency": "explore",
            "notes": stats["notes"][:1],
            "total_notes": stats["total_notes"],
        })

    return {
        "recommendations": recommendations,
        "tag_stats": tag_stats,
        "total_notes": len(notes),
        "total_tags": len(tag_stats),
        "overall_retention": _calc_overall_retention(notes),
    }


def _calc_overall_retention(notes: list) -> float:
    if not notes:
        return 0
    total = sum(fc.calculate_retention(n["id"]) for n in notes)
    return total / len(notes)


def get_weak_notes(limit: int = 10) -> list[dict]:
    """获取最需要复习的笔记"""
    notes_res = table("notes").select("id, preview, tags, importance").execute()
    notes = notes_res.data or []

    scored = []
    for note in notes:
        retention = fc.calculate_retention(note["id"])
        if retention < 0.7:
            urgency_score = (1 - retention) * 10
            if note.get("importance") == "high":
                urgency_score *= 1.5
            scored.append({
                "id": note["id"],
                "preview": note.get("preview", "")[:60],
                "tags": note.get("tags", []),
                "importance": note.get("importance", "normal"),
                "retention": retention,
                "urgency_score": urgency_score,
            })

    scored.sort(key=lambda x: x["urgency_score"], reverse=True)
    return scored[:limit]
