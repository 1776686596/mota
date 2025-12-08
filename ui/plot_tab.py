"""绘图标签页 UI 组件

处理数据绘图相关的所有 UI 交互
"""

import streamlit as st
import io
from typing import Optional
from core.data_loader import load_data, extract_metadata
from core.sandbox import execute_plot_code
from core.llm_service import LLMService
from .data_explorer import render_data_explorer
from .styles import render_loading
from .dashboard import render_dashboard, add_dashboard_styles


def _render_metric_card(label: str, value: str, delta: str = None, delta_type: str = "neutral"):
    """渲染自定义指标卡片"""
    delta_html = ""
    if delta:
        delta_class = f"delta-{delta_type}"
        delta_html = f'<span class="metric-delta {delta_class}">{delta}</span>'
    
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_plot_tab():
    """渲染数据绘图标签页"""
    # 移除默认 header，使用更精致的布局
    # st.header("智能数据绘图")
    
    # 文件上传区域
    st.markdown("### 📂 数据导入")
    st.markdown("上传您的 CSV 或 Excel 文件，开始探索数据洞察。")
    _render_file_upload()
    
    # 如果已加载数据，显示绘图界面
    if st.session_state.df is not None:
        st.divider()
        _render_ai_recommendations()
        st.divider()
        _render_plot_generation()


def _render_file_upload():
    """渲染文件上传界面"""
    with st.container():
        uploaded_file = st.file_uploader(
            "拖拽或点击上传数据文件",
            type=["csv", "xlsx", "xls"],
            help="支持 .csv, .xlsx, .xls 格式",
            key="data_file_uploader"
        )
        
        # 只有当文件发生变化时才重新加载数据
        if uploaded_file is not None:
            # 检查是否是新文件（通过文件名和大小判断）
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            
            if st.session_state.get('_last_uploaded_file_key') != file_key:
                try:
                    st.session_state.df = load_data(uploaded_file)
                    st.session_state.metadata = extract_metadata(st.session_state.df)
                    st.session_state._last_uploaded_file_key = file_key
                    st.success(f"✅ 成功加载文件: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ 文件加载失败: {e}")
                    return
            
            # 显示数据概览（只有当数据已加载时）
            if st.session_state.df is not None:
                # 添加仪表盘样式
                add_dashboard_styles()
                
                # 渲染交互式仪表盘
                render_dashboard(st.session_state.df, st.session_state.metadata)
                
                st.divider()
                
                with st.expander("👀 预览数据前 10 行", expanded=False):
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)
                
                # 数据探索功能
                render_data_explorer(st.session_state.df)
                
                # AI 推荐按钮
                _render_ai_recommend_button()


def _get_llm_service():
    """获取 LLM 服务实例，优先使用用户配置，否则使用后台配置
    
    Returns:
        LLMService or None: LLM 服务实例，如果没有可用配置则返回 None
    """
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
    """检查是否有可用的 LLM 配置（用户配置或后台配置）"""
    config_manager = st.session_state.config_manager
    return bool(st.session_state.get("llm_api_key")) or config_manager.has_backend_config()


def _render_ai_recommend_button():
    """渲染 AI 推荐按钮"""
    if _has_llm_available():
        if st.button("🤖 获取 AI 图表推荐", type="secondary"):
            with st.spinner("AI 正在分析数据并生成推荐..."):
                try:
                    llm = _get_llm_service()
                    if llm is None:
                        st.error("❌ 无法获取 LLM 服务")
                        return
                    st.session_state.plot_recommendations = llm.recommend_plots(
                        st.session_state.metadata
                    )
                    st.success(f"✅ 已生成 {len(st.session_state.plot_recommendations)} 个图表推荐")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 推荐失败: {str(e)}")


def _render_ai_recommendations():
    """渲染 AI 推荐的图表"""
    if st.session_state.plot_recommendations:
        st.markdown("### 💡 AI 智能推荐")
        st.info("根据您的数据特征，AI 为您生成了以下可视化建议。您可以直接应用，或作为灵感来源。")
        
        # 使用卡片式布局展示推荐
        cols = st.columns(min(len(st.session_state.plot_recommendations), 3))
        for idx, rec in enumerate(st.session_state.plot_recommendations):
            with cols[idx % 3]:
                with st.container(border=True):
                    # 图表类型标签
                    chart_type = rec.get('chart_type', 'default')
                    type_emoji = {
                        'scatter': '📊',
                        'line': '📈',
                        'bar': '📊',
                        'box': '📦',
                        'heatmap': '🔥',
                        'histogram': '📊',
                        'grouped_bar': '📊'
                    }.get(chart_type, '📊')
                    
                    st.markdown(f"### {type_emoji} {rec.get('title', '推荐图表')}")
                    st.caption(rec.get('description', ''))
                    
                    # 显示设计要点（可折叠）
                    if 'design_tips' in rec and rec['design_tips']:
                        with st.expander("🎨 设计要点", expanded=False):
                            for tip in rec['design_tips']:
                                st.markdown(f"- {tip}")
                    
                    # 生成按钮
                    if st.button(
                        "🎨 应用此方案",
                        key=f"rec_{idx}",
                        use_container_width=True,
                        type="primary"
                    ):
                        st.session_state.selected_prompt = rec.get('prompt', '')
                        st.session_state.auto_generate = True
                        st.rerun()
        st.divider()



def _render_plot_generation():
    """渲染图表生成界面"""
    with st.container():
        st.markdown("### 🎨 自定义图表生成")
        st.markdown("用自然语言描述您想要的图表，AI 将为您生成 Python 代码并绘制。")
        
        user_prompt = st.text_area(
            "描述您的绘图需求",
            value=st.session_state.get('selected_prompt', ''),
            placeholder="例如：请画出 'age' 和 'income' 的散点图，用 'gender' 区分颜色，并添加线性回归趋势线。",
            height=120,
            max_chars=1000,
            key="user_prompt_input",
            help="提示：描述越具体，生成的图表越准确。包含列名、图表类型、颜色偏好等信息。"
        )
        
        # 清除选中的推荐
        if 'selected_prompt' in st.session_state and user_prompt != st.session_state.selected_prompt:
            del st.session_state.selected_prompt
        
        # 输入验证
        prompt_valid = True
        if user_prompt:
            if len(user_prompt.strip()) < 5:
                st.warning("⚠️ 图表描述至少需要 5 个字符")
                prompt_valid = False
        
        # 样式和格式选项
        col_style, col_format = st.columns(2)
        with col_style:
            style = st.selectbox("图表风格", ["Default", "Nature", "Science", "Cell", "PNAS"])
        with col_format:
            export_format = st.selectbox("导出格式", ["png", "pdf", "svg", "jpg"])
        
        # 生成和历史按钮
        col_gen, col_history = st.columns([1, 1])
        with col_gen:
            generate_btn = st.button("🎨 生成图表", type="primary", use_container_width=True)
        with col_history:
            if st.session_state.plot_history:
                show_history = st.button("📜 查看历史", use_container_width=True)
            else:
                st.button("📜 查看历史", disabled=True, use_container_width=True)
                show_history = False
        
        # 自动生成或手动点击生成
        should_generate = generate_btn or st.session_state.get('auto_generate', False)
        
        if should_generate:
            _handle_plot_generation(user_prompt, prompt_valid, style, export_format)
        
        # 显示历史记录
        if 'show_history' in locals() and show_history and st.session_state.plot_history:
            _render_history()


def _handle_plot_generation(user_prompt: str, prompt_valid: bool, style: str, export_format: str):
    """处理图表生成逻辑"""
    # 清除自动生成标志
    if 'auto_generate' in st.session_state:
        del st.session_state.auto_generate
    
    if user_prompt and prompt_valid and _has_llm_available():
        # 显示终端加载动画
        loading_placeholder = st.empty()
        
        try:
            # 步骤 1: 初始化 LLM
            with loading_placeholder.container():
                render_loading("Initializing AI...")
            
            llm = _get_llm_service()
            if llm is None:
                loading_placeholder.empty()
                st.error("❌ 无法获取 LLM 服务")
                return
            
            # 步骤 2: 生成代码
            with loading_placeholder.container():
                render_loading("Generating code...")
            
            code = llm.generate_plot_code(st.session_state.metadata, user_prompt)
            
            # 步骤 3: 执行代码
            with loading_placeholder.container():
                render_loading("Rendering plot...")
            
            fig, final_code = execute_plot_code(
                code, st.session_state.df, style, max_retries=3, llm_service=llm
            )
            
            # 清除加载动画
            loading_placeholder.empty()
            
            # 保存到历史
            st.session_state.plot_history.append({
                "prompt": user_prompt,
                "code": final_code,
                "style": style
            })
            st.session_state.last_generated_code = final_code
            
            # 显示图表
            st.pyplot(fig, clear_figure=True)
            
            # 显示代码
            _render_code_display(final_code)
            
            # 下载按钮
            _render_download_buttons(fig, final_code, export_format)
            
        except Exception as e:
            loading_placeholder.empty()
            st.error(f"❌ 生成失败: {str(e)}")
            with st.expander("🔍 查看详细错误信息"):
                st.code(str(e))
    elif not _has_llm_available():
        st.warning("⚠️ 请先在侧边栏配置 API Key，或使用平台提供的免费服务")
    else:
        st.warning("⚠️ 请输入图表描述")


def _render_code_display(code: str):
    """渲染代码显示"""
    with st.expander("📝 查看生成的代码", expanded=False):
        st.code(code, language="python")
        if st.button("📋 复制代码"):
            st.code(code, language="python")
            st.success("代码已显示，可手动复制")


def _render_download_buttons(fig, code: str, export_format: str):
    """渲染下载按钮"""
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        buf = io.BytesIO()
        fig.savefig(buf, format=export_format, dpi=300, bbox_inches="tight")
        st.download_button(
            f"⬇️ 下载图片 ({export_format.upper()})",
            buf.getvalue(),
            f"plot.{export_format}",
            f"image/{export_format}",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            "⬇️ 下载代码 (Python)",
            code,
            "plot_code.py",
            "text/plain",
            use_container_width=True
        )


def _render_history():
    """渲染历史记录"""
    st.divider()
    st.subheader("📜 生成历史")
    for idx, record in enumerate(reversed(st.session_state.plot_history)):
        with st.expander(f"记录 {len(st.session_state.plot_history) - idx}: {record['prompt'][:50]}..."):
            st.text(f"提示词: {record['prompt']}")
            st.text(f"风格: {record['style']}")
            st.code(record['code'], language="python")