"""侧边栏 UI 组件

提供 LLM 配置和使用说明
"""

import streamlit as st
from core.llm_service import LLMService


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # 显示当前使用的模型
        _render_current_model_info()
        
        st.markdown("## ⚙️ 设置与帮助")
        _render_llm_config()
        st.divider()
        _render_statistics()
        _render_usage_guide()


def _render_llm_config():
    """渲染 LLM 配置区域"""
    config_manager = st.session_state.config_manager
    is_using_backend = config_manager.is_using_backend_config()
    has_user_key = bool(st.session_state.get("llm_api_key"))
    
    with st.expander("🔑 模型配置 (LLM)", expanded=not (has_user_key or is_using_backend)):
        # 显示连接状态
        if has_user_key:
            st.success("✅ 使用自定义 API 配置")
        elif is_using_backend:
            st.info("🎁 使用平台提供的免费 API（可配置自己的 API 获得更好体验）")
        else:
            st.warning("👉 请配置模型 API 或使用平台免费服务")
        
        # 显示当前使用的配置来源
        if is_using_backend and not has_user_key:
            st.caption("💡 平台已为您配置免费 API，可直接使用。如需使用自己的 API，请在下方配置。")
        
        base_url = st.text_input(
            "API Base URL",
            value=st.session_state.get("llm_base_url", "https://api.openai.com/v1"),
            placeholder="https://api.openai.com/v1",
            help="支持 OpenAI 兼容协议的 API 地址（留空使用平台默认）"
        )
        
        # URL 格式验证
        if base_url and not (base_url.startswith("http://") or base_url.startswith("https://")):
            st.error("❌ API Base URL 必须以 http:// 或 https:// 开头")
        
        api_key = st.text_input(
            "API Key",
            type="password",
            value=st.session_state.get("llm_api_key", ""),
            placeholder="留空使用平台免费 API" if is_using_backend else "请输入 API Key",
            help="你的 API 密钥（留空使用平台默认）"
        )
        
        # API Key 验证（仅当用户输入时验证）
        if api_key and len(api_key.strip()) < 10:
            st.error("❌ API Key 格式不正确（至少 10 个字符）")
        
        # 获取模型按钮
        if st.button("🔍 获取可用模型", use_container_width=True, help="查询 API 支持的所有模型", key="fetch_models_btn"):
            _fetch_available_models(base_url, api_key)
        
        # 显示模型选择
        if 'available_models' in st.session_state and st.session_state.available_models:
            model = st.selectbox(
                "选择模型",
                options=st.session_state.available_models,
                index=st.session_state.available_models.index(st.session_state.get("llm_model", "gpt-3.5-turbo"))
                      if st.session_state.get("llm_model") in st.session_state.available_models else 0,
                help="从可用模型中选择"
            )
        else:
            model = st.text_input(
                "Model",
                value=st.session_state.get("llm_model", "gpt-3.5-turbo"),
                help="模型名称\n例如：\n- OpenAI: gpt-4, gpt-3.5-turbo\n- Qwen: qwen-turbo, qwen-plus\n- DeepSeek: deepseek-chat\n- Google: gemini-2.5-pro"
            )
        
        # Model 验证
        if model and len(model.strip()) < 3:
            st.error("❌ 模型名称格式不正确")
        
        # 保存配置和测试连接按钮
        col_save, col_test = st.columns(2)
        with col_save:
            if st.button("💾 保存配置", use_container_width=True, type="primary", key="save_config_btn"):
                if st.session_state.config_manager.update_llm_config(
                    base_url=base_url,
                    api_key=api_key,
                    model=model
                ):
                    # 更新 session_state
                    st.session_state.llm_base_url = base_url
                    st.session_state.llm_api_key = api_key
                    st.session_state.llm_model = model
                    st.success("✅ 配置已保存")
                else:
                    st.error("❌ 保存失败")
        
        with col_test:
            if st.button("🔌 测试连接", use_container_width=True, type="secondary", key="test_connection_btn"):
                _test_llm_connection(base_url, api_key, model)


def _fetch_available_models(base_url: str, api_key: str):
    """获取可用模型列表
    
    Args:
        base_url: API 基础 URL
        api_key: API 密钥
    """
    if not api_key or len(api_key.strip()) < 10:
        st.error("❌ 请先输入有效的 API Key")
    elif not base_url or not (base_url.startswith("http://") or base_url.startswith("https://")):
        st.error("❌ 请先输入有效的 API Base URL")
    else:
        with st.spinner("正在获取模型列表..."):
            try:
                llm = LLMService(
                    base_url=base_url,
                    api_key=api_key,
                    model="dummy"  # 临时模型名，仅用于初始化
                )
                success, models, message = llm.list_models()
                
                if success:
                    st.session_state.available_models = models
                    st.success(message)
                    st.info(f"📋 可用模型：{', '.join(models[:5])}{'...' if len(models) > 5 else ''}")
                else:
                    st.warning(message)
                    # 清除之前的模型列表
                    if 'available_models' in st.session_state:
                        del st.session_state.available_models
            except Exception as e:
                st.error(f"❌ 获取失败：{str(e)}")
                if 'available_models' in st.session_state:
                    del st.session_state.available_models


def _test_llm_connection(base_url: str, api_key: str, model: str):
    """测试 LLM 连接
    
    Args:
        base_url: API 基础 URL
        api_key: API 密钥
        model: 模型名称
    """
    if not api_key or len(api_key.strip()) < 10:
        st.error("❌ 请先输入有效的 API Key")
    elif not base_url or not (base_url.startswith("http://") or base_url.startswith("https://")):
        st.error("❌ 请先输入有效的 API Base URL")
    elif not model or len(model.strip()) < 3:
        st.error("❌ 请先输入有效的模型名称")
    else:
        with st.spinner("正在测试连接..."):
            try:
                llm = LLMService(
                    base_url=base_url,
                    api_key=api_key,
                    model=model
                )
                success, message = llm.test_connection()
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"❌ 测试失败：{str(e)}")


def _render_usage_guide():
    """渲染使用说明"""
    st.divider()
    with st.expander("📖 快速入门指南", expanded=False):
        st.markdown("""
        #### 📈 智能绘图
        1. **上传数据**: 拖拽上传 CSV/Excel 文件
        2. **对话绘图**: "画出 A 和 B 的关系..."
        3. **专业风格**: 选择 Nature/Science 等期刊风格
        4. **导出**: 获取高清图片和可复现代码

        #### 🧠 逻辑导图
        1. **输入文本**: 粘贴实验步骤或文献摘要
        2. **一键生成**: AI 自动梳理流程逻辑
        3. **交互编辑**: 点击节点修改，拖拽布局
        
        ---
        **💡 小贴士**:
        - 描述越具体，效果越好
        - 遇到问题尝试刷新页面
        """)


def _render_statistics():
    """渲染统计信息"""
    if st.session_state.plot_history:
        st.divider()
        st.metric("📊 已生成图表", len(st.session_state.plot_history))


def _render_current_model_info():
    """渲染当前使用的模型信息"""
    config_manager = st.session_state.config_manager
    effective_config = config_manager.get_effective_llm_config()
    is_using_backend = config_manager.is_using_backend_config()
    
    current_model = effective_config.get("model", "")
    
    if current_model:
        # 根据配置来源显示不同的标签
        if is_using_backend:
            source_label = "系统配置"
            icon = "🌐"
        else:
            source_label = "用户配置"
            icon = "👤"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(94, 106, 210, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
            border: 1px solid rgba(94, 106, 210, 0.3);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 0.75rem; color: #a1a1a1; margin-bottom: 0.25rem;">
                {icon} 当前模型 ({source_label})
            </div>
            <div style="font-size: 1rem; font-weight: 600; color: #fafafa;">
                🤖 {current_model}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 0.75rem; color: #f59e0b; margin-bottom: 0.25rem;">
                ⚠️ 当前模型
            </div>
            <div style="font-size: 0.875rem; color: #a1a1a1;">
                未配置，请在下方设置
            </div>
        </div>
        """, unsafe_allow_html=True)