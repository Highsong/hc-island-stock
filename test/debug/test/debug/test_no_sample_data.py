#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test that no sample data is returned when API fails"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..', 'src'))

try:
    from data_extraction.stock_data_source import StockDataSource

    print("=== Testing No Sample Data Return ===")

    # Create data source
    data_source = StockDataSource()

    # Clear cache first
    print("Clearing cache...")
    data_source.cache_manager.clear_all()

    test_stock = "600519"  # Use a stock that will fail
    print(f"Testing with stock: {test_stock}")

    # Call the API
    print("\nCalling API (should fail and return no data)...")
    result = data_source.get_stock_financial_data(test_stock, "2022", "2023")

    print(f"Result: {result}")
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result)}")

    if result and len(result) > 0:
        print("❌ FAIL: Got data when API should have failed")
        print(f"Data keys: {list(result.keys())}")
    else:
        print("✅ PASS: No data returned when API failed (as expected)")

    # Test A股 specific function
    print(f"\nTesting A股 specific function...")
    result_a = data_source._get_a_stock_data(test_stock, "2022", "2023", "year")
    print(f"A股 result: {result_a}")
    if result_a and len(result_a) > 0:
        print("❌ FAIL: A股 function returned data")
    else:
        print("✅ PASS: A股 function returned no data")

    # Test港股 specific function
    print(f"\nTesting 港股 specific function...")
    result_hk = data_source._get_hk_stock_data("0700.HK", "2022", "2023", "year")
    print(f"港股 result: {result_hk}")
    if result_hk and len(result_hk) > 0:
        print("❌ FAIL: 港股 function returned data")
    else:
        print("✅ PASS: 港股 function returned no data")

    print("\n=== Test Summary ===")
    print("All functions should return empty dict when API fails")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()