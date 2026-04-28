#!/usr/bin/env python3
"""Debug script to test the complete app flow"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from app_new import DataProcessor

def debug_app_flow():
    """Debug the complete app flow"""
    print("=== Debugging App Flow ===")

    # Test the DataProcessor directly
    data_processor = DataProcessor()

    stock_code = "600519"  # 茅台
    start_year = "2022"
    end_year = "2025"
    period = "year"

    print(f"Testing DataProcessor with:")
    print(f"  Stock: {stock_code}")
    print(f"  Start Year: {start_year}")
    print(f"  End Year: {end_year}")
    print(f"  Period: {period}")
    print()

    # Process the data
    analysis_data = data_processor.process_stock_data(
        stock_code=stock_code,
        start_year=start_year,
        end_year=end_year,
        period=period
    )

    print("=== Analysis Data Summary ===")
    print(f"Keys in analysis_data: {list(analysis_data.keys())}")
    print()

    # Check periods
    periods = analysis_data.get('periods', [])
    print(f"Periods: {periods}")
    print(f"Number of periods: {len(periods)}")
    print()

    # Check latest_period
    latest_period = analysis_data.get('latest_period', {})
    print(f"Latest period data keys: {list(latest_period.keys())}")
    if latest_period:
        print(f"Latest period year: {latest_period.get('period', 'N/A')}")
        key_metrics = latest_period.get('key_metrics', {})
        print(f"Key metrics keys: {list(key_metrics.keys())}")
    print()

    # Check trend_analysis
    trend_analysis = analysis_data.get('trend_analysis', {})
    print(f"Trend analysis keys: {list(trend_analysis.keys())}")
    if trend_analysis:
        for metric, data in trend_analysis.items():
            print(f"  {metric}: {data}")
    print()

    # Check charts
    charts = analysis_data.get('charts', {})
    print(f"Charts available: {list(charts.keys())}")
    print()

    # Check raw data if available
    if hasattr(data_processor, 'raw_data_debug'):
        print(f"Raw data years: {list(data_processor.raw_data_debug.keys())}")

if __name__ == "__main__":
    debug_app_flow()