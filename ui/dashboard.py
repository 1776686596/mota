"""交互式数据仪表盘组件

提供炫酷的数据概览和统计可视化
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional


def render_dashboard(df: pd.DataFrame, metadata: dict):
    """渲染交互式数据仪表盘
    
    Args:
        df: 数据框
        metadata: 数据元信息
    """
    st.markdown("### 📊 数据仪表盘 (Data Dashboard)")
    st.markdown("实时数据洞察，一目了然的统计概览")
    
    # 顶部：关键指标卡片
    _render_key_metrics(df, metadata)
    
    st.markdown("---")
    
    # 中部：数据分布可视化
    col1, col2 = st.columns(2)
    
    with col1:
        _render_data_distribution_chart(df)
    
    with col2:
        _render_data_quality_radar(df, metadata)
    
    st.markdown("---")
    
    # 底部：详细分析
    _render_detailed_analysis(df, metadata)


def _render_key_metrics(df: pd.DataFrame, metadata: dict):
    """渲染关键指标卡片（4个核心指标）"""
    
    # 计算关键指标
    total_rows = metadata['shape'][0]
    total_cols = metadata['shape'][1]
    numeric_cols = len(df.select_dtypes(include=['number']).columns)
    categorical_cols = len(df.select_dtypes(include=['object']).columns)
    
    # 数据完整度
    total_cells = total_rows * total_cols
    missing_cells = df.isnull().sum().sum()
    completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
    
    # 数据密度（非零值占比）
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        non_zero_count = (numeric_df != 0).sum().sum()
        total_numeric_cells = numeric_df.shape[0] * numeric_df.shape[1]
        density = (non_zero_count / total_numeric_cells * 100) if total_numeric_cells > 0 else 0
    else:
        density = 0
    
    # 使用自定义 HTML 卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        _render_animated_metric_card(
            "数据规模",
            f"{total_rows:,}",
            "行数据记录",
            "📊",
            "#5e6ad2"
        )
    
    with col2:
        _render_animated_metric_card(
            "特征维度",
            f"{total_cols}",
            f"{numeric_cols} 数值 + {categorical_cols} 分类",
            "🔢",
            "#8b5cf6"
        )
    
    with col3:
        _render_animated_metric_card(
            "数据完整度",
            f"{completeness:.1f}%",
            f"缺失 {missing_cells} 个值",
            "✅" if completeness > 95 else "⚠️",
            "#22c55e" if completeness > 95 else "#f59e0b"
        )
    
    with col4:
        _render_animated_metric_card(
            "数据密度",
            f"{density:.1f}%",
            "非零值占比",
            "📈",
            "#d946ef"
        )


def _render_animated_metric_card(label: str, value: str, subtitle: str, icon: str, color: str):
    """渲染带动画效果的指标卡片"""
    html = f"""
    <div class="dashboard-metric-card" style="--card-color: {color};">
        <div class="metric-icon">{icon}</div>
        <div class="metric-content">
            <div class="metric-label-dash">{label}</div>
            <div class="metric-value-dash">{value}</div>
            <div class="metric-subtitle">{subtitle}</div>
        </div>
        <div class="metric-glow"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def _render_data_distribution_chart(df: pd.DataFrame):
    """渲染数据分布图表（数值列分布）"""
    st.markdown("#### 📈 数值特征分布")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.info("暂无数值类型列")
        return
    
    # 选择要展示的列（最多前5个）
    selected_cols = numeric_cols[:5]
    
    # 创建 Plotly 箱线图
    fig = go.Figure()
    
    for col in selected_cols:
        fig.add_trace(go.Box(
            y=df[col].dropna(),
            name=col,
            boxmean='sd',
            marker_color='rgba(94, 106, 210, 0.6)',
            line=dict(color='rgba(94, 106, 210, 1)', width=2)
        ))
    
    fig.update_layout(
        showlegend=True,
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17,17,17,0.5)',
        font=dict(color='#fafafa', size=11),
        xaxis=dict(
            showgrid=False,
            color='#d4d4d4'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            color='#d4d4d4'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def _render_data_quality_radar(df: pd.DataFrame, metadata: dict):
    """渲染数据质量雷达图"""
    st.markdown("#### 🎯 数据质量评分")
    
    # 计算各维度评分
    total_cells = metadata['shape'][0] * metadata['shape'][1]
    missing_cells = df.isnull().sum().sum()
    completeness_score = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
    
    # 数据一致性（数值列的标准差/均值，越小越一致）
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        cv_scores = []
        for col in numeric_df.columns:
            mean_val = numeric_df[col].mean()
            std_val = numeric_df[col].std()
            if mean_val != 0 and not pd.isna(mean_val) and not pd.isna(std_val):
                cv = abs(std_val / mean_val)
                # 转换为评分（CV越小，评分越高）
                consistency = max(0, 100 - min(cv * 10, 100))
                cv_scores.append(consistency)
        consistency_score = np.mean(cv_scores) if cv_scores else 50
    else:
        consistency_score = 50
    
    # 数据丰富度（列数/理想列数的比例）
    richness_score = min(metadata['shape'][1] / 10 * 100, 100)
    
    # 数据规模评分
    scale_score = min(metadata['shape'][0] / 1000 * 100, 100)
    
    # 数据类型多样性
    type_diversity = len(metadata.get('dtypes', {}))
    diversity_score = min(type_diversity / 5 * 100, 100)
    
    # 创建雷达图
    categories = ['完整度', '一致性', '丰富度', '规模', '多样性']
    scores = [completeness_score, consistency_score, richness_score, scale_score, diversity_score]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(94, 106, 210, 0.3)',
        line=dict(color='rgba(94, 106, 210, 1)', width=2),
        marker=dict(size=8, color='rgba(139, 92, 246, 1)'),
        name='质量评分'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.1)',
                color='#737373'
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                color='#fafafa'
            ),
            bgcolor='rgba(17,17,17,0.5)'
        ),
        showlegend=False,
        height=300,
        margin=dict(l=50, r=50, t=30, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fafafa', size=11)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 显示综合评分
    overall_score = np.mean(scores)
    score_color = "#22c55e" if overall_score >= 80 else "#f59e0b" if overall_score >= 60 else "#ef4444"
    st.markdown(f"""
        <div style="text-align: center; margin-top: 1rem;">
            <span style="font-size: 0.875rem; color: #a1a1a1;">综合评分</span><br>
            <span style="font-size: 2rem; font-weight: 700; color: {score_color};">{overall_score:.0f}</span>
            <span style="font-size: 1rem; color: #737373;">/100</span>
        </div>
    """, unsafe_allow_html=True)


def _render_detailed_analysis(df: pd.DataFrame, metadata: dict):
    """渲染详细分析部分"""
    tab1, tab2, tab3 = st.tabs(["📊 列统计", "🔗 相关性热图", "📈 趋势分析"])
    
    with tab1:
        _render_column_statistics(df)
    
    with tab2:
        _render_correlation_heatmap(df)
    
    with tab3:
        _render_trend_analysis(df)


def _render_column_statistics(df: pd.DataFrame):
    """渲染列统计信息"""
    st.markdown("##### 各列详细统计")
    
    stats_data = []
    for col in df.columns:
        col_type = str(df[col].dtype)
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df) * 100) if len(df) > 0 else 0
        unique_count = df[col].nunique()
        
        if df[col].dtype in ['int64', 'float64']:
            mean_val = df[col].mean()
            std_val = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()
            stats = f"均值: {mean_val:.2f}, 标准差: {std_val:.2f}, 范围: [{min_val:.2f}, {max_val:.2f}]"
        else:
            top_value = df[col].mode()[0] if not df[col].mode().empty else "N/A"
            stats = f"最常见: {top_value}, 唯一值: {unique_count}"
        
        stats_data.append({
            "列名": col,
            "类型": col_type,
            "缺失": f"{missing_count} ({missing_pct:.1f}%)",
            "统计信息": stats
        })
    
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)


def _render_correlation_heatmap(df: pd.DataFrame):
    """渲染相关性热图"""
    st.markdown("##### 数值特征相关性矩阵")
    
    numeric_df = df.select_dtypes(include=['number'])
    
    if numeric_df.shape[1] < 2:
        st.info("需要至少2个数值列才能计算相关性")
        return
    
    # 计算相关性矩阵
    corr_matrix = numeric_df.corr()
    
    # 创建热图
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu_r',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(
            title=dict(text="相关系数", side="right"),
            tickmode="linear",
            tick0=-1,
            dtick=0.5
        )
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17,17,17,0.5)',
        font=dict(color='#fafafa', size=10),
        xaxis=dict(side='bottom', color='#fafafa'),
        yaxis=dict(color='#fafafa')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def _render_trend_analysis(df: pd.DataFrame):
    """渲染趋势分析"""
    st.markdown("##### 数据趋势可视化")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.info("暂无数值类型列")
        return
    
    # 选择要分析的列
    selected_col = st.selectbox("选择要分析的列", numeric_cols, key="trend_col")
    
    if selected_col:
        # 创建趋势图
        fig = go.Figure()
        
        # 原始数据
        fig.add_trace(go.Scatter(
            y=df[selected_col],
            mode='lines',
            name='原始数据',
            line=dict(color='rgba(94, 106, 210, 0.6)', width=1),
            fill='tozeroy',
            fillcolor='rgba(94, 106, 210, 0.1)'
        ))
        
        # 移动平均（如果数据足够）
        if len(df) > 10:
            window_size = min(20, len(df) // 5)
            moving_avg = df[selected_col].rolling(window=window_size, center=True).mean()
            fig.add_trace(go.Scatter(
                y=moving_avg,
                mode='lines',
                name=f'移动平均 (窗口={window_size})',
                line=dict(color='rgba(217, 70, 239, 1)', width=2)
            ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(17,17,17,0.5)',
            font=dict(color='#fafafa', size=11),
            xaxis=dict(
                title="索引",
                gridcolor='rgba(255,255,255,0.1)',
                color='#737373'
            ),
            yaxis=dict(
                title=selected_col,
                gridcolor='rgba(255,255,255,0.1)',
                color='#737373'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # 统计摘要
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("平均值", f"{df[selected_col].mean():.2f}")
        with col2:
            st.metric("中位数", f"{df[selected_col].median():.2f}")
        with col3:
            st.metric("标准差", f"{df[selected_col].std():.2f}")
        with col4:
            st.metric("变异系数", f"{(df[selected_col].std() / df[selected_col].mean() * 100):.1f}%")


# 添加仪表盘样式到全局样式中
def add_dashboard_styles():
    """添加仪表盘专用样式"""
    st.markdown("""
        <style>
        /* 仪表盘指标卡片 */
        .dashboard-metric-card {
            position: relative;
            background: linear-gradient(135deg, rgba(17, 17, 17, 0.9) 0%, rgba(23, 23, 23, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }
        
        .dashboard-metric-card:hover {
            transform: translateY(-4px) scale(1.02);
            border-color: var(--card-color);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 
                        0 0 20px var(--card-color);
        }
        
        .dashboard-metric-card:hover .metric-glow {
            opacity: 1;
        }
        
        .metric-glow {
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, var(--card-color) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
            z-index: 0;
        }
        
        .metric-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            filter: drop-shadow(0 0 10px var(--card-color));
            position: relative;
            z-index: 1;
        }
        
        .metric-content {
            position: relative;
            z-index: 1;
        }
        
        .metric-label-dash {
            font-size: 0.75rem;
            font-weight: 600;
            color: #a1a1a1;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }
        
        .metric-value-dash {
            font-size: 2.25rem;
            font-weight: 800;
            color: #fafafa;
            letter-spacing: -0.02em;
            line-height: 1;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--card-color) 0%, #fafafa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .metric-subtitle {
            font-size: 0.75rem;
            color: #737373;
            font-weight: 500;
        }
        
        /* 动画效果 */
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .dashboard-metric-card {
            animation: slideInUp 0.5s ease-out;
        }
        
        .dashboard-metric-card:nth-child(1) { animation-delay: 0.1s; }
        .dashboard-metric-card:nth-child(2) { animation-delay: 0.2s; }
        .dashboard-metric-card:nth-child(3) { animation-delay: 0.3s; }
        .dashboard-metric-card:nth-child(4) { animation-delay: 0.4s; }
        </style>
    """, unsafe_allow_html=True)