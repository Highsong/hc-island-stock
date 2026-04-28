#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test enhanced AKShare diagnostics"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

def test_enhanced_diagnostics():
    """Test the enhanced AKShare error diagnostics"""
    print("=== Testing Enhanced AKShare Diagnostics ===")

    try:
        from data_extraction.stock_data_source import StockDataSource

        # Create data source and clear cache
        data_source = StockDataSource()
        data_source.cache_manager.clear_all()

        print("\n" + "="*60)
        print("测试股票: 600519 (贵州茅台)")
        print("="*60)

        # Test with a stock that will likely fail
        result = data_source.get_stock_financial_data("600519", "2022", "2023")

        print(f"\n最终结果: {len(result)} 个年份的数据")

        # Check error log
        print(f"\n{'='*60}")
        print("检查错误日志:")
        print("='*60")

        error_log_path = os.path.join("data", "cache", "akshare_errors.log")
        if os.path.exists(error_log_path):
            with open(error_log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                print(f"错误日志文件包含 {len(lines)} 行")
                if lines:
                    print("\n最后一条错误记录:")
                    print("-" * 40)
                    print(lines[-1][:1000] + "..." if len(lines[-1]) > 1000 else lines[-1])
        else:
            print("错误日志文件不存在")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_diagnostics()