"""项目管理模块

提供项目保存、加载、导出功能
"""

import streamlit as st
import pandas as pd
import json
import base64
import io
from datetime import datetime
from typing import Optional, Dict, Any


def render_project_manager():
    """渲染项目管理界面"""
    st.markdown("### 💾 项目管理")
    st.markdown("保存和加载您的工作进度，随时继续分析")
    
    tab1, tab2, tab3 = st.tabs(["💾 保存项目", "📂 加载项目", "📤 导出报告"])
    
    with tab1:
        _render_save_project()
    
    with tab2:
        _render_load_project()
    
    with tab3:
        _render_export_report()


def _render_save_project():
    """渲染保存项目界面"""
    st.markdown("#### 保存当前项目")
    
    # 项目信息
    project_name = st.text_input(
        "项目名称",
        value=st.session_state.get("project_name", "未命名项目"),
        key="save_project_name"
    )
    
    project_desc = st.text_area(
        "项目描述（可选）",
        value=st.session_state.get("project_desc", ""),
        height=100,
        key="save_project_desc"
    )
    
    # 选择保存内容
    st.markdown("**选择保存内容**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        save_data = st.checkbox("📊 数据集", value=True, key="save_data")
        save_plots = st.checkbox("📈 绘图历史", value=True, key="save_plots")
        save_chat = st.checkbox("💬 对话历史", value=True, key="save_chat")
    
    with col2:
        save_graph = st.checkbox("🧠 逻辑图", value=True, key="save_graph")
        save_config = st.checkbox("⚙️ 配置信息", value=True, key="save_config")
    
    # 显示将保存的内容摘要
    st.markdown("---")
    st.markdown("**保存内容预览**")
    
    summary_items = []
    if save_data and st.session_state.df is not None:
        shape = st.session_state.df.shape
        summary_items.append(f"✅ 数据集: {shape[0]} 行 × {shape[1]} 列")
    elif save_data:
        summary_items.append("⚠️ 数据集: 无数据")
    
    if save_plots and st.session_state.plot_history:
        summary_items.append(f"✅ 绘图历史: {len(st.session_state.plot_history)} 个图表")
    elif save_plots:
        summary_items.append("⚠️ 绘图历史: 无记录")
    
    if save_chat and st.session_state.get("chat_messages"):
        summary_items.append(f"✅ 对话历史: {len(st.session_state.chat_messages)} 条消息")
    elif save_chat:
        summary_items.append("⚠️ 对话历史: 无记录")
    
    if save_graph and st.session_state.graph_nodes:
        summary_items.append(f"✅ 逻辑图: {len(st.session_state.graph_nodes)} 个节点")
    elif save_graph:
        summary_items.append("⚠️ 逻辑图: 无内容")
    
    for item in summary_items:
        st.write(item)
    
    # 保存按钮
    if st.button("💾 生成项目文件", type="primary", use_container_width=True):
        project_data = _create_project_data(
            project_name, project_desc,
            save_data, save_plots, save_chat, save_graph, save_config
        )
        
        if project_data:
            # 转换为 JSON
            project_json = json.dumps(project_data, ensure_ascii=False, indent=2, default=str)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sciplot_project_{timestamp}.json"
            
            st.download_button(
                "⬇️ 下载项目文件",
                project_json,
                filename,
                "application/json",
                use_container_width=True
            )
            
            st.success(f"✅ 项目文件已生成！文件名: {filename}")
        else:
            st.error("❌ 没有可保存的内容")


def _render_load_project():
    """渲染加载项目界面"""
    st.markdown("#### 加载已保存的项目")
    
    uploaded_file = st.file_uploader(
        "选择项目文件",
        type=["json"],
        help="上传之前保存的 .json 项目文件",
        key="load_project_file"
    )
    
    if uploaded_file is not None:
        try:
            project_data = json.load(uploaded_file)
            
            # 显示项目信息
            st.markdown("---")
            st.markdown("**项目信息**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"📁 **项目名称**: {project_data.get('name', '未知')}")
                st.write(f"📅 **保存时间**: {project_data.get('saved_at', '未知')}")
            with col2:
                st.write(f"📝 **描述**: {project_data.get('description', '无')}")
                st.write(f"📊 **版本**: {project_data.get('version', '1.0')}")
            
            # 显示包含的内容
            st.markdown("**包含内容**")
            contents = project_data.get('contents', {})
            
            content_items = []
            if contents.get('data'):
                content_items.append("✅ 数据集")
            if contents.get('plot_history'):
                content_items.append(f"✅ 绘图历史 ({len(contents['plot_history'])} 个)")
            if contents.get('chat_messages'):
                content_items.append(f"✅ 对话历史 ({len(contents['chat_messages'])} 条)")
            if contents.get('graph'):
                content_items.append("✅ 逻辑图")
            if contents.get('config'):
                content_items.append("✅ 配置信息")
            
            for item in content_items:
                st.write(item)
            
            # 选择加载内容
            st.markdown("---")
            st.markdown("**选择要加载的内容**")
            
            load_options = {}
            if contents.get('data'):
                load_options['data'] = st.checkbox("加载数据集", value=True, key="load_data")
            if contents.get('plot_history'):
                load_options['plots'] = st.checkbox("加载绘图历史", value=True, key="load_plots")
            if contents.get('chat_messages'):
                load_options['chat'] = st.checkbox("加载对话历史", value=True, key="load_chat")
            if contents.get('graph'):
                load_options['graph'] = st.checkbox("加载逻辑图", value=True, key="load_graph")
            
            # 加载按钮
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📂 加载项目", type="primary", use_container_width=True):
                    _load_project_data(project_data, load_options)
                    st.success("✅ 项目加载成功！")
                    st.rerun()
            
            with col2:
                if st.button("🔄 合并到当前", use_container_width=True):
                    _merge_project_data(project_data, load_options)
                    st.success("✅ 项目合并成功！")
                    st.rerun()
            
        except json.JSONDecodeError:
            st.error("❌ 无效的项目文件格式")
        except Exception as e:
            st.error(f"❌ 加载失败: {str(e)}")


def _render_export_report():
    """渲染导出报告界面"""
    st.markdown("#### 导出分析报告")
    
    if st.session_state.df is None:
        st.warning("⚠️ 请先加载数据")
        return
    
    # 报告设置
    report_title = st.text_input("报告标题", value="数据分析报告", key="report_title")
    report_author = st.text_input("作者", value="", key="report_author")
    
    st.markdown("**选择报告内容**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_summary = st.checkbox("📊 数据概览", value=True, key="report_summary")
        include_stats = st.checkbox("📈 描述统计", value=True, key="report_stats")
        include_plots = st.checkbox("🎨 生成的图表", value=True, key="report_plots")
    
    with col2:
        include_corr = st.checkbox("🔗 相关性分析", value=True, key="report_corr")
        include_missing = st.checkbox("🔍 缺失值分析", value=True, key="report_missing")
        include_code = st.checkbox("💻 代码记录", value=False, key="report_code")
    
    # 生成报告
    if st.button("📄 生成 Markdown 报告", type="primary", use_container_width=True):
        report = _generate_markdown_report(
            report_title, report_author,
            include_summary, include_stats, include_plots,
            include_corr, include_missing, include_code
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_report_{timestamp}.md"
        
        st.download_button(
            "⬇️ 下载报告",
            report,
            filename,
            "text/markdown",
            use_container_width=True
        )
        
        # 预览报告
        with st.expander("📖 预览报告", expanded=True):
            st.markdown(report)


def _create_project_data(
    name: str, description: str,
    save_data: bool, save_plots: bool, save_chat: bool,
    save_graph: bool, save_config: bool
) -> Optional[Dict[str, Any]]:
    """创建项目数据"""
    
    project_data = {
        "name": name,
        "description": description,
        "version": "1.0",
        "saved_at": datetime.now().isoformat(),
        "contents": {}
    }
    
    # 保存数据集
    if save_data and st.session_state.df is not None:
        project_data["contents"]["data"] = {
            "csv": st.session_state.df.to_csv(index=False),
            "metadata": st.session_state.metadata
        }
    
    # 保存绘图历史
    if save_plots and st.session_state.plot_history:
        project_data["contents"]["plot_history"] = st.session_state.plot_history
    
    # 保存对话历史
    if save_chat and st.session_state.get("chat_messages"):
        project_data["contents"]["chat_messages"] = st.session_state.chat_messages
    
    # 保存逻辑图
    if save_graph and st.session_state.graph_nodes:
        # 序列化节点和边
        nodes_data = []
        for node in st.session_state.graph_nodes:
            nodes_data.append({
                "id": node.id,
                "pos": node.position,
                "data": node.data,
                "style": node.style
            })
        
        edges_data = []
        for edge in st.session_state.graph_edges:
            edges_data.append({
                "id": edge.id,
                "source": edge.source,
                "target": edge.target,
                "label": edge.label
            })
        
        project_data["contents"]["graph"] = {
            "nodes": nodes_data,
            "edges": edges_data,
            "node_counter": st.session_state.node_counter
        }
    
    # 保存配置
    if save_config:
        project_data["contents"]["config"] = {
            "llm_base_url": st.session_state.get("llm_base_url", ""),
            "llm_model": st.session_state.get("llm_model", "")
            # 注意：不保存 API Key
        }
    
    # 检查是否有内容
    if not project_data["contents"]:
        return None
    
    return project_data


def _load_project_data(project_data: Dict[str, Any], load_options: Dict[str, bool]):
    """加载项目数据（覆盖当前）"""
    contents = project_data.get("contents", {})
    
    # 加载数据集
    if load_options.get('data') and contents.get('data'):
        csv_data = contents['data']['csv']
        st.session_state.df = pd.read_csv(io.StringIO(csv_data))
        st.session_state.metadata = contents['data'].get('metadata')
    
    # 加载绘图历史
    if load_options.get('plots') and contents.get('plot_history'):
        st.session_state.plot_history = contents['plot_history']
    
    # 加载对话历史
    if load_options.get('chat') and contents.get('chat_messages'):
        st.session_state.chat_messages = contents['chat_messages']
    
    # 加载逻辑图
    if load_options.get('graph') and contents.get('graph'):
        _load_graph_data(contents['graph'])
    
    # 保存项目名称
    st.session_state.project_name = project_data.get('name', '未命名项目')
    st.session_state.project_desc = project_data.get('description', '')


def _merge_project_data(project_data: Dict[str, Any], load_options: Dict[str, bool]):
    """合并项目数据（追加到当前）"""
    contents = project_data.get("contents", {})
    
    # 合并绘图历史
    if load_options.get('plots') and contents.get('plot_history'):
        existing = st.session_state.plot_history or []
        st.session_state.plot_history = existing + contents['plot_history']
    
    # 合并对话历史
    if load_options.get('chat') and contents.get('chat_messages'):
        existing = st.session_state.get('chat_messages', [])
        st.session_state.chat_messages = existing + contents['chat_messages']


def _load_graph_data(graph_data: Dict[str, Any]):
    """加载逻辑图数据"""
    from streamlit_flow import StreamlitFlowNode, StreamlitFlowEdge
    
    # 加载节点
    nodes = []
    for node_data in graph_data.get('nodes', []):
        node = StreamlitFlowNode(
            id=node_data['id'],
            pos=tuple(node_data['pos'].values()) if isinstance(node_data['pos'], dict) else node_data['pos'],
            data=node_data['data'],
            node_type="default",
            draggable=True,
            style=node_data.get('style', {})
        )
        nodes.append(node)
    
    # 加载边
    edges = []
    for edge_data in graph_data.get('edges', []):
        edge = StreamlitFlowEdge(
            id=edge_data['id'],
            source=edge_data['source'],
            target=edge_data['target'],
            label=edge_data.get('label', ''),
            animated=True
        )
        edges.append(edge)
    
    st.session_state.graph_nodes = nodes
    st.session_state.graph_edges = edges
    st.session_state.node_counter = graph_data.get('node_counter', len(nodes))
    st.session_state.graph_version += 1
    st.session_state.flow_state = None


def _generate_markdown_report(
    title: str, author: str,
    include_summary: bool, include_stats: bool, include_plots: bool,
    include_corr: bool, include_missing: bool, include_code: bool
) -> str:
    """生成 Markdown 格式的分析报告"""
    
    df = st.session_state.df
    metadata = st.session_state.metadata
    
    report = []
    
    # 标题
    report.append(f"# {title}\n")
    if author:
        report.append(f"**作者**: {author}\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n")
    
    # 数据概览
    if include_summary:
        report.append("## 📊 数据概览\n")
        report.append(f"- **数据形状**: {df.shape[0]} 行 × {df.shape[1]} 列\n")
        report.append(f"- **列名**: {', '.join(df.columns.tolist())}\n")
        report.append("\n### 数据类型\n")
        report.append("| 列名 | 数据类型 |\n|------|----------|\n")
        for col, dtype in df.dtypes.items():
            report.append(f"| {col} | {dtype} |\n")
        report.append("\n### 数据预览（前5行）\n")
        report.append(df.head().to_markdown())
        report.append("\n\n")
    
    # 描述统计
    if include_stats:
        report.append("## 📈 描述统计\n")
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            desc = numeric_df.describe()
            report.append(desc.to_markdown())
        else:
            report.append("*无数值型数据*\n")
        report.append("\n\n")
    
    # 缺失值分析
    if include_missing:
        report.append("## 🔍 缺失值分析\n")
        missing = df.isnull().sum()
        missing_df = pd.DataFrame({
            '缺失数量': missing,
            '缺失比例(%)': (missing / len(df) * 100).round(2)
        })
        missing_df = missing_df[missing_df['缺失数量'] > 0]
        if len(missing_df) > 0:
            report.append(missing_df.to_markdown())
        else:
            report.append("✅ 数据完整，无缺失值\n")
        report.append("\n\n")
    
    # 相关性分析
    if include_corr:
        report.append("## 🔗 相关性分析\n")
        numeric_df = df.select_dtypes(include=['number'])
        if numeric_df.shape[1] >= 2:
            corr = numeric_df.corr()
            report.append(corr.round(3).to_markdown())
        else:
            report.append("*数值列不足，无法计算相关性*\n")
        report.append("\n\n")
    
    # 绘图历史
    if include_plots and st.session_state.plot_history:
        report.append("## 🎨 生成的图表\n")
        for i, plot in enumerate(st.session_state.plot_history, 1):
            report.append(f"### 图表 {i}\n")
            report.append(f"**提示词**: {plot.get('prompt', '无')}\n")
            report.append(f"**风格**: {plot.get('style', '默认')}\n")
            if include_code:
                report.append(f"\n```python\n{plot.get('code', '')}\n```\n")
            report.append("\n")
    
    # 代码记录
    if include_code and st.session_state.get('last_generated_code'):
        report.append("## 💻 最后生成的代码\n")
        report.append(f"```python\n{st.session_state.last_generated_code}\n```\n")
    
    return "\n".join(report)