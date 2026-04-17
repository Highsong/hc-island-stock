# src/utils/helpers.py
import json
import os
from typing import Dict, List, Any
import pandas as pd

def load_processed_data(data_dir: str = 'data/processed_data') -> Dict[str, Any]:
    """加载处理后的数据"""
    data = {}

    if not os.path.exists(data_dir):
        return data

    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    key = filename.replace('.json', '')
                    data[key] = json.load(f)
            except Exception as e:
                print(f"加载数据文件 {filename} 失败: {e}")

    return data

def save_processed_data(data: Dict[str, Any], filename: str,
                       data_dir: str = 'data/processed_data'):
    """保存处理后的数据"""
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, f"{filename}.json")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存数据文件 {filename} 失败: {e}")

def format_currency(value: float, unit: str = '亿') -> str:
    """格式化货币数值"""
    if unit == '亿':
        return f"{value/100000000:,.2f}亿"
    elif unit == '万':
        return f"{value/10000:,.2f}万"
    else:
        return f"{value:,.2f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """格式化百分比"""
    return f"{value:.{decimals}f}%"

def detect_new_reports(pdf_dir: str = 'data/raw_pdfs') -> List[str]:
    """检测新的年报文件"""
    if not os.path.exists(pdf_dir):
        return []

    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    return pdf_files

def extract_year_from_filename(filename: str) -> str:
    """从文件名提取年份"""
    import re
    # 匹配年份模式
    year_match = re.search(r'(20\d{2})', filename)
    if year_match:
        return year_match.group(1)
    return '未知年份'