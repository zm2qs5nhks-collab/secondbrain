"""
知识图谱 —— 多架构视图（一份基础图谱 → 实时重组为不同结构）

架构清单（用户单选，Web / REST / MCP 均可选）：
  concept   概念关系网络       完整实体-关系网
  hierarchy 层级分类树         属于/包含/上下位
  timeline  时序/发展线        先于/之后/发展
  causal    因果链             导致/因为/解决
  flow      流程/步骤图        首先/然后/步骤
  radial    中心辐射/思维导图   以核心节点向外发散
  community 社区发现图         图算法划分群体
  topic     主题聚类图         按主题/标签聚合

设计：不额外存储，全部基于基础图谱实时计算；只改变“结构/布局”，不改变底层数据。
"""

import math
import random
import html as html_escape

import networkx as nx

from storage.extractor import infer_category, VALID_CATEGORIES

ARCHITECTURES = [
    {"id": "concept",   "name": "概念关系网络",     "desc": "完整实体-关系网状图，看全局联系"},
    {"id": "hierarchy", "name": "层级分类树",       "desc": "属于/包含/上下位，树状分类结构"},
    {"id": "timeline",  "name": "时序/发展线",      "desc": "先于/之后/发展，按脉络排列"},
    {"id": "causal",    "name": "因果链",           "desc": "导致/因为/解决，因果推理链"},
    {"id": "flow",      "name": "流程/步骤图",      "desc": "首先/然后/步骤，流程顺序"},
    {"id": "radial",    "name": "中心辐射/思维导图", "desc": "以核心节点为中心向外发散"},
    {"id": "community", "name": "社区发现图",       "desc": "自动划分知识群体/社区"},
    {"id": "topic",     "name": "主题聚类图",       "desc": "按主题/标签把节点聚成簇"},
    {"id": "list",      "name": "列表清单",         "desc": "以列表/表格直接罗列实体与关系（原始形式）"},
]
_BY_ID = {a["id"]: a for a in ARCHITECTURES}
# 架构 → 关系类别
_CAT_OF = {"hierarchy": "hierarchy", "timeline": "temporal", "causal": "causal", "flow": "sequential"}

# 类型 → 颜色
TYPE_COLORS = {
    "技术": "#4ECDC4", "概念": "#FFE66D", "场景": "#FF6B6B", "工具": "#95E1D3",
    "框架": "#A8D8EA", "方法": "#DCD6F7", "人物": "#F6C6EA", "事件": "#F7C59F",
    "指标": "#B5EAD7", "未知": "#CCCCCC",
}
# 分组调色板
GROUP_COLORS = [
    "#4ECDC4", "#FF6B6B", "#FFD93D", "#A8D8EA", "#B5EAD7", "#DCD6F7",
    "#F6C6EA", "#F7C59F", "#95E1D3", "#C7CEEA", "#FFB7B2", "#E2F0CB",
]


def list_architectures() -> list[dict]:
    """返回全部可选架构"""
    return [dict(a) for a in ARCHITECTURES]


def get_architecture(arch_id: str) -> dict:
    return _BY_ID.get((arch_id or "concept").lower(), _BY_ID["concept"])


def _edge_category(d: dict) -> str:
    cat = (d.get("category") or "").strip().lower()
    if cat in VALID_CATEGORIES:
        return cat
    return infer_category(d.get("relation", ""))


def _layer_dag(sub: nx.DiGraph) -> dict:
    """对有向子图分层（源点=0）；有环则退化用 BFS"""
    if len(sub) == 0:
        return {}
    try:
        order = list(nx.topological_sort(sub))
    except Exception:
        root = max(sub.nodes, key=lambda n: sub.in_degree(n))
        order = list(nx.bfs_tree(sub.to_undirected(), root))
    level = {}
    for n in order:
        preds = list(sub.predecessors(n))
        level[n] = 0 if not preds else max(level.get(p, 0) for p in preds) + 1
    return level


def _community_groups(G: nx.DiGraph):
    UG = G.to_undirected()
    try:
        comms = nx.community.louvain_communities(UG, seed=42)
    except Exception:
        comms = nx.community.greedy_modularity_communities(UG)
    groups, labels = {}, {}
    for i, c in enumerate(comms):
        c = list(c)
        rep = max(c, key=lambda n: G.degree(n)) if c else f"群 {i+1}"
        labels[i] = rep
        for n in c:
            groups[n] = i
    return groups, labels


def _topic_groups(G: nx.DiGraph, note_tags: dict | None):
    groups, labels = {}, {}
    for n, d in G.nodes(data=True):
        tags = []
        if note_tags:
            for nid in (d.get("notes") or []):
                tags += list(note_tags.get(nid, []) or [])
        if tags:
            key = max(set(tags), key=tags.count)
        else:
            key = d.get("type", "未分类") or "未分类"
        groups[n] = key
    for n, key in groups.items():
        labels.setdefault(key, key)
    return groups, labels


def build_view(kg, architecture: str = "concept", center: str = None,
               note_tags: dict | None = None, max_nodes: int = 300,
               hide_isolated: bool = False) -> dict:
    """基于基础图谱构建指定架构的视图（纯计算，不改数据）

    返回：
      {architecture, name, desc, layout, nodes[], edges[], groups[],
       stats{}, center, note}
      nodes: [{id,type,group,group_label,level,degree,size,notes}]
      edges: [{source,target,relation,category}]
      groups: [{id,label,color,size}]
    """
    G = kg.graph
    arch = (architecture or "concept").lower()
    if arch not in _BY_ID:
        arch = "concept"
    meta = _BY_ID[arch]
    view = {
        "architecture": arch, "name": meta["name"], "desc": meta["desc"],
        "layout": "force", "nodes": [], "edges": [], "groups": [],
        "stats": {"nodes": 0, "edges": 0, "groups": 0}, "center": None, "note": "",
    }
    if len(G.nodes) == 0:
        view["note"] = "图谱为空，请先添加笔记。"
        return view

    groups, group_labels, levels, sub = {}, {}, {}, G

    if arch == "list":
        sub, view["layout"] = G, "list"
    elif arch == "concept":
        sub, view["layout"] = G, "force"
    elif arch in _CAT_OF:
        cat = _CAT_OF[arch]
        sub = nx.DiGraph()
        for u, v, d in G.edges(data=True):
            if _edge_category(d) == cat:
                if u not in sub:
                    sub.add_node(u, **G.nodes[u])
                if v not in sub:
                    sub.add_node(v, **G.nodes[v])
                sub.add_edge(u, v, **d)
        view["layout"] = {"hierarchy": "tree", "timeline": "timeline",
                          "causal": "layered", "flow": "layered"}[arch]
        levels = _layer_dag(sub)
        if len(sub) == 0:
            view["note"] = (f"当前图谱里没有「{meta['name']}」类关系。"
                            "可在「添加笔记」用增强抽取补充，或换一个架构。")
    elif arch == "radial":
        sub = G
        view["layout"] = "radial"
        if not center or center not in G:
            pr = kg.pagerank()
            center = next(iter(pr), None) if pr else (list(G.nodes)[0] if G.nodes else None)
        view["center"] = center
        if center:
            lengths = nx.single_source_shortest_path_length(G.to_undirected(), center)
            levels = dict(lengths)
    elif arch == "community":
        sub, view["layout"] = G, "force"
        groups, group_labels = _community_groups(G)
    elif arch == "topic":
        sub, view["layout"] = G, "force"
        groups, group_labels = _topic_groups(G, note_tags)

    # 隐藏孤立节点（无任何连线）
    if hide_isolated:
        sub = sub.copy()
        for n in [n for n in list(sub.nodes) if sub.degree(n) == 0]:
            sub.remove_node(n)

    # 节点数限制（按度数取 top，避免超大图卡死）
    nodes_all = list(sub.nodes)
    if len(nodes_all) > max_nodes:
        nodes_all = sorted(nodes_all, key=lambda n: sub.degree(n), reverse=True)[:max_nodes]
        sub = sub.subgraph(nodes_all).copy()

    # 分组兜底：无显式分组时按类型分组（仅用于着色图例）
    if not groups:
        for n, d in sub.nodes(data=True):
            groups[n] = d.get("type", "未知")
        for g in set(groups.values()):
            group_labels.setdefault(g, g)

    # 组装节点
    degree = dict(sub.degree())
    max_deg = max(degree.values()) if degree else 1
    group_ids = list(dict.fromkeys(groups.values()))
    gcolor = {g: GROUP_COLORS[i % len(GROUP_COLORS)] for i, g in enumerate(group_ids)}
    nodes_out = []
    for n, d in sub.nodes(data=True):
        g = groups.get(n, "未知")
        nodes_out.append({
            "id": n,
            "type": d.get("type", "未知"),
            "group": g,
            "group_label": group_labels.get(g, str(g)),
            "level": levels.get(n, 0),
            "degree": degree.get(n, 0),
            "size": 14 + int((degree.get(n, 0) / max_deg) * 16),
            "notes": list(d.get("notes", [])),
        })
    edges_out = []
    for u, v, d in sub.edges(data=True):
        edges_out.append({
            "source": u, "target": v,
            "relation": d.get("relation", ""),
            "category": _edge_category(d),
        })

    groups_out = []
    for g in group_ids:
        size = sum(1 for n in sub.nodes if groups.get(n) == g)
        groups_out.append({"id": g, "label": group_labels.get(g, str(g)),
                           "color": gcolor[g], "size": size})
    groups_out.sort(key=lambda x: x["size"], reverse=True)

    view["nodes"] = nodes_out
    view["edges"] = edges_out
    view["groups"] = groups_out
    view["stats"] = {"nodes": len(nodes_out), "edges": len(edges_out), "groups": len(groups_out)}
    return view


def view_to_kg(view: dict):
    """把视图转换为一个临时 KnowledgeGraph（便于复用推理/分析/导出）"""
    from storage.graph import KnowledgeGraph
    kg = KnowledgeGraph.__new__(KnowledgeGraph)
    kg.user_id = "__view__"
    kg._file = None
    kg.graph = nx.DiGraph()
    for n in view.get("nodes", []):
        kg.graph.add_node(n["id"], type=n.get("type", "未知"), notes=list(n.get("notes", [])))
    for e in view.get("edges", []):
        kg.graph.add_edge(e["source"], e["target"],
                          relation=e.get("relation", ""),
                          category=e.get("category", ""), notes=[])
    return kg


# ═══════════════════════ 渲染（自包含 SVG/HTML） ═══════════════════════

def _spread(pos: dict, min_dist: float, W: int, H: int, PAD: int, iters: int = 60) -> dict:
    """简单松弛：把距离过近的节点互相推开，缓解重叠"""
    if len(pos) < 2:
        return pos
    ids = list(pos)
    rnd = random.Random(0)
    for _ in range(iters):
        moved = False
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                ax, ay = pos[a]
                bx, by = pos[b]
                dx, dy = bx - ax, by - ay
                d = math.hypot(dx, dy)
                if d < min_dist:
                    if d < 1e-6:
                        dx, dy, d = rnd.uniform(-1, 1), rnd.uniform(-1, 1), 1.0
                    push = (min_dist - d) / 2
                    ux, uy = dx / d, dy / d
                    pos[a] = (ax - ux * push, ay - uy * push)
                    pos[b] = (bx + ux * push, by + uy * push)
                    moved = True
        if not moved:
            break
    for k, (x, y) in list(pos.items()):
        pos[k] = (min(max(x, PAD), W - PAD), min(max(y, PAD), H - PAD))
    return pos


def _positions(view: dict, W: int = 1200, H: int = 860, PAD: int = 90) -> dict:
    nodes = view["nodes"]
    ids = [n["id"] for n in nodes]
    if not ids:
        return {}
    levels = {n["id"]: n.get("level", 0) for n in nodes}
    layout = view.get("layout", "force")
    pos = {}

    if layout in ("tree", "layered", "timeline"):
        by_level = {}
        for i in ids:
            by_level.setdefault(levels.get(i, 0), []).append(i)
        lvls = sorted(by_level)
        if layout == "timeline":
            order = [i for lv in lvls for i in by_level[lv]]
            m = max(len(order), 1)
            for xi, i in enumerate(order):
                pos[i] = (PAD + (xi + 0.5) / m * (W - 2 * PAD), H / 2)
        elif layout == "tree":
            n_lvl = max(len(lvls), 1)
            for li, lv in enumerate(lvls):
                row = by_level[lv]
                y = PAD + (li / max(n_lvl - 1, 1)) * (H - 2 * PAD)
                for xi, i in enumerate(row):
                    x = PAD + (xi + 0.5) / max(len(row), 1) * (W - 2 * PAD)
                    pos[i] = (x, y)
        else:  # layered
            n_lvl = max(len(lvls), 1)
            for li, lv in enumerate(lvls):
                col = by_level[lv]
                x = PAD + (li / max(n_lvl - 1, 1)) * (W - 2 * PAD)
                for yi, i in enumerate(col):
                    y = PAD + (yi + 0.5) / max(len(col), 1) * (H - 2 * PAD)
                    pos[i] = (x, y)
    elif layout == "radial":
        by_level = {}
        for i in ids:
            by_level.setdefault(levels.get(i, 0), []).append(i)
        lvls = sorted(by_level)
        cx, cy = W / 2, H / 2
        maxr = min(W, H) / 2 - PAD
        for li, lv in enumerate(lvls):
            ring = by_level[lv]
            r = 0 if li == 0 else maxr * (li / max(len(lvls) - 1, 1))
            for xi, i in enumerate(ring):
                ang = 2 * math.pi * (xi / max(len(ring), 1))
                pos[i] = (cx + r * math.cos(ang), cy + r * math.sin(ang))
    else:  # force
        g = nx.Graph()
        g.add_nodes_from(ids)
        g.add_edges_from((e["source"], e["target"]) for e in view["edges"])
        n = max(len(ids), 2)
        try:
            if len(g) <= 150:
                raw = nx.kamada_kawai_layout(g)
            else:
                raw = nx.spring_layout(g, seed=42, k=2.6 / math.sqrt(n), iterations=200)
        except Exception:
            raw = nx.spring_layout(g, seed=42, k=2.6 / math.sqrt(n), iterations=200)
        xs = [p[0] for p in raw.values()]
        ys = [p[1] for p in raw.values()]
        xspan = max(max(xs) - min(xs), 1e-6)
        yspan = max(max(ys) - min(ys), 1e-6)
        for i, (x, y) in raw.items():
            pos[i] = (PAD + (x - min(xs)) / xspan * (W - 2 * PAD),
                      PAD + (y - min(ys)) / yspan * (H - 2 * PAD))
    # 统一做一次防重叠松弛
    pos = _spread(pos, min_dist=86, W=W, H=H, PAD=PAD)
    return pos


def _list_to_html(view: dict, title: str) -> str:
    rows_e = "".join(
        f"<tr><td>{html_escape.escape(n['id'])}</td><td>{html_escape.escape(str(n.get('type','')))}</td>"
        f"<td>{n.get('degree', 0)}</td><td>{html_escape.escape(str(n.get('group_label','')))}</td></tr>"
        for n in view["nodes"]
    )
    rows_r = "".join(
        f"<tr><td>{html_escape.escape(e['source'])}</td><td>{html_escape.escape(str(e.get('relation','')))}</td>"
        f"<td>{html_escape.escape(e['target'])}</td><td>{html_escape.escape(str(e.get('category','')))}</td></tr>"
        for e in view["edges"]
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>{html_escape.escape(title)}</title>
<style>
 body{{font-family:'Microsoft YaHei',sans-serif;margin:0;background:#f5f6f8;color:#333}}
 .wrap{{padding:16px 20px}} h2{{font-size:16px;margin:0 0 4px}}
 .stat{{color:#666;font-size:12px;margin-bottom:12px}}
 table{{border-collapse:collapse;width:100%;background:#fff;margin-bottom:18px}}
 th,td{{border:1px solid #e0e2e6;padding:6px 10px;font-size:13px;text-align:left}}
 th{{background:#f0f2f5}} h3{{font-size:14px;margin:14px 0 6px}}
</style></head><body><div class="wrap">
 <h2>📋 {html_escape.escape(view['name'])} · {html_escape.escape(title)}</h2>
 <div class="stat">实体 {view['stats']['nodes']} · 关系 {view['stats']['edges']}</div>
 <h3>实体</h3>
 <table><thead><tr><th>实体</th><th>类型</th><th>连接数</th><th>分组</th></tr></thead><tbody>{rows_e}</tbody></table>
 <h3>关系</h3>
 <table><thead><tr><th>源</th><th>关系</th><th>目标</th><th>类别</th></tr></thead><tbody>{rows_r}</tbody></table>
</div></body></html>"""


def view_to_html(view: dict, title: str = "知识图谱") -> str:
    """把视图渲染为自包含交互式 HTML（可缩放/拖拽/点节点高亮）"""
    nodes = view["nodes"]
    if not nodes:
        return ("<html><body style=\"font-family:sans-serif;padding:24px;color:#666\">"
                f"<h3>{html_escape.escape(title)}</h3><p>{html_escape.escape(view.get('note') or '暂无数据')}</p>"
                "</body></html>")
    if view.get("layout") == "list":
        return _list_to_html(view, title)

    W, H = 1200, 860
    pos = _positions(view, W, H)
    group_color = {g["id"]: g["color"] for g in view["groups"]}
    gmap = {n["id"]: n.get("group") for n in nodes}

    edges_svg = []
    for e in view["edges"]:
        if e["source"] not in pos or e["target"] not in pos:
            continue
        x1, y1 = pos[e["source"]]
        x2, y2 = pos[e["target"]]
        rel = html_escape.escape(e.get("relation", ""))
        edges_svg.append(
            f'<line data-s="{html_escape.escape(e["source"])}" data-t="{html_escape.escape(e["target"])}" '
            f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#9aa5b1" stroke-width="2" '
            f'marker-end="url(#arrow)" opacity="0.75"><title>{html_escape.escape(e["source"])} {rel} {html_escape.escape(e["target"])}</title></line>'
        )

    nodes_svg = []
    for n in nodes:
        x, y = pos[n["id"]]
        r = n.get("size", 16)
        color = group_color.get(gmap.get(n["id"]), TYPE_COLORS.get(n.get("type"), "#CCCCCC"))
        label = html_escape.escape(n["id"])
        sub = html_escape.escape(n.get("group_label", ""))
        nodes_svg.append(
            f'<g class="node" data-id="{label}" transform="translate({x:.1f},{y:.1f})">'
            f'<circle r="{r}" fill="{color}" stroke="#333" stroke-width="1.5">'
            f'<title>{label} · {html_escape.escape(n.get("type",""))} · {sub}</title></circle>'
            f'<text text-anchor="middle" dy="4" font-size="11" font-family="Microsoft YaHei,sans-serif" '
            f'font-weight="600" paint-order="stroke" stroke="#ffffff" stroke-width="3" stroke-linejoin="round">{label}</text>'
            f'</g>'
        )

    legend = "".join(
        f'<span style="margin-right:14px"><span style="display:inline-block;width:12px;height:12px;'
        f'background:{g["color"]};border:1px solid #333;border-radius:2px;margin-right:4px"></span>'
        f'{html_escape.escape(str(g["label"]))} ({g["size"]})</span>'
        for g in view["groups"][:20]
    )

    note = html_escape.escape(view.get("note") or "")
    note_html = f'<div class="tip" style="color:#c0392b">{note}</div>' if note else ""

    svg_body = f"""<svg id="kg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="#9aa5b1"/></marker></defs>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  {''.join(edges_svg)}
  {''.join(nodes_svg)}
</svg>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>{html_escape.escape(title)}</title>
<style>
 body{{margin:0;font-family:'Microsoft YaHei',sans-serif;background:#f5f6f8}}
 .head{{padding:12px 20px;background:#fff;border-bottom:1px solid #e0e2e6;display:flex;justify-content:space-between;align-items:center}}
 .head h1{{font-size:16px;margin:0}} .head .stat{{color:#666;font-size:12px}}
 .wrap{{padding:12px 20px}} .legend{{font-size:12px;color:#444;margin-bottom:8px}}
 #kg{{width:100%;max-height:74vh;background:#fff;border:1px solid #e0e2e6;border-radius:8px;cursor:grab}}
 #kg:active{{cursor:grabbing}} .node circle{{stroke-width:1.5;transition:opacity .15s;cursor:pointer}}
 .node text{{pointer-events:none}} .tip{{color:#888;font-size:12px;margin-top:6px}}
</style></head><body>
 <div class="head"><h1>🕸️ {html_escape.escape(view['name'])} · {html_escape.escape(title)}</h1>
   <div class="stat">节点 {view['stats']['nodes']} · 边 {view['stats']['edges']} · 分组 {view['stats']['groups']}</div></div>
 <div class="wrap">
   <div class="legend">{legend}</div>
   {note_html}
   <div id="kg-wrap">{svg_body}</div>
   <div class="tip">💡 点击节点高亮关联；滚轮缩放；拖拽平移；双击空白恢复。</div>
 </div>
<script>
(function(){{
  var svg=document.getElementById('kg');
  var nodes=[].slice.call(svg.querySelectorAll('g.node'));
  var edges=[].slice.call(svg.querySelectorAll('line[data-s]'));
  var vb=svg.getAttribute('viewBox').split(' ').map(Number);
  var W0=vb[2],H0=vb[3];
  var scale=1,ox=0,oy=0;
  function apply(){{svg.setAttribute('viewBox',(vb[0]+ox)+' '+(vb[1]+oy)+' '+(W0/scale)+' '+(H0/scale));}}
  nodes.forEach(function(n){{n.addEventListener('click',function(){{
    var id=n.getAttribute('data-id');
    nodes.forEach(function(x){{x.style.opacity=(x.getAttribute('data-id')===id)?1:0.12;}});
    edges.forEach(function(e){{var s=e.getAttribute('data-s'),t=e.getAttribute('data-t');e.style.opacity=(s===id||t===id)?1:0.06;}});
  }});}});
  svg.addEventListener('dblclick',function(){{nodes.forEach(function(x){{x.style.opacity=1;}});edges.forEach(function(e){{e.style.opacity=0.75;}});}});
  svg.addEventListener('wheel',function(ev){{
    ev.preventDefault();
    var rect=svg.getBoundingClientRect();
    var cx=(ev.clientX-rect.left)/rect.width, cy=(ev.clientY-rect.top)/rect.height;
    var mx=vb[0]+ox+cx*(W0/scale), my=vb[1]+oy+cy*(H0/scale);
    var f=ev.deltaY>0?0.87:1.15;
    scale=Math.min(Math.max(scale*f,0.3),8);
    ox=mx-vb[0]-cx*(W0/scale); oy=my-vb[1]-cy*(H0/scale);
    apply();
  }},{{passive:false}});
  var drag=false,sx=0,sy=0;
  svg.addEventListener('mousedown',function(ev){{if(ev.target.closest('g.node'))return;drag=true;sx=ev.clientX;sy=ev.clientY;ev.preventDefault();}});
  window.addEventListener('mousemove',function(ev){{
    if(!drag)return;
    var rect=svg.getBoundingClientRect();
    var dx=(ev.clientX-sx)*(W0/scale)/rect.width;
    var dy=(ev.clientY-sy)*(H0/scale)/rect.height;
    ox-=dx; oy-=dy; sx=ev.clientX; sy=ev.clientY; apply();
  }});
  window.addEventListener('mouseup',function(){{drag=false;}});
  var tsx=0,tsy=0;
  svg.addEventListener('touchstart',function(ev){{if(ev.touches.length===1){{drag=true;tsx=ev.touches[0].clientX;tsy=ev.touches[0].clientY;}}}},{{passive:true}});
  svg.addEventListener('touchmove',function(ev){{
    if(!drag||ev.touches.length!==1)return;
    var rect=svg.getBoundingClientRect(); var t=ev.touches[0];
    var dx=(t.clientX-tsx)*(W0/scale)/rect.width;
    var dy=(t.clientY-tsy)*(H0/scale)/rect.height;
    ox-=dx; oy-=dy; tsx=t.clientX; tsy=t.clientY; apply();
  }},{{passive:true}});
  svg.addEventListener('touchend',function(){{drag=false;}});
}})();
</script></body></html>"""
