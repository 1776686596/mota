"""LLM 统一调用接口 - 支持 OpenAI 协议 (Qwen/OpenAI)"""

import os
import re
from openai import OpenAI


class LLMService:
    """LLM 服务封装，支持 OpenAI 协议的模型"""

    def __init__(self, base_url: str = None, api_key: str = None, model: str = None):
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def list_models(self) -> tuple[bool, list[str], str]:
        """获取可用模型列表
        
        Returns:
            tuple[bool, list[str], str]: (是否成功, 模型列表, 消息)
        """
        try:
            # 尝试调用 models API
            models_response = self.client.models.list()
            model_ids = [model.id for model in models_response.data]
            
            if model_ids:
                return True, model_ids, f"✅ 成功获取 {len(model_ids)} 个可用模型"
            else:
                return False, [], "❌ 未找到可用模型"
        except Exception as e:
            error_msg = str(e)
            # 某些 API 可能不支持 list models，返回友好提示
            if "404" in error_msg or "not found" in error_msg.lower():
                return False, [], "⚠️ 该 API 不支持模型列表查询，请手动输入模型名称"
            elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return False, [], f"❌ API Key 无效或未授权\n{error_msg}"
            else:
                return False, [], f"❌ 获取模型列表失败：{error_msg}"
    
    def test_connection(self) -> tuple[bool, str]:
        """测试 API 连接是否可用
        
        Returns:
            tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 发送一个简单的测试请求
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
                temperature=0.3
            )
            # 如果能获取响应，说明连接成功
            if response.choices[0].message.content:
                return True, f"✅ 连接成功！模型 {self.model} 响应正常"
            else:
                return False, "❌ 连接失败：模型无响应"
        except Exception as e:
            error_msg = str(e)
            # 提供更友好的错误提示
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return False, f"❌ API Key 无效或未授权\n{error_msg}"
            elif "not_found" in error_msg.lower() or "model" in error_msg.lower():
                return False, f"❌ 模型 '{self.model}' 不存在或不可用\n{error_msg}"
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                return False, f"❌ 网络连接超时，请检查网络或 Base URL\n{error_msg}"
            else:
                return False, f"❌ 连接失败：{error_msg}"
    
    def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        """发送聊天请求，返回文本响应"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    @staticmethod
    def clean_code_response(code: str) -> str:
        """清理 LLM 返回的代码，移除 markdown 标记"""
        # 移除 markdown 代码块标记
        code = code.strip()
        if code.startswith("```"):
            # 移除开头的 ```python 或 ```
            code = re.sub(r'^```\w*\n', '', code)
            # 移除结尾的 ```
            code = re.sub(r'\n```$', '', code)
        return code.strip()

    def generate_plot_code(self, metadata: dict, user_prompt: str) -> str:
        """生成绘图代码"""
        system_prompt = """你是一个数据可视化专家。根据用户的数据元信息和需求，生成 matplotlib 绘图代码。

严格要求：
1. 直接使用预置的 DataFrame 变量 `df`，严禁重新读取文件或创建新数据
2. 中文字体已预配置（Noto Sans CJK SC），无需在代码中设置字体
3. 只输出纯 Python 代码，不要任何 markdown 标记、解释文字或注释
4. 代码末尾不要调用 plt.show() 或 plt.savefig()
5. 必须使用提供的 ax 对象绘图（已提供 fig, ax），例如：ax.plot() 而不是 plt.plot()
6. 不要导入任何模块（df, pd, np, plt, sns, fig, ax 已预加载）
7. 在访问列名前，必须先检查列名是否与提供的元数据一致
8. 对于分类数据，使用 unique() 获取类别，使用颜色区分

代码安全准则：
- 仔细核对列名，确保与元数据中的列名完全一致（包括大小写、空格）
- 处理数据类型：必要时使用 pd.to_numeric(df['col'], errors='coerce')
- 避免 KeyError：使用准确的列名
- 分类绘图时，先获取类别：categories = df['col'].unique()

标准代码模板：
# 基础散点图
ax.scatter(df['列名1'], df['列名2'], alpha=0.6, s=50)
ax.set_xlabel('X轴标签')
ax.set_ylabel('Y轴标签')
ax.set_title('图表标题')
ax.grid(True, alpha=0.3)

# 分组散点图
for category in df['分组列'].unique():
    mask = df['分组列'] == category
    ax.scatter(df.loc[mask, 'X列'], df.loc[mask, 'Y列'], label=category, alpha=0.6)
ax.legend()"""

        # 构建更详细的列名说明
        columns_info = []
        for col, dtype in metadata.get('dtypes', {}).items():
            columns_info.append(f"  - '{col}' (类型: {dtype})")
        columns_str = "\n".join(columns_info) if columns_info else "无"
        
        user_content = f"""数据详情：

可用列名（请务必使用完全相同的列名，包括空格和括号）:
{columns_str}

数据形状: {metadata.get('shape', (0, 0))[0]} 行 × {metadata.get('shape', (0, 0))[1]} 列

前5行数据示例:
{metadata.get('sample', '')}

用户需求: {user_prompt}

重要提醒：
1. 列名必须与上面列出的完全一致（包括括号、空格等）
2. 使用 df['列名'] 访问数据
3. 仅输出可执行的 Python 代码，不要任何解释

请直接输出代码："""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        code = self.chat(messages, temperature=0.3)
        return self.clean_code_response(code)

    def generate_logic_graph(self, text: str) -> str:
        """从文本生成逻辑图 JSON"""
        system_prompt = """你是一个实体关系抽取专家。从用户输入的文本中提取实体和关系，输出标准 JSON。

输出格式要求：
{
  "nodes": [
    {"id": "1", "data": {"label": "节点名称"}},
    {"id": "2", "data": {"label": "另一个节点"}}
  ],
  "edges": [
    {"id": "e1-2", "source": "1", "target": "2", "label": "关系描述"}
  ]
}

重要规则：
1. 节点 id 必须是字符串类型的数字："1", "2", "3"...
2. 边的 id 格式为 "e{source}-{target}"
3. 节点的 label 应该简洁明确
4. 边的 label 描述节点间的关系（可选）
5. 只输出 JSON，不要 markdown 标记或其他说明
6. 确保 JSON 格式正确，可以被直接解析"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请从以下文本中提取流程节点和关系：\n\n{text}"}
        ]
        response = self.chat(messages, temperature=0.3)
        return self.clean_code_response(response)

    def fix_code(self, code: str, error: str) -> str:
        """修复出错的代码"""
        system_prompt = """你是一个 Python 调试专家。分析错误信息并修复代码。

修复原则：
1. 仔细分析错误的根本原因
2. 只输出修复后的完整代码，不要解释文字
3. 不要添加 markdown 标记
4. 保持代码的原有结构和功能
5. 常见错误类型：
   - KeyError: 检查列名是否正确
   - TypeError: 检查数据类型转换
   - ValueError: 检查数值范围和格式
   - AttributeError: 检查对象方法调用"""

        user_content = f"""需要修复的代码：
```python
{code}
```

错误信息：
{error}

请分析错误原因并输出修复后的完整代码（不要 markdown 标记）。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        fixed_code = self.chat(messages, temperature=0.2)
        return self.clean_code_response(fixed_code)
    
    def recommend_plots(self, metadata: dict) -> list[dict]:
        """根据数据特征推荐合适的图表类型
        
        Returns:
            list[dict]: 推荐的图表列表，每个包含 title, description, prompt, design_tips
        """
        system_prompt = """你是一个专业的科研数据可视化专家。根据用户数据特征，推荐最适合的 3-4 个图表，并提供详细的设计建议。

图形设计对于向外部受众传达研究结果至关重要。你需要考虑：

1. **图表类型选择**：根据数据类型和关系选择最合适的图表（散点图、折线图、箱线图、热图、柱状图等）
2. **颜色方案**：为不同类别或组选择科研友好的配色（如 Nature、Science 期刊风格）
3. **符号与标记**：选择合适的点形状、线型、标记大小
4. **细节层次**：确定应展示的数据粒度和聚合方式
5. **排版布局**：子图排列、图例位置、坐标轴范围
6. **标签与注释**：轴标签、标题、图例、数据标注的清晰度

输出要求：
- 返回 JSON 数组，每个元素包含：
  * title: 图表标题（简短且描述性，如"多组数据散点相关性分析"）
  * description: 图表说明（1-2句话，说明适用场景和优势）
  * chart_type: 图表类型（如 "scatter", "line", "box", "heatmap" 等）
  * prompt: 完整的绘图提示词，包含具体的设计指导（颜色、符号、标签等）
  * design_tips: 设计要点数组，包含 3-5 个关键设计建议（如配色方案、标记样式、注释建议等）
- 推荐 3-4 个不同类型且互补的图表
- 提示词要详细且可执行，明确指定颜色、标记、布局等细节
- 只输出 JSON，不要其他说明"""

        # 构建数据特征描述
        columns_info = []
        numeric_cols = []
        categorical_cols = []
        
        for col, dtype in metadata.get('dtypes', {}).items():
            columns_info.append(f"  - '{col}' (类型: {dtype})")
            if 'int' in str(dtype).lower() or 'float' in str(dtype).lower():
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)
        
        columns_str = "\n".join(columns_info) if columns_info else "无"
        
        # 分析数据特征提供更多上下文
        has_groups = len(categorical_cols) > 0
        has_multiple_numeric = len(numeric_cols) >= 2
        data_size = metadata.get('shape', (0, 0))[0]
        
        context_hints = []
        if has_groups:
            context_hints.append(f"数据包含 {len(categorical_cols)} 个分组变量，适合使用颜色或符号区分不同组")
        if has_multiple_numeric:
            context_hints.append(f"有 {len(numeric_cols)} 个数值变量，可探索变量间关系")
        if data_size < 100:
            context_hints.append("数据量较小，适合展示每个数据点的详细信息")
        elif data_size > 1000:
            context_hints.append("数据量较大，可考虑聚合展示或密度图")
        
        context_str = "\n".join([f"  - {hint}" for hint in context_hints]) if context_hints else "  - 无特殊提示"
        
        # 处理数据示例，避免在 f-string 中使用反斜杠
        sample_data = metadata.get('sample', '')
        if sample_data:
            sample_lines = sample_data.split('\n')[:4]
            sample_preview = '\n'.join(sample_lines)
        else:
            sample_preview = ''
        
        user_content = f"""请根据以下数据特征推荐合适的图表，并提供详细的设计建议：

数据列信息:
{columns_str}

数据形状: {metadata.get('shape', (0, 0))[0]} 行 × {metadata.get('shape', (0, 0))[1]} 列

数值型列 ({len(numeric_cols)} 个): {', '.join([f"'{c}'" for c in numeric_cols[:5]])}{'...' if len(numeric_cols) > 5 else ''}
分类型列 ({len(categorical_cols)} 个): {', '.join([f"'{c}'" for c in categorical_cols[:5]])}{'...' if len(categorical_cols) > 5 else ''}

数据特征分析:
{context_str}

前3行数据示例:
{sample_preview}

请推荐 3-4 个最合适的图表类型，每个包含详细的图形设计建议，直接输出 JSON 数组："""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        try:
            response = self.chat(messages, temperature=0.5)
            # 清理并解析 JSON
            response = self.clean_code_response(response)
            import json
            recommendations = json.loads(response)
            return recommendations
        except Exception as e:
            # 返回默认推荐（带设计建议）
            default_recommendations = [
                {
                    "title": "基础散点图",
                    "description": "展示两个数值变量之间的关系，适合探索相关性",
                    "chart_type": "scatter",
                    "prompt": f"画出前两个数值列的散点图，使用深蓝色（#2E86AB）标记点，设置透明度 0.6，点大小 50，添加清晰的轴标签和网格线",
                    "design_tips": [
                        "使用半透明点避免重叠",
                        "添加浅色网格线提高可读性",
                        "轴标签使用 12pt 字体",
                        "如有分组可用不同颜色区分"
                    ]
                },
                {
                    "title": "数据分布图",
                    "description": "展示数值变量的分布特征和异常值",
                    "chart_type": "box",
                    "prompt": "绘制主要数值列的箱线图，使用淡蓝色填充（#A8DADC），箱体边框使用深色（#1D3557），标注中位数和异常值",
                    "design_tips": [
                        "使用箱线图展示分位数信息",
                        "用不同颜色标注异常值",
                        "横向排列便于比较多个变量",
                        "添加数据点提供完整信息"
                    ]
                }
            ]
            
            # 如果有分组变量，添加分组可视化推荐
            if categorical_cols and numeric_cols:
                default_recommendations.append({
                    "title": "分组对比图",
                    "description": "按类别比较数值变量的差异",
                    "chart_type": "grouped_bar",
                    "prompt": f"绘制按 {categorical_cols[0]} 分组的 {numeric_cols[0]} 柱状图，使用 Nature 配色方案（蓝色系），添加误差线和数值标签",
                    "design_tips": [
                        "使用 Nature/Science 期刊配色",
                        "柱子间距适中便于区分",
                        "添加误差线表示不确定性",
                        "数值标签保留合适位数"
                    ]
                })
            
            return default_recommendations
