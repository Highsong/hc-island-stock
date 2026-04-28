# src/utils/helpers.py
import json
import os
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

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


# 股票分析相关的辅助函数
def validate_stock_code(stock_code: str) -> bool:
    """验证股票代码格式"""
    import re

    # A股代码：6位数字
    a_stock_pattern = r'^\d{6}$'
    # 港股代码：4-5位数字或字母数字组合
    hk_stock_pattern = r'^[A-Za-z0-9]{4,6}$'

    return bool(re.match(a_stock_pattern, stock_code) or re.match(hk_stock_pattern, stock_code))

def format_stock_display_name(stock_code: str, stock_name: str = None) -> str:
    """格式化股票显示名称"""
    if stock_name:
        return f"{stock_code} - {stock_name}"
    return stock_code

def get_market_type(stock_code: str) -> str:
    """获取股票市场类型"""
    if stock_code.isdigit() and len(stock_code) == 6:
        return 'A股'
    elif stock_code.upper().endswith('.HK') or (stock_code.isdigit() and len(stock_code) == 5):
        return '港股'
    else:
        return '未知'

def format_financial_value(value: float, unit: str = '亿') -> str:
    """格式化财务数值显示"""
    if abs(value) >= 100000000 and unit == '亿':
        return f"{value/100000000:.2f}亿"
    elif abs(value) >= 10000 and unit == '万':
        return f"{value/10000:.2f}万"
    else:
        return f"{value:,.2f}"

def calculate_growth_rate(current: float, previous: float) -> float:
    """计算增长率"""
    if previous == 0:
        return 0
    return (current - previous) / abs(previous)

def get_period_display_name(period: str) -> str:
    """获取周期显示名称"""
    period_names = {
        'year': '年度',
        'year_half': '半年度',
        'Q1': '一季度',
        'Q2': '二季度',
        'Q3': '三季度',
        'Q4': '四季度',
        'quarter': '季度',
    }
    return period_names.get(period, period)