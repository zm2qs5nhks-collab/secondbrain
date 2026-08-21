"""
知识图谱工具 —— 让 Agent 能操作知识图谱
"""

import json
from storage.knowledge_graph import add_note_to_graph, get_kg
from storage.reasoning import discover_cross_domain_links, find_related_concepts


def get_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "knowledge_graph",
            "description": "操作知识图谱。支持：add（将内容加入图谱，自动抽取实体关系）、query（查询某个实体的关联节点）、discover（发现跨领域关联）、stats（查看图谱统计）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["add", "query", "discover", "stats"],
                        "description": "操作类型",
                    },
                    "content": {
                        "type": "string",
                        "description": "当 action=add 时，传入要加入图谱的笔记内容",
                    },
                    "node": {
                        "type": "string",
                        "description": "当 action=query 时，传入要查询的实体名称",
                    },
                    "max_hops": {
                        "type": "integer",
                        "description": "当 action=query 时，最大跳数，默认2",
                    },
                },
                "required": ["action"],
            },
        },
    }


def execute(arguments: dict, user_id: str = None) -> str:
    action = arguments.get("action", "")
    kg = get_kg(user_id)

    if action == "add":
        content = arguments.get("content", "")
        if not content.strip():
            return json.dumps({"error": "内容不能为空"}, ensure_ascii=False)
        result = add_note_to_graph(content, user_id=user_id)
        return json.dumps({
            "status": "success",
            "message": f"已加入图谱：{result['entities_count']}个实体，{result['relations_count']}条关系。图谱现有{result['total_nodes']}个节点，{result['total_edges']}条边。",
        }, ensure_ascii=False)

    elif action == "query":
        node = arguments.get("node", "")
        if not node:
            return json.dumps({"error": "请指定要查询的实体名称"}, ensure_ascii=False)
        max_hops = arguments.get("max_hops", 2)
        related = find_related_concepts(kg, node, max_hops=max_hops)
        if not related:
            neighbors = kg.get_neighbors(node, depth=1)
            if not neighbors["nodes"]:
                return json.dumps({"message": f"图谱中没有找到实体「{node}」"}, ensure_ascii=False)
            neighbor_names = [n["name"] for n in neighbors["nodes"] if n["name"] != node]
            return json.dumps({
                "message": f"「{node}」的直接关联：{', '.join(neighbor_names[:10])}",
            }, ensure_ascii=False)
        lines = []
        for r in related[:5]:
            path_str = " → ".join(r["path"])
            lines.append(f"{r['concept']}({r['type']}) {r['hops']}跳: {path_str}")
        return json.dumps({"关联": lines}, ensure_ascii=False)

    elif action == "discover":
        links = discover_cross_domain_links(kg)
        if not links:
            return json.dumps({"message": "暂未发现跨领域关联"}, ensure_ascii=False)
        results = []
        for link in links[:5]:
            path_str = " → ".join(link["path"])
            results.append({
                "from": f"{link['source']}({link['source_type']})",
                "to": f"{link['target']}({link['target_type']})",
                "hops": link["hops"],
                "path": path_str,
            })
        return json.dumps({"跨领域关联": results}, ensure_ascii=False)

    elif action == "stats":
        pr = kg.pagerank()
        top5 = list(pr.items())[:5]
        return json.dumps({
            "nodes": len(kg.graph.nodes),
            "edges": len(kg.graph.edges),
            "top_nodes": [{"name": n, "pagerank": round(s, 4)} for n, s in top5],
        }, ensure_ascii=False)

    else:
        return json.dumps({"error": f"未知操作: {action}"}, ensure_ascii=False)
