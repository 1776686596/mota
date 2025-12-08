"""统计分析标签页 UI 组件

提供假设检验、回归分析、相关性分析等统计功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import io

# 导入统一的字体配置（必须在 matplotlib.pyplot 之前）
from utils.font_config import setup_chinese_font, CHINESE_FONTS

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# 统计库
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau

# 确保字体设置生效
setup_chinese_font()


def render_statistics_tab():
    """渲染统计分析标签页"""
    st.markdown("### 📊 统计分析工具")
    st.markdown("进行假设检验、回归分析、相关性分析等统计操作")
    
    if st.session_state.df is None:
        st.warning("⚠️ 请先在「智能绘图工作室」中上传数据")
        return
    
    df = st.session_state.df
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 假设检验",
        "📈 回归分析", 
        "🔗 相关性分析",
        "📊 描述统计"
    ])
    
    with tab1:
        _render_hypothesis_testing(df)
    
    with tab2:
        _render_regression_analysis(df)
    
    with tab3:
        _render_correlation_analysis(df)
    
    with tab4:
        _render_descriptive_statistics(df)


def _display_test_result(test_name: str, statistic: float, p_value: float, additional_info: dict = None):
    """显示检验结果"""
    st.markdown("---")
    st.markdown(f"### 📋 {test_name} 结果")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("检验统计量", f"{statistic:.4f}")
    with col2:
        st.metric("p 值", f"{p_value:.4f}")
    with col3:
        if p_value < 0.05:
            st.success(f"✅ 显著 (α=0.05)")
        else:
            st.info(f"❌ 不显著 (α=0.05)")
    
    if p_value < 0.001:
        conclusion = "存在极显著差异 (p < 0.001)"
    elif p_value < 0.01:
        conclusion = "存在高度显著差异 (p < 0.01)"
    elif p_value < 0.05:
        conclusion = "存在显著差异 (p < 0.05)"
    else:
        conclusion = "差异不显著 (p ≥ 0.05)"
    
    st.info(f"📊 {conclusion}")
    
    if additional_info:
        with st.expander("📈 详细信息"):
            for key, value in additional_info.items():
                st.write(f"**{key}**: {value}")


def _render_hypothesis_testing(df: pd.DataFrame):
    """渲染假设检验界面"""
    st.markdown("#### 假设检验")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not numeric_cols:
        st.warning("⚠️ 数据中没有数值列")
        return
    
    test_type = st.selectbox(
        "选择检验类型",
        options=[
            "单样本 t 检验",
            "独立样本 t 检验",
            "配对样本 t 检验",
            "单因素方差分析 (ANOVA)",
            "正态性检验 (Shapiro-Wilk)",
            "Mann-Whitney U 检验"
        ],
        key="test_type"
    )
    
    st.divider()
    
    if test_type == "单样本 t 检验":
        col1, col2 = st.columns(2)
        with col1:
            test_col = st.selectbox("选择检验变量", options=numeric_cols, key="one_sample_col")
        with col2:
            pop_mean = st.number_input("总体均值假设", value=0.0, key="pop_mean")
        
        if st.button("🔬 执行检验", key="run_one_sample"):
            data = df[test_col].dropna()
            t_stat, p_value = stats.ttest_1samp(data, pop_mean)
            _display_test_result("单样本 t 检验", t_stat, p_value, {
                "样本均值": f"{data.mean():.4f}",
                "样本标准差": f"{data.std():.4f}",
                "样本量": len(data)
            })
    
    elif test_type == "独立样本 t 检验":
        if not cat_cols:
            st.warning("⚠️ 需要分类变量来分组")
            return
        col1, col2 = st.columns(2)
        with col1:
            test_col = st.selectbox("选择检验变量", options=numeric_cols, key="ind_test_col")
        with col2:
            group_col = st.selectbox("选择分组变量", options=cat_cols, key="ind_group_col")
        
        groups = df[group_col].unique()
        if len(groups) < 2:
            st.warning("⚠️ 分组变量需要至少 2 个类别")
            return
        
        if len(groups) > 2:
            selected_groups = st.multiselect("选择两个分组", options=groups.tolist(), max_selections=2)
            if len(selected_groups) != 2:
                st.info("请选择恰好 2 个分组")
                return
            groups = selected_groups
        
        if st.button("🔬 执行检验", key="run_ind_ttest"):
            group1 = df[df[group_col] == groups[0]][test_col].dropna()
            group2 = df[df[group_col] == groups[1]][test_col].dropna()
            t_stat, p_value = stats.ttest_ind(group1, group2)
            _display_test_result("独立样本 t 检验", t_stat, p_value, {
                f"组 {groups[0]} 均值": f"{group1.mean():.4f}",
                f"组 {groups[1]} 均值": f"{group2.mean():.4f}"
            })
    
    elif test_type == "配对样本 t 检验":
        if len(numeric_cols) < 2:
            st.warning("⚠️ 需要至少 2 个数值变量")
            return
        col1, col2 = st.columns(2)
        with col1:
            var1 = st.selectbox("选择变量 1", options=numeric_cols, key="paired_var1")
        with col2:
            var2 = st.selectbox("选择变量 2", options=[c for c in numeric_cols if c != var1], key="paired_var2")
        
        if st.button("🔬 执行检验", key="run_paired"):
            data1 = df[var1].dropna()
            data2 = df[var2].dropna()
            min_len = min(len(data1), len(data2))
            t_stat, p_value = stats.ttest_rel(data1[:min_len], data2[:min_len])
            _display_test_result("配对样本 t 检验", t_stat, p_value, {
                f"{var1} 均值": f"{data1.mean():.4f}",
                f"{var2} 均值": f"{data2.mean():.4f}"
            })
    
    elif test_type == "单因素方差分析 (ANOVA)":
        if not cat_cols:
            st.warning("⚠️ 需要分类变量作为因子")
            return
        col1, col2 = st.columns(2)
        with col1:
            test_col = st.selectbox("选择因变量", options=numeric_cols, key="anova_test_col")
        with col2:
            factor_col = st.selectbox("选择因子", options=cat_cols, key="anova_factor")
        
        if st.button("🔬 执行检验", key="run_anova"):
            groups = [group[test_col].dropna().values for name, group in df.groupby(factor_col)]
            f_stat, p_value = stats.f_oneway(*groups)
            _display_test_result("单因素方差分析", f_stat, p_value, {"组数": len(groups)})
            
            st.markdown("**各组描述统计**")
            group_stats = df.groupby(factor_col)[test_col].agg(['count', 'mean', 'std'])
            group_stats.columns = ['样本量', '均值', '标准差']
            st.dataframe(group_stats, use_container_width=True)
    
    elif test_type == "正态性检验 (Shapiro-Wilk)":
        test_col = st.selectbox("选择检验变量", options=numeric_cols, key="norm_col")
        if st.button("🔬 执行检验", key="run_norm"):
            data = df[test_col].dropna()
            if len(data) > 5000:
                data = data.sample(5000, random_state=42)
                st.info("样本量超过 5000，已随机抽取 5000 个样本")
            stat, p_value = stats.shapiro(data)
            _display_test_result("Shapiro-Wilk 正态性检验", stat, p_value, {
                "偏度": f"{stats.skew(data):.4f}",
                "峰度": f"{stats.kurtosis(data):.4f}"
            })
    
    elif test_type == "Mann-Whitney U 检验":
        if not cat_cols:
            st.warning("⚠️ 需要分类变量来分组")
            return
        col1, col2 = st.columns(2)
        with col1:
            test_col = st.selectbox("选择检验变量", options=numeric_cols, key="mw_test_col")
        with col2:
            group_col = st.selectbox("选择分组变量", options=cat_cols, key="mw_group_col")
        
        groups = df[group_col].unique()
        if len(groups) != 2:
            st.warning("⚠️ 需要恰好 2 个分组")
            return
        
        if st.button("🔬 执行检验", key="run_mw"):
            group1 = df[df[group_col] == groups[0]][test_col].dropna()
            group2 = df[df[group_col] == groups[1]][test_col].dropna()
            stat, p_value = stats.mannwhitneyu(group1, group2)
            _display_test_result("Mann-Whitney U 检验", stat, p_value, {
                f"组 {groups[0]} 中位数": f"{group1.median():.4f}",
                f"组 {groups[1]} 中位数": f"{group2.median():.4f}"
            })


def _render_regression_analysis(df: pd.DataFrame):
    """渲染回归分析界面"""
    st.markdown("#### 回归分析")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("⚠️ 需要至少 2 个数值变量")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        y_col = st.selectbox("选择因变量 (Y)", options=numeric_cols, key="reg_y")
    with col2:
        x_options = [c for c in numeric_cols if c != y_col]
        x_cols = st.multiselect("选择自变量 (X)", options=x_options, default=[x_options[0]] if x_options else [], key="reg_x")
    
    if not x_cols:
        st.warning("⚠️ 请选择至少一个自变量")
        return
    
    if st.button("📈 执行回归分析", key="run_regression"):
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score, mean_squared_error
        
        data = df[[y_col] + x_cols].dropna()
        X = data[x_cols].values
        y = data[y_col].values
        
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        st.markdown("### 📊 回归分析结果")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("R²", f"{r2:.4f}")
        with col2:
            st.metric("RMSE", f"{rmse:.4f}")
        with col3:
            st.metric("样本量", len(y))
        
        st.markdown("**回归系数**")
        coef_df = pd.DataFrame({
            '变量': ['截距'] + x_cols,
            '系数': [model.intercept_] + list(model.coef_)
        })
        st.dataframe(coef_df, use_container_width=True, hide_index=True)
        
        # 回归方程
        equation = f"{y_col} = {model.intercept_:.4f}"
        for i, col in enumerate(x_cols):
            coef = model.coef_[i]
            equation += f" + {coef:.4f}×{col}" if coef >= 0 else f" - {abs(coef):.4f}×{col}"
        st.code(equation)
        
        # 可视化（单变量）
        if len(x_cols) == 1:
            # 确保中文字体设置
            setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(data[x_cols[0]], data[y_col], alpha=0.6, label='数据点')
            ax.plot(data[x_cols[0]], y_pred, color='red', linewidth=2, label='回归线')
            ax.set_xlabel(x_cols[0])
            ax.set_ylabel(y_col)
            ax.set_title(f'线性回归: {y_col} vs {x_cols[0]}')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            st.image(buf, use_container_width=True)


def _render_correlation_analysis(df: pd.DataFrame):
    """渲染相关性分析界面"""
    st.markdown("#### 相关性分析")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("⚠️ 需要至少 2 个数值变量")
        return
    
    corr_type = st.selectbox(
        "相关系数类型",
        options=["Pearson (线性相关)", "Spearman (秩相关)", "Kendall (等级相关)"],
        key="corr_type"
    )
    
    selected_cols = st.multiselect(
        "选择分析变量",
        options=numeric_cols,
        default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols,
        key="corr_cols"
    )
    
    if len(selected_cols) < 2:
        st.warning("⚠️ 请选择至少 2 个变量")
        return
    
    if st.button("🔗 计算相关性", key="run_corr"):
        method = 'pearson' if "Pearson" in corr_type else ('spearman' if "Spearman" in corr_type else 'kendall')
        corr_matrix = df[selected_cols].corr(method=method)
        
        st.markdown("### 📊 相关系数矩阵")
        
        # 确保中文字体设置
        setup_chinese_font()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='RdBu_r', center=0, square=True, ax=ax)
        ax.set_title(f'{corr_type} 相关系数矩阵', fontsize=14)
        plt.tight_layout()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        st.image(buf, use_container_width=True)
        
        # 显示强相关对
        st.markdown("**显著相关对 (|r| > 0.5)**")
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                r = corr_matrix.iloc[i, j]
                if abs(r) > 0.5:
                    strong_corr.append({
                        '变量 1': corr_matrix.columns[i],
                        '变量 2': corr_matrix.columns[j],
                        '相关系数': f"{r:.4f}"
                    })
        
        if strong_corr:
            st.dataframe(pd.DataFrame(strong_corr), use_container_width=True, hide_index=True)
        else:
            st.info("未发现强相关关系")


def _render_descriptive_statistics(df: pd.DataFrame):
    """渲染描述统计界面"""
    st.markdown("#### 描述统计")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("⚠️ 数据中没有数值列")
        return
    
    selected_cols = st.multiselect(
        "选择分析变量",
        options=numeric_cols,
        default=numeric_cols,
        key="desc_cols"
    )
    
    if not selected_cols:
        return
    
    # 基础统计
    st.markdown("### 📊 基础统计量")
    desc_stats = df[selected_cols].describe().T
    desc_stats['median'] = df[selected_cols].median()
    desc_stats['skew'] = df[selected_cols].skew()
    desc_stats['kurtosis'] = df[selected_cols].kurtosis()
    desc_stats = desc_stats[['count', 'mean', 'median', 'std', 'min', '25%', '50%', '75%', 'max', 'skew', 'kurtosis']]
    desc_stats.columns = ['计数', '均值', '中位数', '标准差', '最小值', '25%', '50%', '75%', '最大值', '偏度', '峰度']
    st.dataframe(desc_stats.round(4), use_container_width=True)
    
    # 分布可视化
    st.markdown("### 📈 分布可视化")
    
    plot_col = st.selectbox("选择可视化变量", options=selected_cols, key="dist_plot_col")
    
    col1, col2 = st.columns(2)
    
    # 确保中文字体设置
    setup_chinese_font()
    
    with col1:
        # 直方图
        fig, ax = plt.subplots(figsize=(8, 5))
        data = df[plot_col].dropna()
        ax.hist(data, bins=30, edgecolor='white', alpha=0.7)
        ax.axvline(data.mean(), color='red', linestyle='--', label=f'均值: {data.mean():.2f}')
        ax.axvline(data.median(), color='green', linestyle='--', label=f'中位数: {data.median():.2f}')
        ax.set_xlabel(plot_col)
        ax.set_ylabel('频数')
        ax.set_title(f'{plot_col} 分布直方图')
        ax.legend()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        st.image(buf, use_container_width=True)
    
    with col2:
        # 箱线图
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.boxplot(data, vert=True)
        ax.set_ylabel(plot_col)
        ax.set_title(f'{plot_col} 箱线图')
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        st.image(buf, use_container_width=True)