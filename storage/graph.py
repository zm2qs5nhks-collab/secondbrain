"""
知识图谱构建与查询 —— 基于 NetworkX

v2 增强：
- 实体/关系可标注来源笔记（notes 字段），便于按笔记子集构建图谱
- 提供 build_subgraph：按所选笔记集合构建子图
- 提供多种导出格式：GraphML / JSON / CSV(打包zip) / PNG / 交互式HTML
"""

import json
import io
import zipfile
import html as html_escape
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

    # ─────────── 加载 / 保存 ───────────
    def load(self):
        """从文件加载图谱（兼容旧数据，无 notes 视为通用实体）"""
        if self._file.exists():
            data = json.loads(self._file.read_text(encoding="utf-8"))
            for entity in data.get("entities", []):
                self.graph.add_node(
                    entity["name"],
                    type=entity.get("type", "未知"),
                    notes=entity.get("notes", []),
                )
            for rel in data.get("relations", []):
                if rel["source"] in self.graph and rel["target"] in self.graph:
                    self.graph.add_edge(
                        rel["source"], rel["target"],
                        relation=rel["relation"],
                        notes=rel.get("notes", []),
                    )

    def save(self):
        """保存图谱到文件"""
        if self._file is None:
            return
        data = {
            "entities": [
                {
                    "name": n,
                    "type": self.graph.nodes[n].get("type", "未知"),
                    "notes": list(self.graph.nodes[n].get("notes", [])),
                }
                for n in self.graph.nodes
            ],
            "relations": [
                {
                    "source": u, "target": v,
                    "relation": d.get("relation", ""),
                    "notes": list(d.get("notes", [])),
                }
                for u, v, d in self.graph.edges(data=True)
            ],
        }
        self._file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ─────────── 添加 ───────────
    def add_entities(self, entities: list[dict], note_id: str = None):
        """添加实体节点；note_id 用于标注来源笔记"""
        for e in entities:
            if e["name"] not in self.graph:
                self.graph.add_node(e["name"], type=e.get("type", "未知"), notes=[])
            if note_id:
                notes = self.graph.nodes[e["name"]].setdefault("notes", [])
                if note_id not in notes:
                    notes.append(note_id)

    def add_relations(self, relations: list[dict], note_id: str = None):
        """添加关系边；note_id 用于标注来源笔记"""
        for r in relations:
            src, tgt = r["source"], r["target"]
            if src in self.graph and tgt in self.graph:
                if not self.graph.has_edge(src, tgt):
                    self.graph.add_edge(src, tgt, relation=r.get("relation", "关联"), notes=[])
                edge_notes = self.graph.edges[src, tgt].setdefault("notes", [])
                if note_id and note_id not in edge_notes:
                    edge_notes.append(note_id)

    # ─────────── 子图构建 ───────────
    def build_subgraph(self, note_ids: list[str]) -> "KnowledgeGraph":
        """根据所选笔记集合，构建"仅含这些笔记相关实体/关系"的子图。

        - 未标注来源笔记的实体/关系（旧数据、通用实体）视为全局，始终保留
        - 标注了来源的，仅当与所选笔记有交集时保留
        - 返回新图谱对象（不写盘）
        """
        selected = set(note_ids or [])

        def _keep(notes):
            notes = list(notes or [])
            if not notes:
                return True
            return bool(selected & set(notes))

        sub = KnowledgeGraph.__new__(KnowledgeGraph)
        sub.user_id = self.user_id
        sub._file = None
        sub.graph = nx.DiGraph()

        for n, data in self.graph.nodes(data=True):
            if _keep(data.get("notes")):
                sub.graph.add_node(n, type=data.get("type", "未知"), notes=list(data.get("notes", [])))

        for u, v, data in self.graph.edges(data=True):
            if u in sub.graph and v in sub.graph and _keep(data.get("notes")):
                sub.graph.add_edge(u, v, relation=data.get("relation", "关联"), notes=list(data.get("notes", [])))
        return sub

    # ─────────── 查询 ───────────
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
            {"name": n, "type": d.get("type", "未知"), "notes": list(d.get("notes", [])), "degree": self.graph.degree(n)}
            for n, d in self.graph.nodes(data=True)
        ]

    def get_all_edges(self) -> list[dict]:
        return [
            {"source": u, "target": v, "relation": d.get("relation", ""), "notes": list(d.get("notes", []))}
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
        if self._file and self._file.exists():
            self._file.unlink()

    # ═══════════════ 导出功能 ═══════════════
    def to_json_bytes(self) -> bytes:
        """导出为 JSON 原始数据"""
        payload = {
            "exported_at": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id,
            "stats": {"nodes": len(self.graph.nodes), "edges": len(self.graph.edges)},
            "entities": [
                {"name": n, "type": d.get("type", "未知"), "notes": list(d.get("notes", []))}
                for n, d in self.graph.nodes(data=True)
            ],
            "relations": [
                {"source": u, "target": v, "relation": d.get("relation", ""), "notes": list(d.get("notes", []))}
                for u, v, d in self.graph.edges(data=True)
            ],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    def to_graphml_bytes(self) -> bytes:
        """导出为 GraphML（Gephi / Neo4j / Cytoscape 可导入）"""
        g = nx.DiGraph()
        for n, d in self.graph.nodes(data=True):
            g.add_node(n, type=d.get("type", "未知"))
        for u, v, d in self.graph.edges(data=True):
            g.add_edge(u, v, relation=d.get("relation", ""))
        try:
            return "".join(nx.generate_graphml(g)).encode("utf-8")
        except Exception:
            # 老版本 networkx 兼容
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".graphml", delete=False, encoding="utf-8") as f:
                nx.write_graphml(g, f.name)
                tmp_path = f.name
            with open(tmp_path, "rb") as f:
                data = f.read()
            import os
            os.unlink(tmp_path)
            return data

    def to_csv_zip(self) -> bytes:
        """导出为 zip（nodes.csv + relations.csv，Excel 可打开）"""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("nodes.csv", self._nodes_csv())
            zf.writestr("relations.csv", self._relations_csv())
        return buf.getvalue()

    def _nodes_csv(self) -> str:
        import csv as _csv
        out = io.StringIO()
        w = _csv.writer(out)
        w.writerow(["name", "type", "source_notes", "degree"])
        for n, d in self.graph.nodes(data=True):
            w.writerow([n, d.get("type", "未知"), ";".join(d.get("notes", []) or []), self.graph.degree(n)])
        return out.getvalue()

    def _relations_csv(self) -> str:
        import csv as _csv
        out = io.StringIO()
        w = _csv.writer(out)
        w.writerow(["source", "relation", "target", "source_notes"])
        for u, v, d in self.graph.edges(data=True):
            w.writerow([u, d.get("relation", ""), v, ";".join(d.get("notes", []) or [])])
        return out.getvalue()

    def to_png_bytes(self) -> bytes:
        """导出为 PNG 图片（依赖系统 graphviz 的 dot 命令）"""
        import graphviz as gv
        dot = self._to_dot()
        return gv.Source(dot).pipe(format="png")

    def to_html(self) -> str:
        """导出为自包含交互式 HTML（浏览器直接打开，点击节点高亮关联）"""
        return self._render_html()

    def _to_dot(self) -> str:
        lines = ["digraph KG {", "  rankdir=LR;", "  bgcolor=transparent;"]
        lines.append('  node [shape=box, style="rounded,filled", fontname="Microsoft YaHei", fontsize=10];')
        lines.append('  edge [fontname="Microsoft YaHei", fontsize=8, color="#666666"];')
        type_colors = {
            "技术": "#4ECDC4", "概念": "#FFE66D", "场景": "#FF6B6B",
            "工具": "#95E1D3", "框架": "#A8D8EA", "方法": "#DCD6F7",
        }
        for node, data in self.graph.nodes(data=True):
            ntype = data.get("type", "未知")
            color = type_colors.get(ntype, "#CCCCCC")
            safe = node.replace('"', '\\"')
            lines.append(f'  "{safe}" [label="{safe}\\n({ntype})", fillcolor="{color}"];')
        for u, v, data in self.graph.edges(data=True):
            rel = data.get("relation", "")
            safe_u = u.replace('"', '\\"')
            safe_v = v.replace('"', '\\"')
            lines.append(f'  "{safe_u}" -> "{safe_v}" [label="{rel}"];')
        lines.append("}")
        return "\n".join(lines)

    def _render_html(self) -> str:
        """生成自包含 HTML，内嵌 NetworkX 布局 + 交互 JS，离线可用"""
        if len(self.graph.nodes) == 0:
            return "<html><body><h3>图谱为空</h3></body></html>"

        layout = nx.spring_layout(self.graph, seed=42, k=0.6)
        xs = [p[0] for p in layout.values()]
        ys = [p[1] for p in layout.values()]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        W, H, PAD = 1000, 720, 90
        xspan = max((xmax - xmin), 1e-6)
        yspan = max((ymax - ymin), 1e-6)

        def _px(name):
            x, y = layout[name]
            px = (x - xmin) / xspan * (W - 2 * PAD) + PAD
            py = (y - ymin) / yspan * (H - 2 * PAD) + PAD
            return px, py

        type_colors = {
            "技术": "#4ECDC4", "概念": "#FFE66D", "场景": "#FF6B6B",
            "工具": "#95E1D3", "框架": "#A8D8EA", "方法": "#DCD6F7",
        }

        edges_svg = []
        for u, v, d in self.graph.edges(data=True):
            x1, y1 = _px(u)
            x2, y2 = _px(v)
            rel = html_escape.escape(d.get("relation", ""))
            edges_svg.append(
                f'<line data-s="{html_escape.escape(u)}" data-t="{html_escape.escape(v)}" '
                f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#9aa5b1" '
                f'stroke-width="2" marker-end="url(#arrow)" opacity="0.7">'
                f'<title>{html_escape.escape(u)} {html_escape.escape(rel)} {html_escape.escape(v)}</title></line>'
            )

        nodes_svg = []
        deg = dict(self.graph.degree())
        max_deg = max(deg.values()) if deg else 1
        for n, d in self.graph.nodes(data=True):
            x, y = _px(n)
            r = 14 + int((deg.get(n, 0) / max_deg) * 16)
            color = type_colors.get(d.get("type", "未知"), "#CCCCCC")
            label = html_escape.escape(n)
            notes = d.get("notes", []) or []
            notestr = "通用" if not notes else f"来自 {len(notes)} 篇笔记"
            nodes_svg.append(
                f'<g class="node" data-id="{label}" transform="translate({x:.1f},{y:.1f})">'
                f'<circle r="{r}" fill="{color}" stroke="#333" stroke-width="1.5">'
                f'<title>{label}\\n({html_escape.escape(d.get("type", "未知"))}) · {notestr}</title></circle>'
                f'<text text-anchor="middle" dy="4" font-size="11" font-family="Microsoft YaHei, sans-serif" font-weight="600">{label}</text>'
                f'</g>'
            )

        legend = "".join(
            f'<span style="margin-right:14px"><span style="display:inline-block;width:12px;height:12px;background:{c};border:1px solid #333;border-radius:2px;margin-right:4px"></span>{t}</span>'
            for t, c in type_colors.items()
        )

        svg_body = f"""<svg id="kg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="#9aa5b1"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  {''.join(edges_svg)}
  {''.join(nodes_svg)}
</svg>"""

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>知识图谱导出 · {html_escape.escape(self.user_id)}</title>
<style>
  body {{ margin:0; font-family:'Microsoft YaHei',sans-serif; background:#f5f6f8; }}
  .head {{ padding:16px 24px; background:#fff; border-bottom:1px solid #e0e2e6; display:flex; justify-content:space-between; align-items:center; }}
  .head h1 {{ font-size:18px; margin:0; }}
  .head .stat {{ color:#666; font-size:13px; }}
  .wrap {{ padding:16px 24px; }}
  .legend {{ font-size:12px; color:#444; margin-bottom:10px; }}
  #kg {{ width:100%; max-height:78vh; background:#fff; border:1px solid #e0e2e6; border-radius:8px; cursor:grab; }}
  #kg:active {{ cursor:grabbing; }}
  .node circle {{ stroke-width:1.5; transition: opacity .15s; cursor:pointer; }}
  .node text {{ pointer-events:none; }}
  .tip {{ color:#888; font-size:12px; }}
</style>
</head>
<body>
  <div class="head">
    <h1>🧠 知识图谱 · {html_escape.escape(self.user_id)}</h1>
    <div class="stat">节点 {len(self.graph.nodes)} · 边 {len(self.graph.edges)} · 生成时间 {__import__("time").strftime("%Y-%m-%d %H:%M")}</div>
  </div>
  <div class="wrap">
    <div class="legend">{legend}</div>
    <div id="kg-wrap">{svg_body}</div>
    <div class="tip">💡 点击节点高亮其所有关联；滚轮缩放；按住拖拽平移；双击空白恢复。</div>
  </div>
<script>
(function(){{
  var svg=document.getElementById('kg');
  var nodes=[].slice.call(svg.querySelectorAll('g.node'));
  var edges=[].slice.call(svg.querySelectorAll('line[data-s]'));
  var viewBox=svg.getAttribute('viewBox').split(' ').map(Number);
  var zoom=1, tx=0, ty=0;

  function applyView(){{
    svg.setAttribute('viewBox', (viewBox[0]+tx)+' '+(viewBox[1]+ty)+' '+(viewBox[2]/zoom)+' '+(viewBox[3]/zoom));
  }}

  nodes.forEach(function(n){{
    n.addEventListener('click',function(){{
      var id=n.getAttribute('data-id');
      nodes.forEach(function(x){{
        x.style.opacity=(x.getAttribute('data-id')===id)?1:0.12;
      }});
      edges.forEach(function(e){{
        var s=e.getAttribute('data-s'), t=e.getAttribute('data-t');
        e.style.opacity=(s===id||t===id)?1:0.06;
      }});
    }});
  }});

  svg.addEventListener('dblclick',function(){{
    nodes.forEach(function(x){{x.style.opacity=1;}});
    edges.forEach(function(e){{e.style.opacity=0.7;}});
  }});

  svg.addEventListener('wheel',function(ev){{
    ev.preventDefault();
    var f=ev.deltaY>0?1.15:0.87;
    zoom=Math.min(Math.max(zoom*f,0.3),8);
    applyView();
  }});

  var dragging=false, sx=0, sy=0;
  svg.addEventListener('mousedown',function(ev){{
    if(ev.target.closest('g.node')) return;
    dragging=true; sx=ev.clientX; sy=ev.clientY;
  }});
  window.addEventListener('mousemove',function(ev){{
    if(!dragging) return;
    tx+=(ev.clientX-sx); ty+=(ev.clientY-sy);
    sx=ev.clientX; sy=ev.clientY;
    applyView();
  }});
  window.addEventListener('mouseup',function(){{dragging=false;}});
}})();
</script>
</body>
</html>"""


def build_subgraph_from(kg: KnowledgeGraph, note_ids: list[str]) -> KnowledgeGraph:
    """便捷入口：从已有图谱构建子图"""
    return kg.build_subgraph(note_ids)