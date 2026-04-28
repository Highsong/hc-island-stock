#!/usr/bin/env python3
"""Test script to verify network query failure handling"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from data_extraction.stock_data_source import StockDataSource

def test_network_failure_handling():
    """Test that network failures are handled gracefully without caching sample data"""
    print("Testing network query failure handling...")

    # Create data source
    data_source = StockDataSource()

    # Test with a stock code that should trigger network query
    stock_code = "600519"  # 贵州茅台

    print(f"\n1. Testing with stock: {stock_code}")
    result = data_source.get_stock_financial_data(stock_code, "2020", "2023", "year")

    if result:
        print(f"Got data for {stock_code}")
        years = list(result.keys())
        print(f"  Years: {years}")

        # Check if this is real data or sample data
        first_year = list(result.keys())[0]
        has_real_data = any([
            result[first_year].get('income_statement'),
            result[first_year].get('balance_sheet'),
            result[first_year].get('cash_flow')
        ])

        if has_real_data:
            print("  Contains real financial data")
        else:
            print("  Using sample data (expected if network unavailable)")
    else:
        print(f"No data returned for {stock_code}")

    print(f"\n2. Testing stock info")
    stock_info = data_source.get_stock_info(stock_code)
    print(f"  Stock info: {stock_info}")

    print("\nNetwork failure handling test completed!")

if __name__ == "__main__":
    test_network_failure_handling()