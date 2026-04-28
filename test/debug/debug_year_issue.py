#!/usr/bin/env python3
"""Debug script to investigate the year range issue"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from data_extraction.stock_data_source import StockDataSource

def debug_year_issue():
    """Debug the year range issue"""
    print("=== Debugging Year Range Issue ===")

    data_source = StockDataSource()

    # Test with a known stock code
    stock_code = "600519"  # 茅台
    start_year = "2022"
    end_year = "2025"
    period = "year"

    print(f"Testing with stock: {stock_code}")
    print(f"Year range: {start_year} to {end_year}")
    print(f"Period: {period}")
    print()

    # Get the data
    result = data_source.get_stock_financial_data(
        stock_code=stock_code,
        start_year=start_year,
        end_year=end_year,
        period=period,
        force_refresh=True  # Force refresh to avoid cache issues
    )

    print(f"\nResult keys: {list(result.keys())}")
    print(f"Number of years returned: {len(result)}")

    if result:
        for year, data in result.items():
            print(f"\nYear {year}:")
            print(f"  Income statement keys: {list(data.get('income_statement', {}).keys())}")
            print(f"  Balance sheet keys: {list(data.get('balance_sheet', {}).keys())}")
            print(f"  Cash flow keys: {list(data.get('cash_flow', {}).keys())}")

            # Show some sample data
            income = data.get('income_statement', {})
            if income:
                revenue = income.get('营业收入', [0])[0] if income.get('营业收入') else 0
                profit = income.get('净利润', [0])[0] if income.get('净利润') else 0
                print(f"  Revenue: {revenue}, Profit: {profit}")
    else:
        print("No data returned!")

if __name__ == "__main__":
    debug_year_issue()