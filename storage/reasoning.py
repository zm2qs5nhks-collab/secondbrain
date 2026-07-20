"""
多跳推理 —— 发现跨领域关联
"""

import networkx as nx
from storage.graph import KnowledgeGraph


def discover_cross_domain_links(kg: KnowledgeGraph, max_hops: int = 3) -> list[dict]:
    """发现跨领域关联"""
    nodes = kg.get_all_nodes()
    if len(nodes) < 2:
        return []

    type_groups = {}
    for node in nodes:
        t = node["type"]
        if t not in type_groups:
            type_groups[t] = []
        type_groups[t].append(node["name"])

    cross_links = []
    type_list = list(type_groups.keys())

    for i in range(len(type_list)):
        for j in range(i + 1, len(type_list)):
            t1, t2 = type_list[i], type_list[j]
            for n1 in type_groups[t1]:
                for n2 in type_groups[t2]:
                    paths = kg.find_paths(n1, n2, max_hops=max_hops)
                    for p in paths:
                        hops = len(p["edges"])
                        if hops >= 2:
                            cross_links.append({
                                "source": n1,
                                "source_type": t1,
                                "target": n2,
                                "target_type": t2,
                                "hops": hops,
                                "path": p["path"],
                                "edges": p["edges"],
                                "score": 1.0 / hops,
                            })

    cross_links.sort(key=lambda x: x["score"], reverse=True)
    return _deduplicate(cross_links)


def find_related_concepts(kg: KnowledgeGraph, concept: str, max_hops: int = 2) -> list[dict]:
    """给定一个概念，找到相关的跨领域概念"""
    neighbors = kg.get_neighbors(concept, depth=max_hops)
    results = []
    concept_type = None

    for n in neighbors["nodes"]:
        if n["name"] == concept:
            concept_type = n["type"]
            break

    for n in neighbors["nodes"]:
        if n["name"] != concept and n["type"] != concept_type:
            paths = kg.find_paths(concept, n["name"], max_hops=max_hops)
            if paths:
                shortest = min(paths, key=lambda p: len(p["edges"]))
                results.append({
                    "concept": n["name"],
                    "type": n["type"],
                    "hops": len(shortest["edges"]),
                    "path": shortest["path"],
                    "edges": shortest["edges"],
                })

    results.sort(key=lambda x: x["hops"])
    return results


def get_importance_scores(kg: KnowledgeGraph) -> list[dict]:
    """基于 PageRank + 度中心性评估节点重要性"""
    pr = kg.pagerank()
    betweenness = nx.betweenness_centrality(kg.graph.to_undirected()) if len(kg.graph) > 1 else {}

    results = []
    for node, pr_score in pr.items():
        results.append({
            "name": node,
            "type": kg.graph.nodes[node].get("type", "未知"),
            "pagerank": round(pr_score, 4),
            "betweenness": round(betweenness.get(node, 0), 4),
            "degree": kg.graph.degree(node),
            "importance": round(pr_score * 0.5 + betweenness.get(node, 0) * 0.3 + kg.graph.degree(node) * 0.02, 4),
        })

    results.sort(key=lambda x: x["importance"], reverse=True)
    return results


def _deduplicate(links: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for link in links:
        key = (link["source"], link["target"])
        if key not in seen:
            seen.add(key)
            result.append(link)
    return result
