"""
知识图谱构建与查询 —— 基于 NetworkX
"""

import json
import networkx as nx
from pathlib import Path

DATA_DIR = Path(__file__).parent / "graph_data"


class KnowledgeGraph:
    def __init__(self, user_id: str = None):
        self.user_id = user_id or "__global__"
        self.graph = nx.DiGraph()
        self._file = DATA_DIR / f"{self.user_id}.json"
        DATA_DIR.mkdir(exist_ok=True)
        self.load()

    def load(self):
        """从文件加载图谱"""
        if self._file.exists():
            data = json.loads(self._file.read_text(encoding="utf-8"))
            for entity in data.get("entities", []):
                self.graph.add_node(entity["name"], type=entity.get("type", "未知"))
            for rel in data.get("relations", []):
                if rel["source"] in self.graph and rel["target"] in self.graph:
                    self.graph.add_edge(
                        rel["source"], rel["target"], relation=rel["relation"]
                    )

    def save(self):
        """保存图谱到文件"""
        data = {
            "entities": [
                {"name": n, "type": self.graph.nodes[n].get("type", "未知")}
                for n in self.graph.nodes
            ],
            "relations": [
                {"source": u, "target": v, "relation": d.get("relation", "")}
                for u, v, d in self.graph.edges(data=True)
            ],
        }
        self._file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_entities(self, entities: list[dict]):
        """添加实体节点"""
        for e in entities:
            if e["name"] not in self.graph:
                self.graph.add_node(e["name"], type=e.get("type", "未知"))

    def add_relations(self, relations: list[dict]):
        """添加关系边"""
        for r in relations:
            src, tgt = r["source"], r["target"]
            if src in self.graph and tgt in self.graph:
                self.graph.add_edge(src, tgt, relation=r.get("relation", "关联"))

    def get_neighbors(self, node: str, depth: int = 1) -> dict:
        """获取节点的邻居（支持多跳）"""
        if node not in self.graph:
            return {"nodes": [], "edges": []}

        visited = set()
        result_nodes = []
        result_edges = []

        def bfs(current, current_depth):
            if current_depth > depth or current in visited:
                return
            visited.add(current)
            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    result_nodes.append({
                        "name": neighbor,
                        "type": self.graph.nodes[neighbor].get("type", "未知"),
                    })
                    result_edges.append({
                        "source": current,
                        "target": neighbor,
                        "relation": self.graph.edges[current, neighbor].get("relation", ""),
                    })
                    bfs(neighbor, current_depth + 1)
            for neighbor in self.graph.predecessors(current):
                if neighbor not in visited:
                    result_nodes.append({
                        "name": neighbor,
                        "type": self.graph.nodes[neighbor].get("type", "未知"),
                    })
                    result_edges.append({
                        "source": neighbor,
                        "target": current,
                        "relation": self.graph.edges[neighbor, current].get("relation", ""),
                    })
                    bfs(neighbor, current_depth + 1)

        result_nodes.append({"name": node, "type": self.graph.nodes[node].get("type", "未知")})
        bfs(node, 1)
        return {"nodes": result_nodes, "edges": result_edges}

    def find_paths(self, source: str, target: str, max_hops: int = 3) -> list[list[dict]]:
        """查找两个节点之间的所有路径（最多 max_hops 跳）"""
        if source not in self.graph or target not in self.graph:
            return []

        try:
            paths = list(nx.all_simple_paths(self.graph.to_undirected(), source, target, cutoff=max_hops))
        except nx.NetworkXError:
            return []

        result = []
        for path in paths:
            edges = []
            for i in range(len(path) - 1):
                if self.graph.has_edge(path[i], path[i + 1]):
                    rel = self.graph.edges[path[i], path[i + 1]].get("relation", "")
                elif self.graph.has_edge(path[i + 1], path[i]):
                    rel = self.graph.edges[path[i + 1], path[i]].get("relation", "")
                else:
                    rel = "关联"
                edges.append({"from": path[i], "relation": rel, "to": path[i + 1]})
            result.append({"path": path, "edges": edges})
        return result

    def get_all_nodes(self) -> list[dict]:
        return [
            {"name": n, "type": d.get("type", "未知"), "degree": self.graph.degree(n)}
            for n, d in self.graph.nodes(data=True)
        ]

    def get_all_edges(self) -> list[dict]:
        return [
            {"source": u, "target": v, "relation": d.get("relation", "")}
            for u, v, d in self.graph.edges(data=True)
        ]

    def pagerank(self) -> dict[str, float]:
        """计算 PageRank，识别核心节点"""
        if len(self.graph) == 0:
            return {}
        pr = nx.pagerank(self.graph.to_undirected())
        return dict(sorted(pr.items(), key=lambda x: x[1], reverse=True))

    def clear(self):
        self.graph.clear()
        if self._file.exists():
            self._file.unlink()
