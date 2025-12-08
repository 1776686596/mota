"""逻辑图辅助函数

提供节点和边的样式生成、导出格式转换等功能
"""

from typing import List, Dict, Any
import io
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from PIL import Image


# 中文字体配置
CHINESE_FONTS = [
    'Noto Sans CJK SC',      # 思源黑体简体
    'WenQuanYi Micro Hei',   # 文泉驿微米黑
    'Noto Sans CJK JP',      # 思源黑体日文
    'SimHei',                # Windows 黑体
    'Microsoft YaHei',       # 微软雅黑
]


def _setup_chinese_font():
    """配置中文字体支持"""
    plt.rcParams['font.sans-serif'] = CHINESE_FONTS + ['DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False


def create_node_style(color: str) -> Dict[str, Any]:
    """创建节点样式
    
    Args:
        color: 节点背景颜色
        
    Returns:
        节点样式字典
    """
    return {
        "background": color,
        "color": "#FFFFFF",
        "border": "2px solid #2C3E50",
        "borderRadius": "8px",
        "padding": "12px",
        "fontSize": "14px",
        "fontWeight": "500",
        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
        "minWidth": "150px",
        "textAlign": "center"
    }


def create_edge_style() -> Dict[str, Any]:
    """创建边样式
    
    Returns:
        边样式字典
    """
    return {
        "style": {
            "stroke": "#95A5A6",
            "strokeWidth": 2
        },
        "label_style": {
            "fill": "#2C3E50",
            "fontSize": "12px",
            "fontWeight": "600"
        },
        "label_bg_style": {
            "fill": "#ECF0F1",
            "fillOpacity": 0.9
        },
        "marker_end": {"type": "arrowclosed", "color": "#95A5A6"}
    }


def generate_mermaid_code(nodes: List, edges: List) -> str:
    """生成 Mermaid 流程图代码
    
    Args:
        nodes: 节点列表
        edges: 边列表
        
    Returns:
        Mermaid 代码字符串
    """
    mermaid_code = "graph TD\n"
    for node in nodes:
        node_label = node.data.get("content", "").replace('"', "'")
        mermaid_code += f'    {node.id}["{node_label}"]\n'
    for edge in edges:
        edge_label = edge.label if edge.label else ""
        if edge_label:
            mermaid_code += f'    {edge.source} -->|{edge_label}| {edge.target}\n'
        else:
            mermaid_code += f'    {edge.source} --> {edge.target}\n'
    return mermaid_code


def generate_python_code(nodes: List, edges: List) -> str:
    """生成 Python 代码
    
    Args:
        nodes: 节点列表
        edges: 边列表
        
    Returns:
        Python 代码字符串
    """
    python_code = '''"""
逻辑图 Python 代码
使用 streamlit-flow 重现此图
"""

from streamlit_flow import StreamlitFlowNode, StreamlitFlowEdge

# 节点定义
nodes = [
'''
    for node in nodes:
        python_code += f'''    StreamlitFlowNode(
        id="{node.id}",
        pos=({node.position['x']}, {node.position['y']}),
        data={{"content": "{node.data.get("content", "")}"}},
        node_type="default",
        draggable=True,
        style={node.style}
    ),
'''
    python_code += ''']\n
# 边定义
edges = [
'''
    for edge in edges:
        python_code += f'''    StreamlitFlowEdge(
        id="{edge.id}",
        source="{edge.source}",
        target="{edge.target}",
        label="{edge.label}",
        animated=True
    ),
'''
    python_code += ''']
'''
    return python_code


def generate_graphml_code(nodes: List, edges: List) -> str:
    """生成 GraphML 代码
    
    Args:
        nodes: 节点列表
        edges: 边列表
        
    Returns:
        GraphML 代码字符串
    """
    graphml_code = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="label" for="node" attr.name="label" attr.type="string"/>
  <key id="x" for="node" attr.name="x" attr.type="double"/>
  <key id="y" for="node" attr.name="y" attr.type="double"/>
  <key id="label" for="edge" attr.name="label" attr.type="string"/>
  <graph id="G" edgedefault="directed">
'''
    for node in nodes:
        graphml_code += f'''    <node id="{node.id}">
      <data key="label">{node.data.get("content", "")}</data>
      <data key="x">{node.position['x']}</data>
      <data key="y">{node.position['y']}</data>
    </node>
'''
    for i, edge in enumerate(edges):
        graphml_code += f'''    <edge id="e{i}" source="{edge.source}" target="{edge.target}">
      <data key="label">{edge.label}</data>
    </edge>
'''
    graphml_code += '''  </graph>
</graphml>
'''
    return graphml_code


def generate_graph_image(nodes: List, edges: List, format: str = 'png', dpi: int = 300) -> bytes:
    """生成逻辑图图片
    
    Args:
        nodes: 节点列表
        edges: 边列表
        format: 图片格式 ('png', 'jpg', 'svg')
        dpi: 图片分辨率
        
    Returns:
        图片字节数据
    """
    # 配置中文字体
    _setup_chinese_font()
    
    # 创建有向图
    G = nx.DiGraph()
    
    # 添加节点
    node_labels = {}
    node_colors = []
    for node in nodes:
        G.add_node(node.id)
        node_labels[node.id] = node.data.get("content", "")
        # 从节点样式中提取颜色
        bg_color = node.style.get("background", "#95A5A6")
        node_colors.append(bg_color)
    
    # 添加边
    edge_labels = {}
    for edge in edges:
        G.add_edge(edge.source, edge.target)
        if edge.label:
            edge_labels[(edge.source, edge.target)] = edge.label
    
    # 设置图形大小和 DPI
    fig, ax = plt.subplots(figsize=(16, 12), dpi=dpi)
    ax.set_facecolor('white')
    
    # 使用层次布局
    try:
        # 尝试使用 hierarchical 布局
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    except:
        # 如果失败，使用 spring 布局
        pos = nx.spring_layout(G, seed=42)
    
    # 绘制边
    nx.draw_networkx_edges(
        G, pos,
        edge_color='#95A5A6',
        width=2,
        alpha=0.6,
        arrows=True,
        arrowsize=20,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1',
        ax=ax
    )
    
    # 绘制节点
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=3000,
        alpha=0.9,
        edgecolors='#2C3E50',
        linewidths=2,
        ax=ax
    )
    
    # 绘制节点标签
    nx.draw_networkx_labels(
        G, pos,
        labels=node_labels,
        font_size=10,
        font_color='white',
        font_weight='bold',
        font_family='sans-serif',
        ax=ax
    )
    
    # 绘制边标签
    if edge_labels:
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=edge_labels,
            font_size=9,
            font_color='#2C3E50',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ECF0F1', alpha=0.8, edgecolor='none'),
            ax=ax
        )
    
    # 设置标题
    plt.title('逻辑流程图', fontsize=16, fontweight='bold', pad=20, fontfamily='sans-serif')
    
    # 移除坐标轴
    ax.set_axis_off()
    
    # 调整布局
    plt.tight_layout()
    
    # 保存到字节流
    buf = io.BytesIO()
    if format.lower() == 'svg':
        plt.savefig(buf, format='svg', bbox_inches='tight', facecolor='white')
    elif format.lower() in ['jpg', 'jpeg']:
        plt.savefig(buf, format='jpeg', bbox_inches='tight', facecolor='white', dpi=dpi)
    else:  # png
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor='white', dpi=dpi)
    
    plt.close(fig)
    
    buf.seek(0)
    return buf.getvalue()