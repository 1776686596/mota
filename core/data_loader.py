"""数据加载器 - 解析 CSV/Excel 并提取元数据"""

import pandas as pd
from io import BytesIO


def load_data(file) -> pd.DataFrame:
    """加载上传的文件为 DataFrame"""
    filename = file.name.lower()
    if filename.endswith('.csv'):
        return pd.read_csv(file)
    elif filename.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file)
    else:
        raise ValueError(f"不支持的文件格式: {filename}")


def extract_metadata(df: pd.DataFrame) -> dict:
    """提取 DataFrame 元数据（不发送完整数据给 LLM）"""
    return {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample": df.head(5).to_string(),
        "shape": df.shape
    }
