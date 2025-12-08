"""统一的字体配置模块

提供 matplotlib 中文字体配置，确保所有模块使用一致的字体设置
"""

import matplotlib
matplotlib.use('Agg')  # 必须在导入 pyplot 之前设置
import matplotlib.pyplot as plt


# 中文字体列表（按优先级排序）
CHINESE_FONTS = [
    'Noto Sans CJK SC',      # 思源黑体简体（Linux 常见）
    'WenQuanYi Micro Hei',   # 文泉驿微米黑（Linux 常见）
    'Noto Sans CJK JP',      # 思源黑体日文（备选）
    'SimHei',                # Windows 黑体
    'Microsoft YaHei',       # 微软雅黑
    'PingFang SC',           # 苹方（macOS）
    'Hiragino Sans GB',      # 冬青黑体（macOS）
    'DejaVu Sans',           # 通用备选
    'Arial',                 # 最终备选
]


def setup_chinese_font():
    """设置 matplotlib 中文字体
    
    在每个需要绑图的模块开头调用此函数
    """
    plt.rcParams['font.sans-serif'] = CHINESE_FONTS
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def get_chinese_fonts():
    """获取中文字体列表"""
    return CHINESE_FONTS.copy()


# 模块加载时自动设置字体
setup_chinese_font()