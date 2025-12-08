"""Session State 管理模块

负责初始化和管理 Streamlit Session State
"""

import streamlit as st
from core.config_manager import ConfigManager


def initialize_session_state():
    """初始化所有 Session State 变量"""
    
    # 初始化配置管理器
    if "config_manager" not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    
    # 确保 LLM 配置始终存在
    if "llm_base_url" not in st.session_state:
        llm_config = st.session_state.config_manager.get_llm_config()
        st.session_state.llm_base_url = llm_config.get("base_url", "https://api.openai.com/v1")
    
    if "llm_api_key" not in st.session_state:
        llm_config = st.session_state.config_manager.get_llm_config()
        st.session_state.llm_api_key = llm_config.get("api_key", "")
    
    if "llm_model" not in st.session_state:
        llm_config = st.session_state.config_manager.get_llm_config()
        st.session_state.llm_model = llm_config.get("model", "gpt-3.5-turbo")
    
    # 数据相关
    if "df" not in st.session_state:
        st.session_state.df = None
    if "metadata" not in st.session_state:
        st.session_state.metadata = None
    if "_last_uploaded_file_key" not in st.session_state:
        st.session_state._last_uploaded_file_key = None
    
    # 逻辑图相关
    if "graph_nodes" not in st.session_state:
        st.session_state.graph_nodes = []
    if "graph_edges" not in st.session_state:
        st.session_state.graph_edges = []
    if "node_counter" not in st.session_state:
        st.session_state.node_counter = 0
    if "flow_state" not in st.session_state:
        st.session_state.flow_state = None
    if "graph_version" not in st.session_state:
        st.session_state.graph_version = 0
    if "selected_node" not in st.session_state:
        st.session_state.selected_node = None
    if "selected_edge" not in st.session_state:
        st.session_state.selected_edge = None
    
    # 绘图相关
    if "plot_history" not in st.session_state:
        st.session_state.plot_history = []
    if "last_generated_code" not in st.session_state:
        st.session_state.last_generated_code = None
    if "plot_recommendations" not in st.session_state:
        st.session_state.plot_recommendations = []
    
    # AI 对话相关
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []