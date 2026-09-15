---
name: spaced-review
description: 当用户问「今天要复习什么 / 有什么要复习的 / 提醒我复习」，或需要检查知识遗忘情况时使用。调用第二大脑的 send_reminder 工具（基于遗忘曲线）。
---

# 间隔复习（Spaced Review）

## 何时使用
- 「今天要复习什么」「有哪些快忘了」「复习提醒」
- 用户想查看知识掌握度 / 遗忘曲线

## 工具
- MCP `send_reminder`（`threshold` 默认 0.5；值越低越严格，会召回更多笔记）

## 结果处理
- 按 `urgency` 排序：紧急 > 重要 > 一般
- 每条给出 `retention`（记忆留存率）与 `days_since_review`（距上次复习天数）
- 建议用户复述要点；复述完成后可再次 `add_knowledge` 记录，或触发新一轮复习

## 附带脚本
```bash
export SECOND_BRAIN_BASE_URL=http://localhost:8000
export SECOND_BRAIN_TOKEN=sb_xxx
python scripts/review_due.py --threshold 0.5
```
