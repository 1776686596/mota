📂 SciPlot-Copilot 需求规格说明书 (Final Version)
项目代号: SciPlot-Copilot 应用类型: AI 驱动的科研可视化与逻辑梳理平台 核心技术栈: Python 3.10, Streamlit, Pandas, Matplotlib, Streamlit-Flow (或同类交互组件), LLM (Qwen/OpenAI Protocol)

1. 系统架构概述
系统采用 双模态 (Dual-Tab) 布局，分别处理“定量数据”和“定性逻辑”。

前端: Streamlit Web UI (负责交互、展示、文件流)。

中台 (State Manager): st.session_state (负责维护 DataFrame、图表对象、节点/边 JSON 数据的一致性)。

后端 (Logic Core):

Data Engine: 解析 CSV/Excel，提取元数据。

Code Sandbox: 安全执行 LLM 生成的 Python 绘图代码。

Layout Engine: 处理逻辑图的自动布局（JSON 坐标计算）。

LLM Service: 统一接口封装，负责 Prompt 组装与 API 调用。

2. 功能模块详细需求
🟢 模块 A：智能数据绘图 (Tab 1: Data Plotter)
目标: 将静态数据转化为符合期刊发表标准的统计图表。

F1. 数据接入与解析
支持格式: .csv, .xlsx。

处理逻辑:

用户上传文件后，系统不应将完整文件内容发送给 LLM。

系统需本地解析文件，提取 Metadata (元数据)：列名 (Columns)、数据类型 (Dtypes)、前 5 行样本数据。

UI 反馈: 必须展示数据预览表格 (DataFrame Preview) 供用户确认。

F2. 自然语言绘图 (Text-to-Code)
输入: 用户的自然语言指令（如“画出电压和电流的散点图，区分不同批次”）。

核心处理:

将 Metadata + User Prompt + System Prompt 组装。

LLM 输出：纯 Python 代码字符串 (基于 matplotlib 或 seaborn)。

约束条件:

生成的代码必须直接使用预置的 DataFrame 变量（严禁代码中重新读取文件）。

生成的代码必须处理中文乱码问题（设置字体）。

F3. 代码沙箱与容错 (Sandbox & Self-Healing)
执行环境: 使用 Python exec()。必须注入全局变量上下文 (df, pd, plt)。

自动修复机制 (Self-Healing):

系统需捕获 exec() 抛出的异常 (Traceback)。

若发生异常，自动触发重试循环：将“报错信息”回传给 LLM 要求修正代码。

最大重试次数建议设为 3 次。

输出: 成功执行后，捕获当前的 Figure 对象进行渲染。

F4. 科研风格化 (Style Transfer)
交互: 提供下拉菜单选择风格 (Default, Nature, Science)。

逻辑: 在执行绘图代码前，预先注入对应的 plt.rcParams 配置（如字体类型、字号、去网格、刻度朝向），确保出图风格统一。

F5. 可复现性交付
展示: 图表下方必须显示生成该图表的 完整 Python 源代码。

下载: 提供图片 (.png) 下载按钮。

🔵 模块 B：交互式逻辑梳理 (Tab 2: Logic Mapper)
目标: 实现科研思路、实验流程的 AI 生成 + 人工编辑 混合工作流。

F6. 双源创建模式
模式 A：AI 生成 (Prompt-to-Graph)

用户输入文本（实验步骤描述）。

LLM 进行实体关系抽取，输出标准化的 JSON 数据 (包含 nodes 和 edges 列表)。

系统对 JSON 数据进行简单的自动布局 (Auto-Layout)，计算每个节点的 (x, y) 坐标。

模式 B：手动创建 (Manual)

工具栏提供“新建节点”按钮。

点击后在画布中心生成一个默认节点。

F7. 交互式画布 (Interactive Canvas)
技术要求: 基于 ReactFlow 或类似机制的 Streamlit 组件。

核心交互:

拖拽布局: 用户可鼠标拖动节点改变位置。

连线: 用户可从一个节点的 Handle 拖拽到另一个节点建立连线。

编辑: 点击节点/连线，可修改其文本标签 (Label) 或颜色。

删除: 选中节点/连线后可删除。

F8. 状态同步 (State Synchronization)
逻辑: 前端组件的任何变动（拖拽、新增、删除）必须实时/回调更新后端的 session_state 数据。

目的: 保证用户切换 Tab 或触发 Streamlit 刷新后，辛苦画的图不会重置。

3. 非功能性需求 (约束)
安全性: 严禁 LLM 生成的代码调用系统级命令（如 os.system）。需在执行前进行关键词正则过滤。

数据隐私: 用户上传的数据文件仅保留在内存中，不持久化保存到服务器磁盘（Session 结束后释放）。

响应速度: 绘图任务端到端延迟控制在 15秒以内。

依赖管理: 项目根目录必须包含 requirements.txt，且兼容 ModelScope 的基础镜像环境。

4. 程序员实现路线建议 (Roadmap)
Phase 1: 基础设施 (Infrastructure)

搭建 Streamlit 多 Tab 框架。

封装 LLM 统一调用接口 (Mock 模式 -> 真实 API)。

实现 Data Loader (只读 metadata)。

Phase 2: 交互式逻辑图 (The Hard Part)

这是难点，建议先攻克。

调试 streamlit-flow (或其他选定库)。

定义 Node/Edge 的 JSON 数据结构 Schema。

实现 "JSON -> Canvas" 和 "Canvas -> JSON" 的双向绑定。

接入 LLM：调试 Prompt 让其稳定输出 JSON。

Phase 3: 数据绘图核心 (The Core)

实现 exec 沙箱环境注入。

调试 Matplotlib 中文显示。

实现 try-except 自动重试闭环。

注入 Nature/Science 风格配置。

Phase 4: 整合与部署

完善 UI 细节 (Help Text, Sidebar)。

本地全流程测试 (从上传数据到下载图片)。

生成依赖清单，准备 Readme。