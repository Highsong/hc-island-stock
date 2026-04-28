#!/usr/bin/env python3
"""
调试年份问题
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_years():
    """调试年份问题"""
    print("=" * 60)
    print("调试年份问题")
    print("=" * 60)

    try:
        from data_extraction.stock_data_source import StockDataSource

        # 模拟用户选择2022-2026年
        start_year = "2022"
        end_year = "2026"
        stock_code = "600519"

        print(f"\\n用户选择的年份范围: {start_year} - {end_year}")
        print(f"股票代码: {stock_code}")

        data_source = StockDataSource()

        # 测试示例数据生成
        print("\\n1. 测试示例数据生成...")
        sample_data = data_source._generate_sample_data(stock_code, start_year, end_year)
        print(f"示例数据年份数量: {len(sample_data)}")
        print(f"示例数据年份: {list(sample_data.keys())}")

        # 测试完整的数据获取
        print("\\n2. 测试完整数据获取...")
        full_data = data_source.get_stock_financial_data(stock_code, start_year, end_year, 'year')
        print(f"完整数据年份数量: {len(full_data)}")
        print(f"完整数据年份: {list(full_data.keys())}")

        # 检查是否有营业收入为0的情况
        print("\\n3. 检查营业收入数据...")
        for year, year_data in full_data.items():
            if isinstance(year_data, dict):
                if 'income_statement' in year_data:
                    revenue = year_data['income_statement'].get('营业收入', [0])
                    print(f"  {year}年营业收入: {revenue}")
                elif '营业收入' in year_data:
                    revenue = year_data.get('营业收入', [0])
                    print(f"  {year}年营业收入: {revenue}")
                else:
                    print(f"  {year}年: 无营业收入数据")

    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_years()