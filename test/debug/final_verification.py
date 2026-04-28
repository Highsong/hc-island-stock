#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终验证 - 测试600519股票2025年利润表数据"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def final_verification():
    """最终验证"""
    print("最终验证 - 600519股票2025年利润表数据")
    print("=" * 80)

    try:
        # 导入修改后的数据源
        from src.data_extraction.stock_data_source import StockDataSource

        # 创建数据源实例（跳过缓存初始化）
        data_source = StockDataSource.__new__(StockDataSource)
        data_source.max_retries = 3
        data_source.retry_delay = 1
        data_source.timeout = 30

        stock_code = "600519"
        period = "year"

        print(f"测试目标: 股票{stock_code} 2025年利润表数据")
        print(f"测试时间: {os.popen('date').read().strip() if os.name != 'nt' else 'Windows系统'}")
        print("=" * 80)

        # 直接调用利润表获取方法
        print("调用_get_income_statement方法:")
        income_data = data_source._get_income_statement(stock_code, period)

        print(f"\n利润表数据获取结果:")
        print(f"数据类型: {type(income_data)}")
        print(f"数据内容: {income_data}")

        if income_data:
            print(f"获取到 {len(income_data)} 年的利润表数据")
            for year, data in income_data.items():
                print(f"  {year}年: {data}")

            # 检查2025年数据
            if '2025' in income_data:
                print(f"\n[SUCCESS] 2025年数据成功获取！")
                data_2025 = income_data['2025']
                print(f"2025年营业收入: {data_2025['营业收入'][0]:,.2f}")
                print(f"2025年净利润: {data_2025['净利润'][0]:,.2f}")
            else:
                print(f"\n[WARNING] 2025年数据未找到")
        else:
            print(f"\n[ERROR] 未能获取到任何利润表数据")

    except Exception as e:
        print(f"验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*80}")
    print("最终验证完成")
    print("=" * 80)

if __name__ == "__main__":
    final_verification()