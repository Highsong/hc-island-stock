# src/data_extraction/pdf_parser.py
import pdfplumber
import pandas as pd
from typing import Dict, List, Any
import json

class PDFParser:
    """PDF年报解析器"""

    def __init__(self):
        self.tables = {}
        self.text_content = ""

    def extract_financial_tables(self, pdf_path: str) -> Dict[str, pd.DataFrame]:
        """从PDF中提取财务报表"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                all_tables = {}

                for page_num, page in enumerate(pdf.pages):
                    # 提取表格
                    tables = page.extract_tables({
                        "vertical_strategy": "lines_strict",
                        "horizontal_strategy": "lines_strict"
                    })

                    for table_idx, table in enumerate(tables):
                        if len(table) > 3:  # 至少4行才可能是财务报表
                            table_name = f"table_{page_num}_{table_idx}"
                            df = pd.DataFrame(table[1:], columns=table[0])
                            all_tables[table_name] = df

                # 识别并分类财务报表
                financial_data = self._classify_financial_tables(all_tables)
                return financial_data

        except Exception as e:
            print(f"PDF解析错误: {e}")
            return {}

    def _classify_financial_tables(self, tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """识别财务报表类型"""
        financial_data = {
            "income_statement": None,
            "balance_sheet": None,
            "cash_flow": None
        }

        for table_name, df in tables.items():
            if df.empty:
                continue

            # 简单的关键词匹配来识别表格类型
            first_column = df.iloc[:, 0].astype(str).str.cat(sep=' ').lower()

            if any(keyword in first_column for keyword in ['营业收入', '营业成本', '净利润']):
                financial_data["income_statement"] = df
            elif any(keyword in first_column for keyword in ['资产', '负债', '所有者权益']):
                financial_data["balance_sheet"] = df
            elif any(keyword in first_column for keyword in ['经营活动', '投资活动', '筹资活动']):
                financial_data["cash_flow"] = df

        return financial_data

    def extract_text_content(self, pdf_path: str) -> str:
        """提取PDF文本内容"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"文本提取错误: {e}")
            return ""