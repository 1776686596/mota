#!/usr/bin/env python3
"""修复 matplotlib 中文字体显示问题"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import shutil

def clear_font_cache():
    """清除 matplotlib 字体缓存"""
    cache_dir = fm.get_cachedir()
    print(f"字体缓存目录: {cache_dir}")
    
    cache_files = [
        'fontlist-v330.json',
        'fontlist-v320.json', 
        'fontlist-v310.json',
        'fontList.cache'
    ]
    
    for cache_file in cache_files:
        cache_path = os.path.join(cache_dir, cache_file)
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print(f"✅ 已删除缓存文件: {cache_file}")
    
    print("✅ 字体缓存已清除")

def list_chinese_fonts():
    """列出系统中可用的中文字体"""
    print("\n系统可用的中文字体:")
    fonts = [f.name for f in fm.fontManager.ttflist if 'CJK' in f.name or 'Chinese' in f.name or '黑' in f.name or 'Hei' in f.name]
    fonts = sorted(set(fonts))
    
    for i, font in enumerate(fonts, 1):
        print(f"  {i}. {font}")
    
    return fonts

def test_chinese_display():
    """测试中文显示"""
    print("\n测试中文字体显示...")
    
    # 设置字体
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建测试图表
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.text(0.5, 0.5, '中文测试 Chinese Test', 
            fontsize=20, ha='center', va='center')
    ax.set_title('中文字体测试图表')
    ax.set_xlabel('X轴标签')
    ax.set_ylabel('Y轴标签')
    
    # 保存测试图片
    output_path = 'font_test.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 测试图片已保存: {output_path}")
    print("   请打开查看中文是否正常显示")

if __name__ == '__main__':
    print("=" * 50)
    print("Matplotlib 中文字体修复工具")
    print("=" * 50)
    
    # 1. 清除缓存
    clear_font_cache()
    
    # 2. 重新构建字体列表
    print("\n重新构建字体列表...")
    fm._load_fontmanager(try_read_cache=False)
    print("✅ 字体列表已重建")
    
    # 3. 列出可用中文字体
    chinese_fonts = list_chinese_fonts()
    
    # 4. 测试中文显示
    if chinese_fonts:
        test_chinese_display()
    else:
        print("\n⚠️ 未找到中文字体，请安装:")
        print("   sudo apt-get install fonts-noto-cjk")
    
    print("\n" + "=" * 50)
    print("修复完成！")
    print("=" * 50)