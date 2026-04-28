#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test data type handling fix"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

import pandas as pd
import pyarrow as pa

def test_arrow_serialization():
    """Test that financial data can be serialized to Arrow without errors"""
    print("Testing Arrow serialization with financial data...")

    # Test data that previously caused issues
    test_data_cases = [
        {
            '周期': ['2020', '2021', '2022', '2023'],
            '营业收入': [100.0, 110.0, 121.0, 133.1]  # All numeric
        },
        {
            '周期': ['2020', '2021', '2022', '2023'],
            '营业收入': [100, 110, 121, 133]  # Integer values
        },
        {
            '周期': ['2020', '2021', '2022', '2023'],
            '营业收入': ['100.0', '110.0', '121.0', '133.1']  # String numbers
        },
        {
            '周期': ['2020', '2021', '2022', '2023'],
            '营业收入': [None, 110.0, 121.0, 133.1]  # With None values
        }
    ]

    for i, data in enumerate(test_data_cases):
        print(f"\nTest case {i+1}: {data['营业收入']}")
        try:
            df = pd.DataFrame(data)
            print(f"  DataFrame created: {df.dtypes}")

            # Try to convert to Arrow
            table = pa.Table.from_pandas(df)
            print(f"  Arrow conversion successful: {table.schema}")

        except Exception as e:
            print(f"  Arrow conversion failed: {e}")

    # Test the problematic case that was causing issues
    print("\nTesting problematic mixed data case:")
    problematic_data = {
        '周期': ['2020', '2021', '2022', '2023'],
        '营业收入': [100.0, 110.0, '上升趋势', 133.1]  # Mixed types - this should fail
    }

    try:
        df = pd.DataFrame(problematic_data)
        print(f"DataFrame created: {df.dtypes}")
        table = pa.Table.from_pandas(df)
        print("This should have failed!")
    except Exception as e:
        print(f"Correctly failed with mixed data: {e}")

    # Test the fixed version
    print("\nTesting fixed data processing:")
    from visualization.chart_generator import ChartGenerator

    cg = ChartGenerator()

    # Simulate the fix
    fixed_data = problematic_data.copy()
    fixed_data['营业收入'] = [float(val) if val is not None and str(val).replace('.','').replace('-','').isdigit() else 0.0 for val in fixed_data['营业收入']]

    print(f"Fixed data: {fixed_data['营业收入']}")

    try:
        df = pd.DataFrame(fixed_data)
        table = pa.Table.from_pandas(df)
        print("Fixed data converts to Arrow successfully")

        # Test chart creation
        fig = cg.create_line_chart(fixed_data, '营业收入', 'Test Chart')
        print("Chart creation successful with fixed data")

    except Exception as e:
        print(f"Fixed data still has issues: {e}")

if __name__ == "__main__":
    test_arrow_serialization()