# src/data_extraction/data_cleaner.py
import pandas as pd
import re
from typing import Dict, Any

class DataCleaner:
    """财务数据清洗器"""

    def __init__(self):
        self.cleaning_rules = {
            'remove_parentheses': r'\([^)]*\)',
            'remove_brackets': r'\[[^]]*\]',
            'remove_percentage': r'\d+\.?\d*%',
            'extract_numbers': r'[\d,]+\.?\d*'
        }

    def clean_financial_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """清洗财务数据"""
        cleaned_data = {}

        for table_type, df in raw_data.items():
            if df is not None:
                cleaned_df = self._clean_dataframe(df)
                cleaned_data[table_type] = cleaned_df

        return cleaned_data

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗单个DataFrame"""
        # 创建副本避免修改原数据
        cleaned_df = df.copy()

        # 清理列名
        cleaned_df.columns = [self._clean_text(str(col)) for col in cleaned_df.columns]

        # 清理数据
        for col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].apply(lambda x: self._clean_cell_value(x))

        # 转换数值类型
        cleaned_df = self._convert_numeric_columns(cleaned_df)

        return cleaned_df

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not isinstance(text, str):
            return str(text)

        # 移除括号内容、百分号等
        text = re.sub(self.cleaning_rules['remove_parentheses'], '', text)
        text = re.sub(self.cleaning_rules['remove_brackets'], '', text)
        text = re.sub(r'\s+', ' ', text)  # 多个空格替换为单个

        return text.strip()

    def _clean_cell_value(self, value: Any) -> str:
        """清理单元格值"""
        if pd.isna(value):
            return ''

        value_str = str(value)
        # 提取数字
        numbers = re.findall(self.cleaning_rules['extract_numbers'], value_str)
        if numbers:
            return numbers[0].replace(',', '')

        return self._clean_text(value_str)

    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换数值列"""
        df_copy = df.copy()

        for col in df_copy.columns[1:]:  # 跳过第一列（通常是项目名称）
            try:
                # 尝试转换为数值
                df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
            except:
                pass

        return df_copy