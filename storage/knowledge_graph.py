"""
知识图谱模块 —— LLM实体抽取 + NetworkX图谱 + 多跳推理
"""

from storage.graph import KnowledgeGraph
from storage.extractor import extract_from_text

_kg = None


def get_kg() -> KnowledgeGraph:
    global _kg
    if _kg is None:
        _kg = KnowledgeGraph()
    return _kg


def add_note_to_graph(content: str) -> dict:
    """从笔记内容中抽取实体关系并加入图谱"""
    kg = get_kg()
    result = extract_from_text(content)
    entities = result.get("entities", [])
    relations = result.get("relations", [])
    kg.add_entities(entities)
    kg.add_relations(relations)
    kg.save()
    return {
        "entities_count": len(entities),
        "relations_count": len(relations),
        "total_nodes": len(kg.graph.nodes),
        "total_edges": len(kg.graph.edges),
    }


def get_graph_stats() -> dict:
    kg = get_kg()
    return {
        "nodes": len(kg.graph.nodes),
        "edges": len(kg.graph.edges),
        "pagerank": kg.pagerank(),
    }
