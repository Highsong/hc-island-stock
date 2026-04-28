#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试季度数据修复是否成功
"""

import sys
import os

# 添加项目路径
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from src.data_extraction.stock_data_source import StockDataSource

def test_quarter_data():
    """测试季度数据获取"""
    print("测试季度数据获取...")

    data_source = StockDataSource()

    # 测试获取季度数据
    result = data_source.get_stock_financial_data(
        stock_code="600519",
        start_year="2022",
        end_year="2023",
        period="quarter"
    )

    print(f"获取结果: {len(result)} 年数据")

    # 检查是否有季度数据
    for year, year_data in result.items():
        print(f"\n{year}年数据:")
        if isinstance(year_data, dict):
            # 检查是否有季度键
            quarter_keys = [key for key in year_data.keys() if key in ['Q1', 'Q2', 'Q3', 'Q4']]
            if quarter_keys:
                print(f"  找到季度数据: {quarter_keys}")
                return True
            else:
                for key, value in year_data.items():
                    print(f"  {key}: {type(value)}")
        else:
            print(f"  数据类型: {type(year_data)}")

    print("未找到季度数据")
    return False

if __name__ == "__main__":
    success = test_quarter_data()
    if success:
        print("\n✅ 季度数据修复成功!")
    else:
        print("\n❌ 季度数据修复失败!")
        sys.exit(1)