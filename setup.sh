#!/bin/bash
# SciPlot-Copilot 快速设置脚本

echo "🚀 SciPlot-Copilot 环境设置"
echo "================================"

# 检查 Python 版本
echo "📌 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "当前 Python 版本: $python_version"

# 创建虚拟环境
echo ""
echo "📦 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo ""
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo ""
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "📥 安装依赖包..."
pip install -r requirements.txt

echo ""
echo "================================"
echo "✅ 环境设置完成！"
echo ""
echo "💡 使用说明："
echo "1. 激活虚拟环境："
echo "   source venv/bin/activate"
echo ""
echo "2. 运行应用："
echo "   streamlit run app.py"
echo ""
echo "3. 运行测试："
echo "   python tests/test_core.py"
echo ""
echo "4. 退出虚拟环境："
echo "   deactivate"
echo ""
echo "📖 查看详细文档："
echo "   - README.md - 项目说明"
echo "   - USAGE_GUIDE.md - 使用指南"
echo "================================"