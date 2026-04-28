#!/usr/bin/env python3
"""Debug script to investigate year mismatch issue"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from app_new import DataProcessor

def debug_year_mismatch():
    """Debug the year mismatch issue"""
    print("=== Debugging Year Mismatch Issue ===")

    # Test the DataProcessor with 2022-2024 range
    data_processor = DataProcessor()

    stock_code = "600519"  # 茅台
    start_year = "2022"
    end_year = "2024"  # Note: NOT including 2025
    period = "year"

    print(f"Testing DataProcessor with:")
    print(f"  Stock: {stock_code}")
    print(f"  Start Year: {start_year}")
    print(f"  End Year: {end_year}")
    print(f"  Expected years: {list(range(int(start_year), int(end_year) + 1))}")
    print(f"  Period: {period}")
    print()

    # Process the data
    analysis_data = data_processor.process_stock_data(
        stock_code=stock_code,
        start_year=start_year,
        end_year=end_year,
        period=period
    )

    print("=== Analysis Data Results ===")

    # Check periods returned
    periods = analysis_data.get('periods', [])
    print(f"Actual periods returned: {periods}")
    print(f"Expected periods: {list(range(int(start_year), int(end_year) + 1))}")
    print(f"Match: {periods == [str(y) for y in range(int(start_year), int(end_year) + 1)]}")
    print()

    # Check latest_period
    latest_period = analysis_data.get('latest_period', {})
    latest_year = latest_period.get('period', 'N/A')
    print(f"Latest period year: {latest_year}")
    print(f"Should be: {end_year}")
    print(f"Match: {latest_year == end_year}")
    print()

    # Check trend_analysis
    trend_analysis = analysis_data.get('trend_analysis', {})
    print(f"Trend analysis available: {bool(trend_analysis)}")
    if trend_analysis:
        for metric, data in trend_analysis.items():
            print(f"  {metric}: {data}")
    print()

    # Check if there's cached data interfering
    cache_key = f"{stock_code}_{start_year}_{end_year}_{period}"
    print(f"Cache key used: {cache_key}")

    # Test with a different range to see if it's a general issue
    print("\n=== Testing with 2020-2023 range ===")
    analysis_data2 = data_processor.process_stock_data(
        stock_code=stock_code,
        start_year="2020",
        end_year="2023",
        period=period
    )

    periods2 = analysis_data2.get('periods', [])
    print(f"2020-2023 result: {periods2}")
    print(f"Expected: ['2020', '2021', '2022', '2023']")

if __name__ == "__main__":
    debug_year_mismatch()