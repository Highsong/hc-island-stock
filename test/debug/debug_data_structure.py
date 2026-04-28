#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug data structure issues"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'src'))

from data_extraction.stock_data_source import StockDataSource

def debug_data_structure():
    """Debug the data structure returned by StockDataSource"""
    print("=" * 80)
    print("DEBUGGING DATA STRUCTURE")
    print("=" * 80)

    try:
        data_source = StockDataSource()

        # Test with sample data first
        print("\n1. Testing with sample data...")
        sample_data = data_source._generate_sample_data('600519', '2021', '2023')
        print(f"Sample data structure: {type(sample_data)}")
        print(f"Sample data keys: {list(sample_data.keys())}")

        if '2023' in sample_data:
            print(f"2023 data type: {type(sample_data['2023'])}")
            print(f"2023 data: {sample_data['2023']}")

        # Test with real data
        print("\n2. Testing with real data...")
        real_data = data_source.get_stock_financial_data('600519', '2021', '2023', 'year')
        print(f"Real data structure: {type(real_data)}")
        print(f"Real data keys: {list(real_data.keys())}")

        if real_data:
            first_year = list(real_data.keys())[0]
            print(f"First year ({first_year}) data type: {type(real_data[first_year])}")
            print(f"First year data: {real_data[first_year]}")

        # Test normalization
        print("\n3. Testing normalization...")
        normalized_data = data_source._normalize_data_structure(real_data, 'year')
        print(f"Normalized data keys: {list(normalized_data.keys())}")

        if normalized_data:
            first_year = list(normalized_data.keys())[0]
            print(f"Normalized first year ({first_year}) data type: {type(normalized_data[first_year])}")
            print(f"Normalized first year data: {normalized_data[first_year]}")

    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("DEBUGGING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    debug_data_structure()