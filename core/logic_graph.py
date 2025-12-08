"""逻辑图模块 - Node/Edge 数据结构与布局计算"""

import json
import math
from typing import TypedDict, List, Dict, Set


class NodeData(TypedDict):
    label: str


class Node(TypedDict):
    id: str
    data: NodeData
    position: dict  # {"x": float, "y": float}


class Edge(TypedDict):
    id: str
    source: str
    target: str
    label: str


class GraphData(TypedDict):
    nodes: list[Node]
    edges: list[Edge]


def create_node(node_id: str, label: str, x: float = 0, y: float = 0) -> Node:
    """创建节点"""
    return {
        "id": node_id,
        "data": {"label": label},
        "position": {"x": x, "y": y}
    }


def create_edge(source: str, target: str, label: str = "") -> Edge:
    """创建边"""
    return {
        "id": f"e{source}-{target}",
        "source": source,
        "target": target,
        "label": label
    }


def auto_layout(nodes: list[dict], edges: list[dict]) -> list[Node]:
    """智能自动布局：层次化布局算法"""
    if not nodes:
        return []
    
    # 构建邻接表
    graph: Dict[str, List[str]] = {node["id"]: [] for node in nodes}
    in_degree: Dict[str, int] = {node["id"]: 0 for node in nodes}
    
    for edge in edges:
        source, target = edge["source"], edge["target"]
        if source in graph and target in graph:
            graph[source].append(target)
            in_degree[target] += 1
    
    # 分层：使用拓扑排序
    layers: List[List[str]] = []
    current_layer: Set[str] = {node_id for node_id, degree in in_degree.items() if degree == 0}
    
    if not current_layer:  # 如果有环，将所有节点放在同一层
        current_layer = set(graph.keys())
    
    visited = set()
    while current_layer:
        layers.append(sorted(list(current_layer)))
        visited.update(current_layer)
        next_layer: Set[str] = set()
        
        for node_id in current_layer:
            for neighbor in graph[node_id]:
                if neighbor not in visited:
                    # 检查所有前驱节点是否都已访问
                    predecessors = [e["source"] for e in edges if e["target"] == neighbor]
                    if all(pred in visited for pred in predecessors):
                        next_layer.add(neighbor)
        
        current_layer = next_layer
        
        # 防止无限循环
        if len(visited) >= len(nodes):
            break
    
    # 添加未访问的节点（处理孤立节点）
    unvisited = set(graph.keys()) - visited
    if unvisited:
        layers.append(sorted(list(unvisited)))
    
    # 计算布局参数
    horizontal_spacing = 200
    vertical_spacing = 120
    start_x = 100
    start_y = 50
    
    # 生成布局
    laid_out = []
    for layer_idx, layer in enumerate(layers):
        layer_width = (len(layer) - 1) * horizontal_spacing if len(layer) > 1 else 0
        y = start_y + layer_idx * vertical_spacing
        
        for node_idx, node_id in enumerate(layer):
            # 居中排列
            if len(layer) == 1:
                x = start_x + horizontal_spacing * 2
            else:
                x = start_x + node_idx * horizontal_spacing
            
            # 查找原始节点数据
            original_node = next((n for n in nodes if n["id"] == node_id), None)
            if original_node:
                laid_out.append({
                    "id": node_id,
                    "data": original_node.get("data", {"label": f"Node {node_id}"}),
                    "position": {"x": x, "y": y}
                })
    
    return laid_out


def circular_layout(nodes: list[dict], radius: float = 300) -> list[Node]:
    """环形布局：将节点排列成圆形"""
    n = len(nodes)
    if n == 0:
        return []
    
    center_x, center_y = 400, 300
    laid_out = []
    
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        laid_out.append({
            "id": node["id"],
            "data": node.get("data", {"label": f"Node {node['id']}"}),
            "position": {"x": x, "y": y}
        })
    
    return laid_out


def grid_layout(nodes: list[dict], cols: int = 3, spacing: int = 150) -> list[Node]:
    """网格布局：将节点排列成网格"""
    laid_out = []
    start_x, start_y = 100, 50
    
    for i, node in enumerate(nodes):
        row = i // cols
        col = i % cols
        x = start_x + col * spacing
        y = start_y + row * spacing
        
        laid_out.append({
            "id": node["id"],
            "data": node.get("data", {"label": f"Node {node['id']}"}),
            "position": {"x": x, "y": y}
        })
    
    return laid_out


def parse_llm_json(llm_output: str, layout: str = "hierarchical") -> GraphData:
    """解析 LLM 输出的 JSON，添加布局坐标
    
    Args:
        llm_output: LLM 返回的 JSON 字符串
        layout: 布局类型 (hierarchical, circular, grid)
    """
    # 清理可能的 markdown 标记
    text = llm_output.strip()
    if text.startswith("```"):
        # 移除代码块标记
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
        text = text.replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"无法解析 JSON 数据: {e}\n原始输出: {text[:200]}...")
    
    # 根据布局类型生成节点位置
    raw_nodes = data.get("nodes", [])
    raw_edges = data.get("edges", [])
    
    if layout == "circular":
        nodes = circular_layout(raw_nodes)
    elif layout == "grid":
        nodes = grid_layout(raw_nodes)
    else:  # hierarchical (default)
        nodes = auto_layout(raw_nodes, raw_edges)
    
    edges = raw_edges

    return {"nodes": nodes, "edges": edges}


def empty_graph() -> GraphData:
    """返回空图数据"""
    return {"nodes": [], "edges": []}
