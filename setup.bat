@echo off
REM SciPlot-Copilot 快速设置脚本 (Windows)

echo ========================================
echo 🚀 SciPlot-Copilot 环境设置
echo ========================================
echo.

REM 检查 Python 版本
echo 📌 检查 Python 版本...
python --version
echo.

REM 创建虚拟环境
echo 📦 创建虚拟环境...
if exist venv (
    echo ⚠️  虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    echo ✅ 虚拟环境创建成功
)
echo.

REM 激活虚拟环境
echo 🔌 激活虚拟环境...
call venv\Scripts\activate.bat
echo.

REM 升级 pip
echo ⬆️  升级 pip...
python -m pip install --upgrade pip
echo.

REM 安装依赖
echo 📥 安装依赖包...
pip install -r requirements.txt
echo.

echo ========================================
echo ✅ 环境设置完成！
echo.
echo 💡 使用说明：
echo 1. 激活虚拟环境：
echo    venv\Scripts\activate
echo.
echo 2. 运行应用：
echo    streamlit run app.py
echo.
echo 3. 运行测试：
echo    python tests\test_core.py
echo.
echo 4. 退出虚拟环境：
echo    deactivate
echo.
echo 📖 查看详细文档：
echo    - README.md - 项目说明
echo    - USAGE_GUIDE.md - 使用指南
echo ========================================
pause