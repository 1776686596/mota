"""数据预处理工具模块

提供数据清洗、转换、筛选等功能
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional, Tuple


def render_data_preprocessing(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """渲染数据预处理工具面板
    
    Args:
        df: 原始数据 DataFrame
        
    Returns:
        处理后的 DataFrame，如果没有修改则返回 None
    """
    st.markdown("### 🔧 数据预处理工具")
    st.markdown("对数据进行清洗、转换和筛选操作")
    
    # 创建处理后的数据副本
    if "processed_df" not in st.session_state or st.session_state.get("_preprocessing_reset"):
        st.session_state.processed_df = df.copy()
        st.session_state._preprocessing_reset = False
    
    processed_df = st.session_state.processed_df
    
    # 使用 tabs 组织不同的预处理功能
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧹 缺失值处理", 
        "🔄 数据转换", 
        "🎯 数据筛选",
        "📊 数据采样"
    ])
    
    with tab1:
        processed_df = _render_missing_value_handler(processed_df)
    
    with tab2:
        processed_df = _render_data_transformer(processed_df)
    
    with tab3:
        processed_df = _render_data_filter(processed_df)
    
    with tab4:
        processed_df = _render_data_sampler(processed_df)
    
    # 显示处理前后对比
    st.divider()
    _render_comparison(df, processed_df)
    
    # 操作按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ 应用更改", type="primary", use_container_width=True):
            st.session_state.df = processed_df
            st.session_state.processed_df = processed_df
            # 更新元数据
            from core.data_loader import extract_metadata
            st.session_state.metadata = extract_metadata(processed_df)
            st.success("✅ 数据已更新！")
            st.rerun()
    
    with col2:
        if st.button("🔄 重置更改", use_container_width=True):
            st.session_state.processed_df = df.copy()
            st.session_state._preprocessing_reset = True
            st.rerun()
    
    with col3:
        # 下载处理后的数据
        csv_data = processed_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ 下载处理后数据",
            csv_data,
            "processed_data.csv",
            "text/csv",
            use_container_width=True
        )
    
    return processed_df


def _render_missing_value_handler(df: pd.DataFrame) -> pd.DataFrame:
    """渲染缺失值处理界面"""
    st.markdown("#### 处理缺失值")
    
    # 显示缺失值统计
    missing_stats = df.isnull().sum()
    missing_cols = missing_stats[missing_stats > 0]
    
    if len(missing_cols) == 0:
        st.success("✅ 数据中没有缺失值")
        return df
    
    # 显示缺失值信息
    st.warning(f"⚠️ 发现 {len(missing_cols)} 列存在缺失值")
    
    missing_info = pd.DataFrame({
        '列名': missing_cols.index,
        '缺失数量': missing_cols.values,
        '缺失比例': (missing_cols.values / len(df) * 100).round(2)
    })
    missing_info['缺失比例'] = missing_info['缺失比例'].astype(str) + '%'
    st.dataframe(missing_info, use_container_width=True, hide_index=True)
    
    # 选择处理方式
    col1, col2 = st.columns(2)
    
    with col1:
        selected_col = st.selectbox(
            "选择要处理的列",
            options=missing_cols.index.tolist(),
            key="missing_col_select"
        )
    
    with col2:
        fill_method = st.selectbox(
            "填充方式",
            options=["删除缺失行", "均值填充", "中位数填充", "众数填充", "前值填充", "后值填充", "自定义值"],
            key="fill_method_select"
        )
    
    # 自定义值输入
    custom_value = None
    if fill_method == "自定义值":
        custom_value = st.text_input("输入填充值", key="custom_fill_value")
    
    # 应用填充
    if st.button("🔧 应用填充", key="apply_fill"):
        df = df.copy()
        
        if fill_method == "删除缺失行":
            df = df.dropna(subset=[selected_col])
            st.success(f"✅ 已删除 {selected_col} 列的缺失行")
        elif fill_method == "均值填充":
            if df[selected_col].dtype in ['int64', 'float64']:
                df[selected_col] = df[selected_col].fillna(df[selected_col].mean())
                st.success(f"✅ 已用均值填充 {selected_col} 列")
            else:
                st.error("❌ 均值填充仅适用于数值列")
        elif fill_method == "中位数填充":
            if df[selected_col].dtype in ['int64', 'float64']:
                df[selected_col] = df[selected_col].fillna(df[selected_col].median())
                st.success(f"✅ 已用中位数填充 {selected_col} 列")
            else:
                st.error("❌ 中位数填充仅适用于数值列")
        elif fill_method == "众数填充":
            mode_val = df[selected_col].mode()
            if len(mode_val) > 0:
                df[selected_col] = df[selected_col].fillna(mode_val[0])
                st.success(f"✅ 已用众数填充 {selected_col} 列")
            else:
                st.error("❌ 无法计算众数")
        elif fill_method == "前值填充":
            df[selected_col] = df[selected_col].fillna(method='ffill')
            st.success(f"✅ 已用前值填充 {selected_col} 列")
        elif fill_method == "后值填充":
            df[selected_col] = df[selected_col].fillna(method='bfill')
            st.success(f"✅ 已用后值填充 {selected_col} 列")
        elif fill_method == "自定义值" and custom_value:
            try:
                # 尝试转换为数值
                if df[selected_col].dtype in ['int64', 'float64']:
                    custom_value = float(custom_value)
                df[selected_col] = df[selected_col].fillna(custom_value)
                st.success(f"✅ 已用自定义值填充 {selected_col} 列")
            except ValueError:
                st.error("❌ 自定义值格式不正确")
        
        st.session_state.processed_df = df
    
    return st.session_state.processed_df


def _render_data_transformer(df: pd.DataFrame) -> pd.DataFrame:
    """渲染数据转换界面"""
    st.markdown("#### 数据转换")
    
    col1, col2 = st.columns(2)
    
    with col1:
        transform_type = st.selectbox(
            "转换类型",
            options=["数据类型转换", "数值标准化", "数值归一化", "对数转换", "独热编码"],
            key="transform_type"
        )
    
    with col2:
        if transform_type in ["数据类型转换", "数值标准化", "数值归一化", "对数转换"]:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            all_cols = df.columns.tolist()
            
            if transform_type == "数据类型转换":
                selected_col = st.selectbox("选择列", options=all_cols, key="transform_col")
            else:
                selected_col = st.selectbox("选择列", options=numeric_cols, key="transform_col")
        elif transform_type == "独热编码":
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            selected_col = st.selectbox("选择列", options=cat_cols, key="transform_col")
    
    # 数据类型转换的目标类型
    target_dtype = None
    if transform_type == "数据类型转换":
        target_dtype = st.selectbox(
            "目标类型",
            options=["int64", "float64", "str", "category", "datetime"],
            key="target_dtype"
        )
    
    if st.button("🔄 执行转换", key="apply_transform"):
        df = df.copy()
        
        try:
            if transform_type == "数据类型转换":
                if target_dtype == "datetime":
                    df[selected_col] = pd.to_datetime(df[selected_col])
                elif target_dtype == "category":
                    df[selected_col] = df[selected_col].astype('category')
                else:
                    df[selected_col] = df[selected_col].astype(target_dtype)
                st.success(f"✅ 已将 {selected_col} 转换为 {target_dtype}")
                
            elif transform_type == "数值标准化":
                mean_val = df[selected_col].mean()
                std_val = df[selected_col].std()
                df[f"{selected_col}_标准化"] = (df[selected_col] - mean_val) / std_val
                st.success(f"✅ 已创建标准化列 {selected_col}_标准化")
                
            elif transform_type == "数值归一化":
                min_val = df[selected_col].min()
                max_val = df[selected_col].max()
                df[f"{selected_col}_归一化"] = (df[selected_col] - min_val) / (max_val - min_val)
                st.success(f"✅ 已创建归一化列 {selected_col}_归一化")
                
            elif transform_type == "对数转换":
                if (df[selected_col] > 0).all():
                    df[f"{selected_col}_log"] = np.log(df[selected_col])
                    st.success(f"✅ 已创建对数转换列 {selected_col}_log")
                else:
                    st.error("❌ 对数转换要求所有值大于 0")
                    
            elif transform_type == "独热编码":
                dummies = pd.get_dummies(df[selected_col], prefix=selected_col)
                df = pd.concat([df, dummies], axis=1)
                st.success(f"✅ 已对 {selected_col} 进行独热编码")
            
            st.session_state.processed_df = df
            
        except Exception as e:
            st.error(f"❌ 转换失败: {str(e)}")
    
    return st.session_state.processed_df


def _render_data_filter(df: pd.DataFrame) -> pd.DataFrame:
    """渲染数据筛选界面"""
    st.markdown("#### 数据筛选")
    
    # 列筛选
    st.markdown("**选择保留的列**")
    all_cols = df.columns.tolist()
    selected_cols = st.multiselect(
        "选择要保留的列",
        options=all_cols,
        default=all_cols,
        key="filter_cols"
    )
    
    st.divider()
    
    # 行筛选
    st.markdown("**条件筛选**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_col = st.selectbox("筛选列", options=all_cols, key="filter_row_col")
    
    with col2:
        if df[filter_col].dtype in ['int64', 'float64']:
            operators = ["等于", "不等于", "大于", "小于", "大于等于", "小于等于", "介于"]
        else:
            operators = ["等于", "不等于", "包含", "不包含"]
        filter_op = st.selectbox("条件", options=operators, key="filter_op")
    
    with col3:
        if filter_op == "介于":
            filter_val1 = st.number_input("最小值", key="filter_val1")
            filter_val2 = st.number_input("最大值", key="filter_val2")
        elif df[filter_col].dtype in ['int64', 'float64']:
            filter_val = st.number_input("值", key="filter_val")
        else:
            unique_vals = df[filter_col].unique().tolist()
            if len(unique_vals) <= 20:
                filter_val = st.selectbox("值", options=unique_vals, key="filter_val")
            else:
                filter_val = st.text_input("值", key="filter_val")
    
    if st.button("🎯 应用筛选", key="apply_filter"):
        df = df.copy()
        
        # 应用列筛选
        if selected_cols:
            df = df[selected_cols]
        
        # 应用行筛选
        try:
            if filter_op == "等于":
                df = df[df[filter_col] == filter_val]
            elif filter_op == "不等于":
                df = df[df[filter_col] != filter_val]
            elif filter_op == "大于":
                df = df[df[filter_col] > filter_val]
            elif filter_op == "小于":
                df = df[df[filter_col] < filter_val]
            elif filter_op == "大于等于":
                df = df[df[filter_col] >= filter_val]
            elif filter_op == "小于等于":
                df = df[df[filter_col] <= filter_val]
            elif filter_op == "介于":
                df = df[(df[filter_col] >= filter_val1) & (df[filter_col] <= filter_val2)]
            elif filter_op == "包含":
                df = df[df[filter_col].astype(str).str.contains(str(filter_val), na=False)]
            elif filter_op == "不包含":
                df = df[~df[filter_col].astype(str).str.contains(str(filter_val), na=False)]
            
            st.success(f"✅ 筛选完成，剩余 {len(df)} 行数据")
            st.session_state.processed_df = df
            
        except Exception as e:
            st.error(f"❌ 筛选失败: {str(e)}")
    
    return st.session_state.processed_df


def _render_data_sampler(df: pd.DataFrame) -> pd.DataFrame:
    """渲染数据采样界面"""
    st.markdown("#### 数据采样")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sample_method = st.selectbox(
            "采样方式",
            options=["随机采样", "头部数据", "尾部数据", "等间隔采样", "分层采样"],
            key="sample_method"
        )
    
    with col2:
        if sample_method in ["随机采样", "分层采样"]:
            sample_size = st.slider(
                "采样比例 (%)",
                min_value=1,
                max_value=100,
                value=50,
                key="sample_size"
            )
        else:
            sample_n = st.number_input(
                "采样数量",
                min_value=1,
                max_value=len(df),
                value=min(100, len(df)),
                key="sample_n"
            )
    
    # 分层采样的分组列
    stratify_col = None
    if sample_method == "分层采样":
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            stratify_col = st.selectbox("分层依据列", options=cat_cols, key="stratify_col")
        else:
            st.warning("⚠️ 没有可用于分层的分类列")
    
    if st.button("📊 执行采样", key="apply_sample"):
        df = df.copy()
        
        try:
            if sample_method == "随机采样":
                n_samples = int(len(df) * sample_size / 100)
                df = df.sample(n=n_samples, random_state=42)
                st.success(f"✅ 随机采样完成，获得 {len(df)} 行数据")
                
            elif sample_method == "头部数据":
                df = df.head(sample_n)
                st.success(f"✅ 获取头部 {len(df)} 行数据")
                
            elif sample_method == "尾部数据":
                df = df.tail(sample_n)
                st.success(f"✅ 获取尾部 {len(df)} 行数据")
                
            elif sample_method == "等间隔采样":
                step = max(1, len(df) // sample_n)
                df = df.iloc[::step].head(sample_n)
                st.success(f"✅ 等间隔采样完成，获得 {len(df)} 行数据")
                
            elif sample_method == "分层采样" and stratify_col:
                from sklearn.model_selection import train_test_split
                _, df = train_test_split(
                    df, 
                    test_size=sample_size/100, 
                    stratify=df[stratify_col],
                    random_state=42
                )
                st.success(f"✅ 分层采样完成，获得 {len(df)} 行数据")
            
            st.session_state.processed_df = df
            
        except Exception as e:
            st.error(f"❌ 采样失败: {str(e)}")
    
    return st.session_state.processed_df


def _render_comparison(original_df: pd.DataFrame, processed_df: pd.DataFrame):
    """渲染处理前后对比"""
    st.markdown("#### 📈 处理前后对比")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        row_change = len(processed_df) - len(original_df)
        delta_color = "normal" if row_change == 0 else ("inverse" if row_change < 0 else "normal")
        st.metric(
            "行数变化",
            f"{len(processed_df)}",
            f"{row_change:+d}" if row_change != 0 else "无变化",
            delta_color=delta_color
        )
    
    with col2:
        col_change = len(processed_df.columns) - len(original_df.columns)
        st.metric(
            "列数变化",
            f"{len(processed_df.columns)}",
            f"{col_change:+d}" if col_change != 0 else "无变化"
        )
    
    with col3:
        orig_missing = original_df.isnull().sum().sum()
        proc_missing = processed_df.isnull().sum().sum()
        missing_change = proc_missing - orig_missing
        st.metric(
            "缺失值",
            f"{proc_missing}",
            f"{missing_change:+d}" if missing_change != 0 else "无变化",
            delta_color="inverse" if missing_change < 0 else "normal"
        )
    
    with col4:
        # 内存使用
        orig_mem = original_df.memory_usage(deep=True).sum() / 1024 / 1024
        proc_mem = processed_df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric(
            "内存占用",
            f"{proc_mem:.2f} MB",
            f"{proc_mem - orig_mem:+.2f} MB" if abs(proc_mem - orig_mem) > 0.01 else "无变化"
        )
    
    # 显示处理后数据预览
    with st.expander("👀 预览处理后数据", expanded=False):
        st.dataframe(processed_df.head(10), use_container_width=True)