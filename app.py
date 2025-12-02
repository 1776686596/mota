"""SciPlot-Copilot - AI 驱动的科研可视化与逻辑梳理平台"""

import streamlit as st
from streamlit_flow import streamlit_flow, StreamlitFlowNode, StreamlitFlowEdge, StreamlitFlowState
from streamlit_flow.layouts import TreeLayout

st.set_page_config(page_title="SciPlot-Copilot", page_icon="📊", layout="wide")

# 初始化 session_state
if "df" not in st.session_state:
    st.session_state.df = None
if "metadata" not in st.session_state:
    st.session_state.metadata = None
if "graph_nodes" not in st.session_state:
    st.session_state.graph_nodes = []
if "graph_edges" not in st.session_state:
    st.session_state.graph_edges = []
if "node_counter" not in st.session_state:
    st.session_state.node_counter = 0
if "plot_history" not in st.session_state:
    st.session_state.plot_history = []
if "last_generated_code" not in st.session_state:
    st.session_state.last_generated_code = None

st.title("📊 SciPlot-Copilot")
st.caption("AI 驱动的科研可视化与逻辑梳理平台")

# 双 Tab 布局
tab1, tab2 = st.tabs(["📈 数据绘图", "🔗 逻辑图"])

with tab1:
    st.header("智能数据绘图")
    from core.data_loader import load_data, extract_metadata

    uploaded_file = st.file_uploader("上传数据文件", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        try:
            st.session_state.df = load_data(uploaded_file)
            st.session_state.metadata = extract_metadata(st.session_state.df)
            st.success(f"已加载数据: {st.session_state.metadata['shape'][0]} 行 × {st.session_state.metadata['shape'][1]} 列")
            st.dataframe(st.session_state.df.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"加载失败: {e}")

    if st.session_state.df is not None:
        from core.sandbox import execute_plot_code
        from core.llm_service import LLMService
        import io

        user_prompt = st.text_area(
            "描述你想要的图表",
            placeholder="例如：画出电压和电流的散点图，使用不同颜色区分批次，添加回归线",
            height=100,
            max_chars=1000
        )
        
        # 输入验证
        prompt_valid = True
        if user_prompt:
            if len(user_prompt.strip()) < 5:
                st.warning("⚠️ 图表描述至少需要 5 个字符")
                prompt_valid = False
        
        col_style, col_format = st.columns(2)
        with col_style:
            style = st.selectbox("图表风格", ["Default", "Nature", "Science", "Cell", "PNAS"])
        with col_format:
            export_format = st.selectbox("导出格式", ["png", "pdf", "svg", "jpg"])

        col_gen, col_history = st.columns([1, 1])
        with col_gen:
            generate_btn = st.button("🎨 生成图表", type="primary", use_container_width=True)
        with col_history:
            if st.session_state.plot_history:
                show_history = st.button("📜 查看历史", use_container_width=True)
            else:
                st.button("📜 查看历史", disabled=True, use_container_width=True)
                show_history = False
        
        if generate_btn:
            if user_prompt and prompt_valid and st.session_state.get("llm_api_key"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 步骤 1: 初始化 LLM
                    status_text.text("🔧 初始化 AI 服务...")
                    progress_bar.progress(10)
                    llm = LLMService(
                        base_url=st.session_state.llm_base_url,
                        api_key=st.session_state.llm_api_key,
                        model=st.session_state.llm_model
                    )
                    
                    # 步骤 2: 生成代码
                    status_text.text("🤖 AI 正在生成绘图代码...")
                    progress_bar.progress(30)
                    code = llm.generate_plot_code(st.session_state.metadata, user_prompt)
                    
                    # 步骤 3: 执行代码
                    status_text.text("⚙️ 执行代码并生成图表...")
                    progress_bar.progress(60)
                    fig, final_code = execute_plot_code(
                        code, st.session_state.df, style, max_retries=3, llm_service=llm
                    )
                    
                    # 步骤 4: 完成
                    progress_bar.progress(100)
                    status_text.text("✅ 图表生成成功！")
                    
                    # 保存到历史
                    st.session_state.plot_history.append({
                        "prompt": user_prompt,
                        "code": final_code,
                        "style": style
                    })
                    st.session_state.last_generated_code = final_code
                    
                    # 显示图表
                    st.pyplot(fig)

                    # 显示代码
                    with st.expander("📝 查看生成的代码", expanded=False):
                        st.code(final_code, language="python")
                        if st.button("📋 复制代码"):
                            st.code(final_code, language="python")
                            st.success("代码已显示，可手动复制")

                    # 下载按钮
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
                            final_code,
                            "plot_code.py",
                            "text/plain",
                            use_container_width=True
                        )
                    
                    # 清理进度条
                    progress_bar.empty()
                    status_text.empty()
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ 生成失败: {str(e)}")
                    with st.expander("🔍 查看详细错误信息"):
                        st.code(str(e))
            elif not st.session_state.get("llm_api_key"):
                st.warning("⚠️ 请先在侧边栏配置 API Key")
            else:
                st.warning("⚠️ 请输入图表描述")
        
        # 显示历史记录
        if 'show_history' in locals() and show_history and st.session_state.plot_history:
            st.divider()
            st.subheader("📜 生成历史")
            for idx, record in enumerate(reversed(st.session_state.plot_history)):
                with st.expander(f"记录 {len(st.session_state.plot_history) - idx}: {record['prompt'][:50]}..."):
                    st.text(f"提示词: {record['prompt']}")
                    st.text(f"风格: {record['style']}")
                    st.code(record['code'], language="python")

with tab2:
    st.header("交互式逻辑图")
    from core.logic_graph import parse_llm_json, create_node
    from core.llm_service import LLMService

    col1, col2 = st.columns([2, 1])
    with col1:
        text_input = st.text_area(
            "输入实验流程描述",
            placeholder="例如：首先进行样品制备，然后进行 XRD 表征，最后进行 SEM 观察...",
            height=120,
            max_chars=2000
        )
        
        # 输入验证
        text_valid = True
        if text_input:
            if len(text_input.strip()) < 10:
                st.warning("⚠️ 流程描述至少需要 10 个字符")
                text_valid = False
        layout_type = st.selectbox(
            "布局方式",
            ["hierarchical", "circular", "grid"],
            format_func=lambda x: {"hierarchical": "层次布局", "circular": "环形布局", "grid": "网格布局"}[x]
        )
        
        if st.button("🤖 AI 生成逻辑图", type="primary", use_container_width=True):
            if text_input and text_valid and st.session_state.get("llm_api_key"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔧 初始化 AI 服务...")
                    progress_bar.progress(20)
                    
                    llm = LLMService(
                        base_url=st.session_state.llm_base_url,
                        api_key=st.session_state.llm_api_key,
                        model=st.session_state.llm_model
                    )
                    
                    status_text.text("🤖 AI 正在分析流程并生成逻辑图...")
                    progress_bar.progress(50)
                    
                    result = llm.generate_logic_graph(text_input)
                    graph_data = parse_llm_json(result, layout=layout_type)
                    
                    progress_bar.progress(80)
                    status_text.text("📊 正在渲染逻辑图...")
                    
                    # 转换为 StreamlitFlowNode/Edge
                    st.session_state.graph_nodes = [
                        StreamlitFlowNode(
                            id=n["id"],
                            pos=(n["position"]["x"], n["position"]["y"]),
                            data={"content": n["data"]["label"]},
                            node_type="default",
                            draggable=True
                        ) for n in graph_data["nodes"]
                    ]
                    st.session_state.graph_edges = [
                        StreamlitFlowEdge(
                            id=e["id"],
                            source=e["source"],
                            target=e["target"],
                            label=e.get("label", ""),
                            animated=True
                        ) for e in graph_data["edges"]
                    ]
                    st.session_state.node_counter = len(graph_data["nodes"])
                    
                    progress_bar.progress(100)
                    status_text.text("✅ 逻辑图生成成功！")
                    
                    # 清理进度条
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"✅ 已生成 {len(graph_data['nodes'])} 个节点和 {len(graph_data['edges'])} 条边")
                    st.rerun()
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ 生成失败: {str(e)}")
                    with st.expander("🔍 查看详细错误"):
                        st.code(str(e))
            elif not st.session_state.get("llm_api_key"):
                st.warning("⚠️ 请先在侧边栏配置 API Key")
            else:
                st.warning("⚠️ 请输入流程描述")

    with col2:
        st.write("### 手动操作")
        
        if st.button("➕ 添加节点", use_container_width=True):
            st.session_state.node_counter += 1
            new_id = str(st.session_state.node_counter)
            st.session_state.graph_nodes.append(
                StreamlitFlowNode(
                    id=new_id,
                    pos=(250, len(st.session_state.graph_nodes) * 100 + 50),
                    data={"content": f"新节点 {new_id}"},
                    node_type="default",
                    draggable=True
                )
            )
            st.rerun()

        if st.button("🗑️ 清空画布", use_container_width=True):
            st.session_state.graph_nodes = []
            st.session_state.graph_edges = []
            st.session_state.node_counter = 0
            st.rerun()
        
        # 显示统计信息
        if st.session_state.graph_nodes:
            st.divider()
            st.metric("节点数量", len(st.session_state.graph_nodes))
            st.metric("连接数量", len(st.session_state.graph_edges))

    # 交互式画布
    st.subheader("画布区域")
    if st.session_state.graph_nodes:
        # 创建 StreamlitFlowState 对象
        flow_state = StreamlitFlowState(
            st.session_state.graph_nodes,
            st.session_state.graph_edges
        )
        
        flow_result = streamlit_flow(
            key="logic_flow",
            state=flow_state,
            layout=TreeLayout(direction="down"),
            fit_view=True,
            height=500,
            enable_node_menu=True,
            enable_edge_menu=True,
            enable_pane_menu=True,
            get_node_on_click=True,
            get_edge_on_click=True
        )
        # 状态同步：更新节点位置
        if flow_result:
            st.caption(f"选中: {flow_result}")
    else:
        st.info("画布为空，请 AI 生成或手动添加节点")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ LLM 配置")
    
    # 显示连接状态
    if st.session_state.get("llm_api_key"):
        st.success("✅ API 已配置")
    else:
        st.warning("⚠️ 未配置 API")
    
    base_url = st.text_input(
        "API Base URL",
        value="https://api.openai.com/v1",
        key="llm_base_url",
        help="支持 OpenAI 协议的 API 地址\n例如：\n- OpenAI: https://api.openai.com/v1\n- Qwen: https://dashscope.aliyuncs.com/compatible-mode/v1\n- DeepSeek: https://api.deepseek.com/v1"
    )
    
    # URL 格式验证
    if base_url and not (base_url.startswith("http://") or base_url.startswith("https://")):
        st.error("❌ API Base URL 必须以 http:// 或 https:// 开头")
    
    api_key = st.text_input("API Key", type="password", key="llm_api_key", help="你的 API 密钥")
    
    # API Key 验证
    if api_key and len(api_key.strip()) < 10:
        st.error("❌ API Key 格式不正确（至少 10 个字符）")
    
    model = st.text_input(
        "Model",
        value="gpt-3.5-turbo",
        key="llm_model",
        help="模型名称\n例如：\n- OpenAI: gpt-4, gpt-3.5-turbo\n- Qwen: qwen-turbo, qwen-plus\n- DeepSeek: deepseek-chat"
    )
    
    # Model 验证
    if model and len(model.strip()) < 3:
        st.error("❌ 模型名称格式不正确")
    
    # API 连接测试
    st.divider()
    if st.button("🔌 测试 API 连接", use_container_width=True, type="secondary"):
        if not api_key or len(api_key.strip()) < 10:
            st.error("❌ 请先输入有效的 API Key")
        elif not base_url or not (base_url.startswith("http://") or base_url.startswith("https://")):
            st.error("❌ 请先输入有效的 API Base URL")
        elif not model or len(model.strip()) < 3:
            st.error("❌ 请先输入有效的模型名称")
        else:
            with st.spinner("正在测试连接..."):
                try:
                    from core.llm_service import LLMService
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

    st.divider()
    st.header("📖 使用说明")
    st.markdown("""
    ### 📈 数据绘图
    1. **上传数据**：支持 CSV/Excel 格式
    2. **描述需求**：用自然语言描述图表
       - 示例：画出 X 和 Y 的散点图
       - 示例：绘制各组的箱线图，添加显著性标记
    3. **选择风格**：Nature/Science/Cell/PNAS
    4. **生成下载**：一键生成并导出

    ### 🔗 逻辑图
    1. **文本输入**：描述实验流程或逻辑
    2. **AI 生成**：自动提取节点和关系
    3. **手动编辑**：拖拽调整节点位置
    4. **动态更新**：实时保存修改

    ### 💡 提示
    - 图表描述越详细，生成效果越好
    - 可以指定颜色、标记、图例等细节
    - 支持中文列名和标签
    - 代码自动修复，最多重试 3 次
    """)
    
    # 统计信息
    if st.session_state.plot_history:
        st.divider()
        st.metric("📊 已生成图表", len(st.session_state.plot_history))
