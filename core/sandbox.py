"""代码沙箱 - 安全执行 LLM 生成的绘图代码"""

import re
import traceback
import matplotlib
matplotlib.use('Agg')  # 必须在导入 pyplot 之前设置非交互式后端
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

# 危险关键词黑名单
FORBIDDEN_PATTERNS = [
    r'\bos\s*\.\s*system',
    r'\bos\s*\.\s*popen',
    r'\bsubprocess',
    r'\b__import__',
    r'\beval\s*\(',
    r'\bexec\s*\(',
    r'\bopen\s*\([^)]*["\']w',
    r'\bimport\s+os\b',
    r'\bfrom\s+os\b',
    r'\bimport\s+subprocess',
    r'\bimport\s+sys\b',
    r'\bsys\s*\.\s*exit',
]


def check_code_safety(code: str) -> tuple[bool, str]:
    """检查代码安全性，返回 (是否安全, 错误信息)"""
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"检测到危险代码模式: {pattern}"
    return True, ""


# 中文字体列表（用于所有风格）
CHINESE_FONTS = [
    'Noto Sans CJK SC',      # 思源黑体简体
    'WenQuanYi Micro Hei',   # 文泉驿微米黑
    'Noto Sans CJK JP',      # 思源黑体日文
    'SimHei',                # Windows 黑体
    'Microsoft YaHei',       # 微软雅黑
]

# 期刊风格配置
STYLES = {
    "Default": {
        "figure.dpi": 100,
    },
    "Nature": {
        "font.family": "sans-serif",
        "font.sans-serif": CHINESE_FONTS + ["Arial", "DejaVu Sans"],
        "font.size": 8,
        "axes.linewidth": 0.5,
        "axes.labelsize": 8,
        "axes.titlesize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "legend.fontsize": 7,
        "legend.frameon": False,
        "figure.dpi": 300,
        "axes.spines.top": False,
        "axes.spines.right": False,
    },
    "Science": {
        "font.family": "sans-serif",
        "font.sans-serif": CHINESE_FONTS + ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 9,
        "axes.linewidth": 0.6,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "legend.fontsize": 8,
        "legend.frameon": False,
        "figure.dpi": 300,
        "axes.grid": False,
    },
    "Cell": {
        "font.family": "sans-serif",
        "font.sans-serif": CHINESE_FONTS + ["Arial", "DejaVu Sans"],
        "font.size": 9,
        "axes.linewidth": 0.75,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.major.width": 0.75,
        "ytick.major.width": 0.75,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "legend.fontsize": 9,
        "legend.frameon": True,
        "figure.dpi": 300,
        "axes.grid": False,
    },
    "PNAS": {
        "font.family": "sans-serif",
        "font.sans-serif": CHINESE_FONTS + ["Arial", "DejaVu Sans"],
        "font.size": 8,
        "axes.linewidth": 0.5,
        "axes.labelsize": 8,
        "axes.titlesize": 9,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "legend.fontsize": 7,
        "legend.frameon": False,
        "figure.dpi": 300,
        "axes.spines.top": False,
        "axes.spines.right": False,
    },
}


def apply_style(style_name: str):
    """应用期刊风格"""
    plt.rcdefaults()
    # 中文支持 - 先设置基础中文字体
    plt.rcParams['font.sans-serif'] = CHINESE_FONTS + ['DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    # 应用风格（风格配置中已包含中文字体）
    if style_name in STYLES:
        plt.rcParams.update(STYLES[style_name])
    # 确保负号显示正常
    plt.rcParams['axes.unicode_minus'] = False


def execute_plot_code(code: str, df: pd.DataFrame, style: str = "Default", max_retries: int = 3, llm_service=None) -> tuple[plt.Figure, str]:
    """
    执行绘图代码，返回 (Figure, 最终代码)
    支持自动修复机制
    """
    # 安全检查
    is_safe, error_msg = check_code_safety(code)
    if not is_safe:
        raise ValueError(error_msg)

    apply_style(style)
    current_code = code
    last_error = None

    for attempt in range(max_retries):
        try:
            plt.close('all')
            # 设置合理的默认图表大小（宽10英寸，高6英寸）
            fig, ax = plt.subplots(figsize=(10, 6))

            # 构建执行环境
            exec_globals = {
                "df": df,
                "pd": pd,
                "np": np,
                "plt": plt,
                "sns": sns,
                "fig": fig,
                "ax": ax,
            }

            exec(current_code, exec_globals)

            # 获取当前 figure
            fig = plt.gcf()
            return fig, current_code

        except Exception as e:
            # 获取详细的错误信息
            last_error = f"{type(e).__name__}: {str(e)}\n\n堆栈信息:\n{traceback.format_exc()}"
            
            if attempt < max_retries - 1 and llm_service:
                # 尝试自动修复
                print(f"⚠️ 第 {attempt + 1} 次执行失败，尝试自动修复...")
                current_code = llm_service.fix_code(current_code, last_error)
                # 再次安全检查
                is_safe, error_msg = check_code_safety(current_code)
                if not is_safe:
                    raise ValueError(f"修复后的代码仍包含危险操作: {error_msg}")
            else:
                raise RuntimeError(f"执行失败 (尝试 {attempt + 1}/{max_retries}):\n{last_error}")

    raise RuntimeError(f"代码执行失败，已尝试 {max_retries} 次:\n{last_error}")
