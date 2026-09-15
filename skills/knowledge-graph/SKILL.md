---
name: knowledge-graph
description: 当用户想探索知识点之间的联系、寻找跨领域关联、或查看知识图谱统计时使用。调用第二大脑的 knowledge_graph 工具。
---

# 知识图谱（Knowledge Graph）

## 何时使用
- 「XX 和 YY 有什么关系」「找跨领域联系」「我的知识图谱长什么样」

## 工具
MCP `knowledge_graph`，`action` 取值：
- `query`（`node=实体名`）：查询某实体的多跳关联
- `discover`：发现跨领域关联
- `stats`：节点 / 边统计与 PageRank Top 节点
- `add`（`content=文本`）：把内容加入图谱（通常由 `add_knowledge` 自动完成，无需手动调用）

## 附带脚本
```bash
export SECOND_BRAIN_BASE_URL=http://localhost:8000
export SECOND_BRAIN_TOKEN=sb_xxx
python scripts/graph.py stats
python scripts/graph.py query "GIL" --max-hops 2
python scripts/graph.py discover
```
