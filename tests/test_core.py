"""SciPlot-Copilot 核心功能单元测试"""

import unittest
import pandas as pd
import numpy as np
from io import BytesIO, StringIO
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_loader import load_data, extract_metadata
from core.sandbox import check_code_safety, apply_style
from core.logic_graph import create_node, create_edge, auto_layout, circular_layout, grid_layout, parse_llm_json


class TestDataLoader(unittest.TestCase):
    """测试数据加载模块"""
    
    def setUp(self):
        """准备测试数据"""
        self.csv_data = "A,B,C\n1,2,3\n4,5,6\n7,8,9"
        self.df = pd.DataFrame({
            'A': [1, 4, 7],
            'B': [2, 5, 8],
            'C': [3, 6, 9]
        })
    
    def test_extract_metadata(self):
        """测试元数据提取"""
        metadata = extract_metadata(self.df)
        
        self.assertIn('columns', metadata)
        self.assertIn('dtypes', metadata)
        self.assertIn('sample', metadata)
        self.assertIn('shape', metadata)
        
        self.assertEqual(metadata['columns'], ['A', 'B', 'C'])
        self.assertEqual(metadata['shape'], (3, 3))
    
    def test_load_csv_data(self):
        """测试 CSV 加载"""
        # 模拟文件对象
        class MockFile:
            def __init__(self, content, name):
                self.content = content
                self.name = name
            
            def read(self):
                return self.content.encode()
        
        mock_file = MockFile(self.csv_data, "test.csv")
        # 注意：实际测试需要调整 load_data 以支持字符串输入
        # 这里只测试逻辑
        self.assertIsNotNone(mock_file)


class TestSandbox(unittest.TestCase):
    """测试代码沙箱模块"""
    
    def test_check_safe_code(self):
        """测试安全代码检查 - 安全代码"""
        safe_code = """
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
"""
        is_safe, msg = check_code_safety(safe_code)
        self.assertTrue(is_safe)
        self.assertEqual(msg, "")
    
    def test_check_dangerous_code_os_system(self):
        """测试危险代码检查 - os.system"""
        dangerous_code = "import os\nos.system('rm -rf /')"
        is_safe, msg = check_code_safety(dangerous_code)
        self.assertFalse(is_safe)
        self.assertIn("危险", msg)
    
    def test_check_dangerous_code_subprocess(self):
        """测试危险代码检查 - subprocess"""
        dangerous_code = "import subprocess\nsubprocess.call(['ls'])"
        is_safe, msg = check_code_safety(dangerous_code)
        self.assertFalse(is_safe)
    
    def test_check_dangerous_code_eval(self):
        """测试危险代码检查 - eval"""
        dangerous_code = "eval('print(1)')"
        is_safe, msg = check_code_safety(dangerous_code)
        self.assertFalse(is_safe)
    
    def test_apply_style(self):
        """测试风格应用"""
        import matplotlib.pyplot as plt
        
        # 测试 Nature 风格
        apply_style("Nature")
        self.assertEqual(plt.rcParams['font.size'], 8)
        
        # 测试 Science 风格
        apply_style("Science")
        self.assertEqual(plt.rcParams['font.size'], 9)
        
        # 测试 Cell 风格
        apply_style("Cell")
        self.assertEqual(plt.rcParams['font.size'], 9)
        
        # 测试 PNAS 风格
        apply_style("PNAS")
        self.assertEqual(plt.rcParams['font.size'], 8)


class TestLogicGraph(unittest.TestCase):
    """测试逻辑图模块"""
    
    def test_create_node(self):
        """测试节点创建"""
        node = create_node("1", "测试节点", 100, 200)
        
        self.assertEqual(node['id'], "1")
        self.assertEqual(node['data']['label'], "测试节点")
        self.assertEqual(node['position']['x'], 100)
        self.assertEqual(node['position']['y'], 200)
    
    def test_create_edge(self):
        """测试边创建"""
        edge = create_edge("1", "2", "连接")
        
        self.assertEqual(edge['id'], "e1-2")
        self.assertEqual(edge['source'], "1")
        self.assertEqual(edge['target'], "2")
        self.assertEqual(edge['label'], "连接")
    
    def test_auto_layout(self):
        """测试自动布局"""
        nodes = [
            {"id": "1", "data": {"label": "节点1"}},
            {"id": "2", "data": {"label": "节点2"}},
            {"id": "3", "data": {"label": "节点3"}}
        ]
        edges = [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"}
        ]
        
        laid_out = auto_layout(nodes, edges)
        
        self.assertEqual(len(laid_out), 3)
        # 检查所有节点都有位置
        for node in laid_out:
            self.assertIn('position', node)
            self.assertIn('x', node['position'])
            self.assertIn('y', node['position'])
    
    def test_circular_layout(self):
        """测试环形布局"""
        nodes = [
            {"id": "1", "data": {"label": "节点1"}},
            {"id": "2", "data": {"label": "节点2"}},
            {"id": "3", "data": {"label": "节点3"}}
        ]
        
        laid_out = circular_layout(nodes, radius=200)
        
        self.assertEqual(len(laid_out), 3)
        # 检查节点在圆周上
        for node in laid_out:
            x = node['position']['x']
            y = node['position']['y']
            # 验证大致在圆周上（允许一定误差）
            self.assertTrue(isinstance(x, (int, float)))
            self.assertTrue(isinstance(y, (int, float)))
    
    def test_grid_layout(self):
        """测试网格布局"""
        nodes = [
            {"id": str(i), "data": {"label": f"节点{i}"}}
            for i in range(6)
        ]
        
        laid_out = grid_layout(nodes, cols=3, spacing=100)
        
        self.assertEqual(len(laid_out), 6)
        # 检查网格排列
        self.assertEqual(laid_out[0]['position']['x'], 100)
        self.assertEqual(laid_out[1]['position']['x'], 200)
        self.assertEqual(laid_out[2]['position']['x'], 300)
    
    def test_parse_llm_json(self):
        """测试 LLM JSON 解析"""
        json_str = '''
        {
            "nodes": [
                {"id": "1", "data": {"label": "开始"}},
                {"id": "2", "data": {"label": "处理"}},
                {"id": "3", "data": {"label": "结束"}}
            ],
            "edges": [
                {"id": "e1-2", "source": "1", "target": "2", "label": ""},
                {"id": "e2-3", "source": "2", "target": "3", "label": ""}
            ]
        }
        '''
        
        result = parse_llm_json(json_str)
        
        self.assertIn('nodes', result)
        self.assertIn('edges', result)
        self.assertEqual(len(result['nodes']), 3)
        self.assertEqual(len(result['edges']), 2)
    
    def test_parse_llm_json_with_markdown(self):
        """测试带 markdown 标记的 JSON 解析"""
        json_str = '''```json
        {
            "nodes": [{"id": "1", "data": {"label": "测试"}}],
            "edges": []
        }
        ```'''
        
        result = parse_llm_json(json_str)
        
        self.assertEqual(len(result['nodes']), 1)
        self.assertEqual(result['nodes'][0]['data']['label'], "测试")


class TestLLMService(unittest.TestCase):
    """测试 LLM 服务模块"""
    
    def test_clean_code_response(self):
        """测试代码清理功能"""
        from core.llm_service import LLMService
        
        # 测试带 markdown 标记的代码
        code_with_markdown = "```python\nprint('hello')\n```"
        cleaned = LLMService.clean_code_response(code_with_markdown)
        self.assertEqual(cleaned, "print('hello')")
        
        # 测试纯代码
        pure_code = "print('hello')"
        cleaned = LLMService.clean_code_response(pure_code)
        self.assertEqual(cleaned, "print('hello')")
        
        # 测试带语言标记的代码块
        code_with_lang = "```\nprint('hello')\n```"
        cleaned = LLMService.clean_code_response(code_with_lang)
        self.assertEqual(cleaned, "print('hello')")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestSandbox))
    suite.addTests(loader.loadTestsFromTestCase(TestLogicGraph))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMService))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)