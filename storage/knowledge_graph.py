"""
知识图谱模块 —— LLM实体抽取 + NetworkX图谱 + 多跳推理
"""

from storage.graph import KnowledgeGraph
from storage.extractor import extract_from_text

_kg_cache = {}


def get_kg(user_id: str = None) -> KnowledgeGraph:
    key = user_id or "__global__"
    if key not in _kg_cache:
        _kg_cache[key] = KnowledgeGraph(user_id=user_id)
    return _kg_cache[key]


def add_note_to_graph(content: str, user_id: str = None, note_id: str = None) -> dict:
    """从笔记内容中抽取实体关系并加入图谱；note_id 用于标注来源笔记"""
    kg = get_kg(user_id)
    result = extract_from_text(content)
    entities = result.get("entities", [])
    relations = result.get("relations", [])
    kg.add_entities(entities, note_id=note_id)
    kg.add_relations(relations, note_id=note_id)
    kg.save()
    return {
        "entities_count": len(entities),
        "relations_count": len(relations),
        "total_nodes": len(kg.graph.nodes),
        "total_edges": len(kg.graph.edges),
    }


def get_graph_stats(user_id: str = None) -> dict:
    kg = get_kg(user_id)
    return {
        "nodes": len(kg.graph.nodes),
        "edges": len(kg.graph.edges),
        "pagerank": kg.pagerank(),
    }
