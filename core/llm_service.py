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

要求：
1. 直接使用预置的 DataFrame 变量 `df`，严禁重新读取文件
2. 必须设置中文字体支持（已预配置，无需在代码中再次设置）
3. 只输出纯 Python 代码，不要任何 markdown 标记、解释文字或注释说明
4. 代码末尾不要调用 plt.show()，图表会自动捕获
5. 使用 ax 对象进行绘图（已提供 fig, ax），例如：ax.plot() 而不是 plt.plot()
6. 确保代码简洁高效，避免不必要的导入
7. 对于分类数据，优先使用颜色、形状等区分
8. 添加适当的图例、轴标签和标题

示例代码结构：
ax.scatter(df['x'], df['y'], c=df['category'])
ax.set_xlabel('X轴标签')
ax.set_ylabel('Y轴标签')
ax.set_title('图表标题')
ax.legend()"""

        user_content = f"""数据元信息：
- 列名: {metadata.get('columns', [])}
- 数据类型: {metadata.get('dtypes', {})}
- 数据形状: {metadata.get('shape', (0, 0))}
- 样本数据(前5行):
{metadata.get('sample', '')}

用户需求: {user_prompt}

请直接输出 Python 代码，不要任何额外说明。"""

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
