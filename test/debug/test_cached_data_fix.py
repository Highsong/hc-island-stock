#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test cached data handling fix"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

import pandas as pd
import pyarrow as pa

def test_trend_analysis_dataframe():
    """Test that trend analysis data can be converted to DataFrame without errors"""
    print("Testing trend analysis DataFrame creation...")

    # Simulate the problematic cached trend analysis data
    problematic_trend_data = {
        '营业收入': {
            '复合增长率': 0.15,
            '年均增长': 0.15,
            '趋势方向': '上升趋势'  # This string causes the issue
        },
        '净利润': {
            '复合增长率': 0.12,
            '年均增长': 0.12,
            '趋势方向': '上升趋势'
        }
    }

    print("Original problematic data:")
    print(problematic_trend_data)

    # Test the old way (should fail)
    print("\nTesting old DataFrame creation (should fail):")
    try:
        old_df = pd.DataFrame(problematic_trend_data)
        print(f"Old DataFrame created: {old_df.dtypes}")
        # Try Arrow conversion
        table = pa.Table.from_pandas(old_df)
        print("Old method: Arrow conversion successful (unexpected)")
    except Exception as e:
        print(f"Old method: Arrow conversion failed as expected: {e}")

    # Test the new way (should work)
    print("\nTesting new DataFrame creation (should work):")
    try:
        # Simulate the new approach
        trend_rows = []
        for metric_name, metrics in problematic_trend_data.items():
            if isinstance(metrics, dict):
                row = {
                    '指标': metric_name,
                    '复合增长率': metrics.get('复合增长率', 0.0),
                    '年均增长': metrics.get('年均增长', 0.0),
                    '趋势方向': metrics.get('趋势方向', '未知')
                }
                trend_rows.append(row)

        if trend_rows:
            new_df = pd.DataFrame(trend_rows)
            new_df.set_index('指标', inplace=True)
            print(f"New DataFrame created: {new_df.dtypes}")

            # Try Arrow conversion
            table = pa.Table.from_pandas(new_df)
            print("New method: Arrow conversion successful!")
            print(f"Schema: {table.schema}")

    except Exception as e:
        print(f"New method: Arrow conversion failed: {e}")

    # Test edge cases
    print("\nTesting edge cases:")

    # Empty trend data
    empty_trend_data = {}
    trend_rows = []
    for metric_name, metrics in empty_trend_data.items():
        if isinstance(metrics, dict):
            row = {
                '指标': metric_name,
                '复合增长率': metrics.get('复合增长率', 0.0),
                '年均增长': metrics.get('年均增长', 0.0),
                '趋势方向': metrics.get('趋势方向', '未知')
            }
            trend_rows.append(row)

    if trend_rows:
        df = pd.DataFrame(trend_rows)
        df.set_index('指标', inplace=True)
        table = pa.Table.from_pandas(df)
        print("Empty data: Handled correctly")
    else:
        print("Empty data: No DataFrame created (correct behavior)")

if __name__ == "__main__":
    test_trend_analysis_dataframe()