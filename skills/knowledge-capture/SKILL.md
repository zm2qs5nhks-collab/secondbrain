---
name: knowledge-capture
description: 当用户想保存笔记、记录学习内容、收藏网页或整理知识时使用。通过第二大脑的 MCP 工具 add_knowledge / fetch_web_content 把内容存入个人知识库。
---

# 知识捕获（Knowledge Capture）

## 何时使用
- 用户说「记一下 / 保存 / 收藏 / 学习记录 / 帮我记住」
- 用户给出一个网页链接希望收录
- 用户粘贴一段需要长期保留的内容

## 使用哪个工具
- 纯文本 / 想法 / 学习笔记 → MCP 工具 `add_knowledge`
- 网页 URL → MCP 工具 `fetch_web_content`

## 约定
- `tags`：3-5 个名词，覆盖主题 / 技术 / 领域，例如 `["Python", "GIL", "并发"]`
- `importance`：核心概念用 `high`，日常记录 `normal`，临时内容 `low`
- 入库前若不确定是否重复，可先用 `search_knowledge` 查一下

## 附带脚本（无 MCP 客户端时可直接走 REST）
```bash
export SECOND_BRAIN_BASE_URL=http://localhost:8000
export SECOND_BRAIN_TOKEN=sb_xxx
python scripts/capture.py text "GIL 是 CPython 的全局解释器锁..." --tags Python 并发 --importance high
python scripts/capture.py url https://example.com/article
```
