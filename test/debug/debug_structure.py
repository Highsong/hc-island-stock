#!/usr/bin/env python3
"""
调试数据结构问题
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_structure():
    """调试数据结构问题"""
    print("=" * 60)
    print("调试数据结构问题")
    print("=" * 60)

    try:
        from data_extraction.stock_data_source import StockDataSource

        # 模拟用户选择2022-2024年
        start_year = "2022"
        end_year = "2024"
        stock_code = "600519"

        data_source = StockDataSource()

        # 测试示例数据结构
        print("\\n1. 测试示例数据结构...")
        sample_data = data_source._generate_sample_data(stock_code, start_year, end_year)
        print(f"示例数据结构: {type(sample_data)}")
        for year, year_data in sample_data.items():
            print(f"  {year}: {type(year_data)}")
            if isinstance(year_data, dict):
                print(f"    键: {list(year_data.keys())}")
                if 'income_statement' in year_data:
                    print(f"    营业收入: {year_data['income_statement'].get('营业收入', 'N/A')}")

        # 测试实际数据结构
        print("\\n2. 测试实际数据结构...")
        full_data = data_source.get_stock_financial_data(stock_code, start_year, end_year, 'year')
        print(f"实际数据结构: {type(full_data)}")

        if full_data:
            year = list(full_data.keys())[0]
            year_data = full_data[year]
            print(f"  {year}: {type(year_data)}")
            if isinstance(year_data, dict):
                print(f"    键: {list(year_data.keys())}")
                for key, value in year_data.items():
                    print(f"    {key}: {type(value)} - {str(value)[:100]}")

    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_structure()