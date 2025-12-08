"""逻辑图标签页 UI 组件

处理逻辑图生成和编辑相关的所有 UI 交互
"""

import streamlit as st
import json
from streamlit_flow import streamlit_flow, StreamlitFlowNode, StreamlitFlowEdge, StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
from core.logic_graph import parse_llm_json
from core.llm_service import LLMService
from .logic_graph_helpers import (
    generate_mermaid_code,
    generate_python_code,
    generate_graphml_code,
    generate_graph_image,
    create_node_style,
    create_edge_style
)
from .styles import render_loading


def render_logic_graph_tab():
    """渲染逻辑图标签页"""
    # st.header("交互式逻辑图") # 移除旧标题
    st.markdown("### 🧠 实验逻辑梳理")
    st.markdown("输入实验步骤文本，AI 自动转换为可视化的流程逻辑图。")

    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        with st.container():
            _render_input_section()
    
    with col2:
        with st.container():
            _render_manual_controls()
    
    st.divider()
    # 交互式画布
    _render_canvas()


def _render_input_section():
    """渲染输入区域"""
    st.markdown("#### 📝 文本描述")
    text_input = st.text_area(
        "在此输入实验流程或逻辑描述",
        placeholder="例如：\n1. 首先将样品 A 与试剂 B 混合，在 50°C 下搅拌 2 小时。\n2. 冷却至室温后，进行离心分离。\n3. 上清液用于 HPLC 分析，沉淀物经洗涤干燥后进行 XRD 表征。",
        height=220,
        max_chars=10000,
        help="支持长文本输入，描述越清晰，生成的逻辑图越准确。",
        label_visibility="collapsed"
    )
    
    # 输入验证
    text_valid = True
    if text_input:
        if len(text_input.strip()) < 10:
            st.warning("⚠️ 流程描述至少需要 10 个字符")
            text_valid = False
    
    col_layout, col_btn = st.columns([1, 2])
    with col_layout:
        layout_type = st.selectbox(
            "布局算法",
            ["hierarchical", "circular", "grid"],
            format_func=lambda x: {"hierarchical": "层次 (Hierarchical)", "circular": "环形 (Circular)", "grid": "网格 (Grid)"}[x],
            help="选择生成图表的节点排列方式"
        )
    
    with col_btn:
        st.write("") # Spacer to align button
        st.write("")
        if st.button("🤖 AI 智能生成 / 重绘", type="primary", use_container_width=True):
            _handle_ai_generation(text_input, text_valid, layout_type)


def _get_llm_service():
    """获取 LLM 服务实例，优先使用用户配置，否则使用后台配置"""
    config_manager = st.session_state.config_manager
    effective_config = config_manager.get_effective_llm_config()
    
    if effective_config.get("api_key"):
        return LLMService(
            base_url=effective_config.get("base_url"),
            api_key=effective_config.get("api_key"),
            model=effective_config.get("model")
        )
    return None


def _has_llm_available():
    """检查是否有可用的 LLM 配置"""
    config_manager = st.session_state.config_manager
    return bool(st.session_state.get("llm_api_key")) or config_manager.has_backend_config()


def _handle_ai_generation(text_input: str, text_valid: bool, layout_type: str):
    """处理 AI 生成逻辑图"""
    if text_input and text_valid and _has_llm_available():
        # 显示终端加载动画
        loading_placeholder = st.empty()
        
        try:
            # 步骤 1: 分析流程
            with loading_placeholder.container():
                render_loading("Analyzing flow...")
            
            llm = _get_llm_service()
            if llm is None:
                loading_placeholder.empty()
                st.error("❌ 无法获取 LLM 服务")
                return
            
            result = llm.generate_logic_graph(text_input)
            
            # 步骤 2: 生成图表
            with loading_placeholder.container():
                render_loading("Building graph...")
            
            graph_data = parse_llm_json(result, layout=layout_type)
            
            # 定义节点颜色方案
            node_colors = ["#4A90E2", "#50C878", "#FFB347", "#FF6B6B", "#9B59B6", "#3498DB"]
            
            # 转换为 StreamlitFlowNode/Edge
            st.session_state.graph_nodes = [
                StreamlitFlowNode(
                    id=n["id"],
                    pos=(n["position"]["x"], n["position"]["y"]),
                    data={"content": n["data"]["label"]},
                    node_type="default",
                    draggable=True,
                    style=create_node_style(node_colors[i % len(node_colors)])
                ) for i, n in enumerate(graph_data["nodes"])
            ]
            
            st.session_state.graph_edges = [
                StreamlitFlowEdge(
                    id=e["id"],
                    source=e["source"],
                    target=e["target"],
                    label=e.get("label", ""),
                    animated=True,
                    **create_edge_style()
                ) for e in graph_data["edges"]
            ]
            
            st.session_state.node_counter = len(graph_data["nodes"])
            st.session_state.graph_version += 1
            st.session_state.flow_state = None
            
            # 清除加载动画
            loading_placeholder.empty()
            
            st.success(f"✅ 已生成 {len(graph_data['nodes'])} 个节点和 {len(graph_data['edges'])} 条边")
            
        except Exception as e:
            loading_placeholder.empty()
            st.error(f"❌ 生成失败: {str(e)}")
            with st.expander("🔍 查看详细错误"):
                st.code(str(e))
    elif not _has_llm_available():
        st.warning("⚠️ 请先在侧边栏配置 API Key，或使用平台提供的免费服务")
    else:
        st.warning("⚠️ 请输入流程描述")


def _render_manual_controls():
    """渲染手动操作控件"""
    st.markdown("#### 🛠️ 画布工具")
    
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("➕ 添加节点", use_container_width=True):
            _add_new_node()
    with col_clear:
        if st.button("🗑️ 清空画布", use_container_width=True):
            _clear_canvas()
    
    # 节点编辑功能
    if st.session_state.selected_node:
        _render_node_editor()
    else:
        st.info("👆 点击画布中的节点进行编辑")
    
    # 导出功能
    if st.session_state.graph_nodes:
        _render_export_section()
        _render_canvas_settings()


def _add_new_node():
    """添加新节点"""
    st.session_state.node_counter += 1
    new_id = str(st.session_state.node_counter)
    st.session_state.graph_nodes.append(
        StreamlitFlowNode(
            id=new_id,
            pos=(250, len(st.session_state.graph_nodes) * 100 + 50),
            data={"content": f"新节点 {new_id}"},
            node_type="default",
            draggable=True,
            style=create_node_style("#95A5A6")
        )
    )
    st.session_state.graph_version += 1
    st.session_state.flow_state = None
    st.rerun()


def _render_node_editor():
    """渲染节点编辑器"""
    st.divider()
    st.write("### ✏️ 编辑节点")
    node_id = st.session_state.selected_node
    node = next((n for n in st.session_state.graph_nodes if n.id == node_id), None)
    
    if node:
        new_label = st.text_input("节点文本", value=node.data.get("content", ""), key=f"edit_label_{node_id}")
        
        # 颜色选择
        colors = {
            "蓝色": "#4A90E2",
            "绿色": "#50C878",
            "橙色": "#FFB347",
            "红色": "#FF6B6B",
            "紫色": "#9B59B6",
            "灰色": "#95A5A6"
        }
        current_color = node.style.get("background", "#95A5A6")
        color_name = next((k for k, v in colors.items() if v == current_color), "灰色")
        new_color_name = st.selectbox("节点颜色", list(colors.keys()), index=list(colors.keys()).index(color_name))
        
        col_save, col_del = st.columns(2)
        with col_save:
            if st.button("💾 保存", use_container_width=True):
                node.data["content"] = new_label
                node.style["background"] = colors[new_color_name]
                st.session_state.graph_version += 1
                st.session_state.flow_state = None
                st.session_state.selected_node = None
                st.rerun()
        
        with col_del:
            if st.button("🗑️ 删除节点", use_container_width=True, type="secondary"):
                st.session_state.graph_nodes = [n for n in st.session_state.graph_nodes if n.id != node_id]
                st.session_state.graph_edges = [
                    e for e in st.session_state.graph_edges 
                    if e.source != node_id and e.target != node_id
                ]
                st.session_state.graph_version += 1
                st.session_state.flow_state = None
                st.session_state.selected_node = None
                st.rerun()


def _clear_canvas():
    """清空画布"""
    st.session_state.graph_nodes = []
    st.session_state.graph_edges = []
    st.session_state.node_counter = 0
    st.session_state.graph_version += 1
    st.session_state.flow_state = None
    st.rerun()


def _render_export_section():
    """渲染导出区域"""
    st.divider()
    st.write("### 📤 导出")
    
    # 准备导出数据
    graph_json = {
        "nodes": [
            {
                "id": n.id,
                "label": n.data.get("content", ""),
                "position": {"x": n.position['x'], "y": n.position['y']},
                "style": n.style
            }
            for n in st.session_state.graph_nodes
        ],
        "edges": [
            {
                "id": e.id,
                "source": e.source,
                "target": e.target,
                "label": e.label
            }
            for e in st.session_state.graph_edges
        ]
    }
    
    # 图片导出选项
    st.write("#### 🖼️ 导出图片")
    
    col1, col2 = st.columns(2)
    with col1:
        image_format = st.selectbox(
            "图片格式",
            ["PNG", "JPG", "SVG"],
            help="选择导出的图片格式"
        )
    
    with col2:
        image_dpi = st.selectbox(
            "图片质量",
            [150, 300, 600],
            index=1,
            format_func=lambda x: f"{x} DPI",
            help="DPI 越高，图片质量越好，文件也越大"
        )
    
    # 生成并下载图片
    try:
        image_bytes = generate_graph_image(
            st.session_state.graph_nodes,
            st.session_state.graph_edges,
            format=image_format.lower(),
            dpi=image_dpi
        )
        
        file_ext = image_format.lower()
        mime_type = f"image/{file_ext}" if file_ext != "svg" else "image/svg+xml"
        
        st.download_button(
            f"🖼️ 下载 {image_format} 图片",
            image_bytes,
            f"logic_graph.{file_ext}",
            mime_type,
            use_container_width=True
        )
    except Exception as e:
        st.error(f"图片生成失败: {str(e)}")
    
    st.divider()
    st.write("#### 📝 导出代码")
    
    # JSON 格式
    json_str = json.dumps(graph_json, ensure_ascii=False, indent=2)
    st.download_button(
        "📄 导出 JSON",
        json_str,
        "logic_graph.json",
        "application/json",
        use_container_width=True
    )
    
    # 其他格式导出
    st.download_button(
        "🔷 导出 Mermaid",
        generate_mermaid_code(st.session_state.graph_nodes, st.session_state.graph_edges),
        "logic_graph.mmd",
        "text/plain",
        use_container_width=True
    )
    
    st.download_button(
        "🐍 导出 Python 代码",
        generate_python_code(st.session_state.graph_nodes, st.session_state.graph_edges),
        "logic_graph.py",
        "text/plain",
        use_container_width=True
    )
    
    st.download_button(
        "📊 导出 GraphML",
        generate_graphml_code(st.session_state.graph_nodes, st.session_state.graph_edges),
        "logic_graph.graphml",
        "application/xml",
        use_container_width=True
    )


def _render_canvas_settings():
    """渲染画布设置"""
    st.divider()
    
    canvas_size = st.radio(
        "画布大小",
        ["正常 (500px)", "大屏 (900px)"],
        key="canvas_size_radio",
        horizontal=True
    )
    
    st.metric("节点数量", len(st.session_state.graph_nodes))
    st.metric("连接数量", len(st.session_state.graph_edges))


def _render_canvas():
    """渲染交互式画布"""
    if st.session_state.graph_nodes:
        # 根据画布大小选项调整高度
        canvas_size = st.session_state.get("canvas_size_radio", "正常 (500px)")
        if "大屏" in canvas_size:
            st.subheader("🖥️ 画布区域 - 大屏模式")
            canvas_height = 900
        else:
            st.subheader("画布区域")
            canvas_height = 500
        
        try:
            # 只有在数据更新时才重新创建 StreamlitFlowState 对象
            if st.session_state.flow_state is None:
                st.session_state.flow_state = StreamlitFlowState(
                    st.session_state.graph_nodes,
                    st.session_state.graph_edges
                )
            
            # 使用版本号作为 key 的一部分
            flow_key = f"logic_flow_v{st.session_state.graph_version}"
            
            # 启用交互功能
            result = streamlit_flow(
                key=flow_key,
                state=st.session_state.flow_state,
                layout=TreeLayout(direction="down"),
                fit_view=True,
                height=canvas_height,
                enable_node_menu=True,
                enable_edge_menu=True,
                enable_pane_menu=False,
                get_node_on_click=True,
                get_edge_on_click=False,
                allow_new_edges=True,
                animate_new_edges=True,
                show_minimap=True
            )
            
            # 处理节点点击事件
            if result and hasattr(result, 'selected_id'):
                if result.selected_id and result.selected_id != st.session_state.selected_node:
                    st.session_state.selected_node = result.selected_id
                    st.rerun()
        except Exception as e:
            st.error(f"❌ 画布渲染失败: {str(e)}")
            with st.expander("🔍 查看详细错误"):
                st.code(str(e))
    else:
        st.subheader("画布区域")
        st.info("画布为空，请 AI 生成或手动添加节点")