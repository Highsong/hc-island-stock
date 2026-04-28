#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""专门测试600519股票2025年利润表数据的调试脚本"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_extraction.stock_data_source import StockDataSource

def test_600519_profit_2025():
    """测试600519股票2025年利润表数据"""
    print("开始测试600519股票2025年利润表数据...")

    # 创建数据源实例
    data_source = StockDataSource()

    # 专门测试利润表数据
    stock_code = "600519"
    period = "year"

    print(f"\n{'='*100}")
    print(f"测试目标: 股票{stock_code} 2025年利润表数据")
    print(f"测试时间: {os.popen('date').read().strip() if os.name != 'nt' else 'Windows系统'}")
    print(f"{'='*100}\n")

    # 直接调用利润表获取方法
    print("直接调用_get_income_statement方法:")
    income_data = data_source._get_income_statement(stock_code, period)

    print(f"\n利润表数据获取结果:")
    print(f"数据类型: {type(income_data)}")
    print(f"数据内容: {income_data}")

    if income_data:
        print(f"获取到 {len(income_data)} 年的利润表数据")
        for year, data in income_data.items():
            print(f"  {year}年: {data}")
    else:
        print("未能获取到任何利润表数据")

    # 测试完整的财务数据获取
    print(f"\n{'='*80}")
    print("测试完整的财务数据获取:")
    financial_data = data_source.get_stock_financial_data(
        stock_code=stock_code,
        start_year="2025",
        end_year="2025",
        period=period
    )

    print(f"\n完整财务数据获取结果:")
    print(f"数据类型: {type(financial_data)}")
    print(f"数据内容: {financial_data}")

    if financial_data:
        print(f"获取到 {len(financial_data)} 年的财务数据")
        for year, data in financial_data.items():
            print(f"  {year}年: {data}")
    else:
        print("未能获取到任何财务数据")

if __name__ == "__main__":
    test_600519_profit_2025()