"""AI 对话标签页 UI 组件

提供与 AI 进行自然语言对话的界面
"""

import streamlit as st
from core.llm_service import LLMService


def render_chat_tab():
    """渲染 AI 对话标签页"""
    st.markdown("### 💬 AI 智能助手")
    st.markdown("与 AI 进行自然语言对话，获取数据分析建议、代码帮助或科研问题解答。")
    
    # 检查 LLM 配置
    if not _has_llm_available():
        st.warning("⚠️ 请先在侧边栏配置 API Key，或使用平台提供的免费服务")
        return
    
    # 初始化对话历史
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # 显示对话历史
    _render_chat_history()
    
    # 用户输入区域
    _render_chat_input()
    
    # 快捷操作按钮
    _render_quick_actions()


def _has_llm_available():
    """检查是否有可用的 LLM 配置"""
    config_manager = st.session_state.config_manager
    return bool(st.session_state.get("llm_api_key")) or config_manager.has_backend_config()


def _get_llm_service():
    """获取 LLM 服务实例"""
    config_manager = st.session_state.config_manager
    effective_config = config_manager.get_effective_llm_config()
    
    if effective_config.get("api_key"):
        return LLMService(
            base_url=effective_config.get("base_url"),
            api_key=effective_config.get("api_key"),
            model=effective_config.get("model")
        )
    return None


def _render_chat_history():
    """渲染对话历史"""
    # 创建一个容器用于显示消息
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(content)
            elif role == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(content)


def _render_chat_input():
    """渲染用户输入区域"""
    # 使用 chat_input 组件
    user_input = st.chat_input(
        placeholder="输入您的问题，例如：如何分析数据相关性？",
        key="chat_input"
    )
    
    if user_input:
        _handle_user_message(user_input)


def _handle_user_message(user_input: str):
    """处理用户消息"""
    # 添加用户消息到历史
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input
    })
    
    # 显示用户消息
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # 生成 AI 回复
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("AI 正在思考..."):
            response = _generate_ai_response(user_input)
            if response:
                st.markdown(response)
                # 添加 AI 回复到历史
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response
                })
            else:
                error_msg = "抱歉，生成回复时出现错误，请稍后重试。"
                st.error(error_msg)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": error_msg
                })


def _generate_ai_response(user_input: str) -> str:
    """生成 AI 回复
    
    Args:
        user_input: 用户输入的消息
        
    Returns:
        AI 生成的回复文本
    """
    try:
        llm = _get_llm_service()
        if llm is None:
            return None
        
        # 构建系统提示词
        system_prompt = _build_system_prompt()
        
        # 构建消息列表（包含历史上下文）
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息（最多保留最近 10 轮对话）
        history_messages = st.session_state.chat_messages[-20:]  # 最多 20 条消息（10 轮）
        for msg in history_messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_input})
        
        # 调用 LLM
        response = llm.chat(messages, temperature=0.7)
        return response
        
    except Exception as e:
        st.error(f"❌ 生成回复失败: {str(e)}")
        return None


def _build_system_prompt() -> str:
    """构建系统提示词"""
    base_prompt = """你是 SciPlot-Copilot 的 AI 助手，一个专业的科研数据分析和可视化助手。

你的主要能力包括：
1. **数据分析建议**：帮助用户理解数据特征、选择合适的分析方法
2. **可视化指导**：推荐合适的图表类型、配色方案、布局设计
3. **代码帮助**：解释 Python/matplotlib/seaborn 代码，提供代码示例
4. **科研写作**：帮助撰写图表说明、方法描述等科研文本
5. **统计知识**：解答统计学相关问题，推荐合适的统计检验方法

回复要求：
- 使用简洁清晰的中文回答
- 提供具体可操作的建议
- 必要时给出代码示例（使用 markdown 代码块）
- 对于复杂问题，分步骤解答
- 保持专业但友好的语气"""
    
    # 如果有已加载的数据，添加数据上下文
    if st.session_state.get("df") is not None and st.session_state.get("metadata"):
        metadata = st.session_state.metadata
        data_context = f"""

当前用户已加载数据集，数据信息如下：
- 数据形状：{metadata.get('shape', (0, 0))[0]} 行 × {metadata.get('shape', (0, 0))[1]} 列
- 列名和类型：
"""
        for col, dtype in metadata.get('dtypes', {}).items():
            data_context += f"  - '{col}' ({dtype})\n"
        
        data_context += f"""
- 数据示例（前几行）：
{metadata.get('sample', '无')}

请根据用户的数据特征提供针对性的建议。"""
        
        base_prompt += data_context
    
    return base_prompt


def _render_quick_actions():
    """渲染快捷操作按钮"""
    st.divider()
    
    # 使用炫酷的文字描边按钮样式
    st.markdown("""
        <div style="display: flex; gap: 1rem; justify-content: center; margin: 2rem 0; flex-wrap: wrap;">
            <button class="stroke-button" onclick="document.querySelector('[data-testid=\\"stButton\\"] button').click()">
                <span class="hover-text">Clear</span>
                Clear
            </button>
            <button class="stroke-button" onclick="alert('请使用下方按钮点击')">
                <span class="hover-text">Analyze</span>
                Analyze
            </button>
            <button class="stroke-button" onclick="alert('请使用下方按钮点击')">
                <span class="hover-text">Charts</span>
                Charts
            </button>
        </div>
    """, unsafe_allow_html=True)
    
    # 实际功能按钮（隐藏样式）
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ 清空对话", use_container_width=True, key="clear_chat_btn"):
            st.session_state.chat_messages = []
            st.rerun()
    
    with col2:
        # 快捷问题按钮
        if st.button("💡 数据分析建议", use_container_width=True, key="analyze_btn"):
            if st.session_state.get("df") is not None:
                _handle_user_message("请根据我当前加载的数据，给出数据分析和可视化的建议。")
            else:
                st.warning("请先上传数据文件")
    
    with col3:
        if st.button("📊 图表推荐", use_container_width=True, key="chart_btn"):
            if st.session_state.get("df") is not None:
                _handle_user_message("请推荐适合我当前数据的图表类型，并说明原因。")
            else:
                st.warning("请先上传数据文件")
    
    # 更多快捷问题
    with st.expander("💬 更多快捷问题", expanded=False):
        quick_questions = [
            "如何选择合适的统计检验方法？",
            "散点图和折线图分别适合什么场景？",
            "如何让图表更符合期刊发表要求？",
            "如何处理数据中的缺失值？",
            "如何进行数据标准化处理？"
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{question[:10]}", use_container_width=True):
                _handle_user_message(question)