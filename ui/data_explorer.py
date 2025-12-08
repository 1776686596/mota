"""数据探索 UI 组件

提供数据统计、相关性分析、缺失值检测等功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import io

# 导入统一的字体配置（必须在 matplotlib.pyplot 之前）
from utils.font_config import setup_chinese_font, CHINESE_FONTS

# 设置 matplotlib 后端 - 必须在导入 pyplot 之前
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# 确保字体设置生效
setup_chinese_font()


def render_data_explorer(df: pd.DataFrame):
    """渲染数据探索界面
    
    Args:
        df: 数据 DataFrame
    """
    # 使用 expander 但避免在内部使用可能导致状态问题的组件
    with st.expander("🔍 数据探索与分析", expanded=False):
        _render_descriptive_stats(df)
        _render_correlation_matrix(df)
        _render_missing_values(df)
        _render_data_types(df)


def _render_metric_card(label: str, value: str, delta: str = None, delta_type: str = "neutral"):
    """渲染自定义指标卡片
    
    Args:
        label: 指标名称
        value: 指标数值
        delta: 变化量/补充信息
        delta_type: 变化类型 (positive, negative, neutral)
    """
    delta_html = ""
    if delta:
        delta_class = f"delta-{delta_type}"
        delta_html = f'<span class="metric-delta {delta_class}">{delta}</span>'
    
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def _render_descriptive_stats(df: pd.DataFrame):
    """渲染描述性统计"""
    st.markdown("#### 📊 描述性统计 (Descriptive Statistics)")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        # 关键指标展示 - 不使用 tabs 避免状态问题
        st.markdown("**📈 统计概览**")
        cols = st.columns(min(len(numeric_cols), 4))
        for i, col in enumerate(numeric_cols[:4]):
            with cols[i]:
                _render_metric_card(
                    label=col,
                    value=f"{df[col].mean():.2f}",
                    delta=f"std: {df[col].std():.2f}",
                    delta_type="neutral"
                )
        
        # 详细数据
        st.markdown("**📋 详细数据**")
        desc_stats = df[numeric_cols].describe().T
        desc_stats['median'] = df[numeric_cols].median()
        desc_stats = desc_stats[['count', 'mean', 'median', 'std', 'min', '25%', '50%', '75%', 'max']]
        desc_stats.columns = ['计数', '均值', '中位数', '标准差', '最小值', '25%分位', '50%分位', '75%分位', '最大值']
        st.dataframe(desc_stats, use_container_width=True)
    else:
        st.info("ℹ️ 数据集中没有数值列，无法生成描述性统计")


def _render_correlation_matrix(df: pd.DataFrame):
    """渲染相关性矩阵热图"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) > 1:
        st.divider()
        st.markdown("#### 🔥 相关性分析 (Correlation Analysis)")
        
        # 计算相关性矩阵
        corr_matrix = df[numeric_cols].corr()
        
        # 确保中文字体设置
        setup_chinese_font()
        
        # 生成热图并转换为图片字节
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        ax.set_title('特征相关性矩阵', fontsize=14, pad=20)
        plt.tight_layout()
        
        # 将图表转换为图片字节，使用 st.image 显示（更稳定）
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(buf, use_container_width=True)
        
        with col2:
            # 显示强相关关系
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_corr.append({
                            '变量1': corr_matrix.columns[i],
                            '变量2': corr_matrix.columns[j],
                            '相关系数': f"{corr_val:.3f}",
                            '关系强度': '强正相关' if corr_val > 0 else '强负相关'
                        })
            
            if strong_corr:
                st.info("💡 发现强相关关系（|r| > 0.7）：")
                st.dataframe(pd.DataFrame(strong_corr), use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ 未发现强相关关系")


def _render_missing_values(df: pd.DataFrame):
    """渲染缺失值分析"""
    st.divider()
    st.markdown("#### 🔍 缺失值分析 (Missing Values)")
    
    missing_data = df.isnull().sum()
    missing_percent = (missing_data / len(df)) * 100
    missing_df = pd.DataFrame({
        '缺失数量': missing_data,
        '缺失比例(%)': missing_percent
    }).sort_values('缺失数量', ascending=False)
    
    missing_df = missing_df[missing_df['缺失数量'] > 0]
    
    if len(missing_df) > 0:
        st.warning(f"⚠️ 发现 {len(missing_df)} 个特征存在缺失值")
        st.dataframe(missing_df, use_container_width=True)
        
        # 确保中文字体设置
        setup_chinese_font()
        
        # 缺失值可视化 - 使用 st.image 替代 st.pyplot
        fig, ax = plt.subplots(figsize=(10, max(6, len(missing_df) * 0.5)))
        missing_df['缺失比例(%)'].plot(kind='barh', ax=ax, color='#E74C3C')
        ax.set_xlabel('缺失比例 (%)', fontsize=12)
        ax.set_ylabel('特征', fontsize=12)
        ax.set_title('各特征缺失值比例', fontsize=14, pad=20)
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        # 转换为图片字节
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        st.image(buf, use_container_width=True)
    else:
        st.success("✅ 数据完整，无缺失值")


def _render_data_types(df: pd.DataFrame):
    """渲染数据类型分析"""
    st.divider()
    st.markdown("#### 🔬 数据类型与建议 (Data Types & Suggestions)")
    
    type_info = []
    for col in df.columns:
        dtype = df[col].dtype
        unique_count = df[col].nunique()
        total_count = len(df[col])
        
        # 推断建议
        suggestion = ""
        if dtype == 'object':
            if unique_count < 10:
                suggestion = "建议转为分类变量 (Categorical)"
            elif unique_count < total_count * 0.5:
                suggestion = "可能是分类变量"
            else:
                suggestion = "文本数据，考虑特征工程"
        elif dtype in ['int64', 'float64']:
            if unique_count < 10:
                suggestion = "数值较少，可能是离散分类变量"
            elif df[col].min() >= 0 and df[col].max() <= 1:
                suggestion = "可能是比例或概率值"
            else:
                suggestion = "连续数值变量"
        
        type_info.append({
            '列名': col,
            '当前类型': str(dtype),
            '唯一值数量': unique_count,
            '建议': suggestion
        })
    
    type_df = pd.DataFrame(type_info)
    st.dataframe(type_df, use_container_width=True, hide_index=True)
    
    # 数据类型分布 - 使用 Metric Card
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    col1, col2, col3 = st.columns(3)
    with col1:
        _render_metric_card("数值列 (Numeric)", str(len(numeric_cols)), "统计基础", "positive")
    with col2:
        _render_metric_card("类别列 (Categorical)", str(len(df.select_dtypes(include=['object']).columns)), "分类基础", "neutral")
    with col3:
        _render_metric_card("总列数 (Total)", str(len(df.columns)), "特征总数", "neutral")