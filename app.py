"""SciPlot-Copilot - AI 驱动的科研可视化与逻辑梳理平台

主入口文件，负责页面配置和模块调用
"""

# 必须在导入任何使用 matplotlib 的模块之前设置后端
import matplotlib
matplotlib.use('Agg')

import streamlit as st
from utils.session import initialize_session_state
from ui import (
    render_plot_tab, render_logic_graph_tab, render_chat_tab, render_sidebar,
    apply_custom_styles, render_loading, add_dashboard_styles,
    render_statistics_tab, render_project_manager, render_data_preprocessing
)

# 页面配置
st.set_page_config(
    page_title="SciPlot-Copilot",
    page_icon="📊",
    layout="wide"
)

# 应用自定义样式
apply_custom_styles()
add_dashboard_styles()

# 初始化 Session State
initialize_session_state()

# 页面标题 - Linear/Vercel 风格 Hero 区域
st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">
            <span class="dot"></span>
            <span>AI-Powered Research Platform</span>
        </div>
        <h1 class="hero-title">
            SciPlot <span class="gradient-text">Copilot</span>
            <span class="title-loader">
                <svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
                    <circle class="dash" cx="60" cy="60" r="54" pathLength="360" fill="none"
                            stroke="url(#gradient)" stroke-width="8" stroke-linecap="round"/>
                    <circle class="spin" cx="60" cy="60" r="54" pathLength="360" fill="none"
                            stroke="url(#gradient)" stroke-width="8" stroke-linecap="round"/>
                    <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#5e6ad2;stop-opacity:1" />
                            <stop offset="50%" style="stop-color:#8b5cf6;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#d946ef;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                </svg>
            </span>
        </h1>
        <p class="hero-subtitle">
            融合大语言模型智慧，一键生成 Nature 级科研图表，智能梳理复杂实验逻辑。让数据说话，让逻辑可见。
        </p>
        <div style="margin: 2rem 0;">
            <button class="fancy-button" onclick="window.scrollTo({top: 400, behavior: 'smooth'})">
                <div class="dots_border"></div>
                <svg class="sparkle" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path class="path" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.187 8.096L15 5.25L15.813 8.096C16.0231 8.83114 16.4171 9.50062 16.9577 10.0413C17.4984 10.5819 18.1679 10.9759 18.903 11.186L21.75 12L18.904 12.813C18.1689 13.0231 17.4994 13.4171 16.9587 13.9577C16.4181 14.4984 16.0241 15.1679 15.814 15.903L15 18.75L14.187 15.904C13.9769 15.1689 13.5829 14.4994 13.0423 13.9587C12.5016 13.4181 11.8321 13.0241 11.097 12.814L8.25 12L11.096 11.187C11.8311 10.9769 12.5006 10.5829 13.0413 10.0423C13.5819 9.50162 13.9759 8.83214 14.186 8.097L14.187 8.096Z"></path>
                    <path class="path" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 14.25L5.741 15.285C5.59267 15.8785 5.28579 16.4206 4.85319 16.8532C4.42059 17.2858 3.87853 17.5927 3.285 17.741L2.25 18L3.285 18.259C3.87853 18.4073 4.42059 18.7142 4.85319 19.1468C5.28579 19.5794 5.59267 20.1215 5.741 20.715L6 21.75L6.259 20.715C6.40725 20.1216 6.71398 19.5796 7.14639 19.147C7.5788 18.7144 8.12065 18.4075 8.714 18.259L9.75 18L8.714 17.741C8.12065 17.5925 7.5788 17.2856 7.14639 16.853C6.71398 16.4204 6.40725 15.8784 6.259 15.285L6 14.25Z"></path>
                    <path class="path" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6.5 4L6.303 4.5915C6.24777 4.75718 6.15472 4.90774 6.03123 5.03123C5.90774 5.15472 5.75718 5.24777 5.5915 5.303L5 5.5L5.5915 5.697C5.75718 5.75223 5.90774 5.84528 6.03123 5.96877C6.15472 6.09226 6.24777 6.24282 6.303 6.4085L6.5 7L6.697 6.4085C6.75223 6.24282 6.84528 6.09226 6.96877 5.96877C7.09226 5.84528 7.24282 5.75223 7.4085 5.697L8 5.5L7.4085 5.303C7.24282 5.24777 7.09226 5.15472 6.96877 5.03123C6.84528 4.90774 6.75223 4.75718 6.697 4.5915L6.5 4Z"></path>
                </svg>
                <span class="text_button">开始探索</span>
            </button>
        </div>
        <div class="hero-features">
            <div class="hero-feature">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0L10 6H16L11 9.5L13 16L8 12L3 16L5 9.5L0 6H6L8 0Z"/></svg>
                <span>智能绘图</span>
            </div>
            <div class="hero-feature">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0L10 6H16L11 9.5L13 16L8 12L3 16L5 9.5L0 6H6L8 0Z"/></svg>
                <span>逻辑梳理</span>
            </div>
            <div class="hero-feature">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0L10 6H16L11 9.5L13 16L8 12L3 16L5 9.5L0 6H6L8 0Z"/></svg>
                <span>AI 对话</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 六 Tab 布局，增加更多功能
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 智能绘图工作室",
    "🧠 逻辑思维导图",
    "💬 AI 对话助手",
    "🔬 统计分析",
    "🔧 数据预处理",
    "💾 项目管理"
])

with tab1:
    with st.container():
        render_plot_tab()

with tab2:
    with st.container():
        render_logic_graph_tab()

with tab3:
    with st.container():
        render_chat_tab()

with tab4:
    with st.container():
        render_statistics_tab()

with tab5:
    with st.container():
        if st.session_state.df is not None:
            render_data_preprocessing(st.session_state.df)
        else:
            st.warning("⚠️ 请先在「智能绘图工作室」中上传数据")

with tab6:
    with st.container():
        render_project_manager()

# 侧边栏
render_sidebar()
